"""
Tests para la API de Tarjetas de Crédito (credit_cards/views.py)
Fase 1: Aumentar cobertura de tests
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Account
from categories.models import Category
from credit_cards.models import InstallmentPlan
from credit_cards.services import InstallmentPlanService
from transactions.models import Transaction
from transactions.services import TransactionService

User = get_user_model()


class CreditCardsViewsTests(TestCase):
    """Tests para endpoints de tarjetas de crédito"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()

        # Crear usuario y token
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Crear cuentas
        self.bank_account = Account.objects.create(
            user=self.user,
            name="Banco Principal",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("1000000.00"),
            currency="COP",
        )

        self.credit_card = Account.objects.create(
            user=self.user,
            name="Tarjeta de Crédito",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            current_balance=Decimal("-50000.00"),
            currency="COP",
        )

        # Crear categorías
        self.purchase_category = Category.objects.create(
            user=self.user,
            name="Compras",
            type=Category.EXPENSE,
            color="#DC2626",
        )

        self.financing_category = Category.objects.create(
            user=self.user,
            name="Financiamiento",
            type=Category.EXPENSE,
            color="#EA580C",
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

    def test_list_installment_plans_success(self):
        """Test: Listar planes de cuotas exitosamente"""
        response = self.client.get("/api/credit-cards/plans/")
        assert response.status_code == status.HTTP_200_OK
        assert "status" in response.data
        assert "data" in response.data
        assert response.data["status"] == "success"
        assert "count" in response.data["data"]
        assert "results" in response.data["data"]
        assert len(response.data["data"]["results"]) == 1

    def test_create_installment_plan_success(self):
        """Test: Crear plan de cuotas exitosamente"""
        # Crear nueva transacción de compra
        new_purchase_tx = Transaction.objects.create(
            user=self.user,
            origin_account=self.credit_card,
            type=TransactionService.EXPENSE,
            base_amount=500000,  # $500.000 en centavos
            total_amount=500000,
            date=date.today(),
            category=self.purchase_category,
            description="Nueva compra",
        )

        data = {
            "credit_card_account_id": self.credit_card.id,
            "purchase_transaction_id": new_purchase_tx.id,
            "financing_category_id": self.financing_category.id,
            "number_of_installments": 6,
            "interest_rate": "1.50",
            "description": "Nuevo plan",
        }

        response = self.client.post("/api/credit-cards/plans/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"
        assert "plan_id" in response.data["data"]

    def test_create_installment_plan_invalid_data(self):
        """Test: Error al crear plan con datos inválidos"""
        data = {
            "credit_card_account_id": 99999,  # No existe
            "purchase_transaction_id": self.purchase_tx.id,
            "financing_category_id": self.financing_category.id,
            "number_of_installments": 6,
            "interest_rate": "1.50",
        }

        response = self.client.post("/api/credit-cards/plans/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_installment_plan_success(self):
        """Test: Obtener detalle de plan de cuotas"""
        response = self.client.get(f"/api/credit-cards/plans/{self.plan.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert "data" in response.data
        assert response.data["data"]["id"] == self.plan.id

    def test_retrieve_installment_plan_not_found(self):
        """Test: Obtener plan que no existe"""
        response = self.client.get("/api/credit-cards/plans/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_installment_plan_success(self):
        """Test: Actualizar plan de cuotas"""
        data = {
            "number_of_installments": 10,
            "interest_rate": "1.75",
            "description": "Plan actualizado",
        }

        response = self.client.patch(
            f"/api/credit-cards/plans/{self.plan.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        self.plan.refresh_from_db()
        assert self.plan.number_of_installments == 10

    def test_get_payment_schedule_success(self):
        """Test: Obtener cronograma de pagos"""
        response = self.client.get(f"/api/credit-cards/plans/{self.plan.id}/schedule/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert "schedule" in response.data["data"]

    def test_record_payment_success(self):
        """Test: Registrar pago de cuota"""
        data = {
            "installment_number": 1,
            "payment_date": str(date.today()),
            "source_account_id": self.bank_account.id,
            "notes": "Pago de prueba",
        }

        response = self.client.post(
            f"/api/credit-cards/plans/{self.plan.id}/payments/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"
        assert "payment" in response.data["data"]
        assert "transactions" in response.data["data"]

    def test_record_payment_invalid_installment(self):
        """Test: Error al registrar pago con número de cuota inválido"""
        data = {
            "installment_number": 999,  # No existe
            "payment_date": str(date.today()),
            "source_account_id": self.bank_account.id,
        }

        response = self.client.post(
            f"/api/credit-cards/plans/{self.plan.id}/payments/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_monthly_summary_success(self):
        """Test: Obtener resumen mensual"""
        response = self.client.get("/api/credit-cards/plans/monthly-summary/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert "data" in response.data

    def test_monthly_summary_with_filters(self):
        """Test: Obtener resumen mensual con filtros"""
        response = self.client.get("/api/credit-cards/plans/monthly-summary/?year=2024&month=12")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

    def test_upcoming_payments_success(self):
        """Test: Obtener pagos próximos"""
        response = self.client.get("/api/credit-cards/plans/upcoming-payments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert "data" in response.data
        assert isinstance(response.data["data"], list)

    def test_upcoming_payments_with_days_filter(self):
        """Test: Obtener pagos próximos con filtro de días"""
        response = self.client.get("/api/credit-cards/plans/upcoming-payments/?days=60")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

    def test_list_requires_authentication(self):
        """Test: Listar planes requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/credit-cards/plans/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_requires_authentication(self):
        """Test: Crear plan requiere autenticación"""
        self.client.credentials()
        data = {
            "credit_card_account_id": self.credit_card.id,
            "purchase_transaction_id": self.purchase_tx.id,
            "financing_category_id": self.financing_category.id,
            "number_of_installments": 6,
            "interest_rate": "1.50",
        }
        response = self.client.post("/api/credit-cards/plans/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_other_user_plan(self):
        """Test: No puede obtener plan de otro usuario"""
        other_user = User.objects.create_user(
            identification="87654321",
            username="otheruser",
            email="other@example.com",
            password="testpass123",
            is_verified=True,
        )

        other_credit_card = Account.objects.create(
            user=other_user,
            name="Otra Tarjeta",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            current_balance=Decimal("-10000.00"),
            currency="COP",
        )

        # Crear categoría de financiamiento para el otro usuario
        other_financing_category = Category.objects.create(
            user=other_user,
            name="Financiamiento Otro",
            type=Category.EXPENSE,
            color="#EA580C",
        )

        other_purchase_tx = Transaction.objects.create(
            user=other_user,
            origin_account=other_credit_card,
            type=TransactionService.EXPENSE,
            base_amount=500000,
            total_amount=500000,
            date=date.today(),
            category=self.purchase_category,
        )

        other_plan = InstallmentPlanService.create_from_transaction(
            purchase_transaction=other_purchase_tx,
            number_of_installments=6,
            interest_rate=Decimal("1.50"),
            start_date=date.today(),
            financing_category=other_financing_category,
        )

        response = self.client.get(f"/api/credit-cards/plans/{other_plan.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
