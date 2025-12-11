# Manejo de Múltiples Monedas - Guía Frontend

## ✅ Estado del Backend

El backend **YA ESTÁ COMPLETAMENTE IMPLEMENTADO** con:
- ✅ Campo `currency` en cuentas, metas y presupuestos
- ✅ Campos de conversión en transacciones (`transaction_currency`, `exchange_rate`, `original_amount`)
- ✅ Endpoints de conversión de monedas
- ✅ Validaciones automáticas de monedas
- ✅ Conversión automática cuando hay diferencia de monedas

## 🎯 Lo que el Frontend DEBE Hacer

### 1. Mostrar Moneda en Todos los Componentes

#### Cuentas
```jsx
<div className="account-card">
  <h3>{account.name}</h3>
  <p className="currency-badge">{account.currency_display}</p>
  <p className="balance">
    {formatMoney(account.current_balance, account.currency)}
  </p>
</div>
```

#### Metas
```jsx
<div className="goal-card">
  <h3>{goal.name}</h3>
  <p className="currency-badge">{goal.currency_display}</p>
  <p>
    {formatMoney(goal.saved_amount, goal.currency)} /
    {formatMoney(goal.target_amount, goal.currency)}
  </p>
</div>
```

#### Presupuestos
```jsx
<div className="budget-card">
  <h3>{budget.category_name}</h3>
  <p className="currency-badge">{budget.currency_display}</p>
  <p>
    {formatMoney(budget.spent_amount, budget.currency)} /
    {formatMoney(budget.amount, budget.currency)}
  </p>
</div>
```

### 2. Formatear Montos Según Moneda

```javascript
const formatMoney = (centavos, currency) => {
  const amount = centavos / 100;

  const formatters = {
    'COP': new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }),
    'USD': new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }),
    'EUR': new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  };

  return formatters[currency]?.format(amount) || `${amount} ${currency}`;
};

// Uso:
formatMoney(40000000, 'COP')  // "$40.000.000"
formatMoney(10000, 'USD')     // "$100.00"
formatMoney(5000, 'EUR')      // "5.000,00 €"
```

### 3. Advertir sobre Diferencia de Monedas

#### Al crear transacción con cuenta y meta de diferentes monedas

```jsx
const CreateSavingTransaction = ({ account, goal }) => {
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (goal && account.currency !== goal.currency) {
      setShowWarning(true);
    }
  }, [account, goal]);

  return (
    <form>
      {showWarning && (
        <div className="alert alert-warning">
          <strong>⚠️ Advertencia de Moneda</strong>
          <p>
            La cuenta está en <strong>{account.currency_display}</strong> pero
            la meta está en <strong>{goal.currency_display}</strong>.
          </p>
          <p>
            Las transacciones deben estar en la misma moneda que la meta.
            Por favor, selecciona una cuenta en {goal.currency_display} o
            crea una nueva meta en {account.currency_display}.
          </p>
        </div>
      )}

      {/* Resto del formulario */}
    </form>
  );
};
```

### 4. Selector de Moneda en Formulario de Transacción

