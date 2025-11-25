"""
Serializers para API de Analytics Financieros (HU-13)
"""
from rest_framework import serializers


class PeriodIndicatorsSerializer(serializers.Serializer):
    """Serializer para indicadores del período (ingresos, gastos, balance)"""
    
    income = serializers.DictField()
    expenses = serializers.DictField()
    balance = serializers.DictField()
    period = serializers.DictField()
    mode = serializers.CharField()
    currency = serializers.CharField()
    context = serializers.DictField(required=False)


class CategoryExpenseSerializer(serializers.Serializer):
    """Serializer para datos de categorías en gráfico de dona"""
    
    category_id = serializers.CharField()
    name = serializers.CharField()
    amount = serializers.FloatField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()
    color = serializers.CharField()
    icon = serializers.CharField()
    formatted_amount = serializers.CharField()
    is_aggregated = serializers.BooleanField(required=False, default=False)


class ExpensesCategoryChartSerializer(serializers.Serializer):
    """Serializer para gráfico de dona de gastos por categoría"""
    
    chart_data = CategoryExpenseSerializer(many=True)
    others_data = CategoryExpenseSerializer(many=True)
    total_expenses = serializers.FloatField()
    uncategorized_amount = serializers.FloatField()
    mode = serializers.CharField()
    period_summary = serializers.CharField()
    categories_count = serializers.IntegerField()
    context = serializers.DictField(required=False)


class ChartSeriesSerializer(serializers.Serializer):
    """Serializer para series de datos de gráficos"""
    
    name = serializers.CharField()
    data = serializers.ListField(child=serializers.FloatField())
    color = serializers.CharField()
    total = serializers.FloatField(required=False)
    final = serializers.FloatField(required=False)


class DailyFlowChartSerializer(serializers.Serializer):
    """Serializer para gráfico de flujo diario"""
    
    dates = serializers.ListField(child=serializers.CharField())
    series = serializers.DictField()
    summary = serializers.DictField()
    mode = serializers.CharField()
    period = serializers.DictField()


class TransactionDetailSerializer(serializers.Serializer):
    """Serializer para detalles de transacciones en drill-down"""
    
    id = serializers.IntegerField()
    date = serializers.CharField()
    description = serializers.CharField()
    amount = serializers.FloatField()
    formatted_amount = serializers.CharField()
    account = serializers.CharField()
    tag = serializers.CharField(allow_null=True)
    category = serializers.DictField(allow_null=True)


class CategoryTransactionsSerializer(serializers.Serializer):
    """Serializer para transacciones filtradas por categoría"""
    
    transactions = TransactionDetailSerializer(many=True)
    total_count = serializers.IntegerField()
    showing_count = serializers.IntegerField()
    category_name = serializers.CharField()
    total_amount = serializers.FloatField()
    formatted_total = serializers.CharField()
    period = serializers.DictField()
    mode = serializers.CharField()
    has_more = serializers.BooleanField()


class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer completo para dashboard de analytics"""
    
    indicators = PeriodIndicatorsSerializer()
    expenses_chart = ExpensesCategoryChartSerializer()
    daily_flow_chart = DailyFlowChartSerializer()
    metadata = serializers.DictField()


class AnalyticsErrorSerializer(serializers.Serializer):
    """Serializer para errores de analytics"""
    
    error = serializers.CharField()
    code = serializers.CharField()
    details = serializers.DictField(required=False)
    suggestions = serializers.ListField(child=serializers.CharField(), required=False)


class PeriodComparisonSummarySerializer(serializers.Serializer):
    """Serializer para resumen de períodos en comparación"""
    
    name = serializers.CharField()
    date_range = serializers.CharField()
    has_data = serializers.BooleanField()
    transactions_count = serializers.IntegerField()


class ComparisonSummarySerializer(serializers.Serializer):
    """Serializer para resumen general de comparación"""
    
    period1 = PeriodComparisonSummarySerializer()
    period2 = PeriodComparisonSummarySerializer()
    can_compare = serializers.BooleanField()
    mode = serializers.CharField()


class MetricDifferenceSerializer(serializers.Serializer):
    """Serializer para diferencias de un métrico específico"""
    
    absolute = serializers.FloatField()
    percentage = serializers.FloatField()
    is_increase = serializers.BooleanField()
    is_significant = serializers.BooleanField()
    period1_amount = serializers.FloatField()
    period2_amount = serializers.FloatField()
    formatted_absolute = serializers.CharField()
    summary = serializers.CharField()


class ComparisonDifferencesSerializer(serializers.Serializer):
    """Serializer para todas las diferencias entre períodos"""
    
    income = MetricDifferenceSerializer()
    expenses = MetricDifferenceSerializer()
    balance = MetricDifferenceSerializer()


class ComparisonInsightsSerializer(serializers.Serializer):
    """Serializer para insights automáticos de comparación"""
    
    messages = serializers.ListField(child=serializers.CharField())
    alert_level = serializers.CharField()
    has_significant_changes = serializers.BooleanField()


class PeriodDataSerializer(serializers.Serializer):
    """Serializer para datos completos de ambos períodos"""
    
    period1 = PeriodIndicatorsSerializer()
    period2 = PeriodIndicatorsSerializer()


class PeriodComparisonSerializer(serializers.Serializer):
    """Serializer completo para comparación entre períodos (HU-14)"""
    
    comparison_summary = ComparisonSummarySerializer()
    period_data = PeriodDataSerializer()
    differences = ComparisonDifferencesSerializer()
    insights = ComparisonInsightsSerializer()
    metadata = serializers.DictField()