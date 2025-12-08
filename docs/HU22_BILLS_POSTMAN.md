# HU-22: Facturas Personales - Documentación API con Postman

## Descripción
API para gestión de facturas de servicios y suscripciones personales - Permite registrar facturas, cambiar su estado automáticamente (pendiente/pagada/atrasada), registrar pagos con contabilidad automática y recibir recordatorios de vencimiento.

## URL Base
```
http://localhost:8000/api/
```

## Autenticación
Todas las solicitudes requieren autenticación mediante Token:

```
Headers:
Authorization: Token YOUR_AUTH_TOKEN_HERE
```

---

## 1. Gestión de Facturas

### 1.1 Crear Factura
**POST** `/api/bills/`

**Body (JSON):**
```json
{
  "provider": "Netflix",
  "amount": 45000.00,
  "due_date": "2024-02-25",
  "suggested_account": 3,
  "category": 5,
  "reminder_days_before": 3,
  "description": "Suscripción Premium",
  "is_recurring": true
}
```

**Campos:**
- `provider` (requerido): Nombre del proveedor (ej: Netflix, EPM, Claro, Internet Hogar)
- `amount` (requerido): Monto de la factura en COP
- `due_date` (requerido): Fecha de vencimiento (YYYY-MM-DD)
- `suggested_account` (opcional): ID de la cuenta sugerida para el pago
- `category` (opcional): ID de la categoría de gasto
- `reminder_days_before` (opcional, default: 3): Días antes del vencimiento para recordatorio
- `description` (opcional): Notas adicionales
- `is_recurring` (opcional, default: false): Si es una factura recurrente mensual

**Respuesta Exitosa (201):**
```json
{
  "id": 15,
  "provider": "Netflix",
  "amount": "45000.00",
  "amount_formatted": "$45,000",
  "due_date": "2024-02-25",
  "suggested_account": 3,
  "suggested_account_info": {
    "id": 3,
    "name": "Cuenta Ahorros",
    "bank_name": "Bancolombia",
    "current_balance": 1500000.00
  },
  "category": 5,
  "category_info": {
    "id": 5,
    "name": "Entretenimiento",
    "color": "#10B981",
    "icon": "fa-film"
  },
  "status": "pending",
  "payment_transaction": null,
  "payment_info": null,
  "reminder_days_before": 3,
  "description": "Suscripción Premium",
  "is_recurring": true,
  "days_until_due": 17,
  "is_overdue": false,
  "is_near_due": false,
  "is_paid": false,
  "created_at": "2024-02-08T10:30:00Z",
  "updated_at": "2024-02-08T10:30:00Z"
}
```

### 1.2 Listar Facturas
**GET** `/api/bills/`

**Query Parameters:**
- `status`: Filtrar por estado (`pending`, `paid`, `overdue`)
- `provider`: Buscar por proveedor (búsqueda parcial)
- `is_recurring`: Filtrar por recurrentes (`true`/`false`)
- `is_paid`: Filtrar por pagadas (`true`/`false`)

**Ejemplos:**
```
GET /api/bills/?status=pending
GET /api/bills/?provider=Netflix
GET /api/bills/?is_recurring=true
GET /api/bills/?is_paid=false&status=overdue
```

