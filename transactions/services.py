"""
Servicios de lógica de negocio para transacciones
"""
from django.db import transaction as db_transaction
from decimal import Decimal
from accounts.models import Account
import logging

logger = logging.getLogger(__name__)


class TransactionService:
    """Servicio para gestionar transacciones y actualización de saldos"""
    
    # Tipos de transacción
    INCOME = 1
    EXPENSE = 2
    TRANSFER = 3
    SAVING = 4
    
    @staticmethod
    @db_transaction.atomic
    def update_account_balance_for_transaction(transaction, is_creation=True):
        """
        Actualizar saldos de cuentas basado en una transacción
        
        Args:
            transaction: Instancia de Transaction
            is_creation: True si es creación, False si es eliminación (revertir)
        """
        transaction_type = transaction.type
        amount = Decimal(str(transaction.total_amount))
        
        # Determinar si sumar o restar (para eliminación, invertir la operación)
        multiplier = 1 if is_creation else -1
        
        try:
            if transaction_type == TransactionService.INCOME:
                # Ingreso: aumentar saldo de cuenta origen
                TransactionService._update_account_balance(
                    transaction.origin_account,
                    amount * multiplier,
                    transaction
                )
                
            elif transaction_type == TransactionService.EXPENSE:
                # Gasto: disminuir saldo de cuenta origen
                TransactionService._update_account_balance(
                    transaction.origin_account,
                    -amount * multiplier,
                    transaction
                )
                
            elif transaction_type == TransactionService.TRANSFER:
                # Transferencia: disminuir origen, aumentar destino
                if transaction.origin_account:
                    TransactionService._update_account_balance(
                        transaction.origin_account,
                        -amount * multiplier,
                        transaction
                    )
                if transaction.destination_account:
                    # Para tarjetas de crédito, solo el capital reduce la deuda
                    # Los intereses ya estaban incluidos en la deuda como transacciones separadas
                    if (transaction.destination_account.category == Account.CREDIT_CARD and
                        transaction.capital_amount is not None):
                        # Usar solo el capital para actualizar el saldo de la tarjeta
                        capital_amount = Decimal(str(transaction.capital_amount))
                        TransactionService._update_account_balance(
                            transaction.destination_account,
                            capital_amount * multiplier,
                            transaction
                        )
                    else:
                        # Para otras cuentas, usar el monto total
                        TransactionService._update_account_balance(
                            transaction.destination_account,
                            amount * multiplier,
                            transaction
                        )
                    
            elif transaction_type == TransactionService.SAVING:
                # Ahorro: similar a ingreso, aumentar saldo
                TransactionService._update_account_balance(
                    transaction.origin_account,
                    amount * multiplier,
                    transaction
                )
            
            logger.info(
                f"Saldo actualizado para transacción {transaction.id} "
                f"(tipo: {transaction_type}, creación: {is_creation})"
            )
            
        except Exception as e:
            logger.error(
                f"Error al actualizar saldo para transacción {transaction.id}: {str(e)}"
            )
            raise
    
    @staticmethod
    def _update_account_balance(account, amount_delta, transaction):
        """
        Actualizar el saldo de una cuenta
        
        Args:
            account: Instancia de Account
            amount_delta: Cantidad a sumar/restar (puede ser negativo)
            transaction: Transacción relacionada (para logging)
        """
        # Usar select_for_update para evitar condiciones de carrera
        account = Account.objects.select_for_update().get(pk=account.pk)
        
        old_balance = account.current_balance
        account.current_balance += amount_delta
        account.save(update_fields=['current_balance', 'updated_at'])
        
        logger.info(
            f"Cuenta {account.id} ({account.name}): "
            f"${old_balance} -> ${account.current_balance} "
            f"(delta: ${amount_delta}) - Transacción {transaction.id}"
        )
    
    @staticmethod
    @db_transaction.atomic
    def handle_transaction_creation(transaction):
        """
        Manejar la creación de una transacción (validar y actualizar saldos)
        
        Args:
            transaction: Instancia de Transaction recién creada
        """
        # Validar límites ANTES de actualizar saldos
        TransactionService._validate_transaction_limits(transaction)
        
        # Actualizar saldos
        TransactionService.update_account_balance_for_transaction(
            transaction,
            is_creation=True
        )
    
    @staticmethod
    @db_transaction.atomic
    def handle_transaction_update(old_transaction, new_transaction):
        """
        Manejar la actualización de una transacción
        
        Primero revierte el cambio anterior, luego valida y aplica el nuevo.
        
        Args:
            old_transaction: Datos de la transacción antes del cambio
            new_transaction: Instancia de Transaction actualizada
        """
        # Revertir el cambio anterior
        TransactionService.update_account_balance_for_transaction(
            old_transaction,
            is_creation=False  # Revertir
        )
        
        # Validar límites ANTES de aplicar el nuevo cambio
        TransactionService._validate_transaction_limits(new_transaction)
        
        # Aplicar el nuevo cambio
        TransactionService.update_account_balance_for_transaction(
            new_transaction,
            is_creation=True
        )
    
    @staticmethod
    def _validate_transaction_limits(transaction):
        """
        Validar que una transacción no exceda los límites de las cuentas
        
        Args:
            transaction: Instancia de Transaction
        """
        from accounts.models import Account
        from decimal import Decimal
        
        transaction_type = transaction.type
        amount = Decimal(str(transaction.total_amount))
        
        # Validar cuenta origen
        if transaction.origin_account:
            account = Account.objects.get(pk=transaction.origin_account.pk)
            current_balance = account.current_balance
            
            # Calcular saldo resultante (disminuye para gastos/transferencias)
            if transaction_type in [TransactionService.EXPENSE, TransactionService.TRANSFER]:
                new_balance = current_balance - amount
                
                # Validar según tipo de cuenta
                if account.account_type == Account.ASSET:
                    if new_balance < 0:
                        raise ValueError(
                            f'No se puede realizar esta transacción. El saldo resultante sería negativo '
                            f'(${new_balance:,.2f}). Saldo actual: ${current_balance:,.2f}, Monto: ${amount:,.2f}'
                        )
                
                elif account.account_type == Account.LIABILITY:
                    if account.category == Account.CREDIT_CARD:
                        if account.credit_limit is None:
                            raise ValueError('La tarjeta de crédito no tiene límite de crédito definido.')
                        
                        current_debt = abs(current_balance)
                        new_debt = abs(new_balance) if new_balance < 0 else Decimal('0.00')
                        
                        if new_debt > account.credit_limit:
                            available_credit = account.credit_limit - current_debt
                            raise ValueError(
                                f'No se puede realizar esta transacción. Se excedería el límite de crédito. '
                                f'Límite: ${account.credit_limit:,.2f}, Deuda actual: ${current_debt:,.2f}, '
                                f'Crédito disponible: ${available_credit:,.2f}, Monto: ${amount:,.2f}'
                            )
                        
                        if new_balance > 0:
                            raise ValueError('Las tarjetas de crédito no pueden tener saldo positivo.')
                    else:
                        if new_balance > 0:
                            raise ValueError('Las cuentas de pasivo no pueden tener saldo positivo.')
        
        # Validar cuenta destino (solo para transferencias)
        if transaction.destination_account and transaction_type == TransactionService.TRANSFER:
            account = Account.objects.get(pk=transaction.destination_account.pk)
            current_balance = account.current_balance
            new_balance = current_balance + amount  # Aumenta para transferencias
            
            if account.account_type == Account.LIABILITY:
                if account.category == Account.CREDIT_CARD:
                    if new_balance > 0:
                        raise ValueError('Las tarjetas de crédito no pueden tener saldo positivo.')
                else:
                    if new_balance > 0:
                        raise ValueError('Las cuentas de pasivo no pueden tener saldo positivo.')
    
    @staticmethod
    @db_transaction.atomic
    def handle_transaction_deletion(transaction):
        """
        Manejar la eliminación de una transacción (revertir cambios en saldos)
        
        Args:
            transaction: Instancia de Transaction a eliminar
        """
        TransactionService.update_account_balance_for_transaction(
            transaction,
            is_creation=False  # Revertir
        )

