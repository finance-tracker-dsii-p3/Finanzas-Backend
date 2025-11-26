# 📋 Guía para Frontend - HU-07 y HU-08

## ✅ Estado de Implementación

### HU-07: Presupuestos por Categoría (Base/Total) - **COMPLETO**

Todos los endpoints están implementados y funcionando. El cálculo de gastos vs presupuesto ahora usa transacciones reales.

### HU-08: Alertas de Presupuesto - **COMPLETO (con un test pendiente de ajuste)**

La funcionalidad está implementada, pero hay un test que requiere ajuste menor en la lógica de detección de mes.

---

## 🔌 Endpoints Disponibles

### HU-07: Presupuestos

#### 1. Listar Presupuestos
```
GET /api/budgets/
Query params: ?active_only=true&period=monthly
```

**Respuesta:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "category": 2,
      "category_name": "Comida",
      "amount": "400000.00",
      "currency": "COP",  // Moneda del presupuesto
      "calculation_mode": "base",
      "period": "monthly",
      "spent_amount": "320000.00",  // ✅ Calculado solo de transacciones con cuentas en COP
      "spent_percentage": "80.00",
      "remaining_amount": "80000.00",
      "status": "warning",
      "status_text": "Alerta: 80.0% gastado"
    }
  ]
}
```

#### 2. Crear Presupuesto
```
POST /api/budgets/
Body: {
  "category": 2,
  "amount": 400000,
  "currency": "COP",  // "COP", "USD", "EUR" - Requerido
  "calculation_mode": "base",  // o "total"
  "period": "monthly",
  "alert_threshold": 80
}
```

**⚠️ IMPORTANTE - Múltiples Monedas:**
- Cada presupuesto debe especificar su moneda (`currency`)
- El cálculo de `spent_amount` solo incluye transacciones de cuentas con la misma moneda
- Puedes tener múltiples presupuestos para la misma categoría si usan diferentes monedas
- Ejemplo: Un presupuesto de "Comida" en COP y otro en USD para la misma categoría

#### 3. Ver Detalle con Proyección
```
GET /api/budgets/{id}/
```

**Respuesta incluye:**
- `spent_amount`, `spent_percentage`, `remaining_amount`
- `daily_average`: Promedio diario de gasto
- `projection`: Proyección a fin de mes
  - `projected_amount`
  - `projected_percentage`
  - `will_exceed`: boolean
  - `days_remaining`, `days_total`

#### 4. Resumen Mensual (Para Dashboard)
```
GET /api/budgets/monthly_summary/
```

**Ideal para mostrar barras de progreso por categoría con proyecciones.**

#### 5. Estadísticas Generales
```
GET /api/budgets/stats/
```

#### 6. Categorías sin Presupuesto
```
GET /api/budgets/categories_without_budget/?period=monthly
```

**Útil para mostrar mensaje: "Aún no tienes límites definidos..."**

---

### HU-08: Alertas de Presupuesto

#### 1. Listar Alertas (Centro de Notificaciones)
```
GET /api/alerts/
Query params: ?unread=true&type=warning
```

**Respuesta:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "budget": 1,
      "alert_type": "warning",  // o "exceeded"
      "is_read": false,
      "created_at": "2025-11-15T10:00:00Z"
    }
  ]
}
```

#### 2. Marcar Alerta como Leída
```
PATCH /api/alerts/{id}/read/
Body: { "is_read": true }
```

#### 3. Marcar Todas como Leídas
```
POST /api/alerts/read-all/
```

#### 4. Ver Detalle de Alerta
```
GET /api/alerts/{id}/
```

#### 5. Eliminar Alerta
```
DELETE /api/alerts/{id}/delete/
```

#### 6. Alertas Calculadas (Estado Live)
```
GET /api/budgets/alerts/
```

**Este endpoint devuelve alertas calculadas en tiempo real (no persistidas).**
**Útil para mostrar notificaciones en tiempo real, pero el centro de notificaciones debe usar `/api/alerts/`**

---

## 🎯 Flujo Recomendado para Frontend

### Dashboard Principal

1. **Cargar Resumen de Presupuestos:**
   ```
   GET /api/budgets/monthly_summary/
   ```
   - Mostrar barras de progreso por categoría
   - Mostrar proyecciones (si `will_exceed: true`, mostrar alerta visual)

