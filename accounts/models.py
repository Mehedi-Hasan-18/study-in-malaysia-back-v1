from django.db import models


class User(models.Model):
    firebase_uid = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_user"
        ordering = ["-date_joined"]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_staff(self):
        return False

    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    country = models.ForeignKey("common.Country", on_delete=models.SET_NULL, null=True, blank=True)
    photo_public_id = models.CharField(max_length=255, blank=True)
    photo_url = models.URLField(blank=True)

    class Meta:
        db_table = "student_profile"

    def __str__(self):
        return f"{self.user.email} profile"
