# HU-17: Multi-moneda y Conversión a Moneda Base - Guía Completa Postman

## 📋 Índice
1. [Introducción](#introducción)
2. [Conceptos Clave](#conceptos-clave)
3. [Configuración Inicial](#configuración-inicial)
4. [Endpoints Disponibles](#endpoints-disponibles)
5. [Flujo Completo de Uso](#flujo-completo-de-uso)
6. [Casos de Uso Comunes](#casos-de-uso-comunes)
7. [Advertencias y Errores](#advertencias-y-errores)

---

## Introducción

La funcionalidad HU-17 permite gestionar transacciones en múltiples monedas (COP, USD, EUR) y ver todos los totales consolidados en una **moneda base** que cada usuario puede configurar. Los valores originales de las transacciones **nunca se modifican**, solo se muestran convertidos usando tipos de cambio históricos mensuales.

### Características principales:
- ✅ Cada usuario define su **moneda base** preferida
- ✅ Tipos de cambio **mensuales** con histórico
- ✅ **Fallback automático** a meses anteriores si falta un tipo de cambio
- ✅ **Advertencias claras** cuando se usa un tipo de cambio no exacto
- ✅ Conversiones aparecen en dashboard, analytics, transacciones y reportes
- ✅ Valores originales **siempre preservados**

---

## Conceptos Clave

### 🔹 Moneda Base
- **¿Qué es?** La moneda en la que el usuario quiere ver todos sus totales consolidados
- **¿Dónde se define?** En la configuración del usuario (`/api/utils/base-currency/`)
- **¿Se puede cambiar?** Sí, en cualquier momento. Al cambiarla, todos los totales se recalculan automáticamente
- **Moneda por defecto:** COP (Pesos Colombianos)

### 🔹 Tipos de Cambio Mensuales
- **¿Qué son?** Tasas de conversión entre monedas para un mes/año específico
- **Ejemplo:** En enero 2025, 1 USD = 4,000 COP
- **¿Cómo funcionan?** El sistema busca el tipo de cambio del mes de la transacción. Si no existe, usa el último disponible anterior
- **¿Dónde se definen?** En `/api/utils/exchange-rates/`

### 🔹 Montos en Centavos
- **Todos los montos se manejan en centavos** para evitar problemas de redondeo
- **Ejemplo:**
  - `10000` centavos = `100.00` unidades monetarias
  - `500050` centavos = `5,000.50` unidades monetarias

---

## Configuración Inicial

### 1. Autenticación
Todos los endpoints requieren autenticación con Token:

```
Headers:
Authorization: Token <tu_token_aqui>
Content-Type: application/json
```

### 2. Obtener Token (si no lo tienes)
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

**Respuesta:**
```json
{
  "token": "a1b2c3d4e5f6...",
  "user": {
    "id": 1,
    "username": "tu_usuario",
    "email": "tu@email.com"
  }
}
```

---

## Endpoints Disponibles

### 📍 1. Consultar Moneda Base Actual

**Descripción:** Obtiene la moneda base configurada para el usuario autenticado.

```http
GET /api/utils/base-currency/
Authorization: Token <tu_token>
```

**Respuesta Ejemplo:**
```json
{
  "base_currency": "COP",
  "updated_at": "2025-01-15T10:30:00Z",
  "available_currencies": ["COP", "USD", "EUR"]
}
```

**Campos explicados:**
- `base_currency`: Moneda base actual del usuario (COP, USD o EUR)
- `updated_at`: Última vez que se modificó la configuración
- `available_currencies`: Lista de monedas soportadas por el sistema

---

### 📍 2. Definir/Cambiar Moneda Base

**Descripción:** Establece o actualiza la moneda base del usuario. Al cambiarla, todos los cálculos se actualizan automáticamente.

```http
PUT /api/utils/base-currency/set_base/
Authorization: Token <tu_token>
Content-Type: application/json

{
  "base_currency": "USD"
}
```

**Campos del body:**
- `base_currency` (string, requerido): Código de la nueva moneda base
  - Valores válidos: `"COP"`, `"USD"`, `"EUR"`
  - **De dónde sale:** Lo defines tú según tu preferencia

**Respuesta Ejemplo:**
```json
{
  "base_currency": "USD",
  "updated_at": "2025-01-15T14:20:30Z",
  "message": "Moneda base actualizada a USD. Los totales se recalcularán automáticamente."
}
```

**¿Qué pasa al cambiar la moneda base?**
1. Se guarda la nueva configuración
2. Todos los endpoints de analytics, dashboard y transacciones mostrarán equivalentes en la nueva moneda
3. Los valores originales de las transacciones NO se modifican

---

### 📍 3. Listar Tipos de Cambio

**Descripción:** Obtiene todos los tipos de cambio registrados. Puedes filtrar por moneda, año o mes.

```http
GET /api/utils/exchange-rates/
Authorization: Token <tu_token>
```

**Parámetros de query opcionales:**
- `currency`: Filtrar por moneda (ej: `USD`)
- `base_currency`: Filtrar por moneda base (ej: `COP`)
- `year`: Filtrar por año (ej: `2025`)
- `month`: Filtrar por mes (ej: `1` para enero)

**Ejemplo con filtros:**
```http
GET /api/utils/exchange-rates/?currency=USD&base_currency=COP&year=2025
```

**Respuesta Ejemplo:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "base_currency": "COP",
      "currency": "USD",
      "year": 2025,
      "month": 1,
      "rate": "4000.000000",
      "source": "manual",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "base_currency": "COP",
      "currency": "EUR",
      "year": 2025,
      "month": 1,
      "rate": "4350.000000",
      "source": "manual",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

**Campos explicados:**
- `base_currency`: Moneda de referencia (normalmente COP)
- `currency`: Moneda que se está valorando
- `year`, `month`: Período al que aplica este tipo de cambio
- `rate`: **Cuántas unidades de `base_currency` vale 1 unidad de `currency`**
  - Ejemplo: `rate: 4000` significa 1 USD = 4,000 COP
- `source`: Origen del dato (`"manual"`, `"API"`, etc.)

---

### 📍 4. Registrar Nuevo Tipo de Cambio

**Descripción:** Crea un tipo de cambio mensual entre dos monedas.

```http
POST /api/utils/exchange-rates/
Authorization: Token <tu_token>
Content-Type: application/json

{
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 1,
  "rate": "4000.0",
  "source": "manual"
}
```

**Campos del body:**
- `base_currency` (string, requerido): Moneda base de referencia
  - **De dónde sale:** Normalmente usas tu moneda local (COP)
- `currency` (string, requerido): Moneda a valorar
  - **De dónde sale:** La moneda extranjera que quieres registrar (USD, EUR)
- `year` (integer, requerido): Año del tipo de cambio (2020-2035)
  - **De dónde sale:** El año actual o histórico que estás registrando
- `month` (integer, requerido): Mes del tipo de cambio (1-12)
  - **De dónde sale:** El mes (1=enero, 12=diciembre)
- `rate` (decimal, requerido): Tasa de conversión
  - **De dónde sale:** El valor del tipo de cambio que encuentres (banco central, casa de cambio, etc.)
  - **Interpretación:** Cuántas unidades de `base_currency` vale 1 unidad de `currency`
  - **Ejemplo:** Si 1 USD = 4,000 COP, entonces `rate: 4000`
- `source` (string, opcional): Fuente del dato
  - **De dónde sale:** Descripción libre (`"Banco de la República"`, `"manual"`, `"API XE"`)

**Respuesta Ejemplo:**
```json
{
  "id": 3,
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 1,
  "rate": "4000.000000",
  "source": "manual",
  "created_at": "2025-01-15T15:00:00Z",
  "updated_at": "2025-01-15T15:00:00Z"
}
```

**Validaciones:**
- ❌ No puedes crear tipos de cambio con `base_currency == currency`
- ❌ El mes debe estar entre 1 y 12
- ❌ El `rate` debe ser mayor a cero
- ❌ No pueden existir duplicados (misma `base_currency`, `currency`, `year`, `month`)

---

### 📍 5. Actualizar Tipo de Cambio

**Descripción:** Modifica un tipo de cambio existente (útil para correcciones).

```http
PUT /api/utils/exchange-rates/3/
Authorization: Token <tu_token>
Content-Type: application/json

{
  "rate": "4050.0",
  "source": "Banco de la República - Actualizado"
}
```

**Nota:** Solo puedes modificar `rate` y `source`. Para cambiar período o monedas, debes crear un registro nuevo.

---

### 📍 6. Obtener Tipo de Cambio Vigente

**Descripción:** Consulta el tipo de cambio aplicable para una fecha específica. Si no existe para ese mes exacto, devuelve el último disponible anterior con advertencia.

```http
GET /api/utils/exchange-rates/current/?currency=USD&base=COP&date=2025-01-15
Authorization: Token <tu_token>
```

**Parámetros de query:**
- `currency` (string, requerido): Moneda a consultar
  - **De dónde sale:** La moneda que quieres convertir (ej: `USD`)
- `base` (string, opcional): Moneda base
  - **De dónde sale:** Moneda destino de la conversión. Si no se especifica, usa la moneda base del usuario
- `date` (string, opcional): Fecha de referencia en formato `YYYY-MM-DD`
  - **De dónde sale:** La fecha de la transacción o consulta. Si no se especifica, usa la fecha actual

**Respuesta Ejemplo (tasa exacta encontrada):**
```json
{
  "currency": "USD",
  "base_currency": "COP",
  "rate": 4000.0,
  "reference_date": "2025-01-15",
  "year": 2025,
  "month": 1
}
```

**Respuesta Ejemplo (con advertencia - usando tasa anterior):**
```json
{
  "currency": "USD",
  "base_currency": "COP",
  "rate": 4000.0,
  "reference_date": "2025-02-15",
  "year": 2025,
  "month": 2,
  "warning": "No hay tipo de cambio para USD->COP en 2025-02. Usando tasa de 2025-01: 4000"
}
```

**Campos explicados:**
- `rate`: Tasa de cambio aplicada
- `reference_date`: Fecha consultada
- `year`, `month`: Período del tipo de cambio usado
- `warning` (si aparece): Indica que se está usando un tipo de cambio de un período anterior porque no hay uno definido para el mes exacto

---

### 📍 7. Convertir Monto entre Monedas

**Descripción:** Convierte un monto de una moneda a otra usando el tipo de cambio del período.

```http
GET /api/utils/exchange-rates/convert/?amount=10000&from=USD&to=COP&date=2025-01-15
Authorization: Token <tu_token>
```

**Parámetros de query:**
- `amount` (integer, requerido): Monto en **centavos** a convertir
  - **De dónde sale:** El monto de tu transacción multiplicado por 100
  - **Ejemplo:** Para convertir 100.00 USD, usa `amount=10000`
- `from` (string, requerido): Moneda origen
  - **De dónde sale:** La moneda del monto que tienes (ej: `USD`)
- `to` (string, opcional): Moneda destino
  - **De dónde sale:** La moneda a la que quieres convertir. Si no se especifica, usa tu moneda base
- `date` (string, opcional): Fecha de referencia `YYYY-MM-DD`
  - **De dónde sale:** La fecha de la transacción. Si no se especifica, usa hoy

**Respuesta Ejemplo:**
```json
{
  "original_amount": 10000,
  "original_currency": "USD",
  "converted_amount": 40000000,
  "target_currency": "COP",
  "exchange_rate": 4000.0,
  "reference_date": "2025-01-15",
  "formatted": {
    "original": "100.00 USD",
    "converted": "400,000.00 COP"
  }
}
```

**Campos explicados:**
- `original_amount`: Monto original en centavos (10000 = 100.00 USD)
- `converted_amount`: Monto convertido en centavos (40000000 = 400,000.00 COP)
- `exchange_rate`: Tasa de cambio aplicada (4000 = 1 USD vale 4,000 COP)
- `formatted`: Montos legibles para humanos

---

## Flujo Completo de Uso

### Escenario: Usuario colombiano con cuentas en COP y USD

#### Paso 1: Configurar moneda base a COP

```http
PUT /api/utils/base-currency/set_base/
Authorization: Token abc123

{
  "base_currency": "COP"
}
```

#### Paso 2: Registrar tipos de cambio mensuales

```http
POST /api/utils/exchange-rates/
Authorization: Token abc123

{
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 1,
  "rate": "4000.0",
  "source": "Banco de la República"
}
```

```http
POST /api/utils/exchange-rates/
Authorization: Token abc123

{
  "base_currency": "COP",
  "currency": "EUR",
  "year": 2025,
  "month": 1,
  "rate": "4350.0",
  "source": "Banco de la República"
}
```

#### Paso 3: Crear cuenta en USD

```http
POST /api/accounts/
Authorization: Token abc123

{
  "name": "Cuenta Bancolombia USD",
  "bank_name": "Bancolombia",
  "account_type": "asset",
  "category": "bank_account",
  "currency": "USD",
  "initial_balance": 100000
}
```
- `initial_balance: 100000` = 1,000.00 USD en centavos

#### Paso 4: Crear transacción en USD

```http
POST /api/transactions/
Authorization: Token abc123

{
  "origin_account": 5,
  "type": 2,
  "category": 3,
  "base_amount": 5000,
  "date": "2025-01-15",
  "description": "Comida en restaurante",
  "transaction_currency": "USD"
}
```

**Campos explicados:**
- `origin_account: 5`: ID de tu cuenta USD (del paso 3)
  - **De dónde sale:** De la respuesta del POST `/api/accounts/`
- `type: 2`: Gasto (1=Ingreso, 2=Gasto, 3=Transferencia, 4=Ahorro)
- `category: 3`: ID de categoría "Alimentación"
  - **De dónde sale:** De `GET /api/categories/` buscas la que se llama "Alimentación"
- `base_amount: 5000`: 50.00 USD en centavos
- `transaction_currency: "USD"`: Moneda de la transacción
  - **De dónde sale:** Debe coincidir con la moneda de la cuenta origen

#### Paso 5: Consultar detalle de la transacción

```http
GET /api/transactions/123/
Authorization: Token abc123
```

**Respuesta:**
```json
{
  "id": 123,
  "origin_account": 5,
  "origin_account_name": "Cuenta Bancolombia USD",
  "origin_account_currency": "USD",
  "category_name": "Alimentación",
  "type": 2,
  "base_amount": 5000,
  "total_amount": 5000,
  "date": "2025-01-15",
  "description": "Comida en restaurante",
  "transaction_currency": "USD",

  // ⭐ Campos de conversión a moneda base
  "base_currency": "COP",
  "base_equivalent_amount": 20000000,
  "base_exchange_rate": 4000.0
}
```

**Interpretación:**
- Transacción original: **50.00 USD** (`base_amount: 5000` centavos)
- Equivalente en moneda base: **200,000.00 COP** (`base_equivalent_amount: 20000000` centavos)
- Tasa aplicada: **1 USD = 4,000 COP**

#### Paso 6: Ver totales en Analytics (dashboard)

```http
GET /api/analytics/indicators/?start_date=2025-01-01&end_date=2025-01-31&mode=base
Authorization: Token abc123
```

**Respuesta:**
```json
{
  "income": {
    "amount": 0,
    "count": 0,
    "formatted": "$0"
  },
  "expenses": {
    "amount": 20000000,
    "count": 1,
    "formatted": "$200,000"
  },
  "balance": {
    "amount": -20000000,
    "formatted": "$-200,000",
    "is_positive": false
  },
  "currency": "COP",
  "mode": "base"
}
```

**¿Qué está pasando?**
- Aunque la transacción se registró en USD, el dashboard muestra el total en COP
- `expenses.amount: 20000000` = 200,000.00 COP (los 50 USD convertidos)
- La moneda base del usuario es COP, por eso aparece en `currency`

#### Paso 7: Cambiar moneda base a USD

```http
PUT /api/utils/base-currency/set_base/
Authorization: Token abc123

{
  "base_currency": "USD"
}
```

#### Paso 8: Volver a consultar Analytics

```http
GET /api/analytics/indicators/?start_date=2025-01-01&end_date=2025-01-31&mode=base
Authorization: Token abc123
```

**Respuesta:**
```json
{
  "income": {
    "amount": 0,
    "count": 0,
    "formatted": "$0"
  },
  "expenses": {
    "amount": 5000,
    "count": 1,
    "formatted": "$50"
  },
  "balance": {
    "amount": -5000,
    "formatted": "$-50",
    "is_positive": false
  },
  "currency": "USD",
  "mode": "base"
}
```

**¿Qué cambió?**
- Ahora los totales se muestran en USD (nueva moneda base)
- `expenses.amount: 5000` = 50.00 USD (valor original sin conversión, ya que la transacción está en USD)
- **Los valores originales en la base de datos NO se modificaron**, solo cambia cómo se presentan

---

## Casos de Uso Comunes

### Caso 1: Registrar múltiples monedas para un mismo mes

```http
POST /api/utils/exchange-rates/
{
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 2,
  "rate": "4050.0",
  "source": "manual"
}

POST /api/utils/exchange-rates/
{
  "base_currency": "COP",
  "currency": "EUR",
  "year": 2025,
  "month": 2,
  "rate": "4400.0",
  "source": "manual"
}
```

### Caso 2: Verificar tipo de cambio antes de crear transacción

```http
GET /api/utils/exchange-rates/current/?currency=USD&base=COP&date=2025-02-15
```

Si recibes `warning`, considera registrar el tipo de cambio exacto del mes antes de continuar.

### Caso 3: Convertir saldo de cuenta USD a COP

```http
GET /api/utils/exchange-rates/convert/?amount=250000000&from=USD&to=COP&date=2025-01-15
```
- `amount=250000000` = 2,500.00 USD en centavos

### Caso 4: Usuario con múltiples cuentas en diferentes monedas

1. Cuenta COP: Nómina
2. Cuenta USD: Ahorros en dólares
3. Cuenta EUR: Inversión internacional

```http
GET /api/analytics/indicators/?start_date=2025-01-01&end_date=2025-01-31&mode=base
```

El endpoint consolidará TODAS las transacciones de las 3 cuentas y las mostrará en la moneda base del usuario (ej: COP).

---

## Advertencias y Errores

### ⚠️ Advertencia: Tipo de cambio no exacto

**Cuándo aparece:** Cuando no hay tipo de cambio definido para el mes de la transacción.

**Ejemplo de respuesta:**
```json
{
  "currency": "USD",
  "base_currency": "COP",
  "rate": 4000.0,
  "warning": "No hay tipo de cambio para USD->COP en 2025-03. Usando tasa de 2025-01: 4000"
}
```

**Qué hacer:**
1. Si es aceptable, continúa con ese tipo de cambio
2. Si necesitas precisión, registra el tipo de cambio correcto para marzo:
```http
POST /api/utils/exchange-rates/
{
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 3,
  "rate": "4100.0"
}
```

### ❌ Error: No hay tipo de cambio disponible

**Cuándo aparece:** Cuando no hay ningún tipo de cambio registrado (ni del mes ni de meses anteriores).

**Respuesta:**
```json
{
  "error": "No hay tipo de cambio para USD->COP en 2025-01 ni en períodos anteriores"
}
```

**Solución:** Registra al menos un tipo de cambio:
```http
POST /api/utils/exchange-rates/
{
  "base_currency": "COP",
  "currency": "USD",
  "year": 2025,
  "month": 1,
  "rate": "4000.0"
}
```

### ❌ Error: Moneda no soportada

**Respuesta:**
```json
{
  "error": "Moneda no soportada: GBP. Monedas válidas: COP, USD, EUR"
}
```

**Solución:** Solo puedes usar COP, USD o EUR.

### ❌ Error: Monto inválido

**Respuesta:**
```json
{
  "error": "El monto debe ser un número entero en centavos"
}
```

**Solución:** Usa montos en centavos (enteros), no decimales:
- ✅ Correcto: `amount=10000` (100.00)
- ❌ Incorrecto: `amount=100.00`

---

## Resumen de URLs

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/utils/base-currency/` | GET | Consultar moneda base |
| `/api/utils/base-currency/set_base/` | PUT | Definir/cambiar moneda base |
| `/api/utils/exchange-rates/` | GET | Listar tipos de cambio |
| `/api/utils/exchange-rates/` | POST | Crear tipo de cambio |
| `/api/utils/exchange-rates/{id}/` | PUT | Actualizar tipo de cambio |
| `/api/utils/exchange-rates/current/` | GET | Tipo de cambio vigente |
| `/api/utils/exchange-rates/convert/` | GET | Convertir monto |

---

## Notas Importantes

1. **Los montos siempre en centavos:** Todos los endpoints esperan y devuelven montos en centavos (sin decimales)
2. **Moneda base por usuario:** Cada usuario tiene su propia configuración de moneda base
3. **Tipos de cambio compartidos:** Los tipos de cambio son globales (no por usuario)
4. **Fallback automático:** Si falta un tipo de cambio, se usa el último disponible
5. **Valores originales preservados:** Cambiar la moneda base NO modifica los datos originales
6. **Conversiones en tiempo real:** Los cálculos se hacen al consultar, no al guardar

---

## Preguntas Frecuentes

**P: ¿Puedo tener transacciones en una moneda y mi moneda base en otra?**
R: Sí, es justamente el propósito de esta funcionalidad. Puedes tener cuentas en USD y EUR, y ver todo consolidado en COP.

**P: ¿Qué pasa si cambio mi moneda base después de tener transacciones?**
R: Todos los totales se recalculan automáticamente usando los tipos de cambio históricos. Las transacciones originales no se modifican.

**P: ¿Debo registrar tipos de cambio inversos (COP->USD y USD->COP)?**
R: No, el sistema calcula automáticamente el inverso. Si registras USD->COP con rate=4000, el sistema puede calcular COP->USD como 1/4000=0.00025.

**P: ¿Los tipos de cambio se actualizan automáticamente?**
R: No, debes registrarlos manualmente o integrar con una API externa.

**P: ¿Puedo ver los tipos de cambio usados en cada transacción?**
R: Sí, en el detalle de transacciones aparecen los campos `base_exchange_rate` y `base_equivalent_amount`.
