from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IntakeViewSet

router = DefaultRouter()
router.register("intakes", IntakeViewSet, basename="intake")

urlpatterns = [
    path("", include(router.urls)),
]
