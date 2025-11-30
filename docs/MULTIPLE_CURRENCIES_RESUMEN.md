# Manejo de Múltiples Monedas - Resumen Ejecutivo

## ✅ Lo que se Implementó en el Backend

### 1. Campo `currency` en Goal
- ✅ Agregado campo `currency` a modelo Goal
- ✅ Agregado a serializers (creación, lectura, actualización)
- ✅ Migración pendiente: `python manage.py makemigrations goals`

### 2. Campos de conversión en Transaction
- ✅ `transaction_currency`: Moneda en que se realizó la transacción
- ✅ `exchange_rate`: Tasa de cambio aplicada
- ✅ `original_amount`: Monto original antes de conversión
- ✅ Migración pendiente: `python manage.py makemigrations transactions`

### 3. Servicio de Conversión
- ✅ Creado `utils/currency_converter.py` con:
  - Método `convert()`: Convierte montos entre monedas
  - Método `get_exchange_rate()`: Obtiene tasa de cambio
  - Soporta: COP, USD, EUR

### 4. Endpoints de Conversión
- ✅ `GET /api/utils/currency/exchange-rate/?from=USD&to=COP`
- ✅ `GET /api/utils/currency/convert/?amount=10000&from=USD&to=COP`

### 5. Validaciones
- ✅ GoalService valida que cuenta y meta tengan la misma moneda

## 📋 Pendiente por Implementar

### Backend:
- [ ] Validar en TransactionSerializer que si `transaction_currency` != `origin_account.currency`, debe haber `exchange_rate` y `original_amount`
- [ ] Convertir automáticamente el monto si hay diferencia de monedas
- [ ] Validar que transferencias tengan misma moneda (o permitir conversión)

### Frontend:
- [ ] Mostrar moneda en todos los componentes
- [ ] Advertir cuando hay diferencia de monedas
- [ ] Selector de moneda en formulario de transacción
- [ ] Mostrar conversión en tiempo real
- [ ] Formatear montos según moneda

## 🎯 División de Responsabilidades

### BACKEND hace:
1. ✅ Almacenar moneda de cuenta/meta/presupuesto
2. ✅ Validar coincidencia de monedas
3. ✅ Convertir montos cuando hay diferencia
4. ✅ Guardar información de conversión (tasa, monto original)
5. ✅ Proporcionar endpoints para obtener tasas y convertir

### FRONTEND hace:
1. ⚠️ Mostrar moneda en todos los componentes
2. ⚠️ Advertir al usuario sobre diferencias de moneda
3. ⚠️ Permitir seleccionar moneda de transacción
4. ⚠️ Mostrar conversión en tiempo real antes de enviar
5. ⚠️ Formatear montos según moneda (COP, USD, EUR)
6. ⚠️ Enviar campos de conversión al backend

## 📝 Ejemplo de Flujo Completo

### Usuario recibe ingreso en USD pero cuenta es en COP:

**1. Frontend muestra:**
```
Cuenta: "Cuenta Principal (COP)"
Moneda de transacción: [USD ▼]
Monto: 100 USD
⚠️ Se convertirá a 400,000 COP (tasa: 4000)
```

**2. Frontend consulta tasa:**
```javascript
GET /api/utils/currency/exchange-rate/?from=USD&to=COP
→ { rate: 4000.0 }
```

**3. Frontend calcula y muestra:**
```
100 USD = 400,000 COP
```

**4. Frontend envía al backend:**
```json
{
  "type": 1,
  "origin_account": 1,
  "base_amount": 40000000,  // En centavos COP
  "transaction_currency": "USD",
  "exchange_rate": 4000.0,
  "original_amount": 10000,  // En centavos USD
  "date": "2024-01-15"
}
```

**5. Backend valida y guarda:**
- ✅ `base_amount` está en COP (moneda de cuenta)
- ✅ Guarda `original_amount` y `exchange_rate` para auditoría
- ✅ Actualiza saldo de cuenta en COP

## 🚨 Validaciones Importantes

### Backend valida:
- ✅ Meta y cuenta deben tener misma moneda (o convertir)
- ⚠️ Si `transaction_currency` != `account.currency`, debe haber conversión
- ⚠️ Transferencias: ambas cuentas misma moneda (o convertir)

### Frontend debe:
- ⚠️ Advertir SIEMPRE cuando hay diferencia de monedas
- ⚠️ Mostrar conversión antes de enviar
- ⚠️ Permitir cancelar si no quiere convertir

## 📚 Documentación Completa

Ver: `docs/MULTIPLE_CURRENCIES_IMPLEMENTATION.md`

