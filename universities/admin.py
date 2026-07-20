from django.contrib import admin
from django import forms

from common.cloudinary_utils import delete_file, upload_file

from .models import Gallery, University


class UniversityAdminForm(forms.ModelForm):
    logo = forms.ImageField(required=False, help_text="Upload logo to Cloudinary. Replaces existing logo.")
    cover = forms.ImageField(required=False, help_text="Upload cover photo to Cloudinary. Replaces existing cover photo.")

    class Meta:
        model = University
        fields = "__all__"


class GalleryAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False, help_text="Upload gallery image to Cloudinary. Replaces existing image.")

    class Meta:
        model = Gallery
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and not cleaned_data.get("image"):
            raise forms.ValidationError("Upload image is required.")
        return cleaned_data

    def save(self, commit=True):
        image = self.cleaned_data.get("image")
        old_public_id = ""
        if image and self.instance.pk:
            old_public_id = Gallery.objects.filter(pk=self.instance.pk).values_list("image_public_id", flat=True).first()

        instance = super().save(commit=False)
        if image:
            result = upload_file(image, f"universities/{instance.university_id}/gallery/", resource_type="image")
            instance.image_public_id = result["public_id"]
            instance.image_url = result["secure_url"]

        if commit:
            instance.save()
            if image and old_public_id and old_public_id != instance.image_public_id:
                delete_file(old_public_id, resource_type="image")

        return instance


class GalleryInline(admin.TabularInline):
    model = Gallery
    form = GalleryAdminForm
    extra = 0
    readonly_fields = ["image_public_id", "image_url"]


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    form = UniversityAdminForm
    list_display = ["name", "university_type", "state", "city", "is_featured", "ranking_tier"]
    list_filter = ["university_type", "state", "city", "is_featured"]
    search_fields = ["name", "short_description", "ranking_tier"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [GalleryInline]
    readonly_fields = ["logo_public_id", "logo_url", "cover_public_id", "cover_url"]

    def save_model(self, request, obj, form, change):
        logo = form.cleaned_data.get("logo")
        cover = form.cleaned_data.get("cover")
        old_logo_public_id = None
        old_cover_public_id = None

        if change:
            old_values = University.objects.filter(pk=obj.pk).values("logo_public_id", "cover_public_id").first()
            if old_values:
                old_logo_public_id = old_values["logo_public_id"]
                old_cover_public_id = old_values["cover_public_id"]

        super().save_model(request, obj, form, change)

        updated_fields = []
        if logo:
            result = upload_file(logo, f"universities/{obj.id}/logo/", resource_type="image")
            obj.logo_public_id = result["public_id"]
            obj.logo_url = result["secure_url"]
            updated_fields.extend(["logo_public_id", "logo_url"])
            if old_logo_public_id and old_logo_public_id != obj.logo_public_id:
                delete_file(old_logo_public_id, resource_type="image")

        if cover:
            result = upload_file(cover, f"universities/{obj.id}/cover/", resource_type="image")
            obj.cover_public_id = result["public_id"]
            obj.cover_url = result["secure_url"]
            updated_fields.extend(["cover_public_id", "cover_url"])
            if old_cover_public_id and old_cover_public_id != obj.cover_public_id:
                delete_file(old_cover_public_id, resource_type="image")

        if updated_fields:
            obj.save(update_fields=updated_fields)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    form = GalleryAdminForm
    list_display = ["university", "caption", "display_order"]
    list_filter = ["university"]
    search_fields = ["university__name", "caption"]
    readonly_fields = ["image_public_id", "image_url"]

    def save_model(self, request, obj, form, change):
        image = form.cleaned_data.get("image")
        old_public_id = None
        if image and change:
            old_public_id = Gallery.objects.filter(pk=obj.pk).values_list("image_public_id", flat=True).first()

        if image:
            result = upload_file(image, f"universities/{obj.university_id}/gallery/", resource_type="image")
            obj.image_public_id = result["public_id"]
            obj.image_url = result["secure_url"]

        super().save_model(request, obj, form, change)

        if image and old_public_id and old_public_id != obj.image_public_id:
            delete_file(old_public_id, resource_type="image")
