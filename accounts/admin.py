from django.contrib import admin

from .models import StudentProfile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "firebase_uid", "date_joined"]
    search_fields = ["email", "full_name", "firebase_uid"]
    readonly_fields = ["date_joined"]


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "country"]
    search_fields = ["user__email", "user__full_name", "phone"]
    list_filter = ["country"]
