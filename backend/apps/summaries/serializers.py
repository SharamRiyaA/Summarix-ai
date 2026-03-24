from rest_framework import serializers

from .models import SummaryRecord


class SummaryCreateSerializer(serializers.ModelSerializer):
    generate_audio = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = SummaryRecord
        fields = (
            "id",
            "title",
            "input_type",
            "output_format",
            "summary_section",
            "source_text",
            "source_file",
            "youtube_url",
            "generate_audio",
        )

    def validate(self, attrs):
        input_type = attrs.get("input_type")
        source_text = attrs.get("source_text")
        source_file = attrs.get("source_file")
        youtube_url = attrs.get("youtube_url")

        if input_type == SummaryRecord.InputType.TEXT and not source_text:
            raise serializers.ValidationError("Text input requires source_text.")
        if input_type in [SummaryRecord.InputType.PDF, SummaryRecord.InputType.IMAGE] and not source_file:
            raise serializers.ValidationError("File input requires source_file.")
        if input_type == SummaryRecord.InputType.YOUTUBE and not youtube_url:
            raise serializers.ValidationError("YouTube input requires youtube_url.")
        return attrs


class SummaryListSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = SummaryRecord
        fields = (
            "id",
            "title",
            "input_type",
            "output_format",
            "summary_section",
            "youtube_url",
            "summary",
            "audio_url",
            "file_url",
            "created_at",
        )

    def get_audio_url(self, obj):
        request = self.context.get("request")
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return obj.audio_file.url if obj.audio_file else ""

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.source_file and request:
            return request.build_absolute_uri(obj.source_file.url)
        return obj.source_file.url if obj.source_file else ""


class SummaryDetailSerializer(SummaryListSerializer):
    class Meta(SummaryListSerializer.Meta):
        fields = SummaryListSerializer.Meta.fields + (
            "source_text",
            "extracted_text",
            "updated_at",
        )
