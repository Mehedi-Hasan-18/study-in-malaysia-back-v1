from rest_framework import viewsets

from .models import Faculty
from .serializers import FacultySerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.select_related("university").all()
    serializer_class = FacultySerializer
    filterset_fields = ["university"]
    search_fields = ["name", "description", "university__name"]
    ordering_fields = ["name"]
