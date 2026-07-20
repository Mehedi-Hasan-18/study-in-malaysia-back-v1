from rest_framework import serializers

from common.serializers import CloudinaryUploadMixin

from .models import Scholarship, ScholarshipApplication


class ScholarshipSerializer(CloudinaryUploadMixin, serializers.ModelSerializer):
    brochure = serializers.FileField(write_only=True, required=False)

    cloudinary_upload_fields = {
        "brochure": {
            "folder": lambda instance: f"scholarships/{instance.id}/brochure/",
            "public_id_field": "brochure_public_id",
            "url_field": "brochure_url",
            "resource_type": "raw",
        },
    }

    class Meta:
        model = Scholarship
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "university",
            "coverage_percentage",
            "eligible_level",
            "eligible_country",
            "application_deadline",
            "brochure",
            "brochure_public_id",
            "brochure_url",
        ]
        read_only_fields = ["brochure_public_id", "brochure_url"]


class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    scholarship_detail = ScholarshipSerializer(source="scholarship", read_only=True)

    class Meta:
        model = ScholarshipApplication
        fields = ["id", "scholarship", "scholarship_detail", "user", "applied_at"]
        read_only_fields = ["user", "applied_at", "scholarship_detail"]
