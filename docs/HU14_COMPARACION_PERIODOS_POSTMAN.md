"""
HU-14: Comparación Básica Entre Períodos - Guía Postman
======================================================

Esta guía explica cómo probar el nuevo endpoint de comparación entre períodos implementado para la HU-14.

## Endpoint Principal

**GET** `/api/analytics/compare-periods/`

Compara indicadores financieros (ingresos, gastos, balance) entre dos períodos específicos.

## Autenticación

Todos los endpoints requieren autenticación por token:

```
Headers:
Authorization: Token tu_token_aqui
```

## Parámetros de Query (Todos requeridos)

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `period1` | string | Período base para comparación | `2025-09` |
| `period2` | string | Período a comparar contra period1 | `2025-10` |
| `mode` | string | Modo de cálculo: "base" o "total" (opcional, default: "total") | `total` |

## Formatos de Período Soportados

### Períodos Predefinidos
- `current_month` - Mes actual
- `last_month` - Mes anterior
- `current_year` - Año actual
- `last_7_days` - Últimos 7 días
- `last_30_days` - Últimos 30 días

### Períodos Específicos
- `YYYY-MM` - Mes específico (ej: `2025-09`)
- `YYYY` - Año específico (ej: `2025`)
- `YYYY-MM-DD,YYYY-MM-DD` - Rango personalizado (ej: `2025-09-01,2025-09-30`)

## Ejemplos de Uso en Postman

### 1. Comparación Básica: Septiembre vs Octubre 2025

```
GET /api/analytics/compare-periods/?period1=2025-09&period2=2025-10&mode=total
```

**Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

### 2. Comparación Mes Anterior vs Actual (Base)

```
GET /api/analytics/compare-periods/?period1=last_month&period2=current_month&mode=base
```

### 3. Comparación con Rango Personalizado

```
GET /api/analytics/compare-periods/?period1=2025-09-01,2025-09-15&period2=2025-09-16,2025-09-30&mode=total
```

### 4. Comparación Anual

```
GET /api/analytics/compare-periods/?period1=2024&period2=2025&mode=total
```

## Estructura de Respuesta Exitosa

```json
{
  "success": true,
  "data": {
    "comparison_summary": {
      "period1": {
        "name": "September 2025",
        "date_range": "01/09/2025 - 30/09/2025",
        "has_data": true,
        "transactions_count": 15
      },
      "period2": {
        "name": "October 2025", 
        "date_range": "01/10/2025 - 31/10/2025",
        "has_data": true,
        "transactions_count": 18
      },
      "can_compare": true,
      "mode": "total"
    },
    "period_data": {
      "period1": {
        "income": {"amount": 250000, "count": 3, "formatted": "$2.500.000"},
        "expenses": {"amount": 180000, "count": 12, "formatted": "$1.800.000"},
        "balance": {"amount": 70000, "formatted": "$700.000", "is_positive": true}
      },
      "period2": {
        "income": {"amount": 300000, "count": 4, "formatted": "$3.000.000"},
        "expenses": {"amount": 160000, "count": 14, "formatted": "$1.600.000"}, 
        "balance": {"amount": 140000, "formatted": "$1.400.000", "is_positive": true}
      }
    },
    "differences": {
      "income": {
        "absolute": 50000,
        "percentage": 20.0,
        "is_increase": true,
        "is_significant": true,
        "period1_amount": 250000,
        "period2_amount": 300000,
        "formatted_absolute": "$500.000",
        "summary": "Ingresos +20.0% (+$500.000)"
      },
      "expenses": {
        "absolute": -20000,
        "percentage": -11.1,
        "is_increase": false,
        "is_significant": true,
        "period1_amount": 180000,
        "period2_amount": 160000,
        "formatted_absolute": "$200.000",
        "summary": "Gastos -11.1% (-$200.000)"
      },
      "balance": {
        "absolute": 70000,
        "percentage": 100.0,
        "is_increase": true,
        "is_significant": true,
        "period1_amount": 70000,
        "period2_amount": 140000,
        "formatted_absolute": "$700.000",
        "summary": "Balance +100.0% (+$700.000)"
      }
    },
    "insights": {
      "messages": [
        "Excelente: Los ingresos aumentaron 20.0%.",
        "Bien: Los gastos disminuyeron 11.1%.",
        "Situación financiera muy mejorada."
      ],
      "alert_level": "success",
      "has_significant_changes": true
    },
    "metadata": {
      "generated_at": "2025-11-25",
      "comparison_mode": "total",
      "currency": "COP"
    }
  },
  "message": "Comparación completada: September 2025 vs October 2025",
  "executive_summary": [
    "Ingresos +20.0% (+$500.000)",
    "Gastos -11.1% (-$200.000)",
    "Balance +100.0% (+$700.000)"
  ]
}
```

## Casos de Error Comunes

### 1. Parámetros Faltantes

**Request:**
```
GET /api/analytics/compare-periods/?period1=2025-09
```

**Response:**
```json
{
  "success": false,
  "error": "Parámetros period1 y period2 son requeridos",
  "code": "MISSING_PERIODS",
  "details": {
    "provided": {
      "period1": "2025-09",
      "period2": null
    },
    "examples": [
      "?period1=2025-09&period2=2025-10&mode=total",
      "?period1=last_month&period2=current_month&mode=base"
    ]
  }
}
```

### 2. Formato de Período Inválido

**Request:**
```
GET /api/analytics/compare-periods/?period1=septiembre&period2=octubre
```

**Response:**
```json
{
  "success": false,
  "error": "Formato de período inválido",
  "code": "INVALID_PERIOD_FORMAT",
  "details": {
    "period1_provided": "septiembre",
    "period2_provided": "octubre",
    "error": "time data 'septiembre' does not match any expected format"
  },
  "supported_formats": [
    "current_month, last_month, current_year",
    "YYYY-MM (ej: 2025-10)",
    "YYYY (ej: 2025)",
    "YYYY-MM-DD,YYYY-MM-DD (rango personalizado)"
  ]
}
```

### 3. Sin Datos en Uno de los Períodos

**Request:**
```
GET /api/analytics/compare-periods/?period1=2025-01&period2=2025-12&mode=total
```

**Response:**
```json
{
  "success": false,
  "error": "No hay datos en el segundo período (2025-12)",
  "code": "NO_DATA_PERIOD2",
  "details": {
    "comparison_summary": {
      "period1": {"has_data": true, "transactions_count": 10},
      "period2": {"has_data": false, "transactions_count": 0},
      "can_compare": false
    },
    "total_user_transactions": 45,
    "suggestion": "Intenta con períodos que tengan transacciones registradas"
  }
}
```

### 4. Usuario Sin Transacciones

**Response:**
```json
{
  "success": false,
  "error": "No tienes transacciones para comparar períodos",
  "code": "NO_USER_TRANSACTIONS",
  "details": {
    "message": "Necesitas crear transacciones antes de poder hacer comparaciones",
    "suggestions": [
      "Crea transacciones con POST /api/transactions/",
      "Asigna categorías a tus transacciones", 
      "Intenta la comparación nuevamente"
    ]
  }
}
```

## Interpretación de Resultados

### Niveles de Alerta (alert_level)
- `success`: Situación financiera mejorada
- `info`: Cambios mínimos o neutros
- `warning`: Atención requerida (gastos altos, ingresos bajos)
- `error`: Situación preocupante

### Significancia de Cambios
- `is_significant`: true cuando el cambio es >= 5%
- Cambios < 5% se consideran mínimos

### Ejemplos de Interpretación

```json
"summary": "Gastos -12% ($-85.000)"
```
- Los gastos disminuyeron 12% 
- Ahorro de $85.000 en el período 2 vs período 1

```json
"summary": "Ingresos +21% ($+310.000)"
```  
- Los ingresos aumentaron 21%
- Incremento de $310.000 en el período 2 vs período 1

## Collection Postman Sugerida

### Environment Variables
```json
{
  "base_url": "http://localhost:8000/api",
  "auth_token": "tu_token_aqui"
}
```

### Requests de Prueba

1. **Setup - Obtener Token**
   - `POST {{base_url}}/auth/login/`
   - Guarda el token en `auth_token`

2. **Comparación Básica**
   - `GET {{base_url}}/analytics/compare-periods/?period1=last_month&period2=current_month&mode=total`

3. **Comparación Específica**
   - `GET {{base_url}}/analytics/compare-periods/?period1=2025-09&period2=2025-10&mode=base`

4. **Test Error - Parámetros Faltantes** 
   - `GET {{base_url}}/analytics/compare-periods/?period1=2025-09`

5. **Test Error - Formato Inválido**
   - `GET {{base_url}}/analytics/compare-periods/?period1=invalid&period2=also-invalid`

## Flujo de Trabajo Recomendado

1. **Verificar Datos Disponibles**
   ```
   GET /api/analytics/periods/
   ```

2. **Ver Dashboard Actual**
   ```
   GET /api/analytics/dashboard/?period=current_month&mode=total
   ```

3. **Comparar Períodos**
   ```
   GET /api/analytics/compare-periods/?period1=last_month&period2=current_month&mode=total
   ```

4. **Análisis Detallado por Categoría**
   ```
   GET /api/analytics/expenses-chart/?period=current_month&mode=total
   ```

## Casos de Uso Ejemplo

### Caso 1: Comparación Mensual Regular
- **Objetivo**: Ver cómo cambiaron las finanzas del mes pasado al actual
- **URL**: `?period1=last_month&period2=current_month&mode=total`
- **Uso**: Dashboard mensual, reportes automáticos

### Caso 2: Análisis Estacional
- **Objetivo**: Comparar mismo mes del año anterior
- **URL**: `?period1=2024-11&period2=2025-11&mode=total`  
- **Uso**: Identificar patrones estacionales

### Caso 3: Evaluación de Cambios de Hábito
- **Objetivo**: Ver impacto de nuevos hábitos financieros
- **URL**: `?period1=2025-09-01,2025-09-15&period2=2025-09-16,2025-09-30&mode=base`
- **Uso**: Medir efectividad de presupuesto o meta

### Caso 4: Reporte Trimestral
- **Objetivo**: Comparar trimestres completos
- **URL**: `?period1=2025-07-01,2025-09-30&period2=2025-10-01,2025-12-31&mode=total`
- **Uso**: Reportes ejecutivos, planificación

## Notas de Implementación

- Los valores están en centavos internamente, pero se muestran formateados en pesos
- El modo "base" excluye impuestos, "total" los incluye
- Las diferencias porcentuales se calculan: `(periodo2 - periodo1) / |periodo1| * 100`
- Los insights se generan automáticamente basados en umbrales configurables
- Las comparaciones son siempre: período2 vs período1 (período2 es el "actual")

## Testing con Datos de Ejemplo

Para probar completamente, necesitas:

1. **Crear transacciones de prueba**:
```json
POST /api/transactions/
{
  "origin_account": 1,
  "category": 1,
  "description": "Salario Septiembre",
  "base_amount": 500000,
  "type": 1,
  "date": "2025-09-01"
}
```

2. **Crear gastos en diferentes períodos**:
```json
POST /api/transactions/
{
  "origin_account": 1, 
  "category": 2,
  "description": "Supermercado Octubre",
  "base_amount": 15000,
  "type": 2,
  "date": "2025-10-15"
}
```

3. **Comparar los períodos** con los endpoints de comparación

Esto te permitirá ver todos los casos: períodos con datos, sin datos, y diferentes niveles de cambio.
"""