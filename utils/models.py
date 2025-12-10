"""
Modelos de utilidades para el sistema
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from datetime import date

User = get_user_model()


class BaseCurrencySetting(models.Model):
    """
    Configuración de moneda base por usuario.
    Cada usuario puede elegir su moneda base preferida para ver totales consolidados.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="base_currency_setting", verbose_name="Usuario"
    )
    base_currency = models.CharField(
        max_length=3,
        default="COP",
        verbose_name="Moneda base",
        help_text="Moneda base para cálculos y reportes del usuario (COP, USD, EUR)",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Configuración de moneda base"
        verbose_name_plural = "Configuraciones de moneda base"

    def __str__(self):
        return f"Base {self.base_currency} para {self.user.username}"


class ExchangeRate(models.Model):
    """
    Tipos de cambio mensuales entre monedas.
    Permite definir tasas de conversión por mes y año para mantener histórico.
    Si no existe tasa para un mes, se usa la última disponible anterior.
    """

    base_currency = models.CharField(
        max_length=3,
        default="COP",
        verbose_name="Moneda base",
        help_text="Moneda base de referencia (ej: COP)",
    )
    currency = models.CharField(
        max_length=3, verbose_name="Moneda", help_text="Moneda a convertir (ej: USD, EUR)"
    )
    year = models.IntegerField(verbose_name="Año", help_text="Año del tipo de cambio")
    month = models.IntegerField(verbose_name="Mes", help_text="Mes del tipo de cambio (1-12)")
    rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[MinValueValidator(0)],
        verbose_name="Tasa de cambio",
        help_text="Valor de conversión (ej: 4000.0 significa 1 USD = 4000 COP)",
    )
    source = models.CharField(
        max_length=100,
        blank=True,
        default="manual",
        verbose_name="Fuente",
        help_text="Origen del tipo de cambio (manual, API, etc)",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        unique_together = [("base_currency", "currency", "year", "month")]
        ordering = ["-year", "-month", "currency"]
        verbose_name = "Tipo de cambio"
        verbose_name_plural = "Tipos de cambio"

    def __str__(self):
        return f"{self.currency}/{self.base_currency} {self.year}-{self.month:02d}: {self.rate}"

    @property
    def period_start(self):
        """Fecha de inicio del período del tipo de cambio"""
        return date(self.year, self.month, 1)