**Respuesta (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "provider": "Netflix",
      "amount": "45000.00",
      "amount_formatted": "$45,000",
      "due_date": "2024-02-25",
      "status": "pending",
      "days_until_due": 17,
      "is_paid": false,
      "is_recurring": true,
      "created_at": "2024-02-08T10:30:00Z"
    },
    {
      "id": 12,
      "provider": "Internet Hogar",
      "amount": "95000.00",
      "amount_formatted": "$95,000",
      "due_date": "2024-02-10",
      "status": "pending",
      "days_until_due": 2,
      "is_paid": false,
      "is_recurring": true,
      "created_at": "2024-02-01T15:00:00Z"
    }
  ]
}
```

### 1.3 Ver Detalle de Factura
**GET** `/api/bills/{id}/`

**Respuesta (200):**
```json
{
  "id": 15,
  "provider": "Netflix",
  "amount": "45000.00",
  "amount_formatted": "$45,000",
  "due_date": "2024-02-25",
  "suggested_account": 3,
  "suggested_account_info": {
    "id": 3,
    "name": "Cuenta Ahorros",
    "bank_name": "Bancolombia",
    "current_balance": 1500000.00
  },
  "category": 5,
  "category_info": {
    "id": 5,
    "name": "Entretenimiento",
    "color": "#10B981",
    "icon": "fa-film"
  },
  "status": "pending",
  "payment_transaction": null,
  "payment_info": null,
  "reminder_days_before": 3,
  "description": "Suscripción Premium",
  "is_recurring": true,
  "days_until_due": 17,
  "is_overdue": false,
  "is_near_due": false,
  "is_paid": false,
  "created_at": "2024-02-08T10:30:00Z",
  "updated_at": "2024-02-08T10:30:00Z"
}
```

### 1.4 Actualizar Factura
**PUT/PATCH** `/api/bills/{id}/`

**Body (JSON):**
```json
{
  "reminder_days_before": 5,
  "description": "Suscripción Premium - Familiar"
}
```

**Respuesta (200):** Retorna la factura actualizada

### 1.5 Eliminar Factura
**DELETE** `/api/bills/{id}/`

**Respuesta (204):** Sin contenido

### 1.6 Registrar Pago de Factura ⭐
**POST** `/api/bills/{id}/register_payment/`

Registra el pago de la factura, creando automáticamente:
- Transacción en la app `transactions`
- Actualización del saldo de la cuenta
- Categoría "Servicios" si no se especificó categoría
- Cambio de estado a "paid"

**Body (JSON):**
```json
{
  "account_id": 3,
  "payment_date": "2024-02-08",
  "notes": "Pago factura Netflix febrero"
}
```

**Campos:**
- `account_id` (requerido): ID de la cuenta desde la cual se paga
- `payment_date` (requerido): Fecha del pago (YYYY-MM-DD)
- `notes` (opcional): Notas adicionales sobre el pago

**Respuesta Exitosa (201):**
```json
{
  "message": "Pago registrado exitosamente",
  "transaction_id": 78,
  "bill": {
    "id": 15,
    "provider": "Netflix",
    "amount": "45000.00",
    "amount_formatted": "$45,000",
    "status": "paid",
    "is_paid": true,
    "payment_transaction": 78,
    "payment_info": {
      "id": 78,
      "date": "2024-02-08",
      "amount": 45000.00,
      "account": "Cuenta Ahorros"
    },
    "days_until_due": 17,
    "is_overdue": false
  }
}
```

**Errores Comunes:**
- `400`: La factura ya está pagada
- `400`: La cuenta no existe o no te pertenece
- `404`: Factura no encontrada

### 1.7 Actualizar Estado de Factura
**POST** `/api/bills/{id}/update_status/`

Fuerza la actualización del estado de la factura basándose en:
- Si tiene pago → `paid`
- Si está vencida y sin pagar → `overdue`
- Si no está vencida y sin pagar → `pending`

**Body:** Vacío (no requiere body)

**Respuesta (200):**
```json
{
  "id": 15,
  "status": "pending",
  "days_until_due": 17,
  "is_paid": false
}
```

### 1.8 Ver Facturas Pendientes
**GET** `/api/bills/pending/`

Obtiene todas las facturas con estado `pending`.

**Respuesta (200):**
```json
[
  {
    "id": 15,
    "provider": "Netflix",
    "amount": "45000.00",
    "amount_formatted": "$45,000",
    "due_date": "2024-02-25",
    "status": "pending",
    "days_until_due": 17,
    "is_paid": false,
    "is_recurring": true,
    "created_at": "2024-02-08T10:30:00Z"
  }
]
```

### 1.9 Ver Facturas Atrasadas
**GET** `/api/bills/overdue/`

Obtiene todas las facturas con estado `overdue` (vencidas sin pagar).

**Respuesta (200):**
```json
[
  {
    "id": 10,
    "provider": "EPM",
    "amount": "120000.00",
    "amount_formatted": "$120,000",
    "due_date": "2024-02-05",
    "status": "overdue",
    "days_until_due": -3,
    "is_paid": false,
    "is_recurring": true,
    "created_at": "2024-01-15T08:00:00Z"
  }
]
```

---

## 2. Gestión de Recordatorios

### 2.1 Listar Recordatorios
**GET** `/api/bill-reminders/`

**Query Parameters:**
- `is_read`: Filtrar por leídos (`true`/`false`)
- `reminder_type`: Filtrar por tipo (`upcoming`, `due_today`, `overdue`)
- `bill`: Filtrar por ID de factura

**Ejemplos:**
```
GET /api/bill-reminders/?is_read=false
GET /api/bill-reminders/?reminder_type=upcoming
GET /api/bill-reminders/?bill=15&is_read=false
```

**Respuesta (200):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 25,
      "bill": 12,
      "bill_info": {
        "id": 12,
        "provider": "Internet Hogar",
        "amount": 95000.00,
        "amount_formatted": "$95,000",
        "due_date": "2024-02-10",
        "status": "pending"
      },
      "reminder_type": "upcoming",
      "reminder_type_display": "Próxima a vencer",
      "message": "La factura de Internet Hogar vence en 2 días ($95,000)",
      "is_read": false,
      "read_at": null,
      "created_at": "2024-02-08T08:00:00Z"
    }
  ]
}
```

