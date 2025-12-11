import logging

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from users.permissions import IsAdminUser, IsVerifiedUser

from .serializers import DashboardDataSerializer
from .services import DashboardService

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
            # Dashboard para usuarios regulares
            dashboard_data = DashboardService.get_user_dashboard_data(user)

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
            dashboard_data = DashboardService.get_user_dashboard_data(user)

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
            dashboard_data = DashboardService.get_user_dashboard_data(user)

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
            dashboard_data = DashboardService.get_user_dashboard_data(user)

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
            dashboard_data = DashboardService.get_user_dashboard_data(user)

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
            "pending_verifications": dashboard_data["stats"].get("pending_verifications", 0),
            "active_users": dashboard_data["stats"].get("active_users", 0),
            "unread_notifications": dashboard_data["stats"].get("unread_notifications", 0),
            "recent_notifications": dashboard_data["stats"].get("recent_notifications", 0),
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
