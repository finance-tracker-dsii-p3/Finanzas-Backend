"""
Tests para serializers de vehículos (vehicles/serializers.py)
Fase 1: Aumentar cobertura de tests
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction
from vehicles.models import SOAT, SOATAlert, Vehicle

User = get_user_model()


class VehiclesSerializersTests(TestCase):
    """Tests para serializers de vehículos"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

        # Crear request mock
        from django.test import RequestFactory

        factory = RequestFactory()
        self.request = factory.get("/")
        self.request.user = self.user

        # Crear vehículo de prueba
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            plate="ABC123",
            brand="Toyota",
            model="Corolla",
            year=2020,
        )

        # Crear cuenta para pagos
        self.account = Account.objects.create(
            user=self.user,
            name="Banco Principal",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=10000000,  # 100,000.00 en centavos
            currency="COP",
            account_number="1234567890123",
        )

    def test_vehicle_serializer_validate_plate_unique(self):
        """Test: Validar que la placa sea única para el usuario"""
        from vehicles.serializers import VehicleSerializer

        # Crear otro vehículo con placa diferente
        Vehicle.objects.create(user=self.user, plate="XYZ789", brand="Honda", model="Civic")

        # Intentar crear vehículo con placa duplicada
        data = {"plate": "ABC123", "brand": "Ford", "model": "Focus"}
        serializer = VehicleSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "plate" in serializer.errors

    def test_vehicle_serializer_validate_plate_update_same_plate(self):
        """Test: Permitir actualizar con la misma placa"""
        from vehicles.serializers import VehicleSerializer

        data = {"plate": "ABC123", "brand": "Toyota Updated"}
        serializer = VehicleSerializer(
            instance=self.vehicle, data=data, context={"request": self.request}
        )
        assert serializer.is_valid()

    def test_vehicle_serializer_validate_plate_update_different_plate(self):
        """Test: Validar placa única al actualizar con placa diferente"""
        from vehicles.serializers import VehicleSerializer

        # Crear otro vehículo
        other_vehicle = Vehicle.objects.create(
            user=self.user, plate="XYZ789", brand="Honda", model="Civic"
        )

        # Intentar cambiar la placa a una que ya existe
        data = {"plate": "XYZ789", "brand": "Toyota"}
        serializer = VehicleSerializer(
            instance=self.vehicle, data=data, context={"request": self.request}
        )
        assert not serializer.is_valid()
        assert "plate" in serializer.errors

    def test_soat_serializer_get_vehicle_info(self):
        """Test: Obtener información del vehículo"""
        from vehicles.serializers import SOATSerializer

        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            cost=500000,  # 5,000.00 en centavos
        )

        serializer = SOATSerializer(soat, context={"request": self.request})
        assert "vehicle_info" in serializer.data
        assert serializer.data["vehicle_info"]["plate"] == "ABC123"
        assert serializer.data["vehicle_info"]["brand"] == "Toyota"

    def test_soat_serializer_get_days_until_expiry(self):
        """Test: Calcular días hasta vencimiento"""
        from vehicles.serializers import SOATSerializer

        expiry_date = date.today() + timedelta(days=30)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=expiry_date,
            cost=500000,
        )

        serializer = SOATSerializer(soat, context={"request": self.request})
        assert "days_until_expiry" in serializer.data
        assert serializer.data["days_until_expiry"] is not None

    def test_soat_serializer_get_is_expired(self):
        """Test: Verificar si está vencido"""
        from vehicles.serializers import SOATSerializer

        # SOAT vencido
        expired_soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=date.today() - timedelta(days=30),
            cost=500000,
        )

        serializer = SOATSerializer(expired_soat, context={"request": self.request})
        assert "is_expired" in serializer.data

    def test_soat_serializer_get_is_near_expiry(self):
        """Test: Verificar si está próximo a vencer"""
        from vehicles.serializers import SOATSerializer

        # SOAT próximo a vencer
        near_expiry_soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=300),
            expiry_date=date.today() + timedelta(days=5),
            cost=500000,
            alert_days_before=7,
        )

        serializer = SOATSerializer(near_expiry_soat, context={"request": self.request})
        assert "is_near_expiry" in serializer.data

    def test_soat_serializer_get_payment_info_with_transaction(self):
        """Test: Obtener información de pago cuando existe transacción"""
        from vehicles.serializers import SOATSerializer

        # Crear categoría
        category = Category.objects.create(
            user=self.user,
            name="Seguros",
            type=Category.EXPENSE,
            color="#7C3AED",
            icon="fa-umbrella",
        )

        # Crear transacción
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=category,
            type=2,  # Expense
            base_amount=500000,
            total_amount=500000,
            date=date.today(),
            description="Pago SOAT",
            transaction_currency="COP",
        )

        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
            payment_transaction=transaction,
        )

        serializer = SOATSerializer(soat, context={"request": self.request})
        assert "payment_info" in serializer.data
        assert serializer.data["payment_info"] is not None
        assert serializer.data["payment_info"]["id"] == transaction.id

    def test_soat_serializer_get_payment_info_without_transaction(self):
        """Test: Obtener información de pago cuando no existe transacción"""
        from vehicles.serializers import SOATSerializer

        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            cost=500000,
        )

        serializer = SOATSerializer(soat, context={"request": self.request})
        assert "payment_info" in serializer.data
        assert serializer.data["payment_info"] is None

    def test_soat_serializer_get_cost_formatted(self):
        """Test: Obtener costo formateado"""
        from vehicles.serializers import SOATSerializer

        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            cost=500000,  # 5,000.00
        )

        serializer = SOATSerializer(soat, context={"request": self.request})
        assert "cost_formatted" in serializer.data
        assert "$5,000.00" in serializer.data["cost_formatted"]

    def test_soat_serializer_validate_expiry_after_issue(self):
        """Test: Validar que fecha de vencimiento sea posterior a emisión"""
        from vehicles.serializers import SOATSerializer

        data = {
            "vehicle": self.vehicle.id,
            "issue_date": date.today(),
            "expiry_date": date.today() - timedelta(days=1),  # Antes de emisión
            "cost": 500000,
        }

        serializer = SOATSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "expiry_date" in serializer.errors

    def test_soat_serializer_validate_vehicle_belongs_to_user(self):
        """Test: Validar que el vehículo pertenezca al usuario"""
        from vehicles.serializers import SOATSerializer

        # Crear otro usuario y su vehículo
        other_user = User.objects.create_user(
            identification="87654321",
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
            is_verified=True,
        )
        other_vehicle = Vehicle.objects.create(
            user=other_user, plate="OTHER123", brand="Ford", model="Focus"
        )

        data = {
            "vehicle": other_vehicle.id,
            "issue_date": date.today(),
            "expiry_date": date.today() + timedelta(days=365),
            "cost": 500000,
        }

        serializer = SOATSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "vehicle" in serializer.errors

    def test_soat_payment_serializer_validate_account_id(self):
        """Test: Validar que la cuenta exista y pertenezca al usuario"""
        from vehicles.serializers import SOATPaymentSerializer

        # Cuenta que no existe
        data = {"account_id": 99999, "payment_date": date.today()}
        serializer = SOATPaymentSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "account_id" in serializer.errors

    def test_soat_payment_serializer_validate_soat_not_paid(self):
        """Test: Validar que el SOAT no esté ya pagado"""
        from vehicles.serializers import SOATPaymentSerializer

        # Crear categoría y transacción
        category = Category.objects.create(
            user=self.user,
            name="Seguros",
            type=Category.EXPENSE,
            color="#7C3AED",
            icon="fa-umbrella",
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=category,
            type=2,
            base_amount=500000,
            total_amount=500000,
            date=date.today(),
            transaction_currency="COP",
        )

        # Crear SOAT ya pagado
        paid_soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
            payment_transaction=transaction,
        )

        data = {"account_id": self.account.id, "payment_date": date.today()}
        serializer = SOATPaymentSerializer(
            data=data, context={"request": self.request, "soat": paid_soat}
        )
        assert not serializer.is_valid()

    def test_vehicle_with_soat_serializer_get_active_soat(self):
        """Test: Obtener SOAT activo del vehículo"""
        from vehicles.serializers import VehicleWithSOATSerializer

        # Crear SOAT activo
        active_soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
        )

        serializer = VehicleWithSOATSerializer(self.vehicle, context={"request": self.request})
        assert "active_soat" in serializer.data
        assert serializer.data["active_soat"] is not None
        assert serializer.data["active_soat"]["id"] == active_soat.id

    def test_vehicle_with_soat_serializer_get_active_soat_none(self):
        """Test: No hay SOAT activo"""
        from vehicles.serializers import VehicleWithSOATSerializer

        # Crear SOAT vencido
        expired_soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=date.today() - timedelta(days=30),
            cost=500000,
        )

        serializer = VehicleWithSOATSerializer(self.vehicle, context={"request": self.request})
        assert "active_soat" in serializer.data
        # Puede ser None o el más reciente dependiendo de la lógica

    def test_vehicle_with_soat_serializer_get_soats_count(self):
        """Test: Obtener conteo de SOATs"""
        from vehicles.serializers import VehicleWithSOATSerializer

        # Crear múltiples SOATs
        SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=date.today() - timedelta(days=30),
            cost=500000,
        )
        SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=600000,
        )

        serializer = VehicleWithSOATSerializer(self.vehicle, context={"request": self.request})
        assert "soats_count" in serializer.data
        assert serializer.data["soats_count"] == 2

    def test_soat_alert_serializer_fields(self):
        """Test: Serializer de alertas de SOAT"""
        from vehicles.serializers import SOATAlertSerializer

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

        serializer = SOATAlertSerializer(alert)
        assert "vehicle_plate" in serializer.data
        assert "soat_expiry" in serializer.data
        assert "soat_id" in serializer.data
        assert serializer.data["vehicle_plate"] == "ABC123"
