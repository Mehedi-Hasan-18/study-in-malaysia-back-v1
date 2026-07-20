from django.contrib import admin

from common.admin import CommaDecimalAdminMixin

from .models import Program, ProgramRequirement


class ProgramRequirementInline(admin.TabularInline):
    model = ProgramRequirement
    extra = 0


@admin.register(Program)
class ProgramAdmin(CommaDecimalAdminMixin, admin.ModelAdmin):
    list_display = ["name", "level", "university", "faculty", "duration_months", "tuition_fee_display"]
    list_filter = ["level", "university", "faculty"]
    search_fields = ["name", "description", "university__name", "faculty__name"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProgramRequirementInline]


@admin.register(ProgramRequirement)
class ProgramRequirementAdmin(admin.ModelAdmin):
    list_display = ["program", "requirement_type"]
    list_filter = ["requirement_type"]
    search_fields = ["program__name", "description"]
