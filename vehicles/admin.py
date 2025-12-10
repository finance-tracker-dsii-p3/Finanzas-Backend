"""
Admin para gestión de vehículos y SOAT
"""

from django.contrib import admin
from vehicles.models import Vehicle, SOAT, SOATAlert


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["plate", "brand", "model", "year", "user", "is_active", "created_at"]
    list_filter = ["is_active", "brand", "year"]
    search_fields = ["plate", "brand", "model", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(SOAT)
class SOATAdmin(admin.ModelAdmin):
    list_display = [
        "vehicle",
        "expiry_date",
        "status",
        "is_paid",
        "cost_display",
        "days_until_expiry",
    ]
    list_filter = ["status", "expiry_date"]
    search_fields = ["vehicle__plate", "insurance_company", "policy_number"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "days_until_expiry",
        "is_expired",
        "is_near_expiry",
        "is_paid",
    ]
    date_hierarchy = "expiry_date"
    ordering = ["-expiry_date"]

    def cost_display(self, obj):
        return f"${obj.cost / 100:,.2f}"

    cost_display.short_description = "Costo"


@admin.register(SOATAlert)
class SOATAlertAdmin(admin.ModelAdmin):
    list_display = ["soat", "user", "alert_type", "is_read", "created_at"]
    list_filter = ["alert_type", "is_read", "created_at"]
    search_fields = ["soat__vehicle__plate", "user__username", "message"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
