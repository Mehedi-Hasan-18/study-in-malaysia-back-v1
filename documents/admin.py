from django.contrib import admin

from .models import ApplicationDocument


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ["application", "document_type", "resource_type", "uploaded_at"]
    list_filter = ["document_type", "resource_type", "uploaded_at"]
    search_fields = ["application__user__email", "file_public_id"]
