from django.db import models


class Scholarship(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scholarships",
    )
    coverage_percentage = models.IntegerField()
    eligible_level = models.CharField(max_length=20)
    eligible_country = models.CharField(max_length=100, blank=True)
    application_deadline = models.DateField()
    brochure_public_id = models.CharField(max_length=255, blank=True)
    brochure_url = models.URLField(blank=True)

    class Meta:
        db_table = "scholarship"
        ordering = ["application_deadline", "name"]
        indexes = [
            models.Index(fields=["university"]),
            models.Index(fields=["eligible_country"]),
            models.Index(fields=["application_deadline"]),
        ]

    def __str__(self):
        return self.name


class ScholarshipApplication(models.Model):
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="scholarship_applications")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scholarship_application"
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["scholarship", "user"], name="unique_scholarship_application"),
        ]
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.scholarship.name}"
