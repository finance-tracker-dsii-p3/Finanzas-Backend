"""
Administración de reglas automáticas (HU-12)
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AutomaticRule


@admin.register(AutomaticRule)
class AutomaticRuleAdmin(admin.ModelAdmin):
    """
    Administración de reglas automáticas con visualización rica
    """
    list_display = [
        'name', 'user', 'criteria_badge', 'action_badge', 
        'is_active_badge', 'order', 'applied_count', 'created_at'
    ]
    list_filter = [
        'is_active', 'criteria_type', 'action_type', 
        'target_transaction_type', 'created_at'
    ]
    search_fields = ['name', 'keyword', 'target_tag', 'user__username', 'user__email']
    ordering = ['user', 'order', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'applied_count']
    
    fieldsets = [
        ('Información Básica', {
            'fields': ['user', 'name', 'is_active', 'order']
        }),
        ('Criterio de Aplicación', {
            'fields': ['criteria_type', 'keyword', 'target_transaction_type'],
            'description': 'Define cuándo se aplicará la regla'
        }),
        ('Acción a Realizar', {
            'fields': ['action_type', 'target_category', 'target_tag'],
            'description': 'Define qué se hará cuando se cumpla el criterio'
        }),
        ('Estadísticas', {
            'fields': ['applied_count', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def criteria_badge(self, obj):
        """Badge visual para el tipo de criterio"""
        colors = {
            'description_contains': '#3B82F6',  # Azul
            'transaction_type': '#10B981',      # Verde
        }
        color = colors.get(obj.criteria_type, '#6B7280')
        
        if obj.criteria_type == 'description_contains':
            text = f"Descripción: '{obj.keyword}'"
        elif obj.criteria_type == 'transaction_type':
            text = f"Tipo: {obj.get_target_transaction_type_display()}"
        else:
            text = obj.get_criteria_type_display()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, text
        )
    criteria_badge.short_description = 'Criterio'
    
    def action_badge(self, obj):
        """Badge visual para el tipo de acción"""
        colors = {
            'assign_category': '#EF4444',  # Rojo
            'assign_tag': '#F59E0B',       # Amarillo
        }
        color = colors.get(obj.action_type, '#6B7280')
        
        if obj.action_type == 'assign_category':
            text = f"Categoría: {obj.target_category.name if obj.target_category else 'N/A'}"
        elif obj.action_type == 'assign_tag':
            text = f"Etiqueta: '{obj.target_tag}'"
        else:
            text = obj.get_action_type_display()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, text
        )
    action_badge.short_description = 'Acción'
    
    def is_active_badge(self, obj):
        """Badge visual para el estado activo/inactivo"""
        if obj.is_active:
            color = '#10B981'
            text = '✓ Activa'
        else:
            color = '#EF4444'
            text = '✗ Inactiva'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, text
        )
    is_active_badge.short_description = 'Estado'
    
    def applied_count(self, obj):
        """Número de transacciones a las que se ha aplicado la regla"""
        count = obj.applied_transactions.count()
        return f"{count} transacciones"
    applied_count.short_description = 'Aplicaciones'
    
    actions = ['activate_rules', 'deactivate_rules']
    
    def activate_rules(self, request, queryset):
        """Acción para activar reglas seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} reglas activadas exitosamente.'
        )
    activate_rules.short_description = 'Activar reglas seleccionadas'
    
    def deactivate_rules(self, request, queryset):
        """Acción para desactivar reglas seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} reglas desactivadas exitosamente.'
        )
    deactivate_rules.short_description = 'Desactivar reglas seleccionadas'
