from django.db import models


class ApplicationDocument(models.Model):
    DOC_PASSPORT = "passport"
    DOC_TRANSCRIPT = "transcript"
    DOC_CERTIFICATE = "certificate"
    DOC_ENGLISH_TEST = "english_test"
    DOC_PERSONAL_STATEMENT = "personal_statement"
    DOC_RESUME = "resume"
    DOC_OTHER = "other"
    DOC_TYPES = [
        (DOC_PASSPORT, "Passport"),
        (DOC_TRANSCRIPT, "Academic Transcript"),
        (DOC_CERTIFICATE, "Certificate"),
        (DOC_ENGLISH_TEST, "English Test"),
        (DOC_PERSONAL_STATEMENT, "Personal Statement"),
        (DOC_RESUME, "Resume"),
        (DOC_OTHER, "Other"),
    ]
    RESOURCE_IMAGE = "image"
    RESOURCE_RAW = "raw"
    RESOURCE_CHOICES = [
        (RESOURCE_IMAGE, "Image"),
        (RESOURCE_RAW, "Raw"),
    ]

    application = models.ForeignKey(
        "applications.Application",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(choices=DOC_TYPES, max_length=30)
    file_public_id = models.CharField(max_length=255)
    file_url = models.URLField()
    resource_type = models.CharField(choices=RESOURCE_CHOICES, max_length=10)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "application_document"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["application"]),
        ]

    def __str__(self):
        return f"{self.application_id} - {self.document_type}"
