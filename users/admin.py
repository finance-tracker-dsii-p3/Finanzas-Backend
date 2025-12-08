"""
Admin configuration for users app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, UserNotificationPreferences


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom User model"""
    
    list_display = ['username', 'email', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active']
    search_fields = ['username', 'email', 'identification']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'identification', 'phone', 'is_verified', 'verified_by', 'verification_date')}),
    )


@admin.register(UserNotificationPreferences)
class UserNotificationPreferencesAdmin(admin.ModelAdmin):
    """Admin configuration for notification preferences"""
    
    list_display = ['user', 'timezone', 'language', 'enable_budget_alerts', 'enable_bill_reminders', 'enable_soat_reminders']
    list_filter = ['language', 'enable_budget_alerts', 'enable_bill_reminders']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Configuración Regional', {
            'fields': ('timezone', 'language')
        }),
        ('Tipos de Notificaciones', {
            'fields': (
                'enable_budget_alerts',
                'enable_bill_reminders',
                'enable_soat_reminders',
                'enable_month_end_reminders',
                'enable_custom_reminders',
            )
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
