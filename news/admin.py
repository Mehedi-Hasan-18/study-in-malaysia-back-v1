from django.contrib import admin

from .models import Blog, FAQ, Inquiry, News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["title", "published_at"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ["title"]}
    list_filter = ["published_at"]


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
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
