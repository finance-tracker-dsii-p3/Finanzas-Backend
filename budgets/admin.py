"""
Configuración del admin de Django para presupuestos
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Admin para gestionar presupuestos"""
    
    list_display = [
        'id',
        'user_link',
        'category_badge',
        'amount_display',
        'calculation_mode_badge',
        'period_badge',
        'spent_percentage_bar',
        'status_badge',
        'is_active_badge',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'period',
        'calculation_mode',
        'created_at'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'category__name'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'spent_info_display',
        'projection_display'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'user', 'category', 'amount', 'is_active')
        }),
        ('Configuración', {
            'fields': ('calculation_mode', 'period', 'start_date', 'alert_threshold')
        }),
        ('Estadísticas', {
            'fields': ('spent_info_display', 'projection_display'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Mostrar usuario con enlace"""
        from django.urls import reverse
        from django.utils.safestring import mark_safe
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return mark_safe(f'<a href="{url}">{obj.user.username}</a>')
    user_link.short_description = 'Usuario'
    
    def category_badge(self, obj):
        """Mostrar categoría con color"""
        color = obj.category.color
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.category.name
        )
    category_badge.short_description = 'Categoría'
    
    def amount_display(self, obj):
        """Mostrar monto formateado"""
        return f'${obj.amount:,.2f}'
    amount_display.short_description = 'Límite'
    amount_display.admin_order_field = 'amount'
    
    def calculation_mode_badge(self, obj):
        """Mostrar modo de cálculo con badge"""
        colors = {
            'base': '#3B82F6',
            'total': '#10B981'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.calculation_mode, '#6B7280'),
            obj.get_calculation_mode_display()
        )
    calculation_mode_badge.short_description = 'Modo'
    
    def period_badge(self, obj):
        """Mostrar período con badge"""
        colors = {
            'monthly': '#8B5CF6',
            'yearly': '#F59E0B'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.period, '#6B7280'),
            obj.get_period_display()
        )
    period_badge.short_description = 'Período'
    
    def spent_percentage_bar(self, obj):
        """Mostrar barra de progreso del gasto"""
        percentage = float(obj.get_spent_percentage())
        
        # Color según el estado
        if percentage >= 100:
            color = '#EF4444'  # Rojo
        elif percentage >= obj.alert_threshold:
            color = '#F59E0B'  # Amarillo
        else:
            color = '#10B981'  # Verde
        
        # Limitar a 100% para la barra visual
        bar_percentage = min(percentage, 100)
        
        return format_html(
            '<div style="width: 100px; background-color: #E5E7EB; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; height: 20px; display: flex; '
            'align-items: center; justify-content: center; color: white; font-size: 11px; font-weight: bold;">'
            '{}%'
            '</div>'
            '</div>',
            bar_percentage,
            color,
            round(percentage, 1)
        )
    spent_percentage_bar.short_description = '% Gastado'
    
    def status_badge(self, obj):
        """Mostrar estado del presupuesto"""
        status = obj.get_status()
        colors = {
            'good': '#10B981',
            'warning': '#F59E0B',
            'exceeded': '#EF4444'
        }
        texts = {
            'good': '✓ OK',
            'warning': '⚠ Alerta',
            'exceeded': '✗ Excedido'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(status, '#6B7280'),
            texts.get(status, 'Desconocido')
        )
    status_badge.short_description = 'Estado'
    
    def is_active_badge(self, obj):
        """Badge para estado activo/inactivo"""
        if obj.is_active:
            return format_html(
                '<span style="color: #10B981; font-weight: bold;">● Activo</span>'
            )
        return format_html(
            '<span style="color: #EF4444; font-weight: bold;">● Inactivo</span>'
        )
    is_active_badge.short_description = 'Estado'
    is_active_badge.boolean = True
    
    def spent_info_display(self, obj):
        """Mostrar información detallada del gasto"""
        spent = obj.get_spent_amount()
        percentage = obj.get_spent_percentage()
        remaining = obj.get_remaining_amount()
        daily_avg = obj.get_daily_average()
        
        return format_html(
            '<ul style="margin: 0; padding-left: 20px;">'
            '<li><strong>Gastado:</strong> ${:,.2f} ({}%)</li>'
            '<li><strong>Restante:</strong> ${:,.2f}</li>'
            '<li><strong>Promedio diario:</strong> ${:,.2f}</li>'
            '</ul>',
            spent,
            percentage,
            remaining,
            daily_avg
        )
    spent_info_display.short_description = 'Información de Gastos'
    
    def projection_display(self, obj):
        """Mostrar proyección del gasto"""
        projection = obj.get_projection()
        
        will_exceed_text = '✗ Sí' if projection['will_exceed'] else '✓ No'
        will_exceed_color = '#EF4444' if projection['will_exceed'] else '#10B981'
        
        return format_html(
            '<ul style="margin: 0; padding-left: 20px;">'
            '<li><strong>Proyección:</strong> ${:,.2f} ({}%)</li>'
            '<li><strong>¿Excederá?</strong> <span style="color: {}; font-weight: bold;">{}</span></li>'
            '<li><strong>Días restantes:</strong> {} de {}</li>'
            '</ul>',
            projection['projected_amount'],
            projection['projected_percentage'],
            will_exceed_color,
            will_exceed_text,
            projection['days_remaining'],
            projection['days_total']
        )
    projection_display.short_description = 'Proyección'
    
    actions = ['activate_budgets', 'deactivate_budgets']
    
    def activate_budgets(self, request, queryset):
        """Acción para activar presupuestos seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} presupuesto(s) activado(s).')
    activate_budgets.short_description = 'Activar presupuestos seleccionados'
    
    def deactivate_budgets(self, request, queryset):
        """Acción para desactivar presupuestos seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} presupuesto(s) desactivado(s).')
    deactivate_budgets.short_description = 'Desactivar presupuestos seleccionados'

