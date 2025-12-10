"""
Servicios para cálculos de analytics financieros (HU-13)
Maneja indicadores, gráficos y agregaciones por período y categoría
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q
from transactions.models import Transaction
from categories.models import Category
from typing import Dict, Tuple
import calendar

from utils.currency_converter import FxService


class FinancialAnalyticsService:
    """
    Servicio para cálculos de analytics financieros con soporte
    para modo base vs total y filtrado por períodos
    """

    @staticmethod
    def get_period_indicators(user, start_date: date, end_date: date, mode: str = "total") -> Dict:
        """
        Calcula indicadores de ingresos, gastos y balance para un período

        Args:
            user: Usuario autenticado
            start_date: Fecha inicio del período
            end_date: Fecha fin del período
            mode: 'base' o 'total' (incluye impuestos)

        Returns:
            Dict con ingresos, gastos, balance y metadata
        """
        amount_field = "base_amount" if mode == "base" else "total_amount"
        base_currency = FxService.get_base_currency(user)

        base_filter = Q(user=user, date__gte=start_date, date__lte=end_date) & ~Q(type=3)

        def _sum_by_currency(qs):
            rows = qs.values("transaction_currency", "origin_account__currency").annotate(
                total=Sum(amount_field), count=Count("id")
            )
            total_base = Decimal("0")
            total_count = 0
            for r in rows:
                curr = r["transaction_currency"] or r["origin_account__currency"] or base_currency
                amount = r["total"] or Decimal("0")
                converted, _, _ = (
                    FxService.convert_to_base(int(amount), curr, base_currency, end_date)
                    if amount is not None
                    else (0, Decimal("1"), None)
                )
                total_base += Decimal(str(converted))
                total_count += r["count"]
            return total_base, total_count

        income_total, income_count = _sum_by_currency(
            Transaction.objects.filter(base_filter & Q(type=1))
        )
        expense_total, expense_count = _sum_by_currency(
            Transaction.objects.filter(base_filter & Q(type=2))
        )
        balance = income_total - expense_total

        return {
            "income": {
                "amount": float(income_total),
                "count": income_count,
                "formatted": f"${income_total:,.0f}",
            },
            "expenses": {
                "amount": float(expense_total),
                "count": expense_count,
                "formatted": f"${expense_total:,.0f}",
            },
            "balance": {
                "amount": float(balance),
                "formatted": f"${balance:,.0f}",
                "is_positive": balance >= 0,
            },
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days + 1,
            },
            "mode": mode,
            "currency": base_currency,
        }

    @staticmethod
    def get_expenses_by_category(
        user, start_date: date, end_date: date, mode: str = "total", others_threshold: float = 0.05
    ) -> Dict:
        """
        Obtiene distribución de gastos por categoría para gráfico de dona

        Args:
            user: Usuario autenticado
            start_date: Fecha inicio del período
            end_date: Fecha fin del período
            mode: 'base' o 'total'
            others_threshold: % mínimo para categoría individual (default 5%)

        Returns:
            Dict con datos del gráfico de dona y metadata
        """
        amount_field = "base_amount" if mode == "base" else "total_amount"
        base_currency = FxService.get_base_currency(user)

        rows = (
            Transaction.objects.filter(
                user=user,
                type=2,
                date__gte=start_date,
                date__lte=end_date,
                category__isnull=False,
            )
            .values(
                "category__id",
                "category__name",
                "category__color",
                "category__icon",
                "transaction_currency",
                "origin_account__currency",
            )
            .annotate(amount=Sum(amount_field), count=Count("id"))
        )

        category_totals = {}
        for item in rows:
            cat_id = item["category__id"]
            currency = (
                item["transaction_currency"] or item["origin_account__currency"] or base_currency
            )
            amount = item["amount"] or Decimal("0")
            converted, _, _ = FxService.convert_to_base(
                int(amount), currency, base_currency, end_date
            )
            if cat_id not in category_totals:
                category_totals[cat_id] = {
                    "amount": Decimal("0"),
                    "count": 0,
                    "name": item["category__name"],
                    "color": item["category__color"],
                    "icon": item["category__icon"],
                }
            category_totals[cat_id]["amount"] += Decimal(str(converted))
            category_totals[cat_id]["count"] += item["count"]

        uncategorized_rows = (
            Transaction.objects.filter(
                user=user, type=2, date__gte=start_date, date__lte=end_date, category__isnull=True
            )
            .values("transaction_currency", "origin_account__currency")
            .annotate(amount=Sum(amount_field), count=Count("id"))
        )
        uncategorized_amount = Decimal("0")
        uncategorized_count = 0
        for item in uncategorized_rows:
            currency = (
                item["transaction_currency"] or item["origin_account__currency"] or base_currency
            )
            amount = item["amount"] or Decimal("0")
            converted, _, _ = FxService.convert_to_base(
                int(amount), currency, base_currency, end_date
            )
            uncategorized_amount += Decimal(str(converted))
            uncategorized_count += item["count"]

        total_expenses = sum([v["amount"] for v in category_totals.values()]) + uncategorized_amount

        if total_expenses == 0:
            return {
                "chart_data": [],
                "others_data": [],
                "total_expenses": 0,
                "uncategorized_amount": float(uncategorized_amount),
                "mode": mode,
                "period_summary": f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}",
                "categories_count": 0,
            }

        # Procesar categorías principales vs "Otros"
        main_categories = []
        others_categories = []
        others_total = Decimal("0")

        for cat_id, item in category_totals.items():
            percentage = float(item["amount"] / total_expenses)

            category_data = {
                "category_id": cat_id,
                "name": item["name"],
                "amount": float(item["amount"]),
                "count": item["count"],
                "percentage": percentage * 100,
                "color": item["color"],
                "icon": item["icon"],
                "formatted_amount": f"${item['amount']:,.0f}",
            }

            if percentage >= others_threshold:
                main_categories.append(category_data)
            else:
                others_categories.append(category_data)
                others_total += item["amount"]

        # Agregar "Otros" si hay categorías pequeñas
        chart_data = main_categories.copy()
        if others_categories or uncategorized_amount > 0:
            others_amount = others_total + uncategorized_amount
            others_percentage = float(others_amount / total_expenses) * 100

            chart_data.append(
                {
                    "category_id": "others",
                    "name": "Otros",
                    "amount": float(others_amount),
                    "count": len(others_categories) + (1 if uncategorized_amount > 0 else 0),
                    "percentage": others_percentage,
                    "color": "#9CA3AF",  # Color gris para "Otros"
                    "icon": "fa-ellipsis-h",
                    "formatted_amount": f"${others_amount:,.0f}",
                    "is_aggregated": True,
                }
            )

        # Agregar categoría sin asignar si existe
        if uncategorized_amount > 0:
            others_categories.append(
                {
                    "category_id": "uncategorized",
                    "name": "Sin categoría",
                    "amount": float(uncategorized_amount),
                    "count": uncategorized_count,
                    "percentage": float(uncategorized_amount / total_expenses) * 100,
                    "color": "#6B7280",
                    "icon": "fa-question-circle",
                    "formatted_amount": f"${uncategorized_amount:,.0f}",
                }
            )

        return {
            "chart_data": chart_data,
            "others_data": others_categories,
            "total_expenses": float(total_expenses),
            "uncategorized_amount": float(uncategorized_amount),
            "mode": mode,
            "period_summary": f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}",
            "categories_count": len(main_categories) + len(others_categories),
            "currency": base_currency,
        }

    @staticmethod
    def get_daily_flow_chart(user, start_date: date, end_date: date, mode: str = "total") -> Dict:
        """
        Obtiene datos para gráfico de líneas con flujo diario acumulado

        Args:
            user: Usuario autenticado
            start_date: Fecha inicio del período
            end_date: Fecha fin del período
            mode: 'base' o 'total'

        Returns:
            Dict con series de datos para gráfico de líneas
        """
        amount_field = "base_amount" if mode == "base" else "total_amount"
        base_currency = FxService.get_base_currency(user)

        # Obtener transacciones diarias agrupadas por fecha, tipo Y moneda (sin transferencias)
        daily_transactions = (
            Transaction.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
            .exclude(type=3)
            .values("date", "type", "transaction_currency", "origin_account__currency")
            .annotate(total=Sum(amount_field), count=Count("id"))
            .order_by("date")
        )

        # Crear diccionario para búsqueda rápida, agrupando por fecha y convirtiendo monedas
        transactions_by_date = {}
        for item in daily_transactions:
            transaction_date = item["date"]
            transaction_type = item["type"]
            curr = item["transaction_currency"] or item["origin_account__currency"] or base_currency
            amount = item["total"] or Decimal("0")
            
            # Convertir a moneda base
            converted, _, _ = FxService.convert_to_base(
                int(amount), curr, base_currency, transaction_date
            )
            
            # Inicializar fecha si no existe
            if transaction_date not in transactions_by_date:
                transactions_by_date[transaction_date] = {"income": 0.0, "expenses": 0.0}
            
            # Acumular por tipo (1=ingreso, 2=gasto)
            if transaction_type == 1:
                transactions_by_date[transaction_date]["income"] += float(converted)
            elif transaction_type == 2:
                transactions_by_date[transaction_date]["expenses"] += float(converted)

        # Generar series de datos día por día
        dates = []
        income_series = []
        expense_series = []
        balance_series = []

        current_date = start_date
        cumulative_balance = 0

        while current_date <= end_date:
            dates.append(current_date.strftime("%Y-%m-%d"))

            # Obtener datos del día (0 si no hay transacciones)
            day_data = transactions_by_date.get(current_date, {"income": 0, "expenses": 0})

            income_series.append(day_data["income"])
            expense_series.append(day_data["expenses"])

            # Calcular balance acumulado
            daily_balance = day_data["income"] - day_data["expenses"]
            cumulative_balance += daily_balance
            balance_series.append(cumulative_balance)

            current_date += timedelta(days=1)

        # Calcular estadísticas
        total_income = sum(income_series)
        total_expenses = sum(expense_series)
        final_balance = cumulative_balance

        return {
            "dates": dates,
            "series": {
                "income": {
                    "name": "Ingresos diarios",
                    "data": income_series,
                    "color": "#10B981",  # Verde
                    "total": total_income,
                },
                "expenses": {
                    "name": "Gastos diarios",
                    "data": expense_series,
                    "color": "#EF4444",  # Rojo
                    "total": total_expenses,
                },
                "balance": {
                    "name": "Balance acumulado",
                    "data": balance_series,
                    "color": "#3B82F6",  # Azul
                    "final": final_balance,
                },
            },
            "summary": {
                "period_days": len(dates),
                "total_income": total_income,
                "total_expenses": total_expenses,
                "final_balance": final_balance,
                "avg_daily_income": total_income / len(dates) if dates else 0,
                "avg_daily_expense": total_expenses / len(dates) if dates else 0,
            },
            "mode": mode,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "currency": base_currency,
        }

    @staticmethod
    def get_transactions_by_category(
        user,
        category_id: int,
        start_date: date,
        end_date: date,
        mode: str = "total",
        limit: int = 50,
    ) -> Dict:
        """
        Obtiene transacciones filtradas por categoría para drill-down

        Args:
            user: Usuario autenticado
            category_id: ID de categoría o 'uncategorized' para sin categoría
            start_date: Fecha inicio del período
            end_date: Fecha fin del período
            mode: 'base' o 'total'
            limit: Número máximo de transacciones

        Returns:
            Dict con lista de transacciones y metadata
        """
        amount_field = "base_amount" if mode == "base" else "total_amount"

        # Filtro por categoría
        if category_id == "uncategorized":
            category_filter = Q(category__isnull=True)
            category_name = "Sin categoría"
        else:
            category_filter = Q(category__id=category_id)
            try:
                category = Category.objects.get(id=category_id, user=user)
                category_name = category.name
            except Category.DoesNotExist:
                return {"error": "Categoría no encontrada", "transactions": [], "total_count": 0}

        # Obtener transacciones
        transactions_query = (
            Transaction.objects.filter(
                user=user,
                type=2,  # Solo gastos para drill-down de categorías
                date__gte=start_date,
                date__lte=end_date,
            )
            .filter(category_filter)
            .select_related("category", "origin_account")
            .order_by("-date", "-created_at")
        )

        total_count = transactions_query.count()
        transactions_page = transactions_query[:limit]

        # Formatear transacciones
        transactions_data = []
        for tx in transactions_page:
            amount = getattr(tx, amount_field)
            transactions_data.append(
                {
                    "id": tx.id,
                    "date": tx.date.isoformat(),
                    "description": tx.description or f"Gasto en {category_name}",
                    "amount": float(amount),
                    "formatted_amount": f"${amount:,.0f}",
                    "account": tx.origin_account.name,
                    "tag": tx.tag,
                    "category": (
                        {
                            "id": tx.category.id if tx.category else None,
                            "name": tx.category.name if tx.category else "Sin categoría",
                            "color": tx.category.color if tx.category else "#6B7280",
                            "icon": tx.category.icon if tx.category else "fa-question-circle",
                        }
                        if tx.category
                        else None
                    ),
                }
            )

        # Calcular total de la categoría en el período
        total_amount = transactions_query.aggregate(total=Sum(amount_field))["total"] or Decimal(
            "0"
        )

        return {
            "transactions": transactions_data,
            "total_count": total_count,
            "showing_count": len(transactions_data),
            "category_name": category_name,
            "total_amount": float(total_amount),
            "formatted_total": f"${total_amount:,.0f}",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "mode": mode,
            "has_more": total_count > limit,
        }

    @staticmethod
    def parse_period_param(period_str: str) -> Tuple[date, date]:
        """
        Parsea parámetro de período y devuelve fechas de inicio y fin

        Formatos soportados:
        - 'current_month' -> mes actual
        - 'last_month' -> mes anterior
        - 'current_year' -> año actual
        - 'last_7_days' -> últimos 7 días
        - 'last_30_days' -> últimos 30 días
        - 'YYYY-MM' -> mes específico (ej: '2025-10')
        - 'YYYY' -> año específico (ej: '2025')
        - 'YYYY-MM-DD,YYYY-MM-DD' -> rango personalizado

        Args:
            period_str: String de período

        Returns:
            Tuple (start_date, end_date)
        """
        today = date.today()

        if period_str == "current_month":
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)

        elif period_str == "last_month":
            if today.month == 1:
                prev_year = today.year - 1
                prev_month = 12
            else:
                prev_year = today.year
                prev_month = today.month - 1

            start_date = date(prev_year, prev_month, 1)
            last_day = calendar.monthrange(prev_year, prev_month)[1]
            end_date = date(prev_year, prev_month, last_day)

        elif period_str == "current_year":
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 12, 31)

        elif period_str == "last_7_days":
            end_date = today
            start_date = today - timedelta(days=6)

        elif period_str == "last_30_days":
            end_date = today
            start_date = today - timedelta(days=29)

        elif "," in period_str:
            # Rango personalizado: 'YYYY-MM-DD,YYYY-MM-DD'
            start_str, end_str = period_str.split(",")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d").date()

        elif len(period_str) == 7 and period_str[4] == "-":
            # Mes específico: 'YYYY-MM'
            year, month = map(int, period_str.split("-"))
            start_date = date(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, last_day)

        elif len(period_str) == 4 and period_str.isdigit():
            # Año específico: 'YYYY'
            year = int(period_str)
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)

        else:
            # Formato no reconocido, lanzar error específico
            raise ValueError(
                f"Formato de período no reconocido: '{period_str}'. Formatos válidos: current_month, last_month, current_year, last_7_days, last_30_days, YYYY-MM, YYYY, YYYY-MM-DD,YYYY-MM-DD"
            )

        return start_date, end_date

    @staticmethod
    def compare_periods(
        user,
        period1_start: date,
        period1_end: date,
        period2_start: date,
        period2_end: date,
        mode: str = "total",
    ) -> Dict:
        """
        Compara indicadores financieros entre dos períodos (HU-14)

        Args:
            user: Usuario autenticado
            period1_start: Fecha inicio período 1 (base de comparación)
            period1_end: Fecha fin período 1
            period2_start: Fecha inicio período 2 (período a comparar)
            period2_end: Fecha fin período 2
            mode: 'base' o 'total' (incluye impuestos)

        Returns:
            Dict con comparación detallada entre períodos
        """
        base_currency = FxService.get_base_currency(user)
        
        # Obtener indicadores de ambos períodos
        period1_data = FinancialAnalyticsService.get_period_indicators(
            user, period1_start, period1_end, mode
        )

        period2_data = FinancialAnalyticsService.get_period_indicators(
            user, period2_start, period2_end, mode
        )

        # Función auxiliar para calcular diferencias
        def calculate_difference(period1_val, period2_val):
            absolute_diff = period2_val - period1_val

            if period1_val == 0:
                if period2_val == 0:
                    percentage_diff = 0
                else:
                    percentage_diff = 100 if period2_val > 0 else -100
            else:
                percentage_diff = (absolute_diff / abs(period1_val)) * 100

            return {
                "absolute": absolute_diff,
                "percentage": percentage_diff,
                "is_increase": absolute_diff > 0,
                "is_significant": abs(percentage_diff) >= 5,  # Cambio >= 5%
            }

        # Extraer valores numéricos
        period1_income = period1_data["income"]["amount"]
        period1_expenses = period1_data["expenses"]["amount"]
        period1_balance = period1_data["balance"]["amount"]

        period2_income = period2_data["income"]["amount"]
        period2_expenses = period2_data["expenses"]["amount"]
        period2_balance = period2_data["balance"]["amount"]

        # Calcular diferencias
        income_diff = calculate_difference(period1_income, period2_income)
        expenses_diff = calculate_difference(period1_expenses, period2_expenses)
        balance_diff = calculate_difference(period1_balance, period2_balance)

        # Verificar disponibilidad de datos
        period1_has_data = (
            period1_data["income"]["count"] > 0 or period1_data["expenses"]["count"] > 0
        )
        period2_has_data = (
            period2_data["income"]["count"] > 0 or period2_data["expenses"]["count"] > 0
        )

        return {
            "comparison_summary": {
                "period1": {
                    "name": f"{period1_start.strftime('%B %Y')}",
                    "date_range": f"{period1_start.strftime('%d/%m/%Y')} - {period1_end.strftime('%d/%m/%Y')}",
                    "has_data": period1_has_data,
                    "transactions_count": period1_data["income"]["count"]
                    + period1_data["expenses"]["count"],
                },
                "period2": {
                    "name": f"{period2_start.strftime('%B %Y')}",
                    "date_range": f"{period2_start.strftime('%d/%m/%Y')} - {period2_end.strftime('%d/%m/%Y')}",
                    "has_data": period2_has_data,
                    "transactions_count": period2_data["income"]["count"]
                    + period2_data["expenses"]["count"],
                },
                "can_compare": period1_has_data and period2_has_data,
                "mode": mode,
            },
            "period_data": {"period1": period1_data, "period2": period2_data},
            "differences": {
                "income": {
                    **income_diff,
                    "period1_amount": period1_income,
                    "period2_amount": period2_income,
                    "formatted_absolute": FinancialAnalyticsService.format_currency(
                        abs(income_diff["absolute"])
                    ),
                    "summary": FinancialAnalyticsService._format_comparison_summary(
                        "Ingresos", income_diff, mode
                    ),
                },
                "expenses": {
                    **expenses_diff,
                    "period1_amount": period1_expenses,
                    "period2_amount": period2_expenses,
                    "formatted_absolute": FinancialAnalyticsService.format_currency(
                        abs(expenses_diff["absolute"])
                    ),
                    "summary": FinancialAnalyticsService._format_comparison_summary(
                        "Gastos", expenses_diff, mode
                    ),
                },
                "balance": {
                    **balance_diff,
                    "period1_amount": period1_balance,
                    "period2_amount": period2_balance,
                    "formatted_absolute": FinancialAnalyticsService.format_currency(
                        abs(balance_diff["absolute"])
                    ),
                    "summary": FinancialAnalyticsService._format_comparison_summary(
                        "Balance", balance_diff, mode
                    ),
                },
            },
            "insights": FinancialAnalyticsService._generate_comparison_insights(
                income_diff, expenses_diff, balance_diff, period1_has_data, period2_has_data
            ),
            "metadata": {
                "generated_at": date.today().isoformat(),
                "comparison_mode": mode,
                "currency": base_currency,
            },
        }

    @staticmethod
    def _format_comparison_summary(metric_name: str, diff_data: Dict, mode: str) -> str:
        """
        Formatea resumen textual de comparación

        Args:
            metric_name: Nombre del métrico (Ingresos, Gastos, Balance)
            diff_data: Datos de diferencia calculados
            mode: Modo de cálculo usado

        Returns:
            String con resumen formateado (ej: "Gastos -12% ($-85.000)")
        """
        sign = "+" if diff_data["is_increase"] else ""
        percentage = diff_data["percentage"]
        formatted_amount = FinancialAnalyticsService.format_currency(abs(diff_data["absolute"]))
        amount_sign = "+" if diff_data["is_increase"] else "-"

        if diff_data["absolute"] == 0:
            return f"{metric_name} sin cambios (0%)"

        return f"{metric_name} {sign}{percentage:.1f}% ({amount_sign}{formatted_amount})"

    @staticmethod
    def _generate_comparison_insights(
        income_diff: Dict,
        expenses_diff: Dict,
        balance_diff: Dict,
        period1_has_data: bool,
        period2_has_data: bool,
    ) -> Dict:
        """
        Genera insights automáticos de la comparación

        Returns:
            Dict con insights y recomendaciones
        """
        insights = []
        alert_level = "info"  # info, warning, success, error

        if not period1_has_data:
            insights.append("No hay información del primer período para comparar.")
            alert_level = "warning"
        elif not period2_has_data:
            insights.append("No hay información del segundo período para comparar.")
            alert_level = "warning"
        else:
            # Análisis de ingresos
            if income_diff["is_significant"]:
                if income_diff["is_increase"]:
                    insights.append(
                        f"Excelente: Los ingresos aumentaron {income_diff['percentage']:.1f}%."
                    )
                    alert_level = "success"
                else:
                    insights.append(
                        f"Atención: Los ingresos disminuyeron {abs(income_diff['percentage']):.1f}%."
                    )
                    if alert_level == "info":
                        alert_level = "warning"

            # Análisis de gastos
            if expenses_diff["is_significant"]:
                if expenses_diff["is_increase"]:
                    insights.append(
                        f"Cuidado: Los gastos aumentaron {expenses_diff['percentage']:.1f}%."
                    )
                    if alert_level in ["info", "success"]:
                        alert_level = "warning"
                else:
                    insights.append(
                        f"Bien: Los gastos disminuyeron {abs(expenses_diff['percentage']):.1f}%."
                    )
                    if alert_level == "info":
                        alert_level = "success"

            # Análisis de balance general
            if balance_diff["is_increase"]:
                if balance_diff["percentage"] >= 20:
                    insights.append("Situación financiera muy mejorada.")
                    alert_level = "success"
                elif balance_diff["percentage"] >= 5:
                    insights.append("Situación financiera mejorada.")
                    if alert_level == "info":
                        alert_level = "success"
            else:
                if abs(balance_diff["percentage"]) >= 20:
                    insights.append("La situación financiera ha empeorado significativamente.")
                    alert_level = "error"
                elif abs(balance_diff["percentage"]) >= 5:
                    insights.append("La situación financiera ha empeorado.")
                    if alert_level in ["info", "success"]:
                        alert_level = "warning"

            if not insights:
                insights.append("Los cambios entre períodos son mínimos (< 5%).")

        return {
            "messages": insights,
            "alert_level": alert_level,
            "has_significant_changes": (
                any(
                    [
                        income_diff.get("is_significant", False),
                        expenses_diff.get("is_significant", False),
                        balance_diff.get("is_significant", False),
                    ]
                )
                if period1_has_data and period2_has_data
                else False
            ),
        }

    @staticmethod
    def format_currency(amount: int, currency: str = "COP") -> str:
        """
        Formatea monto en centavos a string con formato de moneda

        Args:
            amount: Monto en centavos
            currency: Código de moneda (COP, USD, etc.)

        Returns:
            String formateado (ej: "$1.250.000")
        """
        if currency == "COP":
            # Convertir centavos a pesos y formatear
            pesos = amount / 100
            return f"${pesos:,.0f}".replace(",", ".")
        else:
            # Para otras monedas, usar formato estándar
            decimal_amount = amount / 100
            return f"${decimal_amount:,.2f}"
