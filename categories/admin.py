"""
Admin configuration for categories app
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin para gestión de categorías"""
    
    list_display = [
        'name', 'user_link', 'type_badge', 'color_display', 
        'icon_display', 'is_active_badge', 'is_default', 
        'order', 'usage_count_display', 'created_at'
    ]
    
    list_filter = ['type', 'is_active', 'is_default', 'created_at']
    
    search_fields = ['name', 'user__username', 'user__email']
    
    readonly_fields = [
        'created_at', 'updated_at', 'usage_count_display', 
        'related_data_display', 'color_preview'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'name', 'type')
        }),
        ('Apariencia', {
            'fields': ('color', 'color_preview', 'icon')
        }),
        ('Estado y Orden', {
            'fields': ('is_active', 'is_default', 'order')
        }),
        ('Uso', {
            'fields': ('usage_count_display', 'related_data_display'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['user', 'order', 'name']
    
    list_per_page = 25
    
    actions = ['activate_categories', 'deactivate_categories']
    
    def user_link(self, obj):
        """Mostrar usuario como enlace"""
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'Usuario'
    
    def type_badge(self, obj):
        """Mostrar tipo con badge de color"""
        if obj.type == Category.INCOME:
            color = '#10B981'
            text = 'Ingreso'
        else:
            color = '#EF4444'
            text = 'Gasto'
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, text
        )
    type_badge.short_description = 'Tipo'
    
    def color_display(self, obj):
        """Mostrar color como cuadrado coloreado"""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; '
            'border: 1px solid #ddd; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def color_preview(self, obj):
        """Vista previa del color con código"""
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<div style="width: 60px; height: 40px; background-color: {}; '
            'border: 2px solid #ddd; border-radius: 5px;"></div>'
            '<span style="font-family: monospace; font-weight: bold;">{}</span>'
            '</div>',
            obj.color, obj.color
        )
    color_preview.short_description = 'Vista previa del color'
    
    def icon_display(self, obj):
        """Mostrar ícono de Font Awesome"""
        return format_html(
            '<i class="fas {}"></i> {}',
            obj.icon, obj.get_icon_display()
        )
    icon_display.short_description = 'Ícono'
    
    def is_active_badge(self, obj):
        """Mostrar estado activo/inactivo con badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #10B981; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-size: 11px;">Activa</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6B7280; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-size: 11px;">Inactiva</span>'
            )
    is_active_badge.short_description = 'Estado'
    
    def usage_count_display(self, obj):
        """Mostrar contador de uso"""
        count = obj.get_usage_count()
        return format_html(
            '<strong>{}</strong> usos',
            count
        )
    usage_count_display.short_description = 'Veces usada'
    
    def related_data_display(self, obj):
        """Mostrar información sobre datos relacionados"""
        related = obj.get_related_data()
        return format_html(
            '<ul style="margin: 0; padding-left: 20px;">'
            '<li>Transacciones: {}</li>'
            '<li>Presupuestos: {}</li>'
            '<li>Total usos: {}</li>'
            '<li>¿Se puede eliminar?: {}</li>'
            '</ul>',
            related['transactions_count'],
            related['budgets_count'],
            related['usage_count'],
            '✓ Sí' if related['can_be_deleted'] else '✗ No'
        )
    related_data_display.short_description = 'Datos relacionados'
    
    def activate_categories(self, request, queryset):
        """Acción para activar categorías seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categorías activadas correctamente.')
    activate_categories.short_description = 'Activar categorías seleccionadas'
    
    def deactivate_categories(self, request, queryset):
        """Acción para desactivar categorías seleccionadas"""
        # No desactivar categorías del sistema
        system_categories = queryset.filter(is_default=True)
        if system_categories.exists():
            self.message_user(
                request, 
                f'No se pueden desactivar {system_categories.count()} categorías del sistema.',
                level='warning'
            )
            queryset = queryset.exclude(is_default=True)
        
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categorías desactivadas correctamente.')
    deactivate_categories.short_description = 'Desactivar categorías seleccionadas'
    
    class Media:
        """Cargar Font Awesome para iconos"""
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',)
        }
