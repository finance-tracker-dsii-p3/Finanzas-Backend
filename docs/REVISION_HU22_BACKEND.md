# Revisión Backend HU-22 - Facturas Personales

**Fecha de revisión:** 2024-01-XX
**Estado:** Implementación completa con mejoras sugeridas

---

## ✅ Criterios de Aceptación - Estado

### CA-01: Crear factura con proveedor, monto, fecha de vencimiento, cuenta sugerida y categoría ✅

**Estado:** ✅ **COMPLETO**

**Implementación:**
- ✅ Modelo `Bill` con todos los campos requeridos:
  - `provider` (CharField, max_length=200)
  - `amount` (DecimalField)
  - `due_date` (DateField)
  - `suggested_account` (ForeignKey a Account, nullable)
  - `category` (ForeignKey a Category, nullable)
- ✅ Validaciones:
  - Cuenta sugerida debe pertenecer al usuario
  - Categoría debe pertenecer al usuario
  - Monto debe ser positivo
- ✅ Serializer `BillSerializer` con validaciones completas
- ✅ Endpoint `POST /api/bills/` funcional

**Evidencia:**
```python
# bills/models.py
class Bill(models.Model):
    provider = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    suggested_account = models.ForeignKey("accounts.Account", ...)
    category = models.ForeignKey("categories.Category", ...)
```

---

### CA-02: Cambios de estado automáticos: pendiente → pagada (al registrar pago) → atrasada (si vence sin pagar) ✅

**Estado:** ✅ **COMPLETO**

**Implementación:**
- ✅ Método `update_status()` en modelo `Bill`:
  - Si tiene `payment_transaction` → `PAID`
  - Si está vencida y no pagada → `OVERDUE`
  - Si no está vencida y no pagada → `PENDING`
- ✅ Actualización automática en `list()`, `pending()`, `overdue()`
- ✅ Al registrar pago, estado cambia automáticamente a `PAID`

**Evidencia:**
```python
# bills/models.py
def update_status(self):
    if self.payment_transaction:
        self.status = self.PAID
    elif self.is_overdue:
        self.status = self.OVERDUE
    else:
        self.status = self.PENDING
```

---

### CA-03: Registrar pago genera movimiento con cuenta y categoría correspondiente ✅

**Estado:** ✅ **COMPLETO**

**Implementación:**
- ✅ Método `BillService.register_payment()`:
  - Valida que la factura no esté pagada
  - Valida que la cuenta pertenezca al usuario
  - Usa categoría de la factura o crea "Servicios"
  - Crea `Transaction` con:
    - `type`: 2 (Expense)
    - `category`: categoría de la factura o "Servicios"
    - `base_amount`: monto en centavos
    - `description`: "Pago factura {provider}"
  - Actualiza saldo de cuenta (`current_balance`)
  - Vincula transacción a la factura (`payment_transaction`)
  - Operación atómica (rollback en errores)
- ✅ Endpoint `POST /api/bills/{id}/register_payment/`

**Evidencia:**
```python
# bills/services.py
def register_payment(bill, account_id, payment_date, notes=""):
    # ... validaciones ...
    txn = Transaction.objects.create(
        user=user,
        origin_account=account,
        category=category,
        type=2,  # Expense
        base_amount=amount_cents,
        date=payment_date,
        description=f"Pago factura {bill.provider}",
    )
    bill.payment_transaction = txn
    account.current_balance -= bill.amount
```

---

### CA-04: Facturas vencidas se marcan automáticamente como "atrasadas" ✅

**Estado:** ✅ **COMPLETO**

**Implementación:**
- ✅ Propiedad `is_overdue` calcula si está vencida
- ✅ Método `update_status()` marca como `OVERDUE` si está vencida
- ✅ Actualización automática en `check_and_create_reminders()`:
  - Si `days_until_due < 0` y no está pagada → `OVERDUE`
