"""
Serializers para configuración de monedas y tipos de cambio
"""
from rest_framework import serializers
from utils.models import BaseCurrencySetting, ExchangeRate
from utils.currency_converter import FxService
from datetime import date


class BaseCurrencySerializer(serializers.ModelSerializer):
    """Serializer para configuración de moneda base del usuario"""
    
    class Meta:
        model = BaseCurrencySetting
        fields = ["base_currency", "updated_at"]
        read_only_fields = ["updated_at"]

    def validate_base_currency(self, value):
        """Valida que la moneda esté soportada"""
        try:
            FxService.ensure_supported(value.upper())
            return value.upper()
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return BaseCurrencySetting.objects.update_or_create(
            user=user,
            defaults=validated_data
        )[0]


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer para tipos de cambio mensuales"""
    
    class Meta:
        model = ExchangeRate
        fields = [
            "id",
            "base_currency",
            "currency",
            "year",
            "month",
            "rate",
            "source",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_base_currency(self, value):
        """Valida que la moneda base esté soportada"""
        FxService.ensure_supported(value.upper())
        return value.upper()

    def validate_currency(self, value):
        """Valida que la moneda esté soportada"""
        FxService.ensure_supported(value.upper())
        return value.upper()

    def validate_month(self, value):
        """Valida que el mes sea válido (1-12)"""
        if not 1 <= value <= 12:
            raise serializers.ValidationError("El mes debe estar entre 1 y 12")
        return value

    def validate_year(self, value):
        """Valida que el año sea razonable"""
        current_year = date.today().year
        if not 2000 <= value <= current_year + 10:
            raise serializers.ValidationError(
                f"El año debe estar entre 2000 y {current_year + 10}"
            )
        return value

    def validate_rate(self, value):
        """Valida que la tasa sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La tasa de cambio debe ser mayor a cero")
        return value

    def validate(self, data):
        """Validación cruzada de campos"""
        if data.get("base_currency") == data.get("currency"):
            raise serializers.ValidationError(
                "La moneda base y la moneda de destino no pueden ser iguales"
            )
        return data
