from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsFirebaseAuthenticated

from .models import ApplicationDocument
from .serializers import ApplicationDocumentSerializer


class ApplicationDocumentViewSet(viewsets.GenericViewSet):
    serializer_class = ApplicationDocumentSerializer
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get_queryset(self):
        return ApplicationDocument.objects.filter(application__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
