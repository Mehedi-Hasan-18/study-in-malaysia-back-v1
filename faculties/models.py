from django.db import models


class Faculty(models.Model):
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.CASCADE,
        related_name="faculties",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "faculty"
        ordering = ["name"]
        verbose_name_plural = "faculties"
        indexes = [
            models.Index(fields=["university"]),
        ]

    def __str__(self):
        return self.name
