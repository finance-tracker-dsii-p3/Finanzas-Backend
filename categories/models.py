"""
Modelos para gestión de categorías de ingresos y gastos
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

User = get_user_model()


def validate_hex_color(value):
    """Validar que el color sea un código hexadecimal válido"""
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError(
            f'{value} no es un código de color hexadecimal válido. Debe ser formato #RRGGBB'
        )


def validate_color_contrast(value):
    """
    Validar que el color tenga buen contraste con fondo blanco
    Calcula la luminancia relativa según WCAG 2.1
    """
    # Remover el # y convertir a RGB
    hex_color = value.lstrip('#')
    
    # Si el formato no es válido (longitud incorrecta), saltear validación
    # El validate_hex_color se encargará de mostrar el error correcto
    if len(hex_color) != 6:
        return
    
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        # Si hay caracteres inválidos, saltear validación
        return
    
    # Calcular luminancia relativa
    def get_relative_luminance(channel):
        channel = channel / 255.0
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4
    
    r_lum = get_relative_luminance(r)
    g_lum = get_relative_luminance(g)
    b_lum = get_relative_luminance(b)
    
    luminance = 0.2126 * r_lum + 0.7152 * g_lum + 0.0722 * b_lum
    
    # Calcular contraste con blanco (luminancia = 1)
    # Fórmula correcta: (L1 + 0.05) / (L2 + 0.05) donde L1 es el más claro
    white_luminance = 1.0
    if white_luminance > luminance:
        contrast_ratio = (white_luminance + 0.05) / (luminance + 0.05)
    else:
        contrast_ratio = (luminance + 0.05) / (white_luminance + 0.05)
    
    # WCAG AA requiere ratio mínimo de 4.5:1 para texto normal
    # Usamos 3.0 como mínimo para ser menos restrictivo con colores de UI
    if contrast_ratio < 3.0:
        raise ValidationError(
            f'El color {value} no tiene suficiente contraste con fondo blanco. '
            f'Ratio actual: {contrast_ratio:.2f}:1, mínimo requerido: 3.0:1'
        )


class Category(models.Model):
    """
    Modelo para categorías de ingresos y gastos
    
    Permite a los usuarios organizar sus transacciones en categorías
    personalizadas con colores e íconos para mejor visualización.
    """
    
    # Tipos de categoría
    INCOME = 'income'
    EXPENSE = 'expense'
    
    TYPE_CHOICES = [
        (INCOME, 'Ingreso'),
        (EXPENSE, 'Gasto'),
    ]
    
    # Lista de iconos válidos (Font Awesome)
    ICON_CHOICES = [
        ('fa-shopping-cart', 'Carrito de compras'),
        ('fa-utensils', 'Comida'),
        ('fa-home', 'Casa'),
        ('fa-car', 'Transporte'),
        ('fa-heart', 'Salud'),
        ('fa-graduation-cap', 'Educación'),
        ('fa-film', 'Entretenimiento'),
        ('fa-tshirt', 'Ropa'),
        ('fa-plane', 'Viajes'),
        ('fa-mobile-alt', 'Teléfono'),
        ('fa-wifi', 'Internet'),
        ('fa-bolt', 'Servicios públicos'),
        ('fa-money-bill-wave', 'Salario'),
        ('fa-briefcase', 'Negocio'),
        ('fa-gift', 'Regalos'),
        ('fa-hand-holding-usd', 'Inversión'),
        ('fa-piggy-bank', 'Ahorros'),
        ('fa-credit-card', 'Tarjeta'),
        ('fa-wallet', 'Billetera'),
        ('fa-chart-line', 'Ingresos'),
        ('fa-shopping-bag', 'Compras'),
        ('fa-coffee', 'Café'),
        ('fa-dumbbell', 'Gimnasio'),
        ('fa-paw', 'Mascotas'),
        ('fa-gamepad', 'Juegos'),
        ('fa-book', 'Libros'),
        ('fa-music', 'Música'),
        ('fa-tools', 'Herramientas'),
        ('fa-paint-brush', 'Arte'),
        ('fa-umbrella', 'Seguros'),
        ('fa-medkit', 'Medicinas'),
        ('fa-laptop', 'Tecnología'),
        ('fa-tv', 'Electrónicos'),
        ('fa-couch', 'Muebles'),
        ('fa-baby', 'Bebé'),
        ('fa-hamburger', 'Comida rápida'),
        ('fa-pizza-slice', 'Pizza'),
        ('fa-wine-glass', 'Bebidas'),
        ('fa-smoking', 'Tabaco'),
        ('fa-tree', 'Jardín'),
        ('fa-bicycle', 'Bicicleta'),
        ('fa-bus', 'Bus'),
        ('fa-taxi', 'Taxi'),
        ('fa-gas-pump', 'Gasolina'),
        ('fa-parking', 'Parqueadero'),
        ('fa-hotel', 'Hotel'),
        ('fa-suitcase', 'Equipaje'),
        ('fa-map', 'Mapas'),
        ('fa-ticket-alt', 'Tickets'),
        ('fa-dollar-sign', 'Dinero'),
        ('fa-coins', 'Monedas'),
        ('fa-percent', 'Descuentos'),
        ('fa-tags', 'Etiquetas'),
        ('fa-star', 'Favoritos'),
        ('fa-question-circle', 'Otros'),
    ]
    
    # Campos del modelo
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        help_text='Usuario propietario de la categoría'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Nombre de la categoría (ej: Comida, Salario)'
    )
    
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        help_text='Tipo de categoría: ingreso o gasto'
    )
    
    color = models.CharField(
        max_length=7,
        validators=[validate_hex_color, validate_color_contrast],
        help_text='Color en formato hexadecimal (ej: #FF5733)',
        default='#3B82F6'
    )
    
    icon = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        default='fa-question-circle',
        help_text='Ícono de Font Awesome para representar la categoría'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si la categoría está activa y disponible para usar'
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text='Indica si es una categoría del sistema (no editable por usuario)'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text='Orden de visualización en listas'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación de la categoría'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de última actualización'
    )
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['order', 'name']
        
        # Restricción de unicidad: un usuario no puede tener dos categorías
        # con el mismo nombre y tipo
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name', 'type'],
                name='unique_category_per_user'
            )
        ]
        
        indexes = [
            models.Index(fields=['user', 'type', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def clean(self):
        """Validaciones adicionales del modelo"""
        super().clean()
        
        # Normalizar nombre: primera letra mayúscula, resto minúsculas
        if self.name:
            self.name = self.name.strip().title()
        
        # Validar que no exista otra categoría con el mismo nombre y tipo
        # para este usuario (excluyendo la instancia actual si es actualización)
        existing = Category.objects.filter(
            user=self.user,
            name__iexact=self.name,
            type=self.type
        )
        
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        
        if existing.exists():
            raise ValidationError({
                'name': f'Ya tienes una categoría de {self.get_type_display()} llamada "{self.name}"'
            })
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def can_be_deleted(self):
        """
        Verificar si la categoría puede ser eliminada
        No se puede eliminar si tiene transacciones o presupuestos asociados
        """
        # TODO: Verificar transacciones cuando se implemente el modelo
        # has_transactions = self.transactions.exists()
        has_transactions = False
        
        # TODO: Verificar presupuestos cuando se implemente el modelo
        # has_budgets = self.budgets.exists()
        has_budgets = False
        
        return not (has_transactions or has_budgets)
    
    def get_usage_count(self):
        """
        Obtener el número de veces que se usa esta categoría
        """
        # TODO: Implementar cuando existan transacciones y presupuestos
        # transactions_count = self.transactions.count()
        # budgets_count = self.budgets.count()
        # return transactions_count + budgets_count
        return 0
    
    def get_related_data(self):
        """
        Obtener información sobre datos relacionados con esta categoría
        """
        return {
            'transactions_count': 0,  # TODO: self.transactions.count()
            'budgets_count': 0,  # TODO: self.budgets.count()
            'can_be_deleted': self.can_be_deleted(),
            'usage_count': self.get_usage_count()
        }
