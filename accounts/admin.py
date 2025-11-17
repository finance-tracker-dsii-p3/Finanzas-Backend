"""
Admin interface para cuentas financieras
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Account, AccountOption


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Configuración del admin para cuentas
    """
    list_display = [
        'name',
        'user_display', 
        'category_display',
        'account_type_display',
        'balance_display',
        'currency',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'account_type',
        'category', 
        'currency',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'user__username',
        'user__email',
        'user__first_name', 
        'user__last_name',
        'description'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'user',
                'name',
                'bank_name',
                'account_number',
                'description',
                'account_type',
                'category'
            )
        }),
        ('Detalles Financieros', {
            'fields': (
                'current_balance',
                'currency',
                'gmf_exempt'
            )
        }),
        ('Tarjeta de Crédito', {
            'fields': (
                'expiration_date',
                'credit_limit'
            ),
            'classes': ('collapse',),
            'description': 'Solo aplica para tarjetas de crédito'
        }),
        ('Estado y Fechas', {
            'fields': (
                'is_active',
                'created_at',
                'updated_at'
            )
        }),
        ('Información Técnica', {
            'fields': (
                'id',
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['user__username', 'name']
    
    def user_display(self, obj):
        """Mostrar información del usuario"""
        return f"{obj.user.get_full_name() or obj.user.username} ({obj.user.email})"
    user_display.short_description = 'Usuario'
    
    def category_display(self, obj):
        """Mostrar categoría con color"""
        colors = {
            Account.BANK_ACCOUNT: '#28a745',
            Account.SAVINGS_ACCOUNT: '#17a2b8',
            Account.CREDIT_CARD: '#dc3545',
            Account.WALLET: '#ffc107',
            Account.OTHER: '#6c757d'
        }
        
        color = colors.get(obj.category, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_display.short_description = 'Categoría'
    
    def account_type_display(self, obj):
        """Mostrar tipo de cuenta con badge"""
        if obj.account_type == Account.ASSET:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px;">ACTIVO</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px;">PASIVO</span>'
            )
    account_type_display.short_description = 'Tipo'
    
    def balance_display(self, obj):
        """Mostrar balance con formato y color"""
        balance = obj.current_balance
        
        if balance > 0:
            color = '#28a745'
        elif balance < 0:
            color = '#dc3545'
        else:
            color = '#6c757d'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:,.2f}</span>',
            color,
            balance
        )
    balance_display.short_description = 'Saldo'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related('user')
    
    def has_delete_permission(self, request, obj=None):
        """Verificar si se puede eliminar"""
        if obj:
            return obj.can_be_deleted()
        return True
    
    actions = ['activate_accounts', 'deactivate_accounts']
    
    def activate_accounts(self, request, queryset):
        """Activar cuentas seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'{updated} cuenta(s) activada(s) exitosamente.'
        )
    activate_accounts.short_description = "Activar cuentas seleccionadas"
    
    def deactivate_accounts(self, request, queryset):
        """Desactivar cuentas seleccionadas (solo sin saldo)"""
        accounts_with_balance = queryset.exclude(current_balance=0)
        
        if accounts_with_balance.exists():
            self.message_user(
                request,
                f'{accounts_with_balance.count()} cuenta(s) no se pueden desactivar porque tienen saldo.',
                level='warning'
            )
        
        accounts_without_balance = queryset.filter(current_balance=0)
        updated = accounts_without_balance.update(is_active=False)
        
        self.message_user(
            request, 
            f'{updated} cuenta(s) desactivada(s) exitosamente.'
        )
    deactivate_accounts.short_description = "Desactivar cuentas sin saldo"


@admin.register(AccountOption)
class AccountOptionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para opciones de cuentas (bancos, billeteras, etc.)
    """
    list_display = [
        'name',
        'option_type_display',
        'is_active',
        'order',
        'created_at'
    ]
    
    list_filter = [
        'option_type',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name'
    ]
    
    ordering = ['option_type', 'order', 'name']
    
    list_editable = ['is_active', 'order']  # Permite editar directamente desde la lista
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'option_type')
        }),
        ('Configuración', {
            'fields': ('is_active', 'order')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def option_type_display(self, obj):
        """Mostrar tipo de opción con badge"""
        colors = {
            'bank': '#28a745',  # Verde
            'wallet': '#ffc107',  # Amarillo
            'credit_card_bank': '#dc3545',  # Rojo
        }
        
        color = colors.get(obj.option_type, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color,
            obj.get_option_type_display()
        )
    option_type_display.short_description = 'Tipo'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related()
