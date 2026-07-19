from rest_framework import serializers

from .models import Scholarship, ScholarshipApplication


class ScholarshipSerializer(serializers.ModelSerializer):
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
            "brochure_public_id",
            "brochure_url",
        ]


class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    scholarship_detail = ScholarshipSerializer(source="scholarship", read_only=True)

    class Meta:
        model = ScholarshipApplication
        fields = ["id", "scholarship", "scholarship_detail", "user", "applied_at"]
        read_only_fields = ["user", "applied_at", "scholarship_detail"]
