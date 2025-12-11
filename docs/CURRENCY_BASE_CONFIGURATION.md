# Configuración de Moneda Base - Guía para Frontend

## 📋 Índice
- [Concepto General](#concepto-general)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Flujo de Usuario Recomendado](#flujo-de-usuario-recomendado)
- [Ejemplos de Implementación](#ejemplos-de-implementación)
- [Integración con Analytics](#integración-con-analytics)

---

## Concepto General

### ¿Qué es la Moneda Base?

La **moneda base** es una configuración **global por usuario** que define en qué moneda se mostrarán todos los totales consolidados (analytics, reportes, balances, etc.).

### Características Clave:

- ✅ **Una moneda base por usuario** (no por cuenta)
- ✅ **Independiente de las monedas de las cuentas** del usuario
- ✅ **Conversión automática**: Todas las transacciones se convierten a esta moneda
- ✅ **Valor por defecto**: `COP` si el usuario no la configura
- ✅ **Cambio instantáneo**: Al cambiar la moneda base, todos los cálculos se recalculan automáticamente

### Monedas Soportadas:

| Código | Nombre                  | Símbolo |
|--------|-------------------------|---------|
| `COP`  | Peso Colombiano         | $       |
| `USD`  | Dólar Estadounidense    | $       |
| `EUR`  | Euro                    | €       |

---

## Endpoints Disponibles

### 1. Consultar Moneda Base Actual

**GET** `/api/utils/base-currency/`

**Headers:**
```http
Authorization: Token {user_token}
```

**Respuesta (200 OK):**
```json
{
  "base_currency": "COP",
  "updated_at": "2025-12-10T15:30:00Z",
  "available_currencies": ["COP", "USD", "EUR"]
}
```

---

### 2. Cambiar Moneda Base

**PUT** `/api/utils/base-currency/set_base/`

**Headers:**
```http
Authorization: Token {user_token}
Content-Type: application/json
```

**Body:**
```json
{
  "base_currency": "USD"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "base_currency": "USD",
  "updated_at": "2025-12-10T16:45:00Z",
  "message": "Moneda base actualizada a USD. Los totales se recalcularán automáticamente."
}
```

**Errores Posibles:**

**400 Bad Request** - Moneda no soportada:
```json
{
  "base_currency": ["Moneda no soportada. Use: COP, USD, EUR"]
}
```

**401 Unauthorized** - Token inválido o ausente:
```json
{
  "detail": "Invalid token."
}
```

---

## Flujo de Usuario Recomendado

### Escenario 1: Usuario Nuevo (Primera vez)

```javascript
// 1. Usuario se registra/inicia sesión
// → Moneda base por defecto: COP

// 2. (Opcional) Mostrar configuración de moneda en perfil/configuración
GET /api/utils/base-currency/
// → { "base_currency": "COP", ... }

// 3. Si el usuario quiere cambiar:
// Mostrar selector con: ["COP", "USD", "EUR"]

// 4. Al seleccionar una moneda diferente:
PUT /api/utils/base-currency/set_base/
Body: { "base_currency": "USD" }

// 5. Mostrar mensaje de confirmación
// "Moneda base actualizada a USD. Todos tus totales se mostrarán en dólares."

// 6. Recargar datos de analytics/dashboard
GET /api/analytics/dashboard/
// → Ahora todos los valores están en USD
```

---

### Escenario 2: Usuario con Múltiples Cuentas

```javascript
// Usuario tiene:
// - Cuenta 1: Bancolombia (COP)
// - Cuenta 2: Bank of America (USD)
// - Cuenta 3: Deutsche Bank (EUR)

// Transacciones:
// - $500,000 COP desde Cuenta 1
// - $200 USD desde Cuenta 2
// - €150 EUR desde Cuenta 3

// Si moneda base = USD:
GET /api/analytics/indicators/
// Respuesta:
{
  "income": { "amount": 450.50, "formatted": "$451" },
  "expenses": { "amount": 0, "formatted": "$0" },
  "balance": { "amount": 450.50, "formatted": "$451" },
  "currency": "USD"  // ← Todo convertido a USD
}

// Conversiones aplicadas automáticamente:
// - 500,000 COP → ~$122 USD (usando tipo de cambio actual)
// - $200 USD → $200 USD (sin conversión)
// - €150 EUR → ~$165 USD (usando tipo de cambio actual)
// Total: $122 + $200 + $165 = $487 USD
```

---

## Ejemplos de Implementación

### React/TypeScript - Componente de Selector de Moneda

```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface BaseCurrencyResponse {
  base_currency: string;
  updated_at: string;
  available_currencies: string[];
}

export const CurrencySelector: React.FC = () => {
  const [baseCurrency, setBaseCurrency] = useState<string>('COP');
  const [availableCurrencies, setAvailableCurrencies] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');

  // Cargar moneda actual al montar el componente
  useEffect(() => {
    fetchCurrentCurrency();
  }, []);

  const fetchCurrentCurrency = async () => {
    try {
      const response = await axios.get<BaseCurrencyResponse>(
        '/api/utils/base-currency/',
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        }
      );
      setBaseCurrency(response.data.base_currency);
      setAvailableCurrencies(response.data.available_currencies);
    } catch (error) {
      console.error('Error al cargar moneda base:', error);
    }
  };

  const handleCurrencyChange = async (newCurrency: string) => {
    if (newCurrency === baseCurrency) return;

    setLoading(true);
    setMessage('');

    try {
      const response = await axios.put(
        '/api/utils/base-currency/set_base/',
        { base_currency: newCurrency },
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setBaseCurrency(newCurrency);
      setMessage(response.data.message);
      
      // Recargar datos de analytics/dashboard
      window.dispatchEvent(new CustomEvent('currency-changed', { 
        detail: { currency: newCurrency } 
      }));
      
    } catch (error) {
      console.error('Error al cambiar moneda:', error);
      setMessage('Error al actualizar la moneda. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="currency-selector">
      <label htmlFor="currency">Moneda Base:</label>
      <select
        id="currency"
        value={baseCurrency}
        onChange={(e) => handleCurrencyChange(e.target.value)}
        disabled={loading}
      >
        {availableCurrencies.map(currency => (
          <option key={currency} value={currency}>
            {currency}
          </option>
        ))}
      </select>
      
      {loading && <span>Actualizando...</span>}
      {message && <p className="message">{message}</p>}
    </div>
  );
};
```

---

### JavaScript Vanilla - Cambiar Moneda

```javascript
// Función para obtener moneda actual
async function getCurrentBaseCurrency() {
  const response = await fetch('/api/utils/base-currency/', {
    headers: {
      'Authorization': `Token ${localStorage.getItem('authToken')}`
    }
  });
  
  const data = await response.json();
  return data.base_currency; // "COP", "USD", o "EUR"
}

// Función para cambiar moneda base
async function changeBaseCurrency(newCurrency) {
  const response = await fetch('/api/utils/base-currency/set_base/', {
    method: 'PUT',
    headers: {
      'Authorization': `Token ${localStorage.getItem('authToken')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      base_currency: newCurrency
    })
  });

  if (!response.ok) {
    throw new Error('Error al cambiar moneda');
  }

  const data = await response.json();
  console.log(data.message); // "Moneda base actualizada a USD..."
  
  // Recargar datos de analytics
  reloadAnalytics();
}

