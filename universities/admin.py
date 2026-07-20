from django.contrib import admin
from django import forms
from django.db.models import Max

from common.admin import CommaDecimalAdminMixin
from common.cloudinary_utils import delete_file, upload_file

from .models import Gallery, University


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]
        return [single_file_clean(data, initial)] if data else []


class UniversityAdminForm(forms.ModelForm):
    logo = forms.FileField(required=False, help_text="Upload logo to Cloudinary. Replaces existing logo.")
    cover = forms.FileField(required=False, help_text="Upload cover photo to Cloudinary. Replaces existing cover photo.")
    gallery_images = MultipleFileField(
        required=False,
        help_text="Upload multiple gallery photos to Cloudinary. New photos append after existing gallery.",
    )

    class Meta:
        model = University
        fields = "__all__"


class GalleryAdminForm(forms.ModelForm):
    image = MultipleFileField(required=False, help_text="Upload one or more gallery images to Cloudinary.")

    class Meta:
        model = Gallery
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and not cleaned_data.get("image"):
            raise forms.ValidationError("Upload image is required.")
        return cleaned_data

    def save(self, commit=True):
        images = self.cleaned_data.get("image", [])
        image = images[0] if images else None
        old_public_id = ""
        if image and self.instance.pk:
            old_public_id = Gallery.objects.filter(pk=self.instance.pk).values_list("image_public_id", flat=True).first()

        instance = super().save(commit=False)
        instance._extra_gallery_images = images[1:]
        instance._old_gallery_public_id = old_public_id

        if image:
            result = upload_file(image, f"universities/{instance.university_id}/gallery/", resource_type="image")
            instance.image_public_id = result["public_id"]
            instance.image_url = result["secure_url"]

        if commit:
            instance.save()
            for extra_index, extra_image in enumerate(instance._extra_gallery_images, start=1):
                result = upload_file(extra_image, f"universities/{instance.university_id}/gallery/", resource_type="image")
                Gallery.objects.create(
                    university=instance.university,
                    image_public_id=result["public_id"],
                    image_url=result["secure_url"],
                    caption=instance.caption,
                    display_order=instance.display_order + extra_index,
                )
            if image and old_public_id and old_public_id != instance.image_public_id:
                delete_file(old_public_id, resource_type="image")

        return instance


class GalleryInline(CommaDecimalAdminMixin, admin.TabularInline):
    model = Gallery
    form = GalleryAdminForm
    extra = 0
    readonly_fields = ["image_public_id", "image_url"]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for deleted_object in formset.deleted_objects:
            deleted_object.delete()

        for instance in instances:
            instance.save()
            for extra_index, extra_image in enumerate(getattr(instance, "_extra_gallery_images", []), start=1):
                result = upload_file(extra_image, f"universities/{instance.university_id}/gallery/", resource_type="image")
                Gallery.objects.create(
                    university=instance.university,
                    image_public_id=result["public_id"],
                    image_url=result["secure_url"],
                    caption=instance.caption,
                    display_order=instance.display_order + extra_index,
                )

            old_public_id = getattr(instance, "_old_gallery_public_id", "")
            if old_public_id and old_public_id != instance.image_public_id:
                delete_file(old_public_id, resource_type="image")

        formset.save_m2m()


@admin.register(University)
class UniversityAdmin(CommaDecimalAdminMixin, admin.ModelAdmin):
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
        gallery_images = form.cleaned_data.get("gallery_images", [])
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

        if gallery_images:
            max_order = Gallery.objects.filter(university=obj).aggregate(Max("display_order"))["display_order__max"]
            start_order = (max_order or 0) + 1
            for index, image in enumerate(gallery_images):
                result = upload_file(image, f"universities/{obj.id}/gallery/", resource_type="image")
                Gallery.objects.create(
                    university=obj,
                    image_public_id=result["public_id"],
                    image_url=result["secure_url"],
                    display_order=start_order + index,
                )


@admin.register(Gallery)
class GalleryAdmin(CommaDecimalAdminMixin, admin.ModelAdmin):
    form = GalleryAdminForm
    list_display = ["university", "caption", "display_order"]
    list_filter = ["university"]
    search_fields = ["university__name", "caption"]
    readonly_fields = ["image_public_id", "image_url"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        for extra_index, extra_image in enumerate(getattr(obj, "_extra_gallery_images", []), start=1):
            result = upload_file(extra_image, f"universities/{obj.university_id}/gallery/", resource_type="image")
            Gallery.objects.create(
                university=obj.university,
                image_public_id=result["public_id"],
                image_url=result["secure_url"],
                caption=obj.caption,
                display_order=obj.display_order + extra_index,
            )

        old_public_id = getattr(obj, "_old_gallery_public_id", "")
        if old_public_id and old_public_id != obj.image_public_id:
            delete_file(old_public_id, resource_type="image")
