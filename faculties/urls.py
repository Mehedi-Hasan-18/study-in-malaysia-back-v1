from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FacultyViewSet

router = DefaultRouter()
router.register("faculties", FacultyViewSet, basename="faculty")

urlpatterns = [
    path("", include(router.urls)),
]
