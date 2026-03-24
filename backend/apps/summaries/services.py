from pathlib import Path
import re
import shutil
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from rest_framework.exceptions import ValidationError

from .models import SummaryRecord


COMMON_ENGLISH_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "data",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "learning",
    "machine",
    "model",
    "models",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "using",
    "with",
}

SUMMARY_CUE_WORDS = {
    "important",
    "key",
    "main",
    "overall",
    "result",
    "results",
    "conclusion",
    "concludes",
    "summary",
    "recommend",
    "recommends",
    "finding",
    "findings",
}

TRANSCRIPT_FILLER_PATTERNS = [
    r"\bhey everyone\b",
    r"\bhi everyone\b",
    r"\bwelcome back(?: to the channel)?\b",
    r"\bthanks for watching\b",
    r"\bdon't forget to like and subscribe\b",
    r"\bmake sure to like and subscribe\b",
    r"\blike and subscribe\b",
    r"\bsubscribe to the channel\b",
    r"\bsee you in the next video\b",
]


def _clean_text(raw_text: str) -> str:
    return re.sub(r"\s+", " ", raw_text).strip()


def _clean_transcript_chunk(text: str) -> str:
    cleaned = _clean_text(text)
    for pattern in TRANSCRIPT_FILLER_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(um+|uh+|you know|sort of|kind of)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\b(and|but|so)\s*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^[,.\-\s]+|[,.\-\s]+$", "", cleaned)
    return cleaned


def _normalize_transcript_text(chunks) -> str:
    cleaned_chunks: list[str] = []
    previous_chunk = ""

    for chunk in chunks:
        raw_text = getattr(chunk, "text", str(chunk))
        cleaned = _clean_transcript_chunk(raw_text)
        if not cleaned:
            continue
        if cleaned.lower() == previous_chunk.lower():
            continue
        cleaned_chunks.append(cleaned)
        previous_chunk = cleaned

    if not cleaned_chunks:
        return ""

    merged_segments: list[str] = []
    pending_chunk = ""

    for chunk_text in cleaned_chunks:
        word_count = len(chunk_text.split())
        has_terminal_punctuation = chunk_text.endswith((".", "!", "?"))

        if pending_chunk:
            pending_chunk = f"{pending_chunk} {chunk_text}".strip()
        elif word_count < 6 and not has_terminal_punctuation:
            pending_chunk = chunk_text
            continue
        else:
            pending_chunk = chunk_text

        pending_word_count = len(pending_chunk.split())
        if has_terminal_punctuation or pending_word_count >= 12:
            sentence = pending_chunk.strip(" ,")
            if sentence and sentence[-1] not in ".!?":
                sentence += "."
            merged_segments.append(sentence)
            pending_chunk = ""

    if pending_chunk:
        sentence = pending_chunk.strip(" ,")
        if sentence and sentence[-1] not in ".!?":
            sentence += "."
        merged_segments.append(sentence)

    return " ".join(merged_segments)


def _split_long_sentence(sentence: str, max_words: int = 18) -> list[str]:
    words = sentence.split()
    if len(words) <= max_words:
        return [sentence]

    clause_split = re.split(r"(?i)\b(?:and then|but|because|so|while|however|meanwhile|also|another|toward the end)\b", sentence)
    clause_split = [_clean_text(part) for part in clause_split if _clean_text(part)]
    if 1 < len(clause_split) <= 4:
        normalized_clauses = []
        for clause in clause_split:
            if clause and clause[-1] not in ".!?":
                clause += "."
            normalized_clauses.append(clause)
        return normalized_clauses

    segments: list[str] = []
    current_words: list[str] = []

    for word in words:
        current_words.append(word)
        if len(current_words) >= max_words:
            segment = " ".join(current_words).strip(" ,")
            if segment and segment[-1] not in ".!?":
                segment += "."
            segments.append(segment)
            current_words = []

    if current_words:
        segment = " ".join(current_words).strip(" ,")
        if segment and segment[-1] not in ".!?":
            segment += "."
        segments.append(segment)

    return segments


def _chunk_text(text: str, max_chars: int = 6000) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    current_words: list[str] = []
    current_length = 0

    for word in words:
        additional_length = len(word) + (1 if current_words else 0)
        if current_words and current_length + additional_length > max_chars:
            chunks.append(" ".join(current_words))
            current_words = [word]
            current_length = len(word)
        else:
            current_words.append(word)
            current_length += additional_length

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def _shift_letter(char: str, offset: int) -> str:
    if "a" <= char <= "z":
        return chr((ord(char) - ord("a") + offset) % 26 + ord("a"))
    if "A" <= char <= "Z":
        return chr((ord(char) - ord("A") + offset) % 26 + ord("A"))
    return char


