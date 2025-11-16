"""
Modelos para gestión de presupuestos por categoría
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, date
import calendar

User = get_user_model()


class Budget(models.Model):
    """
    Modelo para límites de gasto por categoría.
    Permite establecer presupuestos mensuales o anuales con modo de cálculo base o total.
    """
    
    # Modos de cálculo
    BASE = 'base'
    TOTAL = 'total'
    
    CALCULATION_MODE_CHOICES = [
        (BASE, 'Base (sin impuestos)'),
        (TOTAL, 'Total (con impuestos)'),
    ]
    
    # Períodos
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    
    PERIOD_CHOICES = [
        (MONTHLY, 'Mensual'),
        (YEARLY, 'Anual'),
    ]
    
    # Campos del modelo
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Usuario'
    )
    
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Categoría'
    )
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Límite de presupuesto',
        help_text='Monto máximo permitido para esta categoría'
    )
    
    calculation_mode = models.CharField(
        max_length=10,
        choices=CALCULATION_MODE_CHOICES,
        default=BASE,
        verbose_name='Modo de cálculo',
        help_text='Base: sin impuestos, Total: con impuestos'
    )
    
    period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        default=MONTHLY,
        verbose_name='Período',
        help_text='Frecuencia del presupuesto'
    )
    
    start_date = models.DateField(
        default=date.today,
        verbose_name='Fecha de inicio',
        help_text='Desde cuándo aplica este presupuesto'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no se calculan alertas'
    )
    
    alert_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('80.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Umbral de alerta (%)',
        help_text='Porcentaje al cual se genera alerta (por defecto 80%)'
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
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category', 'period'],
                name='unique_budget_per_category_period',
                violation_error_message='Ya existe un presupuesto para esta categoría y período.'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['period', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.category.name} - {self.get_period_display()} - ${self.amount}"
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que la categoría pertenezca al mismo usuario
        if self.category and self.user:
            if self.category.user != self.user:
                raise ValidationError({
                    'category': 'La categoría debe pertenecer al mismo usuario.'
                })
        
        # Validar que el umbral no sea mayor a 100
        if self.alert_threshold > 100:
            raise ValidationError({
                'alert_threshold': 'El umbral de alerta no puede ser mayor a 100%.'
            })
    
    def save(self, *args, **kwargs):
        """Ejecutar validaciones antes de guardar"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_period_dates(self, reference_date=None):
        """
        Obtener las fechas de inicio y fin del período actual.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            tuple: (start_date, end_date)
        """
        if reference_date is None:
            reference_date = date.today()
        
        if self.period == self.MONTHLY:
            # Primer y último día del mes de la fecha de referencia
            start = reference_date.replace(day=1)
            last_day = calendar.monthrange(reference_date.year, reference_date.month)[1]
            end = reference_date.replace(day=last_day)
        else:  # YEARLY
            # Primer y último día del año
            start = reference_date.replace(month=1, day=1)
            end = reference_date.replace(month=12, day=31)
        
        return start, end
    
    def get_spent_amount(self, reference_date=None):
        """
        Calcular el monto gastado en el período actual según el modo de cálculo.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            Decimal: Monto gastado
        """
        # TODO: Implementar cuando exista el modelo Transaction
        # Por ahora retornar 0
        # start_date, end_date = self.get_period_dates(reference_date)
        # transactions = self.category.transactions.filter(
        #     user=self.user,
        #     date__gte=start_date,
        #     date__lte=end_date,
        #     type='expense'
        # )
        # 
        # if self.calculation_mode == self.BASE:
        #     return transactions.aggregate(
        #         total=models.Sum('amount')
        #     )['total'] or Decimal('0.00')
        # else:  # TOTAL
        #     return transactions.aggregate(
        #         total=models.Sum('total_amount')
        #     )['total'] or Decimal('0.00')
        
        return Decimal('0.00')
    
    def get_spent_percentage(self, reference_date=None):
        """
        Calcular el porcentaje gastado del presupuesto.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            Decimal: Porcentaje gastado (0-100+)
        """
        spent = self.get_spent_amount(reference_date)
        if self.amount == 0:
            return Decimal('0.00')
        
        percentage = (spent / self.amount) * 100
        return round(percentage, 2)
    
    def get_remaining_amount(self, reference_date=None):
        """
        Calcular el monto restante del presupuesto.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            Decimal: Monto restante (puede ser negativo si se excedió)
        """
        spent = self.get_spent_amount(reference_date)
        return self.amount - spent
    
    def get_daily_average(self, reference_date=None):
        """
        Calcular el promedio de gasto diario en el período.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            Decimal: Promedio diario
        """
        if reference_date is None:
            reference_date = date.today()
        
        start_date, end_date = self.get_period_dates(reference_date)
        
        # Días transcurridos desde el inicio del período
        days_elapsed = (reference_date - start_date).days + 1
        
        if days_elapsed == 0:
            return Decimal('0.00')
        
        spent = self.get_spent_amount(reference_date)
        return round(spent / days_elapsed, 2)
    
    def get_projection(self, reference_date=None):
        """
        Calcular la proyección de gasto a fin de período basada en el promedio diario.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            dict: {
                'projected_amount': Decimal,
                'projected_percentage': Decimal,
                'will_exceed': bool,
                'days_remaining': int,
                'days_total': int
            }
        """
        if reference_date is None:
            reference_date = date.today()
        
        start_date, end_date = self.get_period_dates(reference_date)
        
        # Total de días en el período
        if self.period == self.MONTHLY:
            days_total = calendar.monthrange(reference_date.year, reference_date.month)[1]
        else:  # YEARLY
            days_total = 366 if calendar.isleap(reference_date.year) else 365
        
        # Días restantes
        days_remaining = (end_date - reference_date).days
        
        # Promedio diario
        daily_avg = self.get_daily_average(reference_date)
        
        # Proyección = gasto actual + (promedio diario × días restantes)
        spent = self.get_spent_amount(reference_date)
        projected_amount = spent + (daily_avg * days_remaining)
        
        # Porcentaje proyectado
        projected_percentage = Decimal('0.00')
        if self.amount > 0:
            projected_percentage = round((projected_amount / self.amount) * 100, 2)
        
        return {
            'projected_amount': round(projected_amount, 2),
            'projected_percentage': projected_percentage,
            'will_exceed': projected_amount > self.amount,
            'days_remaining': days_remaining,
            'days_total': days_total,
            'daily_average': daily_avg
        }
    
    def is_over_budget(self, reference_date=None):
        """
        Verificar si se ha excedido el presupuesto.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            bool: True si se excedió el presupuesto
        """
        return self.get_spent_amount(reference_date) > self.amount
    
    def is_alert_triggered(self, reference_date=None):
        """
        Verificar si se alcanzó el umbral de alerta.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            bool: True si se alcanzó o superó el umbral
        """
        percentage = self.get_spent_percentage(reference_date)
        return percentage >= self.alert_threshold
    
    def get_status(self, reference_date=None):
        """
        Obtener el estado actual del presupuesto.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            str: 'exceeded', 'warning', 'good'
        """
        if self.is_over_budget(reference_date):
            return 'exceeded'
        elif self.is_alert_triggered(reference_date):
            return 'warning'
        return 'good'
    
    def get_status_display_text(self, reference_date=None):
        """
        Obtener texto descriptivo del estado.
        
        Args:
            reference_date: Fecha de referencia (default: hoy)
        
        Returns:
            str: Texto del estado
        """
        status = self.get_status(reference_date)
        status_messages = {
            'exceeded': 'Presupuesto excedido',
            'warning': f'Alerta: {self.get_spent_percentage(reference_date)}% gastado',
            'good': 'Dentro del presupuesto'
        }
        return status_messages.get(status, 'Desconocido')
