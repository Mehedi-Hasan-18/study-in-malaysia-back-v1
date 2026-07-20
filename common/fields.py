from decimal import Decimal

from django import forms
from rest_framework import serializers


def normalize_number(value):
    if isinstance(value, str):
        return value.replace(",", "").strip()
    return value


class CommaDecimalFormField(forms.DecimalField):
    widget = forms.TextInput

    def to_python(self, value):
        return super().to_python(normalize_number(value))


class CommaDecimalSerializerField(serializers.DecimalField):
    def to_internal_value(self, data):
        return super().to_internal_value(normalize_number(data))


def decimal_to_int(value):
    if value is None:
        return None
    return int(Decimal(value))
