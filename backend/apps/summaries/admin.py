from django.contrib import admin

from .models import SummaryRecord


@admin.register(SummaryRecord)
class SummaryRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "input_type", "output_format", "created_at")
    search_fields = ("title", "summary", "youtube_url", "user__username")
    list_filter = ("input_type", "output_format", "created_at")
