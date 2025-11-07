from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from .managers import CustomUserManager
from django.conf import settings


class User(AbstractUser):
    """
    Modelo personalizado de usuario para la aplicación de gestión financiera personal
    """
    # Roles de usuario
    ADMIN = 'admin'
    USER = 'user'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (USER, 'Usuario'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        help_text='Rol del usuario en el sistema de gestión financiera'
    )
    identification = models.CharField(
      max_length=20,
      unique=True,
      verbose_name="Número de Identificación",
      help_text='Número de identificación del usuario',
      error_messages={'unique': 'Ya existe un usuario con esta identificación'}
    )
    
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name="Teléfono",
        help_text='Número de teléfono de contacto'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado",
        help_text='Indica si el usuario ha sido verificado por un administrador'
    )
    verified_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_users',
        verbose_name="Verificado por",
        help_text='Administrador que verificó al usuario'
    )
    verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de verificación",
        help_text='Fecha y hora en que fue verificado el usuario'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['email', 'identification']
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_resets'
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users_password_reset"
        indexes = [
            models.Index(fields=['token_hash']),
            models.Index(fields=['user']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def is_used(self) -> bool:
        return self.used_at is not None

    def is_valid(self) -> bool:
        return not self.is_used() and not self.is_expired()

    def mark_as_used(self) -> None:
        if not self.is_used():
            self.used_at = timezone.now()
            self.save(update_fields=['used_at'])