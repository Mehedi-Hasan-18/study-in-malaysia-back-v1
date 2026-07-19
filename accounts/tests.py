from unittest.mock import patch

from rest_framework.test import APITestCase

from .models import StudentProfile, User


class FirebaseLoginTests(APITestCase):
    @patch("accounts.views.initialize_firebase")
    @patch("accounts.views.auth.verify_id_token")
    def test_firebase_login_creates_user_and_profile(self, mocked_verify, mocked_initialize):
        mocked_verify.return_value = {
            "uid": "firebase-123",
            "email": "student@example.com",
            "name": "Student User",
        }

        response = self.client.post("/api/v1/auth/firebase-login/", {"id_token": "token"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(StudentProfile.objects.count(), 1)
        self.assertEqual(response.data["data"]["user"]["email"], "student@example.com")
        mocked_initialize.assert_called_once()
        mocked_verify.assert_called_once_with("token")

# Create your tests here.
