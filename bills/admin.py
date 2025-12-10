"""
Configuración del admin para facturas
"""

from django.contrib import admin
from bills.models import Bill, BillReminder


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Configuración del admin para facturas"""

    list_display = [
        "provider",
        "amount",
        "due_date",
        "status",
        "is_recurring",
        "user",
        "created_at",
    ]

    list_filter = [
        "status",
        "is_recurring",
        "due_date",
        "created_at",
    ]

    search_fields = [
        "provider",
        "description",
        "user__username",
        "user__email",
    ]

    readonly_fields = [
        "payment_transaction",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("Información básica", {"fields": ("user", "provider", "amount", "due_date")}),
        ("Cuentas y categorías", {"fields": ("suggested_account", "category")}),
        ("Estado y pago", {"fields": ("status", "payment_transaction")}),
        ("Configuración", {"fields": ("reminder_days_before", "is_recurring", "description")}),
        ("Fechas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "suggested_account", "category", "payment_transaction")
        )


@admin.register(BillReminder)
class BillReminderAdmin(admin.ModelAdmin):
    """Configuración del admin para recordatorios"""

    list_display = [
        "bill",
        "reminder_type",
        "is_read",
        "user",
        "created_at",
    ]

    list_filter = [
        "reminder_type",
        "is_read",
        "created_at",
    ]

    search_fields = [
        "bill__provider",
        "message",
        "user__username",
        "user__email",
    ]

    readonly_fields = [
        "created_at",
        "read_at",
    ]

    fieldsets = (
        ("Recordatorio", {"fields": ("user", "bill", "reminder_type", "message")}),
        ("Estado", {"fields": ("is_read", "read_at")}),
        ("Fecha", {"fields": ("created_at",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "bill")
