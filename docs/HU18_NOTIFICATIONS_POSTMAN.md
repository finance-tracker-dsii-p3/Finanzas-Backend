# HU-18: Notificaciones y Recordatorios - Documentación API con Postman

## Descripción
API completa para gestión de notificaciones automáticas y recordatorios personalizados - Sistema que envía alertas de presupuesto (80%, 100%), recordatorios de facturas, SOAT, fin de mes y recordatorios personalizados, respetando preferencias del usuario (timezone, idioma) y evitando duplicados.

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

## 1. Gestión de Preferencias de Notificaciones

### 1.1 Ver Preferencias del Usuario
**GET** `/api/auth/preferences/`

Obtiene o crea las preferencias de notificación del usuario autenticado.

**Respuesta (200):**
```json
{
  "id": 1,
  "timezone": "America/Bogota",
  "timezone_display": "America/Bogota",
  "language": "es",
  "language_display": "Español",
  "enable_budget_alerts": true,
  "enable_bill_reminders": true,
  "enable_soat_reminders": true,
  "enable_month_end_reminders": true,
  "enable_custom_reminders": true,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

### 1.2 Actualizar Preferencias
**PATCH** `/api/auth/preferences/{id}/`

**Body (JSON):**
```json
{
  "timezone": "America/Mexico_City",
  "language": "en",
  "enable_budget_alerts": true,
  "enable_bill_reminders": false,
  "enable_soat_reminders": true
}
```

**Campos:**
- `timezone`: Zona horaria (ver endpoint de timezones)
- `language`: Idioma (`es` o `en`)
- `enable_budget_alerts`: Activar alertas de presupuesto (80%, 100%)
- `enable_bill_reminders`: Activar recordatorios de facturas
- `enable_soat_reminders`: Activar recordatorios de SOAT
- `enable_month_end_reminders`: Activar recordatorio de fin de mes
- `enable_custom_reminders`: Activar recordatorios personalizados

**Respuesta (200):**
```json
{
  "id": 1,
  "timezone": "America/Mexico_City",
  "timezone_display": "America/Mexico_City",
  "language": "en",
  "language_display": "English",
  "enable_budget_alerts": true,
  "enable_bill_reminders": false,
  "enable_soat_reminders": true,
  "enable_month_end_reminders": true,
  "enable_custom_reminders": true,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

### 1.3 Listar Zonas Horarias Disponibles
**GET** `/api/auth/preferences/timezones/`

**Respuesta (200):**
```json
[
  {
    "timezone": "America/Bogota",
    "display_name": "America/Bogota"
  },
  {
    "timezone": "America/Mexico_City",
    "display_name": "America/Mexico City"
  },
  {
    "timezone": "America/Lima",
    "display_name": "America/Lima"
  },
  {
    "timezone": "America/Buenos_Aires",
    "display_name": "America/Buenos Aires"
  },
  {
    "timezone": "UTC",
    "display_name": "UTC"
  }
]
```

---

## 2. Gestión de Notificaciones

### 2.1 Listar Notificaciones
**GET** `/api/notifications/notifications/`

**Query Parameters:**
- `type`: Filtrar por tipo (`budget_warning`, `budget_exceeded`, `bill_reminder`, `soat_reminder`, `month_end_reminder`, `custom_reminder`)
- `read`: Filtrar por leídas (`true`/`false`)
- `related_type`: Filtrar por tipo de objeto (`budget`, `bill`, `soat`, `custom_reminder`, `system`)

**Ejemplos:**
```
GET /api/notifications/notifications/?read=false
GET /api/notifications/notifications/?type=budget_warning
GET /api/notifications/notifications/?type=bill_reminder&read=false
```

**Respuesta (200):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "notification_type": "budget_warning",
      "notification_type_display": "Alerta de presupuesto (80%)",
      "title": "⚠️ Alerta de Presupuesto",
      "message": "Has alcanzado el 85% del presupuesto de la categoría 'Comida' ($850,000 de $1,000,000).",
      "read": false,
      "is_read": false,
      "read_timestamp": null,
      "related_object_id": 12,
      "related_object_type": "budget",
      "scheduled_for": null,
      "sent_at": "2025-01-20T16:45:00Z",
      "created_at": "2025-01-20T16:45:00Z",
      "recipient_name": "Juan Pérez",
      "recipient_username": "juanperez",
      "user_id": 5,
      "user_name": "Juan Pérez"
    },
    {
      "id": 41,
      "notification_type": "bill_reminder",
      "notification_type_display": "Recordatorio de factura",
      "title": "📄 Recordatorio de Factura",
      "message": "La factura de Netflix vence en 3 días ($45,000).",
      "read": false,
      "is_read": false,
      "read_timestamp": null,
      "related_object_id": 8,
      "related_object_type": "bill",
      "scheduled_for": null,
      "sent_at": "2025-01-20T09:00:00Z",
      "created_at": "2025-01-20T09:00:00Z",
      "recipient_name": "Juan Pérez",
      "recipient_username": "juanperez",
      "user_id": 5,
      "user_name": "Juan Pérez"
    }
  ]
}
```

### 2.2 Ver Detalle de Notificación
**GET** `/api/notifications/notifications/{id}/`

**Respuesta (200):**
```json
{
  "id": 42,
  "notification_type": "budget_warning",
  "notification_type_display": "Alerta de presupuesto (80%)",
  "title": "⚠️ Alerta de Presupuesto",
  "message": "Has alcanzado el 85% del presupuesto de la categoría 'Comida' ($850,000 de $1,000,000).",
  "read": false,
  "is_read": false,
  "read_timestamp": null,
  "related_object_id": 12,
  "related_object_type": "budget",
  "scheduled_for": null,
  "sent_at": "2025-01-20T16:45:00Z",
  "created_at": "2025-01-20T16:45:00Z",
  "recipient_name": "Juan Pérez",
  "recipient_username": "juanperez",
  "user_id": 5,
  "user_name": "Juan Pérez"
}
```

### 2.3 Marcar Notificación como Leída
**POST** `/api/notifications/notifications/{id}/mark_as_read/`

**Body:** Vacío

**Respuesta (200):**
```json
{
  "message": "Notificación marcada como leída"
}
```

### 2.4 Marcar Todas las Notificaciones como Leídas
**POST** `/api/notifications/notifications/mark_all_read/`

**Body:** Vacío

**Respuesta (200):**
```json
{
  "message": "5 notificaciones marcadas como leídas"
}
```

### 2.5 Ver Resumen de Notificaciones
**GET** `/api/notifications/notifications/summary/`

**Respuesta (200):**
```json
{
  "total": 25,
  "unread": 8,
  "recent": [
    {
      "id": 42,
      "notification_type": "budget_warning",
      "title": "⚠️ Alerta de Presupuesto",
      "message": "Has alcanzado el 85% del presupuesto de la categoría 'Comida'.",
      "read": false,
      "created_at": "2025-01-20T16:45:00Z"
    }
  ],
  "by_type": [
    {"notification_type": "budget_warning", "count": 5},
    {"notification_type": "bill_reminder", "count": 8},
    {"notification_type": "soat_reminder", "count": 2},
    {"notification_type": "month_end_reminder", "count": 1},
    {"notification_type": "custom_reminder", "count": 9}
  ]
}
```

---

## 3. Gestión de Recordatorios Personalizados

### 3.1 Crear Recordatorio Personalizado
**POST** `/api/notifications/custom-reminders/`

**Body (JSON):**
```json
{
  "title": "Reunión con contador",
  "message": "Llevar documentos de gastos del mes para la reunión de cierre contable",
  "reminder_date": "2025-02-05",
  "reminder_time": "09:00:00"
}
```

**Campos:**
- `title` (requerido): Título del recordatorio
- `message` (requerido): Mensaje detallado
- `reminder_date` (requerido): Fecha del recordatorio (YYYY-MM-DD)
- `reminder_time` (requerido): Hora del recordatorio (HH:MM:SS)

**Respuesta Exitosa (201):**
```json
{
  "id": 15,
  "title": "Reunión con contador",
  "message": "Llevar documentos de gastos del mes para la reunión de cierre contable",
  "reminder_date": "2025-02-05",
  "reminder_time": "09:00:00",
  "is_sent": false,
  "sent_at": null,
  "notification_id": null,
  "is_read": false,
  "read_at": null,
  "is_past_due_display": false,
  "user_username": "juanperez",
  "created_at": "2025-01-20T14:30:00Z",
  "updated_at": "2025-01-20T14:30:00Z"
}
```

**Errores Comunes:**
- `400`: La fecha y hora del recordatorio debe ser futura

### 3.2 Listar Recordatorios Personalizados
**GET** `/api/notifications/custom-reminders/`

**Query Parameters:**
- `is_sent`: Filtrar por enviados (`true`/`false`)
- `is_read`: Filtrar por leídos (`true`/`false`)

**Ejemplos:**
```
GET /api/notifications/custom-reminders/?is_sent=false
GET /api/notifications/custom-reminders/?is_sent=true&is_read=false
```

**Respuesta (200):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "title": "Reunión con contador",
      "reminder_date": "2025-02-05",
      "reminder_time": "09:00:00",
      "is_sent": false,
      "is_read": false,
      "is_past_due_display": false,
      "created_at": "2025-01-20T14:30:00Z"
    },
    {
      "id": 12,
      "title": "Pagar tarjeta de crédito",
      "reminder_date": "2025-01-28",
      "reminder_time": "10:00:00",
      "is_sent": true,
      "is_read": false,
      "is_past_due_display": false,
      "created_at": "2025-01-15T08:00:00Z"
    }
  ]
}
```

