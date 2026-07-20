from django.contrib import admin
from django import forms

from common.cloudinary_utils import delete_file, upload_file

from .models import Blog, FAQ, Inquiry, News


class CoverUploadAdminForm(forms.ModelForm):
    cover = forms.ImageField(required=False, help_text="Upload cover image to Cloudinary. Replaces existing cover.")

    class Meta:
        fields = "__all__"


class NewsAdminForm(CoverUploadAdminForm):
    class Meta(CoverUploadAdminForm.Meta):
        model = News


class BlogAdminForm(CoverUploadAdminForm):
    class Meta(CoverUploadAdminForm.Meta):
        model = Blog


class CoverUploadAdminMixin:
    readonly_fields = ["cover_public_id", "cover_url"]

    def save_model(self, request, obj, form, change):
        cover = form.cleaned_data.get("cover")
        old_public_id = None
        if cover and change:
            old_public_id = obj.__class__.objects.filter(pk=obj.pk).values_list("cover_public_id", flat=True).first()

        super().save_model(request, obj, form, change)

        if cover:
            folder_name = obj.__class__.__name__.lower()
            result = upload_file(cover, f"{folder_name}/{obj.id}/cover/", resource_type="image")
            obj.cover_public_id = result["public_id"]
            obj.cover_url = result["secure_url"]
            obj.save(update_fields=["cover_public_id", "cover_url"])

            if old_public_id and old_public_id != obj.cover_public_id:
                delete_file(old_public_id, resource_type="image")


@admin.register(News)
class NewsAdmin(CoverUploadAdminMixin, admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ["title", "published_at"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ["title"]}
    list_filter = ["published_at"]


@admin.register(Blog)
class BlogAdmin(CoverUploadAdminMixin, admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ["title", "author", "published_at"]
    search_fields = ["title", "body", "author", "tags"]
    prepopulated_fields = {"slug": ["title"]}
    list_filter = ["published_at", "author"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "category", "display_order"]
    search_fields = ["question", "answer", "category"]
    list_filter = ["category"]


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "created_at"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["created_at"]
