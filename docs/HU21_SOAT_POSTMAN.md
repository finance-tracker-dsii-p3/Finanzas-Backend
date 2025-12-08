# HU-21: SOAT - Documentación API con Postman

## Descripción
API para gestión de SOAT (Seguro Obligatorio de Accidentes de Tránsito) - Permite registrar vehículos, administrar pólizas SOAT, registrar pagos, recibir alertas automáticas de vencimiento y consultar historial.

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

## 1. Gestión de Vehículos

### 1.1 Crear Vehículo
**POST** `/api/vehicles/`

**Body (JSON):**
```json
{
  "plate": "ABC123",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "description": "Vehículo familiar"
}
```

**Respuesta Exitosa (201):**
```json
{
  "id": 1,
  "plate": "ABC123",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "description": "Vehículo familiar",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 1.2 Listar Vehículos
**GET** `/api/vehicles/`

**Respuesta (200):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "plate": "ABC123",
      "brand": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "description": "Vehículo familiar",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "active_soat": {
        "id": 5,
        "issue_date": "2024-01-01",
        "expiry_date": "2025-01-01",
        "cost": "500000.00",
        "status": "vigente",
        "days_until_expiry": 120,
        "is_paid": true
      }
    }
  ]
}
```

### 1.3 Ver Detalle de Vehículo
**GET** `/api/vehicles/{id}/`

**Respuesta (200):**
```json
{
  "id": 1,
  "plate": "ABC123",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "description": "Vehículo familiar",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 1.4 Actualizar Vehículo
**PUT/PATCH** `/api/vehicles/{id}/`

**Body (JSON):**
```json
{
  "description": "Vehículo de trabajo",
  "is_active": true
}
```

### 1.5 Eliminar Vehículo
**DELETE** `/api/vehicles/{id}/`

**Respuesta (204):** Sin contenido

### 1.6 Ver SOATs de un Vehículo
**GET** `/api/vehicles/{id}/soats/`

**Respuesta (200):**
```json
[
  {
    "id": 5,
    "issue_date": "2024-01-01",
    "expiry_date": "2025-01-01",
    "cost": "500000.00",
    "insurance_company": "Seguros SURA",
    "policy_number": "POL123456",
    "status": "vigente",
    "is_paid": true,
    "days_until_expiry": 120,
    "payment_info": {
      "id": 45,
      "date": "2024-01-01",
      "amount": "500000.00"
    }
  }
]
```

### 1.7 Ver Historial de Pagos de SOAT (de un vehículo)
**GET** `/api/vehicles/{id}/payment_history/`

**Respuesta (200):**
```json
[
  {
    "year": 2024,
    "soat_id": 5,
    "issue_date": "2024-01-01",
    "expiry_date": "2025-01-01",
    "cost": "500000.00",
    "paid": true,
    "payment_date": "2024-01-01",
    "transaction_id": 45
  },
  {
    "year": 2023,
    "soat_id": 3,
    "issue_date": "2023-01-01",
    "expiry_date": "2024-01-01",
    "cost": "450000.00",
    "paid": true,
    "payment_date": "2023-01-02",
    "transaction_id": 23
  }
]
```

---

## 2. Gestión de SOAT

### 2.1 Crear SOAT
**POST** `/api/soats/`

**Body (JSON):**
```json
{
  "vehicle": 1,
  "issue_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "cost": 500000.00,
  "insurance_company": "Seguros SURA",
  "policy_number": "POL123456",
  "alert_days_before": 30
}
```

**Campos:**
- `vehicle` (requerido): ID del vehículo
- `issue_date` (requerido): Fecha de emisión (YYYY-MM-DD)
- `expiry_date` (requerido): Fecha de vencimiento (YYYY-MM-DD)
- `cost` (requerido): Costo del SOAT en COP
- `insurance_company` (opcional): Aseguradora
- `policy_number` (opcional): Número de póliza
- `alert_days_before` (opcional, default: 30): Días antes del vencimiento para alertar

**Respuesta Exitosa (201):**
```json
{
  "id": 5,
  "vehicle": 1,
  "vehicle_info": {
    "id": 1,
    "plate": "ABC123",
    "brand": "Toyota",
    "model": "Corolla"
  },
  "issue_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "cost": "500000.00",
  "cost_formatted": "$500,000",
  "insurance_company": "Seguros SURA",
  "policy_number": "POL123456",
  "alert_days_before": 30,
  "status": "vigente",
  "is_paid": false,
  "days_until_expiry": 365,
  "is_expired": false,
  "is_near_expiry": false,
  "payment_transaction": null,
  "created_at": "2024-01-01T15:30:00Z"
}
```

### 2.2 Listar SOATs
**GET** `/api/soats/`

**Query Parameters:**
- `status`: Filtrar por estado (`vigente`, `por_vencer`, `vencido`, `pendiente_pago`, `atrasado`)
- `vehicle`: Filtrar por ID de vehículo
- `is_paid`: Filtrar por pagados (`true`/`false`)

**Ejemplos:**
```
GET /api/soats/?status=vigente
GET /api/soats/?vehicle=1
GET /api/soats/?is_paid=false
GET /api/soats/?status=por_vencer&is_paid=false
```

**Respuesta (200):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "vehicle_info": {
        "id": 1,
        "plate": "ABC123",
        "brand": "Toyota",
        "model": "Corolla"
      },
      "issue_date": "2024-01-01",
      "expiry_date": "2025-01-01",
      "cost": "500000.00",
      "cost_formatted": "$500,000",
      "status": "vigente",
      "is_paid": true,
      "days_until_expiry": 120,
      "payment_info": {
        "id": 45,
        "date": "2024-01-01",
        "amount": "500000.00"
      }
    }
  ]
}
```

