from rest_framework import serializers

from .models import Program, ProgramRequirement


class ProgramRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramRequirement
        fields = ["id", "program", "requirement_type", "description"]


class ProgramSerializer(serializers.ModelSerializer):
    requirements = ProgramRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = [
            "id",
            "faculty",
            "university",
            "name",
            "slug",
            "level",
            "duration_months",
            "language",
            "description",
            "tuition_fee_display",
            "requirements",
        ]
