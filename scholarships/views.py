from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsFirebaseAuthenticated, IsStaffOrReadOnly
from wishlist.models import WishlistScholarship

from .filters import ScholarshipFilter
from .models import Scholarship, ScholarshipApplication
from .serializers import ScholarshipApplicationSerializer, ScholarshipSerializer


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.select_related("university").all()
    serializer_class = ScholarshipSerializer
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsStaffOrReadOnly]
    filterset_class = ScholarshipFilter
    search_fields = ["name", "description", "eligible_country"]
    ordering_fields = ["application_deadline", "coverage_percentage", "name"]

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsFirebaseAuthenticated])
    def save(self, request, pk=None):
        scholarship = self.get_object()
        if request.method == "DELETE":
            WishlistScholarship.objects.filter(user=request.user, scholarship=scholarship).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        saved, created = WishlistScholarship.objects.get_or_create(user=request.user, scholarship=scholarship)
        return Response({"data": {"id": saved.id, "saved": True, "created": created}})

    @action(detail=True, methods=["post"], permission_classes=[IsFirebaseAuthenticated])
    def apply(self, request, pk=None):
        scholarship = self.get_object()
        application, created = ScholarshipApplication.objects.get_or_create(
            user=request.user,
            scholarship=scholarship,
        )
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({"data": ScholarshipApplicationSerializer(application).data}, status=status_code)


@api_view(["GET"])
@authentication_classes([FirebaseAuthentication, SessionAuthentication])
@permission_classes([IsFirebaseAuthenticated])
def my_scholarships(request):
    queryset = ScholarshipApplication.objects.filter(user=request.user).select_related("scholarship")
    serializer = ScholarshipApplicationSerializer(queryset, many=True)
    return Response({"data": serializer.data})