### 2.3 Ver Detalle de SOAT
**GET** `/api/soats/{id}/`

**Respuesta (200):**
```json
{
  "id": 5,
  "vehicle": 1,
  "vehicle_info": {
    "id": 1,
    "plate": "ABC123",
    "brand": "Toyota",
    "model": "Corolla"
  },
  "issue_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "cost": "500000.00",
  "cost_formatted": "$500,000",
  "insurance_company": "Seguros SURA",
  "policy_number": "POL123456",
  "alert_days_before": 30,
  "status": "vigente",
  "is_paid": true,
  "days_until_expiry": 120,
  "is_expired": false,
  "is_near_expiry": false,
  "payment_transaction": 45,
  "payment_info": {
    "id": 45,
    "date": "2024-01-01",
    "amount": "500000.00",
    "account": "Cuenta Bancolombia"
  },
  "created_at": "2024-01-01T15:30:00Z",
  "updated_at": "2024-01-01T15:30:00Z"
}
```

### 2.4 Actualizar SOAT
**PUT/PATCH** `/api/soats/{id}/`

**Body (JSON):**
```json
{
  "alert_days_before": 45,
  "insurance_company": "Seguros Bolívar"
}
```

### 2.5 Registrar Pago de SOAT ⭐
**POST** `/api/soats/{id}/register_payment/`

Registra el pago del SOAT, creando automáticamente:
- Transacción en la app `transactions`
- Actualización del saldo de la cuenta
- Categoría "Seguros" (si no existe)
- Cambio de estado del SOAT

**Body (JSON):**
```json
{
  "account_id": 3,
  "payment_date": "2024-01-15",
  "notes": "Pago SOAT 2024"
}
```

**Campos:**
- `account_id` (requerido): ID de la cuenta desde la cual se paga
- `payment_date` (requerido): Fecha del pago (YYYY-MM-DD)
- `notes` (opcional): Notas adicionales

**Respuesta Exitosa (201):**
```json
{
  "message": "Pago registrado exitosamente",
  "transaction_id": 45,
  "soat": {
    "id": 5,
    "status": "vigente",
    "is_paid": true,
    "payment_info": {
      "id": 45,
      "date": "2024-01-15",
      "amount": "500000.00"
    }
  }
}
```

**Errores Comunes:**
- `400`: El SOAT ya está pagado
- `400`: La cuenta no existe o no te pertenece
- `404`: SOAT no encontrado

### 2.6 Actualizar Estado de SOAT
**POST** `/api/soats/{id}/update_status/`

Fuerza la actualización del estado del SOAT basándose en fechas y pago.

**Body:** Vacío (no requiere body)

**Respuesta (200):**
```json
{
  "id": 5,
  "status": "por_vencer",
  "days_until_expiry": 15,
  "is_paid": true
}
```

### 2.7 Ver Historial de Pagos
**GET** `/api/soats/{id}/payment_history/`

Ver historial completo de pagos del vehículo asociado al SOAT.

