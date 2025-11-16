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