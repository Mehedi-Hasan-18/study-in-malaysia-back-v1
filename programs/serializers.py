from rest_framework import serializers

from common.fields import CommaDecimalSerializerField

from .models import Program, ProgramRequirement


class ProgramRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramRequirement
        fields = ["id", "program", "requirement_type", "description"]


class ProgramSerializer(serializers.ModelSerializer):
    requirements = ProgramRequirementSerializer(many=True, read_only=True)
    duration_months = CommaDecimalSerializerField(max_digits=6, decimal_places=2)
    tuition_fee_display = CommaDecimalSerializerField(max_digits=10, decimal_places=2, required=False, allow_null=True)

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