def _caesar_shift(text: str, offset: int) -> str:
    return "".join(_shift_letter(char, offset) for char in text)


def _english_score(text: str) -> float:
    words = re.findall(r"[A-Za-z]{2,}", text.lower())
    if not words:
        return 0.0

    common_matches = sum(1 for word in words if word in COMMON_ENGLISH_WORDS)
    vowel_heavy_words = sum(1 for word in words if any(vowel in word for vowel in "aeiou"))
    return (common_matches * 3 + vowel_heavy_words) / len(words)


def _maybe_decode_shifted_text(text: str) -> str:
    baseline_score = _english_score(text)
    best_text = text
    best_score = baseline_score

    for offset in range(1, 26):
        candidate = _caesar_shift(text, -offset)
        candidate_score = _english_score(candidate)
        if candidate_score > best_score:
            best_text = candidate
            best_score = candidate_score

    if best_score >= baseline_score + 0.25:
        return best_text
    return text


def _extract_youtube_video_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")

    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/")[0]
        if len(candidate) == 11:
            return candidate

    if host in {"youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
            if len(candidate) == 11:
                return candidate

        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live", "v"} and len(parts[1]) == 11:
            return parts[1]

    match = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/|/live/)([\w-]{11})", url)
    if match:
        return match.group(1)

    raise ValidationError("Could not detect a valid YouTube video id from this URL.")


def _build_summary_prompt(text: str, output_format: str, input_type: str, summary_section: str) -> str:
    source_context = {
        SummaryRecord.InputType.PDF: (
            "This content comes from a PDF document. Focus on the main topic, core arguments, key findings, "
            "important numbers, and practical takeaways. If the PDF is a resume or profile, mention the person's name,"
            " role or profile, experience, skills, education, projects, achievements, and other notable details."
            " Ignore garbled fragments, page furniture, citation noise, and repeated headers or footers."
        ),
        SummaryRecord.InputType.IMAGE: (
            "This content comes from OCR on an image. Ignore OCR glitches and summarize only the clearly readable meaning."
        ),
        SummaryRecord.InputType.YOUTUBE: (
            "This content comes from a video transcript. Combine repeated spoken phrases into a clean written summary."
        ),
        SummaryRecord.InputType.TEXT: (
            "This content is plain text. Preserve the intended meaning and keep the summary direct."
        ),
    }.get(input_type, "Summarize the content faithfully.")

    section_instructions = (
        "1. Short Summary:\n"
        "- Provide a clear and complete overview of the content in about 6 to 10 lines.\n\n"
        if summary_section == SummaryRecord.SummarySection.SHORT_SUMMARY
        else "1. Key Points:\n- Highlight the most important ideas as clear bullet points.\n\n"
    )

    return (
        "You are an AI assistant that summarizes content clearly and accurately.\n\n"
        f"{source_context}\n\n"
        "Analyze the following content and generate a structured summary.\n\n"
        "Output format:\n\n"
        f"{section_instructions}"
        "Instructions:\n"
        "- Do not add extra information.\n"
        "- Keep it accurate and relevant.\n"
        "- Avoid repetition.\n"
        "- Use clear and clean sentences.\n"
        "- Cover the whole content, not just the beginning.\n"
        "- For transcripts, avoid filler phrases and repeated spoken lines.\n\n"
        f"Content:\n{text}\n"
    )


def _openai_system_prompt() -> str:
    return (
        "You are an intelligent summarization assistant. "
        "Your job is to produce accurate, concise, well-structured summaries in simple language. "
        "Do not copy long transcript passages verbatim. Merge repetition and keep only the important information."
    )


