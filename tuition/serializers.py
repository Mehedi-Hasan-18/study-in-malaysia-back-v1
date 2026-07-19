from rest_framework import serializers

from .models import TuitionFee


class TuitionFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuitionFee
        fields = [
            "id",
            "program",
            "university",
            "tuition_amount",
            "registration_fee",
            "misc_fee",
            "currency",
            "bdt_equivalent",
            "academic_year",
            "pdf_public_id",
            "pdf_url",
        ]
