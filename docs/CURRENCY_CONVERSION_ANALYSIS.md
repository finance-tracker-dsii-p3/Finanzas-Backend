# Análisis Completo de Conversión de Monedas y Formatos

## 🔍 Problema Encontrado y Corregido

### ❌ Problema Crítico Detectado

**Inconsistencia en formatos de almacenamiento:**

1. **Account.current_balance**: `DecimalField` (almacena en **PESOS** con 2 decimales)
   - Ejemplo: `1948000.00` = 1,948,000 pesos

2. **Transaction.total_amount**: `IntegerField` (almacena en **CENTAVOS**)
   - Ejemplo: `500000000` = 5,000,000 pesos (500 millones de centavos)

3. **TransactionService.update_account_balance_for_transaction**: 
   - ❌ **ANTES**: Tomaba `transaction.total_amount` (centavos) y lo trataba como pesos
   - ✅ **AHORA**: Convierte centavos a pesos dividiendo por 100

### ✅ Correcciones Aplicadas

#### 1. TransactionService.update_account_balance_for_transaction
```python
# ANTES (INCORRECTO):
amount = Decimal(str(transaction.total_amount))  # 500000000 tratado como pesos

# AHORA (CORRECTO):
amount = Decimal(str(transaction.total_amount)) / Decimal('100')  # 500000000 centavos = 5000000 pesos
```

#### 2. TransactionService._validate_transaction_limits
```python
# ANTES (INCORRECTO):
amount = Decimal(str(transaction.total_amount))  # Centavos tratados como pesos

# AHORA (CORRECTO):
amount = Decimal(str(transaction.total_amount)) / Decimal('100')  # Convertir a pesos
```

#### 3. TransactionSerializer._validate_account_limits
```python
# ANTES (INCORRECTO):
# final_total estaba en centavos pero se comparaba con current_balance en pesos

# AHORA (CORRECTO):
final_total_pesos = Decimal(str(final_total)) / Decimal('100')  # Convertir antes de validar
```

## 📊 Resumen de Formatos por Modelo

| Modelo | Campo | Tipo | Formato | Ejemplo |
|--------|-------|------|---------|---------|
| **Account** | `current_balance` | DecimalField | **PESOS** (2 decimales) | `1948000.00` |
| **Account** | `credit_limit` | DecimalField | **PESOS** (2 decimales) | `5000000.00` |
| **Transaction** | `base_amount` | IntegerField | **CENTAVOS** | `500000000` |
| **Transaction** | `total_amount` | IntegerField | **CENTAVOS** | `500000000` |
| **Transaction** | `original_amount` | IntegerField | **CENTAVOS** | `10000` (USD) |
| **Goal** | `target_amount` | IntegerField | **CENTAVOS** | `400000000` |
| **Goal** | `saved_amount` | IntegerField | **CENTAVOS** | `120000000` |
| **Budget** | `amount` | DecimalField | **PESOS** (2 decimales) | `1000000.00` |

## 🔄 Flujo de Conversión Correcto

### Escenario: Crear transacción de ingreso

1. **Frontend envía:**
   ```json
   {
     "type": 1,
     "origin_account": 3,
     "total_amount": 500000000,  // 5 millones de pesos en CENTAVOS
     "date": "2025-11-30"
   }
   ```

2. **Backend recibe y valida:**
   - `total_amount` = 500000000 (centavos)
   - Se mantiene como está (ya está en centavos)

3. **Backend valida límites:**
   ```python
   # Convertir centavos a pesos para comparar con current_balance
   amount_pesos = 500000000 / 100 = 5000000.00 pesos
   current_balance = 1948000.00 pesos
   new_balance = 1948000.00 + 5000000.00 = 6948000.00 pesos ✅
   ```

4. **Backend actualiza saldo:**
   ```python
   # TransactionService convierte centavos a pesos
   amount = Decimal('500000000') / Decimal('100') = 5000000.00
   account.current_balance += 5000000.00 ✅
   ```

5. **Backend guarda transacción:**
   - `total_amount` = 500000000 (centavos) ✅
   - `account.current_balance` = 6948000.00 (pesos) ✅

## 💱 Conversión de Monedas

### Cuando hay diferencia de monedas:

1. **Frontend envía:**
   ```json
   {
     "type": 1,
     "origin_account": 1,  // Cuenta en COP
     "base_amount": 400000000,  // Ya convertido a COP en centavos
     "transaction_currency": "USD",
     "exchange_rate": 4000.0,
     "original_amount": 10000,  // 100 USD en centavos
     "date": "2025-11-30"
   }
   ```

2. **Backend valida:**
   - ✅ `base_amount` está en centavos de la moneda de la cuenta (COP)
   - ✅ `original_amount` está en centavos de la moneda original (USD)
   - ✅ `exchange_rate` es la tasa aplicada

3. **Backend actualiza saldo:**
   ```python
   # base_amount ya está en COP (centavos)
   # Convertir a pesos para actualizar cuenta
   amount = Decimal('400000000') / Decimal('100') = 4000000.00 pesos COP
   account.current_balance += 4000000.00 ✅
   ```

## ✅ Validaciones de Moneda

### 1. Transacción → Cuenta
- ✅ Si `transaction_currency` != `account.currency`, requiere `exchange_rate` y `original_amount`
- ✅ `base_amount` debe estar en centavos de la moneda de la cuenta
- ✅ La conversión se hace automáticamente si se proporciona `original_amount`

### 2. Transacción → Meta
- ✅ `goal.currency` debe coincidir con `account.currency`
- ✅ `transaction.total_amount` (centavos) se suma directamente a `goal.saved_amount` (centavos)
- ✅ No se requiere conversión porque ambas están en la misma moneda

### 3. Transferencia
- ✅ `origin_account.currency` debe coincidir con `destination_account.currency`
- ✅ No se permite conversión en transferencias (por ahora)

### 4. Presupuesto
- ✅ Filtra transacciones por `origin_account.currency == budget.currency`
- ✅ Convierte centavos a Decimal (pesos) para comparar con `budget.amount`

## 📝 Notas Importantes para el Frontend

### ⚠️ CRÍTICO: Formato de Envío

**SIEMPRE enviar montos como INTEGER (centavos):**

```javascript
// ✅ CORRECTO
{
  total_amount: 500000000  // integer - 5 millones de pesos
}

// ❌ INCORRECTO (se convertirá por 100)
{
  total_amount: 5000000.00  // float - se interpretará como 5 millones de pesos y se convertirá a 500 millones de centavos
}
```

### Conversión Frontend → Backend

```javascript
// Convertir pesos a centavos antes de enviar
const amountInCents = Math.round(amountInPesos * 100);

// Ejemplo:
const amountInPesos = 5000000;  // 5 millones de pesos
const amountInCents = 500000000;  // 500 millones de centavos

// Enviar:
{
  total_amount: amountInCents  // 500000000
}
```

### Conversión Backend → Frontend

```javascript
// Convertir centavos a pesos al recibir
const amountInPesos = centavos / 100;

// Ejemplo:
const centavos = 500000000;  // Del backend
const amountInPesos = 5000000;  // 5 millones de pesos

// Mostrar al usuario:
formatMoney(amountInPesos, currency);
```

## 🔍 Verificación de Conversiones

### Checklist de Verificación

- [x] TransactionService convierte centavos a pesos al actualizar saldo
- [x] TransactionService._validate_transaction_limits convierte centavos a pesos
- [x] TransactionSerializer._validate_account_limits recibe pesos (convertido antes)
- [x] Budget.get_spent_amount convierte centavos a Decimal (pesos)
- [x] GoalService suma centavos directamente (misma moneda)
- [x] CurrencyConverter trabaja con centavos (entero → entero)

## 🚨 Errores Comunes a Evitar

1. ❌ **No convertir centavos a pesos** al actualizar `account.current_balance`
2. ❌ **Enviar montos como float** desde el frontend (se convertirá por 100)
3. ❌ **Comparar centavos con pesos** sin conversión
4. ❌ **Olvidar convertir** en validaciones de límites

## ✅ Estado Actual

### Backend:
- ✅ Conversión centavos → pesos en TransactionService
- ✅ Conversión centavos → pesos en validaciones
- ✅ Conversión de monedas con CurrencyConverter
- ✅ Validaciones de moneda implementadas

### Frontend (Pendiente):
- ⚠️ Asegurar que siempre envía montos como INTEGER (centavos)
- ⚠️ Convertir centavos a pesos al mostrar
- ⚠️ Manejar conversión de monedas correctamente