### 3.3 Ver Detalle de Recordatorio
**GET** `/api/notifications/custom-reminders/{id}/`

**Respuesta (200):**
```json
{
  "id": 15,
  "title": "Reunión con contador",
  "message": "Llevar documentos de gastos del mes para la reunión de cierre contable",
  "reminder_date": "2025-02-05",
  "reminder_time": "09:00:00",
  "is_sent": false,
  "sent_at": null,
  "notification_id": null,
  "is_read": false,
  "read_at": null,
  "is_past_due_display": false,
  "user_username": "juanperez",
  "created_at": "2025-01-20T14:30:00Z",
  "updated_at": "2025-01-20T14:30:00Z"
}
```

### 3.4 Actualizar Recordatorio
**PATCH** `/api/notifications/custom-reminders/{id}/`

**Body (JSON):**
```json
{
  "reminder_date": "2025-02-06",
  "reminder_time": "10:30:00",
  "message": "Llevar documentos de gastos + facturas del mes"
}
```

**Respuesta (200):** Retorna el recordatorio actualizado

### 3.5 Eliminar Recordatorio
**DELETE** `/api/notifications/custom-reminders/{id}/`

**Respuesta (204):** Sin contenido

### 3.6 Marcar Recordatorio como Leído
**POST** `/api/notifications/custom-reminders/{id}/mark_read/`

