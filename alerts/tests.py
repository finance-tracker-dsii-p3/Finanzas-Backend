from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Account
from alerts.models import Alert
from budgets.models import Budget
from categories.models import Category
from transactions.models import Transaction


User = get_user_model()


class BudgetAlertsTests(TestCase):
    """Tests de integración básica para HU-08 (alertas de presupuesto)."""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="ALERT-USER-001",
            username="alertuser",
            email="alert@example.com",
            password="testpass123",
            role="user",
            is_verified=True,
        )

        # Cuenta simple de gastos
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta pruebas alertas",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("1000000.00"),
        )

        # Categoría de gasto
        self.category = Category.objects.create(
            user=self.user,
            name="Comida",
            type="expense",
            color="#DC2626",
            icon="fa-utensils",
        )

        # Presupuesto mensual de 400.000 con umbral 80%
        # Importante: debe tener la misma moneda que la cuenta (COP por defecto)
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("400000.00"),
            currency='COP',  # Misma moneda que la cuenta
            calculation_mode=Budget.BASE,
            period=Budget.MONTHLY,
            start_date=date(2025, 11, 1),
            is_active=True,
            alert_threshold=Decimal("80.00"),
        )

    def _create_expense(self, base_amount, tx_date):
        """Helper para crear una transacción de gasto en la categoría del presupuesto."""
        return Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,  # Expense
            base_amount=int(base_amount),  # enteros (centavos)
            date=tx_date,
            category=self.category,
        )

    def test_warning_alert_created_at_80_percent(self):
        """
        Debe crearse una alerta 'warning' cuando el gasto acumulado
        alcanza al menos el 80 % del presupuesto en el mes.
        """
        # 80 % de 400.000 = 320.000
        self._create_expense(base_amount=32000000, tx_date=date(2025, 11, 10))

        alerts = Alert.objects.filter(user=self.user, budget=self.budget)
        self.assertEqual(alerts.count(), 1)
        alert = alerts.first()
        self.assertEqual(alert.alert_type, "warning")
        self.assertFalse(alert.is_read)

    def test_exceeded_alert_created_at_100_percent(self):
        """
        Debe crearse una alerta 'exceeded' cuando el gasto acumulado
        alcanza o supera el 100 % del presupuesto en el mes.
        """
        # Primero un gasto que deje el presupuesto en 50%
        self._create_expense(base_amount=20000000, tx_date=date(2025, 11, 5))
        # Luego otro que lleve el total a 100%
        self._create_expense(base_amount=20000000, tx_date=date(2025, 11, 15))

        alerts = Alert.objects.filter(user=self.user, budget=self.budget, alert_type="exceeded")
        self.assertEqual(alerts.count(), 1)

    def test_only_one_alert_per_month_and_type(self):
        """
        No debe generar más de una alerta por presupuesto / tipo / mes,
        incluso si se registran más gastos en el mismo mes.
        """
        # Primera transacción que dispara alerta warning
        self._create_expense(base_amount=32000000, tx_date=date(2025, 11, 10))
        # Más gastos en el mismo mes que mantendrían el estado en warning
        self._create_expense(base_amount=1000000, tx_date=date(2025, 11, 12))
        self._create_expense(base_amount=500000, tx_date=date(2025, 11, 20))

        warnings_count = Alert.objects.filter(
            user=self.user,
            budget=self.budget,
            alert_type="warning",
            transaction_year=2025,
            transaction_month=11,
        ).count()
        self.assertEqual(warnings_count, 1)

    def test_new_month_generates_new_alert(self):
        """
        En un nuevo mes, se puede generar una nueva alerta para el mismo presupuesto y tipo.
        """
        # Noviembre: genera primera alerta
        self._create_expense(base_amount=32000000, tx_date=date(2025, 11, 10))
        # Diciembre: nuevo mes, vuelve a disparar alerta
        self._create_expense(base_amount=32000000, tx_date=date(2025, 12, 10))

        warnings_nov = Alert.objects.filter(
            user=self.user,
            budget=self.budget,
            alert_type="warning",
            transaction_year=2025,
            transaction_month=11,
        ).count()

        warnings_dec = Alert.objects.filter(
            user=self.user,
            budget=self.budget,
            alert_type="warning",
            transaction_year=2025,
            transaction_month=12,
        ).count()

        self.assertEqual(warnings_nov, 1)
        self.assertEqual(warnings_dec, 1)