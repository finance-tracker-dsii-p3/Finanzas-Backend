import contextlib

from django.contrib.auth import get_user_model
from django.utils import timezone as dj_timezone
from rest_framework import serializers

from .models import CustomReminder, Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer para notificaciones del sistema financiero
    Soporta todos los tipos de notificaciones: presupuesto, facturas, SOAT, fin de mes, personalizadas
    """

    recipient_name = serializers.CharField(source="user.get_full_name", read_only=True)
    recipient_username = serializers.CharField(source="user.username", read_only=True)
    is_read = serializers.BooleanField(source="read", read_only=True)
    is_dismissed = serializers.BooleanField(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )

    # Permitir creación desde API para admins
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=False, write_only=True
    )
    notification_type = serializers.ChoiceField(
        choices=Notification.TYPE_CHOICES, write_only=True, required=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "notification_type_display",
            "title",
            "message",
            "read",
            "is_read",
            "read_timestamp",
            "is_dismissed",
            "dismissed_at",
            "related_object_id",
            "related_object_type",
            "scheduled_for",
            "sent_at",
            "created_at",
            "updated_at",
            "recipient_name",
            "recipient_username",
            "user_id",
            "user_name",
            "user",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "sent_at",
            "read_timestamp",
            "is_dismissed",
            "dismissed_at",
            "notification_type_display",
        ]

    def create(self, validated_data):
        """Crear notificación asignando usuario apropiado"""
        request = self.context.get("request") if self.context else None
        user = validated_data.pop("user", None)

        if user is None and request is not None:
            user = request.user

        return Notification.objects.create(user=user, **validated_data)


class SystemAlertSerializer(serializers.ModelSerializer):
    """
    Serializer para alertas del sistema - versión simplificada
    """

    recipient_name = serializers.CharField(source="user.get_full_name", read_only=True)
    recipient_username = serializers.CharField(source="user.username", read_only=True)
    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "notification_type_display",
            "read",
            "created_at",
            "recipient_name",
            "recipient_username",
            "related_object_id",
            "related_object_type",
        ]
        read_only_fields = ["created_at"]


class CustomReminderSerializer(serializers.ModelSerializer):
    """
    Serializer para recordatorios personalizados del usuario
    """

    is_past_due_display = serializers.BooleanField(source="is_past_due", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)
    notification_id = serializers.IntegerField(
        source="notification.id", read_only=True, allow_null=True
    )

    class Meta:
        model = CustomReminder
        fields = [
            "id",
            "title",
            "message",
            "reminder_date",
            "reminder_time",
            "is_sent",
            "sent_at",
            "notification_id",
            "is_read",
            "read_at",
            "is_past_due_display",
            "user_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_sent",
            "sent_at",
            "notification_id",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        """Validar que la fecha/hora del recordatorio sea futura"""
        if "reminder_date" in data and "reminder_time" in data:
            from datetime import datetime

            import pytz

            reminder_datetime = datetime.combine(data["reminder_date"], data["reminder_time"])

            # Obtener timezone del usuario (o usar default)
            request = self.context.get("request")
            user_tz = pytz.timezone("America/Bogota")  # Default timezone

            if request and hasattr(request.user, "notification_preferences"):
                with contextlib.suppress(Exception):
                    user_tz = request.user.notification_preferences.timezone_object

            # Siempre hacer el datetime timezone-aware
            reminder_datetime = dj_timezone.make_aware(reminder_datetime, user_tz)

            if reminder_datetime < dj_timezone.now():
                msg = "La fecha y hora del recordatorio debe ser futura"
                raise serializers.ValidationError(msg)

        return data

    def create(self, validated_data):
        """Crear recordatorio asociado al usuario autenticado"""
        request = self.context.get("request")
        if request:
            validated_data["user"] = request.user
        return super().create(validated_data)


class CustomReminderListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar recordatorios personalizados
    """

    is_past_due_display = serializers.BooleanField(source="is_past_due", read_only=True)

    class Meta:
        model = CustomReminder
        fields = [
            "id",
            "title",
            "reminder_date",
            "reminder_time",
            "is_sent",
            "is_read",
            "is_past_due_display",
            "created_at",
        ]