Marca el recordatorio como leído. También marca la notificación asociada (si existe) como leída.

**Body:** Vacío

**Respuesta (200):**
```json
{
  "id": 15,
  "title": "Reunión con contador",
  "message": "Llevar documentos de gastos del mes para la reunión de cierre contable",
  "reminder_date": "2025-02-05",
  "reminder_time": "09:00:00",
  "is_sent": true,
  "sent_at": "2025-02-05T09:00:00Z",
  "notification_id": 50,
  "is_read": true,
  "read_at": "2025-02-05T09:15:00Z",
  "is_past_due_display": false,
  "user_username": "juanperez",
  "created_at": "2025-01-20T14:30:00Z",
  "updated_at": "2025-02-05T09:15:00Z"
}
```

### 3.7 Marcar Todos los Recordatorios como Leídos
**POST** `/api/notifications/custom-reminders/mark_all_read/`

**Body:** Vacío

**Respuesta (200):**
```json
{
  "message": "5 recordatorios marcados como leídos",
  "updated_count": 5
}
```

### 3.8 Ver Recordatorios Pendientes
**GET** `/api/notifications/custom-reminders/pending/`

Lista todos los recordatorios que aún no han sido enviados.

**Respuesta (200):**
```json
[
  {
    "id": 15,
    "title": "Reunión con contador",
    "reminder_date": "2025-02-05",
    "reminder_time": "09:00:00",
    "is_sent": false,
    "is_read": false,
    "is_past_due_display": false,
    "created_at": "2025-01-20T14:30:00Z"
  }
]
```

### 3.9 Ver Recordatorios Enviados
**GET** `/api/notifications/custom-reminders/sent/`

Lista todos los recordatorios que ya fueron enviados.

**Respuesta (200):**
```json
[
  {
    "id": 12,
    "title": "Pagar tarjeta de crédito",
    "reminder_date": "2025-01-28",
    "reminder_time": "10:00:00",
    "is_sent": true,
    "is_read": false,
    "is_past_due_display": false,
    "created_at": "2025-01-15T08:00:00Z"
  }
]
```

---

## 4. Tipos de Notificaciones Automáticas

El sistema genera automáticamente 6 tipos de notificaciones:

### 4.1 Budget Warning (Alerta de Presupuesto 80%)
**Cuándo se genera:** Cuando una transacción de gasto hace que se alcance el 80% (o el umbral configurado) del presupuesto mensual de una categoría.

