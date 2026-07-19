from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "user",
            "program",
            "intake",
            "status",
            "submitted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "status", "submitted_at", "created_at", "updated_at"]


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "status", "submitted_at", "updated_at"]
