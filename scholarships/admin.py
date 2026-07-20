from django.contrib import admin
from django import forms

from common.admin import CommaDecimalAdminMixin
from common.cloudinary_utils import delete_file, upload_file

from .models import Scholarship, ScholarshipApplication


class ScholarshipAdminForm(forms.ModelForm):
    brochure = forms.FileField(required=False, help_text="Upload brochure to Cloudinary. Replaces existing brochure.")
    eligible_level = forms.MultipleChoiceField(
        choices=Scholarship.ELIGIBLE_LEVEL_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Scholarship
        fields = "__all__"


class EligibleLevelFilter(admin.SimpleListFilter):
    title = "eligible level"
    parameter_name = "eligible_level"

    def lookups(self, request, model_admin):
        return Scholarship.ELIGIBLE_LEVEL_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(eligible_level__contains=[self.value()])
        return queryset


@admin.register(Scholarship)
class ScholarshipAdmin(CommaDecimalAdminMixin, admin.ModelAdmin):
    form = ScholarshipAdminForm
    list_display = ["name", "university", "coverage_percentage", "eligible_level", "eligible_country", "application_deadline"]
    list_filter = ["university", EligibleLevelFilter, "eligible_country", "application_deadline"]
    search_fields = ["name", "description", "eligible_country"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["brochure_public_id", "brochure_url"]

    def save_model(self, request, obj, form, change):
        brochure = form.cleaned_data.get("brochure")
        old_public_id = None
        if brochure and change:
            old_public_id = Scholarship.objects.filter(pk=obj.pk).values_list("brochure_public_id", flat=True).first()

        super().save_model(request, obj, form, change)

        if brochure:
            result = upload_file(brochure, f"scholarships/{obj.id}/brochure/", resource_type="raw")
            obj.brochure_public_id = result["public_id"]
            obj.brochure_url = result["secure_url"]
            obj.save(update_fields=["brochure_public_id", "brochure_url"])

            if old_public_id and old_public_id != obj.brochure_public_id:
                delete_file(old_public_id, resource_type="raw")


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ["scholarship", "user", "applied_at"]
    list_filter = ["scholarship", "applied_at"]
    search_fields = ["scholarship__name", "user__email"]