def _call_openai_summary(client, prompt: str) -> str:
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=getattr(settings, "OPENAI_TEMPERATURE", 0.2),
        messages=[
            {"role": "system", "content": _openai_system_prompt()},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def _sentence_tokenize(text: str) -> list[str]:
    base_sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
    expanded_sentences: list[str] = []
    for sentence in base_sentences:
        expanded_sentences.extend(_split_long_sentence(sentence))
    return expanded_sentences


def _word_frequencies(text: str) -> dict[str, int]:
    frequencies: dict[str, int] = {}
    for word in re.findall(r"[A-Za-z]{3,}", text.lower()):
        if word in COMMON_ENGLISH_WORDS:
            continue
        frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies


def _sentence_signature(sentence: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[A-Za-z]{3,}", sentence.lower())
        if word not in COMMON_ENGLISH_WORDS
    }


def _score_sentence(sentence: str, frequencies: dict[str, int], index: int, total_sentences: int) -> float:
    words = re.findall(r"[A-Za-z]{3,}", sentence.lower())
    if not words:
        return 0.0

    informative_words = [word for word in words if word not in COMMON_ENGLISH_WORDS]
    if not informative_words:
        return 0.0

    base_score = sum(frequencies.get(word, 0) for word in informative_words) / len(informative_words)
    length_penalty = 1.0
    if len(sentence) > 260:
        length_penalty = 0.85
    elif len(sentence) < 40:
        length_penalty = 0.75

    position_bonus = 0.0
    if total_sentences > 1 and index == total_sentences - 1:
        position_bonus += 0.35
    elif index == 0:
        position_bonus += 0.05

    cue_bonus = 0.2 if any(word in SUMMARY_CUE_WORDS for word in informative_words) else 0.0
    return base_score * length_penalty + position_bonus + cue_bonus


def _extractive_summary_sentences(text: str, max_sentences: int = 4) -> list[str]:
    sentences = _sentence_tokenize(text)
    if not sentences:
        return []

    if len(sentences) <= max_sentences:
        return sentences

    frequencies = _word_frequencies(text)
    if not frequencies:
        return sentences[:max_sentences]

    scored_sentences = [
        (index, sentence, _score_sentence(sentence, frequencies, index, len(sentences)))
        for index, sentence in enumerate(sentences)
    ]
    ranked_sentences = sorted(scored_sentences, key=lambda item: item[2], reverse=True)

    selected: list[tuple[int, str, float]] = []
    for candidate in ranked_sentences:
        candidate_signature = _sentence_signature(candidate[1])
        is_redundant = False
        for chosen in selected:
            chosen_signature = _sentence_signature(chosen[1])
            overlap = len(candidate_signature & chosen_signature)
            baseline = max(1, min(len(candidate_signature), len(chosen_signature)))
            if overlap / baseline >= 0.7:
                is_redundant = True
                break
        if not is_redundant:
            selected.append(candidate)
        if len(selected) >= max_sentences:
            break

    selected.sort(key=lambda item: item[0])
    return [sentence for _, sentence, _ in selected]


def _target_sentence_count(output_format: str, input_type: str, source_sentence_count: int) -> int:
    if output_format == SummaryRecord.OutputFormat.BULLETS:
        target = 8 if input_type == SummaryRecord.InputType.YOUTUBE else 8 if input_type == SummaryRecord.InputType.PDF else 6
    else:
        target = 6 if input_type == SummaryRecord.InputType.YOUTUBE else 8 if input_type == SummaryRecord.InputType.PDF else 6

    if source_sentence_count <= target:
        return source_sentence_count
    return max(4, target)


def _format_fallback_summary(summary_sentences: list[str], summary_section: str) -> str:
    if not summary_sentences:
        return "No summary generated."

    if summary_section == SummaryRecord.SummarySection.KEY_POINTS:
        key_points = summary_sentences[:6]
        lines = ["Key Points:"]
        lines.extend(f"- {sentence}" for sentence in key_points)
        return "\n".join(lines)

    short_summary = " ".join(summary_sentences[:8]).strip()
    return "\n".join(
        [
            "Short Summary:",
            short_summary or "No summary generated.",
        ]
    )


def _fallback_summary(
    text: str,
    output_format: str,
    input_type: str = SummaryRecord.InputType.TEXT,
    summary_section: str = SummaryRecord.SummarySection.SHORT_SUMMARY,
) -> str:
    source_sentences = _sentence_tokenize(text)
    max_sentences = _target_sentence_count(output_format, input_type, len(source_sentences))
    summary_sentences = _extractive_summary_sentences(text, max_sentences=max_sentences)
    normalized_sentences = [re.sub(r"\s+", " ", sentence).strip() for sentence in summary_sentences if sentence.strip()]
    return _format_fallback_summary(normalized_sentences, summary_section)


def extract_content(record: SummaryRecord) -> str:
    if record.input_type == SummaryRecord.InputType.TEXT:
        return _clean_text(record.source_text)
    if record.input_type == SummaryRecord.InputType.PDF:
        from pypdf import PdfReader

        reader = PdfReader(record.source_file.path)
        extracted_text = _clean_text(" ".join(page.extract_text() or "" for page in reader.pages))
        return _maybe_decode_shifted_text(extracted_text)
    if record.input_type == SummaryRecord.InputType.IMAGE:
        import pytesseract
        from PIL import Image
        from pytesseract import TesseractNotFoundError

        tesseract_cmd = settings.TESSERACT_CMD or shutil.which("tesseract")
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        try:
            with Image.open(record.source_file.path) as image:
                extracted_text = pytesseract.image_to_string(image)
        except TesseractNotFoundError:
            raise ValidationError(
                "Image OCR is not configured. Install Tesseract OCR and add it to PATH, "
                "or set TESSERACT_CMD in backend/.env to the full tesseract.exe path."
            )
        except OSError:
            raise ValidationError("The uploaded image could not be opened. Please upload a valid PNG, JPG, or JPEG file.")

        cleaned_text = _clean_text(extracted_text)
        if not cleaned_text:
            raise ValidationError("No readable text was found in the image. Try a clearer image with larger text.")
        return cleaned_text
    if record.input_type == SummaryRecord.InputType.YOUTUBE:
        from youtube_transcript_api import (
            NoTranscriptFound,
            TranscriptsDisabled,
            VideoUnavailable,
            YouTubeTranscriptApi,
        )
        from requests.exceptions import RequestException

        video_id = _extract_youtube_video_id(record.youtube_url)
        try:
            transcript = YouTubeTranscriptApi().fetch(
                video_id,
                languages=("en", "en-IN", "hi", "auto"),
            )
        except (TranscriptsDisabled, NoTranscriptFound):
            raise ValidationError("This YouTube video does not have an accessible transcript.")
        except VideoUnavailable:
            raise ValidationError("This YouTube video is unavailable or could not be accessed.")
        except RequestException:
            raise ValidationError("Could not connect to YouTube from the backend. Check your internet, firewall, or proxy settings.")
        except Exception as exc:
            raise ValidationError(f"Could not fetch the YouTube transcript: {exc}")

        text = _normalize_transcript_text(transcript)
        if not text:
            raise ValidationError("The YouTube transcript was empty, so no summary could be generated.")
        return text
    raise ValueError("Unsupported input type.")


def summarize_text(
    text: str,
    output_format: str,
    input_type: str = SummaryRecord.InputType.TEXT,
    summary_section: str = SummaryRecord.SummarySection.SHORT_SUMMARY,
) -> str:
    if settings.OPENAI_API_KEY:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        try:
            chunks = _chunk_text(text, max_chars=3500)

            if len(chunks) <= 1:
                return _call_openai_summary(client, _build_summary_prompt(text, output_format, input_type, summary_section))

            partial_summaries: list[str] = []
            for index, chunk in enumerate(chunks, start=1):
                partial_summary = _call_openai_summary(
                    client,
                    (
                        f"This is chunk {index} of {len(chunks)} from a larger document.\n"
                        "Summarize only this chunk and keep the points factual and compact.\n\n"
                        + _build_summary_prompt(chunk, SummaryRecord.OutputFormat.BULLETS, input_type, summary_section)
                    ),
                )
                partial_summaries.append(partial_summary)

            combined_notes = "\n\n".join(
                f"Chunk {index} summary:\n{summary}" for index, summary in enumerate(partial_summaries, start=1)
            )
            return _call_openai_summary(
                client,
                (
                    "You are combining summaries from multiple chunks of the same source.\n"
                    "Create one final summary of the full content.\n"
                    "Merge overlapping points, remove repetition, and keep the most important details only.\n\n"
                    + _build_summary_prompt(combined_notes, output_format, input_type, summary_section)
                ),
            )
        except Exception:
            # Fall back to the local summarizer if the API call fails or quota is unavailable.
            return _fallback_summary(text, output_format, input_type, summary_section)

    return _fallback_summary(text, output_format, input_type, summary_section)


def generate_speech(record: SummaryRecord) -> None:
    import pyttsx3

    target_path = Path(settings.MEDIA_ROOT) / "speech"
    target_path.mkdir(parents=True, exist_ok=True)
    filename = f"summary_{record.pk}.wav"
    file_path = target_path / filename

    engine = pyttsx3.init()
    engine.save_to_file(record.summary, str(file_path))
    engine.runAndWait()
    record.audio_file.name = f"speech/{filename}"
