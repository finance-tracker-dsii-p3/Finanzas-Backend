import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import CustomUserManager


class User(AbstractUser):
    """
    Modelo personalizado de usuario para la aplicación de gestión financiera personal
    """

    # Roles de usuario
    ADMIN = "admin"
    USER = "user"

    ROLE_CHOICES = [
        (ADMIN, "Administrador"),
        (USER, "Usuario"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        help_text="Rol del usuario en el sistema de gestión financiera",
    )
    identification = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Identificación",
        help_text="Número de identificación del usuario",
        error_messages={"unique": "Ya existe un usuario con esta identificación"},
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Teléfono",
        help_text="Número de teléfono de contacto",
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado",
        help_text="Indica si el usuario ha sido verificado por un administrador",
    )
    verified_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_users",
        verbose_name="Verificado por",
        help_text="Administrador que verificó al usuario",
    )
    verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de verificación",
        help_text="Fecha y hora en que fue verificado el usuario",
    )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ["email", "identification"]
    USERNAME_FIELD = "username"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["username"]
        db_table = "users_user"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == self.ADMIN

    @property
    def is_user(self):
        """Verifica si el usuario es un usuario regular"""
        return self.role == self.USER

    def save(self, *args, **kwargs):
        """Sobrescribe el método save para verificar automáticamente a los administradores"""
        if not self.pk and self.role == self.ADMIN:
            self.is_verified = True
        super().save(*args, **kwargs)


class PasswordReset(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_resets"
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users_password_reset"
        indexes = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["user"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def is_used(self) -> bool:
        return self.used_at is not None

    def is_valid(self) -> bool:
        return not self.is_used() and not self.is_expired()

    def mark_as_used(self) -> None:
        if not self.is_used():
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])


class UserNotificationPreferences(models.Model):
    """
    Preferencias de notificaciones y recordatorios del usuario
    Incluye timezone, idioma y tipos de notificaciones habilitadas
    """

    # Idiomas soportados
    SPANISH = "es"
    ENGLISH = "en"

    LANGUAGE_CHOICES = [
        (SPANISH, "Español"),
        (ENGLISH, "English"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name="Usuario",
        help_text="Usuario propietario de las preferencias",
    )

    # Configuración regional
    timezone = models.CharField(
        max_length=50,
        default="America/Bogota",
        verbose_name="Zona horaria",
        help_text="Zona horaria del usuario para programar recordatorios",
    )

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default=SPANISH,
        verbose_name="Idioma",
        help_text="Idioma preferido para las notificaciones",
    )

    # Tipos de notificaciones habilitadas
    enable_budget_alerts = models.BooleanField(
        default=True,
        verbose_name="Alertas de presupuesto",
        help_text="Recibir alertas cuando se alcance el 80% o 100% del presupuesto",
    )

    enable_bill_reminders = models.BooleanField(
        default=True,
        verbose_name="Recordatorios de facturas",
        help_text="Recibir recordatorios de vencimiento de facturas",
    )

    enable_soat_reminders = models.BooleanField(
        default=True,
        verbose_name="Recordatorios de SOAT",
        help_text="Recibir recordatorios de vencimiento de SOAT",
    )

    enable_month_end_reminders = models.BooleanField(
        default=True,
        verbose_name="Recordatorios de fin de mes",
        help_text="Recibir recordatorio de importar extractos antes del cierre del mes",
    )

    enable_custom_reminders = models.BooleanField(
        default=True,
        verbose_name="Recordatorios personalizados",
        help_text="Recibir recordatorios personalizados creados por el usuario",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preferencia de notificaciones"
        verbose_name_plural = "Preferencias de notificaciones"
        db_table = "users_notification_preferences"

    def __str__(self):
        return f"Preferencias de {self.user.username}"

    @property
    def timezone_object(self):
        """Retorna el objeto pytz de la zona horaria"""
        try:
            return pytz.timezone(self.timezone)
        except Exception:
            return pytz.timezone("America/Bogota")