- ✅ Actualización automática en `list()`, `pending()`, `overdue()`

**Evidencia:**
```python
# bills/models.py
@property
def is_overdue(self):
    return self.due_date < timezone.now().date() and self.status != self.PAID

def update_status(self):
    # ...
    elif self.is_overdue:
        self.status = self.OVERDUE
```

---

### CA-05: Vista con filtros por estado, proveedor o fecha, más recordatorios ⚠️

**Estado:** ⚠️ **PARCIALMENTE COMPLETO** (falta filtro por fecha)

**Implementación actual:**
- ✅ Filtro por estado: `?status=pending|paid|overdue`
- ✅ Filtro por proveedor: `?provider=Netflix` (búsqueda parcial)
- ✅ Filtro por recurrencia: `?is_recurring=true|false`
- ✅ Filtro por pagado: `?is_paid=true|false`
- ❌ **FALTA:** Filtro por fecha de vencimiento

**Recordatorios:**
- ✅ Endpoint `/api/bill-reminders/` con filtros:
  - `?is_read=true|false`
  - `?reminder_type=upcoming|due_today|overdue`
  - `?bill={id}`

**Mejora sugerida:**
Agregar filtros por fecha:
- `?due_date_from=YYYY-MM-DD` - Facturas que vencen desde esta fecha
- `?due_date_to=YYYY-MM-DD` - Facturas que vencen hasta esta fecha
- `?due_date=YYYY-MM-DD` - Facturas que vencen en esta fecha específica

---

## ✅ Definition of Done - Estado

### DoD-01: Modelo validado con estados y fechas correctas ✅

**Estado:** ✅ **COMPLETO**

**Implementación:**
- ✅ Modelo `Bill` con validaciones en `clean()`
- ✅ Estados: `PENDING`, `PAID`, `OVERDUE`
- ✅ Propiedades calculadas: `days_until_due`, `is_overdue`, `is_near_due`, `is_paid`
- ✅ Método `update_status()` para actualización automática
- ✅ Validación de fechas (due_date)
- ✅ Tests: 5 tests del modelo pasando

---

### DoD-02: Recordatorios automáticos con horario del usuario ⚠️

**Estado:** ⚠️ **PARCIALMENTE COMPLETO** (no usa timezone del usuario)

**Implementación actual:**
- ✅ Comando `check_bill_reminders` para ejecutar con cron
- ✅ Método `BillService.check_and_create_reminders()`:
  - Crea recordatorios: `upcoming`, `due_today`, `overdue`
  - Previene duplicados en 24 horas
  - Integración con `NotificationEngine` (HU-18)
- ⚠️ **PROBLEMA:** Usa `timezone.now().date()` que es timezone del servidor, no del usuario

**Cálculo actual:**
```python
# bills/models.py
@property
def days_until_due(self):
    today = timezone.now().date()  # ❌ Usa timezone del servidor
    delta = self.due_date - today
    return delta.days
```

**Mejora necesaria:**
Similar a HU-21 (SOAT), debería usar el timezone del usuario:
```python
def days_until_due(self, user_tz=None):
    if user_tz:
        user_now = timezone.now().astimezone(user_tz).date()
    else:
        user_now = timezone.now().date()
    delta = self.due_date - user_now
    return delta.days
```

**Impacto:**
- Los recordatorios pueden generarse en el momento incorrecto para usuarios en diferentes timezones
- El cálculo de "días restantes" puede ser incorrecto

---

### DoD-03: Registro único al pagar (sin duplicar movimientos) ✅

**Estado:** ✅ **COMPLETO**

**Implementación:**
- ✅ Validación: `if bill.is_paid: raise ValueError`
- ✅ Relación `OneToOne` entre `Bill` y `Transaction`:
  - `payment_transaction = OneToOneField(Transaction, ...)`
  - Solo puede haber una transacción de pago por factura
