from django.db import models
from django.conf import settings
from django.utils import timezone as dj_timezone


class Notification(models.Model):
    """
    Modelo para gestionar notificaciones en tiempo real
    Sistema de notificaciones para alertas de presupuesto, recordatorios de facturas,
    SOAT, fin de mes y recordatorios personalizados
    """

    # Tipos de notificaciones
    GENERAL = "general"
    ADMIN_VERIFICATION = "admin_verification"
    SYSTEM_ALERT = "system_alert"
    USER_ACTION = "user_action"
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    BILL_REMINDER = "bill_reminder"
    SOAT_REMINDER = "soat_reminder"
    MONTH_END_REMINDER = "month_end_reminder"
    CUSTOM_REMINDER = "custom_reminder"

    TYPE_CHOICES = [
        (GENERAL, "Notificación general"),
        (ADMIN_VERIFICATION, "Verificación de usuario"),
        (SYSTEM_ALERT, "Alerta del sistema"),
        (USER_ACTION, "Acción del usuario"),
        (BUDGET_WARNING, "Alerta de presupuesto (80%)"),
        (BUDGET_EXCEEDED, "Presupuesto excedido (100%)"),
        (BILL_REMINDER, "Recordatorio de factura"),
        (SOAT_REMINDER, "Recordatorio de SOAT"),
        (MONTH_END_REMINDER, "Recordatorio de fin de mes"),
        (CUSTOM_REMINDER, "Recordatorio personalizado"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications_received",
        help_text="Usuario que recibe la notificación",
    )
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=GENERAL,
        verbose_name="Tipo",
        help_text="Tipo de notificación",
    )
    title = models.CharField(
        max_length=200, verbose_name="Título", help_text="Título breve de la notificación"
    )
    message = models.TextField(
        verbose_name="Mensaje", help_text="Mensaje detallado de la notificación"
    )
    related_object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID de objeto relacionado",
        help_text="ID del objeto relacionado con la notificación (Budget, Bill, SOAT, etc.)",
    )
    related_object_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Tipo de objeto relacionado",
        help_text="Tipo del objeto relacionado (budget, bill, soat, custom_reminder)",
    )
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Programado para",
        help_text="Fecha y hora programada para enviar la notificación (recordatorios)",
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Enviado en",
        help_text="Fecha y hora en que se envió la notificación",
    )
    read = models.BooleanField(
        default=False, verbose_name="Leída", help_text="Indica si la notificación ha sido leída"
    )
    read_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de lectura",
        help_text="Fecha y hora en que se leyó la notificación",
    )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read"]),
            models.Index(fields=["notification_type"]),
            models.Index(fields=["scheduled_for"]),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title} ({self.user})"
    
    def mark_as_sent(self):
        """Marca la notificación como enviada"""
        if not self.sent_at:
            self.sent_at = dj_timezone.now()
            self.save(update_fields=["sent_at"])
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        if not self.read:
            self.read = True
            self.read_timestamp = dj_timezone.now()
            self.save(update_fields=["read", "read_timestamp"])


class CustomReminder(models.Model):
    """
    Modelo para recordatorios personalizados creados por el usuario
    Permite programar recordatorios con fecha y hora específicas
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="custom_reminders",
        verbose_name="Usuario",
        help_text="Usuario propietario del recordatorio"
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título del recordatorio"
    )
    
    message = models.TextField(
        verbose_name="Mensaje",
        help_text="Mensaje detallado del recordatorio"
    )
    
    reminder_date = models.DateField(
        verbose_name="Fecha del recordatorio",
        help_text="Fecha en que se debe enviar el recordatorio"
    )
    
    reminder_time = models.TimeField(
        verbose_name="Hora del recordatorio",
        help_text="Hora en que se debe enviar el recordatorio"
    )
    
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Enviado",
        help_text="Indica si el recordatorio ya fue enviado"
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Enviado en",
        help_text="Fecha y hora en que se envió el recordatorio"
    )
    
    notification = models.OneToOneField(
        Notification,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="custom_reminder",
        verbose_name="Notificación",
        help_text="Notificación generada para este recordatorio"
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name="Leído",
        help_text="Indica si el recordatorio ha sido leído"
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Leído en",
        help_text="Fecha y hora en que se leyó el recordatorio"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Recordatorio personalizado"
        verbose_name_plural = "Recordatorios personalizados"
        ordering = ["reminder_date", "reminder_time"]
        indexes = [
            models.Index(fields=["user", "is_sent"]),
            models.Index(fields=["reminder_date", "reminder_time"]),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.reminder_date} {self.reminder_time}"
    
    @property
    def is_past_due(self):
        """Verifica si el recordatorio ya pasó su fecha"""
        from datetime import datetime
        now = dj_timezone.now()
        
        # Crear datetime del recordatorio en timezone del usuario
        try:
            prefs = self.user.notification_preferences
            tz = prefs.timezone_object
        except Exception:
            import pytz
            tz = pytz.timezone("America/Bogota")
        
        reminder_datetime = dj_timezone.make_aware(
            datetime.combine(self.reminder_date, self.reminder_time),
            tz
        )
        
        return now > reminder_datetime
    
    def mark_as_sent(self):
        """Marca el recordatorio como enviado"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = dj_timezone.now()
            self.save(update_fields=["is_sent", "sent_at"])
    
    def mark_as_read(self):
        """Marca el recordatorio como leído"""
        if not self.is_read:
            self.is_read = True
            self.read_at = dj_timezone.now()
            self.save(update_fields=["is_read", "read_at"])
