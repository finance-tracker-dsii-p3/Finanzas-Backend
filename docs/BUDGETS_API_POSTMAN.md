# 📊 API de Presupuestos - Guía de Postman (HU-07)

Esta guía te ayudará a probar todos los endpoints de la API de **Presupuestos por Categoría** usando Postman.

---

## 🔐 Configuración Inicial

### 1. Variables de Entorno en Postman

Crea una colección en Postman y configura estas variables:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | URL base del backend |
| `token` | `Token xxxxx...` | Token de autenticación del usuario |

### 2. Autenticación

Todos los endpoints requieren autenticación. En cada petición, agrega el header:

```
Authorization: {{token}}
```

### 3. Obtener Token de Autenticación

**Endpoint:** `POST {{base_url}}/api/auth/login/`

**Body (JSON):**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com"
  }
}
```

---

## 📋 Endpoints CRUD Básicos

### 1. Listar Presupuestos

**Método:** `GET`
**URL:** `{{base_url}}/api/budgets/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `active_only=true` - Solo presupuestos activos (default: true)
- `active_only=false` - Incluir presupuestos inactivos
- `period=monthly` - Solo presupuestos mensuales
- `period=yearly` - Solo presupuestos anuales

**Ejemplo con filtros:**
```
GET {{base_url}}/api/budgets/?active_only=true&period=monthly
```

**Respuesta Exitosa (200 OK):**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "category": 2,
      "category_name": "Comida",
      "category_type": "expense",
      "category_type_display": "Gasto",
      "category_color": "#DC2626",
      "category_icon": "fa-utensils",
      "amount": "400000.00",
      "calculation_mode": "base",
      "calculation_mode_display": "Base (sin impuestos)",
      "period": "monthly",
      "period_display": "Mensual",
      "start_date": "2025-11-01",
      "is_active": true,
      "alert_threshold": "80.00",
      "spent_amount": "320000.00",
      "spent_percentage": "80.00",
      "remaining_amount": "80000.00",
      "status": "warning",
      "status_text": "Alerta: 80.0% gastado",
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-15T14:30:00Z"
    },
    {
      "id": 2,
      "category": 5,
      "category_name": "Transporte",
      "category_type": "expense",
      "category_type_display": "Gasto",
      "category_color": "#EA580C",
      "category_icon": "fa-car",
      "amount": "200000.00",
      "calculation_mode": "total",
      "calculation_mode_display": "Total (con impuestos)",
      "period": "monthly",
      "period_display": "Mensual",
      "start_date": "2025-11-01",
      "is_active": true,
      "alert_threshold": "80.00",
      "spent_amount": "150000.00",
      "spent_percentage": "75.00",
      "remaining_amount": "50000.00",
      "status": "good",
      "status_text": "Dentro del presupuesto",
      "created_at": "2025-11-01T10:30:00Z",
      "updated_at": "2025-11-15T14:35:00Z"
    }
  ]
}
```

**Respuesta cuando no hay presupuestos:**
```json
{
  "count": 0,
  "message": "Aún no tienes límites definidos. ¡Agrega uno para empezar a controlar tus gastos!",
  "results": []
}
```

---

### 2. Crear Presupuesto Nuevo

**Método:** `POST`
**URL:** `{{base_url}}/api/budgets/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Presupuesto Mensual:**
```json
{
  "category": 2,
  "amount": 400000,
  "calculation_mode": "base",
  "period": "monthly",
  "alert_threshold": 80
}
```

**Body (JSON) - Presupuesto con Todos los Campos:**
```json
{
  "category": 5,
  "amount": 200000,
  "calculation_mode": "total",
  "period": "monthly",
  "start_date": "2025-11-01",
  "is_active": true,
  "alert_threshold": 85
}
```

**Body (JSON) - Presupuesto Anual:**
```json
{
  "category": 8,
  "amount": 5000000,
  "calculation_mode": "base",
  "period": "yearly",
  "alert_threshold": 75
}
```

**Respuesta Exitosa (201 Created):**
```json
{
  "id": 3,
  "category": 2,
  "category_name": "Comida",
  "category_type": "expense",
  "category_type_display": "Gasto",
  "category_color": "#DC2626",
  "category_icon": "fa-utensils",
  "amount": "400000.00",
  "calculation_mode": "base",
  "calculation_mode_display": "Base (sin impuestos)",
  "period": "monthly",
  "period_display": "Mensual",
  "start_date": "2025-11-15",
  "is_active": true,
  "alert_threshold": "80.00",
  "spent_amount": "0.00",
  "spent_percentage": "0.00",
  "remaining_amount": "400000.00",
  "daily_average": "0.00",
  "projection": {
    "projected_amount": "0.00",
    "projected_percentage": "0.00",
    "will_exceed": false,
    "days_remaining": 15,
    "days_total": 30,
    "daily_average": "0.00"
  },
  "status": "good",
  "status_text": "Dentro del presupuesto",
  "is_over_budget": false,
  "is_alert_triggered": false,
  "period_dates": {
    "start": "2025-11-01",
    "end": "2025-11-30"
  },
  "created_at": "2025-11-15T15:00:00Z",
  "updated_at": "2025-11-15T15:00:00Z"
}
```

