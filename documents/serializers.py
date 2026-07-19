from rest_framework import serializers

from .models import ApplicationDocument


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = [
            "id",
            "application",
            "document_type",
            "file_public_id",
            "file_url",
            "resource_type",
            "uploaded_at",
        ]
        read_only_fields = ["application", "file_public_id", "file_url", "resource_type", "uploaded_at"]
