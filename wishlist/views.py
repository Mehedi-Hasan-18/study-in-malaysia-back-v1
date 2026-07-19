from rest_framework import mixins, viewsets
from rest_framework.authentication import SessionAuthentication

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsFirebaseAuthenticated

from .models import WishlistScholarship, WishlistUniversity
from .serializers import WishlistScholarshipSerializer, WishlistUniversitySerializer


class WishlistUniversityViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = WishlistUniversitySerializer
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get_queryset(self):
        return WishlistUniversity.objects.filter(user=self.request.user).select_related("university")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistScholarshipViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = WishlistScholarshipSerializer
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get_queryset(self):
        return WishlistScholarship.objects.filter(user=self.request.user).select_related("scholarship")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
