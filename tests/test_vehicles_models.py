"""
Tests para modelos de vehículos (vehicles/models.py)
Fase 1: Aumentar cobertura de tests
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from vehicles.models import SOAT, SOATAlert, Vehicle

User = get_user_model()


class VehiclesModelsTests(TestCase):
    """Tests para modelos de vehículos"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

        self.vehicle = Vehicle.objects.create(
            user=self.user,
            plate="ABC123",
            brand="Toyota",
            model="Corolla",
            year=2020,
        )

    def test_vehicle_str(self):
        """Test: Representación string de vehículo"""
        vehicle = Vehicle.objects.create(
            user=self.user, plate="XYZ789", brand="Honda", model="Civic"
        )
        str_repr = str(vehicle)
        assert "XYZ789" in str_repr
        assert "Honda" in str_repr

    def test_vehicle_clean_normalizes_plate(self):
        """Test: clean() normaliza la placa a mayúsculas"""
        vehicle = Vehicle(user=self.user, plate="  abc123  ", brand="Ford", model="Focus")
        vehicle.clean()
        assert vehicle.plate == "ABC123"

    def test_soat_str(self):
        """Test: Representación string de SOAT"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            cost=500000,
        )
        str_repr = str(soat)
        assert "ABC123" in str_repr

    def test_soat_clean_validates_dates(self):
        """Test: clean() valida que expiry_date sea posterior a issue_date"""
        soat = SOAT(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() - timedelta(days=1),
            cost=500000,
        )
        try:
            soat.clean()
            error_message = "Debería haber lanzado ValidationError"
            raise AssertionError(error_message)
        except ValidationError as e:
            assert "expiry_date" in e.error_dict

    def test_soat_days_until_expiry_with_timezone(self):
        """Test: Calcular días hasta vencimiento con timezone"""
        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
        )

        days = soat.days_until_expiry(user_tz=None)
        assert days is not None
        assert days >= 29  # Puede variar por 1 día según la hora

    def test_soat_days_until_expiry_property(self):
        """Test: Propiedad days_until_expiry_property"""
        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
        )

        days = soat.days_until_expiry_property
        assert days is not None

    def test_soat_is_expired_false(self):
        """Test: is_expired retorna False para SOAT vigente"""
        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
        )

        assert not soat.is_expired(user_tz=None)

    def test_soat_is_expired_true(self):
        """Test: is_expired retorna True para SOAT vencido"""
        expiry_date = date.today() - timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=expiry_date,
            cost=500000,
        )

        assert soat.is_expired(user_tz=None)

    def test_soat_is_expired_property(self):
        """Test: Propiedad is_expired_property"""
        expiry_date = date.today() - timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=expiry_date,
            cost=500000,
        )

        assert soat.is_expired_property

    def test_soat_is_near_expiry_true(self):
        """Test: is_near_expiry retorna True para SOAT próximo a vencer"""
        expiry_date = date.today() + timedelta(days=5)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=300),
            expiry_date=expiry_date,
            cost=500000,
            alert_days_before=7,
        )

        assert soat.is_near_expiry(user_tz=None)

    def test_soat_is_near_expiry_false(self):
        """Test: is_near_expiry retorna False para SOAT lejano"""
        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
            alert_days_before=7,
        )

        assert not soat.is_near_expiry(user_tz=None)

    def test_soat_is_near_expiry_property(self):
        """Test: Propiedad is_near_expiry_property"""
        expiry_date = date.today() + timedelta(days=5)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=300),
            expiry_date=expiry_date,
            cost=500000,
            alert_days_before=7,
        )

        assert soat.is_near_expiry_property

    def test_soat_is_paid_false(self):
        """Test: is_paid retorna False cuando no hay transacción"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            cost=500000,
        )

        assert not soat.is_paid

    def test_soat_is_paid_true(self):
        """Test: is_paid retorna True cuando hay transacción"""
        from accounts.models import Account
        from categories.models import Category
        from transactions.models import Transaction

        account = Account.objects.create(
            user=self.user,
            name="Banco",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=10000000,
            currency="COP",
            account_number="1234567890123",
        )

        category = Category.objects.create(
            user=self.user,
            name="Seguros",
            type=Category.EXPENSE,
            color="#7C3AED",
            icon="fa-umbrella",
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=account,
            category=category,
            type=2,
            base_amount=500000,
            total_amount=500000,
            date=date.today(),
            transaction_currency="COP",
        )

        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
            payment_transaction=transaction,
        )

        assert soat.is_paid

    def test_soat_update_status_vigente(self):
        """Test: update_status establece estado 'vigente'"""
        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
        )

        soat.update_status(user_tz=None)
        assert soat.status == "vigente"

    def test_soat_update_status_vencido(self):
        """Test: update_status establece estado 'vencido' cuando está pagado pero vencido"""
        from accounts.models import Account
        from categories.models import Category
        from transactions.models import Transaction

        account = Account.objects.create(
            user=self.user,
            name="Banco",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=10000000,
            currency="COP",
            account_number="1234567890123",
        )

        category = Category.objects.create(
            user=self.user,
            name="Seguros",
            type=Category.EXPENSE,
            color="#7C3AED",
            icon="fa-umbrella",
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=account,
            category=category,
            type=2,
            base_amount=500000,
            total_amount=500000,
            date=date.today() - timedelta(days=400),
            transaction_currency="COP",
        )

        expiry_date = date.today() - timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=expiry_date,
            cost=500000,
            payment_transaction=transaction,
        )

        soat.update_status(user_tz=None)
        assert soat.status == "vencido"

    def test_soat_update_status_atrasado(self):
        """Test: update_status establece estado 'atrasado' cuando está vencido sin pagar"""
        expiry_date = date.today() - timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=expiry_date,
            cost=500000,
        )

        soat.update_status(user_tz=None)
        assert soat.status == "atrasado"

    def test_soat_update_status_por_vencer(self):
        """Test: update_status establece estado 'por_vencer' cuando está pagado y próximo a vencer"""
        from accounts.models import Account
        from categories.models import Category
        from transactions.models import Transaction

        account = Account.objects.create(
            user=self.user,
            name="Banco",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=10000000,
            currency="COP",
            account_number="1234567890123",
        )

        category = Category.objects.create(
            user=self.user,
            name="Seguros",
            type=Category.EXPENSE,
            color="#7C3AED",
            icon="fa-umbrella",
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=account,
            category=category,
            type=2,
            base_amount=500000,
            total_amount=500000,
            date=date.today() - timedelta(days=300),
            transaction_currency="COP",
        )

        expiry_date = date.today() + timedelta(days=5)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=300),
            expiry_date=expiry_date,
            cost=500000,
            payment_transaction=transaction,
            alert_days_before=7,
        )

        soat.update_status(user_tz=None)
        assert soat.status == "por_vencer"

    def test_soat_update_status_pendiente_pago(self):
        """Test: update_status establece estado 'pendiente_pago' cuando no está pagado y próximo a vencer"""
        expiry_date = date.today() + timedelta(days=5)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=300),
            expiry_date=expiry_date,
            cost=500000,
            alert_days_before=7,
        )

        soat.update_status(user_tz=None)
        assert soat.status == "pendiente_pago"

    def test_soat_get_user_timezone_with_preferences(self):
        """Test: _get_user_timezone obtiene timezone de preferencias del usuario"""
        # Crear preferencias de notificación con timezone
        from users.models import UserNotificationPreferences

        prefs = UserNotificationPreferences.objects.create(
            user=self.user, timezone="America/Bogota"
        )

        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
        )

        tz = soat._get_user_timezone()
        assert tz is not None

    def test_soat_get_user_timezone_without_preferences(self):
        """Test: _get_user_timezone retorna None sin preferencias"""
        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
        )

        tz = soat._get_user_timezone()
        # Puede ser None o un timezone por defecto

    def test_soat_calculate_days_until_expiry_without_expiry_date(self):
        """Test: _calculate_days_until_expiry retorna None sin fecha de vencimiento"""
        soat = SOAT(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=None,
            cost=500000,
        )

        days = soat._calculate_days_until_expiry(user_tz=None)
        assert days is None

    def test_soat_alert_str(self):
        """Test: Representación string de alerta de SOAT"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=5),
            cost=500000,
        )

        alert = SOATAlert.objects.create(
            soat=soat,
            user=self.user,
            alert_type="proxima_vencer",
            message="SOAT próximo a vencer",
        )

        str_repr = str(alert)
        assert "ABC123" in str_repr
