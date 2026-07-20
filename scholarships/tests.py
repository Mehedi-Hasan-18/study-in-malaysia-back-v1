from datetime import date

from rest_framework.test import APITestCase

from accounts.models import User
from wishlist.models import WishlistScholarship

from .models import Scholarship, ScholarshipApplication


class ScholarshipTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            firebase_uid="scholar-user",
            email="scholar@example.com",
            full_name="Scholar User",
        )
        self.client.force_authenticate(user=self.user)
        self.scholarship = Scholarship.objects.create(
            name="Engineering Merit",
            slug="engineering-merit",
            description="Merit scholarship",
            coverage_percentage=100,
            eligible_level=["bachelor"],
            eligible_country="Bangladesh",
            application_deadline=date(2027, 1, 1),
        )

    def test_apply_creates_scholarship_application(self):
        response = self.client.post(f"/api/v1/scholarships/{self.scholarship.id}/apply/")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ScholarshipApplication.objects.count(), 1)

    def test_save_creates_wishlist_scholarship(self):
        response = self.client.post(f"/api/v1/scholarships/{self.scholarship.id}/save/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(WishlistScholarship.objects.count(), 1)

# Create your tests here.
