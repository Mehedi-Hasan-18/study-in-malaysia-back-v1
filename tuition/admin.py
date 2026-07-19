from django.contrib import admin
from django import forms

from common.cloudinary_utils import delete_file, upload_file

from .models import TuitionFee


class TuitionFeeAdminForm(forms.ModelForm):
    upload_pdf = forms.FileField(required=False, help_text="Upload PDF to Cloudinary. Replaces existing PDF.")

    class Meta:
        model = TuitionFee
        fields = "__all__"

    def clean_upload_pdf(self):
        uploaded_pdf = self.cleaned_data.get("upload_pdf")
        if uploaded_pdf and not uploaded_pdf.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        return uploaded_pdf


@admin.register(TuitionFee)
class TuitionFeeAdmin(admin.ModelAdmin):
    form = TuitionFeeAdminForm
    list_display = [
        "program",
        "university",
        "tuition_amount",
        "currency",
        "academic_year",
        "pdf_url",
    ]
    list_filter = ["university", "program", "currency", "academic_year"]
    search_fields = ["program__name", "university__name", "academic_year"]
    readonly_fields = ["pdf_public_id", "pdf_url"]

    def save_model(self, request, obj, form, change):
        uploaded_pdf = form.cleaned_data.get("upload_pdf")
        old_public_id = None
        if uploaded_pdf and obj.pk:
            old_public_id = TuitionFee.objects.filter(pk=obj.pk).values_list("pdf_public_id", flat=True).first()

        if uploaded_pdf:
            result = upload_file(
                uploaded_pdf,
                f"fees/{obj.university_id}/{obj.program_id}/",
                resource_type="raw",
            )
            obj.pdf_public_id = result["public_id"]
            obj.pdf_url = result["secure_url"]

        super().save_model(request, obj, form, change)

        if uploaded_pdf and old_public_id and old_public_id != obj.pdf_public_id:
            delete_file(old_public_id, resource_type="raw")