**Errores Comunes:**

```json
{
  "category": ["La categoría no pertenece al usuario autenticado."]
}
```

```json
{
  "category": ["Ya existe un presupuesto mensual para esta categoría."]
}
```

```json
{
  "category": ["Solo se pueden crear presupuestos para categorías de gasto."]
}
```

```json
{
  "amount": ["El monto debe ser mayor a cero."]
}
```

---

### 3. Ver Detalle de un Presupuesto

**Método:** `GET`
**URL:** `{{base_url}}/api/budgets/{id}/`

**Ejemplo:**
```
GET {{base_url}}/api/budgets/1/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "category": 2,
  "category_name": "Comida",
  "category_type": "expense",
  "category_type_display": "Gasto",
  "category_color": "#DC2626",
  "category_icon": "fa-utensils",
  "amount": "400000.00",
  "calculation_mode": "base",
  "calculation_mode_display": "Base (sin impuestos)",
  "period": "monthly",
  "period_display": "Mensual",
  "start_date": "2025-11-01",
  "is_active": true,
  "alert_threshold": "80.00",
  "spent_amount": "320000.00",
  "spent_percentage": "80.00",
  "remaining_amount": "80000.00",
  "daily_average": "21333.33",
  "projection": {
    "projected_amount": "600000.00",
    "projected_percentage": "150.00",
    "will_exceed": true,
    "days_remaining": 15,
    "days_total": 30,
    "daily_average": "21333.33"
  },
  "status": "warning",
  "status_text": "Alerta: 80.0% gastado",
  "is_over_budget": false,
  "is_alert_triggered": true,
  "period_dates": {
    "start": "2025-11-01",
    "end": "2025-11-30"
  },
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-15T14:30:00Z"
}
```

---

### 4. Actualizar Presupuesto (PATCH)

**Método:** `PATCH`
**URL:** `{{base_url}}/api/budgets/{id}/`