- ✅ Operación atómica con `db_transaction.atomic()`
- ✅ Test: `test_register_payment` verifica que no se puede pagar dos veces

**Evidencia:**
```python
# bills/services.py
if bill.is_paid:
    msg = "Esta factura ya está pagada"
    raise ValueError(msg)
```

---

### DoD-04: Interfaz clara, accesible y sin errores visuales ✅

**Estado:** ✅ **COMPLETO** (Backend)

**Implementación:**
- ✅ Endpoints RESTful bien estructurados
- ✅ Serializers con mensajes de error claros
- ✅ Códigos HTTP apropiados (200, 201, 400, 404)
- ✅ Documentación en `docs/HU22_BILLS_POSTMAN.md`
- ✅ Admin interface configurada

**Nota:** La interfaz visual es responsabilidad del frontend.

---

### DoD-05: Pruebas de estados, recordatorios y pagos completadas ✅

**Estado:** ✅ **COMPLETO**

**Tests implementados:**
- ✅ **Modelos (5 tests):**
  - `test_create_bill`
  - `test_days_until_due`
  - `test_is_overdue`
  - `test_is_near_due`
  - `test_update_status`
- ✅ **Servicios (1 test):**
  - `test_register_payment`
- ✅ **API (6 tests):**
  - `test_create_bill`
  - `test_list_bills`
  - `test_register_payment`
  - `test_pending_bills`
  - `test_overdue_bills`
  - `test_mark_reminder_read`
- ✅ **Recordatorios (2 tests):**
  - `test_create_reminder`
  - `test_can_create_reminder`

**Resultado:** 14/14 tests pasando ✅

---

## 📋 Resumen de Implementación

### ✅ Componentes Completos

1. **Modelos:**
   - ✅ `Bill` - Modelo principal con validaciones
   - ✅ `BillReminder` - Recordatorios automáticos

2. **Serializers:**
   - ✅ `BillSerializer` - CRUD completo
   - ✅ `BillListSerializer` - Listado simplificado
   - ✅ `BillPaymentSerializer` - Validación de pagos
   - ✅ `BillReminderSerializer` - Recordatorios

3. **Servicios:**
   - ✅ `BillService.register_payment()` - Registro de pagos
   - ✅ `BillService.check_and_create_reminders()` - Recordatorios automáticos
   - ✅ `BillService.mark_reminder_as_read()` - Marcar como leído

4. **Vistas:**
   - ✅ `BillViewSet` - CRUD + acciones custom
   - ✅ `BillReminderViewSet` - Recordatorios (read-only)

5. **Endpoints:**
   - ✅ `/api/bills/` - CRUD facturas
   - ✅ `/api/bills/{id}/register_payment/` - Registrar pago
   - ✅ `/api/bills/{id}/update_status/` - Actualizar estado
   - ✅ `/api/bills/pending/` - Facturas pendientes
   - ✅ `/api/bills/overdue/` - Facturas atrasadas
   - ✅ `/api/bill-reminders/` - Listar recordatorios
   - ✅ `/api/bill-reminders/{id}/mark_read/` - Marcar leído
   - ✅ `/api/bill-reminders/mark_all_read/` - Marcar todos leídos

6. **Management Command:**
   - ✅ `check_bill_reminders` - Comando para cron

7. **Tests:**
   - ✅ 14 tests completos, todos pasando

8. **Documentación:**
   - ✅ `docs/HU22_BILLS_IMPLEMENTATION_SUMMARY.md`
   - ✅ `docs/HU22_BILLS_POSTMAN.md`

---

## ⚠️ Mejoras Sugeridas

### 1. Filtro por Fecha de Vencimiento (CA-05)

**Prioridad:** Media
**Esfuerzo:** Bajo

