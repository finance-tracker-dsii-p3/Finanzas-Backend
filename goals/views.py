"""
Views para gestión de metas de ahorro
"""

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
import logging

from .models import Goal
from .serializers import (
    GoalSerializer,
    GoalDetailSerializer,
    GoalUpdateSerializer,
)

logger = logging.getLogger(__name__)


class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de metas de ahorro

    Proporciona operaciones CRUD completas más acciones adicionales
    para activar/desactivar, reordenar y obtener estadísticas.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar metas por usuario autenticado"""
        return Goal.objects.filter(user=self.request.user).order_by(
            "order", "name"
        )

    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == "create":
            return GoalSerializer
        elif self.action in ["retrieve", "list"]:
            return GoalDetailSerializer
        elif self.action in ["update", "partial_update"]:
            return GoalUpdateSerializer
        else:
            return GoalDetailSerializer

    def list(self, request, *args, **kwargs):
        """
        Listar metas del usuario
        """
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)

        count = queryset.count()
        logger.info(
            f"Usuario {request.user.id} listó transacciones: {count} encontradas"
        )

        # Si no hay metas, devolver mensaje informativo
        if count == 0:
            return Response(
                {
                    "count": 0,
                    "message": "No tienes metas creadas.",
                    "results": [],
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Crear una meta asignando el usuario autenticado"""
        try:
            goal = serializer.save()

            logger.info(
                f"Usuario {self.request.user.id} creó una meta: {goal.name} "
            )

        except Exception as e:
            logger.warning(
                f"Error al crear meta para usuario {self.request.user.id}: {str(e)}"
            )
            raise e

    def perform_update(self, serializer):
        """Actualizar una meta existente"""
        try:
            goal = serializer.save()
            logger.info(f"Usuario {self.request.user.id} actualizó la meta {goal.name}")

        except Exception as e:
            logger.warning(
                f"Error al actualizar meta {self.get_object().id}: {str(e)}"
            )
            raise e

    def perform_destroy(self, instance):
        """Eliminar meta existente"""
        try:
            instance.delete()

            logger.info(f"Usuario {self.request.user.id} eliminó una meta")
        except Exception as e:
            logger.warning(f"Error al eliminar transacción {instance.id}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
