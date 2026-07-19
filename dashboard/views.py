from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

from accounts.authentication import FirebaseAuthentication
from accounts.permissions import IsFirebaseAuthenticated
from applications.models import Application
from applications.serializers import ApplicationSerializer


class DashboardView(APIView):
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        applications = Application.objects.filter(user=request.user)
        return Response(
            {
                "data": {
                    "statistics": {
                        "total_applications": applications.count(),
                        "submitted_applications": applications.exclude(status=Application.STATUS_DRAFT).count(),
                        "approved_applications": applications.filter(status=Application.STATUS_APPROVED).count(),
                    },
                    "profile_completion": calculate_profile_completion(request.user),
                }
            }
        )


class RecentApplicationsView(APIView):
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        queryset = Application.objects.filter(user=request.user).select_related("program", "intake")[:5]
        return Response({"data": ApplicationSerializer(queryset, many=True).data})


class StatisticsView(APIView):
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        applications = Application.objects.filter(user=request.user)
        return Response(
            {
                "data": {
                    "total": applications.count(),
                    "draft": applications.filter(status=Application.STATUS_DRAFT).count(),
                    "submitted": applications.filter(status=Application.STATUS_SUBMITTED).count(),
                    "under_review": applications.filter(status=Application.STATUS_UNDER_REVIEW).count(),
                    "approved": applications.filter(status=Application.STATUS_APPROVED).count(),
                    "rejected": applications.filter(status=Application.STATUS_REJECTED).count(),
                }
            }
        )


class ProfileCompletionView(APIView):
    authentication_classes = [FirebaseAuthentication, SessionAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        return Response({"data": calculate_profile_completion(request.user)})


def calculate_profile_completion(user):
    profile = user.profile
    fields = {
        "full_name": bool(user.full_name),
        "email": bool(user.email),
        "phone": bool(profile.phone),
        "country": bool(profile.country_id),
        "photo": bool(profile.photo_url),
    }
    completed = sum(fields.values())
    return {
        "completed_fields": completed,
        "total_fields": len(fields),
        "percentage": int((completed / len(fields)) * 100),
        "fields": fields,
    }
