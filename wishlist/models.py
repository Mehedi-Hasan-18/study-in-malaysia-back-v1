from django.db import models


class WishlistUniversity(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="saved_universities")
    university = models.ForeignKey("universities.University", on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist_university"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "university"], name="unique_wishlist_university"),
        ]
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.email} saved {self.university.name}"


class WishlistScholarship(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="saved_scholarships")
    scholarship = models.ForeignKey("scholarships.Scholarship", on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist_scholarship"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "scholarship"], name="unique_wishlist_scholarship"),
        ]
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.email} saved {self.scholarship.name}"
