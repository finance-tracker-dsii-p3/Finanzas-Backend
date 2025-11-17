from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone

User = get_user_model()


class Account(models.Model):
    """Modelo simplificado para cuentas financieras"""
    
    # Tipos de cuenta
    ASSET = 'asset'
    LIABILITY = 'liability'
    
    ACCOUNT_TYPE_CHOICES = [
        (ASSET, 'Activo'),
        (LIABILITY, 'Pasivo'),
    ]
    
    # Categorías
    BANK_ACCOUNT = 'bank_account'
    SAVINGS_ACCOUNT = 'savings_account' 
    CREDIT_CARD = 'credit_card'
    WALLET = 'wallet'
    OTHER = 'other'
    
    CATEGORY_CHOICES = [
        (BANK_ACCOUNT, 'Cuenta Bancaria'),
        (SAVINGS_ACCOUNT, 'Cuenta de Ahorros'),
        (CREDIT_CARD, 'Tarjeta de Crédito'),
        (WALLET, 'Billetera'),
        (OTHER, 'Otro'),
    ]
    
    # Monedas
    CURRENCY_CHOICES = [
        ('COP', 'Pesos Colombianos'),
        ('USD', 'Dólares'),
        ('EUR', 'Euros'),
    ]
    
    # Campos del modelo
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='accounts',
        verbose_name='Usuario propietario'
    )
    
    name = models.CharField(
        max_length=100, 
        verbose_name='Nombre de la cuenta'
    )
    
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombre del banco',
        help_text='Nombre del banco o entidad financiera'
    )
    
    account_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Número de cuenta',
        help_text='Número de cuenta, tarjeta o identificación de la cuenta'
    )
    
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Descripción'
    )
    
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        verbose_name='Tipo de cuenta'
    )
    
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría'
    )
    
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo actual'
    )
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='COP',
        verbose_name='Moneda'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    # Campo para exención de GMF (Gravamen a los Movimientos Financieros)
    gmf_exempt = models.BooleanField(
        default=False,
        verbose_name='Exenta GMF',
        help_text='Si está marcada, la cuenta está exenta del GMF (4x1000)'
    )
    
    # Campos específicos para tarjetas de crédito
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de vencimiento',
        help_text='Fecha de vencimiento de la tarjeta (solo para tarjetas de crédito)'
    )
    
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Límite de crédito',
        help_text='Límite de crédito de la tarjeta (solo para tarjetas de crédito)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    def __str__(self):
        return f"{self.name} ({self.get_currency_display()})"
    
    @property
    def balance_for_totals(self):
        """
        Retorna el balance en el formato correcto para cálculos de totales
        Para activos: valor positivo
        Para pasivos: valor positivo del absoluto (deuda)
        """
        if self.account_type == self.LIABILITY:
            return abs(self.current_balance)
        return self.current_balance
    
    def can_be_deleted(self):
        """
        Verificar si la cuenta puede ser eliminada
        No se puede eliminar si tiene transacciones asociadas.
        """
        # TODO: Implementar cuando exista el modelo de transacciones
        # return not self.transactions.exists()
        return True  # Por ahora permitir eliminación

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['name']


class AccountOptionType(models.TextChoices):
    """Tipos de opciones para cuentas"""
    BANK = 'bank', 'Banco'
    WALLET = 'wallet', 'Billetera'
    CREDIT_CARD_BANK = 'credit_card_bank', 'Banco para Tarjeta de Crédito'


class AccountOption(models.Model):
    """
    Modelo para almacenar las opciones de bancos, billeteras y bancos para tarjetas.
    Permite administrar estos listados desde el admin de Django.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre del banco, billetera o entidad'
    )
    option_type = models.CharField(
        max_length=20,
        choices=AccountOptionType.choices,
        verbose_name='Tipo de opción',
        help_text='Tipo de opción: banco, billetera o banco para tarjeta'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no aparecerá en los listados del frontend'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de aparición (menor número aparece primero)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    class Meta:
        ordering = ['option_type', 'order', 'name']
        unique_together = [['name', 'option_type']]
        verbose_name = 'Opción de Cuenta'
        verbose_name_plural = 'Opciones de Cuentas'
        indexes = [
            models.Index(fields=['option_type', 'is_active']),
            models.Index(fields=['option_type', 'order']),
        ]

    def __str__(self):
        return f"{self.get_option_type_display()}: {self.name}"