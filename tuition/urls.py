from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TuitionFeeViewSet

router = DefaultRouter()
router.register("fees", TuitionFeeViewSet, basename="fee")

urlpatterns = [
    path("", include(router.urls)),
]
