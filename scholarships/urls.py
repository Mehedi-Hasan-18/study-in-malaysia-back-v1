from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ScholarshipViewSet, my_scholarships

router = DefaultRouter()
router.register("scholarships", ScholarshipViewSet, basename="scholarship")

urlpatterns = [
    path("", include(router.urls)),
    path("my-scholarships/", my_scholarships, name="my-scholarships"),
]
