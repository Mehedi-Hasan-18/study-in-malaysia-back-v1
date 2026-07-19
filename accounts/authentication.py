import json
import os

import firebase_admin
from firebase_admin import auth, credentials
from rest_framework import authentication, exceptions

from .models import StudentProfile, User


def initialize_firebase():
    if firebase_admin._apps:
        return

    credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if credentials_json:
        cred = credentials.Certificate(json.loads(credentials_json))
        firebase_admin.initialize_app(cred)
        return

    firebase_admin.initialize_app()


class FirebaseAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed("Invalid Authorization header.")

        initialize_firebase()
        try:
            decoded_token = auth.verify_id_token(parts[1])
        except Exception as exc:
            raise exceptions.AuthenticationFailed("Invalid Firebase token.") from exc

        user = get_or_create_user_from_firebase(decoded_token)
        return (user, decoded_token)


def get_or_create_user_from_firebase(decoded_token):
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    full_name = decoded_token.get("name") or decoded_token.get("email", "")

    if not firebase_uid or not email:
        raise exceptions.AuthenticationFailed("Firebase token missing uid or email.")

    user, _ = User.objects.update_or_create(
        firebase_uid=firebase_uid,
        defaults={
            "email": email,
            "full_name": full_name,
        },
    )
    StudentProfile.objects.get_or_create(user=user)
    return user
