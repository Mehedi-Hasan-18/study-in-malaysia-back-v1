from django.contrib import admin

from .models import WishlistScholarship, WishlistUniversity


@admin.register(WishlistUniversity)
class WishlistUniversityAdmin(admin.ModelAdmin):
    list_display = ["user", "university", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "university__name"]


@admin.register(WishlistScholarship)
class WishlistScholarshipAdmin(admin.ModelAdmin):
    list_display = ["user", "scholarship", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "scholarship__name"]
