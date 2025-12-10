"""
Views para gestión de categorías de ingresos y gastos
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
import logging

from .models import Transaction
from .serializers import (
    TransactionSerializer,
    TransactionDetailSerializer,
    TransactionUpdateSerializer,
)
from .services import TransactionService
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
    search_fields = ["tag", "date"]  # DRF search filter (optional)
    ordering_fields = ["date", "created_at", "total_amount"]  # user can order by these
    ordering = ["-created_at"]  # default ordering: más reciente primero (por fecha y hora de creación)

    def get_queryset(self):
        """Filtrar transacciones por usuario autenticado"""
        # Ordenar por fecha y hora de creación (más reciente primero)
        # created_at tiene fecha y hora, así que es más preciso que solo date
        return Transaction.objects.filter(user=self.request.user).order_by("-created_at")

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
        queryset = self.filter_queryset(self.get_queryset())

        # Filtro por tipo
        transaction_type = request.query_params.get("type")
        if transaction_type:
            queryset = queryset.filter(type=transaction_type)

        count = queryset.count()
        logger.info(f"Usuario {request.user.id} listó transacciones: {count} encontradas")

        serializer = self.get_serializer(queryset, many=True)

        # Formato estandarizado de respuesta
        return Response(
            {
                "count": count,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        """Crear transacción asignando el usuario autenticado y actualizar saldos"""
        try:
            transaction = serializer.save()

            # Actualizar saldos de cuentas automáticamente
            TransactionService.handle_transaction_creation(transaction)

            desc = ""
            if hasattr(transaction, "description") and transaction.description:
                desc = f" - Descripción: {transaction.description}"
            logger.info(
                f"Usuario {self.request.user.id} creó transacción ID: {transaction.id} "
                f"({transaction.get_type_display()}) - Monto: {transaction.total_amount}{desc}"
            )

        except Exception as e:
            logger.error(
                f"Error al crear transacción para usuario {self.request.user.id}: {str(e)}"
            )
            raise e

    def perform_update(self, serializer):
        """Actualizar transacción y actualizar saldos"""
        try:
            # Obtener la instancia actual antes de actualizar
            old_transaction = self.get_object()

            # Guardar los valores antiguos necesarios para revertir
            old_type = old_transaction.type
            old_origin_account = old_transaction.origin_account
            old_destination_account = old_transaction.destination_account
            old_total_amount = old_transaction.total_amount

            # Guardar la nueva transacción
            new_transaction = serializer.save()

            # Solo actualizar saldos si algo cambió que afecte los saldos
            needs_update = (
                old_type != new_transaction.type
                or old_origin_account != new_transaction.origin_account
                or old_destination_account != new_transaction.destination_account
                or old_total_amount != new_transaction.total_amount
            )

            if needs_update:
                # Crear instancia temporal con datos antiguos para revertir
                from decimal import Decimal

                old_transaction_temp = Transaction(
                    type=old_type,
                    origin_account=old_origin_account,
                    destination_account=old_destination_account,
                    total_amount=Decimal(str(old_total_amount)),
                )

                # Actualizar saldos: revertir el anterior y aplicar el nuevo
                TransactionService.handle_transaction_update(old_transaction_temp, new_transaction)

            logger.info(
                f"Usuario {self.request.user.id} actualizó transacción {new_transaction.id}"
            )

        except Exception as e:
            logger.error(f"Error al actualizar transacción {self.get_object().id}: {str(e)}")
            raise e

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """
        Duplicar una transacción existente
        Opcionalmente se puede modificar la fecha en el body
        """
        original_transaction = self.get_object()

        # Crear copia de la transacción
        duplicated_data = {
            "user": request.user,
            "origin_account": original_transaction.origin_account,
            "destination_account": original_transaction.destination_account,
            "category": original_transaction.category,
            "type": original_transaction.type,
            "base_amount": original_transaction.base_amount,
            "tax_percentage": original_transaction.tax_percentage,
            "total_amount": original_transaction.total_amount,
            "date": request.data.get("date", original_transaction.date),  # Permitir cambiar fecha
            "tag": request.data.get("tag", original_transaction.tag),
            "note": request.data.get("note", original_transaction.note),
        }

        serializer = TransactionSerializer(data=duplicated_data, context={"request": request})

        if serializer.is_valid():
            duplicated_transaction = serializer.save()

            # Actualizar saldos automáticamente (la duplicación es una creación)
            TransactionService.handle_transaction_creation(duplicated_transaction)

            logger.info(
                f"Usuario {request.user.id} duplicó transacción "
                f"{original_transaction.id} -> {duplicated_transaction.id}"
            )

            detail_serializer = TransactionDetailSerializer(duplicated_transaction)
            return Response(
                {
                    "message": "Transacción duplicada exitosamente",
                    "transaction": detail_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        transaction_ids = request.data.get("ids", [])

        if not transaction_ids:
            return Response(
                {"error": 'Debe proporcionar una lista de IDs en el campo "ids".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(transaction_ids, list):
            return Response(
                {"error": 'El campo "ids" debe ser una lista.'}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(id__in=transaction_ids)

        if queryset.count() != len(transaction_ids):
            found_ids = list(queryset.values_list("id", flat=True))
            missing_ids = [tid for tid in transaction_ids if tid not in found_ids]
            return Response(
                {
                    "error": (
                        "Algunas transacciones no fueron encontradas o no pertenecen al usuario."
                    ),
                    "missing_ids": missing_ids,
                    "found_ids": found_ids,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        deleted_count = 0
        errors = []

        for transaction in queryset:
            try:
                TransactionService.handle_transaction_deletion(transaction)
                transaction.delete()
                deleted_count += 1
                logger.info(
                    f"Usuario {request.user.id} eliminó transacción {transaction.id} (bulk delete)"
                )
            except Exception as e:
                errors.append({"transaction_id": transaction.id, "error": str(e)})
                logger.error(
                    f"Error al eliminar transacción {transaction.id} en bulk delete: {str(e)}"
                )

        if errors:
            return Response(
                {
                    "message": (
                        f"Se eliminaron {deleted_count} transacciones, "
                        f"pero hubo {len(errors)} errores."
                    ),
                    "deleted_count": deleted_count,
                    "errors": errors,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": f"Se eliminaron {deleted_count} transacciones exitosamente.",
                "deleted_count": deleted_count,
            },
            status=status.HTTP_200_OK,
        )

    def perform_destroy(self, instance):
        try:
            TransactionService.handle_transaction_deletion(instance)
            instance.delete()

            logger.info(f"Usuario {self.request.user.id} eliminó transacción {instance.id}")

        except Exception as e:
            logger.error(f"Error al eliminar transacción {instance.id}: {str(e)}")
            raise e
