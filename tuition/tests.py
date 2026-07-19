from rest_framework.test import APITestCase

from common.models import Country, State
from faculties.models import Faculty
from programs.models import Program
from universities.models import University

from .models import TuitionFee


class TuitionFeeTests(APITestCase):
    def test_fee_download_redirects_to_pdf_url(self):
        country = Country.objects.create(name="Malaysia", code="MY")
        state = State.objects.create(country=country, name="Selangor")
        university = University.objects.create(
            name="Fee University",
            slug="fee-university",
            short_description="Short",
            full_description="Full",
            university_type=University.TYPE_PRIVATE,
            state=state,
        )
        faculty = Faculty.objects.create(university=university, name="Business")
        program = Program.objects.create(
            faculty=faculty,
            university=university,
            name="MBA",
            slug="mba-fee-test",
            level=Program.LEVEL_MASTER,
            duration_months=18,
        )
        fee = TuitionFee.objects.create(
            program=program,
            university=university,
            tuition_amount="25000.00",
            academic_year="2026/2027",
            pdf_public_id="fees/demo.pdf",
            pdf_url="https://res.cloudinary.com/demo/raw/upload/fees/demo.pdf",
        )

        response = self.client.get(f"/api/v1/fees/{fee.id}/download/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], fee.pdf_url)

# Create your tests here.
