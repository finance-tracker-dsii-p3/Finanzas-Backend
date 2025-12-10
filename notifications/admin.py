"""
Admin configuration for notifications app
"""

from django.contrib import admin
from notifications.models import Notification, CustomReminder


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model"""

    list_display = ["id", "user", "notification_type", "title", "read", "sent_at", "created_at"]
    list_filter = ["notification_type", "read", "created_at", "related_object_type"]
    search_fields = ["user__username", "user__email", "title", "message"]
    readonly_fields = ["created_at", "updated_at", "sent_at", "read_timestamp"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Usuario", {"fields": ("user",)}),
        ("Contenido", {"fields": ("notification_type", "title", "message")}),
        (
            "Objeto Relacionado",
            {"fields": ("related_object_type", "related_object_id"), "classes": ("collapse",)},
        ),
        ("Programación y Envío", {"fields": ("scheduled_for", "sent_at")}),
        ("Lectura", {"fields": ("read", "read_timestamp")}),
        ("Auditoría", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(CustomReminder)
class CustomReminderAdmin(admin.ModelAdmin):
    """Admin configuration for CustomReminder model"""

    list_display = [
        "id",
        "user",
        "title",
        "reminder_date",
        "reminder_time",
        "is_sent",
        "is_read",
        "created_at",
    ]
    list_filter = ["is_sent", "is_read", "reminder_date"]
    search_fields = ["user__username", "user__email", "title", "message"]
    readonly_fields = ["created_at", "updated_at", "sent_at", "read_at", "notification"]
    date_hierarchy = "reminder_date"

    fieldsets = (
        ("Usuario", {"fields": ("user",)}),
        ("Contenido", {"fields": ("title", "message")}),
        ("Programación", {"fields": ("reminder_date", "reminder_time")}),
        ("Estado", {"fields": ("is_sent", "sent_at", "notification", "is_read", "read_at")}),
        ("Auditoría", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "notification")
