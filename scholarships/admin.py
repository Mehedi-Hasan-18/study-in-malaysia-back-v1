from django.contrib import admin

from .models import Scholarship, ScholarshipApplication


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ["name", "university", "coverage_percentage", "eligible_level", "eligible_country", "application_deadline"]
    list_filter = ["university", "eligible_level", "eligible_country", "application_deadline"]
    search_fields = ["name", "description", "eligible_country"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ["scholarship", "user", "applied_at"]
    list_filter = ["scholarship", "applied_at"]
    search_fields = ["scholarship__name", "user__email"]
