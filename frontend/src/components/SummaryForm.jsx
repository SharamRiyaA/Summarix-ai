import { useState } from "react";
import { api } from "../api/client";
import { useToast } from "./ToastProvider";

const inputTypes = [
  { value: "text", label: "Text", helper: "Paste notes, articles, or raw content." },
  { value: "pdf", label: "PDF", helper: "Upload documents, papers, or reports." },
  { value: "image", label: "Image", helper: "Extract text from screenshots or photos." },
  { value: "youtube", label: "YouTube", helper: "Summarize videos from transcript data." }
];

function getErrorMessage(responseError) {
  if (!responseError) {
    return null;
  }

  if (typeof responseError === "string") {
    return responseError;
  }

  if (responseError.detail) {
    return responseError.detail;
  }

  if (responseError.non_field_errors?.[0]) {
    return responseError.non_field_errors[0];
  }

  const firstFieldError = Object.values(responseError).find((value) => Array.isArray(value) && value[0]);
  if (firstFieldError) {
    return firstFieldError[0];
  }

  return null;
}

export default function SummaryForm({ onCreated }) {
  const { addToast } = useToast();
  const [form, setForm] = useState({
    title: "",
    input_type: "text",
    output_format: "paragraph",
    summary_section: "short_summary",
    source_text: "",
    youtube_url: "",
    source_file: null,
    generate_audio: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const selectedType = inputTypes.find((item) => item.value === form.input_type);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    const payload = new FormData();
    Object.entries(form).forEach(([key, value]) => {
      if (value !== null && value !== "") {
        payload.append(key, value);
      }
    });

    try {
      const response = await api.post("/summaries/create/", payload, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setForm({
        title: "",
        input_type: "text",
        output_format: "paragraph",
        summary_section: "short_summary",
        source_text: "",
        youtube_url: "",
        source_file: null,
        generate_audio: true
      });
      onCreated(response.data);
      addToast("Summary created successfully.");
    } catch (requestError) {
      const responseError = requestError.response?.data;
      const message =
        getErrorMessage(responseError) ||
        "The summary could not be generated. Check the file type or YouTube link and try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card stack" onSubmit={handleSubmit}>
      <div className="panel-header">
        <div>
          <span className="pill">Create summary</span>
          <h2>Choose your source and summary type</h2>
          <p>{selectedType?.helper}</p>
        </div>
      </div>
      <label className="field-group">
        <span>Title</span>
        <input
          placeholder="Weekly research digest"
          value={form.title}
          onChange={(event) => setForm({ ...form, title: event.target.value })}
        />
      </label>
      <div className="grid-two">
        <label className="field-group">
          <span>Input type</span>
          <select
            value={form.input_type}
            onChange={(event) =>
              setForm({ ...form, input_type: event.target.value, source_text: "", youtube_url: "", source_file: null })
            }
          >
            {inputTypes.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className="field-group">
        <span>Summary section</span>
        <select
          value={form.summary_section}
          onChange={(event) => setForm({ ...form, summary_section: event.target.value })}
        >
          <option value="short_summary">Short Summary</option>
          <option value="key_points">Key Points</option>
        </select>
      </label>

      {form.input_type === "text" ? (
        <label className="field-group">
          <span>Source text</span>
          <textarea
            rows="10"
            placeholder="Paste or type the content you want summarized..."
            value={form.source_text}
            onChange={(event) => setForm({ ...form, source_text: event.target.value })}
          />
        </label>
      ) : null}

      {form.input_type === "youtube" ? (
        <label className="field-group">
          <span>YouTube URL</span>
          <input
            placeholder="https://www.youtube.com/watch?v=..."
            value={form.youtube_url}
            onChange={(event) => setForm({ ...form, youtube_url: event.target.value })}
          />
        </label>
      ) : null}

      {form.input_type === "pdf" || form.input_type === "image" ? (
        <label className="upload-zone">
          <span className="upload-title">{form.input_type === "pdf" ? "Upload a PDF" : "Upload an image"}</span>
          <span className="upload-copy">
            {form.source_file?.name || "Choose a file to extract text and generate a summary."}
          </span>
          <input
            type="file"
            accept={form.input_type === "pdf" ? ".pdf" : "image/*"}
            onChange={(event) => setForm({ ...form, source_file: event.target.files?.[0] ?? null })}
          />
        </label>
      ) : null}

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.generate_audio}
          onChange={(event) => setForm({ ...form, generate_audio: event.target.checked })}
        />
        Create speech output
      </label>

      {error ? <div className="error-text">{error}</div> : null}
      <button className="primary-button" type="submit" disabled={loading}>
        {loading ? "Generating..." : "Generate summary"}
      </button>
    </form>
  );
}
