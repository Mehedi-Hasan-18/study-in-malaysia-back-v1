from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsFirebaseAuthenticated
from common.cloudinary_utils import upload_file
from documents.models import ApplicationDocument
from documents.serializers import ApplicationDocumentSerializer
from notifications.models import Notification

from .models import Application
from .serializers import ApplicationSerializer, ApplicationStatusSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user).select_related("program", "intake")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        application = self.get_object()
        application.status = Application.STATUS_SUBMITTED
        application.submitted_at = timezone.now()
        application.save(update_fields=["status", "submitted_at", "updated_at"])
        Notification.objects.create(user=request.user, message="Your application has been submitted.")
        return Response({"data": ApplicationSerializer(application).data})

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        return Response({"data": ApplicationStatusSerializer(self.get_object()).data})

    @action(detail=False, methods=["get"])
    def history(self, request):
        queryset = self.get_queryset().exclude(status=Application.STATUS_DRAFT)
        page = self.paginate_queryset(queryset)
        serializer = ApplicationSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get", "post"], parser_classes=[MultiPartParser])
    def documents(self, request, pk=None):
        application = self.get_object()
        if request.method == "GET":
            serializer = ApplicationDocumentSerializer(application.documents.all(), many=True)
            return Response({"data": serializer.data})

        document_type = request.data.get("document_type")
        file_obj = request.FILES.get("file")
        if not document_type or not file_obj:
            return Response({"error": "document_type and file are required."}, status=status.HTTP_400_BAD_REQUEST)

        valid_types = {choice[0] for choice in ApplicationDocument.DOC_TYPES}
        if document_type not in valid_types:
            return Response({"error": "Invalid document_type."}, status=status.HTTP_400_BAD_REQUEST)

        resource_type = request.data.get("resource_type") or ApplicationDocument.RESOURCE_RAW
        if resource_type not in {ApplicationDocument.RESOURCE_IMAGE, ApplicationDocument.RESOURCE_RAW}:
            return Response({"error": "Invalid resource_type."}, status=status.HTTP_400_BAD_REQUEST)

        result = upload_file(file_obj, f"applications/{application.id}/{document_type}/", resource_type=resource_type)
        document = ApplicationDocument.objects.create(
            application=application,
            document_type=document_type,
            file_public_id=result["public_id"],
            file_url=result["secure_url"],
            resource_type=result["resource_type"],
        )
        return Response({"data": ApplicationDocumentSerializer(document).data}, status=status.HTTP_201_CREATED)
