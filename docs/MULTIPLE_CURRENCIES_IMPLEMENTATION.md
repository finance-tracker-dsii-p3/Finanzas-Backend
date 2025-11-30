# Manejo de Múltiples Monedas - Guía de Implementación

## 📊 Estado Actual del Backend

### ✅ Lo que YA existe:

1. **Cuentas (Account)**: Tienen campo `currency` (COP, USD, EUR)
2. **Presupuestos (Budget)**: Tienen campo `currency` y filtran transacciones por moneda de cuenta
3. **Transacciones (Transaction)**: La moneda se obtiene de `origin_account.currency`

### ❌ Lo que FALTA:

1. **Metas (Goal)**: NO tienen campo `currency` - **NECESITA AGREGARSE**
2. **Validaciones de moneda**: No valida que transacción coincida con cuenta
3. **Conversión de monedas**: No existe servicio de conversión
4. **Advertencias**: No advierte sobre diferencias de moneda

## 🎯 Qué Implementar

### BACKEND (Responsabilidades)

#### 1. Agregar campo `currency` a Goal

```python
# goals/models.py
class Goal(models.Model):
    # ... campos existentes ...
    
    CURRENCY_CHOICES = [
        ('COP', 'Pesos Colombianos'),
        ('USD', 'Dólares'),
        ('EUR', 'Euros'),
    ]
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='COP',
        verbose_name='Moneda',
        help_text='Moneda de la meta de ahorro'
    )
```

#### 2. Validar coincidencia de monedas

**En TransactionSerializer:**
- Validar que `origin_account.currency` coincida con la moneda de la transacción
- Si hay `goal`, validar que `goal.currency` coincida con `origin_account.currency`
- Si hay `destination_account`, validar que ambas cuentas tengan la misma moneda (para transferencias)

**En GoalService:**
- Validar que `transaction.origin_account.currency == goal.currency` antes de asignar

#### 3. Servicio de Conversión de Monedas

```python
# Crear: utils/currency_converter.py
class CurrencyConverter:
    """
    Servicio para conversión de monedas.
    Puede usar API externa (ej: exchangerate-api.com) o tasas fijas.
    """
    
    # Tasas de ejemplo (deberían venir de API o BD)
    EXCHANGE_RATES = {
        'COP': {'USD': 0.00025, 'EUR': 0.00023},  # 1 COP = 0.00025 USD
        'USD': {'COP': 4000, 'EUR': 0.92},        # 1 USD = 4000 COP
        'EUR': {'COP': 4350, 'USD': 1.09},        # 1 EUR = 4350 COP
    }
    
    @staticmethod
    def convert(amount, from_currency, to_currency):
        """
        Convertir monto de una moneda a otra
        
        Args:
            amount: Monto en centavos (entero)
            from_currency: Moneda origen (COP, USD, EUR)
            to_currency: Moneda destino (COP, USD, EUR)
        
        Returns:
            int: Monto convertido en centavos
        """
        if from_currency == to_currency:
            return amount
        
        rate = CurrencyConverter.EXCHANGE_RATES[from_currency][to_currency]
        # Convertir centavos a decimal, aplicar tasa, volver a centavos
        amount_decimal = Decimal(str(amount)) / Decimal('100')
        converted = amount_decimal * Decimal(str(rate))
        return int(converted * 100)
    
    @staticmethod
    def get_exchange_rate(from_currency, to_currency):
        """Obtener tasa de cambio actual"""
        if from_currency == to_currency:
            return Decimal('1.00')
        return Decimal(str(CurrencyConverter.EXCHANGE_RATES[from_currency][to_currency]))
```

#### 4. Campos adicionales en Transaction para conversión

```python
# transactions/models.py
class Transaction(models.Model):
    # ... campos existentes ...
    
    # Campos para conversión de moneda
    transaction_currency = models.CharField(
        max_length=3,
        choices=Account.CURRENCY_CHOICES,
        null=True,
        blank=True,
        verbose_name='Moneda de la transacción',
        help_text='Moneda en que se realizó la transacción (si difiere de la cuenta)'
    )
    
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Tasa de cambio',
        help_text='Tasa de cambio aplicada si hubo conversión'
    )
    
    original_amount = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Monto original',
        help_text='Monto original antes de conversión (en centavos de la moneda original)'
    )
```

