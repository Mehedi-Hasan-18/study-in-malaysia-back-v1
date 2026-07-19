from datetime import date

from rest_framework.test import APITestCase

from common.models import Country, State
from universities.models import University

from .models import Intake


class IntakeTests(APITestCase):
    def test_university_intakes_endpoint_returns_intakes(self):
        country = Country.objects.create(name="Malaysia", code="MY")
        state = State.objects.create(country=country, name="Selangor")
        university = University.objects.create(
            name="Test University",
            slug="test-university-intake",
            short_description="Short",
            full_description="Full",
            university_type=University.TYPE_PRIVATE,
            state=state,
        )
        Intake.objects.create(
            university=university,
            name="January 2027",
            application_deadline=date(2026, 12, 1),
            start_date=date(2027, 1, 15),
        )

        response = self.client.get(f"/api/v1/universities/{university.id}/intakes/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["count"], 1)

# Create your tests here.
