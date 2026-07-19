from rest_framework import viewsets

from .models import Intake
from .serializers import IntakeSerializer


class IntakeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Intake.objects.select_related("university", "program").all()
    serializer_class = IntakeSerializer
    filterset_fields = ["university", "program"]
    search_fields = ["name", "university__name", "program__name"]
    ordering_fields = ["application_deadline", "start_date", "name"]
