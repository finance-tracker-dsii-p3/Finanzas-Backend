"""
URLs para Analytics Financieros (HU-13)
"""

from django.urls import path

from . import views

urlpatterns = [
    # Dashboard principal de analytics
    path("dashboard/", views.analytics_dashboard, name="analytics_dashboard"),
    # Componentes individuales
    path("indicators/", views.period_indicators, name="period_indicators"),
    path("expenses-chart/", views.expenses_by_category, name="expenses_by_category"),
    path("daily-flow-chart/", views.daily_flow_chart, name="daily_flow_chart"),
    # Drill-down de categorías
    path(
        "category/<str:category_id>/transactions/",
        views.category_transactions,
        name="category_transactions",
    ),
    # Utilidades
    path("periods/", views.available_periods, name="available_periods"),
    # HU-14: Comparación entre períodos
    path("compare-periods/", views.compare_periods, name="compare_periods"),
]

# URLs disponibles para HU-13:
# GET /api/analytics/dashboard/ - Dashboard completo con indicadores, gráficos
# GET /api/analytics/indicators/ - Solo KPIs (ingresos, gastos, balance)
# GET /api/analytics/expenses-chart/ - Solo gráfico de dona por categorías
# GET /api/analytics/daily-flow-chart/ - Solo gráfico de líneas de flujo diario
# GET /api/analytics/category/{id}/transactions/ - Transacciones de una categoría
# GET /api/analytics/periods/ - Períodos disponibles
#
# Query parameters comunes:
# ?period=current_month - Período (current_month, last_month, 2025-10, etc.)
# ?mode=total - Modo de cálculo (base o total)
# ?others_threshold=0.05 - % mínimo para categorías individuales en dona
# ?limit=50 - Límite de transacciones en drill-down
#
# Ejemplos de uso:
# GET /api/analytics/dashboard/?period=current_month&mode=base
# GET /api/analytics/expenses-chart/?period=2025-10&mode=total
# GET /api/analytics/category/5/transactions/?period=last_month&limit=20
# GET /api/analytics/category/uncategorized/transactions/?period=current_year
#
# HU-14: Comparación entre períodos
# GET /api/analytics/compare-periods/ - Compara dos períodos
# Query parameters:
# ?period1=2025-09&period2=2025-10&mode=total - Compara septiembre vs octubre
# ?period1=last_month&period2=current_month&mode=base - Mes anterior vs actual
#
# Ejemplos de comparación:
# GET /api/analytics/compare-periods/?period1=2025-09&period2=2025-10&mode=total
# GET /api/analytics/compare-periods/?period1=last_month&period2=current_month&mode=base