**Ejemplo de mensaje (español):**
```
⚠️ Alerta de Presupuesto
Has alcanzado el 85% del presupuesto de la categoría 'Comida' ($850,000 de $1,000,000).
```

**Ejemplo de mensaje (inglés):**
```
⚠️ Budget Alert
You've reached 85% of your 'Food' budget ($850,000 of $1,000,000).
```

**Campos relacionados:**
- `related_object_type`: `budget`
- `related_object_id`: ID del presupuesto

### 4.2 Budget Exceeded (Presupuesto Excedido 100%)
**Cuándo se genera:** Cuando una transacción de gasto hace que se exceda el 100% del presupuesto mensual de una categoría.

**Ejemplo de mensaje (español):**
```
🚨 Presupuesto Excedido
Has excedido el presupuesto de la categoría 'Comida' ($1,050,000 de $1,000,000).
```

### 4.3 Bill Reminder (Recordatorio de Factura)
**Cuándo se genera:** Automáticamente según días configurados antes del vencimiento, el día del vencimiento, o después del vencimiento sin pagar.

**Ejemplos de mensajes:**
- Próxima a vencer: `La factura de Netflix vence en 3 días ($45,000).`
- Vence hoy: `La factura de Netflix vence hoy ($45,000).`
- Atrasada: `La factura de Netflix está atrasada 2 días ($45,000).`

**Campos relacionados:**
- `related_object_type`: `bill`
- `related_object_id`: ID de la factura

### 4.4 SOAT Reminder (Recordatorio de SOAT)
**Cuándo se genera:** Automáticamente según días configurados antes del vencimiento, próximo a vencer, o vencido.

**Ejemplos de mensajes:**
- Próximo: `El SOAT de tu vehículo ABC123 vence en 15 días.`
- Próximo a vencer: `El SOAT de tu vehículo ABC123 vence pronto.`
- Vencido: `El SOAT de tu vehículo ABC123 está vencido desde hace 5 días.`

**Campos relacionados:**
- `related_object_type`: `soat`
- `related_object_id`: ID del SOAT

### 4.5 Month End Reminder (Recordatorio de Fin de Mes)
**Cuándo se genera:** Automáticamente el día 28 de cada mes a las 9 AM (en la zona horaria del usuario).

**Mensaje (español):**
```
📅 Fin de Mes
Importa tu extracto bancario antes del cierre del mes.
```

**Mensaje (inglés):**
```
📅 Month End
Import your bank statement before the month ends.
```

**Campos relacionados:**
- `related_object_type`: `system`
- `related_object_id`: null

### 4.6 Custom Reminder (Recordatorio Personalizado)
**Cuándo se genera:** Cuando llega la fecha y hora programada por el usuario.

**Mensaje:** El título y mensaje definidos por el usuario

**Campos relacionados:**
- `related_object_type`: `custom_reminder`
- `related_object_id`: ID del CustomReminder

---

## 5. Comando Cron para Notificaciones Automáticas

Para generar y enviar notificaciones automáticamente, ejecuta:

```bash
python manage.py check_notifications
```

Este comando verifica:
1. ✅ Recordatorios personalizados pendientes (según timezone del usuario)
2. ✅ Recordatorios de fin de mes (día 28 a las 9 AM)
3. ✅ Facturas próximas a vencer, que vencen hoy, o atrasadas
4. ✅ SOATs próximos a vencer o vencidos

**Programación sugerida (crontab):**
```bash
# Ejecutar todos los días a las 9:00 AM
0 9 * * * cd /ruta/proyecto && python manage.py check_notifications
```

**Windows Task Scheduler:**
```powershell
schtasks /create /tn "Check Notifications" /tr "python C:\ruta\manage.py check_notifications" /sc daily /st 09:00
```

**Output del comando:**
```
=================================================================
  Verificación de Notificaciones - 2025-01-20 09:00:00
=================================================================

[1/4] Verificando recordatorios personalizados...
  ✓ 3 recordatorios personalizados procesados

[2/4] Verificando recordatorios de fin de mes...
  ✓ 0 recordatorios de fin de mes enviados

[3/4] Verificando facturas pendientes...
  ✓ Facturas verificadas: 12
    - Próximas a vencer: 4
    - Vencen hoy: 1
    - Atrasadas: 2

[4/4] Verificando SOATs pendientes...
  ✓ 2 alertas de SOAT creadas

=================================================================
  Resumen Final
=================================================================
  ✓ Total de notificaciones enviadas: 12

  Verificación completada exitosamente
=================================================================
```

