# Exchange Rates API - Guía para Frontend

## 📚 Índice

- [Introducción](#introducción)
- [Conceptos Clave](#conceptos-clave)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Casos de Uso](#casos-de-uso)
- [Ejemplos de Código](#ejemplos-de-código)
- [Validaciones y Errores](#validaciones-y-errores)
- [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Introducción

Esta guía explica cómo gestionar tipos de cambio personalizados en el sistema. Los tipos de cambio permiten:

- ✅ Definir tasas de conversión mensuales entre monedas
- ✅ Mantener histórico de tasas por mes y año
- ✅ Sobrescribir las tasas predeterminadas del sistema
- ✅ Consultar tasas vigentes para una fecha específica

---

## 💡 Conceptos Clave

### 1. **Tipos de cambio mensuales**
- Se definen por: `base_currency`, `currency`, `year`, `month`
- Ejemplo: USD/COP para enero 2025 = 4000
- Si no existe tasa para un mes, se usa la última disponible anterior

### 2. **Moneda base vs Moneda destino**
- **Base currency** (base_currency): La moneda de referencia (ej: COP)
- **Currency** (currency): La moneda que se quiere convertir (ej: USD)
- **Rate**: Cuántas unidades de base_currency equivalen a 1 unidad de currency
  - Ejemplo: `rate: 4000.00` → 1 USD = 4000 COP

### 3. **Tasas predeterminadas vs personalizadas**
- El sistema tiene tasas estáticas predeterminadas
- Los usuarios pueden crear tasas personalizadas que sobrescriben las predeterminadas
- Las tasas personalizadas tienen prioridad sobre las predeterminadas

### 4. **Formato de montos**
- **IMPORTANTE**: Los montos se manejan en **centavos** (multiplicados por 100)
- Ejemplo: $100 USD = 10000 centavos
- Resultado de conversión también viene en centavos

---

## 🔌 Endpoints Disponibles

### Base URL
```
http://127.0.0.1:8000/api/utils/exchange-rates/
```

---

### 1. **Listar tipos de cambio**

#### `GET /api/utils/exchange-rates/`

Lista todos los tipos de cambio con filtros opcionales.

**Query Parameters:**
- `currency` (opcional): Filtrar por moneda (USD, EUR, COP)
- `base_currency` (opcional): Filtrar por moneda base
- `year` (opcional): Filtrar por año
- `month` (opcional): Filtrar por mes (1-12)

**Ejemplo de request:**
```http
GET /api/utils/exchange-rates/?currency=USD&year=2025
Authorization: Token YOUR_TOKEN
```

**Ejemplo de response:**
```json
[
  {
    "id": 1,
    "base_currency": "COP",
    "currency": "USD",
    "year": 2025,
    "month": 1,
    "rate": "4000.000000",
    "source": "manual",
    "created_at": "2025-12-10T10:30:00Z",
    "updated_at": "2025-12-10T10:30:00Z"
  },
  {
    "id": 2,
    "base_currency": "COP",
    "currency": "USD",
    "year": 2025,
    "month": 2,
    "rate": "4100.000000",
    "source": "manual",
    "created_at": "2025-12-10T11:00:00Z",
    "updated_at": "2025-12-10T11:00:00Z"
  }
]
```

---

### 2. **Crear tipo de cambio**

#### `POST /api/utils/exchange-rates/`

Crea un nuevo tipo de cambio mensual.

**Request Body:**
```json
{
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 12,
  "rate": "4250.50",
  "source": "manual"
}
```

**Campos:**
- `base_currency` (requerido): Moneda base (COP, USD, EUR)
- `currency` (requerido): Moneda a convertir (COP, USD, EUR)
- `year` (requerido): Año (2000 - año actual + 10)
- `month` (requerido): Mes (1-12)
- `rate` (requerido): Tasa de cambio (debe ser > 0)
- `source` (opcional): Origen de la tasa (default: "manual")

**Ejemplo de response:**
```json
{
  "id": 3,
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 12,
  "rate": "4250.500000",
  "source": "manual",
  "created_at": "2025-12-10T15:30:00Z",
  "updated_at": "2025-12-10T15:30:00Z"
}
```

**Códigos de estado:**
- `201 Created`: Tipo de cambio creado exitosamente
- `400 Bad Request`: Datos inválidos
- `401 Unauthorized`: Token no válido

---

### 3. **Obtener tipo de cambio específico**

#### `GET /api/utils/exchange-rates/{id}/`

Obtiene los detalles de un tipo de cambio por su ID.

**Ejemplo de request:**
```http
GET /api/utils/exchange-rates/1/
Authorization: Token YOUR_TOKEN
```

**Ejemplo de response:**
```json
{
  "id": 1,
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 1,
  "rate": "4000.000000",
  "source": "manual",
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T10:30:00Z"
}
```

---

### 4. **Actualizar tipo de cambio**

#### `PUT /api/utils/exchange-rates/{id}/`
#### `PATCH /api/utils/exchange-rates/{id}/`

Actualiza un tipo de cambio existente.

**PUT Request (actualización completa):**
```json
{
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 1,
  "rate": "4050.00",
  "source": "banco_central"
}
```

**PATCH Request (actualización parcial):**
```json
{
  "rate": "4050.00",
  "source": "banco_central"
}
```

**Ejemplo de response:**
```json
{
  "id": 1,
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 1,
  "rate": "4050.000000",
  "source": "banco_central",
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T16:00:00Z"
}
```

**Códigos de estado:**
- `200 OK`: Actualización exitosa
- `400 Bad Request`: Datos inválidos
- `404 Not Found`: Tipo de cambio no encontrado

---

### 5. **Eliminar tipo de cambio**

#### `DELETE /api/utils/exchange-rates/{id}/`

Elimina un tipo de cambio existente.

**Ejemplo de request:**
```http
DELETE /api/utils/exchange-rates/1/
Authorization: Token YOUR_TOKEN
```

**Códigos de estado:**
- `204 No Content`: Eliminación exitosa
- `404 Not Found`: Tipo de cambio no encontrado

---

### 6. **Consultar tasa vigente**

#### `GET /api/utils/exchange-rates/current/`

Obtiene la tasa de cambio vigente para una moneda en una fecha específica.

**Query Parameters:**
- `currency` (requerido): Moneda a consultar (USD, EUR, etc.)
- `base` (opcional): Moneda base (si no se especifica, usa la del usuario)
- `date` (opcional): Fecha en formato YYYY-MM-DD (si no se especifica, usa hoy)

**Ejemplo de request:**
```http
GET /api/utils/exchange-rates/current/?currency=USD&base=COP&date=2025-01-15
Authorization: Token YOUR_TOKEN
```

**Ejemplo de response:**
```json
{
  "currency": "USD",
  "base_currency": "COP",
  "rate": 4000.0,
  "reference_date": "2025-01-15",
  "year": 2025,
  "month": 1,
  "warning": null
}
```

**Con advertencia (cuando usa tasa predeterminada):**
```json
{
  "currency": "USD",
  "base_currency": "COP",
  "rate": 4000.0,
  "reference_date": "2025-01-15",
  "year": 2025,
  "month": 1,
  "warning": "Usando tasa predeterminada. No hay ExchangeRate para USD/COP 2025-01"
}
```

---

### 7. **Convertir monto**

#### `GET /api/utils/exchange-rates/convert/`

Convierte un monto entre dos monedas para una fecha específica.

**Query Parameters:**
- `amount` (requerido): Monto en centavos a convertir
- `from` (requerido): Moneda origen
- `to` (opcional): Moneda destino (usa moneda base del usuario si no se especifica)
- `date` (opcional): Fecha en formato YYYY-MM-DD (usa hoy si no se especifica)

**Ejemplo de request:**
```http
GET /api/utils/exchange-rates/convert/?amount=10000&from=USD&to=COP&date=2025-01-15
Authorization: Token YOUR_TOKEN
```

**Explicación:**
- `amount=10000` → $100.00 USD (10000 centavos)

**Ejemplo de response:**
```json
{
  "original_amount": 10000,
  "original_currency": "USD",
  "converted_amount": 40000000,
  "converted_currency": "COP",
  "rate": 4000.0,
  "reference_date": "2025-01-15",
  "warning": null
}
```

**Explicación de resultado:**
- `converted_amount=40000000` → $400,000.00 COP (40000000 centavos)
- Cálculo: 10000 centavos USD × 4000 tasa = 40000000 centavos COP
- En pesos: $100 USD × 4000 = $400,000 COP ✅

---

## 📋 Casos de Uso

### Caso 1: Configurar tasas de cambio para el año

```javascript
// Configurar tasas mensuales de USD/COP para 2025
const rates = [
  { month: 1, rate: 4000 },
  { month: 2, rate: 4100 },
  { month: 3, rate: 4050 },
  // ... resto de meses
];

async function setupYearlyRates() {
  for (const { month, rate } of rates) {
    await fetch('http://127.0.0.1:8000/api/utils/exchange-rates/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        base_currency: 'COP',
        currency: 'USD',
        year: 2025,
        month: month,
        rate: rate,
        source: 'manual'
      })
    });
  }
}
```

---

### Caso 2: Consultar tasa actual antes de crear transacción

```javascript
async function getCurrentRate(currency) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/utils/exchange-rates/current/?currency=${currency}`,
    {
      headers: { 'Authorization': `Token ${token}` }
    }
  );
  
  const data = await response.json();
  
  if (data.warning) {
    console.warn(`⚠️ ${data.warning}`);
  }
  
  return data.rate;
}

// Uso
const rate = await getCurrentRate('USD');
console.log(`Tasa actual USD/COP: ${rate}`);
```

---

### Caso 3: Convertir monto antes de mostrar en UI

```javascript
async function convertAndDisplay(amountInCents, fromCurrency, toCurrency) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/utils/exchange-rates/convert/?amount=${amountInCents}&from=${fromCurrency}&to=${toCurrency}`,
    {
      headers: { 'Authorization': `Token ${token}` }
    }
  );
  
  const data = await response.json();
  
  // Convertir centavos a pesos para mostrar
  const originalPesos = data.original_amount / 100;
  const convertedPesos = data.converted_amount / 100;
  
  console.log(`${originalPesos} ${fromCurrency} = ${convertedPesos} ${toCurrency}`);
  console.log(`Tasa: ${data.rate}`);
  
  return convertedPesos;
}

// Ejemplo: Convertir $100 USD a COP
// 10000 centavos USD = $100 USD
const copAmount = await convertAndDisplay(10000, 'USD', 'COP');
// Resultado: 400000 COP (si la tasa es 4000)
```

---

### Caso 4: Actualizar tasa existente

```javascript
async function updateExchangeRate(id, newRate) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/utils/exchange-rates/${id}/`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        rate: newRate,
        source: 'actualización_manual'
      })
    }
  );
  
  if (response.ok) {
    const data = await response.json();
    console.log(`✅ Tasa actualizada: ${data.rate}`);
    return data;
  }
}

