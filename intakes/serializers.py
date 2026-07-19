from rest_framework import serializers

from .models import Intake


class IntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intake
        fields = ["id", "university", "program", "name", "application_deadline", "start_date"]
