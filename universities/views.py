from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsStaffOrReadOnly
from faculties.models import Faculty
from faculties.serializers import FacultySerializer
from intakes.models import Intake
from intakes.serializers import IntakeSerializer
from programs.models import Program
from programs.serializers import ProgramSerializer
from scholarships.models import Scholarship
from scholarships.serializers import ScholarshipSerializer
from tuition.models import TuitionFee
from tuition.serializers import TuitionFeeSerializer

from .filters import UniversityFilter
from .models import Gallery, University
from .serializers import GallerySerializer, UniversitySerializer


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.select_related("state", "city").prefetch_related("gallery").all()
    serializer_class = UniversitySerializer
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsStaffOrReadOnly]
    filterset_class = UniversityFilter
    search_fields = ["name", "short_description", "full_description"]
    ordering_fields = ["name", "established_year", "total_students"]

    @action(detail=True, methods=["get"])
    def faculties(self, request, pk=None):
        queryset = Faculty.objects.filter(university_id=pk).order_by("name")
        page = self.paginate_queryset(queryset)
        serializer = FacultySerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get"])
    def programs(self, request, pk=None):
        queryset = Program.objects.filter(university_id=pk).order_by("name")
        page = self.paginate_queryset(queryset)
        serializer = ProgramSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get"])
    def gallery(self, request, pk=None):
        queryset = Gallery.objects.filter(university_id=pk).order_by("display_order", "id")
        page = self.paginate_queryset(queryset)
        serializer = GallerySerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get"])
    def intakes(self, request, pk=None):
        queryset = Intake.objects.filter(university_id=pk).select_related("program").order_by("start_date")
        page = self.paginate_queryset(queryset)
        serializer = IntakeSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get"])
    def fees(self, request, pk=None):
        queryset = TuitionFee.objects.filter(university_id=pk).select_related("program").order_by("-academic_year")
        page = self.paginate_queryset(queryset)
        serializer = TuitionFeeSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get"])
    def scholarships(self, request, pk=None):
        queryset = Scholarship.objects.filter(university_id=pk).order_by("application_deadline")
        page = self.paginate_queryset(queryset)
        serializer = ScholarshipSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})
