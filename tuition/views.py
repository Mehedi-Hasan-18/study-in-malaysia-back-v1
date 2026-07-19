from django.shortcuts import redirect
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import TuitionFee
from .serializers import TuitionFeeSerializer


class TuitionFeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TuitionFee.objects.select_related("university", "program").all()
    serializer_class = TuitionFeeSerializer
    filterset_fields = ["university", "program", "currency", "academic_year"]
    search_fields = ["program__name", "university__name", "academic_year"]
    ordering_fields = ["tuition_amount", "academic_year"]

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        fee = self.get_object()
        if not fee.pdf_url:
            return Response({"error": "PDF is not available."}, status=status.HTTP_404_NOT_FOUND)
        return redirect(fee.pdf_url)