// Ejemplo de uso
document.getElementById('currency-select').addEventListener('change', async (e) => {
  try {
    await changeBaseCurrency(e.target.value);
    alert('Moneda actualizada exitosamente');
  } catch (error) {
    alert('Error al actualizar moneda');
  }
});
```

---

### Vue.js - Composable para Moneda Base

```typescript
// composables/useBaseCurrency.ts
import { ref, Ref } from 'vue';
import axios from 'axios';

export function useBaseCurrency() {
  const baseCurrency: Ref<string> = ref('COP');
  const availableCurrencies: Ref<string[]> = ref([]);
  const loading: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);

  const fetchBaseCurrency = async () => {
    try {
      const response = await axios.get('/api/utils/base-currency/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`
        }
      });
      
      baseCurrency.value = response.data.base_currency;
      availableCurrencies.value = response.data.available_currencies;
    } catch (err) {
      error.value = 'Error al cargar moneda base';
      console.error(err);
    }
  };

  const updateBaseCurrency = async (newCurrency: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.put(
        '/api/utils/base-currency/set_base/',
        { base_currency: newCurrency },
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      baseCurrency.value = newCurrency;
      return response.data.message;
    } catch (err) {
      error.value = 'Error al actualizar moneda';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    baseCurrency,
    availableCurrencies,
    loading,
    error,
    fetchBaseCurrency,
    updateBaseCurrency
  };
}
```

---

## Integración con Analytics

### Importante: Todos los endpoints de analytics respetan la moneda base

Cuando el usuario consulta analytics, los valores **siempre** vienen en su moneda base configurada:

```javascript
// Usuario tiene moneda base = USD