// Actualizar tasa del tipo de cambio con ID 1
await updateExchangeRate(1, 4200);
```

---

### Caso 5: Listar tasas de un año específico

```javascript
async function getYearlyRates(year, currency) {
  const response = await fetch(
    `http://127.0.0.1:8000/api/utils/exchange-rates/?year=${year}&currency=${currency}`,
    {
      headers: { 'Authorization': `Token ${token}` }
    }
  );
  
  const rates = await response.json();
  
  console.log(`Tasas de ${currency} para ${year}:`);
  rates.forEach(rate => {
    console.log(`${rate.month}/${rate.year}: ${rate.rate}`);
  });
  
  return rates;
}

// Obtener todas las tasas USD del 2025
const usdRates2025 = await getYearlyRates(2025, 'USD');
```

---

## 💻 Ejemplos de Código Frontend

### React/TypeScript

```typescript
import { useState, useEffect } from 'react';

interface ExchangeRate {
  id: number;
  base_currency: string;
  currency: string;
  year: number;
  month: number;
  rate: string;
  source: string;
  created_at: string;
  updated_at: string;
}

interface CreateRateForm {
  base_currency: string;
  currency: string;
  year: number;
  month: number;
  rate: number;
  source: string;
}

const ExchangeRatesManager = () => {
  const [rates, setRates] = useState<ExchangeRate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_URL = 'http://127.0.0.1:8000/api/utils/exchange-rates/';
  const token = localStorage.getItem('authToken');

  // Obtener todas las tasas
  const fetchRates = async () => {
    setLoading(true);
    try {
      const response = await fetch(API_URL, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Error al obtener tasas');
      
      const data = await response.json();
      setRates(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  // Crear nueva tasa
  const createRate = async (formData: CreateRateForm) => {
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(JSON.stringify(errorData));
      }

      const newRate = await response.json();
      setRates([...rates, newRate]);
      return newRate;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al crear tasa');
      throw err;
    }
  };

  // Actualizar tasa
  const updateRate = async (id: number, rate: number) => {
    try {
      const response = await fetch(`${API_URL}${id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rate })
      });

      if (!response.ok) throw new Error('Error al actualizar tasa');

      const updatedRate = await response.json();
      setRates(rates.map(r => r.id === id ? updatedRate : r));
      return updatedRate;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al actualizar');
      throw err;
    }
  };

  // Eliminar tasa
  const deleteRate = async (id: number) => {
    try {
      const response = await fetch(`${API_URL}${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (!response.ok) throw new Error('Error al eliminar tasa');

      setRates(rates.filter(r => r.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al eliminar');
      throw err;
    }
  };

  // Consultar tasa actual
  const getCurrentRate = async (currency: string, date?: string) => {
    try {
      const params = new URLSearchParams({ currency });
      if (date) params.append('date', date);

      const response = await fetch(`${API_URL}current/?${params}`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (!response.ok) throw new Error('Error al consultar tasa');

      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al consultar');
      throw err;
    }
  };

  useEffect(() => {
    fetchRates();
  }, []);

  return {
    rates,
    loading,
    error,
    fetchRates,
    createRate,
    updateRate,
    deleteRate,
    getCurrentRate
  };
};

export default ExchangeRatesManager;
```

---

### Vue.js 3 (Composition API)

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface ExchangeRate {
  id: number;
  base_currency: string;
  currency: string;
  year: number;
  month: number;
  rate: string;
  source: string;
}

const API_URL = 'http://127.0.0.1:8000/api/utils/exchange-rates/';
const token = localStorage.getItem('authToken');

const rates = ref<ExchangeRate[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

const fetchRates = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(API_URL, {
      headers: { 'Authorization': `Token ${token}` }
    });
    
    if (!response.ok) throw new Error('Error al obtener tasas');
    
    rates.value = await response.json();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error desconocido';
  } finally {
    loading.value = false;
  }
};

const createRate = async (formData: Omit<ExchangeRate, 'id' | 'created_at' | 'updated_at'>) => {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) throw new Error('Error al crear tasa');
    
    const newRate = await response.json();
    rates.value.push(newRate);
    return newRate;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error al crear';
    throw err;
  }
};

onMounted(() => {
  fetchRates();
});
</script>

<template>
  <div class="exchange-rates-manager">
    <h2>Gestión de Tipos de Cambio</h2>
    
    <div v-if="loading">Cargando...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <table v-if="!loading && rates.length > 0">
      <thead>
        <tr>
          <th>Moneda</th>
          <th>Base</th>
          <th>Año/Mes</th>
          <th>Tasa</th>
          <th>Fuente</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rate in rates" :key="rate.id">
          <td>{{ rate.currency }}</td>
          <td>{{ rate.base_currency }}</td>
          <td>{{ rate.year }}-{{ String(rate.month).padStart(2, '0') }}</td>
          <td>{{ rate.rate }}</td>
          <td>{{ rate.source }}</td>
          <td>
            <button @click="() => deleteRate(rate.id)">Eliminar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

---

## ⚠️ Validaciones y Errores

### Errores comunes

#### 1. **Moneda base igual a moneda destino**
```json
{
  "non_field_errors": [
    "La moneda base y la moneda de destino no pueden ser iguales"
  ]
}
```

#### 2. **Moneda no soportada**
```json
{
  "currency": [
    "Moneda no soportada: JPY. Monedas disponibles: COP, USD, EUR"
  ]
}
```

#### 3. **Mes inválido**
```json
{
  "month": [
    "El mes debe estar entre 1 y 12"
  ]
}
```

#### 4. **Tasa negativa o cero**
```json
{
  "rate": [
    "La tasa de cambio debe ser mayor a cero"
  ]
}
```

#### 5. **Tipo de cambio duplicado**
```json
{
  "non_field_errors": [
    "Ya existe un tipo de cambio para COP/USD en 2025-01"
  ]
}
```

#### 6. **Parámetro faltante en consulta**
```json
{
  "error": "El parámetro 'currency' es requerido"
}
```

---

## ✅ Mejores Prácticas

### 1. **Manejo de centavos**
```javascript
// ❌ INCORRECTO
const amount = 100; // $100 USD
await convert(amount, 'USD', 'COP');

// ✅ CORRECTO
const amount = 10000; // $100 USD en centavos
await convert(amount, 'USD', 'COP');
```

### 2. **Verificar advertencias**
```javascript
const data = await getCurrentRate('USD');

if (data.warning) {
  // Mostrar al usuario que está usando tasa predeterminada
  showWarning(`⚠️ ${data.warning}`);
}
```

### 3. **Validar antes de crear**
```javascript
const formData = {
  base_currency: 'COP',
  currency: 'USD',
  year: 2025,
  month: 13, // ❌ Inválido
  rate: 4000
};

// Validar mes antes de enviar
if (formData.month < 1 || formData.month > 12) {
  alert('El mes debe estar entre 1 y 12');
  return;
}
```

### 4. **Cachear tasas consultadas frecuentemente**
```javascript
const rateCache = new Map();

async function getCachedRate(currency, date) {
  const key = `${currency}-${date}`;
  
  if (rateCache.has(key)) {
    return rateCache.get(key);
  }
  
  const data = await getCurrentRate(currency, date);
  rateCache.set(key, data);
  
  return data;
}
```

### 5. **Manejo de errores robusto**
```javascript
async function safeCreateRate(formData) {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (!response.ok) {
      // Mostrar errores específicos por campo
      if (data.month) {
        throw new Error(`Mes inválido: ${data.month[0]}`);
      }
      if (data.rate) {
        throw new Error(`Tasa inválida: ${data.rate[0]}`);
      }
      if (data.non_field_errors) {
        throw new Error(data.non_field_errors[0]);
      }
      
      throw new Error('Error al crear tipo de cambio');
    }

    return data;
  } catch (error) {
    console.error('Error:', error);
    alert(error.message);
    throw error;
  }
}
```

### 6. **UI amigable para selección de mes**
```javascript
const MONTHS = [
  { value: 1, label: 'Enero' },
  { value: 2, label: 'Febrero' },
  { value: 3, label: 'Marzo' },
  // ... resto de meses
];

// En tu componente
<select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
  {MONTHS.map(m => (
    <option key={m.value} value={m.value}>{m.label}</option>
  ))}
</select>
```

---

## 🔗 Endpoints Relacionados

### Moneda base del usuario
- `GET /api/utils/base-currency/` - Obtener moneda base configurada
- `POST /api/utils/base-currency/` - Establecer moneda base

Ver: [CURRENCY_BASE_CONFIGURATION.md](./CURRENCY_BASE_CONFIGURATION.md)

### Conversión de monedas (endpoints heredados)
- `GET /api/utils/currency/exchange-rate/` - Obtener tasa predeterminada
- `POST /api/utils/currency/convert/` - Convertir usando tasa predeterminada

---

## 📊 Ejemplo de flujo completo

```javascript
// 1. Usuario selecciona moneda base
await fetch('http://127.0.0.1:8000/api/utils/base-currency/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ base_currency: 'COP' })
});

// 2. Configurar tasas personalizadas para 2025
const months = [
  { month: 1, rate: 4000 },
  { month: 2, rate: 4100 },
  { month: 3, rate: 4050 }
];

for (const { month, rate } of months) {
  await fetch('http://127.0.0.1:8000/api/utils/exchange-rates/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      base_currency: 'COP',
      currency: 'USD',
      year: 2025,
      month,
      rate,
      source: 'manual'
    })
  });
}

// 3. Consultar tasa actual
const currentRate = await fetch(
  'http://127.0.0.1:8000/api/utils/exchange-rates/current/?currency=USD&date=2025-01-15',
  { headers: { 'Authorization': `Token ${token}` } }
).then(r => r.json());

console.log(`Tasa USD/COP para enero 2025: ${currentRate.rate}`);

// 4. Convertir monto ($100 USD a COP)
const conversion = await fetch(
  'http://127.0.0.1:8000/api/utils/exchange-rates/convert/?amount=10000&from=USD&to=COP&date=2025-01-15',
  { headers: { 'Authorization': `Token ${token}` } }
).then(r => r.json());

console.log(`$100 USD = $${conversion.converted_amount / 100} COP`);
```

---

## 📞 Soporte

Si tienes dudas sobre:
- Implementación de tipos de cambio
- Conversión de monedas
- Errores o comportamientos inesperados

Contacta al equipo de backend.

---

## 📚 Ver también

- [CURRENCY_BASE_CONFIGURATION.md](./CURRENCY_BASE_CONFIGURATION.md) - Configuración de moneda base
- [ANALYTICS_AMOUNTS_FORMAT.md](./ANALYTICS_AMOUNTS_FORMAT.md) - Formato de montos en analytics
- [API_REFERENCE.md](./API_REFERENCE.md) - Referencia completa de la API

---

**Última actualización:** 10 de diciembre de 2025  
**Versión:** 1.0  
**Autor:** Backend Team
