import logging

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from users.permissions import IsAdminUser, IsVerifiedUser

from .serializers import DashboardDataSerializer, FinancialDashboardSerializer
from .services import DashboardService, FinancialDashboardService

logger = logging.getLogger(__name__)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def dashboard_view(request):
    """
    Vista principal del dashboard con mini cards y estadísticas
    """
    try:
        user = request.user

        if user.is_admin:
            # Dashboard para administradores
            dashboard_data = DashboardService.get_admin_dashboard_data(user)
        else:
            # Dashboard para monitores
            dashboard_data = DashboardService.get_monitor_dashboard_data(user)

        # Serializar los datos
        serializer = DashboardDataSerializer(dashboard_data)

        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": f"Dashboard cargado exitosamente para {user.get_full_name()}",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Error en dashboard: {e}")
        return Response(
            {"success": False, "error": "Error interno del servidor", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def mini_cards_view(request):
    """
    Vista para obtener solo las mini cards del dashboard
    """
    try:
        user = request.user

        if user.is_admin:
            dashboard_data = DashboardService.get_admin_dashboard_data(user)
        else:
            dashboard_data = DashboardService.get_monitor_dashboard_data(user)

        return Response(
            {
                "success": True,
                "mini_cards": dashboard_data["mini_cards"],
                "message": "Mini cards obtenidas exitosamente",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Error obteniendo mini cards: {e}")
        return Response(
            {"success": False, "error": "Error interno del servidor", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def stats_view(request):
    """
    Vista para obtener solo las estadísticas del dashboard
    """
    try:
        user = request.user

        if user.is_admin:
            dashboard_data = DashboardService.get_admin_dashboard_data(user)
        else:
            dashboard_data = DashboardService.get_monitor_dashboard_data(user)

        return Response(
            {
                "success": True,
                "stats": dashboard_data["stats"],
                "message": "Estadísticas obtenidas exitosamente",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Error obteniendo estadísticas: {e}")
        return Response(
            {"success": False, "error": "Error interno del servidor", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def alerts_view(request):
    """
    Vista para obtener alertas del dashboard
    """
    try:
        user = request.user

        if user.is_admin:
            dashboard_data = DashboardService.get_admin_dashboard_data(user)
        else:
            dashboard_data = DashboardService.get_monitor_dashboard_data(user)

        return Response(
            {
                "success": True,
                "alerts": dashboard_data["alerts"],
                "message": "Alertas obtenidas exitosamente",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Error obteniendo alertas: {e}")
        return Response(
            {"success": False, "error": "Error interno del servidor", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def charts_data_view(request):
    """
    Vista para obtener datos de gráficos del dashboard
    """
    try:
        user = request.user

        if user.is_admin:
            dashboard_data = DashboardService.get_admin_dashboard_data(user)
        else:
            dashboard_data = DashboardService.get_monitor_dashboard_data(user)

        return Response(
            {
                "success": True,
                "charts_data": dashboard_data["charts_data"],
                "message": "Datos de gráficos obtenidos exitosamente",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Error obteniendo datos de gráficos: {e}")
        return Response(
            {"success": False, "error": "Error interno del servidor", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_overview_view(request):
    """
    Vista de resumen para administradores con información crítica
    """
    try:
        dashboard_data = DashboardService.get_admin_dashboard_data(request.user)

        # Filtrar solo información crítica para administradores
        critical_info = {
            "pending_verifications": dashboard_data["stats"]["pending_verifications"],
            "excessive_hours_alerts": dashboard_data["stats"]["excessive_hours_alerts"],
            "critical_alerts": dashboard_data["stats"]["critical_alerts"],
            "active_entries": dashboard_data["stats"]["active_entries"],
            "alerts": dashboard_data["alerts"],
        }

        return Response(
            {
                "success": True,
                "overview": critical_info,
                "message": "Resumen administrativo obtenido exitosamente",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Error obteniendo resumen administrativo: {e}")
        return Response(
            {"success": False, "error": "Error interno del servidor", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsVerifiedUser])
def financial_dashboard_view(request):
    """
    Vista principal del dashboard financiero con totales, filtros y gráficos

    Query Parameters:
        - year (opcional): Año a filtrar (ej: 2025)
        - month (opcional): Mes a filtrar (1-12, requiere year)
        - account_id (opcional): ID de cuenta a filtrar
        - all (opcional): Si es "true", obtiene todos los períodos

    Ejemplos de uso:
        GET /api/dashboard/financial/                           # Mes actual
        GET /api/dashboard/financial/?all=true                  # Todos los períodos
        GET /api/dashboard/financial/?year=2025                 # Año 2025
        GET /api/dashboard/financial/?year=2025&month=12        # Diciembre 2025
        GET /api/dashboard/financial/?account_id=5              # Cuenta específica
        GET /api/dashboard/financial/?year=2025&month=12&account_id=5  # Combinado

    Returns:
        - has_data: bool - Indica si hay transacciones
        - summary: dict - Totales (ingresos, gastos, ahorros, IVA, GMF)
        - filters: dict - Filtros aplicados
        - recent_transactions: list - Últimos 5 movimientos
        - charts: dict - Datos para gráficos (distribución de gastos, flujo diario)
        - accounts_info: dict - Información de cuentas del usuario
        - empty_state: dict - Mensaje y sugerencias si no hay datos
    """
    try:
        user = request.user

        # Obtener parámetros de filtro
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        account_id = request.query_params.get("account_id")
        show_all = request.query_params.get("all", "false").lower() == "true"

        # Validar y convertir parámetros
        try:
            if year:
                year = int(year)
                if year < 2000 or year > 2100:
                    return Response(
                        {
                            "success": False,
                            "error": "Año inválido",
                            "details": "El año debe estar entre 2000 y 2100",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if month:
                if not year:
                    return Response(
                        {
                            "success": False,
                            "error": "Parámetro 'year' requerido",
                            "details": "Para filtrar por mes, debes especificar también el año",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                month = int(month)
                if month < 1 or month > 12:
                    return Response(
                        {
                            "success": False,
                            "error": "Mes inválido",
                            "details": "El mes debe estar entre 1 y 12",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if account_id:
                account_id = int(account_id)

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "error": "Parámetros inválidos",
                    "details": "Los parámetros year, month y account_id deben ser números enteros",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Si show_all=true, no aplicar filtros de fecha
        if show_all:
            year = None
            month = None

        # Si no se especifica ningún filtro, usar mes actual
        if not show_all and not year and not month:
            from datetime import date

            today = date.today()
            year = today.year
            month = today.month

        # Obtener datos del dashboard
        dashboard_data = FinancialDashboardService.get_financial_summary(
            user, year=year, month=month, account_id=account_id
        )

        # Verificar si hay error en el servicio
        if "error" in dashboard_data and not dashboard_data.get("has_data", True):
            return Response(
                {
                    "success": False,
                    "error": dashboard_data["error"],
                    "has_data": False,
                },
                status=status.HTTP_400_BAD_REQUEST
                if "no encontrada" in dashboard_data["error"]
                else status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Serializar respuesta
        serializer = FinancialDashboardSerializer(dashboard_data)

        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Dashboard financiero obtenido exitosamente",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception(f"Error en dashboard financiero: {e}")
        return Response(
            {
                "success": False,
                "error": "Error interno del servidor",
                "details": str(e),
                "has_data": False,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