// 1. Obtener indicadores
GET /api/analytics/indicators/?period=current_month
{
  "income": { "amount": 5000, "formatted": "$5,000" },
  "expenses": { "amount": 3000, "formatted": "$3,000" },
  "balance": { "amount": 2000, "formatted": "$2,000" },
  "currency": "USD"  // ← Indica que todo está en USD
}

// 2. Dashboard completo
GET /api/analytics/dashboard/?period=current_month
{
  "indicators": {
    "currency": "USD",
    "income": { ... },
    "expenses": { ... }
  },
  "expenses_chart": {
    "currency": "USD",
    "categories": [...]
  },
  "daily_flow": {
    "currency": "USD",
    "series": [...]
  }
}
```

### Recomendaciones para el Frontend:

1. **Mostrar el símbolo de moneda correcto:**
```javascript
const getCurrencySymbol = (currency) => {
  const symbols = {
    'COP': '$',
    'USD': '$',
    'EUR': '€'
  };
  return symbols[currency] || '$';
};

// Uso:
const symbol = getCurrencySymbol(response.data.currency);
console.log(`${symbol}${amount.toLocaleString()}`);
// Output: "$5,000" o "€5,000"
```

2. **Recargar datos después de cambiar moneda:**
```javascript
async function onCurrencyChange(newCurrency) {
  await changeBaseCurrency(newCurrency);
  
  // Recargar todos los componentes que muestran valores monetarios
  await Promise.all([
    fetchAnalytics(),
    fetchDashboard(),
    fetchBalances(),
    fetchReports()
  ]);
}
```

3. **Mostrar moneda en la UI:**
```html
<!-- Indicador visual de moneda activa -->
<div class="currency-badge">
  <span>Mostrando valores en: </span>
  <strong>USD</strong>
</div>
```

---

## Preguntas Frecuentes (FAQ)

### ¿La moneda base afecta las cuentas del usuario?
**No.** Las cuentas mantienen su moneda original. Solo afecta cómo se **muestran los totales consolidados**.

### ¿Puedo tener cuentas en diferentes monedas?
**Sí.** Puedes tener cuentas en COP, USD, EUR, etc. Todas se consolidarán en tu moneda base.

### ¿Qué pasa si cambio la moneda base?
Todos los totales se **recalculan automáticamente** a la nueva moneda. Los valores históricos también se convierten usando tipos de cambio.

### ¿Necesito configurar tipos de cambio?
Para conversiones básicas, **el sistema usa tasas por defecto**. Para mayor precisión, el administrador puede configurar tipos de cambio mensuales en:
```
POST /api/utils/exchange-rates/
```

### ¿Dónde debería mostrar el selector de moneda?
Recomendamos:
- **Configuración de usuario / Perfil**
- **Página de dashboard** (esquina superior derecha)
- **Primera vez** (wizard de bienvenida)

---

## Testing

### Casos de Prueba Recomendados:

```javascript
// Test 1: Verificar moneda por defecto en nuevo usuario
test('Nuevo usuario tiene COP por defecto', async () => {
  const response = await fetch('/api/utils/base-currency/', {
    headers: { 'Authorization': 'Token new_user_token' }
  });
  const data = await response.json();
  expect(data.base_currency).toBe('COP');
});

// Test 2: Cambiar moneda exitosamente
test('Cambiar moneda a USD', async () => {
  const response = await fetch('/api/utils/base-currency/set_base/', {
    method: 'PUT',
    headers: {
      'Authorization': 'Token user_token',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ base_currency: 'USD' })
  });
  expect(response.status).toBe(200);
  const data = await response.json();
  expect(data.base_currency).toBe('USD');
});

// Test 3: Rechazar moneda inválida
test('Rechazar moneda no soportada', async () => {
  const response = await fetch('/api/utils/base-currency/set_base/', {
    method: 'PUT',
    headers: {
      'Authorization': 'Token user_token',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ base_currency: 'JPY' })
  });
  expect(response.status).toBe(400);
});
```

---

## Soporte

Para más información sobre:
- **Tipos de cambio**: Ver `docs/EXCHANGE_RATES_GUIDE.md`
- **Analytics API**: Ver `docs/ANALYTICS_API_POSTMAN.md`
- **Reportes**: Ver `docs/API_REFERENCE.md`

¿Dudas? Contacta al equipo de backend.
