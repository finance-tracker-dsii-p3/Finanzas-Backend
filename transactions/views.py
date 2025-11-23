"""
Views para gestión de categorías de ingresos y gastos
"""

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
import logging

from .models import Transaction
from .serializers import (
    TransactionSerializer,
    TransactionDetailSerializer,
    TransactionUpdateSerializer
)
from .filters import TransactionFilter
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de categorías

    Proporciona operaciones CRUD completas más acciones adicionales
    para activar/desactivar, reordenar y obtener estadísticas.
    """

    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = TransactionFilter
    search_fields = ["origin_account", "destination_account", "tag", "date"]  # DRF search filter (optional)
    ordering_fields = ["date", "total_amount"]  # user can order by these
    ordering = ["-date"]  # default ordering

    def get_queryset(self):
        """Filtrar categorías por usuario autenticado"""
        return Transaction.objects.filter(user=self.request.user).order_by("order", "name")

    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == "create":
            return TransactionSerializer
        elif self.action in ["retrieve", "list"]:
            return TransactionDetailSerializer
        elif self.action in ["update", "partial_update"]:
            return TransactionUpdateSerializer
        else:
            return TransactionDetailSerializer

    def list(self, request, *args, **kwargs):
        """
        Listar transacciones del usuario con filtros opcionales
        """
        queryset = self.get_queryset()

        # Filtro por tipo
        transaction_type = request.query_params.get("type")
        if transaction_type:
            queryset = queryset.filter(type=transaction_type)

        serializer = self.get_serializer(queryset, many=True)

        count = queryset.count()
        logger.info(f"Usuario {request.user.id} listó transacciones: {count} encontradas")

        # Si no hay transacciones, devolver mensaje informativo
        if count == 0:
            return Response(
                {
                    "count": 0,
                    "message": "No tienes transacciones creadas.",
                    "results": [],
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Crear transacción asignando el usuario autenticado"""
        try:
            transaction = serializer.save()
            
            logger.info(
                f"Usuario {self.request.user.id} creó transacción: {transaction.name} "
                f"({transaction.get_type_display()})"
            )

        except Exception as e:
            logger.warning(
                f"Error al crear transacción para usuario {self.request.user.id}: {str(e)}"
            )
            raise e

    def perform_update(self, serializer):
        """Actualizar transacción"""
        try:
            serializer.save()
            logger.info(
                f"Usuario {self.request.user.id} actualizó una transacción"
            )

        except Exception as e:
            logger.warning(
                f"Error al actualizar transacción {self.get_object().id}: {str(e)}"
            )
            raise e
        
    def perform_duplicate(self, instance):
        """Duplicar transacción existente"""
        try:
            instance.pk = None  # Resetear PK para crear nuevo objeto
            instance.save()

            logger.info(
                f"Usuario {self.request.user.id} duplicó una transacción"
            )

        except Exception as e:
            logger.warning(
                f"Error al duplicar transacción {instance.id}: {str(e)}"
            )
            raise e

    def perform_destroy(self, instance):
        """Eliminar transacción existente"""
        try:
            instance.delete()

            logger.info(
                f"Usuario {self.request.user.id} eliminó una transacción"
            )

        except Exception as e:
            logger.warning(
                f"Error al eliminar transacción {instance.id}: {str(e)}"
            )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)