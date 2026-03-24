from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import SummaryRecord
from .serializers import SummaryCreateSerializer, SummaryDetailSerializer, SummaryListSerializer
from .services import extract_content, generate_speech, summarize_text


class SummaryListView(generics.ListAPIView):
    serializer_class = SummaryListSerializer

    def get_queryset(self):
        return SummaryRecord.objects.filter(user=self.request.user)


class SummaryDetailView(generics.RetrieveAPIView):
    serializer_class = SummaryDetailSerializer

    def get_queryset(self):
        return SummaryRecord.objects.filter(user=self.request.user)


class SummaryCreateView(generics.CreateAPIView):
    serializer_class = SummaryCreateSerializer

    def perform_create(self, serializer):
        generate_audio = serializer.validated_data.pop("generate_audio", False)
        record = serializer.save(user=self.request.user)
        try:
            extracted_text = extract_content(record)
            summary = summarize_text(
                extracted_text,
                record.output_format,
                record.input_type,
                record.summary_section,
            )

            record.extracted_text = extracted_text
            record.summary = summary
            if not record.title:
                record.title = extracted_text[:60] or f"{record.input_type.title()} Summary"
            if generate_audio:
                try:
                    generate_speech(record)
                except Exception:
                    record.audio_file = None
            record.save()
            self.record = record
        except ValidationError:
            record.delete()
            raise
        except Exception as exc:
            record.delete()
            raise ValidationError(str(exc))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = SummaryDetailSerializer(self.record, context={"request": request})
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)


class SummaryDeleteView(generics.DestroyAPIView):
    serializer_class = SummaryDetailSerializer

    def get_queryset(self):
        return SummaryRecord.objects.filter(user=self.request.user)
