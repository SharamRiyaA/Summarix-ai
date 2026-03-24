from django.conf import settings
from django.db import models


class SummaryRecord(models.Model):
    class InputType(models.TextChoices):
        TEXT = "text", "Text"
        PDF = "pdf", "PDF"
        IMAGE = "image", "Image"
        YOUTUBE = "youtube", "YouTube"

    class OutputFormat(models.TextChoices):
        PARAGRAPH = "paragraph", "Paragraph"
        BULLETS = "bullets", "Bullets"

    class SummarySection(models.TextChoices):
        SHORT_SUMMARY = "short_summary", "Short Summary"
        KEY_POINTS = "key_points", "Key Points"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="summary_records")
    title = models.CharField(max_length=255, blank=True)
    input_type = models.CharField(max_length=20, choices=InputType.choices)
    output_format = models.CharField(max_length=20, choices=OutputFormat.choices, default=OutputFormat.PARAGRAPH)
    summary_section = models.CharField(
        max_length=20,
        choices=SummarySection.choices,
        default=SummarySection.SHORT_SUMMARY,
    )
    source_text = models.TextField(blank=True)
    source_file = models.FileField(upload_to="uploads/", blank=True, null=True)
    youtube_url = models.URLField(blank=True)
    extracted_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    audio_file = models.FileField(upload_to="speech/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"{self.input_type} summary #{self.pk}"