---

## 6. Validaciones y Reglas de Negocio

### 6.1 Prevención de Duplicados
El sistema evita notificaciones duplicadas usando estas reglas:
- **Presupuesto:** Una notificación por presupuesto/tipo/mes
- **Facturas:** Una notificación por factura cada 24 horas
- **SOAT:** Una alerta por SOAT cada 24 horas
- **Fin de mes:** Una notificación por usuario por mes

### 6.2 Respeto de Preferencias del Usuario
- Si `enable_budget_alerts = false`, no se envían alertas de presupuesto
- Si `enable_bill_reminders = false`, no se envían recordatorios de facturas
- Si `enable_soat_reminders = false`, no se envían recordatorios de SOAT
- Si `enable_month_end_reminders = false`, no se envía recordatorio de fin de mes
- Si `enable_custom_reminders = false`, no se envían recordatorios personalizados

### 6.3 Manejo de Timezone
- Los recordatorios personalizados se envían en el timezone configurado
- El recordatorio de fin de mes se envía a las 9 AM del timezone del usuario
- Las fechas se muestran en el timezone local del usuario

### 6.4 Idioma de las Notificaciones
- Si `language = "es"`: Mensajes en español
- Si `language = "en"`: Mensajes en inglés
- El idioma afecta todos los mensajes automáticos

---

## 7. Flujo Completo de Uso

### Paso 1: Configurar Preferencias
```http
PATCH /api/auth/preferences/1/
{
  "timezone": "America/Bogota",
  "language": "es",
  "enable_budget_alerts": true,
  "enable_bill_reminders": true,
  "enable_soat_reminders": true,
  "enable_month_end_reminders": true,
  "enable_custom_reminders": true
}
```

### Paso 2: Crear Recordatorios Personalizados
```http
POST /api/notifications/custom-reminders/
{
  "title": "Pagar tarjeta de crédito",
  "message": "Fecha límite para pagar sin intereses",
  "reminder_date": "2025-01-28",
  "reminder_time": "10:00:00"
}
```

### Paso 3: Ver Notificaciones No Leídas
```http
GET /api/notifications/notifications/?read=false
```

### Paso 4: Marcar Notificación como Leída
```http
POST /api/notifications/notifications/42/mark_as_read/
```

### Paso 5: Ver Recordatorios Pendientes
```http
GET /api/notifications/custom-reminders/pending/
```

### Paso 6: Programar Cron Job
```bash
# Agregar a crontab
0 9 * * * cd /ruta/proyecto && python manage.py check_notifications
```

---

## 8. Ejemplos de Casos de Uso

### Caso 1: Alerta de Presupuesto
**Escenario:** Usuario gasta $850,000 de un presupuesto de $1,000,000 en "Comida"

**Notificación generada automáticamente:**
```json
{
  "notification_type": "budget_warning",
  "title": "⚠️ Alerta de Presupuesto",
  "message": "Has alcanzado el 85% del presupuesto de la categoría 'Comida' ($850,000 de $1,000,000).",
  "related_object_type": "budget",
  "related_object_id": 12
}
```

### Caso 2: Recordatorio de Factura
**Escenario:** Factura de Netflix vence en 3 días

**Notificación generada automáticamente (día 25 si vence día 28):**
```json
{
  "notification_type": "bill_reminder",
  "title": "📄 Recordatorio de Factura",
  "message": "La factura de Netflix vence en 3 días ($45,000).",
  "related_object_type": "bill",
  "related_object_id": 8
}
```

### Caso 3: Recordatorio de Fin de Mes
**Escenario:** Es día 28 y son las 9 AM en la zona horaria del usuario

**Notificación generada automáticamente:**
```json
{
  "notification_type": "month_end_reminder",
  "title": "📅 Fin de Mes",
  "message": "Importa tu extracto bancario antes del cierre del mes.",
  "related_object_type": "system"
}
```

### Caso 4: Recordatorio Personalizado
**Escenario:** Usuario programa recordatorio para reunión

**1. Crear recordatorio:**
```http
POST /api/notifications/custom-reminders/
{
  "title": "Reunión con contador",
  "message": "Llevar facturas del mes",
  "reminder_date": "2025-02-05",
  "reminder_time": "09:00:00"
}
```

**2. Notificación generada automáticamente (cuando llega la fecha):**
```json
{
  "notification_type": "custom_reminder",
  "title": "Reunión con contador",
  "message": "Llevar facturas del mes",
  "related_object_type": "custom_reminder",
  "related_object_id": 15
}
```

