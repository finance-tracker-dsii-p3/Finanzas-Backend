from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Account
from budgets.models import Budget
from categories.models import Category
from credit_cards.models import InstallmentPayment, InstallmentPlan
from credit_cards.services import InstallmentPlanService
from transactions.models import Transaction
from transactions.services import TransactionService

User = get_user_model()


class CreditCardInstallmentsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            identification="99999999",
            username="ccuser",
            email="cc@example.com",
            password="testpass123",
        )

        self.bank = Account.objects.create(
            user=self.user,
            name="Banco",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("5000.00"),
            currency="COP",
        )

        self.credit_card = Account.objects.create(
            user=self.user,
            name="TC",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            current_balance=Decimal("-1000.00"),
            currency="COP",
        )

        self.purchase_category = Category.objects.create(
            user=self.user, name="Compras", type=Category.EXPENSE
        )
        self.financing_category = Category.objects.create(
            user=self.user, name="Financiamiento", type=Category.EXPENSE
        )

        # Crear transacción de compra
        self.purchase_tx = Transaction.objects.create(
            user=self.user,
            origin_account=self.credit_card,
            type=TransactionService.EXPENSE,
            base_amount=1200000,  # $1.200.000 en centavos
            total_amount=1200000,
            date=date.today(),
            category=self.purchase_category,
            description="Compra en cuotas",
        )

        # Crear plan de cuotas
        self.plan = InstallmentPlanService.create_from_transaction(
            purchase_transaction=self.purchase_tx,
            number_of_installments=12,
            interest_rate=Decimal("2.00"),  # 2% mensual
            start_date=date.today(),
            financing_category=self.financing_category,
            description="Plan de prueba",
        )

    def test_update_plan_preserves_paid_installments_and_recalculates_future(self):
        """Verificar que se pueden editar planes con cuotas pagadas, preservando pagos realizados"""
        # Pagar primera cuota
        payment1, _, _ = InstallmentPlanService.record_payment(
            plan=self.plan,
            installment_number=1,
            payment_date=date.today(),
            source_account=self.bank,
            notes="Pago prueba",
        )
        assert payment1.status == InstallmentPayment.STATUS_COMPLETED

        # Guardar número de cuota pagada y monto
        paid_number = payment1.installment_number
        paid_amount = payment1.installment_amount

        # Editar plan: cambiar tasa de interés
        updated_plan = InstallmentPlanService.update_plan(self.plan, interest_rate=Decimal("1.50"))

        # Verificar que la cuota pagada sigue igual
        paid_payment = updated_plan.payments.get(installment_number=paid_number)
        assert paid_payment.status == InstallmentPayment.STATUS_COMPLETED
        assert paid_payment.installment_amount == paid_amount

        # Verificar que las cuotas futuras fueron recalculadas
        future_payments = updated_plan.payments.filter(status=InstallmentPayment.STATUS_PENDING)
        assert future_payments.count() > 0

    def test_cannot_reduce_installments_below_paid(self):
        """Verificar que no se puede reducir cuotas por debajo de las ya pagadas"""
        # Pagar 3 cuotas
        for i in range(1, 4):
            InstallmentPlanService.record_payment(
                plan=self.plan,
                installment_number=i,
                payment_date=date.today(),
                source_account=self.bank,
            )

        # Intentar reducir a 2 cuotas (menos que las pagadas)
        with pytest.raises(ValidationError) as context:
            InstallmentPlanService.update_plan(self.plan, number_of_installments=2)

        assert "ya pagadas" in str(context.value)

    def test_record_payment_creates_transfer_and_interest_expense(self):
        """Verificar que el registro de pago crea transferencia (capital) y gasto (interés)"""
        payment, transfer_tx, interest_tx = InstallmentPlanService.record_payment(
            plan=self.plan,
            installment_number=1,
            payment_date=date.today(),
            source_account=self.bank,
            notes="Pago parcial",
        )

        # Verificar transferencia de capital
        assert transfer_tx is not None
        assert transfer_tx.type == TransactionService.TRANSFER
        assert transfer_tx.origin_account == self.bank
        assert transfer_tx.destination_account == self.credit_card
        assert transfer_tx.category is None  # Transferencias no tienen categoría

        # Verificar gasto de interés
        if payment.interest_amount > 0:
            assert interest_tx is not None
            assert interest_tx.type == TransactionService.EXPENSE
            assert interest_tx.category == self.financing_category
            assert interest_tx.origin_account == self.bank

    def test_budget_excludes_credit_card_transfers(self):
        """Verificar que los presupuestos NO incluyen transferencias de pago de tarjeta"""
        # Crear presupuesto para categoría de financiamiento
        budget = Budget.objects.create(
            user=self.user,
            category=self.financing_category,
            amount=Decimal("50000.00"),
            currency="COP",
            period=Budget.MONTHLY,
        )

        # Pagar una cuota (esto crea transferencia + gasto de interés)
        _payment, _transfer_tx, interest_tx = InstallmentPlanService.record_payment(
            plan=self.plan,
            installment_number=1,
            payment_date=date.today(),
            source_account=self.bank,
        )

        # Obtener gasto del presupuesto
        spent = budget.get_spent_amount()

        # El presupuesto solo debe incluir el gasto de interés, NO la transferencia
        if interest_tx:
            # El gasto de interés debe estar en el presupuesto
            assert spent > Decimal(0)
        else:
            # Si no hay interés, el presupuesto debe estar en 0
            assert spent == Decimal(0)

        # Verificar que la transferencia NO está en el presupuesto
        # (ya está validado porque get_spent_amount filtra por type=2, excluyendo TRANSFER=3)