**Respuesta (200):**
```json
[
  {
    "year": 2024,
    "soat_id": 5,
    "issue_date": "2024-01-01",
    "expiry_date": "2025-01-01",
    "cost": "500000.00",
    "paid": true,
    "payment_date": "2024-01-15",
    "transaction_id": 45
  },
  {
    "year": 2023,
    "soat_id": 3,
    "issue_date": "2023-01-01",
    "expiry_date": "2024-01-01",
    "cost": "450000.00",
    "paid": true,
    "payment_date": "2023-01-10",
    "transaction_id": 23
  }
]
```

### 2.8 Ver SOATs Próximos a Vencer
**GET** `/api/soats/expiring_soon/`

Obtiene todos los SOATs que están próximos a vencer (dentro del rango configurado en `alert_days_before`).

**Respuesta (200):**
```json
[
  {
    "id": 7,
    "vehicle_info": {
      "id": 2,
      "plate": "XYZ789",
      "brand": "Mazda",
      "model": "3"
    },
    "expiry_date": "2024-02-01",
    "days_until_expiry": 15,
    "cost": "480000.00",
    "status": "por_vencer",
    "is_paid": true
  }
]
```

### 2.9 Ver SOATs Vencidos
**GET** `/api/soats/expired/`

Obtiene todos los SOATs vencidos.

**Respuesta (200):**
```json
[
  {
    "id": 4,
    "vehicle_info": {
      "id": 3,
      "plate": "DEF456",
      "brand": "Chevrolet",
      "model": "Spark"
    },
    "expiry_date": "2023-12-15",
    "days_until_expiry": -30,
    "cost": "420000.00",
    "status": "vencido",
    "is_paid": false
  }
]
```

---

## 3. Gestión de Alertas de SOAT

### 3.1 Listar Alertas
**GET** `/api/soat-alerts/`

**Query Parameters:**
- `is_read`: Filtrar por leídas (`true`/`false`)
- `alert_type`: Filtrar por tipo (`proxima_vencer`, `vencida`, `pendiente_pago`, `atrasada`)
- `soat`: Filtrar por ID de SOAT

**Ejemplos:**
```
GET /api/soat-alerts/?is_read=false
GET /api/soat-alerts/?alert_type=proxima_vencer
GET /api/soat-alerts/?soat=5&is_read=false
```

