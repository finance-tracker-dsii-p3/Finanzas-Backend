# 📊 API de Analytics Financieros - Guía de Postman (HU-13)

Esta guía te ayudará a probar todos los endpoints de la API de **Analytics Financieros** usando Postman para la Historia de Usuario HU-13.

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

---

## 📊 Endpoints Principales de HU-13

### 1. Dashboard Completo de Analytics

**Método:** `GET`  
**URL:** `{{base_url}}/api/analytics/dashboard/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `period=current_month` - Período de análisis
- `mode=total` - Modo de cálculo (base o total)
- `others_threshold=0.05` - % mínimo para categorías individuales

**Ejemplo con parámetros:**
```
GET {{base_url}}/api/analytics/dashboard/?period=current_month&mode=base&others_threshold=0.1
```

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "data": {
    "indicators": {
      "income": {
        "amount": 500000,
        "count": 3,
        "formatted": "$500,000"
      },
      "expenses": {
        "amount": 350000,
        "count": 12,
        "formatted": "$350,000"
      },
      "balance": {
        "amount": 150000,
        "formatted": "$150,000",
        "is_positive": true
      },
      "period": {
        "start": "2025-11-01",
        "end": "2025-11-30",
        "days": 30
      },
      "mode": "base",
      "currency": "COP"
    },
    "expenses_chart": {
      "chart_data": [
        {
          "category_id": 1,
          "name": "Comida",
          "amount": 150000,
          "count": 8,
          "percentage": 42.86,
          "color": "#DC2626",
          "icon": "fa-utensils",
          "formatted_amount": "$150,000"
        },
        {
          "category_id": 2,
          "name": "Transporte",
          "amount": 100000,
          "count": 3,
          "percentage": 28.57,
          "color": "#EA580C",
          "icon": "fa-car",
          "formatted_amount": "$100,000"
        },
        {
          "category_id": "others",
          "name": "Otros",
          "amount": 100000,
          "count": 4,
          "percentage": 28.57,
          "color": "#9CA3AF",
          "icon": "fa-ellipsis-h",
          "formatted_amount": "$100,000",
          "is_aggregated": true
        }
      ],
      "others_data": [
        {
          "category_id": 3,
          "name": "Entretenimiento",
          "amount": 50000,
          "count": 2,
          "percentage": 14.29,
          "color": "#C2410C",
          "icon": "fa-film",
          "formatted_amount": "$50,000"
        }
      ],
      "total_expenses": 350000,
      "uncategorized_amount": 50000,
      "mode": "base",
      "period_summary": "01/11 - 30/11",
      "categories_count": 4
    },
    "daily_flow_chart": {
      "dates": ["2025-11-01", "2025-11-02", "2025-11-03"],
      "series": {
        "income": {
          "name": "Ingresos diarios",
          "data": [0, 200000, 0],
          "color": "#10B981",
          "total": 200000
        },
        "expenses": {
          "name": "Gastos diarios",
          "data": [50000, 25000, 30000],
          "color": "#EF4444",
          "total": 105000
        },
        "balance": {
          "name": "Balance acumulado",
          "data": [-50000, 125000, 95000],
          "color": "#3B82F6",
          "final": 95000
        }
      },
      "summary": {
        "period_days": 3,
        "total_income": 200000,
        "total_expenses": 105000,
        "final_balance": 95000,
        "avg_daily_income": 66666.67,
        "avg_daily_expense": 35000
      },
      "mode": "base",
      "period": {
        "start": "2025-11-01",
        "end": "2025-11-03"
      }
    },
    "metadata": {
      "generated_at": "2025-11-23",
      "user_id": 1,
      "period_requested": "current_month",
      "mode_used": "base",
      "others_threshold": 0.1
    }
  },
  "message": "Analytics dashboard generado para período current_month en modo base"
}
```

---

### 2. Solo Indicadores KPI

