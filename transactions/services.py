import logging
from decimal import Decimal

from django.db import transaction as db_transaction

from accounts.models import Account

logger = logging.getLogger(__name__)


class TransactionService:
    INCOME = 1
    EXPENSE = 2
    TRANSFER = 3
    SAVING = 4

    @staticmethod
    @db_transaction.atomic
    def update_account_balance_for_transaction(transaction, is_creation=True):
        transaction_type = transaction.type
        total_amount_cents = transaction.total_amount
        amount = Decimal(str(total_amount_cents)) / Decimal(100)

        print(
            f"[DEBUG SERVICE] Actualizando saldo - Transacción ID: {transaction.id}, "
            f"total_amount (centavos): {total_amount_cents}, "
            f"amount (pesos): {amount}, "
            f"tipo: {transaction_type}, "
            f"creación: {is_creation}"
        )
        logger.info(
            f"[DEBUG] Actualizando saldo - Transacción ID: {transaction.id}, "
            f"total_amount (centavos): {total_amount_cents}, "
            f"amount (pesos): {amount}, "
            f"tipo: {transaction_type}, "
            f"creación: {is_creation}"
        )

        multiplier = 1 if is_creation else -1

        try:
            if transaction_type == TransactionService.INCOME:
                TransactionService._update_account_balance(
                    transaction.origin_account, amount * multiplier, transaction
                )

            elif transaction_type == TransactionService.EXPENSE:
                TransactionService._update_account_balance(
                    transaction.origin_account, -amount * multiplier, transaction
                )

            elif transaction_type == TransactionService.TRANSFER:
                if transaction.origin_account:
                    TransactionService._update_account_balance(
                        transaction.origin_account, -amount * multiplier, transaction
                    )
                if transaction.destination_account:
                    if (
                        transaction.destination_account.category == Account.CREDIT_CARD
                        and transaction.capital_amount is not None
                    ):
                        capital_amount = Decimal(str(transaction.capital_amount)) / Decimal(100)
                        TransactionService._update_account_balance(
                            transaction.destination_account,
                            capital_amount * multiplier,
                            transaction,
                        )
                    else:
                        TransactionService._update_account_balance(
                            transaction.destination_account, amount * multiplier, transaction
                        )

            elif transaction_type == TransactionService.SAVING:
                # SAVING debe RESTAR de la cuenta (el dinero se mueve a la meta)
                TransactionService._update_account_balance(
                    transaction.origin_account, -amount * multiplier, transaction
                )

            logger.info(
                f"Saldo actualizado para transacción {transaction.id} "
                f"(tipo: {transaction_type}, creación: {is_creation})"
            )

        except Exception as e:
            logger.exception(f"Error al actualizar saldo para transacción {transaction.id}: {e!s}")
            raise

    @staticmethod
    def _update_account_balance(account, amount_delta, transaction):
        account = Account.objects.select_for_update().get(pk=account.pk)

        old_balance = account.current_balance
        account.current_balance += amount_delta
        account.save(update_fields=["current_balance", "updated_at"])

        print(
            f"[DEBUG SERVICE] Cuenta {account.id} ({account.name}): "
            f"Saldo anterior: ${old_balance}, "
            f"Delta aplicado: ${amount_delta}, "
            f"Nuevo saldo: ${account.current_balance}, "
            f"Transacción: {transaction.id}"
        )
        logger.info(
            f"[DEBUG] Cuenta {account.id} ({account.name}): "
            f"Saldo anterior: ${old_balance}, "
            f"Delta aplicado: ${amount_delta}, "
            f"Nuevo saldo: ${account.current_balance}, "
            f"Transacción: {transaction.id}"
        )

    @staticmethod
    @db_transaction.atomic
    def handle_transaction_creation(transaction):
        TransactionService._validate_transaction_limits(transaction)

        TransactionService.update_account_balance_for_transaction(transaction, is_creation=True)

    @staticmethod
    @db_transaction.atomic
    def handle_transaction_update(old_transaction, new_transaction):
        TransactionService.update_account_balance_for_transaction(
            old_transaction, is_creation=False
        )

        TransactionService._validate_transaction_limits(new_transaction)

        TransactionService.update_account_balance_for_transaction(new_transaction, is_creation=True)

    @staticmethod
    def _validate_transaction_limits(transaction):
        from decimal import Decimal

        from accounts.models import Account

        transaction_type = transaction.type
        amount = Decimal(str(transaction.total_amount)) / Decimal(100)

        # Validar cuenta origen
        if transaction.origin_account:
            account = Account.objects.get(pk=transaction.origin_account.pk)
            current_balance = account.current_balance

            # Income (1) y Saving (4) aumentan el saldo
            if transaction_type in [TransactionService.INCOME, TransactionService.SAVING]:
                new_balance = current_balance + amount

                # Para cuentas de activo, no hay restricción (pueden aumentar sin límite)
                # Para cuentas de pasivo, validar que no queden positivas
                if account.account_type == Account.LIABILITY:
                    if account.category == Account.CREDIT_CARD:
                        if new_balance > 0:
                            msg = "Las tarjetas de crédito no pueden tener saldo positivo."
                            raise ValueError(msg)
                    elif new_balance > 0:
                        msg = "Las cuentas de pasivo no pueden tener saldo positivo."
                        raise ValueError(msg)

            # Expense (2) y Transfer (3) disminuyen el saldo
            elif transaction_type in [TransactionService.EXPENSE, TransactionService.TRANSFER]:
                new_balance = current_balance - amount

                if account.account_type == Account.ASSET:
                    if new_balance < 0:
                        msg = (
                            f"No se puede realizar esta transacción. El saldo resultante sería negativo "
                            f"(${new_balance:,.2f}). Saldo actual: ${current_balance:,.2f}, Monto: ${amount:,.2f}"
                        )
                        raise ValueError(msg)

                elif account.account_type == Account.LIABILITY:
                    if account.category == Account.CREDIT_CARD:
                        if account.credit_limit is not None:
                            current_debt = abs(current_balance)
                            new_debt = abs(new_balance) if new_balance < 0 else Decimal("0.00")

                            if new_debt > account.credit_limit:
                                available_credit = account.credit_limit - current_debt
                                msg = (
                                    f"No se puede realizar esta transacción. Se excedería el límite de crédito. "
                                    f"Límite: ${account.credit_limit:,.2f}, Deuda actual: ${current_debt:,.2f}, "
                                    f"Crédito disponible: ${available_credit:,.2f}, Monto: ${amount:,.2f}"
                                )
                                raise ValueError(msg)

                        if new_balance > 0:
                            msg = "Las tarjetas de crédito no pueden tener saldo positivo."
                            raise ValueError(msg)
                    elif new_balance > 0:
                        msg = "Las cuentas de pasivo no pueden tener saldo positivo."
                        raise ValueError(msg)

        # Validar cuenta destino (solo para transferencias)
        if transaction.destination_account and transaction_type == TransactionService.TRANSFER:
            account = Account.objects.get(pk=transaction.destination_account.pk)
            current_balance = account.current_balance

            # Para transferencias, el destino recibe el monto (aumenta el saldo)
            # Si es tarjeta de crédito y tiene capital_amount, usar ese monto
            if account.category == Account.CREDIT_CARD and transaction.capital_amount is not None:
                capital_amount = Decimal(str(transaction.capital_amount)) / Decimal(100)
                new_balance = current_balance + capital_amount
            else:
                new_balance = current_balance + amount

            # Para cuentas de activo, no hay restricción (pueden recibir dinero)
            # Para cuentas de pasivo, validar que no queden positivas
            if account.account_type == Account.LIABILITY:
                if account.category == Account.CREDIT_CARD:
                    if new_balance > 0:
                        msg = "Las tarjetas de crédito no pueden tener saldo positivo."
                        raise ValueError(msg)
                elif new_balance > 0:
                    msg = "Las cuentas de pasivo no pueden tener saldo positivo."
                    raise ValueError(msg)

    @staticmethod
    @db_transaction.atomic
    def handle_transaction_deletion(transaction):
        TransactionService.update_account_balance_for_transaction(transaction, is_creation=False)
