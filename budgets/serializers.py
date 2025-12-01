"""
Serializers para la gestión de presupuestos
"""

from rest_framework import serializers
from .models import Budget
from categories.models import Category


class BudgetListSerializer(serializers.ModelSerializer):
    """Serializer para listar presupuestos con información de stats"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    category_type = serializers.CharField(source="category.type", read_only=True)
    category_type_display = serializers.CharField(
        source="category.get_type_display", read_only=True
    )
    category_color = serializers.CharField(source="category.color", read_only=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True)

    calculation_mode_display = serializers.CharField(
        source="get_calculation_mode_display", read_only=True
    )
    period_display = serializers.CharField(source="get_period_display", read_only=True)

    # Campos calculados
    spent_amount = serializers.SerializerMethodField()
    spent_percentage = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "category_name",
            "category_type",
            "category_type_display",
            "category_color",
            "category_icon",
            "amount",
            "currency",
            "calculation_mode",
            "calculation_mode_display",
            "period",
            "period_display",
            "start_date",
            "is_active",
            "alert_threshold",
            "spent_amount",
            "spent_percentage",
            "remaining_amount",
            "status",
            "status_text",
            "created_at",
            "updated_at",
        ]

    def get_spent_amount(self, obj):
        return str(obj.get_spent_amount())

    def get_spent_percentage(self, obj):
        return str(obj.get_spent_percentage())

    def get_remaining_amount(self, obj):
        return str(obj.get_remaining_amount())

    def get_status(self, obj):
        return obj.get_status()

    def get_status_text(self, obj):
        return obj.get_status_display_text()


class BudgetDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalle completo de un presupuesto con proyecciones"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    category_type = serializers.CharField(source="category.type", read_only=True)
    category_type_display = serializers.CharField(
        source="category.get_type_display", read_only=True
    )
    category_color = serializers.CharField(source="category.color", read_only=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True)

    calculation_mode_display = serializers.CharField(
        source="get_calculation_mode_display", read_only=True
    )
    period_display = serializers.CharField(source="get_period_display", read_only=True)

    # Campos calculados
    spent_amount = serializers.SerializerMethodField()
    spent_percentage = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    daily_average = serializers.SerializerMethodField()
    projection = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    is_over_budget = serializers.SerializerMethodField()
    is_alert_triggered = serializers.SerializerMethodField()
    period_dates = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "category_name",
            "category_type",
            "category_type_display",
            "category_color",
            "category_icon",
            "amount",
            "currency",
            "calculation_mode",
            "calculation_mode_display",
            "period",
            "period_display",
            "start_date",
            "is_active",
            "alert_threshold",
            "spent_amount",
            "spent_percentage",
            "remaining_amount",
            "daily_average",
            "projection",
            "status",
            "status_text",
            "is_over_budget",
            "is_alert_triggered",
            "period_dates",
            "created_at",
            "updated_at",
        ]

    def get_spent_amount(self, obj):
        return str(obj.get_spent_amount())

    def get_spent_percentage(self, obj):
        return str(obj.get_spent_percentage())

    def get_remaining_amount(self, obj):
        return str(obj.get_remaining_amount())

    def get_daily_average(self, obj):
        return str(obj.get_daily_average())

    def get_projection(self, obj):
        projection = obj.get_projection()
        return {
            "projected_amount": str(projection["projected_amount"]),
            "projected_percentage": str(projection["projected_percentage"]),
            "will_exceed": projection["will_exceed"],
            "days_remaining": projection["days_remaining"],
            "days_total": projection["days_total"],
            "daily_average": str(projection["daily_average"]),
        }

    def get_status(self, obj):
        return obj.get_status()

    def get_status_text(self, obj):
        return obj.get_status_display_text()

    def get_is_over_budget(self, obj):
        return obj.is_over_budget()

    def get_is_alert_triggered(self, obj):
        return obj.is_alert_triggered()

    def get_period_dates(self, obj):
        start, end = obj.get_period_dates()
        return {"start": start.isoformat(), "end": end.isoformat()}


class BudgetCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos presupuestos"""

    class Meta:
        model = Budget
        fields = [
            "category",
            "amount",
            "currency",
            "calculation_mode",
            "period",
            "start_date",
            "is_active",
            "alert_threshold",
        ]
        extra_kwargs = {
            "start_date": {"required": False},
            "is_active": {"required": False},
            "alert_threshold": {"required": False},
            "calculation_mode": {"required": False},
            "period": {"required": False},
            "currency": {"required": False},
        }

    def validate_category(self, value):
        """Validar que la categoría pertenezca al usuario"""
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("La categoría no pertenece al usuario autenticado.")
        return value

    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value

    def validate_alert_threshold(self, value):
        """Validar que el umbral esté entre 0 y 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("El umbral de alerta debe estar entre 0 y 100.")
        return value

    def validate(self, attrs):
        """Validaciones adicionales"""
        user = self.context["request"].user
        category = attrs.get("category")
        period = attrs.get("period", Budget.MONTHLY)

        # Obtener moneda (por defecto COP si no se especifica)
        currency = attrs.get("currency", "COP")

        # Verificar si ya existe un presupuesto para esta categoría, período y moneda
        if Budget.objects.filter(
            user=user, category=category, period=period, currency=currency
        ).exists():
            raise serializers.ValidationError(
                {
                    "category": f"Ya existe un presupuesto {Budget(period=period).get_period_display().lower()} en {Budget(currency=currency).get_currency_display()} para esta categoría."
                }
            )

        # Validar que la categoría sea de tipo gasto
        if category.type != Category.EXPENSE:
            raise serializers.ValidationError(
                {"category": "Solo se pueden crear presupuestos para categorías de gasto."}
            )

        return attrs

    def create(self, validated_data):
        """Crear presupuesto asignando el usuario actual"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class BudgetUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar presupuestos existentes"""

    class Meta:
        model = Budget
        fields = ["amount", "currency", "calculation_mode", "is_active", "alert_threshold"]
        extra_kwargs = {
            "amount": {"required": False},
            "calculation_mode": {"required": False},
            "is_active": {"required": False},
            "alert_threshold": {"required": False},
        }

    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value

    def validate_alert_threshold(self, value):
        """Validar que el umbral esté entre 0 y 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("El umbral de alerta debe estar entre 0 y 100.")
        return value


class BudgetStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas generales de presupuestos"""

    total_budgets = serializers.IntegerField()
    active_budgets = serializers.IntegerField()
    exceeded_budgets = serializers.IntegerField()
    warning_budgets = serializers.IntegerField()
    good_budgets = serializers.IntegerField()
    total_allocated = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_remaining = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_usage_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    monthly_budgets_count = serializers.IntegerField()
    yearly_budgets_count = serializers.IntegerField()


class BudgetSummarySerializer(serializers.Serializer):
    """Serializer para resumen mensual de presupuestos"""

    budget_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    category_color = serializers.CharField()
    category_icon = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    spent_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    spent_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField()
    projection = serializers.DictField()
