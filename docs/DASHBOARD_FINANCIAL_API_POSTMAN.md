# Dashboard Financiero API - Guía de Pruebas Postman

## 📚 Índice

- [Endpoint Principal](#endpoint-principal)
- [Ejemplos de Requests](#ejemplos-de-requests)
- [Estructura de Respuestas](#estructura-de-respuestas)
- [Facturas Próximas a Vencer](#facturas-próximas-a-vencer)
- [Filtros Disponibles](#filtros-disponibles)
- [Casos de Uso](#casos-de-uso)
- [Códigos de Estado](#códigos-de-estado)

---

## 🎯 Endpoint Principal

### `GET /api/dashboard/financial/`

Obtiene el resumen financiero completo del usuario con totales, movimientos recientes y datos para gráficos.

**Base URL:** `http://127.0.0.1:8000`

**Headers Requeridos:**
```
Authorization: Token YOUR_AUTH_TOKEN
Content-Type: application/json
```

---

## 📋 Ejemplos de Requests

### 1. Dashboard del Mes Actual (Sin filtros)

```http
GET http://127.0.0.1:8000/api/dashboard/financial/
Authorization: Token YOUR_AUTH_TOKEN
```

**Comportamiento:** 
- Si no se especifican filtros, muestra datos del mes actual
- Incluye todos los totales y movimientos recientes

**Respuesta Esperada (200 OK):**
```json
{
  "success": true,
  "data": {
    "has_data": true,
    "summary": {
      "total_income": 15000000,
      "total_expenses": 8500000,
      "total_savings": 200000,
      "total_iva": 1615000,
      "total_gmf": 42500,
      "net_balance": 6500000,
      "currency": "COP"
    },
    "filters": {
      "year": 2025,
      "month": 12,
      "account_id": null,
      "period_label": "Diciembre 2025"
    },
    "recent_transactions": [
      {
        "id": 45,
        "type": "Expense",
        "type_code": 2,
        "date": "2025-12-10",
        "description": "Compra supermercado",
        "amount": 350400,
        "amount_formatted": "$3.504",
        "currency": "COP",
        "account": "Cuenta Ahorros",
        "category": "Comida",
        "category_color": "#FF6B6B",
        "category_icon": "🍔"
      }
      // ... hasta 5 movimientos
    ],
    "upcoming_bills": [
      {
        "id": 12,
        "provider": "Netflix",
        "amount": 4490000,
        "amount_formatted": "$44.900",
        "due_date": "2025-12-15",
        "days_until_due": 5,
        "status": "pending",
        "urgency": "soon",
        "urgency_label": "Próxima",
        "urgency_color": "#3B82F6",
        "suggested_account": "Cuenta Ahorros",
        "suggested_account_id": 2,
        "category": "Entretenimiento",
        "category_color": "#9333EA",
        "category_icon": "🎬",
        "description": "Suscripción mensual premium",
        "is_recurring": true
      },
      {
        "id": 15,
        "provider": "EPM",
        "amount": 15000000,
        "amount_formatted": "$150.000",
        "due_date": "2025-12-12",
        "days_until_due": 2,
        "status": "pending",
        "urgency": "urgent",
        "urgency_label": "Urgente",
        "urgency_color": "#F59E0B",
        "suggested_account": "Cuenta Corriente",
        "suggested_account_id": 1,
        "category": "Servicios",
        "category_color": "#10B981",
        "category_icon": "⚡",
        "description": "Factura energía diciembre",
        "is_recurring": true
      }
      // ... hasta 5 facturas ordenadas por proximidad
    ],
    "charts": {
      "expense_distribution": {
        "categories": [
          {
            "id": 1,
            "name": "Comida",
            "amount": 350400,
            "count": 5,
            "percentage": 41.22,
            "color": "#FF6B6B",
            "icon": "🍔",
            "formatted": "$3.504"
          }
          // ... más categorías
        ],
        "total": 8500000,
        "total_formatted": "$85.000",
        "has_data": true
      },
      "daily_flow": {
        "dates": ["2025-12-01", "2025-12-02", "..."],
        "income": [500000, 0, 300000, "..."],
        "expenses": [100000, 250000, 150000, "..."],
        "total_income": 15000000,
        "total_expenses": 8500000,
        "has_data": true
      }
    },
    "accounts_info": {
      "total_accounts": 3,
      "has_accounts": true
    }
  },
  "message": "Dashboard financiero obtenido exitosamente"
}
```

---

### 2. Filtrar por Año Específico

```http
GET http://127.0.0.1:8000/api/dashboard/financial/?year=2025
Authorization: Token YOUR_AUTH_TOKEN
```

**Comportamiento:** 
- Muestra todos los datos del año 2025
- Agrupa transacciones de enero a diciembre

---

### 3. Filtrar por Mes y Año Específico

```http
GET http://127.0.0.1:8000/api/dashboard/financial/?year=2025&month=11
Authorization: Token YOUR_AUTH_TOKEN
```

**Comportamiento:** 
- Muestra solo datos de noviembre 2025
- Gráfico diario muestra del 1 al 30 de noviembre

**Nota:** El parámetro `month` requiere especificar `year`.

---

### 4. Filtrar por Cuenta Específica

```http
GET http://127.0.0.1:8000/api/dashboard/financial/?account_id=5
Authorization: Token YOUR_AUTH_TOKEN
```

**Comportamiento:** 
- Muestra solo transacciones de la cuenta con ID 5
- Aplica al mes actual si no se especifica year/month

---

### 5. Filtrar por Mes, Año y Cuenta

```http
GET http://127.0.0.1:8000/api/dashboard/financial/?year=2025&month=12&account_id=5
Authorization: Token YOUR_AUTH_TOKEN
```

**Comportamiento:** 
- Combina filtros: diciembre 2025 + cuenta ID 5
- Ideal para análisis específico de una cuenta en un período

---

### 6. Ver Todos los Períodos

```http
GET http://127.0.0.1:8000/api/dashboard/financial/?all=true
Authorization: Token YOUR_AUTH_TOKEN
```

**Comportamiento:** 
- Muestra todas las transacciones sin filtro de fecha
- Útil para ver histórico completo

---

### 7. Ver Todos los Períodos de una Cuenta

```http
GET http://127.0.0.1:8000/api/dashboard/financial/?all=true&account_id=5
Authorization: Token YOUR_AUTH_TOKEN
```

**Comportamiento:** 
- Histórico completo filtrado por cuenta específica

---

## 📊 Estructura de Respuestas

### Respuesta Exitosa con Datos

```json
{
  "success": true,
  "data": {
    "has_data": true,
    "summary": {
      "total_income": 15000000,        // Centavos ($150,000.00)
      "total_expenses": 8500000,       // Centavos ($85,000.00)
      "total_savings": 200000,         // Centavos ($2,000.00)
      "total_iva": 1615000,            // Centavos ($16,150.00)
      "total_gmf": 42500,              // Centavos ($425.00)
      "net_balance": 6500000,          // Centavos ($65,000.00)
      "currency": "COP"
    },
    "filters": {
      "year": 2025,
      "month": 12,
      "account_id": null,
      "period_label": "Diciembre 2025"
    },
    "recent_transactions": [
      {
        "id": 45,
        "type": "Expense",
        "type_code": 2,
        "date": "2025-12-10",
        "description": "Compra supermercado",
        "amount": 350400,
        "amount_formatted": "$3.504",
        "currency": "COP",
        "account": "Cuenta Ahorros",
        "category": "Comida",
        "category_color": "#FF6B6B",
        "category_icon": "🍔"
      }
    ],
    "charts": {
      "expense_distribution": {
        "categories": [...],
        "total": 8500000,
        "has_data": true
      },
      "daily_flow": {
        "dates": [...],
        "income": [...],
        "expenses": [...],
        "has_data": true
      }
    },
    "accounts_info": {
      "total_accounts": 3,
      "has_accounts": true
    }
  },
  "message": "Dashboard financiero obtenido exitosamente"
}
```

---

### Respuesta con Estado Vacío (Sin Transacciones)

```json
{
  "success": true,
  "data": {
    "has_data": false,
    "summary": {
      "total_income": 0.0,
      "total_expenses": 0.0,
      "total_savings": 0.0,
      "total_iva": 0.0,
      "total_gmf": 0.0,
      "net_balance": 0.0,
      "currency": "COP"
    },
    "filters": {
      "year": null,
      "month": null,
      "account_id": null,
      "period_label": "Todos"
    },
    "recent_transactions": [],
    "upcoming_bills": [],
    "charts": {
      "expense_distribution": {
        "categories": [],
        "total": 0,
        "has_data": false
      },
      "daily_flow": {
        "dates": [],
        "income": [],
        "expenses": [],
        "total_income": 0,
        "total_expenses": 0,
        "has_data": false
      }
    },
    "accounts_info": {
      "total_accounts": 2,
      "has_accounts": true
    },
    "empty_state": {
      "message": "No tienes movimientos registrados",
      "suggestion": "Registra tu primer movimiento",
      "action": "create_transaction"
    }
  },
  "message": "Dashboard financiero obtenido exitosamente"
}
```

---

### Respuesta con Estado Vacío (Sin Cuentas)

```json
{
  "success": true,
  "data": {
    "has_data": false,
    "summary": {
      "total_income": 0.0,
      "total_expenses": 0.0,
      "total_savings": 0.0,
      "total_iva": 0.0,
      "total_gmf": 0.0,
      "net_balance": 0.0,
      "currency": "COP"
    },
    "filters": {
      "year": null,
      "month": null,
      "account_id": null,
      "period_label": "Todos"
    },
    "recent_transactions": [],
    "upcoming_bills": [],
    "charts": {
      "expense_distribution": {
        "categories": [],
        "total": 0,
        "has_data": false
      },
      "daily_flow": {
        "dates": [],
        "income": [],
        "expenses": [],
        "total_income": 0,
        "total_expenses": 0,
        "has_data": false
      }
    },
    "accounts_info": {
      "total_accounts": 0,
      "has_accounts": false
    },
    "empty_state": {
      "message": "No tienes cuentas creadas",
      "suggestion": "Crea una cuenta para empezar",
      "action": "create_account"
    }
  },
  "message": "Dashboard financiero obtenido exitosamente"
}
```

---

## 🔍 Filtros Disponibles

### Query Parameters

| Parámetro | Tipo | Requerido | Descripción | Ejemplo |
|-----------|------|-----------|-------------|---------|
| `year` | integer | No | Año a filtrar (2000-2100) | `2025` |
| `month` | integer | No | Mes a filtrar (1-12, requiere `year`) | `12` |
| `account_id` | integer | No | ID de cuenta a filtrar | `5` |
| `all` | boolean | No | Si es `true`, muestra todos los períodos | `true` |

### Reglas de Validación

1. **`month` requiere `year`:**
   ```
   ❌ ?month=12
   ✅ ?year=2025&month=12
   ```

2. **`year` debe estar entre 2000 y 2100:**
   ```
   ❌ ?year=1999
   ✅ ?year=2025
   ```

3. **`month` debe estar entre 1 y 12:**
   ```
   ❌ ?month=13
   ✅ ?month=12
   ```

4. **Si `all=true`, se ignoran filtros de fecha:**
   ```
   ?all=true&year=2025  → Se muestra todo (year se ignora)
   ```

5. **Sin filtros = mes actual:**
   ```
   ?  → Diciembre 2025 (si estamos en diciembre)
   ```

---

## 📋 Facturas Próximas a Vencer

### Estructura del Campo `upcoming_bills`

El campo `upcoming_bills` contiene un array de las próximas 5 facturas a vencer, ordenadas por proximidad (las más urgentes primero).

**Niveles de Urgencia:**

| Urgencia | Label | Color | Condición |
|----------|-------|-------|-----------|
| `overdue` | Vencida | `#EF4444` (Rojo) | `days_until_due < 0` |
| `today` | Hoy | `#F59E0B` (Naranja) | `days_until_due == 0` |
| `urgent` | Urgente | `#F59E0B` (Naranja) | `days_until_due <= 3` |
| `soon` | Próxima | `#3B82F6` (Azul) | `days_until_due <= 7` |
| `normal` | Pendiente | `#6B7280` (Gris) | `days_until_due > 7` |

### Ejemplo de Factura

```json
{
  "id": 12,
  "provider": "Netflix",
  "amount": 4490000,                    // Centavos ($44,900)
  "amount_formatted": "$44.900",
  "due_date": "2025-12-15",
  "days_until_due": 5,
  "status": "pending",                  // pending | paid | overdue
  "urgency": "soon",
  "urgency_label": "Próxima",
  "urgency_color": "#3B82F6",
  "suggested_account": "Cuenta Ahorros",
  "suggested_account_id": 2,
  "category": "Entretenimiento",
  "category_color": "#9333EA",
  "category_icon": "🎬",
  "description": "Suscripción mensual premium",
  "is_recurring": true
}
```

### Características Importantes

1. **Ordenamiento:** Las facturas se ordenan automáticamente por `due_date` (más cercanas primero)
2. **Límite:** Máximo 5 facturas en la lista
3. **Filtrado:** Solo muestra facturas con estado `pending` u `overdue` (no incluye pagadas)
4. **Montos:** Los montos están en centavos (igual que todo el dashboard)
5. **Días negativos:** Si `days_until_due` es negativo, la factura está vencida

### Casos de Uso de Facturas

**Mostrar alerta de urgencia:**
```javascript
upcoming_bills.forEach(bill => {
  if (bill.urgency === 'overdue') {
    showAlert(`¡Factura vencida! ${bill.provider} - ${bill.amount_formatted}`);
  } else if (bill.urgency === 'today') {
    showAlert(`¡Vence hoy! ${bill.provider} - ${bill.amount_formatted}`);
  } else if (bill.urgency === 'urgent') {
    showWarning(`Vence en ${bill.days_until_due} días: ${bill.provider}`);
  }
});
```

**Renderizar lista con colores:**
```javascript
upcoming_bills.forEach(bill => {
  const bgColor = bill.urgency_color + '20'; // 20% opacity
  const item = `
    <div style="background-color: ${bgColor}; border-left: 4px solid ${bill.urgency_color}">
      <span>${bill.category_icon}</span>
      <h4>${bill.provider}</h4>
      <p>${bill.urgency_label} - ${Math.abs(bill.days_until_due)} días</p>
      <p>${bill.amount_formatted}</p>
    </div>
  `;
});
```

**Sugerir pago desde cuenta:**
```javascript
if (bill.suggested_account) {
  console.log(`Pagar desde: ${bill.suggested_account} (ID: ${bill.suggested_account_id})`);
  // Mostrar botón de pago rápido
}
```

---

## 🎯 Casos de Uso

### Caso 1: Dashboard Principal de la App

**Objetivo:** Mostrar resumen del mes actual al abrir la app

```http
GET /api/dashboard/financial/
```

**UI Frontend:**
- Card "Total Ingresos": `summary.total_income / 100`
- Card "Total Gastos": `summary.total_expenses / 100`
- Card "Total Ahorros": `summary.total_savings / 100`
- Card "Total IVA": `summary.total_iva / 100`
- Card "Total GMF": `summary.total_gmf / 100`
- Lista de movimientos recientes: `recent_transactions`
- Lista de facturas próximas: `upcoming_bills` (ordenadas por urgencia)
- Gráfico de dona: `charts.expense_distribution`
- Gráfico de líneas: `charts.daily_flow`

---

### Caso 2: Selector de Mes en la App

**Objetivo:** Usuario selecciona "Noviembre 2025" en un dropdown

```http
GET /api/dashboard/financial/?year=2025&month=11
```

**UI Frontend:**
- Actualizar título: `filters.period_label` → "Noviembre 2025"
- Actualizar todos los cards con nuevos totales
- Actualizar gráficos con datos del mes seleccionado

---

### Caso 3: Filtrar por Cuenta

**Objetivo:** Ver solo movimientos de "Cuenta Ahorros" (ID: 5)

```http
GET /api/dashboard/financial/?account_id=5
```

**UI Frontend:**
- Mostrar badge "Filtrando por: Cuenta Ahorros"
- Mostrar solo totales de esa cuenta
- Lista de movimientos solo de esa cuenta

---

### Caso 4: Ver Histórico Completo

**Objetivo:** Botón "Ver todo el histórico"

```http
GET /api/dashboard/financial/?all=true
```

**UI Frontend:**
- Título: "Histórico Completo"
- Mostrar totales acumulados de todas las transacciones
- Gráfico diario puede ser extenso (considerar paginación o resumen)

---

### Caso 5: Análisis Específico

**Objetivo:** Ver gastos de "Tarjeta de Crédito" en Diciembre 2025

```http
GET /api/dashboard/financial/?year=2025&month=12&account_id=3
```

**UI Frontend:**
- Título: "Tarjeta de Crédito - Diciembre 2025"
- Análisis detallado de ese período y cuenta

---

## ⚠️ Validaciones y Errores

### Error: Mes sin Año

**Request:**
```http
GET /api/dashboard/financial/?month=12
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Parámetro 'year' requerido",
  "details": "Para filtrar por mes, debes especificar también el año"
}
```

---

### Error: Año Inválido

**Request:**
```http
GET /api/dashboard/financial/?year=1999
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Año inválido",
  "details": "El año debe estar entre 2000 y 2100"
}
```

---

### Error: Mes Inválido

**Request:**
```http
GET /api/dashboard/financial/?year=2025&month=13
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Mes inválido",
  "details": "El mes debe estar entre 1 y 12"
}
```

---

### Error: Cuenta No Encontrada

**Request:**
```http
GET /api/dashboard/financial/?account_id=999
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Cuenta con ID 999 no encontrada",
  "has_data": false
}
```

---

### Error: Parámetros No Numéricos

**Request:**
```http
GET /api/dashboard/financial/?year=abc&month=xyz
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Parámetros inválidos",
  "details": "Los parámetros year, month y account_id deben ser números enteros"
}
```

---

### Error: Sin Autenticación

**Request:**
```http
GET /api/dashboard/financial/
```
(Sin header `Authorization`)

**Response (401 Unauthorized):**
```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

---

## 📈 Códigos de Estado HTTP

| Código | Significado | Cuándo Ocurre |
|--------|-------------|---------------|
| **200 OK** | Éxito | Dashboard obtenido correctamente (con o sin datos) |
| **400 Bad Request** | Error en parámetros | Filtros inválidos, cuenta no encontrada |
| **401 Unauthorized** | Sin autenticación | Token faltante o inválido |
| **500 Internal Server Error** | Error del servidor | Error inesperado en el backend |

---

## 💡 Notas Importantes

### 1. **Formato de Montos (CRÍTICO)**

Todos los montos vienen en **centavos**:
```javascript
// ❌ INCORRECTO
const income = data.summary.total_income; // 15000000
console.log(`$${income}`); // "$15000000" 😱

// ✅ CORRECTO
const income = data.summary.total_income / 100; // 150000
console.log(`$${income.toLocaleString()}`); // "$150,000" 👍
```

### 2. **Moneda Base**

- El campo `summary.currency` indica la moneda base del usuario
- Todos los totales están convertidos a esa moneda
- Si el usuario tiene cuentas en USD y COP, todo se convierte a su moneda base configurada

### 3. **Gráficos**

Los datos de los gráficos también vienen en centavos:
```javascript
// Gráfico de dona
charts.expense_distribution.categories.forEach(cat => {
  const amount = cat.amount / 100; // Convertir a pesos
  console.log(`${cat.name}: $${amount}`);
});

// Gráfico de líneas
charts.daily_flow.income.forEach(amount => {
  const value = amount / 100; // Convertir a pesos
  // Usar en gráfico
});
```

### 4. **Estado Vacío**

Siempre verificar `has_data` antes de renderizar:
```javascript
if (!data.has_data) {
  // Mostrar empty_state
  console.log(data.empty_state.message);
  console.log(data.empty_state.suggestion);
  
  if (data.empty_state.action === 'create_account') {
    // Mostrar botón "Crear Cuenta"
  } else if (data.empty_state.action === 'create_transaction') {
    // Mostrar botón "Registrar Movimiento"
  }
}
```

### 5. **Movimientos Recientes**

Los movimientos ya vienen con el campo `amount_formatted`:
```javascript
recent_transactions.forEach(tx => {
  // Opción 1: Usar el formato del backend
  console.log(tx.amount_formatted); // "$3.504"
  
  // Opción 2: Formatear manualmente
  const amount = tx.amount / 100;
  console.log(`${tx.currency} ${amount.toLocaleString()}`);
});
```

---

## 🧪 Collection de Postman

### Variables de Entorno

Crear un environment con estas variables:

```json
{
  "base_url": "http://127.0.0.1:8000",
  "auth_token": "TU_TOKEN_AQUI"
}
```

### Requests Organizados

**Folder:** `Dashboard Financiero`

1. **Dashboard Mes Actual**
   - Method: GET
   - URL: `{{base_url}}/api/dashboard/financial/`
   - Headers: `Authorization: Token {{auth_token}}`

2. **Dashboard Año Específico**
   - Method: GET
   - URL: `{{base_url}}/api/dashboard/financial/?year=2025`

3. **Dashboard Mes y Año**
   - Method: GET
   - URL: `{{base_url}}/api/dashboard/financial/?year=2025&month=11`

4. **Dashboard Por Cuenta**
   - Method: GET
   - URL: `{{base_url}}/api/dashboard/financial/?account_id={{account_id}}`

5. **Dashboard Histórico**
   - Method: GET
   - URL: `{{base_url}}/api/dashboard/financial/?all=true`

6. **Dashboard Combinado**
   - Method: GET
   - URL: `{{base_url}}/api/dashboard/financial/?year=2025&month=12&account_id={{account_id}}`

---

## 📞 Soporte

Si encuentras problemas o comportamientos inesperados:

1. Verificar que el token de autenticación sea válido
2. Validar que los parámetros cumplan las reglas (año, mes, cuenta)
3. Revisar logs del backend para errores detallados
4. Contactar al equipo de backend con el request exacto que falla

---

## 📚 Ver También

- [CURRENCY_BASE_CONFIGURATION.md](./CURRENCY_BASE_CONFIGURATION.md) - Configuración de moneda base
- [ANALYTICS_AMOUNTS_FORMAT.md](./ANALYTICS_AMOUNTS_FORMAT.md) - Formato de montos en analytics
- [API_REFERENCE.md](./API_REFERENCE.md) - Referencia completa de la API

---

**Última actualización:** 11 de diciembre de 2025  
**Versión:** 1.0  
**Autor:** Backend Team
