from django.contrib import admin

from .models import Intake


@admin.register(Intake)
class IntakeAdmin(admin.ModelAdmin):
    list_display = ["name", "university", "program", "application_deadline", "start_date"]
    list_filter = ["university", "program", "start_date"]
    search_fields = ["name", "university__name", "program__name"]
