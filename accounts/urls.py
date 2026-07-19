from django.urls import path

from .views import FirebaseLoginView, LogoutView, MeView, ProfilePhotoView, ProfileView

urlpatterns = [
    path("auth/firebase-login/", FirebaseLoginView.as_view(), name="firebase-login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/photo/", ProfilePhotoView.as_view(), name="profile-photo"),
]
