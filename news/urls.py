from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BlogViewSet, ContactView, FAQViewSet, InquiryViewSet, NewsViewSet

router = DefaultRouter()
router.register("news", NewsViewSet, basename="news")
router.register("blogs", BlogViewSet, basename="blog")
router.register("faq", FAQViewSet, basename="faq")
router.register("inquiry", InquiryViewSet, basename="inquiry")

urlpatterns = [
    path("", include(router.urls)),
    path("contact/", ContactView.as_view(), name="contact"),
]
