"""
Vistas para gestión de vehículos y SOAT
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from vehicles.models import SOAT, SOATAlert, Vehicle
from vehicles.serializers import (
    SOATAlertSerializer,
    SOATPaymentSerializer,
    SOATSerializer,
    VehicleSerializer,
    VehicleWithSOATSerializer,
)
from vehicles.services import SOATService


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de vehículos
    """

    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar vehículos del usuario autenticado"""
        return Vehicle.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Usar serializer con SOAT para el listado"""
        if self.action == "list":
            return VehicleWithSOATSerializer
        return VehicleSerializer

    def perform_create(self, serializer):
        """Asignar usuario al crear vehículo"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def soats(self, request, pk=None):
        """
        GET /api/vehicles/{id}/soats/
        Listar todos los SOATs de un vehículo
        """
        vehicle = self.get_object()
        soats = vehicle.soats.all()
        serializer = SOATSerializer(soats, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def payment_history(self, request, pk=None):
        """
        GET /api/vehicles/{id}/payment_history/
        Historial de pagos de SOAT del vehículo
        """
        vehicle = self.get_object()
        transactions = SOATService.get_payment_history(vehicle)

        history = []
        for txn in transactions:
            history.append(
                {
                    "id": txn.id,
                    "date": txn.date,
                    "amount": txn.total_amount,
                    "amount_formatted": f"${txn.total_amount / 100:,.2f}",
                    "account": txn.origin_account.name,
                    "category": txn.category.name if txn.category else None,
                    "description": txn.description,
                }
            )

        return Response(
            {
                "vehicle": vehicle.plate,
                "payments": history,
                "total_paid": sum([p["amount"] for p in history]),
            }
        )


class SOATViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de SOAT
    """

    serializer_class = SOATSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar SOATs de los vehículos del usuario"""
        return SOAT.objects.filter(vehicle__user=self.request.user).select_related(
            "vehicle", "payment_transaction"
        )

    def perform_create(self, serializer):
        """Validar que el vehículo pertenezca al usuario"""
        vehicle = serializer.validated_data["vehicle"]
        if vehicle.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            error_message = "El vehículo no te pertenece"
            raise PermissionDenied(error_message)
        serializer.save()

    @action(detail=True, methods=["post"])
    def register_payment(self, request, pk=None):
        """
        POST /api/soats/{id}/register_payment/
        Registrar el pago de un SOAT

        Body:
        {
            "account_id": 1,
            "payment_date": "2025-12-08",
            "notes": "Pago anual SOAT"
        }
        """
        soat = self.get_object()

        serializer = SOATPaymentSerializer(
            data=request.data, context={"request": request, "soat": soat}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = SOATService.register_payment(
                soat=soat,
                account_id=serializer.validated_data["account_id"],
                payment_date=serializer.validated_data["payment_date"],
                notes=serializer.validated_data.get("notes", ""),
            )

            # Refrescar SOAT con datos actualizados
            soat.refresh_from_db()
            soat_serializer = SOATSerializer(soat, context={"request": request})

            return Response(
                {
                    "message": "Pago registrado exitosamente",
                    "soat": soat_serializer.data,
                    "transaction_id": transaction.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """
        POST /api/soats/{id}/update_status/
        Actualizar manualmente el estado del SOAT
        """
        soat = self.get_object()
        soat.update_status()
        serializer = SOATSerializer(soat, context={"request": request})
        return Response(
            {
                "message": "Estado actualizado",
                "soat": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        """
        GET /api/soats/expiring_soon/
        Listar SOATs que están por vencer (próximos 30 días)
        """
        today = timezone.now().date()
        days = int(request.query_params.get("days", 30))

        soats = self.get_queryset().filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=days),
        )

        serializer = self.get_serializer(soats, many=True)
        return Response(
            {
                "count": soats.count(),
                "days_range": days,
                "soats": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def expired(self, request):
        """
        GET /api/soats/expired/
        Listar SOATs vencidos
        """
        today = timezone.now().date()
        soats = self.get_queryset().filter(expiry_date__lt=today)

        serializer = self.get_serializer(soats, many=True)
        return Response(
            {
                "count": soats.count(),
                "soats": serializer.data,
            }
        )


class SOATAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para alertas de SOAT (solo lectura)
    """

    serializer_class = SOATAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar alertas del usuario"""
        queryset = SOATAlert.objects.filter(user=self.request.user).select_related(
            "soat", "soat__vehicle"
        )

        # Filtro por estado de lectura
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")

        return queryset

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """
        POST /api/soat-alerts/{id}/mark_read/
        Marcar alerta como leída
        """
        try:
            alert = SOATService.mark_alert_as_read(pk, request.user)
            serializer = self.get_serializer(alert)
            return Response(
                {
                    "message": "Alerta marcada como leída",
                    "alert": serializer.data,
                }
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        POST /api/soat-alerts/mark_all_read/
        Marcar todas las alertas como leídas
        """
        SOATAlert.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": "Todas las alertas marcadas como leídas"})
