"""
Serializers para reglas automáticas (HU-12)
"""

from rest_framework import serializers
from .models import AutomaticRule
from categories.models import Category


class AutomaticRuleListSerializer(serializers.ModelSerializer):
    """Serializer para listar reglas automáticas"""

    criteria_type_display = serializers.CharField(
        source="get_criteria_type_display", read_only=True
    )
    action_type_display = serializers.CharField(source="get_action_type_display", read_only=True)
    target_transaction_type_display = serializers.CharField(
        source="get_target_transaction_type_display", read_only=True
    )
    target_category_name = serializers.CharField(source="target_category.name", read_only=True)
    target_category_color = serializers.CharField(source="target_category.color", read_only=True)
    target_category_icon = serializers.CharField(source="target_category.icon", read_only=True)
    applied_count = serializers.SerializerMethodField()

    class Meta:
        model = AutomaticRule
        fields = [
            "id",
            "name",
            "criteria_type",
            "criteria_type_display",
            "keyword",
            "target_transaction_type",
            "target_transaction_type_display",
            "action_type",
            "action_type_display",
            "target_category",
            "target_category_name",
            "target_category_color",
            "target_category_icon",
            "target_tag",
            "is_active",
            "order",
            "applied_count",
            "created_at",
            "updated_at",
        ]

    def get_applied_count(self, obj):
        """Número de transacciones a las que se ha aplicado esta regla"""
        return obj.applied_transactions.count()


class AutomaticRuleDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalles de una regla automática"""

    criteria_type_display = serializers.CharField(
        source="get_criteria_type_display", read_only=True
    )
    action_type_display = serializers.CharField(source="get_action_type_display", read_only=True)
    target_transaction_type_display = serializers.CharField(
        source="get_target_transaction_type_display", read_only=True
    )

    # Información completa de la categoría objetivo
    target_category_info = serializers.SerializerMethodField()

    # Estadísticas de aplicación
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = AutomaticRule
        fields = [
            "id",
            "name",
            "criteria_type",
            "criteria_type_display",
            "keyword",
            "target_transaction_type",
            "target_transaction_type_display",
            "action_type",
            "action_type_display",
            "target_category",
            "target_category_info",
            "target_tag",
            "is_active",
            "order",
            "statistics",
            "created_at",
            "updated_at",
        ]

    def get_target_category_info(self, obj):
        """Información completa de la categoría objetivo"""
        if obj.target_category:
            return {
                "id": obj.target_category.id,
                "name": obj.target_category.name,
                "type": obj.target_category.type,
                "type_display": obj.target_category.get_type_display(),
                "color": obj.target_category.color,
                "icon": obj.target_category.icon,
            }
        return None

    def get_statistics(self, obj):
        """Estadísticas de aplicación de la regla"""
        applied_transactions = obj.applied_transactions.all()
        total_count = applied_transactions.count()

        if total_count == 0:
            return {"total_applied": 0, "last_applied": None, "avg_amount": None}

        # Calcular promedio de montos
        amounts = [t.total_amount for t in applied_transactions]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0

        return {
            "total_applied": total_count,
            "last_applied": applied_transactions.order_by("-created_at").first().created_at,
            "avg_amount": round(avg_amount, 2),
        }


class AutomaticRuleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reglas automáticas"""

    class Meta:
        model = AutomaticRule
        fields = [
            "name",
            "criteria_type",
            "keyword",
            "target_transaction_type",
            "action_type",
            "target_category",
            "target_tag",
            "is_active",
            "order",
        ]

    def validate(self, data):
        """Validaciones adicionales"""
        # Validar nombre duplicado
        if hasattr(self.context, "request"):
            request = self.context["request"]
            name = data.get("name")
            if name and AutomaticRule.objects.filter(user=request.user, name=name).exists():
                raise serializers.ValidationError({"name": "Ya tienes una regla con este nombre."})

        # Validar campos requeridos según criterio
        if data["criteria_type"] == AutomaticRule.DESCRIPTION_CONTAINS:
            if not data.get("keyword"):
                raise serializers.ValidationError(
                    {
                        "keyword": 'La palabra clave es requerida para criterio "descripción contiene texto"'
                    }
                )

        elif data["criteria_type"] == AutomaticRule.TRANSACTION_TYPE:
            if data.get("target_transaction_type") is None:
                raise serializers.ValidationError(
                    {
                        "target_transaction_type": 'El tipo de transacción es requerido para criterio "tipo de transacción"'
                    }
                )

        # Validar campos requeridos según acción
        if data["action_type"] == AutomaticRule.ASSIGN_CATEGORY:
            if not data.get("target_category"):
                raise serializers.ValidationError(
                    {
                        "target_category": 'La categoría objetivo es requerida para acción "asignar categoría"'
                    }
                )

        elif data["action_type"] == AutomaticRule.ASSIGN_TAG:
            if not data.get("target_tag"):
                raise serializers.ValidationError(
                    {
                        "target_tag": 'La etiqueta objetivo es requerida para acción "asignar etiqueta"'
                    }
                )

        return data

    def validate_target_category(self, value):
        """Validar que la categoría pertenezca al usuario"""
        if value and hasattr(self.context, "request"):
            request = self.context["request"]
            if value.user != request.user:
                # Obtener categorías disponibles del usuario para el mensaje de error
                user_categories = Category.objects.filter(user=request.user)
                available_ids = list(user_categories.values_list("id", flat=True))

                raise serializers.ValidationError(
                    f"La categoría con ID {value.id} no te pertenece. "
                    f"IDs de categorías disponibles: {available_ids}. "
                    f"Usa GET /api/categories/ para ver tus categorías."
                )
        return value

    def create(self, validated_data):
        """Crear regla asignando el usuario automáticamente"""
        request = self.context["request"]
        validated_data["user"] = request.user
        return super().create(validated_data)


class AutomaticRuleUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar reglas automáticas"""

    class Meta:
        model = AutomaticRule
        fields = [
            "name",
            "criteria_type",
            "keyword",
            "target_transaction_type",
            "action_type",
            "target_category",
            "target_tag",
            "is_active",
            "order",
        ]

    def validate(self, data):
        """Validaciones adicionales"""
        # Usar datos existentes si no se proporcionan nuevos
        instance = self.instance
        criteria_type = data.get("criteria_type", instance.criteria_type)
        action_type = data.get("action_type", instance.action_type)

        # Validar campos requeridos según criterio
        if criteria_type == AutomaticRule.DESCRIPTION_CONTAINS:
            keyword = data.get("keyword", instance.keyword)
            if not keyword:
                raise serializers.ValidationError(
                    {
                        "keyword": 'La palabra clave es requerida para criterio "descripción contiene texto"'
                    }
                )

        elif criteria_type == AutomaticRule.TRANSACTION_TYPE:
            target_transaction_type = data.get(
                "target_transaction_type", instance.target_transaction_type
            )
            if target_transaction_type is None:
                raise serializers.ValidationError(
                    {
                        "target_transaction_type": 'El tipo de transacción es requerido para criterio "tipo de transacción"'
                    }
                )

        # Validar campos requeridos según acción
        if action_type == AutomaticRule.ASSIGN_CATEGORY:
            target_category = data.get("target_category", instance.target_category)
            if not target_category:
                raise serializers.ValidationError(
                    {
                        "target_category": 'La categoría objetivo es requerida para acción "asignar categoría"'
                    }
                )

        elif action_type == AutomaticRule.ASSIGN_TAG:
            target_tag = data.get("target_tag", instance.target_tag)
            if not target_tag:
                raise serializers.ValidationError(
                    {
                        "target_tag": 'La etiqueta objetivo es requerida para acción "asignar etiqueta"'
                    }
                )

        return data

    def validate_target_category(self, value):
        """Validar que la categoría pertenezca al usuario"""
        if value and hasattr(self.context, "request"):
            request = self.context["request"]
            if value.user != request.user:
                # Obtener categorías disponibles del usuario para el mensaje de error
                user_categories = Category.objects.filter(user=request.user)
                available_ids = list(user_categories.values_list("id", flat=True))

                raise serializers.ValidationError(
                    f"La categoría con ID {value.id} no te pertenece. "
                    f"IDs de categorías disponibles: {available_ids}. "
                    f"Usa GET /api/categories/ para ver tus categorías."
                )
        return value


class AutomaticRuleStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de reglas automáticas"""

    total_rules = serializers.IntegerField()
    active_rules = serializers.IntegerField()
    inactive_rules = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    most_used_rule = serializers.DictField()
    recent_applications = serializers.ListField()