**Ejemplo:**
```
PATCH {{base_url}}/api/budgets/1/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Cambiar solo el monto:**
```json
{
  "amount": 450000
}
```

**Body (JSON) - Cambiar modo de cálculo:**
```json
{
  "calculation_mode": "total"
}
```

**Body (JSON) - Cambiar umbral de alerta:**
```json
{
  "alert_threshold": 85
}
```

**Body (JSON) - Desactivar:**
```json
{
  "is_active": false
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "category": 2,
  "category_name": "Comida",
  "category_type": "expense",
  "category_type_display": "Gasto",
  "category_color": "#DC2626",
  "category_icon": "fa-utensils",
  "amount": "450000.00",
  "calculation_mode": "base",
  "calculation_mode_display": "Base (sin impuestos)",
  "period": "monthly",
  "period_display": "Mensual",
  "start_date": "2025-11-01",
  "is_active": true,
  "alert_threshold": "80.00",
  "spent_amount": "320000.00",
  "spent_percentage": "71.11",
  "remaining_amount": "130000.00",
  "daily_average": "21333.33",
  "projection": {
    "projected_amount": "600000.00",
    "projected_percentage": "133.33",
    "will_exceed": true,
    "days_remaining": 15,
    "days_total": 30,
    "daily_average": "21333.33"
  },
  "status": "good",
  "status_text": "Dentro del presupuesto",
  "is_over_budget": false,
  "is_alert_triggered": false,
  "period_dates": {
    "start": "2025-11-01",
    "end": "2025-11-30"
  },
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-15T16:00:00Z"
}
```

---

### 5. Eliminar Presupuesto

**Método:** `DELETE`
**URL:** `{{base_url}}/api/budgets/{id}/`

**Ejemplo:**
```
DELETE {{base_url}}/api/budgets/3/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Presupuesto para categoría \"Comida\" eliminado exitosamente.",
  "deleted_budget": {
    "id": 3,
    "category_name": "Comida",
    "amount": "400000.00"
  }
}
```

---

## 🔧 Acciones Especiales

### 6. Activar/Desactivar Presupuesto

**Método:** `POST`
**URL:** `{{base_url}}/api/budgets/{id}/toggle_active/`

**Ejemplo:**
```
POST {{base_url}}/api/budgets/1/toggle_active/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Presupuesto desactivado exitosamente.",
  "budget": {
    "id": 1,
    "category": 2,
    "category_name": "Comida",
    "is_active": false,
    "amount": "400000.00",
    "spent_amount": "320000.00",
    "spent_percentage": "80.00",
    "status": "warning",
    "updated_at": "2025-11-15T16:30:00Z"
  }
}
```

---

### 7. Obtener Estadísticas Generales

**Método:** `GET`
**URL:** `{{base_url}}/api/budgets/stats/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "total_budgets": 5,
  "active_budgets": 4,
  "exceeded_budgets": 1,
  "warning_budgets": 2,
  "good_budgets": 1,
  "total_allocated": "1500000.00",
  "total_spent": "850000.00",
  "total_remaining": "650000.00",
  "average_usage_percentage": "56.67",
  "monthly_budgets_count": 4,
  "yearly_budgets_count": 1
}
```

---

### 8. Obtener Resumen Mensual con Proyecciones

**Método:** `GET`
**URL:** `{{base_url}}/api/budgets/monthly_summary/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "period": {
    "month": 11,
    "year": 2025
  },
  "count": 3,
  "budgets": [
    {
      "budget_id": 1,
      "category_id": 2,
      "category_name": "Comida",
      "category_color": "#DC2626",
      "category_icon": "fa-utensils",
      "amount": "400000.00",
      "spent_amount": "320000.00",
      "spent_percentage": "80.00",
      "remaining_amount": "80000.00",
      "status": "warning",
      "projection": {
        "projected_amount": "600000.00",
        "projected_percentage": "150.00",
        "will_exceed": true,
        "days_remaining": 15,
        "days_total": 30,
        "daily_average": "21333.33"
      }
    },
    {
      "budget_id": 2,
      "category_id": 5,
      "category_name": "Transporte",
      "category_color": "#EA580C",
      "category_icon": "fa-car",
      "amount": "200000.00",
      "spent_amount": "150000.00",
      "spent_percentage": "75.00",
      "remaining_amount": "50000.00",
      "status": "good",
      "projection": {
        "projected_amount": "300000.00",
        "projected_percentage": "150.00",
        "will_exceed": true,
        "days_remaining": 15,
        "days_total": 30,
        "daily_average": "10000.00"
      }
    },
    {
      "budget_id": 4,
      "category_id": 8,
      "category_name": "Entretenimiento",
      "category_color": "#C2410C",
      "category_icon": "fa-film",
      "amount": "150000.00",
      "spent_amount": "45000.00",
      "spent_percentage": "30.00",
      "remaining_amount": "105000.00",
      "status": "good",
      "projection": {
        "projected_amount": "90000.00",
        "projected_percentage": "60.00",
        "will_exceed": false,
        "days_remaining": 15,
        "days_total": 30,
        "daily_average": "3000.00"
      }
    }
  ]
}
```

---

### 9. Obtener Presupuestos por Categoría

**Método:** `GET`
**URL:** `{{base_url}}/api/budgets/by_category/{category_id}/`

**Ejemplo:**
```
GET {{base_url}}/api/budgets/by_category/2/
```

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `active_only=true` - Solo presupuestos activos (default)
- `active_only=false` - Incluir inactivos

**Respuesta Exitosa (200 OK):**
```json
{
  "category": {
    "id": 2,
    "name": "Comida",
    "type": "expense"
  },
  "count": 2,
  "budgets": [
    {
      "id": 1,
      "category": 2,
      "category_name": "Comida",
      "amount": "400000.00",
      "calculation_mode": "base",
      "calculation_mode_display": "Base (sin impuestos)",
      "period": "monthly",
      "period_display": "Mensual",
      "spent_amount": "320000.00",
      "spent_percentage": "80.00",
      "status": "warning",
      "is_active": true
    },
    {
      "id": 5,
      "category": 2,
      "category_name": "Comida",
      "amount": "5000000.00",
      "calculation_mode": "base",
      "calculation_mode_display": "Base (sin impuestos)",
      "period": "yearly",
      "period_display": "Anual",
      "spent_amount": "3200000.00",
      "spent_percentage": "64.00",
      "status": "good",
      "is_active": true
    }
  ]
}
```

---

### 10. Obtener Categorías sin Presupuesto

**Método:** `GET`
**URL:** `{{base_url}}/api/budgets/categories_without_budget/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `period=monthly` - Buscar categorías sin presupuesto mensual (default)
- `period=yearly` - Buscar categorías sin presupuesto anual

