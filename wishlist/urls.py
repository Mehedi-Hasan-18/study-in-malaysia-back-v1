from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WishlistScholarshipViewSet, WishlistUniversityViewSet

router = DefaultRouter()
router.register("wishlist/universities", WishlistUniversityViewSet, basename="wishlist-university")
router.register("wishlist/scholarships", WishlistScholarshipViewSet, basename="wishlist-scholarship")

urlpatterns = [
    path("", include(router.urls)),
]
