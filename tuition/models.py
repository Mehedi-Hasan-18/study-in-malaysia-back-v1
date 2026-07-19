from django.db import models


class TuitionFee(models.Model):
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.CASCADE,
        related_name="fees",
    )
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.CASCADE,
        related_name="fees",
    )
    tuition_amount = models.DecimalField(max_digits=10, decimal_places=2)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    misc_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="MYR")
    bdt_equivalent = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    academic_year = models.CharField(max_length=20)
    pdf_public_id = models.CharField(max_length=255, blank=True)
    pdf_url = models.URLField(blank=True)

    class Meta:
        db_table = "tuition_fee"
        ordering = ["-academic_year", "program__name"]
        indexes = [
            models.Index(fields=["program"]),
            models.Index(fields=["university"]),
        ]

    def __str__(self):
        return f"{self.program.name} - {self.academic_year}"