### FRONTEND (Responsabilidades)

#### 1. Mostrar moneda de cuenta/meta/presupuesto

```jsx
// Al mostrar cuenta
<div>
  <h3>{account.name}</h3>
  <p>Moneda: {account.currency_display}</p>
  <p>Saldo: {formatMoney(account.current_balance, account.currency)}</p>
</div>

// Al mostrar meta
<div>
  <h3>{goal.name}</h3>
  <p>Moneda: {goal.currency_display}</p>
  <p>Objetivo: {formatMoney(goal.target_amount, goal.currency)}</p>
</div>
```

#### 2. Advertir sobre diferencia de monedas

```jsx
const TransactionForm = ({ account, goal }) => {
  const [showCurrencyWarning, setShowCurrencyWarning] = useState(false);
  const [selectedCurrency, setSelectedCurrency] = useState(account.currency);
  const [exchangeRate, setExchangeRate] = useState(null);
  
  useEffect(() => {
    // Verificar si hay diferencia de monedas
    if (goal && goal.currency !== account.currency) {
      setShowCurrencyWarning(true);
      // Obtener tasa de cambio del backend
      fetchExchangeRate(account.currency, goal.currency);
    }
  }, [account, goal]);
  
  const fetchExchangeRate = async (from, to) => {
    const response = await fetch(`/api/currency/exchange-rate/?from=${from}&to=${to}`);
    const data = await response.json();
    setExchangeRate(data.rate);
  };
  
  return (
    <form>
      {/* Campos del formulario */}
      
      {showCurrencyWarning && (
        <div className="alert alert-warning">
          <strong>⚠️ Advertencia de Moneda</strong>
          <p>
            La cuenta está en {account.currency_display} pero la meta está en {goal.currency_display}.
          </p>
          {exchangeRate && (
            <p>
              Tasa de cambio: 1 {account.currency} = {exchangeRate} {goal.currency}
            </p>
          )}
          <label>
            <input
              type="checkbox"
              checked={convertCurrency}
              onChange={(e) => setConvertCurrency(e.target.checked)}
            />
            Convertir automáticamente a {goal.currency_display}
          </label>
        </div>
      )}
    </form>
  );
};
```

#### 3. Selector de moneda al crear transacción

```jsx
const CreateTransactionForm = ({ account }) => {
  const [transactionCurrency, setTransactionCurrency] = useState(account.currency);
  const [amount, setAmount] = useState('');
  const [convertedAmount, setConvertedAmount] = useState(null);
  
  const handleCurrencyChange = async (newCurrency) => {
    setTransactionCurrency(newCurrency);
    
    if (newCurrency !== account.currency && amount) {
      // Obtener conversión del backend
      const response = await fetch(
        `/api/currency/convert/?amount=${amount}&from=${newCurrency}&to=${account.currency}`
      );
      const data = await response.json();
      setConvertedAmount(data.converted_amount);
    } else {
      setConvertedAmount(null);
    }
  };
  
  return (
    <form>
      <div>
        <label>Moneda de la transacción</label>
        <select
          value={transactionCurrency}
          onChange={(e) => handleCurrencyChange(e.target.value)}
        >
          <option value="COP">Pesos Colombianos (COP)</option>
          <option value="USD">Dólares (USD)</option>
          <option value="EUR">Euros (EUR)</option>
        </select>
        
        {transactionCurrency !== account.currency && (
          <div className="info">
            <p>
              La cuenta está en {account.currency_display}. 
              El monto se convertirá automáticamente.
            </p>
            {convertedAmount && (
              <p>
                {formatMoney(amount, transactionCurrency)} = 
                {formatMoney(convertedAmount, account.currency)}
              </p>
            )}
          </div>
        )}
      </div>
      
      <div>
        <label>Monto (en {transactionCurrency})</label>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
      </div>
    </form>
  );
};
```

#### 4. Formatear montos según moneda

