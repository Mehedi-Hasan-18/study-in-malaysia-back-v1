from rest_framework import serializers

from common.fields import CommaDecimalSerializerField

from .models import TuitionFee


class TuitionFeeSerializer(serializers.ModelSerializer):
    tuition_amount = CommaDecimalSerializerField(max_digits=10, decimal_places=2)
    registration_fee = CommaDecimalSerializerField(max_digits=10, decimal_places=2, required=False)
    misc_fee = CommaDecimalSerializerField(max_digits=10, decimal_places=2, required=False)
    bdt_equivalent = CommaDecimalSerializerField(max_digits=12, decimal_places=2, required=False, allow_null=True)

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
