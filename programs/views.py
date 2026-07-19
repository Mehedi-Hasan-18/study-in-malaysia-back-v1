from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsStaffOrReadOnly
from tuition.models import TuitionFee
from tuition.serializers import TuitionFeeSerializer

from .filters import ProgramFilter
from .models import Program, ProgramRequirement
from .serializers import ProgramRequirementSerializer, ProgramSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related("faculty", "university").prefetch_related("requirements").all()
    serializer_class = ProgramSerializer
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsStaffOrReadOnly]
    filterset_class = ProgramFilter
    search_fields = ["name", "description", "university__name", "faculty__name"]
    ordering_fields = ["name", "duration_months", "tuition_fee_display"]

    @action(detail=True, methods=["get"])
    def requirements(self, request, pk=None):
        queryset = ProgramRequirement.objects.filter(program_id=pk)
        serializer = ProgramRequirementSerializer(queryset, many=True)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get"])
    def fees(self, request, pk=None):
        queryset = TuitionFee.objects.filter(program_id=pk).select_related("university")
        serializer = TuitionFeeSerializer(queryset, many=True)
        return Response({"data": serializer.data})
