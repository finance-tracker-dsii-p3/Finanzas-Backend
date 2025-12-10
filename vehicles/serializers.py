"""
Serializers para vehículos y SOAT
"""

from rest_framework import serializers
from vehicles.models import Vehicle, SOAT, SOATAlert
from accounts.models import Account
from django.utils import timezone


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer para vehículos"""

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "plate",
            "brand",
            "model",
            "year",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_plate(self, value):
        """Validar que la placa sea única para el usuario"""
        user = self.context["request"].user
        plate = value.upper().strip()

        # Si estamos actualizando, excluir el vehículo actual
        if self.instance:
            if Vehicle.objects.filter(user=user, plate=plate).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya tienes un vehículo registrado con esta placa")
        else:
            if Vehicle.objects.filter(user=user, plate=plate).exists():
                raise serializers.ValidationError("Ya tienes un vehículo registrado con esta placa")

        return plate


class SOATSerializer(serializers.ModelSerializer):
    """Serializer para SOAT"""

    vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True)
    vehicle_info = serializers.SerializerMethodField()
    days_until_expiry = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_near_expiry = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    payment_info = serializers.SerializerMethodField()
    cost_formatted = serializers.SerializerMethodField()

    class Meta:
        model = SOAT
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "vehicle_info",
            "issue_date",
            "expiry_date",
            "alert_days_before",
            "cost",
            "cost_formatted",
            "status",
            "payment_transaction",
            "payment_info",
            "insurance_company",
            "policy_number",
            "notes",
            "days_until_expiry",
            "is_expired",
            "is_near_expiry",
            "is_paid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "payment_transaction", "created_at", "updated_at"]

    def get_vehicle_info(self, obj):
        """Información completa del vehículo"""
        return {
            "id": obj.vehicle.id,
            "plate": obj.vehicle.plate,
            "brand": obj.vehicle.brand,
            "model": obj.vehicle.model,
            "year": obj.vehicle.year,
        }

    def get_payment_info(self, obj):
        """Información del pago si existe"""
        if not obj.payment_transaction:
            return None

        txn = obj.payment_transaction
        return {
            "id": txn.id,
            "date": txn.date,
            "amount": txn.total_amount,
            "account": txn.origin_account.name,
            "category": txn.category.name if txn.category else None,
        }

    def get_cost_formatted(self, obj):
        """Costo formateado en unidades monetarias"""
        return f"${obj.cost / 100:,.2f}"

    def validate(self, data):
        """Validaciones de fechas"""
        issue_date = data.get("issue_date")
        expiry_date = data.get("expiry_date")

        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                raise serializers.ValidationError(
                    {
                        "expiry_date": "La fecha de vencimiento debe ser posterior a la fecha de emisión"
                    }
                )

        # Validar que el vehículo pertenezca al usuario
        vehicle = data.get("vehicle")
        if vehicle:
            user = self.context["request"].user
            if vehicle.user != user:
                raise serializers.ValidationError(
                    {"vehicle": "El vehículo no pertenece a este usuario"}
                )

        return data


class SOATPaymentSerializer(serializers.Serializer):
    """Serializer para registrar el pago de un SOAT"""

    account_id = serializers.IntegerField(
        required=True, help_text="ID de la cuenta desde la que se paga"
    )
    payment_date = serializers.DateField(required=True, help_text="Fecha del pago")
    notes = serializers.CharField(
        required=False, allow_blank=True, help_text="Notas adicionales del pago"
    )

    def validate_account_id(self, value):
        """Validar que la cuenta exista y pertenezca al usuario"""
        user = self.context["request"].user
        try:
            Account.objects.get(id=value, user=user)
        except Account.DoesNotExist:
            raise serializers.ValidationError("La cuenta no existe o no te pertenece")
        return value

    def validate(self, data):
        """Validar que el SOAT no esté ya pagado"""
        soat = self.context.get("soat")
        if soat and soat.is_paid:
            raise serializers.ValidationError("Este SOAT ya ha sido pagado")
        return data


class SOATAlertSerializer(serializers.ModelSerializer):
    """Serializer para alertas de SOAT"""

    vehicle_plate = serializers.CharField(source="soat.vehicle.plate", read_only=True)
    soat_expiry = serializers.DateField(source="soat.expiry_date", read_only=True)
    soat_id = serializers.IntegerField(source="soat.id", read_only=True)

    class Meta:
        model = SOATAlert
        fields = [
            "id",
            "soat",
            "soat_id",
            "vehicle_plate",
            "soat_expiry",
            "alert_type",
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "soat", "user", "alert_type", "message", "created_at"]


class VehicleWithSOATSerializer(serializers.ModelSerializer):
    """Serializer de vehículo con su SOAT activo"""

    active_soat = serializers.SerializerMethodField()
    soats_count = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "plate",
            "brand",
            "model",
            "year",
            "is_active",
            "active_soat",
            "soats_count",
            "created_at",
        ]

    def get_active_soat(self, obj):
        """SOAT más reciente del vehículo"""
        soat = (
            obj.soats.filter(expiry_date__gte=timezone.now().date())
            .order_by("-expiry_date")
            .first()
        )

        if soat:
            return {
                "id": soat.id,
                "expiry_date": soat.expiry_date,
                "status": soat.status,
                "days_until_expiry": soat.days_until_expiry,
                "is_paid": soat.is_paid,
            }
        return None

    def get_soats_count(self, obj):
        """Total de SOATs registrados para este vehículo"""
        return obj.soats.count()