**Respuesta (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "soat": 7,
      "soat_info": {
        "id": 7,
        "vehicle": {
          "plate": "XYZ789",
          "brand": "Mazda",
          "model": "3"
        },
        "expiry_date": "2024-02-01",
        "cost": "480000.00"
      },
      "alert_type": "proxima_vencer",
      "alert_type_display": "Próxima a vencer",
      "message": "Tu SOAT del vehículo XYZ789 vence en 15 días",
      "is_read": false,
      "created_at": "2024-01-17T08:00:00Z"
    }
  ]
}
```

### 3.2 Ver Detalle de Alerta
**GET** `/api/soat-alerts/{id}/`

**Respuesta (200):**
```json
{
  "id": 12,
  "soat": 7,
  "soat_info": {
    "id": 7,
    "vehicle": {
      "plate": "XYZ789",
      "brand": "Mazda",
      "model": "3"
    },
    "expiry_date": "2024-02-01",
    "cost": "480000.00",
    "status": "por_vencer"
  },
  "alert_type": "proxima_vencer",
  "alert_type_display": "Próxima a vencer",
  "message": "Tu SOAT del vehículo XYZ789 vence en 15 días",
  "is_read": false,
  "created_at": "2024-01-17T08:00:00Z",
  "read_at": null
}
```

### 3.3 Marcar Alerta como Leída
**POST** `/api/soat-alerts/{id}/mark_read/`

**Body:** Vacío

**Respuesta (200):**
```json
{
  "id": 12,
  "is_read": true,
  "read_at": "2024-01-20T10:45:00Z",
  "message": "Alerta marcada como leída"
}
```

### 3.4 Marcar Todas las Alertas como Leídas
**POST** `/api/soat-alerts/mark_all_read/`

**Body:** Vacío

**Respuesta (200):**
```json
{
  "message": "Todas las alertas han sido marcadas como leídas",
  "updated_count": 5
}
```

---

## 4. Estados del SOAT

El sistema maneja 5 estados automáticos:

| Estado | Descripción | Condición |
|--------|-------------|-----------|
| `vigente` | SOAT vigente | Pagado y no próximo a vencer |
| `por_vencer` | Próximo a vencer | Dentro del rango de `alert_days_before` |
| `vencido` | SOAT vencido | Fecha pasada y sin pagar |
| `pendiente_pago` | Pendiente de pago | No pagado pero no vencido |
| `atrasado` | Pago atrasado | Vencido y sin pagar |

---

## 5. Tipos de Alertas

El sistema genera 4 tipos de alertas automáticas:

| Tipo | Cuándo se genera | Mensaje |
|------|------------------|---------|
| `proxima_vencer` | N días antes del vencimiento | "Tu SOAT del vehículo {placa} vence en {días} días" |
| `vencida` | El día del vencimiento | "Tu SOAT del vehículo {placa} ha vencido" |
| `pendiente_pago` | Cuando no está pagado | "El SOAT del vehículo {placa} está pendiente de pago" |
| `atrasada` | Cuando está vencido y sin pagar | "El SOAT del vehículo {placa} está atrasado desde hace {días} días" |

---

## 6. Comando Cron para Alertas Automáticas

Para generar alertas automáticas diariamente, ejecuta:

```bash
python manage.py check_soat_alerts
```

**Programación sugerida (crontab):**
```bash
# Ejecutar todos los días a las 8:00 AM
0 8 * * * cd /ruta/proyecto && python manage.py check_soat_alerts
```

**Windows Task Scheduler:**
```powershell
# Crear tarea programada
schtasks /create /tn "SOAT Alerts" /tr "python C:\ruta\manage.py check_soat_alerts" /sc daily /st 08:00
```

---

## 7. Flujo Completo de Uso

### Paso 1: Registrar Vehículo
```http
POST /api/vehicles/
{
  "plate": "ABC123",
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2020
}
```

### Paso 2: Crear SOAT
```http
POST /api/soats/
{
  "vehicle": 1,
  "issue_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "cost": 500000.00,
  "insurance_company": "Seguros SURA",
  "policy_number": "POL123456",
  "alert_days_before": 30
}
```

### Paso 3: Registrar Pago
```http
POST /api/soats/5/register_payment/
{
  "account_id": 3,
  "payment_date": "2024-01-15",
  "notes": "Pago SOAT 2024"
}
```

### Paso 4: Ver Alertas
```http
GET /api/soat-alerts/?is_read=false
```

### Paso 5: Ver Historial
```http
GET /api/vehicles/1/payment_history/
```

---

## 8. Validaciones y Reglas de Negocio

1. **Un SOAT solo puede pagarse una vez**
   - El endpoint `register_payment` rechaza pagos duplicados

2. **La categoría "Seguros" se crea automáticamente**
   - Al registrar el primer pago, se crea la categoría

3. **Las alertas se generan automáticamente**
   - Se evitan duplicados (una alerta del mismo tipo cada 24 horas)

4. **El estado se actualiza automáticamente**
   - Al registrar pago, crear SOAT, o ejecutar el comando cron

5. **Los pagos se registran como transacciones**
   - Se crea automáticamente en la app `transactions`
   - Se actualiza el saldo de la cuenta

---

## 9. Errores Comunes

### Error 400: SOAT ya pagado
```json
{
  "error": "Este SOAT ya está pagado"
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

### Error 404: Vehículo no encontrado
```json
{
  "detail": "No encontrado."
}
```
**Solución:** Verificar ID del vehículo

---

## 10. Colección Postman

### Variables de Entorno
```json
{
  "base_url": "http://localhost:8000/api",
  "token": "YOUR_AUTH_TOKEN",
  "vehicle_id": "1",
  "soat_id": "5",
  "account_id": "3"
}
```

### Headers Globales
```
Authorization: Token {{token}}
Content-Type: application/json
```

---

## Conclusión

Esta API permite gestionar completamente el ciclo de vida del SOAT:
- ✅ Registro de vehículos
- ✅ Creación y seguimiento de pólizas
- ✅ Registro automatizado de pagos con contabilidad
- ✅ Alertas automáticas configurables
- ✅ Historial completo de pagos
- ✅ Estados automáticos
- ✅ Integración con transacciones y cuentas

**¿Necesitas más ayuda?** Consulta la documentación general en `/docs/API_REFERENCE.md`
