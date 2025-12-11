"""
Configuración del panel de administración para utils
"""

from django.contrib import admin

from utils.models import BaseCurrencySetting, ExchangeRate


@admin.register(BaseCurrencySetting)
class BaseCurrencySettingAdmin(admin.ModelAdmin):
    list_display = ["user", "base_currency", "updated_at"]
    list_filter = ["base_currency", "updated_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["updated_at"]


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ["currency", "base_currency", "year", "month", "rate", "source", "updated_at"]
    list_filter = ["base_currency", "currency", "year", "month", "source"]
    search_fields = ["currency", "base_currency"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-year", "-month", "currency"]

    fieldsets = (
        ("Información del Tipo de Cambio", {"fields": ("base_currency", "currency", "rate")}),
        ("Período", {"fields": ("year", "month")}),
        ("Metadatos", {"fields": ("source", "created_at", "updated_at"), "classes": ("collapse",)}),
    )
