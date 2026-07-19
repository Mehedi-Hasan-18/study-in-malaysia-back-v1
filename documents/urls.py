from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApplicationDocumentViewSet

router = DefaultRouter()
router.register("documents", ApplicationDocumentViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
]
