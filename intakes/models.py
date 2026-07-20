from django.db import models


class Intake(models.Model):
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.CASCADE,
        related_name="intakes",
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intakes",
    )
    name = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "intake"
        ordering = ["start_date", "name"]
        indexes = [
            models.Index(fields=["university"]),
            models.Index(fields=["program"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.university.name}"
