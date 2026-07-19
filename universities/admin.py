from django.contrib import admin

from .models import Gallery, University


class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 0


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ["name", "university_type", "state", "city", "is_featured", "ranking_tier"]
    list_filter = ["university_type", "state", "city", "is_featured"]
    search_fields = ["name", "short_description", "ranking_tier"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [GalleryInline]


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ["university", "caption", "display_order"]
    list_filter = ["university"]
    search_fields = ["university__name", "caption"]
