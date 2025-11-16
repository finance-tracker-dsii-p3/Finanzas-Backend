"""
Services para la lógica de negocio de cuentas
"""
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Count, Q
from .models import Account


class AccountService:
    """
    Service class para operaciones de negocio relacionadas con cuentas
    """
    
    @staticmethod
    def get_user_accounts(user, include_inactive=False):
        """
        Obtener todas las cuentas de un usuario
        
        Args:
            user: Usuario propietario
            include_inactive (bool): Si incluir cuentas inactivas
            
        Returns:
            QuerySet de cuentas del usuario
        """
        queryset = Account.objects.filter(user=user).order_by('name')
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
            
        return queryset
    
    @staticmethod
    def get_accounts_summary(user):
        """
        Calcular resumen financiero del usuario
        
        Args:
            user: Usuario propietario
            
        Returns:
            dict: Resumen con totales, patrimonio neto, etc.
        """
        accounts = Account.objects.filter(user=user, is_active=True)
        
        # Calcular totales por tipo
        total_assets = Decimal('0.00')
        total_liabilities = Decimal('0.00')
        
        # Balances por moneda
        balances_by_currency = {}
        
        # Cuentas por categoría
        accounts_by_category = {}
        
        for account in accounts:
            # Totales por tipo
            if account.account_type == Account.ASSET:
                total_assets += account.current_balance
            else:  # LIABILITY
                total_liabilities += abs(account.current_balance)
            
            # Balances por moneda
            if account.currency not in balances_by_currency:
                balances_by_currency[account.currency] = {
                    'assets': Decimal('0.00'),
                    'liabilities': Decimal('0.00'),
                    'net': Decimal('0.00')
                }
            
            if account.account_type == Account.ASSET:
                balances_by_currency[account.currency]['assets'] += account.current_balance
            else:
                balances_by_currency[account.currency]['liabilities'] += abs(account.current_balance)
            
            # Actualizar neto por moneda
            balances_by_currency[account.currency]['net'] = (
                balances_by_currency[account.currency]['assets'] - 
                balances_by_currency[account.currency]['liabilities']
            )
            
            # Cuentas por categoría
            category_name = account.get_category_display()
            if category_name not in accounts_by_category:
                accounts_by_category[category_name] = {
                    'count': 0,
                    'balance': Decimal('0.00')
                }
            
            accounts_by_category[category_name]['count'] += 1
            # Para el modelo simplificado, usamos current_balance directamente
            if account.account_type == Account.ASSET:
                accounts_by_category[category_name]['balance'] += account.current_balance
            else:  # LIABILITY - usar valor absoluto
                accounts_by_category[category_name]['balance'] += abs(account.current_balance)
        
        # Patrimonio neto
        net_worth = total_assets - total_liabilities
        
        # Estadísticas generales
        accounts_count = accounts.count()
        active_accounts_count = accounts.filter(is_active=True).count()
        
        return {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'net_worth': net_worth,
            'accounts_count': accounts_count,
            'active_accounts_count': active_accounts_count,
            'balances_by_currency': balances_by_currency,
            'accounts_by_category': accounts_by_category
        }
    
    @staticmethod
    @transaction.atomic
    def create_account(user, account_data):
        """
        Crear nueva cuenta con validaciones de negocio
        
        Args:
            user: Usuario propietario
            account_data (dict): Datos de la cuenta
            
        Returns:
            Account: Cuenta creada
        """
        # Validar límite de cuentas por usuario (opcional)
        user_accounts_count = Account.objects.filter(user=user, is_active=True).count()
        
        if user_accounts_count >= 50:  # Límite configurable
            raise ValueError('Has alcanzado el límite máximo de cuentas (50)')
        
        # Crear la cuenta
        account_data['user'] = user
        account = Account.objects.create(**account_data)
        
        return account
    
    @staticmethod
    @transaction.atomic
    def update_account(account, update_data):
        """
        Actualizar cuenta existente
        
        Args:
            account (Account): Cuenta a actualizar
            update_data (dict): Datos a actualizar
            
        Returns:
            Account: Cuenta actualizada
        """
        # Validar si hay cambios que afecten transacciones existentes
        critical_fields = ['currency', 'account_type']
        
        for field in critical_fields:
            if field in update_data and getattr(account, field) != update_data[field]:
                # TODO: Validar si la cuenta tiene transacciones
                # if account.transactions.exists():
                #     raise ValueError(f'No se puede cambiar {field} en cuentas con transacciones')
                pass
        
        # Actualizar campos
        for field, value in update_data.items():
            setattr(account, field, value)
        
        account.full_clean()  # Validar modelo
        account.save()
        
        return account
    
    @staticmethod
    @transaction.atomic
    def delete_account(account):
        """
        Eliminar cuenta con validaciones
        
        Args:
            account (Account): Cuenta a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            ValueError: Si la cuenta no puede ser eliminada
        """
        # Verificar si puede ser eliminada
        if not account.can_be_deleted():
            raise ValueError(
                'No se puede eliminar la cuenta porque tiene transacciones asociadas. '
                'Primero debe eliminar todas las transacciones o transferir el saldo.'
            )
        
        # Verificar saldo
        if account.current_balance != 0:
            raise ValueError(
                f'No se puede eliminar la cuenta porque tiene saldo: '
                f'{account.current_balance} {account.currency}'
            )
        
        account_name = account.name
        account.delete()
        
        return True
    
    @staticmethod
    @transaction.atomic
    def update_account_balance(account, new_balance, reason=None):
        """
        Actualizar saldo de cuenta manualmente (ajuste)
        
        Args:
            account (Account): Cuenta a actualizar
            new_balance (Decimal): Nuevo saldo
            reason (str): Razón del ajuste
            
        Returns:
            Account: Cuenta actualizada
        """
        old_balance = account.current_balance
        account.current_balance = new_balance
        account.save(update_fields=['current_balance', 'updated_at'])
        
        # TODO: Registrar el ajuste en un log de auditoria
        # AuditLog.objects.create(
        #     account=account,
        #     action='balance_adjustment',
        #     old_value=old_balance,
        #     new_value=new_balance,
        #     reason=reason
        # )
        
        return account
    
    @staticmethod
    def get_accounts_by_currency(user, currency):
        """
        Obtener cuentas de un usuario filtradas por moneda
        
        Args:
            user: Usuario propietario
            currency (str): Código de moneda (COP, USD, EUR)
            
        Returns:
            QuerySet: Cuentas en la moneda especificada
        """
        return Account.objects.filter(
            user=user, 
            currency=currency,
            is_active=True
        ).order_by('name')
    
    @staticmethod
    def get_credit_cards_summary(user):
        """
        Obtener resumen específico de tarjetas de crédito
        
        Args:
            user: Usuario propietario
            
        Returns:
            dict: Resumen de tarjetas de crédito
        """
        credit_cards = Account.objects.filter(
            user=user,
            category=Account.CREDIT_CARD,
            is_active=True
        )
        
        # Nota: El modelo simplificado no tiene credit_limit
        # Por ahora retornamos solo el conteo y saldo usado
        total_used_credit = sum(
            abs(card.current_balance) for card in credit_cards
        )
        
        return {
            'cards_count': credit_cards.count(),
            'total_credit_limit': Decimal('0.00'),  # No disponible en modelo simplificado
            'total_used_credit': total_used_credit,
            'available_credit': Decimal('0.00'),  # No se puede calcular sin credit_limit
            'utilization_percentage': 0.0  # No se puede calcular sin credit_limit
        }
    
    @staticmethod
    def validate_account_deletion_with_confirmation(account, force=False):
        """
        Validar eliminación de cuenta con confirmación
        
        Args:
            account (Account): Cuenta a eliminar
            force (bool): Si forzar eliminación ignorando advertencias
            
        Returns:
            dict: Resultado de la validación
        """
        result = {
            'can_delete': True,
            'requires_confirmation': False,
            'warnings': [],
            'errors': []
        }
        
        # Verificar saldo
        if account.current_balance != 0:
            result['warnings'].append(
                f'La cuenta tiene saldo: {account.current_balance} {account.currency}'
            )
            result['requires_confirmation'] = True
        
        # TODO: Verificar transacciones cuando esté implementado
        # if account.transactions.exists():
        #     result['warnings'].append(
        #         f'La cuenta tiene {account.transactions.count()} transacciones'
        #     )
        #     result['requires_confirmation'] = True
        
        # Verificar si es la única cuenta en su moneda
        same_currency_accounts = Account.objects.filter(
            user=account.user,
            currency=account.currency,
            is_active=True
        ).exclude(id=account.id).count()
        
        if same_currency_accounts == 0:
            result['warnings'].append(
                f'Es la única cuenta en {account.currency}'
            )
            result['requires_confirmation'] = True
        
        # Si hay errores críticos
        if not account.can_be_deleted() and not force:
            result['can_delete'] = False
            result['errors'].append(
                'La cuenta tiene transacciones asociadas y no puede ser eliminada'
            )
        
        return result