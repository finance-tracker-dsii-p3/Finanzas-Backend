from rest_framework import serializers
from goals.models import Goal


class GoalDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalle completo de una transacción"""

    class Meta:
        model = Goal
        fields = [
            "id",
            "user",
            "name",
            "target_amount",
            "saved_amount",
            "date",
            "description",
        ]
        read_only_fields = [
            "id",
            "user",
            "name",
            "target_amount",
            "saved_amount",
            "date",
            "description",
        ]

class GoalSerializer(serializers.ModelSerializer):
    """Serializer para la creación de transacciones"""

    class Meta:
        model = Goal
        fields = [
            "id",
            "user",
            "name",
            "target_amount",
            "saved_amount",
            "date",
            "description",
        ]
        read_only_fields = ["id", "user"]

    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError(
                "El monto debe ser un valor positivo mayor que cero."
            )
        return value

    def validate(self, data):
        """Validar lógica específica para transferencias"""
        user = self.context["request"].user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                "El usuario debe estar autenticado para crear una transacción."
            )
        return data

    def create(self, validated_data):
        """Crear transacción asignando el usuario del request"""
        user = self.context["request"].user
        validated_data["user"] = user
        return Goal.objects.create(**validated_data)


class GoalUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar metas de ahorro existentes"""

    class Meta:
        model = Goal
        fields = [
            "name",
            "target_amount",
            "saved_amount",
            "date",
            "description",
        ]

    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError(
                "El monto debe ser un valor positivo mayor que cero."
            )
        return value