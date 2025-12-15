from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas básicas del dashboard - adaptado para proyecto financiero
    """

    # Estadísticas de usuarios
    total_users = serializers.IntegerField(required=False)
    active_users = serializers.IntegerField(required=False)
    pending_verifications = serializers.IntegerField(required=False)

    # Estadísticas de notificaciones
    unread_notifications = serializers.IntegerField(required=False)
    recent_notifications = serializers.IntegerField(required=False)
    total_notifications = serializers.IntegerField(required=False)

    # Estadísticas de perfil
    profile_complete = serializers.BooleanField(required=False)


class MiniCardSerializer(serializers.Serializer):
    """
    Serializer para las mini cards del dashboard
    """

    title = serializers.CharField()
    value = serializers.CharField()
    icon = serializers.CharField()
    color = serializers.CharField()
    trend = serializers.CharField(required=False)
    trend_value = serializers.CharField(required=False)


class ActivitySerializer(serializers.Serializer):
    """
    Serializer para actividades recientes
    """

    id = serializers.IntegerField()
    type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    description = serializers.CharField()
    read = serializers.BooleanField(required=False)


class AlertSerializer(serializers.Serializer):
    """
    Serializer para alertas
    """

    type = serializers.CharField()
    severity = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    timestamp = serializers.DateTimeField()


class DashboardDataSerializer(serializers.Serializer):
    """
    Serializer completo del dashboard - simplificado para proyecto financiero
    """

    user_info = serializers.DictField()
    stats = DashboardStatsSerializer()
    mini_cards = MiniCardSerializer(many=True)
    recent_activities = ActivitySerializer(many=True)
    alerts = AlertSerializer(many=True)
    charts_data = serializers.DictField()


# ========== Serializers para Dashboard Financiero ==========


class FinancialSummarySerializer(serializers.Serializer):
    """Serializer para resumen financiero principal"""

    total_income = serializers.FloatField(help_text="Total de ingresos en centavos")
    total_expenses = serializers.FloatField(help_text="Total de gastos en centavos")
    total_savings = serializers.FloatField(help_text="Total de ahorros en centavos")
    total_iva = serializers.FloatField(help_text="Total de IVA pagado en centavos")
    total_gmf = serializers.FloatField(help_text="Total de GMF (4x1000) pagado en centavos")
    net_balance = serializers.FloatField(help_text="Balance neto (ingresos - gastos) en centavos")
    currency = serializers.CharField(help_text="Moneda base del usuario")


class FilterSerializer(serializers.Serializer):
    """Serializer para filtros aplicados"""

    year = serializers.IntegerField(allow_null=True, help_text="Año filtrado")
    month = serializers.IntegerField(allow_null=True, help_text="Mes filtrado (1-12)")
    account_id = serializers.IntegerField(allow_null=True, help_text="ID de cuenta filtrada")
    period_label = serializers.CharField(help_text="Etiqueta legible del período")


class RecentTransactionSerializer(serializers.Serializer):
    """Serializer para movimientos recientes"""

    id = serializers.IntegerField(help_text="ID de la transacción")
    type = serializers.CharField(help_text="Tipo de transacción (Income, Expense, etc.)")
    type_code = serializers.IntegerField(help_text="Código del tipo (1=Income, 2=Expense, etc.)")
    date = serializers.DateField(help_text="Fecha de la transacción")
    description = serializers.CharField(help_text="Descripción de la transacción")
    amount = serializers.IntegerField(help_text="Monto en centavos")
    amount_formatted = serializers.CharField(help_text="Monto formateado")
    currency = serializers.CharField(help_text="Moneda de la transacción")
    account = serializers.CharField(help_text="Nombre de la cuenta origen")
    category = serializers.CharField(allow_null=True, help_text="Nombre de la categoría")
    category_color = serializers.CharField(allow_null=True, help_text="Color de la categoría (hex)")
    category_icon = serializers.CharField(allow_null=True, help_text="Icono de la categoría")


class UpcomingBillSerializer(serializers.Serializer):
    """Serializer para facturas próximas a vencer"""

    id = serializers.IntegerField(help_text="ID de la factura")
    provider = serializers.CharField(help_text="Nombre del proveedor")
    amount = serializers.IntegerField(help_text="Monto en centavos")
    amount_formatted = serializers.CharField(help_text="Monto formateado")
    due_date = serializers.DateField(help_text="Fecha de vencimiento")
    days_until_due = serializers.IntegerField(
        help_text="Días hasta vencimiento (negativo si está vencida)"
    )
    status = serializers.CharField(help_text="Estado de la factura (pending, paid, overdue)")
    urgency = serializers.CharField(
        help_text="Nivel de urgencia (overdue, today, urgent, soon, normal)"
    )
    urgency_label = serializers.CharField(help_text="Etiqueta de urgencia (Vencida, Hoy, etc.)")
    urgency_color = serializers.CharField(help_text="Color para la urgencia (hex)")
    suggested_account = serializers.CharField(
        allow_null=True, help_text="Nombre de la cuenta sugerida para pagar"
    )
    suggested_account_id = serializers.IntegerField(
        allow_null=True, help_text="ID de la cuenta sugerida"
    )
    category = serializers.CharField(allow_null=True, help_text="Nombre de la categoría")
    category_color = serializers.CharField(allow_null=True, help_text="Color de la categoría (hex)")
    category_icon = serializers.CharField(allow_null=True, help_text="Icono de la categoría")
    description = serializers.CharField(help_text="Descripción adicional")
    is_recurring = serializers.BooleanField(help_text="Indica si es una factura recurrente")


class CategoryDistributionSerializer(serializers.Serializer):
    """Serializer para distribución por categoría"""

    id = serializers.IntegerField(help_text="ID de la categoría")
    name = serializers.CharField(help_text="Nombre de la categoría")
    amount = serializers.FloatField(help_text="Monto total en centavos")
    count = serializers.IntegerField(help_text="Cantidad de transacciones")
    percentage = serializers.FloatField(help_text="Porcentaje del total")
    color = serializers.CharField(help_text="Color de la categoría")
    icon = serializers.CharField(help_text="Icono de la categoría")
    formatted = serializers.CharField(help_text="Monto formateado")


class ExpenseDistributionSerializer(serializers.Serializer):
    """Serializer para gráfico de distribución de gastos"""

    categories = CategoryDistributionSerializer(many=True)
    total = serializers.FloatField(help_text="Total de gastos en centavos")
    total_formatted = serializers.CharField(required=False, help_text="Total formateado")
    has_data = serializers.BooleanField(help_text="Indica si hay datos disponibles")


class DailyFlowSerializer(serializers.Serializer):
    """Serializer para gráfico de flujo diario"""

    dates = serializers.ListField(child=serializers.DateField(), help_text="Fechas del período")
    income = serializers.ListField(
        child=serializers.FloatField(), help_text="Ingresos por fecha en centavos"
    )
    expenses = serializers.ListField(
        child=serializers.FloatField(), help_text="Gastos por fecha en centavos"
    )
    total_income = serializers.FloatField(help_text="Total de ingresos del período")
    total_expenses = serializers.FloatField(help_text="Total de gastos del período")
    has_data = serializers.BooleanField(help_text="Indica si hay datos disponibles")


class ChartsSerializer(serializers.Serializer):
    """Serializer para datos de gráficos"""

    expense_distribution = ExpenseDistributionSerializer()
    daily_flow = DailyFlowSerializer()


class AccountsInfoSerializer(serializers.Serializer):
    """Serializer para información de cuentas"""

    total_accounts = serializers.IntegerField(help_text="Total de cuentas del usuario")
    has_accounts = serializers.BooleanField(help_text="Indica si el usuario tiene cuentas")


class EmptyStateSerializer(serializers.Serializer):
    """Serializer para estado vacío"""

    message = serializers.CharField(help_text="Mensaje principal")
    suggestion = serializers.CharField(help_text="Sugerencia de acción")
    action = serializers.CharField(help_text="Código de acción sugerida")


class FinancialDashboardSerializer(serializers.Serializer):
    """Serializer completo para dashboard financiero"""

    has_data = serializers.BooleanField(help_text="Indica si hay datos de transacciones")
    summary = FinancialSummarySerializer()
    filters = FilterSerializer()
    recent_transactions = RecentTransactionSerializer(many=True)
    upcoming_bills = UpcomingBillSerializer(many=True)
    charts = ChartsSerializer()
    accounts_info = AccountsInfoSerializer()
    empty_state = EmptyStateSerializer(required=False)
    error = serializers.CharField(required=False, help_text="Mensaje de error si aplica")