### 2.2 Ver Detalle de Recordatorio
**GET** `/api/bill-reminders/{id}/`

**Respuesta (200):**
```json
{
  "id": 25,
  "bill": 12,
  "bill_info": {
    "id": 12,
    "provider": "Internet Hogar",
    "amount": 95000.00,
    "amount_formatted": "$95,000",
    "due_date": "2024-02-10",
    "status": "pending"
  },
  "reminder_type": "upcoming",
  "reminder_type_display": "Próxima a vencer",
  "message": "La factura de Internet Hogar vence en 2 días ($95,000)",
  "is_read": false,
  "read_at": null,
  "created_at": "2024-02-08T08:00:00Z"
}
```

### 2.3 Marcar Recordatorio como Leído
**POST** `/api/bill-reminders/{id}/mark_read/`

**Body:** Vacío

**Respuesta (200):**
```json
{
  "id": 25,
  "is_read": true,
  "read_at": "2024-02-08T14:30:00Z",
  "message": "Recordatorio marcado como leído"
}
```

### 2.4 Marcar Todos los Recordatorios como Leídos
**POST** `/api/bill-reminders/mark_all_read/`

**Body:** Vacío

**Respuesta (200):**
```json
{
  "message": "Todos los recordatorios han sido marcados como leídos",
  "updated_count": 5
}
```

---

## 3. Estados de las Facturas

El sistema maneja 3 estados automáticos:

| Estado | Descripción | Condición | Color sugerido |
|--------|-------------|-----------|----------------|
| `pending` | Pendiente | No pagada y no vencida | Amarillo |
| `paid` | Pagada | Tiene transacción de pago | Verde |
| `overdue` | Atrasada | Vencida y sin pagar | Rojo |

**Transiciones automáticas:**
```
pending → paid (al registrar pago)
pending → overdue (al vencer sin pagar)
overdue → paid (al registrar pago tardío)
```

---

## 4. Tipos de Recordatorios

El sistema genera 3 tipos de recordatorios automáticos:

| Tipo | Cuándo se genera | Mensaje de ejemplo |
|------|------------------|-------------------|
| `upcoming` | N días antes del vencimiento | "La factura de {proveedor} vence en {días} días (${monto})" |
| `due_today` | El día del vencimiento | "La factura de {proveedor} vence hoy (${monto})" |
| `overdue` | Después del vencimiento sin pagar | "La factura de {proveedor} está atrasada {días} días (${monto})" |

---

## 5. Comando Cron para Recordatorios Automáticos

Para generar recordatorios automáticos diariamente, ejecuta:

```bash
python manage.py check_bill_reminders
```

**Programación sugerida (crontab):**
```bash
# Ejecutar todos los días a las 8:00 AM
0 8 * * * cd /ruta/proyecto && python manage.py check_bill_reminders
```

**Windows Task Scheduler:**
```powershell
# Crear tarea programada
schtasks /create /tn "Bill Reminders" /tr "python C:\ruta\manage.py check_bill_reminders" /sc daily /st 08:00
```

---

## 6. Flujo Completo de Uso

### Paso 1: Crear Factura
```http
POST /api/bills/
{
  "provider": "Internet Hogar",
  "amount": 95000.00,
  "due_date": "2024-02-25",
  "suggested_account": 3,
  "category": 8,
  "reminder_days_before": 3,
  "is_recurring": true
}
```

### Paso 2: Ver Facturas Pendientes
```http
GET /api/bills/pending/
```

### Paso 3: Ver Recordatorios No Leídos
```http
GET /api/bill-reminders/?is_read=false
```

### Paso 4: Registrar Pago
```http
POST /api/bills/15/register_payment/
{
  "account_id": 3,
  "payment_date": "2024-02-08",
  "notes": "Pago factura Internet febrero"
}
```

### Paso 5: Verificar Estado
```http
GET /api/bills/15/
```

---

## 7. Validaciones y Reglas de Negocio

1. **Una factura solo puede pagarse una vez**
   - El endpoint `register_payment` rechaza pagos duplicados

2. **La categoría "Servicios" se crea automáticamente**
   - Si no se especifica categoría, se crea al primer pago

3. **Los recordatorios se generan automáticamente**
   - Se evitan duplicados (un recordatorio del mismo tipo cada 24 horas)

4. **El estado se actualiza automáticamente**
   - Al registrar pago, crear factura, o ejecutar el comando cron

5. **Los pagos se registran como transacciones**
   - Se crea automáticamente en la app `transactions`
   - Se actualiza el saldo de la cuenta
   - Se reduce el balance en la moneda de la cuenta

6. **Las fechas de vencimiento se monitorean**
   - El sistema verifica diariamente facturas próximas a vencer
   - Las facturas vencidas cambian automáticamente a `overdue`

