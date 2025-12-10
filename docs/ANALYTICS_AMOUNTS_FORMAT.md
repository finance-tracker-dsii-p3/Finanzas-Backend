# Analytics API - Formato de Montos (URGENTE)

## 🚨 Información Crítica para Frontend

### Pregunta: ¿En qué unidad viene el campo `amount`?

**Respuesta: CENTAVOS** ✅

Todos los campos `amount` en los endpoints de analytics vienen en **centavos**, NO en pesos/dólares/euros.

---

## 📊 Ejemplo Real

Para una transacción de **$600,000 COP**:

### Respuesta del Backend:
```json
{
  "income": {
    "amount": 60000000,        // ← 60,000,000 centavos
    "count": 1,
    "formatted": "$60,000,000" // ⚠️ INCORRECTO (bug en el backend)
  },
  "expenses": {
    "amount": 0,
    "count": 0,
    "formatted": "$0"
  },
  "balance": {
    "amount": 60000000,
    "formatted": "$60,000,000",
    "is_positive": true
  },
  "currency": "COP"
}
```

### Conversión:
```
60,000,000 centavos ÷ 100 = 600,000 pesos
```

---

## ⚠️ Problema Detectado

### Campo `formatted` tiene un BUG

El campo `formatted` del backend está mostrando los centavos directamente sin dividir entre 100:

| Campo | Valor Actual | Valor Esperado |
|-------|--------------|----------------|
| `amount` | `60000000` ✅ | `60000000` |
| `formatted` | `"$60,000,000"` ❌ | `"$600,000"` |

**Recomendación: NO usar el campo `formatted` del backend por ahora.**

---

## 💡 Solución para el Frontend

### Opción 1: Convertir y formatear manualmente (Recomendada)

```javascript
// Función helper para convertir centavos a moneda formateada
function formatAmount(centavos, currency = 'COP') {
  // Convertir centavos a unidad monetaria
  const amount = centavos / 100;
  
  // Formatear según la moneda
  const locale = {
    'COP': 'es-CO',
    'USD': 'en-US',
    'EUR': 'de-DE'
  }[currency] || 'es-CO';
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
}

// Uso:
const response = await fetch('/api/analytics/indicators/');
const data = await response.json();

const incomeFormatted = formatAmount(data.income.amount, data.currency);
console.log(incomeFormatted); // "$600.000" para COP o "$600" para USD
```

### Opción 2: Función simple

```javascript
function centavosAPesos(centavos) {
  return centavos / 100;
}

function formatearMoneda(pesos, moneda = 'COP') {
  const simbolo = moneda === 'USD' ? '$' : moneda === 'EUR' ? '€' : '$';
  return `${simbolo}${pesos.toLocaleString('es-CO')}`;
}

// Uso:
const pesos = centavosAPesos(data.income.amount); // 600000
const texto = formatearMoneda(pesos, data.currency); // "$600.000"
```

### Opción 3: TypeScript Helper

```typescript
interface AmountData {
  amount: number;      // En centavos
  count: number;
  formatted: string;   // ⚠️ No usar por ahora
}

interface AnalyticsResponse {
  income: AmountData;
  expenses: AmountData;
  balance: AmountData & { is_positive: boolean };
  currency: 'COP' | 'USD' | 'EUR';
}

class CurrencyFormatter {
  private static readonly LOCALES = {
    COP: 'es-CO',
    USD: 'en-US',
    EUR: 'de-DE'
  };

  static centsToCurrency(cents: number): number {
    return cents / 100;
  }

  static format(cents: number, currency: string): string {
    const amount = this.centsToCurrency(cents);
    const locale = this.LOCALES[currency as keyof typeof this.LOCALES] || 'es-CO';
    
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }
}

// Uso:
const response: AnalyticsResponse = await fetchAnalytics();
const incomeAmount = CurrencyFormatter.centsToCurrency(response.income.amount);
const incomeFormatted = CurrencyFormatter.format(response.income.amount, response.currency);
```

---

## 📋 Tabla de Conversión Rápida

| Centavos (Backend) | Pesos/Dólares/Euros | Formato Visual |
|--------------------|---------------------|----------------|
| `10000` | `100` | $100 |
| `50000` | `500` | $500 |
| `100000` | `1,000` | $1.000 |
| `1000000` | `10,000` | $10.000 |
| `10000000` | `100,000` | $100.000 |
| `60000000` | `600,000` | $600.000 |
| `100000000` | `1,000,000` | $1.000.000 |

**Fórmula:** `valor_en_moneda = centavos ÷ 100`

---

## 🔍 Endpoints Afectados

Todos estos endpoints retornan `amount` en **centavos** y ahora incluyen el campo `currency`:

### 1. `/api/analytics/indicators/`
```json
{
  "income": { "amount": 60000000 },      // centavos
  "expenses": { "amount": 30000000 },    // centavos
  "balance": { "amount": 30000000 },     // centavos
  "currency": "EUR"                      // ✅ Moneda base del usuario
}
```

### 2. `/api/analytics/dashboard/`
```json
{
  "indicators": {
    "income": { "amount": 60000000 },
    "expenses": { "amount": 30000000 },
    "currency": "EUR"                    // ✅ Incluido
  }
}
```