**Respuesta Exitosa (200 OK):**
```json
{
  "period": "monthly",
  "count": 3,
  "categories": [
    {
      "id": 10,
      "name": "Salud",
      "type": "expense",
      "color": "#4B5563",
      "icon": "fa-heart"
    },
    {
      "id": 11,
      "name": "Educación",
      "type": "expense",
      "color": "#2563EB",
      "icon": "fa-graduation-cap"
    },
    {
      "id": 12,
      "name": "Otros Gastos",
      "type": "expense",
      "color": "#4B5563",
      "icon": "fa-question-circle"
    }
  ],
  "message": "Estas categorías aún no tienen presupuesto asignado."
}
```

**Cuando todas tienen presupuesto:**
```json
{
  "period": "monthly",
  "count": 0,
  "categories": [],
  "message": "Todas tus categorías de gasto tienen presupuesto."
}
```

---

### 11. Obtener Alertas de Presupuestos

**Método:** `GET`
**URL:** `{{base_url}}/api/budgets/alerts/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "count": 2,
  "alerts": [
    {
      "budget_id": 1,
      "category": "Comida",
      "category_color": "#DC2626",
      "amount": "400000.00",
      "spent_percentage": "95.00",
      "status": "exceeded",
      "message": "Presupuesto excedido"
    },
    {
      "budget_id": 2,
      "category": "Transporte",
      "category_color": "#EA580C",
      "amount": "200000.00",
      "spent_percentage": "82.00",
      "status": "warning",
      "message": "Alerta: 82.0% gastado"
    }
  ],
  "message": "Tienes presupuestos que requieren atención."
}
```

**Cuando no hay alertas:**
```json
{
  "count": 0,
  "alerts": [],
  "message": "Todos tus presupuestos están bajo control."
}
```

---

## 📊 Casos de Uso Completos

### Caso 1: Crear y Configurar Presupuesto Mensual para Comida

**Paso 1: Verificar categorías disponibles**
```
GET {{base_url}}/api/categories/expense/
```

**Paso 2: Crear presupuesto**
```
POST {{base_url}}/api/budgets/
Content-Type: application/json

{
  "category": 2,
  "amount": 400000,
  "calculation_mode": "base",
  "period": "monthly",
  "alert_threshold": 80
}
```

**Paso 3: Ver detalle y proyección**
```
GET {{base_url}}/api/budgets/1/
```

**Paso 4: Ajustar si es necesario**
```
PATCH {{base_url}}/api/budgets/1/

{
  "amount": 450000,
  "alert_threshold": 85
}
```

---

### Caso 2: Monitorear Todos los Presupuestos del Mes

**Paso 1: Ver resumen mensual**
```
GET {{base_url}}/api/budgets/monthly_summary/
```

**Paso 2: Ver estadísticas generales**
```
GET {{base_url}}/api/budgets/stats/
```

**Paso 3: Ver alertas**
```
GET {{base_url}}/api/budgets/alerts/
```

**Paso 4: Ver categorías sin presupuesto**
```
GET {{base_url}}/api/budgets/categories_without_budget/
```

---

### Caso 3: Gestionar Presupuesto Excedido

**Paso 1: Identificar presupuestos excedidos**
```
GET {{base_url}}/api/budgets/alerts/
```

**Paso 2: Ver detalles del presupuesto problemático**
```
GET {{base_url}}/api/budgets/1/
```

Respuesta mostrará:
- `is_over_budget`: true
- `status`: "exceeded"
- `projection`: Proyección a fin de mes

**Paso 3: Opciones de acción:**

**Opción A: Aumentar el límite**
```
PATCH {{base_url}}/api/budgets/1/

{
  "amount": 500000
}
```

**Opción B: Desactivar temporalmente**
```
POST {{base_url}}/api/budgets/1/toggle_active/
```

**Opción C: Eliminar y crear uno nuevo**
```
DELETE {{base_url}}/api/budgets/1/

POST {{base_url}}/api/budgets/
{
  "category": 2,
  "amount": 500000,
  "calculation_mode": "base"
}
```

---

## 🎨 Interpretación de Estados

### Estados del Presupuesto

| Estado | Color Sugerido | Descripción |
|--------|---------------|-------------|
| `good` | 🟢 Verde | Dentro del presupuesto, sin alertas |
| `warning` | 🟡 Amarillo | Alcanzó el umbral de alerta (default 80%) |
| `exceeded` | 🔴 Rojo | Presupuesto excedido |

### Modos de Cálculo

| Modo | Valor | Descripción |
|------|-------|-------------|
| Base | `base` | Calcula solo el monto base sin impuestos |
| Total | `total` | Calcula el monto total incluyendo impuestos |

