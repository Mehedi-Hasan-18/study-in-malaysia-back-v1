from django.contrib import admin

from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ["name", "university"]
    list_filter = ["university"]
    search_fields = ["name", "university__name"]