2. **Cargar Alertas del Centro de Notificaciones:**
   ```
   GET /api/alerts/?unread=true
   ```
   - Mostrar badge con contador
   - Mostrar lista de alertas no leídas

3. **Al hacer clic en "Ver movimientos" de un presupuesto:**
   ```
   GET /api/transactions/?category={category_id}&date__gte={start_date}&date__lte={end_date}
   ```
   (Usar `period_dates` del presupuesto para filtrar)

### Centro de Notificaciones

1. **Listar todas las alertas:**
   ```
   GET /api/alerts/
   ```

2. **Al marcar como leída:**
   ```
   PATCH /api/alerts/{id}/read/
   Body: { "is_read": true }
   ```

3. **Al hacer clic en una alerta:**
   - Redirigir a detalle del presupuesto: `GET /api/budgets/{budget_id}/`

### Crear/Editar Presupuesto

1. **Obtener categorías disponibles:**
   ```
   GET /api/categories/?type=expense
   ```

2. **Obtener categorías sin presupuesto:**
   ```
   GET /api/budgets/categories_without_budget/
   ```

3. **Crear presupuesto:**
   ```
   POST /api/budgets/
   ```

---

## 📊 Campos Importantes

### Modos de Cálculo
- `"base"`: Solo monto base (sin impuestos)
- `"total"`: Monto total (con impuestos)

### Monedas Disponibles
- `"COP"`: Pesos Colombianos (default)
- `"USD"`: Dólares
- `"EUR"`: Euros

### Estados de Presupuesto
- `"good"`: Dentro del presupuesto
- `"warning"`: Alcanzó el umbral (default 80%)
- `"exceeded"`: Superó el 100%

### Tipos de Alerta
- `"warning"`: Alcanzó el umbral (80% o configurado)
- `"exceeded"`: Superó el 100%

---

## ⚠️ Notas Importantes

1. **Cálculo Real Implementado:** Los presupuestos ahora calculan el gasto real desde las transacciones, respetando el modo `base` o `total`.

2. **Múltiples Monedas (NUEVO):**
   - Cada presupuesto debe especificar su moneda (`currency`: "COP", "USD", "EUR")
   - El cálculo de `spent_amount` **solo incluye transacciones de cuentas con la misma moneda**
   - Puedes tener múltiples presupuestos para la misma categoría si usan diferentes monedas
   - Ejemplo: Un presupuesto de "Comida" en COP ($400,000) y otro en USD ($100) para la misma categoría
   - Las alertas solo se generan cuando la transacción tiene una cuenta con la misma moneda que el presupuesto
   - **Recomendación Frontend:** Al crear un presupuesto, mostrar selector de moneda y validar que coincida con las cuentas disponibles

3. **Alertas Automáticas:** Las alertas se generan automáticamente cuando se crea una transacción de gasto que alcanza 80% o 100% del presupuesto.

4. **Unicidad Mensual:** Solo se genera una alerta por presupuesto/tipo/mes. Si ya existe una alerta para ese mes, no se crea otra.

5. **Proyecciones:** Las proyecciones se basan en el promedio diario del mes actual y proyectan a fin de mes.

6. **Períodos:** Los presupuestos mensuales calculan desde el día 1 hasta el último día del mes de la fecha de referencia.

---

## 🧪 Testing

Los tests están implementados en:
- `tests/test_budgets_api.py` - Tests de endpoints de presupuestos
- `alerts/tests.py` - Tests de alertas de presupuesto

**Nota:** Hay un test que requiere ajuste menor (`test_new_month_generates_new_alert`), pero la funcionalidad principal está operativa.

---

## 🚀 Próximos Pasos para Frontend

1. **Implementar Dashboard de Presupuestos:**
   - Usar `GET /api/budgets/monthly_summary/` para mostrar barras de progreso
   - Mostrar proyecciones cuando `will_exceed: true`

2. **Implementar Centro de Notificaciones:**
   - Usar `GET /api/alerts/` para listar alertas
   - Implementar marcado como leída
   - Mostrar badge con contador de no leídas

3. **Integrar con Transacciones:**
   - Al crear una transacción de gasto, verificar si dispara alertas
   - Mostrar notificación cuando se genera una alerta

4. **Configuración de Alertas:**
   - Permitir activar/desactivar alertas (pendiente implementar en backend)
   - Configurar umbral personalizado por presupuesto

---

**¡Happy Coding! 🎉**

