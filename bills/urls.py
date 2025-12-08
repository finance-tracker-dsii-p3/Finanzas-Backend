"""
URLs para gestión de facturas
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from bills.views import BillViewSet, BillReminderViewSet

router = DefaultRouter()

# /api/bills/ - Gestión de facturas de servicios y suscripciones
# GET    /api/bills/              - Listar facturas (filtros: status, provider, is_recurring, is_paid)
# POST   /api/bills/              - Crear factura
# GET    /api/bills/{id}/         - Ver detalle de factura
# PUT    /api/bills/{id}/         - Actualizar factura completa
# PATCH  /api/bills/{id}/         - Actualizar factura parcial
# DELETE /api/bills/{id}/         - Eliminar factura
# POST   /api/bills/{id}/register_payment/  - Registrar pago (crea transacción)
# POST   /api/bills/{id}/update_status/     - Actualizar estado manualmente
# GET    /api/bills/pending/      - Listar facturas pendientes
# GET    /api/bills/overdue/      - Listar facturas atrasadas
router.register(r"bills", BillViewSet, basename="bill")

# /api/bill-reminders/ - Gestión de recordatorios de facturas (solo lectura)
# GET  /api/bill-reminders/           - Listar recordatorios (filtros: is_read, reminder_type, bill)
# GET  /api/bill-reminders/{id}/      - Ver detalle de recordatorio
# POST /api/bill-reminders/{id}/mark_read/     - Marcar recordatorio como leído
# POST /api/bill-reminders/mark_all_read/      - Marcar todos como leídos
router.register(r"bill-reminders", BillReminderViewSet, basename="bill-reminder")

urlpatterns = router.urls
