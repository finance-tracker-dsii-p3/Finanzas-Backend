"""
Servicios para cálculos de analytics financieros (HU-13)
Maneja indicadores, gráficos y agregaciones por período y categoría
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDate
from transactions.models import Transaction
from categories.models import Category
from typing import Dict, List, Optional, Tuple
import calendar


class FinancialAnalyticsService:
    """
    Servicio para cálculos de analytics financieros con soporte
    para modo base vs total y filtrado por períodos
    """
    
    @staticmethod
    def get_period_indicators(
        user,
        start_date: date,
        end_date: date,
        mode: str = 'total'
    ) -> Dict:
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
        # Definir campo de monto según modo
        amount_field = 'base_amount' if mode == 'base' else 'total_amount'
        
        # Filtro base por usuario y período, excluyendo transferencias
        base_filter = Q(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ) & ~Q(type=3)  # Excluir transferencias (type=3)
        
        # Calcular ingresos (type=1)
        income_data = Transaction.objects.filter(
            base_filter & Q(type=1)
        ).aggregate(
            total=Sum(amount_field),
            count=Count('id')
        )
        
        # Calcular gastos (type=2)
        expense_data = Transaction.objects.filter(
            base_filter & Q(type=2)
        ).aggregate(
            total=Sum(amount_field),
            count=Count('id')
        )
        
        # Valores seguros
        income_total = income_data['total'] or Decimal('0')
        expense_total = expense_data['total'] or Decimal('0')
        balance = income_total - expense_total
        
        return {
            'income': {
                'amount': float(income_total),
                'count': income_data['count'],
                'formatted': f"${income_total:,.0f}"
            },
            'expenses': {
                'amount': float(expense_total),
                'count': expense_data['count'],
                'formatted': f"${expense_total:,.0f}"
            },
            'balance': {
                'amount': float(balance),
                'formatted': f"${balance:,.0f}",
                'is_positive': balance >= 0
            },
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': (end_date - start_date).days + 1
            },
            'mode': mode,
            'currency': 'COP'
        }
    
    @staticmethod
    def get_expenses_by_category(
        user,
        start_date: date,
        end_date: date,
        mode: str = 'total',
        others_threshold: float = 0.05
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
        amount_field = 'base_amount' if mode == 'base' else 'total_amount'
        
        # Obtener gastos por categoría
        expenses_by_category = Transaction.objects.filter(
            user=user,
            type=2,  # Solo gastos
            date__gte=start_date,
            date__lte=end_date,
            category__isnull=False  # Solo transacciones con categoría
        ).values(
            'category__id',
            'category__name',
            'category__color',
            'category__icon'
        ).annotate(
            amount=Sum(amount_field),
            count=Count('id')
        ).order_by('-amount')
        
        # Gastos sin categoría
        uncategorized_amount = Transaction.objects.filter(
            user=user,
            type=2,
            date__gte=start_date,
            date__lte=end_date,
            category__isnull=True
        ).aggregate(total=Sum(amount_field))['total'] or Decimal('0')
        
        # Calcular total de gastos
        total_expenses = sum([item['amount'] for item in expenses_by_category])
        total_expenses += uncategorized_amount
        
        if total_expenses == 0:
            return {
                'chart_data': [],
                'others_data': [],
                'total_expenses': 0,
                'uncategorized_amount': float(uncategorized_amount),
                'mode': mode,
                'period_summary': f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}",
                'categories_count': 0
            }
        
        # Procesar categorías principales vs "Otros"
        main_categories = []
        others_categories = []
        others_total = Decimal('0')
        
        for item in expenses_by_category:
            percentage = float(item['amount'] / total_expenses)
            
            category_data = {
                'category_id': item['category__id'],
                'name': item['category__name'],
                'amount': float(item['amount']),
                'count': item['count'],
                'percentage': percentage * 100,
                'color': item['category__color'],
                'icon': item['category__icon'],
                'formatted_amount': f"${item['amount']:,.0f}"
            }
            
            if percentage >= others_threshold:
                main_categories.append(category_data)
            else:
                others_categories.append(category_data)
                others_total += item['amount']
        
        # Agregar "Otros" si hay categorías pequeñas
        chart_data = main_categories.copy()
        if others_categories or uncategorized_amount > 0:
            others_amount = others_total + uncategorized_amount
            others_percentage = float(others_amount / total_expenses) * 100
            
            chart_data.append({
                'category_id': 'others',
                'name': 'Otros',
                'amount': float(others_amount),
                'count': len(others_categories) + (1 if uncategorized_amount > 0 else 0),
                'percentage': others_percentage,
                'color': '#9CA3AF',  # Color gris para "Otros"
                'icon': 'fa-ellipsis-h',
                'formatted_amount': f"${others_amount:,.0f}",
                'is_aggregated': True
            })
        
        # Agregar categoría sin asignar si existe
        if uncategorized_amount > 0:
            others_categories.append({
                'category_id': 'uncategorized',
                'name': 'Sin categoría',
                'amount': float(uncategorized_amount),
                'count': Transaction.objects.filter(
                    user=user, type=2, 
                    date__gte=start_date, date__lte=end_date,
                    category__isnull=True
                ).count(),
                'percentage': float(uncategorized_amount / total_expenses) * 100,
                'color': '#6B7280',
                'icon': 'fa-question-circle',
                'formatted_amount': f"${uncategorized_amount:,.0f}"
            })
        
        return {
            'chart_data': chart_data,
            'others_data': others_categories,
            'total_expenses': float(total_expenses),
            'uncategorized_amount': float(uncategorized_amount),
            'mode': mode,
            'period_summary': f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}",
            'categories_count': len(main_categories) + len(others_categories)
        }
    
    @staticmethod
    def get_daily_flow_chart(
        user,
        start_date: date,
        end_date: date,
        mode: str = 'total'
    ) -> Dict:
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
        amount_field = 'base_amount' if mode == 'base' else 'total_amount'
        
        # Obtener transacciones diarias agrupadas (sin transferencias)
        daily_transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).exclude(type=3).values('date').annotate(
            income=Sum(amount_field, filter=Q(type=1)),
            expenses=Sum(amount_field, filter=Q(type=2))
        ).order_by('date')
        
        # Crear diccionario para búsqueda rápida
        transactions_by_date = {}
        for item in daily_transactions:
            transactions_by_date[item['date']] = {
                'income': float(item['income'] or 0),
                'expenses': float(item['expenses'] or 0)
            }
        
        # Generar series de datos día por día
        dates = []
        income_series = []
        expense_series = []
        balance_series = []
        
        current_date = start_date
        cumulative_balance = 0
        
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            
            # Obtener datos del día (0 si no hay transacciones)
            day_data = transactions_by_date.get(current_date, {'income': 0, 'expenses': 0})
            
            income_series.append(day_data['income'])
            expense_series.append(day_data['expenses'])
            
            # Calcular balance acumulado
            daily_balance = day_data['income'] - day_data['expenses']
            cumulative_balance += daily_balance
            balance_series.append(cumulative_balance)
            
            current_date += timedelta(days=1)
        
        # Calcular estadísticas
        total_income = sum(income_series)
        total_expenses = sum(expense_series)
        final_balance = cumulative_balance
        
        return {
            'dates': dates,
            'series': {
                'income': {
                    'name': 'Ingresos diarios',
                    'data': income_series,
                    'color': '#10B981',  # Verde
                    'total': total_income
                },
                'expenses': {
                    'name': 'Gastos diarios', 
                    'data': expense_series,
                    'color': '#EF4444',  # Rojo
                    'total': total_expenses
                },
                'balance': {
                    'name': 'Balance acumulado',
                    'data': balance_series,
                    'color': '#3B82F6',  # Azul
                    'final': final_balance
                }
            },
            'summary': {
                'period_days': len(dates),
                'total_income': total_income,
                'total_expenses': total_expenses,
                'final_balance': final_balance,
                'avg_daily_income': total_income / len(dates) if dates else 0,
                'avg_daily_expense': total_expenses / len(dates) if dates else 0
            },
            'mode': mode,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    @staticmethod
    def get_transactions_by_category(
        user,
        category_id: int,
        start_date: date,
        end_date: date,
        mode: str = 'total',
        limit: int = 50
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
        amount_field = 'base_amount' if mode == 'base' else 'total_amount'
        
        # Filtro por categoría
        if category_id == 'uncategorized':
            category_filter = Q(category__isnull=True)
            category_name = 'Sin categoría'
        else:
            category_filter = Q(category__id=category_id)
            try:
                category = Category.objects.get(id=category_id, user=user)
                category_name = category.name
            except Category.DoesNotExist:
                return {
                    'error': 'Categoría no encontrada',
                    'transactions': [],
                    'total_count': 0
                }
        
        # Obtener transacciones
        transactions_query = Transaction.objects.filter(
            user=user,
            type=2,  # Solo gastos para drill-down de categorías
            date__gte=start_date,
            date__lte=end_date
        ).filter(category_filter).select_related(
            'category', 'origin_account'
        ).order_by('-date', '-created_at')
        
        total_count = transactions_query.count()
        transactions_page = transactions_query[:limit]
        
        # Formatear transacciones
        transactions_data = []
        for tx in transactions_page:
            amount = getattr(tx, amount_field)
            transactions_data.append({
                'id': tx.id,
                'date': tx.date.isoformat(),
                'description': tx.description or f'Gasto en {category_name}',
                'amount': float(amount),
                'formatted_amount': f"${amount:,.0f}",
                'account': tx.origin_account.name,
                'tag': tx.tag,
                'category': {
                    'id': tx.category.id if tx.category else None,
                    'name': tx.category.name if tx.category else 'Sin categoría',
                    'color': tx.category.color if tx.category else '#6B7280',
                    'icon': tx.category.icon if tx.category else 'fa-question-circle'
                } if tx.category else None
            })
        
        # Calcular total de la categoría en el período
        total_amount = transactions_query.aggregate(
            total=Sum(amount_field)
        )['total'] or Decimal('0')
        
        return {
            'transactions': transactions_data,
            'total_count': total_count,
            'showing_count': len(transactions_data),
            'category_name': category_name,
            'total_amount': float(total_amount),
            'formatted_total': f"${total_amount:,.0f}",
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'mode': mode,
            'has_more': total_count > limit
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
        
        if period_str == 'current_month':
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)
            
        elif period_str == 'last_month':
            if today.month == 1:
                prev_year = today.year - 1
                prev_month = 12
            else:
                prev_year = today.year
                prev_month = today.month - 1
                
            start_date = date(prev_year, prev_month, 1)
            last_day = calendar.monthrange(prev_year, prev_month)[1]
            end_date = date(prev_year, prev_month, last_day)
            
        elif period_str == 'current_year':
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 12, 31)
            
        elif period_str == 'last_7_days':
            end_date = today
            start_date = today - timedelta(days=6)
            
        elif period_str == 'last_30_days':
            end_date = today
            start_date = today - timedelta(days=29)
            
        elif ',' in period_str:
            # Rango personalizado: 'YYYY-MM-DD,YYYY-MM-DD'
            start_str, end_str = period_str.split(',')
            start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d').date()
            
        elif len(period_str) == 7 and period_str[4] == '-':
            # Mes específico: 'YYYY-MM'
            year, month = map(int, period_str.split('-'))
            start_date = date(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, last_day)
            
        elif len(period_str) == 4 and period_str.isdigit():
            # Año específico: 'YYYY'
            year = int(period_str)
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
        else:
            # Default: mes actual
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)
        
        return start_date, end_date