from rest_framework.test import APITestCase

from .models import Inquiry


class ContentTests(APITestCase):
    def test_contact_creates_inquiry(self):
        response = self.client.post(
            "/api/v1/contact/",
            {"name": "Student", "email": "student@example.com", "message": "Need help"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Inquiry.objects.count(), 1)

# Create your tests here.
