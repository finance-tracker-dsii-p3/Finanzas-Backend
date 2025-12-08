"""
Serializers para preferencias de notificaciones
"""

from rest_framework import serializers
from users.models import UserNotificationPreferences
import pytz


class UserNotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer para preferencias de notificaciones del usuario"""
    
    timezone_display = serializers.SerializerMethodField()
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = UserNotificationPreferences
        fields = [
            'id',
            'timezone',
            'timezone_display',
            'language',
            'language_display',
            'enable_budget_alerts',
            'enable_bill_reminders',
            'enable_soat_reminders',
            'enable_month_end_reminders',
            'enable_custom_reminders',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_timezone_display(self, obj):
        """Retorna el nombre completo de la zona horaria"""
        try:
            tz = pytz.timezone(obj.timezone)
            return obj.timezone
        except:
            return "America/Bogota"
    
    def validate_timezone(self, value):
        """Valida que la zona horaria sea válida"""
        try:
            pytz.timezone(value)
            return value
        except:
            raise serializers.ValidationError("Zona horaria inválida")


class TimezoneListSerializer(serializers.Serializer):
    """Serializer para listar zonas horarias disponibles"""
    
    timezone = serializers.CharField()
    display_name = serializers.CharField()
    
    class Meta:
        fields = ['timezone', 'display_name']
