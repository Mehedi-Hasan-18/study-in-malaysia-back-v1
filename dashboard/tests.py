from rest_framework.test import APITestCase

from accounts.models import StudentProfile, User


class DashboardTests(APITestCase):
    def test_profile_completion_endpoint(self):
        user = User.objects.create(firebase_uid="dash-user", email="dash@example.com", full_name="Dash User")
        StudentProfile.objects.create(user=user, phone="12345")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/v1/dashboard/profile-completion/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["completed_fields"], 3)

# Create your tests here.