```jsx
const CreateTransactionForm = ({ account }) => {
  const [transactionCurrency, setTransactionCurrency] = useState(account.currency);
  const [amount, setAmount] = useState('');
  const [convertedAmount, setConvertedAmount] = useState(null);
  const [exchangeRate, setExchangeRate] = useState(null);
  const [loading, setLoading] = useState(false);

  // Cuando cambia la moneda o el monto, obtener conversión
  useEffect(() => {
    if (transactionCurrency !== account.currency && amount) {
      fetchConversion();
    } else {
      setConvertedAmount(null);
      setExchangeRate(null);
    }
  }, [transactionCurrency, amount, account.currency]);

  const fetchConversion = async () => {
    setLoading(true);
    try {
      // Obtener tasa de cambio
      const rateResponse = await fetch(
        `/api/utils/currency/exchange-rate/?from=${transactionCurrency}&to=${account.currency}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const rateData = await rateResponse.json();
      setExchangeRate(rateData.rate);

      // Convertir monto
      const amountInCents = Math.round(parseFloat(amount) * 100);
      const convertResponse = await fetch(
        `/api/utils/currency/convert/?amount=${amountInCents}&from=${transactionCurrency}&to=${account.currency}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const convertData = await convertResponse.json();
      setConvertedAmount(convertData.converted_amount);
    } catch (error) {
      console.error('Error obteniendo conversión:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      type: 4, // Saving
      origin_account: account.id,
      base_amount: convertedAmount || Math.round(parseFloat(amount) * 100),
      transaction_currency: transactionCurrency,
      date: formData.date,
      goal: formData.goal_id
    };

    // Si hay conversión, agregar campos adicionales
    if (transactionCurrency !== account.currency) {
      payload.exchange_rate = exchangeRate;
      payload.original_amount = Math.round(parseFloat(amount) * 100);
    }

    // Enviar al backend
    const response = await fetch('/api/transactions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    // ... manejar respuesta
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Moneda de la transacción</label>
        <select
          value={transactionCurrency}
          onChange={(e) => setTransactionCurrency(e.target.value)}
        >
          <option value="COP">Pesos Colombianos (COP)</option>
          <option value="USD">Dólares (USD)</option>
          <option value="EUR">Euros (EUR)</option>
        </select>
      </div>

      {transactionCurrency !== account.currency && (
        <div className="info-box">
          <p>
            <strong>ℹ️ Conversión de Moneda</strong>
          </p>
          <p>
            La cuenta está en <strong>{account.currency_display}</strong>.
            El monto se convertirá automáticamente.
          </p>
          {loading ? (
            <p>Cargando tasa de cambio...</p>
          ) : exchangeRate && convertedAmount ? (
            <div className="conversion-display">
              <p>
                {formatMoney(Math.round(parseFloat(amount) * 100), transactionCurrency)} =
                {formatMoney(convertedAmount, account.currency)}
              </p>
              <p className="rate-info">
                Tasa: 1 {transactionCurrency} = {exchangeRate} {account.currency}
              </p>
            </div>
          ) : null}
        </div>
      )}

      <div>
        <label>Monto (en {transactionCurrency})</label>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
          min="0.01"
          step="0.01"
        />
      </div>

      <button type="submit" disabled={loading}>
        Registrar Transacción
      </button>
    </form>
  );
};
```

### 5. Filtrar Cuentas/Metas por Moneda

```jsx
const SelectAccountForGoal = ({ goal, onSelect }) => {
  const [accounts, setAccounts] = useState([]);

  useEffect(() => {
    // Filtrar cuentas que tengan la misma moneda que la meta
    fetch(`/api/accounts/?currency=${goal.currency}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setAccounts(data));
  }, [goal]);

  return (
    <select onChange={(e) => onSelect(parseInt(e.target.value))}>
      <option value="">Seleccionar cuenta</option>
      {accounts.map(account => (
        <option key={account.id} value={account.id}>
          {account.name} ({account.currency_display})
        </option>
      ))}
    </select>
  );
};
```

### 6. Mostrar Información de Conversión en Historial

```jsx
const TransactionHistoryItem = ({ transaction }) => {
  const hasConversion = transaction.transaction_currency &&
                        transaction.transaction_currency !== transaction.origin_account_currency;

  return (
    <div className="transaction-item">
      <div className="transaction-main">
        <p>{transaction.description}</p>
        <p className="amount">
          {formatMoney(transaction.total_amount, transaction.origin_account_currency)}
        </p>
      </div>

      {hasConversion && (
        <div className="conversion-info">
          <p className="original">
            Original: {formatMoney(transaction.original_amount, transaction.transaction_currency)}
          </p>
          <p className="rate">
            Tasa: {transaction.exchange_rate} {transaction.transaction_currency}/{transaction.origin_account_currency}
          </p>
        </div>
      )}
    </div>
  );
};
```

## 📋 Checklist de Implementación Frontend

- [ ] **Mostrar moneda en componentes de cuenta**
  - [ ] Badge o etiqueta con moneda
  - [ ] Formatear saldo según moneda

- [ ] **Mostrar moneda en componentes de meta**
  - [ ] Badge con moneda
  - [ ] Formatear montos según moneda

- [ ] **Mostrar moneda en componentes de presupuesto**
  - [ ] Badge con moneda
  - [ ] Formatear montos según moneda

- [ ] **Función formatMoney()**
  - [ ] Soporte para COP, USD, EUR
  - [ ] Formato correcto según moneda

- [ ] **Advertencias de moneda**
  - [ ] Al seleccionar cuenta y meta con diferentes monedas
  - [ ] Al crear transacción con moneda diferente a la cuenta

- [ ] **Selector de moneda en formulario de transacción**
  - [ ] Dropdown con opciones COP, USD, EUR
  - [ ] Valor por defecto: moneda de la cuenta

- [ ] **Conversión en tiempo real**
  - [ ] Consultar tasa de cambio cuando hay diferencia
  - [ ] Mostrar monto convertido
  - [ ] Mostrar tasa de cambio aplicada

- [ ] **Enviar campos de conversión al backend**
  - [ ] `transaction_currency` (si difiere de cuenta)
  - [ ] `exchange_rate` (si hay conversión)
  - [ ] `original_amount` (si hay conversión)
  - [ ] `base_amount` en moneda de la cuenta

- [ ] **Filtrar por moneda**
  - [ ] Filtrar cuentas al seleccionar para meta
  - [ ] Filtrar metas al seleccionar para transacción

- [ ] **Mostrar información de conversión en historial**
  - [ ] Mostrar monto original si hubo conversión
  - [ ] Mostrar tasa de cambio aplicada

## 🎨 Estilos CSS Sugeridos

```css
.currency-badge {
  display: inline-block;
  padding: 4px 8px;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 8px;
}

