"""
Vistas para API de Analytics Financieros (HU-13)
"""
from datetime import date
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models

from .services import FinancialAnalyticsService
from .serializers import (
    AnalyticsDashboardSerializer,
    PeriodIndicatorsSerializer,
    ExpensesCategoryChartSerializer,
    DailyFlowChartSerializer,
    CategoryTransactionsSerializer
)

import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    """
    Vista principal del dashboard de analytics financieros (HU-13)
    
    Query Parameters:
    - period: Período de análisis (default: 'current_month')
    - mode: 'base' o 'total' (default: 'total')
    - others_threshold: % mínimo para categorías individuales (default: 0.05)
    
    Returns:
        Datos completos del dashboard: indicadores, gráfico dona, gráfico líneas
    """
    try:
        # Parámetros de query
        period_str = request.GET.get('period', 'current_month')
        mode = request.GET.get('mode', 'total')
        others_threshold = float(request.GET.get('others_threshold', 0.05))
        
        # Validar modo
        if mode not in ['base', 'total']:
            return Response({
                'error': 'Modo inválido. Debe ser "base" o "total"',
                'code': 'INVALID_MODE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parsear período
        try:
            start_date, end_date = FinancialAnalyticsService.parse_period_param(period_str)
        except Exception as e:
            return Response({
                'error': 'Formato de período inválido',
                'code': 'INVALID_PERIOD',
                'details': {'period_provided': period_str, 'error': str(e)},
                'suggestions': [
                    'Usar: current_month, last_month, current_year, last_7_days, last_30_days',
                    'O formato: YYYY-MM (ej: 2025-10)',
                    'O rango: YYYY-MM-DD,YYYY-MM-DD'
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Validar que el usuario tenga datos para analytics
        from transactions.models import Transaction
        total_transactions = Transaction.objects.filter(user=user).count()
        
        if total_transactions == 0:
            return Response({
                'success': False,
                'error': 'No tienes transacciones registradas',
                'code': 'NO_DATA_AVAILABLE',
                'details': {
                    'message': 'Para generar analytics necesitas al menos una transacción',
                    'suggestions': [
                        'Crea algunas transacciones de ingresos y gastos',
                        'Asigna categorías a tus gastos para mejores gráficos',
                        'El dashboard se activará automáticamente cuando tengas datos'
                    ],
                    'quick_start': {
                        'step1': 'POST /api/transactions/ - Crear transacciones',
                        'step2': 'GET /api/categories/ - Ver categorías disponibles',
                        'step3': 'GET /api/analytics/dashboard/ - Ver analytics'
                    }
                }
            }, status=status.HTTP_200_OK)  # 200 porque no es error del sistema
        
        # Verificar transacciones en el período solicitado
        period_transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).count()
        
        if period_transactions == 0:
            return Response({
                'success': True,
                'data': {
                    'indicators': {
                        'income': {'amount': 0, 'count': 0, 'formatted': '$0'},
                        'expenses': {'amount': 0, 'count': 0, 'formatted': '$0'},
                        'balance': {'amount': 0, 'formatted': '$0', 'is_positive': True},
                        'period': {
                            'start': start_date.isoformat(),
                            'end': end_date.isoformat(),
                            'days': (end_date - start_date).days + 1
                        },
                        'mode': mode,
                        'currency': 'COP'
                    },
                    'expenses_chart': {
                        'chart_data': [],
                        'others_data': [],
                        'total_expenses': 0,
                        'uncategorized_amount': 0,
                        'mode': mode,
                        'period_summary': f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}",
                        'categories_count': 0
                    },
                    'daily_flow_chart': {
                        'dates': [],
                        'series': {
                            'income': {'name': 'Ingresos diarios', 'data': [], 'color': '#10B981', 'total': 0},
                            'expenses': {'name': 'Gastos diarios', 'data': [], 'color': '#EF4444', 'total': 0},
                            'balance': {'name': 'Balance acumulado', 'data': [], 'color': '#3B82F6', 'final': 0}
                        },
                        'summary': {
                            'period_days': (end_date - start_date).days + 1,
                            'total_income': 0,
                            'total_expenses': 0,
                            'final_balance': 0,
                            'avg_daily_income': 0,
                            'avg_daily_expense': 0
                        },
                        'mode': mode,
                        'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()}
                    },
                    'metadata': {
                        'generated_at': date.today().isoformat(),
                        'user_id': user.id,
                        'period_requested': period_str,
                        'mode_used': mode,
                        'others_threshold': others_threshold,
                        'data_status': 'EMPTY_PERIOD'
                    },
                    'info_message': f'No hay transacciones en el período {start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}. Tienes {total_transactions} transacciones en total.'
                },
                'message': f'Analytics generado para período vacío {period_str}. Sin transacciones en este rango de fechas.'
            }, status=status.HTTP_200_OK)
        
        # Obtener datos de analytics
        indicators = FinancialAnalyticsService.get_period_indicators(
            user, start_date, end_date, mode
        )
        
        expenses_chart = FinancialAnalyticsService.get_expenses_by_category(
            user, start_date, end_date, mode, others_threshold
        )
        
        daily_flow_chart = FinancialAnalyticsService.get_daily_flow_chart(
            user, start_date, end_date, mode
        )
        
        # Preparar respuesta completa
        dashboard_data = {
            'indicators': indicators,
            'expenses_chart': expenses_chart,
            'daily_flow_chart': daily_flow_chart,
            'metadata': {
                'generated_at': date.today().isoformat(),
                'user_id': user.id,
                'period_requested': period_str,
                'mode_used': mode,
                'others_threshold': others_threshold
            }
        }
        
        # Serializar respuesta
        serializer = AnalyticsDashboardSerializer(dashboard_data)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': f'Analytics dashboard generado para período {period_str} en modo {mode}'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en analytics dashboard para usuario {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR',
            'details': {'error_message': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def period_indicators(request):
    """
    Obtiene solo los indicadores del período (KPIs)
    
    Query Parameters:
    - period: Período de análisis (default: 'current_month')
    - mode: 'base' o 'total' (default: 'total')
    """
    try:
        period_str = request.GET.get('period', 'current_month')
        mode = request.GET.get('mode', 'total')
        
        if mode not in ['base', 'total']:
            return Response({
                'error': 'Modo inválido. Debe ser "base" o "total"',
                'code': 'INVALID_MODE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_date, end_date = FinancialAnalyticsService.parse_period_param(period_str)
        
        user = request.user
        
        # Validar que el usuario tenga transacciones
        from transactions.models import Transaction
        total_transactions = Transaction.objects.filter(user=user).count()
        
        if total_transactions == 0:
            return Response({
                'success': False,
                'error': 'No tienes transacciones para calcular indicadores',
                'code': 'NO_TRANSACTIONS',
                'details': {
                    'message': 'Necesitas crear transacciones primero',
                    'help': 'Usa POST /api/transactions/ para crear transacciones',
                    'total_user_transactions': 0
                }
            }, status=status.HTTP_200_OK)
        
        # Verificar transacciones en el período
        period_transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date, 
            date__lte=end_date
        ).count()
        
        indicators = FinancialAnalyticsService.get_period_indicators(
            user, start_date, end_date, mode
        )
        
        # Agregar información contextual
        indicators['context'] = {
            'total_user_transactions': total_transactions,
            'period_transactions': period_transactions,
            'period_range': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        }
        
        serializer = PeriodIndicatorsSerializer(indicators)
        
        message = 'Indicadores del período obtenidos exitosamente'
        if period_transactions == 0:
            message = f'Período sin transacciones. Tienes {total_transactions} transacciones en total, pero ninguna en el rango {start_date.strftime("%d/%m")} - {end_date.strftime("%d/%m")}.'
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': message
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo indicadores: {e}")
        return Response({
            'success': False,
            'error': 'Error obteniendo indicadores',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def expenses_by_category(request):
    """
    Obtiene datos del gráfico de dona de gastos por categoría
    
    Query Parameters:
    - period: Período de análisis (default: 'current_month')
    - mode: 'base' o 'total' (default: 'total')
    - others_threshold: % mínimo para mostrar categoría individual (default: 0.05)
    """
    try:
        period_str = request.GET.get('period', 'current_month')
        mode = request.GET.get('mode', 'total')
        others_threshold = float(request.GET.get('others_threshold', 0.05))
        
        if mode not in ['base', 'total']:
            return Response({
                'error': 'Modo inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_date, end_date = FinancialAnalyticsService.parse_period_param(period_str)
        
        user = request.user
        
        # Validar datos del usuario
        from transactions.models import Transaction
        total_expenses = Transaction.objects.filter(user=user, type=2).count()
        
        if total_expenses == 0:
            return Response({
                'success': False,
                'error': 'No tienes gastos registrados',
                'code': 'NO_EXPENSES',
                'details': {
                    'message': 'El gráfico de categorías requiere transacciones de tipo "gasto"',
                    'help': 'Crea transacciones con type=2 (gastos) y asigna categorías',
                    'total_expenses': 0
                }
            }, status=status.HTTP_200_OK)
        
        period_expenses = Transaction.objects.filter(
            user=user, 
            type=2,
            date__gte=start_date,
            date__lte=end_date
        ).count()
        
        chart_data = FinancialAnalyticsService.get_expenses_by_category(
            user, start_date, end_date, mode, others_threshold
        )
        
        # Agregar contexto a los datos
        chart_data['context'] = {
            'total_user_expenses': total_expenses,
            'period_expenses': period_expenses
        }
        
        serializer = ExpensesCategoryChartSerializer(chart_data)
        
        message = 'Datos de gráfico de categorías obtenidos exitosamente'
        if period_expenses == 0:
            message = f'Sin gastos en el período. Tienes {total_expenses} gastos en total.'
        elif chart_data.get('total_expenses', 0) == 0:
            message = 'Período sin gastos categorizados'
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': message
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo gráfico de categorías: {e}")
        return Response({
            'success': False,
            'error': 'Error obteniendo gráfico de categorías',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def daily_flow_chart(request):
    """
    Obtiene datos del gráfico de líneas de flujo diario
    
    Query Parameters:
    - period: Período de análisis (default: 'current_month')
    - mode: 'base' o 'total' (default: 'total')
    """
    try:
        period_str = request.GET.get('period', 'current_month')
        mode = request.GET.get('mode', 'total')
        
        if mode not in ['base', 'total']:
            return Response({
                'error': 'Modo inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_date, end_date = FinancialAnalyticsService.parse_period_param(period_str)
        
        chart_data = FinancialAnalyticsService.get_daily_flow_chart(
            request.user, start_date, end_date, mode
        )
        
        serializer = DailyFlowChartSerializer(chart_data)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Datos de gráfico de flujo diario obtenidos exitosamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo gráfico de flujo diario: {e}")
        return Response({
            'success': False,
            'error': 'Error obteniendo gráfico de flujo diario',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def category_transactions(request, category_id):
    """
    Obtiene transacciones filtradas por categoría (drill-down del gráfico de dona)
    
    Path Parameters:
    - category_id: ID de categoría o 'uncategorized' para sin categoría
    
    Query Parameters:
    - period: Período de análisis (default: 'current_month')
    - mode: 'base' o 'total' (default: 'total')
    - limit: Número máximo de transacciones (default: 50)
    """
    try:
        period_str = request.GET.get('period', 'current_month')
        mode = request.GET.get('mode', 'total')
        limit = int(request.GET.get('limit', 50))
        
        if mode not in ['base', 'total']:
            return Response({
                'error': 'Modo inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_date, end_date = FinancialAnalyticsService.parse_period_param(period_str)
        
        # Convertir category_id si no es 'uncategorized'
        if category_id != 'uncategorized':
            try:
                category_id = int(category_id)
            except ValueError:
                return Response({
                    'error': 'ID de categoría inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        transactions_data = FinancialAnalyticsService.get_transactions_by_category(
            request.user, category_id, start_date, end_date, mode, limit
        )
        
        if 'error' in transactions_data:
            return Response({
                'success': False,
                'error': transactions_data['error']
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategoryTransactionsSerializer(transactions_data)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Transacciones de categoría obtenidas exitosamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo transacciones de categoría: {e}")
        return Response({
            'success': False,
            'error': 'Error obteniendo transacciones de categoría',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def available_periods(request):
    """
    Obtiene períodos disponibles basados en transacciones del usuario
    
    Returns:
        Lista de períodos con datos disponibles
    """
    try:
        from transactions.models import Transaction
        
        # Obtener rango de fechas de transacciones del usuario
        date_range = Transaction.objects.filter(
            user=request.user
        ).aggregate(
            min_date=models.Min('date'),
            max_date=models.Max('date')
        )
        
        min_date = date_range['min_date']
        max_date = date_range['max_date']
        
        if not min_date or not max_date:
            return Response({
                'success': True,
                'data': {
                    'available_periods': [],
                    'message': 'No hay transacciones registradas'
                }
            }, status=status.HTTP_200_OK)
        
        # Generar períodos sugeridos
        today = date.today()
        
        periods = [
            {
                'key': 'current_month',
                'name': 'Mes actual',
                'description': today.strftime('%B %Y')
            },
            {
                'key': 'last_month', 
                'name': 'Mes anterior',
                'description': 'Mes completo anterior'
            },
            {
                'key': 'current_year',
                'name': 'Año actual',
                'description': str(today.year)
            },
            {
                'key': 'last_7_days',
                'name': 'Últimos 7 días',
                'description': 'Semana reciente'
            },
            {
                'key': 'last_30_days',
                'name': 'Últimos 30 días',
                'description': 'Mes reciente'
            }
        ]
        
        return Response({
            'success': True,
            'data': {
                'available_periods': periods,
                'data_range': {
                    'min_date': min_date.isoformat(),
                    'max_date': max_date.isoformat()
                },
                'custom_period_info': {
                    'formats': [
                        'YYYY-MM (mes específico)',
                        'YYYY (año específico)',
                        'YYYY-MM-DD,YYYY-MM-DD (rango personalizado)'
                    ]
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo períodos disponibles: {e}")
        return Response({
            'success': False,
            'error': 'Error obteniendo períodos disponibles',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def compare_periods(request):
    """
    Compara indicadores financieros entre dos períodos (HU-14)
    
    Query Parameters:
    - period1: Período base para comparación (requerido)
    - period2: Período a comparar contra period1 (requerido)  
    - mode: 'base' o 'total' (default: 'total')
    
    Examples:
    - ?period1=2025-09&period2=2025-10&mode=total
    - ?period1=last_month&period2=current_month&mode=base
    
    Returns:
        Comparación detallada con diferencias absolutas y porcentuales
    """
    try:
        # Validar parámetros requeridos
        period1_str = request.GET.get('period1')
        period2_str = request.GET.get('period2')
        mode = request.GET.get('mode', 'total')
        
        if not period1_str or not period2_str:
            return Response({
                'success': False,
                'error': 'Parámetros period1 y period2 son requeridos',
                'code': 'MISSING_PERIODS',
                'details': {
                    'provided': {
                        'period1': period1_str,
                        'period2': period2_str
                    },
                    'examples': [
                        '?period1=2025-09&period2=2025-10&mode=total',
                        '?period1=last_month&period2=current_month&mode=base',
                        '?period1=2025-01-01,2025-01-31&period2=2025-02-01,2025-02-28'
                    ]
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar modo
        if mode not in ['base', 'total']:
            return Response({
                'success': False,
                'error': 'Modo inválido. Debe ser "base" o "total"',
                'code': 'INVALID_MODE',
                'details': {'provided_mode': mode}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parsear períodos
        try:
            period1_start, period1_end = FinancialAnalyticsService.parse_period_param(period1_str)
            period2_start, period2_end = FinancialAnalyticsService.parse_period_param(period2_str)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Formato de período inválido',
                'code': 'INVALID_PERIOD_FORMAT',
                'details': {
                    'period1_provided': period1_str,
                    'period2_provided': period2_str,
                    'error': str(e)
                },
                'supported_formats': [
                    'current_month, last_month, current_year',
                    'YYYY-MM (ej: 2025-10)', 
                    'YYYY (ej: 2025)',
                    'YYYY-MM-DD,YYYY-MM-DD (rango personalizado)'
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que los períodos no se superpongan (opcional, para mayor claridad)
        if (period1_start <= period2_end and period2_start <= period1_end):
            logger.warning(f"Períodos superpuestos detectados: {period1_str} vs {period2_str}")
        
        user = request.user
        
        # Validar que el usuario tenga transacciones
        from transactions.models import Transaction
        total_transactions = Transaction.objects.filter(user=user).count()
        
        if total_transactions == 0:
            return Response({
                'success': False,
                'error': 'No tienes transacciones para comparar períodos',
                'code': 'NO_USER_TRANSACTIONS',
                'details': {
                    'message': 'Necesitas crear transacciones antes de poder hacer comparaciones',
                    'suggestions': [
                        'Crea transacciones con POST /api/transactions/',
                        'Asigna categorías a tus transacciones',
                        'Intenta la comparación nuevamente'
                    ]
                }
            }, status=status.HTTP_200_OK)
        
        # Realizar comparación
        comparison_data = FinancialAnalyticsService.compare_periods(
            user, period1_start, period1_end, period2_start, period2_end, mode
        )
        
        # Verificar si se puede hacer comparación válida
        if not comparison_data['comparison_summary']['can_compare']:
            period1_has_data = comparison_data['comparison_summary']['period1']['has_data']
            period2_has_data = comparison_data['comparison_summary']['period2']['has_data']
            
            if not period1_has_data and not period2_has_data:
                error_msg = f"Ninguno de los períodos tiene transacciones"
                code = 'NO_DATA_IN_PERIODS'
            elif not period1_has_data:
                error_msg = f"No hay datos en el primer período ({period1_str})"
                code = 'NO_DATA_PERIOD1'
            else:
                error_msg = f"No hay datos en el segundo período ({period2_str})"
                code = 'NO_DATA_PERIOD2'
            
            return Response({
                'success': False,
                'error': error_msg,
                'code': code,
                'details': {
                    'comparison_summary': comparison_data['comparison_summary'],
                    'total_user_transactions': total_transactions,
                    'suggestion': 'Intenta con períodos que tengan transacciones registradas'
                }
            }, status=status.HTTP_200_OK)
        
        # Serializar la respuesta
        from .serializers import PeriodComparisonSerializer
        
        # Preparar mensaje de éxito
        period1_name = comparison_data['comparison_summary']['period1']['name']
        period2_name = comparison_data['comparison_summary']['period2']['name']
        
        # Generar resumen ejecutivo
        differences = comparison_data['differences']
        executive_summary = []
        
        if differences['income']['percentage'] != 0:
            executive_summary.append(differences['income']['summary'])
        if differences['expenses']['percentage'] != 0:
            executive_summary.append(differences['expenses']['summary'])
        if differences['balance']['percentage'] != 0:
            executive_summary.append(differences['balance']['summary'])
            
        if not executive_summary:
            executive_summary = ["Sin cambios significativos entre períodos"]
        
        # Serializar datos
        serializer = PeriodComparisonSerializer(comparison_data)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': f'Comparación completada: {period1_name} vs {period2_name}',
            'executive_summary': executive_summary,
            'metadata': {
                'request_params': {
                    'period1': period1_str,
                    'period2': period2_str,
                    'mode': mode
                },
                'generated_at': date.today().isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en comparación de períodos para usuario {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor en comparación de períodos',
            'code': 'INTERNAL_ERROR',
            'details': {
                'error_message': str(e),
                'provided_params': {
                    'period1': request.GET.get('period1'),
                    'period2': request.GET.get('period2'),
                    'mode': request.GET.get('mode', 'total')
                }
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
