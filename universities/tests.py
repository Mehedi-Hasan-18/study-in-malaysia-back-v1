from rest_framework.test import APITestCase

from common.models import City, Country, State
from faculties.models import Faculty
from programs.models import Program

from .models import University


class UniversityCatalogTests(APITestCase):
    def test_university_programs_endpoint_returns_programs(self):
        country = Country.objects.create(name="Malaysia", code="MY")
        state = State.objects.create(country=country, name="Selangor")
        city = City.objects.create(state=state, name="Cyberjaya")
        university = University.objects.create(
            name="Cyberjaya University",
            slug="cyberjaya-university",
            short_description="Tech university",
            full_description="Technology focused university.",
            university_type=University.TYPE_PRIVATE,
            state=state,
            city=city,
        )
        faculty = Faculty.objects.create(university=university, name="Computing")
        Program.objects.create(
            faculty=faculty,
            university=university,
            name="Diploma in Computer Science",
            slug="diploma-computer-science",
            level=Program.LEVEL_DIPLOMA,
            duration_months=36,
        )
        Program.objects.create(
            faculty=faculty,
            university=university,
            name="Bachelor of Software Engineering",
            slug="bachelor-software-engineering",
            level=Program.LEVEL_BACHELOR,
            duration_months=48,
        )

        response = self.client.get(f"/api/v1/universities/{university.id}/programs/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["count"], 2)

# Create your tests here.