**Método:** `GET`  
**URL:** `{{base_url}}/api/analytics/indicators/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters:**
- `period=last_month` - Período a analizar
- `mode=total` - Incluir impuestos

**Ejemplo:**
```
GET {{base_url}}/api/analytics/indicators/?period=last_month&mode=total
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "income": {
      "amount": 650000,
      "count": 4,
      "formatted": "$650,000"
    },
    "expenses": {
      "amount": 480000,
      "count": 15,
      "formatted": "$480,000"
    },
    "balance": {
      "amount": 170000,
      "formatted": "$170,000",
      "is_positive": true
    },
    "period": {
      "start": "2025-10-01",
      "end": "2025-10-31",
      "days": 31
    },
    "mode": "total",
    "currency": "COP"
  },
  "message": "Indicadores del período obtenidos exitosamente"
}
```

---

### 3. Gráfico de Dona - Gastos por Categoría

**Método:** `GET`  
**URL:** `{{base_url}}/api/analytics/expenses-chart/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters:**
- `period=2025-10` - Mes específico (Octubre 2025)
- `mode=base` - Solo montos base
- `others_threshold=0.08` - 8% mínimo para categorías individuales

**Ejemplo:**
```
GET {{base_url}}/api/analytics/expenses-chart/?period=2025-10&mode=base&others_threshold=0.08
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "chart_data": [
      {
        "category_id": 1,
        "name": "Comida",
        "amount": 200000,
        "count": 12,
        "percentage": 45.45,
        "color": "#DC2626",
        "icon": "fa-utensils",
        "formatted_amount": "$200,000"
      },
      {
        "category_id": 2,
        "name": "Transporte",
        "amount": 120000,
        "count": 8,
        "percentage": 27.27,
        "color": "#EA580C",
        "icon": "fa-car",
        "formatted_amount": "$120,000"
      },
      {
        "category_id": "others",
        "name": "Otros",
        "amount": 120000,
        "count": 5,
        "percentage": 27.27,
        "color": "#9CA3AF",
        "icon": "fa-ellipsis-h",
        "formatted_amount": "$120,000",
        "is_aggregated": true
      }
    ],
    "others_data": [
      {
        "category_id": 3,
        "name": "Entretenimiento",
        "amount": 70000,
        "count": 3,
        "percentage": 15.91,
        "color": "#C2410C",
        "icon": "fa-film",
        "formatted_amount": "$70,000"
      },
      {
        "category_id": "uncategorized",
        "name": "Sin categoría",
        "amount": 50000,
        "count": 2,
        "percentage": 11.36,
        "color": "#6B7280",
        "icon": "fa-question-circle",
        "formatted_amount": "$50,000"
      }
    ],
    "total_expenses": 440000,
    "uncategorized_amount": 50000,
    "mode": "base",
    "period_summary": "01/10 - 31/10",
    "categories_count": 4
  },
  "message": "Datos de gráfico de categorías obtenidos exitosamente"
}
```

---

### 4. Gráfico de Líneas - Flujo Diario

