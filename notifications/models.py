from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Modelo para gestionar notificaciones en tiempo real
    Adaptado para el sistema financiero - se expandirá con tipos específicos
    """
    # Tipos básicos de notificaciones (se expandirán para el proyecto financiero)
    GENERAL = 'general'
    ADMIN_VERIFICATION = 'admin_verification'
    SYSTEM_ALERT = 'system_alert'
    USER_ACTION = 'user_action'
    
    TYPE_CHOICES = [
        (GENERAL, 'Notificación general'),
        (ADMIN_VERIFICATION, 'Verificación de usuario'),
        (SYSTEM_ALERT, 'Alerta del sistema'),
        (USER_ACTION, 'Acción del usuario'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications_received',
        help_text='Usuario que recibe la notificación'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=GENERAL,
        verbose_name="Tipo",
        help_text='Tipo de notificación'
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text='Título breve de la notificación'
    )
    message = models.TextField(
        verbose_name="Mensaje",
        help_text='Mensaje detallado de la notificación'
    )
    related_object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID de objeto relacionado",
        help_text='ID del objeto relacionado con la notificación'
    )
    read = models.BooleanField(
        default=False,
        verbose_name="Leída",
        help_text='Indica si la notificación ha sido leída'
    )
    read_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de lectura",
        help_text='Fecha y hora en que se leyó la notificación'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title} ({self.user})"