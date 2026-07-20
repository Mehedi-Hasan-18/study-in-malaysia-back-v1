from django.db import models


class Program(models.Model):
    LEVEL_DIPLOMA = "diploma"
    LEVEL_BACHELOR = "bachelor"
    LEVEL_MASTER = "master"
    LEVEL_PHD = "phd"
    LEVEL_CHOICES = [
        (LEVEL_DIPLOMA, "Diploma"),
        (LEVEL_BACHELOR, "Bachelor"),
        (LEVEL_MASTER, "Master"),
        (LEVEL_PHD, "PhD"),
    ]

    faculty = models.ForeignKey(
        "faculties.Faculty",
        on_delete=models.CASCADE,
        related_name="programs",
    )
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.CASCADE,
        related_name="programs",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    level = models.CharField(choices=LEVEL_CHOICES, max_length=20)
    duration_months = models.DecimalField(max_digits=6, decimal_places=2)
    language = models.CharField(max_length=50, default="English")
    description = models.TextField(blank=True)
    tuition_fee_display = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "program"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["university"]),
            models.Index(fields=["faculty"]),
            models.Index(fields=["level"]),
        ]

    def __str__(self):
        return self.name


class ProgramRequirement(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="requirements")
    requirement_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "program_requirement"
        ordering = ["id"]

    def __str__(self):
        return f"{self.program.name}: {self.requirement_type}"