**Implementación sugerida:**
```python
# bills/views.py - get_queryset()
due_date_from = self.request.query_params.get("due_date_from")
if due_date_from:
    queryset = queryset.filter(due_date__gte=due_date_from)

due_date_to = self.request.query_params.get("due_date_to")
if due_date_to:
    queryset = queryset.filter(due_date__lte=due_date_to)

due_date = self.request.query_params.get("due_date")
if due_date:
    queryset = queryset.filter(due_date=due_date)
```

---

### 2. Uso de Timezone del Usuario (DoD-02)

**Prioridad:** Alta (similar a HU-21)
**Esfuerzo:** Medio

**Implementación sugerida:**

1. **Modificar `days_until_due` para aceptar timezone:**
```python
# bills/models.py
def days_until_due(self, user_tz=None):
    """Calcula los días restantes hasta el vencimiento usando timezone del usuario"""
    if user_tz:
        try:
            user_now = timezone.now().astimezone(user_tz).date()
        except Exception:
            user_now = timezone.now().date()
    else:
        user_now = timezone.now().date()

    delta = self.due_date - user_now
    return delta.days

@property
def days_until_due_property(self):
    """Propiedad para compatibilidad"""
    return self.days_until_due(user_tz=self._get_user_timezone())
```

2. **Modificar `is_overdue` y `is_near_due`:**
```python
def is_overdue(self, user_tz=None):
    """Verifica si la factura está vencida usando timezone del usuario"""
    days = self.days_until_due(user_tz=user_tz)
    return days is not None and days < 0

def is_near_due(self, user_tz=None):
    """Verifica si está próxima a vencer usando timezone del usuario"""
    days = self.days_until_due(user_tz=user_tz)
    return 0 <= days <= self.reminder_days_before and self.status == self.PENDING
```

3. **Modificar `check_and_create_reminders` para usar timezone:**
```python
# bills/services.py
def check_and_create_reminders():
    bills = Bill.objects.select_related("user", "user__notification_preferences").filter(...)

    for bill in bills:
        user = bill.user
        user_tz = user.notification_preferences.timezone_object  # Obtener timezone

        days_until_due = bill.days_until_due(user_tz=user_tz)  # Usar timezone

        # ... resto de la lógica ...
```

4. **Modificar serializers para usar timezone:**
```python
# bills/serializers.py
def get_days_until_due(self, obj):
    user_tz = self.context["request"].user.notification_preferences.timezone_object
    return obj.days_until_due(user_tz=user_tz)
```

---

## ✅ Conclusión

### Estado General: ✅ **COMPLETO CON MEJORAS SUGERIDAS**

**Criterios de Aceptación:**
- ✅ CA-01: Crear factura - **COMPLETO**
- ✅ CA-02: Cambios de estado automáticos - **COMPLETO**
- ✅ CA-03: Registrar pago genera movimiento - **COMPLETO**
- ✅ CA-04: Facturas vencidas marcadas como atrasadas - **COMPLETO**
- ⚠️ CA-05: Vista con filtros - **PARCIAL** (falta filtro por fecha)

**Definition of Done:**
- ✅ DoD-01: Modelo validado - **COMPLETO**
- ⚠️ DoD-02: Recordatorios con timezone del usuario - **PARCIAL** (usa timezone del servidor)
- ✅ DoD-03: Registro único - **COMPLETO**
- ✅ DoD-04: Interfaz clara - **COMPLETO**
- ✅ DoD-05: Pruebas completas - **COMPLETO**

### Recomendaciones

1. **Alta prioridad:** Implementar uso de timezone del usuario (similar a HU-21)
2. **Media prioridad:** Agregar filtros por fecha de vencimiento
3. **Baja prioridad:** Agregar tests para timezone (si se implementa la mejora)

### Próximos Pasos

1. Implementar mejora de timezone (similar a HU-21)
2. Agregar filtros por fecha
3. Crear tests adicionales para las mejoras
4. Documentar cambios

---

**La implementación está funcional y lista para producción, pero se recomienda implementar las mejoras sugeridas para una mejor experiencia de usuario.**
