from django.contrib import admin

from .models import Application
from notifications.models import Notification


def notify_status(queryset, message):
    Notification.objects.bulk_create(
        [Notification(user=application.user, message=message) for application in queryset]
    )


@admin.action(description="Mark selected applications as under review")
def mark_under_review(modeladmin, request, queryset):
    queryset.update(status=Application.STATUS_UNDER_REVIEW)
    notify_status(queryset, "Your application is now under review.")


@admin.action(description="Approve selected applications")
def approve_applications(modeladmin, request, queryset):
    queryset.update(status=Application.STATUS_APPROVED)
    notify_status(queryset, "Your application has been approved.")


@admin.action(description="Reject selected applications")
def reject_applications(modeladmin, request, queryset):
    queryset.update(status=Application.STATUS_REJECTED)
    notify_status(queryset, "Your application has been rejected.")


@admin.action(description="Request more documents")
def request_more_documents(modeladmin, request, queryset):
    queryset.update(status=Application.STATUS_MORE_DOCS_NEEDED)
    notify_status(queryset, "More documents are required for your application.")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "program", "intake", "status", "submitted_at", "created_at"]
    list_filter = ["status", "program", "intake", "created_at"]
    search_fields = ["user__email", "program__name"]
    readonly_fields = ["created_at", "updated_at"]
    actions = [mark_under_review, approve_applications, reject_applications, request_more_documents]
