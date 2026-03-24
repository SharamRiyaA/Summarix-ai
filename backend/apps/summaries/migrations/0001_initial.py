from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SummaryRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, max_length=255)),
                ("input_type", models.CharField(choices=[("text", "Text"), ("pdf", "PDF"), ("image", "Image"), ("youtube", "YouTube")], max_length=20)),
                ("output_format", models.CharField(choices=[("paragraph", "Paragraph"), ("bullets", "Bullets")], default="paragraph", max_length=20)),
                ("source_text", models.TextField(blank=True)),
                ("source_file", models.FileField(blank=True, null=True, upload_to="uploads/")),
                ("youtube_url", models.URLField(blank=True)),
                ("extracted_text", models.TextField(blank=True)),
                ("summary", models.TextField(blank=True)),
                ("audio_file", models.FileField(blank=True, null=True, upload_to="speech/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="summary_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