### 3. `/api/analytics/expenses-chart/`
```json
{
  "categories": [
    {
      "name": "Comida",
      "amount": 15000000,  // centavos
      "percentage": 50
    }
  ],
  "total": 30000000,     // centavos
  "currency": "EUR"      // ✅ Incluido
}
```

### 4. `/api/analytics/daily-flow-chart/`
```json
{
  "series": {
    "income": {
      "total": 60000000,  // centavos
      "data": [
        { "date": "2025-12-01", "amount": 10000000 }  // centavos
      ]
    }
  },
  "currency": "EUR"      // ✅ AHORA INCLUIDO
}
```

### 5. `/api/analytics/compare-periods/`
```json
{
  "period1": {
    "income": 50000000,    // centavos
    "expenses": 30000000   // centavos
  },
  "period2": {
    "income": 60000000,    // centavos
    "expenses": 35000000   // centavos
  },
  "metadata": {
    "currency": "EUR"      // ✅ AHORA INCLUIDO (antes estaba hardcoded a "COP")
  }
}
```

---

## 🎯 Checklist para Implementación

- [ ] Crear función helper `centavosAMoneda(centavos)`
- [ ] Crear función `formatearMoneda(monto, moneda)`
- [ ] **NO usar** el campo `formatted` del backend
- [ ] Siempre dividir `amount` entre 100 antes de mostrar
- [ ] Usar `Intl.NumberFormat` para formateo correcto por país
- [ ] Respetar el campo `currency` de la respuesta
- [ ] Probar con diferentes monedas (COP, USD, EUR)

---

## 🧪 Testing

### Test 1: Conversión básica
```javascript
test('Convertir centavos a pesos', () => {
  const centavos = 60000000;
  const pesos = centavos / 100;
  expect(pesos).toBe(600000);
});
```

### Test 2: Formato COP
```javascript
test('Formatear moneda COP', () => {
  const centavos = 60000000;
  const formatted = formatAmount(centavos, 'COP');
  expect(formatted).toMatch(/600[.,]000/); // "$600.000" o "$600,000"
});
```

### Test 3: Formato USD
```javascript
test('Formatear moneda USD', () => {
  const centavos = 60000;
  const formatted = formatAmount(centavos, 'USD');
  expect(formatted).toBe('$600');
});
```

### Test 4: Formato EUR
```javascript
test('Formatear moneda EUR', () => {
  const centavos = 60000;
  const formatted = formatAmount(centavos, 'EUR');
  expect(formatted).toMatch(/600.*€/);
});
```

---

## 🐛 Bug Report al Backend

**Estado:** Identificado, pendiente de corrección

**Descripción:** El campo `formatted` en la respuesta de analytics muestra los centavos directamente sin dividir entre 100.

**Impacto:** Bajo (el frontend puede ignorar este campo y formatear manualmente)

**Ejemplo:**
- Backend retorna: `"formatted": "$60,000,000"`
- Debería retornar: `"formatted": "$600,000"`

**Workaround:** Usar el campo `amount` y formatear en el frontend.

---

## 📞 Contacto

Si tienes dudas sobre:
- Conversión de montos
- Formatos de moneda
- Comportamiento de la API

Contacta al equipo de backend.

---

## 📚 Referencias

- [Documentación de Intl.NumberFormat](https://developer.mozilla.org/es/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat)
- [Configuración de moneda base](./CURRENCY_BASE_CONFIGURATION.md)
- [API Reference completa](./API_REFERENCE.md)

---

## 📝 Changelog

### v1.2 - 10 de diciembre de 2025
**🐛 BUG CRÍTICO CORREGIDO: Conversión de monedas en daily-flow-chart**

Se corrigió un bug crítico en `/api/analytics/daily-flow-chart/` donde **NO se estaba convirtiendo los montos a la moneda base del usuario**.

**Problema:**
- El endpoint sumaba directamente los montos sin considerar la moneda de cada transacción
- Si el usuario tenía transacciones en COP, USD y EUR, las sumaba sin convertir
- Los demás endpoints (`indicators`, `expenses-chart`) SÍ hacían la conversión correctamente

**Solución:**
- Ahora agrupa transacciones por fecha, tipo **Y moneda**
- Convierte cada monto a la `base_currency` del usuario usando `FxService`
- Consistente con el comportamiento de todos los demás endpoints

**Impacto:**
- ✅ Los gráficos de flujo diario ahora muestran valores correctos en la moneda base
- ✅ Coherencia con los demás endpoints de analytics
- ✅ Soporte correcto para usuarios con cuentas en múltiples monedas

---

### v1.1 - 10 de diciembre de 2025
**✅ Campo `currency` agregado a todos los endpoints**

Se corrigieron los siguientes endpoints para que TODOS retornen el campo `currency`:

1. ✅ `/api/analytics/indicators/` - Ya lo tenía
2. ✅ `/api/analytics/expenses-chart/` - **AGREGADO**
3. ✅ `/api/analytics/daily-flow-chart/` - **AGREGADO**
4. ✅ `/api/analytics/compare-periods/` - **CORREGIDO** (antes estaba hardcoded a "COP")

**Impacto para el frontend:**
- Ahora el campo `currency` está disponible en TODOS los endpoints de analytics
- Ya no es necesario hacer workarounds para obtener la moneda
- La moneda siempre refleja la **moneda base configurada por el usuario**

---

**Última actualización:** 10 de diciembre de 2025  
**Versión:** 1.2  
**Autor:** Backend Team