```javascript
const formatMoney = (centavos, currency) => {
  const amount = centavos / 100;
  
  const formatters = {
    'COP': new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }),
    'USD': new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }),
    'EUR': new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2
    })
  };
  
  return formatters[currency].format(amount);
};
```

## 🔄 Flujo Completo con Conversión

### Escenario: Usuario recibe ingreso en USD pero cuenta es en COP

1. **Frontend muestra:**
   - Cuenta: "Cuenta Principal (COP)"
   - Selector: "Moneda de transacción: USD"
   - Input: "Monto: 100 USD"
   - Advertencia: "Se convertirá a COP a tasa actual"

2. **Frontend calcula conversión:**
   ```
   GET /api/currency/exchange-rate/?from=USD&to=COP
   → { rate: 4000 }
   
   Muestra: "100 USD = 400,000 COP"
   ```

3. **Frontend envía al backend:**
   ```json
   {
     "type": 1,
     "origin_account": 1,
     "base_amount": 40000000,  // 400,000 COP en centavos
     "transaction_currency": "USD",
     "exchange_rate": 4000.0,
     "original_amount": 10000,  // 100 USD en centavos
     "date": "2024-01-15"
   }
   ```

4. **Backend valida:**
   - ✅ `origin_account.currency == "COP"`
   - ✅ `transaction_currency == "USD"`
   - ✅ `base_amount` ya está convertido a COP
   - ✅ Guarda `original_amount` y `exchange_rate` para auditoría

5. **Backend actualiza:**
   - Saldo de cuenta en COP
   - Transacción guardada con información de conversión

## 📋 Endpoints Necesarios en Backend

### 1. Obtener tasa de cambio

```http
GET /api/currency/exchange-rate/?from=USD&to=COP
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
GET /api/currency/convert/?amount=10000&from=USD&to=COP
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

## ✅ Checklist de Implementación

### Backend:
- [ ] Agregar campo `currency` a Goal
- [ ] Crear migración para Goal.currency
- [ ] Agregar campos `transaction_currency`, `exchange_rate`, `original_amount` a Transaction
- [ ] Crear migración para campos de conversión
- [ ] Crear servicio `CurrencyConverter`
- [ ] Crear endpoints `/api/currency/exchange-rate/` y `/api/currency/convert/`
- [ ] Validar coincidencia de monedas en TransactionSerializer
- [ ] Validar coincidencia de monedas en GoalService
- [ ] Actualizar serializers para incluir campos de moneda

### Frontend:
- [ ] Mostrar moneda en componentes de cuenta/meta/presupuesto
- [ ] Advertir cuando hay diferencia de monedas
- [ ] Selector de moneda en formulario de transacción
- [ ] Mostrar conversión en tiempo real
- [ ] Formatear montos según moneda
- [ ] Enviar campos de conversión al backend
- [ ] Mostrar información de conversión en historial

## 🚨 Validaciones Importantes

### Backend debe validar:

1. **Transacción → Cuenta:**
   - Si `transaction_currency` != `origin_account.currency`, debe haber `exchange_rate` y `original_amount`
   - El `base_amount` debe estar en la moneda de la cuenta

2. **Transacción → Meta:**
   - `goal.currency` debe coincidir con `origin_account.currency` (o convertirse)
   - Si hay conversión, guardar información

3. **Transferencia:**
   - `origin_account.currency` debe coincidir con `destination_account.currency`
   - O permitir conversión y guardar información

### Frontend debe:

1. **Advertir siempre** cuando hay diferencia de monedas
2. **Mostrar conversión** antes de enviar
3. **Permitir cancelar** si el usuario no quiere convertir
4. **Mostrar claramente** la moneda en todos los componentes

## 💡 Recomendaciones

1. **Usar API de tasas de cambio** (ej: exchangerate-api.com, fixer.io) para tasas actuales
2. **Guardar historial de tasas** para auditoría
3. **Permitir tasas manuales** para casos especiales
4. **Mostrar advertencias claras** en el frontend
5. **Validar en ambos lados** (frontend para UX, backend para seguridad)

