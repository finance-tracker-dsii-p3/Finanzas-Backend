"""
Vistas para gestión de facturas personales
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from bills.models import Bill, BillReminder
from bills.serializers import (
    BillSerializer,
    BillListSerializer,
    BillPaymentSerializer,
    BillReminderSerializer,
)
from bills.services import BillService


class BillViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de facturas
    
    Endpoints:
    - list: Listar facturas con filtros
    - create: Crear factura
    - retrieve: Ver detalle de factura
    - update/partial_update: Actualizar factura
    - destroy: Eliminar factura
    - register_payment: Registrar pago de factura
    - update_status: Actualizar estado manualmente
    - pending: Facturas pendientes
    - overdue: Facturas atrasadas
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar facturas del usuario autenticado"""
        queryset = Bill.objects.filter(user=self.request.user)
        
        # Filtros por query params
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        provider_filter = self.request.query_params.get("provider")
        if provider_filter:
            queryset = queryset.filter(provider__icontains=provider_filter)
        
        is_recurring = self.request.query_params.get("is_recurring")
        if is_recurring is not None:
            queryset = queryset.filter(is_recurring=is_recurring.lower() == "true")
        
        is_paid = self.request.query_params.get("is_paid")
        if is_paid is not None:
            if is_paid.lower() == "true":
                queryset = queryset.exclude(payment_transaction=None)
            else:
                queryset = queryset.filter(payment_transaction=None)
        
        return queryset.select_related(
            "suggested_account",
            "category",
            "payment_transaction"
        )
    
    def get_serializer_class(self):
        """Usar serializer simplificado para list"""
        if self.action == "list":
            return BillListSerializer
        return BillSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Lista facturas actualizando estados automáticamente
        """
        # Actualizar estados de todas las facturas no pagadas antes de listar
        unpaid_bills = Bill.objects.filter(
            user=request.user,
            payment_transaction__isnull=True
        )
        for bill in unpaid_bills:
            bill.update_status()
            bill.save(update_fields=["status"])
        
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Asociar factura al usuario autenticado"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=["post"])
    def register_payment(self, request, pk=None):
        """
        Registra el pago de una factura
        
        POST /api/bills/{id}/register_payment/
        Body: {account_id, payment_date, notes}
        """
        bill = self.get_object()
        
        serializer = BillPaymentSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            transaction = BillService.register_payment(
                bill=bill,
                account_id=serializer.validated_data["account_id"],
                payment_date=serializer.validated_data["payment_date"],
                notes=serializer.validated_data.get("notes", "")
            )
            
            # Refrescar la factura
            bill.refresh_from_db()
            
            return Response({
                "message": "Pago registrado exitosamente",
                "transaction_id": transaction.id,
                "bill": BillSerializer(bill, context={"request": request}).data
            }, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """
        Actualiza el estado de la factura manualmente
        
        POST /api/bills/{id}/update_status/
        """
        bill = self.get_object()
        bill.update_status()
        bill.save(update_fields=["status"])
        
        return Response({
            "id": bill.id,
            "status": bill.status,
            "days_until_due": bill.days_until_due,
            "is_paid": bill.is_paid
        })
    
    @action(detail=False, methods=["get"])
    def pending(self, request):
        """
        Obtiene todas las facturas pendientes
        
        GET /api/bills/pending/
        """
        # Actualizar estados de todas las facturas no pagadas
        unpaid_bills = self.get_queryset().filter(payment_transaction__isnull=True)
        for bill in unpaid_bills:
            bill.update_status()
            bill.save(update_fields=["status"])
        
        bills = self.get_queryset().filter(status=Bill.PENDING)
        serializer = BillListSerializer(bills, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """
        Obtiene todas las facturas atrasadas
        
        GET /api/bills/overdue/
        """
        # Actualizar estados de todas las facturas no pagadas
        unpaid_bills = self.get_queryset().filter(payment_transaction__isnull=True)
        for bill in unpaid_bills:
            bill.update_status()
            bill.save(update_fields=["status"])
        
        bills = self.get_queryset().filter(status=Bill.OVERDUE)
        serializer = BillListSerializer(bills, many=True)
        return Response(serializer.data)


class BillReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para recordatorios de facturas (solo lectura)
    
    Endpoints:
    - list: Listar recordatorios con filtros
    - retrieve: Ver detalle de recordatorio
    - mark_read: Marcar recordatorio como leído
    - mark_all_read: Marcar todos como leídos
    """
    
    serializer_class = BillReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar recordatorios del usuario autenticado"""
        queryset = BillReminder.objects.filter(user=self.request.user)
        
        # Filtros por query params
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")
        
        reminder_type = self.request.query_params.get("reminder_type")
        if reminder_type:
            queryset = queryset.filter(reminder_type=reminder_type)
        
        bill_id = self.request.query_params.get("bill")
        if bill_id:
            queryset = queryset.filter(bill_id=bill_id)
        
        return queryset.select_related("bill")
    
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """
        Marca un recordatorio como leído
        
        POST /api/bill-reminders/{id}/mark_read/
        """
        reminder = self.get_object()
        BillService.mark_reminder_as_read(reminder)
        
        return Response({
            "id": reminder.id,
            "is_read": reminder.is_read,
            "read_at": reminder.read_at,
            "message": "Recordatorio marcado como leído"
        })
    
    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        Marca todos los recordatorios como leídos
        
        POST /api/bill-reminders/mark_all_read/
        """
        unread_reminders = self.get_queryset().filter(is_read=False)
        
        for reminder in unread_reminders:
            BillService.mark_reminder_as_read(reminder)
        
        return Response({
            "message": "Todos los recordatorios han sido marcados como leídos",
            "updated_count": unread_reminders.count()
        })