---

## 9. Errores Comunes

### Error 400: Fecha de recordatorio inválida
```json
{
  "error": "La fecha y hora del recordatorio debe ser futura"
}
```
**Solución:** Asegurar que `reminder_date` y `reminder_time` sean en el futuro

### Error 400: Zona horaria inválida
```json
{
  "timezone": ["Zona horaria inválida"]
}
```
**Solución:** Usar una zona horaria del endpoint `/api/auth/preferences/timezones/`

### Error 403: Sin permisos
```json
{
  "detail": "No tienes permiso para realizar esta acción."
}
```
**Solución:** Verificar autenticación y que el recurso pertenezca al usuario

---

## 10. Colección Postman

### Variables de Entorno
```json
{
  "base_url": "http://localhost:8000/api",
  "token": "YOUR_AUTH_TOKEN",
  "notification_id": "42",
  "reminder_id": "15",
  "preferences_id": "1"
}
```

### Headers Globales
```
Authorization: Token {{token}}
Content-Type: application/json
```

### Tests Sugeridos para Postman

#### Test 1: Configurar Preferencias
```javascript
pm.test("Preferences updated successfully", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.timezone).to.exist;
    pm.expect(jsonData.language).to.be.oneOf(["es", "en"]);
});
```

#### Test 2: Crear Recordatorio
```javascript
pm.test("Custom reminder created", function () {
    pm.response.to.have.status(201);
    var jsonData = pm.response.json();
    pm.expect(jsonData.is_sent).to.be.false;
    pm.environment.set("reminder_id", jsonData.id);
});
```

#### Test 3: Listar Notificaciones No Leídas
```javascript
pm.test("Unread notifications retrieved", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.results).to.be.an('array');
    jsonData.results.forEach(function(notif) {
        pm.expect(notif.read).to.be.false;
    });
});
```

---

## 11. Integración con Otras Apps

### Con `budgets`
- Signals en `budgets` llaman a `NotificationEngine.create_budget_warning()` al alcanzar 80%
- Signals en `budgets` llaman a `NotificationEngine.create_budget_exceeded()` al exceder 100%
- Se respetan las preferencias `enable_budget_alerts`

### Con `bills`
- `BillService.check_and_create_reminders()` crea BillReminders y Notifications
- Se respetan las preferencias `enable_bill_reminders`
- Los recordatorios consideran `reminder_days_before` de cada factura

### Con `vehicles` (SOAT)
- `SOATService.check_and_create_alerts()` crea SOATAlerts y Notifications
- Se respetan las preferencias `enable_soat_reminders`
- Las alertas consideran `alert_days_before` de cada SOAT

---

## 12. Buenas Prácticas

1. **Configura tus preferencias primero**
   - Define tu timezone correcta para recibir recordatorios a la hora adecuada
   - Selecciona tu idioma preferido (español o inglés)
   - Activa/desactiva tipos de notificaciones según tus necesidades

2. **Revisa notificaciones regularmente**
   - Usa `GET /api/notifications/notifications/?read=false` para ver pendientes
   - Marca como leídas para mantener tu bandeja organizada

3. **Crea recordatorios personalizados con anticipación**
   - Programa recordatorios con varios días de anticipación
   - Incluye mensajes detallados para recordar el contexto

4. **Programa el cron job correctamente**
   - Ejecuta `check_notifications` diariamente a una hora fija
   - Revisa los logs para verificar que se ejecuta correctamente

5. **Monitorea alertas de presupuesto**
   - Las alertas de 80% te dan tiempo para ajustar tus gastos
   - No ignores las alertas de 100% excedido

---

## Conclusión

Esta API permite gestionar completamente el sistema de notificaciones y recordatorios:
- ✅ Configuración de preferencias por usuario (timezone, idioma, tipos)
- ✅ Notificaciones automáticas de presupuesto (80%, 100%)
- ✅ Recordatorios automáticos de facturas (próximas, hoy, atrasadas)
- ✅ Recordatorios automáticos de SOAT (próximos, vencidos)
- ✅ Recordatorio de fin de mes (día 28 a las 9 AM)
- ✅ Recordatorios personalizados con fecha/hora
- ✅ Respeto de timezone e idioma del usuario
- ✅ Prevención de notificaciones duplicadas
- ✅ Historial completo de notificaciones
- ✅ Comando cron para verificación diaria

**¿Necesitas más ayuda?** Consulta la documentación general en `/docs/API_REFERENCE.md`
