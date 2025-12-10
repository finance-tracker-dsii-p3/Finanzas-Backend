"""
Tests para verificar el cálculo de credit_card_details
Específicamente para detectar el error de total_paid y capital_paid
"""

from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Account
from accounts.services import AccountService
from transactions.models import Transaction
from transactions.services import TransactionService

User = get_user_model()


class CreditCardDetailsCalculationTests(TestCase):
    """Tests para verificar el cálculo correcto de total_paid y capital_paid"""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Crear cuenta bancaria
        self.bank = Account.objects.create(
            user=self.user,
            name="Banco Test",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("10000.00"),  # 10,000 pesos
            currency="COP",
        )

        # Crear tarjeta de crédito
        self.credit_card = Account.objects.create(
            user=self.user,
            name="TC Test",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            current_balance=Decimal("-5000.00"),  # Deuda de 5,000 pesos
            currency="COP",
            credit_limit=Decimal("10000.00"),  # Límite de 10,000 pesos
        )

    def test_total_paid_calculation_with_transfer_payment(self):
        """
        Test para verificar que total_paid se calcula correctamente.

        Escenario:
        - Pago de 1,000 pesos (100,000 centavos) a la tarjeta
        - NOTA: Los pagos a tarjetas de crédito NO tienen GMF (según la lógica implementada)
        - total_amount = 100,000 centavos (sin GMF)
        - total_paid debería ser 1,000 pesos (sin GMF), NO 100,400 pesos
        """
        # Crear transferencia de pago (1,000 pesos = 100,000 centavos)
        payment_amount_cents = 100000  # 1,000 pesos en centavos

        transfer = Transaction.objects.create(
            user=self.user,
            origin_account=self.bank,
            destination_account=self.credit_card,
            type=TransactionService.TRANSFER,
            base_amount=payment_amount_cents,
            total_amount=payment_amount_cents,  # Sin GMF porque destino es tarjeta de crédito
            date=date.today(),
        )

        # Refrescar para obtener el total_amount final
        transfer.refresh_from_db()

        # Los pagos a tarjetas de crédito NO tienen GMF
        expected_total_paid = Decimal("1000.00")  # Solo el monto base, sin GMF

        # Actualizar saldos
        TransactionService.handle_transaction_creation(transfer)

        # Obtener detalles de la tarjeta
        details = AccountService.get_credit_card_details(self.credit_card)

        print(f"\n[TEST] total_paid calculado: {details['total_paid']}")
        print(f"[TEST] total_paid esperado: {expected_total_paid} (1,000 sin GMF)")
        print(f"[TEST] Diferencia: {details['total_paid'] - expected_total_paid}")
        print(
            f"[TEST] GMF calculado: {transfer.gmf_amount} centavos = {Decimal(str(transfer.gmf_amount)) / Decimal('100')} pesos"
        )

        # El test fallará si el error existe (total_paid será 100,400)
        # Si está correcto, total_paid será 1,000 (sin GMF porque es pago a tarjeta)
        self.assertEqual(
            details["total_paid"],
            expected_total_paid,
            f"total_paid debería ser {expected_total_paid} pesos (1,000 sin GMF), pero es {details['total_paid']} pesos. "
            f"Si es 100,400, el error está confirmado (100x mayor).",
        )

    def test_capital_paid_calculation_with_capital_amount(self):
        """
        Test para verificar que capital_paid se calcula correctamente cuando hay capital_amount.

        Escenario:
        - Pago de 1,000 pesos con capital_amount de 800 pesos (200 son intereses)
        - GMF = 1,000 * 0.004 = 4 pesos
        - total_amount = 1,004 pesos
        - total_paid debería ser 1,004 pesos (incluye GMF), NO 100,400 pesos
        """
        # Crear transferencia con capital_amount específico
        base_payment_cents = 100000  # 1,000 pesos base
        capital_amount_cents = 80000  # 800 pesos de capital

        transfer = Transaction.objects.create(
            user=self.user,
            origin_account=self.bank,
            destination_account=self.credit_card,
            type=TransactionService.TRANSFER,
            base_amount=base_payment_cents,
            total_amount=base_payment_cents,  # Se actualizará con GMF en save()
            capital_amount=capital_amount_cents,
            interest_amount=base_payment_cents - capital_amount_cents,
            date=date.today(),
        )

        # Refrescar para obtener el total_amount con GMF calculado
        transfer.refresh_from_db()

        # Los pagos a tarjetas de crédito NO tienen GMF
        expected_total_paid = Decimal("1000.00")  # Solo el monto base, sin GMF

        # Actualizar saldos
        TransactionService.handle_transaction_creation(transfer)

        # Obtener detalles de la tarjeta
        details = AccountService.get_credit_card_details(self.credit_card)

        print(f"\n[TEST] total_paid con capital_amount: {details['total_paid']}")
        print(f"[TEST] total_paid esperado: {expected_total_paid} (1,000 sin GMF)")
        print(f"[TEST] GMF calculado: {transfer.gmf_amount} centavos")

        self.assertEqual(
            details["total_paid"],
            expected_total_paid,
            f"total_paid debería ser {expected_total_paid} pesos (1,000 sin GMF), pero es {details['total_paid']} pesos.",
        )

    def test_total_paid_with_multiple_payments(self):
        """
        Test para verificar total_paid con múltiples pagos.

        Escenario:
        - Pago 1: 500 pesos (50,000 centavos) sin GMF = 500 pesos
        - Pago 2: 300 pesos (30,000 centavos) sin GMF = 300 pesos
        - NOTA: Los pagos a tarjetas de crédito NO tienen GMF
        - total_paid debería ser 800 pesos, NO 80,320 pesos
        """
        # Primer pago: 500 pesos
        payment1 = Transaction.objects.create(
            user=self.user,
            origin_account=self.bank,
            destination_account=self.credit_card,
            type=TransactionService.TRANSFER,
            base_amount=50000,  # 500 pesos en centavos
            total_amount=50000,  # Se actualizará con GMF en save()
            date=date.today(),
        )
        payment1.refresh_from_db()
        TransactionService.handle_transaction_creation(payment1)

        # Segundo pago: 300 pesos
        payment2 = Transaction.objects.create(
            user=self.user,
            origin_account=self.bank,
            destination_account=self.credit_card,
            type=TransactionService.TRANSFER,
            base_amount=30000,  # 300 pesos en centavos
            total_amount=30000,  # Se actualizará con GMF en save()
            date=date.today(),
        )
        payment2.refresh_from_db()
        TransactionService.handle_transaction_creation(payment2)

        # Obtener detalles
        details = AccountService.get_credit_card_details(self.credit_card)

        # Los pagos a tarjetas de crédito NO tienen GMF
        expected_total_paid = Decimal("500.00") + Decimal("300.00")  # 800 pesos (sin GMF)

        print(f"\n[TEST] total_paid con múltiples pagos: {details['total_paid']}")
        print(f"[TEST] total_paid esperado: {expected_total_paid} (500 + 300 sin GMF)")
        print(
            f"[TEST] GMF pago 1: {payment1.gmf_amount} centavos = {Decimal(str(payment1.gmf_amount)) / Decimal('100')} pesos"
        )
        print(
            f"[TEST] GMF pago 2: {payment2.gmf_amount} centavos = {Decimal(str(payment2.gmf_amount)) / Decimal('100')} pesos"
        )

        self.assertEqual(
            details["total_paid"],
            expected_total_paid,
            f"total_paid debería ser {expected_total_paid} pesos (500 + 300 sin GMF), pero es {details['total_paid']} pesos.",
        )