.alert-warning {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  padding: 12px;
  margin: 16px 0;
}

.info-box {
  background-color: #e7f3ff;
  border-left: 4px solid #2196f3;
  padding: 12px;
  margin: 16px 0;
  border-radius: 4px;
}

.conversion-display {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px;
}

.conversion-display p {
  margin: 4px 0;
}

.rate-info {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.conversion-info {
  background-color: #f9f9f9;
  padding: 8px;
  border-left: 3px solid #4caf50;
  margin-top: 8px;
  font-size: 12px;
}
```

## 🔗 Endpoints del Backend Disponibles

### 1. Obtener tasa de cambio
```http
GET /api/utils/currency/exchange-rate/?from=USD&to=COP
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "from": "USD",
  "to": "COP",
  "rate": 4000.0,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### 2. Convertir monto
```http
GET /api/utils/currency/convert/?amount=10000&from=USD&to=COP
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "original_amount": 10000,
  "original_currency": "USD",
  "converted_amount": 40000000,
  "converted_currency": "COP",
  "exchange_rate": 4000.0
}
```

### 3. Filtrar cuentas por moneda
```http
GET /api/accounts/?currency=USD
Authorization: Bearer <token>
```

## ⚠️ Validaciones que el Backend Hace Automáticamente

1. ✅ Si `transaction_currency` != `account.currency`, **debe** haber `exchange_rate` y `original_amount`
2. ✅ El `base_amount` **debe** estar en la moneda de la cuenta
3. ✅ Meta y cuenta **deben** tener la misma moneda (validado en backend)
4. ✅ Transferencias: ambas cuentas **deben** tener la misma moneda

**El frontend NO necesita validar esto**, pero debe:
- Advertir al usuario antes de enviar
- Mostrar claramente la conversión
- Enviar todos los campos requeridos

## 💡 Ejemplo Completo de Flujo

### Usuario crea transacción de ahorro en USD para meta en COP:

1. **Usuario selecciona meta en COP**
2. **Frontend muestra advertencia:**
   ```
   ⚠️ La meta está en COP. Selecciona una cuenta en COP.
   ```
3. **Usuario selecciona cuenta en COP**
4. **Usuario ingresa monto en USD:**
   - Selecciona "USD" en dropdown de moneda
   - Ingresa: 100 USD
5. **Frontend consulta conversión:**
   ```
   GET /api/utils/currency/exchange-rate/?from=USD&to=COP
   → rate: 4000.0

   GET /api/utils/currency/convert/?amount=10000&from=USD&to=COP
   → converted_amount: 40000000
   ```
6. **Frontend muestra:**
   ```
   ℹ️ Conversión de Moneda
   100.00 USD = 400,000.00 COP
   Tasa: 1 USD = 4000 COP
   ```
7. **Frontend envía:**
   ```json
   {
     "type": 4,
     "origin_account": 1,
     "base_amount": 40000000,  // En centavos COP
     "transaction_currency": "USD",
     "exchange_rate": 4000.0,
     "original_amount": 10000,  // En centavos USD
     "goal": 1,
     "date": "2024-01-15"
   }
   ```
8. **Backend valida y guarda correctamente**

## ✅ Resumen

**El backend ya hace todo lo necesario.** El frontend solo debe:
1. Mostrar monedas claramente
2. Advertir sobre diferencias
3. Permitir seleccionar moneda de transacción
4. Mostrar conversión en tiempo real
5. Enviar campos de conversión al backend
6. Formatear montos según moneda