**Método:** `GET`  
**URL:** `{{base_url}}/api/analytics/daily-flow-chart/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters:**
- `period=last_7_days` - Últimos 7 días
- `mode=total` - Incluir impuestos

**Ejemplo:**
```
GET {{base_url}}/api/analytics/daily-flow-chart/?period=last_7_days&mode=total
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "dates": ["2025-11-17", "2025-11-18", "2025-11-19", "2025-11-20", "2025-11-21", "2025-11-22", "2025-11-23"],
    "series": {
      "income": {
        "name": "Ingresos diarios",
        "data": [0, 0, 300000, 0, 0, 150000, 0],
        "color": "#10B981",
        "total": 450000
      },
      "expenses": {
        "name": "Gastos diarios",
        "data": [25000, 45000, 30000, 15000, 60000, 20000, 35000],
        "color": "#EF4444",
        "total": 230000
      },
      "balance": {
        "name": "Balance acumulado",
        "data": [-25000, -70000, 160000, 145000, 85000, 215000, 180000],
        "color": "#3B82F6",
        "final": 180000
      }
    },
    "summary": {
      "period_days": 7,
      "total_income": 450000,
      "total_expenses": 230000,
      "final_balance": 180000,
      "avg_daily_income": 64285.71,
      "avg_daily_expense": 32857.14
    },
    "mode": "total",
    "period": {
      "start": "2025-11-17",
      "end": "2025-11-23"
    }
  },
  "message": "Datos de gráfico de flujo diario obtenidos exitosamente"
}
```

---

### 5. Drill-down: Transacciones por Categoría

**Método:** `GET`  
**URL:** `{{base_url}}/api/analytics/category/{category_id}/transactions/`

**Path Parameters:**
- `category_id`: ID de la categoría o `uncategorized` para sin categoría

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters:**
- `period=current_month` - Período a filtrar
- `mode=total` - Modo de cálculo
- `limit=20` - Número máximo de transacciones

**Ejemplos:**

#### Categoría específica:
```
GET {{base_url}}/api/analytics/category/1/transactions/?period=current_month&mode=total&limit=20
```

#### Sin categoría:
```
GET {{base_url}}/api/analytics/category/uncategorized/transactions/?period=last_month&limit=10
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": 15,
        "date": "2025-11-23",
        "description": "Almuerzo restaurante italiano",
        "amount": 45000,
        "formatted_amount": "$45,000",
        "account": "Tarjeta Crédito",
        "tag": "comida",
        "category": {
          "id": 1,
          "name": "Comida",
          "color": "#DC2626",
          "icon": "fa-utensils"
        }
      },
      {
        "id": 14,
        "date": "2025-11-22",
        "description": "Supermercado semanal",
        "amount": 120000,
        "formatted_amount": "$120,000",
        "account": "Cuenta Ahorros",
        "tag": "mercado",
        "category": {
          "id": 1,
          "name": "Comida",
          "color": "#DC2626",
          "icon": "fa-utensils"
        }
      }
    ],
    "total_count": 8,
    "showing_count": 2,
    "category_name": "Comida",
    "total_amount": 250000,
    "formatted_total": "$250,000",
    "period": {
      "start": "2025-11-01",
      "end": "2025-11-30"
    },
    "mode": "total",
    "has_more": true
  },
  "message": "Transacciones de categoría obtenidas exitosamente"
}
```

---

### 6. Períodos Disponibles

**Método:** `GET`  
**URL:** `{{base_url}}/api/analytics/periods/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "available_periods": [
      {
        "key": "current_month",
        "name": "Mes actual",
        "description": "Noviembre 2025"
      },
      {
        "key": "last_month",
        "name": "Mes anterior",
        "description": "Mes completo anterior"
      },
      {
        "key": "current_year",
        "name": "Año actual",
        "description": "2025"
      },
      {
        "key": "last_7_days",
        "name": "Últimos 7 días",
        "description": "Semana reciente"
      },
      {
        "key": "last_30_days",
        "name": "Últimos 30 días",
        "description": "Mes reciente"
      }
    ],
    "data_range": {
      "min_date": "2025-01-15",
      "max_date": "2025-11-23"
    },
    "custom_period_info": {
      "formats": [
        "YYYY-MM (mes específico)",
        "YYYY (año específico)",
        "YYYY-MM-DD,YYYY-MM-DD (rango personalizado)"
      ]
    }
  }
}
```

---

## 🎯 Casos de Uso Completos para HU-13

### Caso 1: Dashboard del Mes Actual en Modo Base

**Paso 1: Obtener dashboard completo**
```
GET {{base_url}}/api/analytics/dashboard/?period=current_month&mode=base
```

**Paso 2: Si hay categoría "Comida" al 30%, hacer drill-down**
```
GET {{base_url}}/api/analytics/category/1/transactions/?period=current_month&mode=base&limit=50
```

---

### Caso 2: Comparar Base vs Total

**Paso 1: Obtener indicadores en modo base**
```
GET {{base_url}}/api/analytics/indicators/?period=last_month&mode=base
```

**Paso 2: Obtener los mismos indicadores en modo total**
```
GET {{base_url}}/api/analytics/indicators/?period=last_month&mode=total
```

**Paso 3: Comparar diferencias en impuestos**

---

### Caso 3: Análisis de Período Específico

**Paso 1: Verificar períodos disponibles**
```
GET {{base_url}}/api/analytics/periods/
```

**Paso 2: Analizar mes específico (ej: Octubre 2025)**
```
GET {{base_url}}/api/analytics/dashboard/?period=2025-10&mode=total&others_threshold=0.05
```

**Paso 3: Ver detalles del gráfico de flujo diario**
```
GET {{base_url}}/api/analytics/daily-flow-chart/?period=2025-10&mode=total
```

---

### Caso 4: Análisis de Rango Personalizado

**Analizar período específico (ej: primera quincena de noviembre):**
```
GET {{base_url}}/api/analytics/dashboard/?period=2025-11-01,2025-11-15&mode=total
```

---

## 📋 Parámetros de Período Soportados

| Formato | Ejemplo | Descripción |
|---------|---------|-------------|
| `current_month` | - | Mes actual completo |
| `last_month` | - | Mes anterior completo |
| `current_year` | - | Año actual completo |
| `last_7_days` | - | Últimos 7 días |
| `last_30_days` | - | Últimos 30 días |
| `YYYY-MM` | `2025-10` | Mes específico |
| `YYYY` | `2025` | Año específico |
| `YYYY-MM-DD,YYYY-MM-DD` | `2025-11-01,2025-11-15` | Rango personalizado |

---

## 🎨 Interpretación de Modos

| Modo | Descripción | Campo Usado |
|------|-------------|-------------|
| `base` | Solo monto base sin impuestos | `base_amount` |
| `total` | Monto base + impuestos | `total_amount` |

---

## ❌ Errores Comunes y Soluciones

### Error 400 - Modo inválido
**Causa:** Parámetro `mode` no es 'base' o 'total'  
**Solución:** Usar solo `mode=base` o `mode=total`

### Error 400 - Período inválido
**Causa:** Formato de período no reconocido  
**Ejemplo de respuesta:**
```json
{
  "error": "Formato de período inválido",
  "code": "INVALID_PERIOD",
  "suggestions": [
    "Usar: current_month, last_month, current_year, last_7_days, last_30_days",
    "O formato: YYYY-MM (ej: 2025-10)",
    "O rango: YYYY-MM-DD,YYYY-MM-DD"
  ]
}
```
**Solución:** Usar formatos válidos de período

### Error 404 - Categoría no encontrada
**Causa:** `category_id` no existe o no pertenece al usuario  
**Solución:** Verificar IDs con el gráfico de categorías primero

### Error 401 - No autenticado
**Causa:** Token no válido o no enviado  
**Solución:** Verificar header `Authorization: Token xxxxx`

---

## 🧪 Casos de Prueba Específicos para HU-13

### Prueba 1: Sin datos (período sin transacciones)
```
GET {{base_url}}/api/analytics/dashboard/?period=2024-01&mode=total
```
**Resultado esperado:** Valores en 0, arrays vacíos, sin errores

### Prueba 2: Muchos datos (período con muchas transacciones)
```
GET {{base_url}}/api/analytics/expenses-chart/?period=current_year&others_threshold=0.01
```
**Resultado esperado:** Categorías agrupadas correctamente en "Otros"

### Prueba 3: Cambio de modo base/total
```
GET {{base_url}}/api/analytics/indicators/?period=current_month&mode=base
GET {{base_url}}/api/analytics/indicators/?period=current_month&mode=total
```
**Resultado esperado:** Diferencias en montos según impuestos

### Prueba 4: Transacciones sin categoría
```
GET {{base_url}}/api/analytics/category/uncategorized/transactions/?period=current_month
```
**Resultado esperado:** Lista de transacciones sin categoría asignada

---

## 🚀 Colección de Postman para HU-13

```
📁 Finanzas Backend - Analytics HU-13
  📁 Dashboard Completo
    ├─ GET Dashboard Mes Actual (Base)
    ├─ GET Dashboard Mes Actual (Total)
    ├─ GET Dashboard Mes Anterior
    └─ GET Dashboard Período Personalizado
  📁 Indicadores KPI
    ├─ GET Indicadores Base
    ├─ GET Indicadores Total
    └─ GET Indicadores Año Actual
  📁 Gráficos
    ├─ GET Gráfico Dona Categorías
    ├─ GET Gráfico Flujo Diario
    └─ GET Gráfico Con Threshold Alto
  📁 Drill-down Categorías
    ├─ GET Transacciones Comida
    ├─ GET Transacciones Transporte
    ├─ GET Transacciones Sin Categoría
    └─ GET Transacciones Con Límite
  📁 Utilidades
    ├─ GET Períodos Disponibles
    └─ GET Períodos Con Rango de Fechas
  📁 Casos Extremos
    ├─ GET Sin Datos (Período Vacío)
    ├─ GET Muchos Datos (Año Completo)
    └─ GET Errores (Parámetros Inválidos)
```

---

**¡Happy Analytics Testing! 📊📈**