### Períodos

| Período | Valor | Descripción |
|---------|-------|-------------|
| Mensual | `monthly` | Presupuesto se resetea cada mes |
| Anual | `yearly` | Presupuesto se resetea cada año |

---

## 📈 Campos Calculados Explicados

### spent_amount
Monto total gastado en el período actual según el modo de cálculo.

### spent_percentage
Porcentaje del presupuesto utilizado. Puede ser > 100% si se excedió.

### remaining_amount
Monto restante. Negativo si se excedió el presupuesto.

### daily_average
Promedio de gasto diario desde el inicio del período.

### projection
Proyección de gasto a fin de período basada en el promedio diario:
- `projected_amount`: Monto proyectado al final
- `projected_percentage`: Porcentaje proyectado
- `will_exceed`: true si se proyecta exceder el presupuesto
- `days_remaining`: Días faltantes en el período
- `days_total`: Total de días del período

---

## ❌ Errores Comunes y Soluciones

### Error 401 Unauthorized
**Causa:** Token no válido o no enviado
**Solución:** Verifica el header `Authorization: Token xxxxx`

### Error 400 - Presupuesto duplicado
**Causa:** Ya existe un presupuesto para esa categoría y período
**Solución:** Usa PATCH para actualizar el existente o DELETE para eliminarlo

### Error 400 - Categoría de ingreso
**Causa:** Intentaste crear presupuesto para categoría de ingreso
**Solución:** Solo se pueden crear presupuestos para categorías de tipo "expense"

### Error 400 - Categoría no pertenece al usuario
**Causa:** La categoría es de otro usuario
**Solución:** Verifica el ID de la categoría con GET /api/categories/

### Error 404 - Presupuesto no encontrado
**Causa:** El ID no existe o pertenece a otro usuario
**Solución:** Verifica el ID con GET /api/budgets/

---

## 📝 Notas Importantes

1. **Presupuestos únicos:** No puedes tener dos presupuestos del mismo período para la misma categoría
2. **Solo categorías de gasto:** Los presupuestos solo aplican a categorías de tipo "expense"
3. **Cálculo automático:** Los campos `spent_amount`, `spent_percentage`, etc. se calculan automáticamente
4. **Proyecciones:** Las proyecciones se basan en el promedio diario actual del período
5. **Períodos:** Los períodos mensuales van del día 1 al último del mes, los anuales del 1 de enero al 31 de diciembre
6. **Umbral de alerta:** Por defecto es 80%, pero puedes configurarlo entre 0 y 100%
7. **Gastos reales:** Actualmente los gastos están en 0 porque no hay transacciones implementadas todavía

---

## 🚀 Colección de Postman

Puedes importar esta estructura en Postman:

```
📁 Finanzas Backend - Budgets API (HU-07)
  📁 Auth
    ├─ POST Login
  📁 CRUD Básico
    ├─ GET Listar Presupuestos
    ├─ POST Crear Presupuesto
    ├─ GET Detalle Presupuesto
    ├─ PATCH Actualizar Presupuesto
    └─ DELETE Eliminar Presupuesto
  📁 Gestión Avanzada
    ├─ POST Activar/Desactivar
    ├─ GET Resumen Mensual
    ├─ GET Por Categoría
    ├─ GET Categorías sin Presupuesto
    └─ GET Alertas
  📁 Estadísticas
    └─ GET Estadísticas Generales
```

---

## 🎯 Ejemplos de Integración con Frontend

### Dashboard Principal
```javascript
// Obtener resumen mensual para mostrar barras de progreso
fetch('/api/budgets/monthly_summary/', {
  headers: { 'Authorization': `Token ${token}` }
})
.then(res => res.json())
.then(data => {
  data.budgets.forEach(budget => {
    // Mostrar barra de progreso
    const percentage = budget.spent_percentage;
    const color = budget.status === 'exceeded' ? 'red' :
                  budget.status === 'warning' ? 'yellow' : 'green';

    // Mostrar proyección
    if (budget.projection.will_exceed) {
      showAlert(`${budget.category_name}: Se proyecta exceder el presupuesto`);
    }
  });
});
```

### Widget de Alertas
```javascript
// Mostrar notificaciones de presupuestos con alertas
fetch('/api/budgets/alerts/', {
  headers: { 'Authorization': `Token ${token}` }
})
.then(res => res.json())
.then(data => {
  if (data.count > 0) {
    showNotificationBadge(data.count);
    data.alerts.forEach(alert => {
      addNotification(alert.category, alert.message);
    });
  }
});
```

---

**¡Happy Testing! 🎉**
