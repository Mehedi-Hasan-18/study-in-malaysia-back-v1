from datetime import date
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from accounts.models import User
from common.models import Country, State
from faculties.models import Faculty
from intakes.models import Intake
from programs.models import Program
from universities.models import University
from documents.models import ApplicationDocument

from .models import Application


class ApplicationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            firebase_uid="application-user",
            email="applicant@example.com",
            full_name="Applicant User",
        )
        self.client.force_authenticate(user=self.user)
        country = Country.objects.create(name="Malaysia", code="MY")
        state = State.objects.create(country=country, name="Selangor")
        university = University.objects.create(
            name="Application University",
            slug="application-university",
            short_description="Short",
            full_description="Full",
            university_type=University.TYPE_PRIVATE,
            state=state,
        )
        faculty = Faculty.objects.create(university=university, name="Computing")
        self.program = Program.objects.create(
            faculty=faculty,
            university=university,
            name="BSc Computing",
            slug="bsc-computing-application",
            level=Program.LEVEL_BACHELOR,
            duration_months=36,
        )
        self.intake = Intake.objects.create(
            university=university,
            program=self.program,
            name="January 2027",
            application_deadline=date(2026, 12, 1),
            start_date=date(2027, 1, 10),
        )

    def test_create_and_submit_application(self):
        create_response = self.client.post(
            "/api/v1/applications/",
            {"program": self.program.id, "intake": self.intake.id},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)

        application_id = create_response.data["id"]
        submit_response = self.client.post(f"/api/v1/applications/{application_id}/submit/")

        self.assertEqual(submit_response.status_code, 200)
        self.assertEqual(submit_response.data["data"]["status"], Application.STATUS_SUBMITTED)

    @patch("documents.signals.delete_file")
    @patch("applications.views.upload_file")
    def test_upload_and_delete_application_document(self, mocked_upload, mocked_delete):
        mocked_upload.return_value = {
            "public_id": "applications/1/passport/file.pdf",
            "secure_url": "https://res.cloudinary.com/demo/raw/upload/file.pdf",
            "resource_type": "raw",
            "format": "pdf",
        }
        application = Application.objects.create(user=self.user, program=self.program, intake=self.intake)
        file_obj = SimpleUploadedFile("passport.pdf", b"%PDF-1.4", content_type="application/pdf")

        upload_response = self.client.post(
            f"/api/v1/applications/{application.id}/documents/",
            {"document_type": "passport", "resource_type": "raw", "file": file_obj},
            format="multipart",
        )

        self.assertEqual(upload_response.status_code, 201)
        document_id = upload_response.data["data"]["id"]
        self.assertEqual(ApplicationDocument.objects.count(), 1)

        delete_response = self.client.delete(f"/api/v1/documents/{document_id}/")

        self.assertEqual(delete_response.status_code, 204)
        mocked_delete.assert_called_once_with("applications/1/passport/file.pdf", resource_type="raw")

# Create your tests here.
