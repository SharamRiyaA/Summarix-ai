from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("summaries", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="summaryrecord",
            name="summary_section",
            field=models.CharField(
                choices=[("short_summary", "Short Summary"), ("key_points", "Key Points")],
                default="short_summary",
                max_length=20,
            ),
        ),
    ]
