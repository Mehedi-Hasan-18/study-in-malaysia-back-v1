from decimal import Decimal, InvalidOperation

from django.db.models import Max
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsStaffOrReadOnly
from common.cloudinary_utils import upload_file
from common.fields import normalize_number
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
    parser_classes = [JSONParser, FormParser, MultiPartParser]
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

    @action(detail=True, methods=["get", "post"])
    def gallery(self, request, pk=None):
        if request.method == "POST":
            university = self.get_object()
            images = (
                request.FILES.getlist("images")
                or request.FILES.getlist("images[]")
                or request.FILES.getlist("image")
                or request.FILES.getlist("files")
                or request.FILES.getlist("files[]")
            )
            if not images:
                return Response({"error": "images is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                start_order = Decimal(normalize_number(request.data.get("display_order", "")))
            except (InvalidOperation, TypeError):
                max_order = Gallery.objects.filter(university=university).aggregate(Max("display_order"))["display_order__max"]
                start_order = (max_order or 0) + 1

            created_gallery = []
            for index, image in enumerate(images):
                result = upload_file(image, f"universities/{university.id}/gallery/", resource_type="image")
                created_gallery.append(
                    Gallery.objects.create(
                        university=university,
                        image_public_id=result["public_id"],
                        image_url=result["secure_url"],
                        caption=request.data.get("caption", ""),
                        display_order=start_order + index,
                    )
                )

            serializer = GallerySerializer(created_gallery, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)

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
