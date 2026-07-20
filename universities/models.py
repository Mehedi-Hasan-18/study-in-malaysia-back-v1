from django.db import models


class University(models.Model):
    TYPE_PUBLIC = "public"
    TYPE_PRIVATE = "private"
    UNIVERSITY_TYPE_CHOICES = [
        (TYPE_PUBLIC, "Public"),
        (TYPE_PRIVATE, "Private"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    full_description = models.TextField(blank=True)
    university_type = models.CharField(choices=UNIVERSITY_TYPE_CHOICES, max_length=10)
    state = models.ForeignKey("common.State", on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey("common.City", on_delete=models.SET_NULL, null=True, blank=True)
    ranking_tier = models.CharField(max_length=50, blank=True)
    is_featured = models.BooleanField(default=False)
    logo_public_id = models.CharField(max_length=255, blank=True)
    logo_url = models.URLField(blank=True)
    cover_public_id = models.CharField(max_length=255, blank=True)
    cover_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    established_year = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_students = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "university"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["state"]),
            models.Index(fields=["city"]),
            models.Index(fields=["is_featured"]),
        ]

    def __str__(self):
        return self.name


class Gallery(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="gallery")
    image_public_id = models.CharField(max_length=255)
    image_url = models.URLField()
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        db_table = "gallery"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.university.name} gallery image"