---

## 8. Ejemplos de Casos de Uso

### Caso 1: Suscripción Mensual (Netflix)
```json
{
  "provider": "Netflix",
  "amount": 45000.00,
  "due_date": "2024-02-25",
  "suggested_account": 3,
  "category": 5,
  "is_recurring": true,
  "description": "Plan Premium - 4 pantallas"
}
```

### Caso 2: Servicio Público (EPM)
```json
{
  "provider": "EPM",
  "amount": 120000.00,
  "due_date": "2024-02-15",
  "suggested_account": 1,
  "category": 10,
  "reminder_days_before": 5,
  "is_recurring": true,
  "description": "Agua, luz, gas"
}
```

### Caso 3: Telefonía Móvil
```json
{
  "provider": "Claro",
  "amount": 65000.00,
  "due_date": "2024-02-20",
  "suggested_account": 2,
  "category": 11,
  "reminder_days_before": 3,
  "is_recurring": true
}
```

### Caso 4: Internet Hogar
```json
{
  "provider": "Internet Hogar",
  "amount": 95000.00,
  "due_date": "2024-02-10",
  "suggested_account": 1,
  "category": 11,
  "is_recurring": true
}
```

---

## 9. Errores Comunes

### Error 400: Factura ya pagada
```json
{
  "error": "Esta factura ya está pagada"
}
```
**Solución:** Verificar `is_paid` antes de intentar registrar pago

### Error 400: Cuenta no existe
```json
{
  "error": "La cuenta no existe o no te pertenece"
}
```
**Solución:** Verificar ID de cuenta y propiedad

### Error 400: Monto inválido
```json
{
  "amount": ["El monto debe ser mayor a cero"]
}
```
**Solución:** Asegurar que el monto sea positivo

### Error 404: Factura no encontrada
```json
{
  "detail": "No encontrado."
}
```
**Solución:** Verificar ID de la factura

---

## 10. Colección Postman

### Variables de Entorno
```json
{
  "base_url": "http://localhost:8000/api",
  "token": "YOUR_AUTH_TOKEN",
  "bill_id": "15",
  "account_id": "3",
  "reminder_id": "25"
}
```

### Headers Globales
```
Authorization: Token {{token}}
Content-Type: application/json
```

### Tests Sugeridos para Postman

#### Test 1: Crear Factura
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Bill created successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.provider).to.eql("Netflix");
    pm.expect(jsonData.status).to.eql("pending");
    pm.environment.set("bill_id", jsonData.id);
});
```

#### Test 2: Registrar Pago
```javascript
pm.test("Payment registered successfully", function () {
    pm.response.to.have.status(201);
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include("exitosamente");
    pm.expect(jsonData.bill.status).to.eql("paid");
    pm.environment.set("transaction_id", jsonData.transaction_id);
});
```

---

## 11. Integración con Otras Apps

### Con `transactions`
- Al registrar pago se crea `Transaction` con tipo=2 (Expense)
- Se vincula con `Bill.payment_transaction` (OneToOne)
- El monto se convierte a centavos para el sistema interno

### Con `accounts`
- Se actualiza `Account.current_balance` al pagar
- Se valida propiedad de la cuenta
- Se usa la cuenta sugerida como recordatorio

### Con `categories`
- Se puede especificar categoría al crear factura
- Si no se especifica, se crea "Servicios" automáticamente
- La categoría se asigna a la transacción de pago

---

## 12. Buenas Prácticas

1. **Siempre especifica cuenta y categoría sugeridas**
   - Facilita el proceso de pago posterior
   - Mantiene consistencia en la contabilidad

2. **Usa `is_recurring` para facturas mensuales**
   - Ayuda a identificar gastos fijos
   - Útil para proyecciones y presupuestos

3. **Configura `reminder_days_before` apropiadamente**
   - 3-5 días para servicios básicos
   - 7+ días para facturas de mayor monto

4. **Revisa facturas atrasadas regularmente**
   - Endpoint: `GET /api/bills/overdue/`
   - Evita multas e intereses

5. **Marca recordatorios como leídos**
   - Mantén tu sistema de notificaciones limpio
   - Usa `mark_all_read` periódicamente

---

## Conclusión

Esta API permite gestionar completamente el ciclo de vida de las facturas personales:
- ✅ Registro de facturas con datos completos
- ✅ Estados automáticos (pendiente/pagada/atrasada)
- ✅ Registro automatizado de pagos con contabilidad
- ✅ Recordatorios automáticos configurables
- ✅ Filtros y búsquedas avanzadas
- ✅ Integración completa con transacciones y cuentas
- ✅ Historial de pagos por factura

**¿Necesitas más ayuda?** Consulta la documentación general en `/docs/API_REFERENCE.md`
