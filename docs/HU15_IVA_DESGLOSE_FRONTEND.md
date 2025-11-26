# HU-15: Desglose Simple de IVA en Movimientos - Guía para Frontend

## 📋 Resumen

Esta funcionalidad permite a los usuarios ingresar el **total** de un movimiento junto con la **tasa de IVA**, y el sistema calcula automáticamente la **base** y el **IVA** desglosado.

## 🎯 Funcionalidad

### Modo de Operación

El backend soporta **dos modos** de creación/edición de transacciones:

1. **Modo Tradicional** (compatible con versiones anteriores):
   - Usuario ingresa: `base_amount` + `tax_percentage` (opcional)
   - Sistema calcula: `taxed_amount` y `total_amount`

2. **Modo Nuevo (HU-15)**:
   - Usuario ingresa: `total_amount` + `tax_percentage` (opcional)
   - Sistema calcula: `base_amount` y `taxed_amount`

### ⚠️ Reglas Importantes

- **NO se pueden enviar** `base_amount` y `total_amount` simultáneamente
- Si se envía `tax_percentage`, debe ir acompañado de `total_amount` (modo nuevo) o `base_amount` (modo tradicional)
- El `tax_percentage` debe estar entre **0 y 30%**
- El `total_amount` debe ser **mayor a cero**
- El IVA es **opcional**: si no se envía `tax_percentage`, el movimiento funciona normalmente sin IVA

---

## 🔌 Endpoints

### 1. Crear Transacción con IVA

**Endpoint:** `POST /api/transactions/`

**Headers:**
```
Authorization: Token <token_usuario>
Content-Type: application/json
```

**Body (Modo Nuevo - HU-15):**
```json
{
  "origin_account": 1,
  "category": 2,
  "type": 2,
  "total_amount": 119000,
  "tax_percentage": 19,
  "date": "2025-01-15",
  "tag": "compra",
  "note": "Compra con IVA"
}
```

**Body (Modo Tradicional - Compatible):**
```json
{
  "origin_account": 1,
  "category": 2,
  "type": 2,
  "base_amount": 100000,
  "tax_percentage": 19,
  "date": "2025-01-15"
}
```

**Body (Sin IVA):**
```json
{
  "origin_account": 1,
  "category": 2,
  "type": 2,
  "total_amount": 50000,
  "date": "2025-01-15"
}
```

**Respuesta Exitosa (201 Created):**
```json
{
  "id": 123,
  "origin_account": 1,
  "origin_account_name": "Cuenta Principal",
  "category": 2,
  "category_name": "Alimentación",
  "category_color": "#B71C1C",
  "type": 2,
  "base_amount": 100000,
  "tax_percentage": 19,
  "taxed_amount": 19000,
  "gmf_amount": 476,
  "total_amount": 119476,
  "date": "2025-01-15",
  "tag": "compra",
  "note": "Compra con IVA",
  "description": null,
  "applied_rule": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Errores Posibles:**

```json
// Error: Enviar ambos base_amount y total_amount
{
  "base_amount": ["No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro."],
  "total_amount": ["No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro."]
}

// Error: IVA fuera de rango
{
  "tax_percentage": ["La tasa de IVA debe estar entre 0 y 30%."]
}

// Error: Total inválido
{
  "total_amount": ["El monto total debe ser un valor positivo mayor que cero."]
}
```

---

### 2. Actualizar Transacción con IVA

**Endpoint:** `PATCH /api/transactions/{id}/`

**Headers:**
```
Authorization: Token <token_usuario>
Content-Type: application/json
```

**Body (Modo Nuevo - HU-15):**
```json
{
  "total_amount": 119000,
  "tax_percentage": 19
}
```

**Body (Modo Tradicional):**
```json
{
  "base_amount": 100000,
  "tax_percentage": 19
}
```

**Body (Eliminar IVA):**
```json
{
  "tax_percentage": null
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 123,
  "base_amount": 100000,
  "tax_percentage": 19,
  "taxed_amount": 19000,
  "gmf_amount": 476,
  "total_amount": 119476,
  ...
}
```

---

### 3. Ver Detalle de Transacción

**Endpoint:** `GET /api/transactions/{id}/`

**Headers:**
```
Authorization: Token <token_usuario>
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 123,
  "base_amount": 100000,
  "tax_percentage": 19,
  "taxed_amount": 19000,
  "gmf_amount": 476,
  "total_amount": 119476,
  ...
}
```

---

## 🧮 Cálculos del Backend

### Fórmulas Utilizadas

Cuando el frontend envía `total_amount` + `tax_percentage`:

1. **Base calculada:**
   ```
   base_amount = total_amount / (1 + tax_percentage/100)
   ```

2. **IVA calculado:**
   ```
   taxed_amount = total_amount - base_amount
   ```

3. **GMF (si aplica):**
   ```
   gmf_amount = (base_amount + taxed_amount) * 0.004
   ```

4. **Total final:**
   ```
   total_amount_final = base_amount + taxed_amount + gmf_amount
   ```

### Ejemplo Práctico

**Input del Frontend:**
- `total_amount`: 119000
- `tax_percentage`: 19

**Cálculos del Backend:**
1. `base_amount = 119000 / (1 + 19/100) = 119000 / 1.19 = 100000`
2. `taxed_amount = 119000 - 100000 = 19000`
3. `gmf_amount = (100000 + 19000) * 0.004 = 476` (si aplica)
4. `total_amount_final = 100000 + 19000 + 476 = 119476`

---

## 🎨 Interfaz de Usuario Recomendada

### Campos del Formulario

#### Opción 1: Modo Simple (Recomendado para HU-15)

```
┌─────────────────────────────────────────┐
│ Total a pagar:                          │
│ [119000                    ]            │
│                                         │
│ IVA (%) (opcional):                     │
│ [19                       ]             │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Desglose:                           │ │
│ │ Base: $100,000                      │ │
│ │ IVA (19%): $19,000                  │ │
│ │ GMF: $476                           │ │
│ │ Total: $119,476                     │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

#### Opción 2: Modo Avanzado (Compatible con ambos modos)

```
┌─────────────────────────────────────────┐
│ Modo de entrada:                        │
│ ○ Total con IVA  ● Base sin IVA        │
│                                         │
│ Total a pagar:                          │
│ [119000                    ]            │
│                                         │
│ IVA (%) (opcional):                     │
│ [19                       ]             │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Desglose calculado:                 │ │
│ │ Base: $100,000                      │ │
│ │ IVA (19%): $19,000                  │ │
│ │ GMF: $476                           │ │
│ │ Total final: $119,476               │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Etiquetas Sugeridas

- **"Total"** o **"Total a pagar"** para `total_amount`
- **"IVA (%)"** o **"Tasa de IVA (%)"** para `tax_percentage`
- **"Base calculada"** para mostrar `base_amount`
- **"IVA calculado"** para mostrar `taxed_amount`
- **"GMF"** para mostrar `gmf_amount` (si aplica)
- **"Total final"** para mostrar el `total_amount` final (incluye GMF)

---

## 💻 Implementación en Frontend

### Ejemplo con React/TypeScript

```typescript
interface TransactionFormData {
  origin_account: number;
  category: number;
  type: number;
  total_amount?: number;
  tax_percentage?: number;
  date: string;
  tag?: string;
  note?: string;
}

const TransactionForm: React.FC = () => {
  const [formData, setFormData] = useState<TransactionFormData>({
    origin_account: 0,
    category: 0,
    type: 2,
    date: new Date().toISOString().split('T')[0],
  });

  const [breakdown, setBreakdown] = useState<{
    base: number;
    tax: number;
    gmf: number;
    total: number;
  } | null>(null);

  // Calcular desglose en tiempo real
  const calculateBreakdown = (total: number, taxPercent?: number) => {
    if (!taxPercent || taxPercent === 0) {
      setBreakdown(null);
      return;
    }

    const taxRate = taxPercent / 100;
    const base = total / (1 + taxRate);
    const tax = total - base;
    const gmf = (base + tax) * 0.004; // 0.4%
    const finalTotal = base + tax + gmf;

    setBreakdown({
      base: Math.round(base),
      tax: Math.round(tax),
      gmf: Math.round(gmf),
      total: Math.round(finalTotal),
    });
  };

  const handleTotalChange = (value: number) => {
    setFormData({ ...formData, total_amount: value });
    calculateBreakdown(value, formData.tax_percentage);
  };

  const handleTaxChange = (value: number) => {
    const taxValue = value > 30 ? 30 : value < 0 ? 0 : value;
    setFormData({ ...formData, tax_percentage: taxValue });
    if (formData.total_amount) {
      calculateBreakdown(formData.total_amount, taxValue);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validaciones
    if (!formData.total_amount || formData.total_amount <= 0) {
      alert('El total debe ser mayor a cero');
      return;
    }

    if (formData.tax_percentage !== undefined) {
      if (formData.tax_percentage < 0 || formData.tax_percentage > 30) {
        alert('La tasa de IVA debe estar entre 0 y 30%');
        return;
      }
    }

    try {
      const response = await fetch('/api/transactions/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${userToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          origin_account: formData.origin_account,
          category: formData.category,
          type: formData.type,
          total_amount: formData.total_amount,
          tax_percentage: formData.tax_percentage || undefined,
          date: formData.date,
          tag: formData.tag,
          note: formData.note,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        console.error('Error:', error);
        return;
      }

      const transaction = await response.json();
      console.log('Transacción creada:', transaction);
    } catch (error) {
      console.error('Error al crear transacción:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Total a pagar:</label>
        <input
          type="number"
          value={formData.total_amount || ''}
          onChange={(e) => handleTotalChange(Number(e.target.value))}
          required
          min="1"
        />
      </div>

      <div>
        <label>IVA (%) (opcional):</label>
        <input
          type="number"
          value={formData.tax_percentage || ''}
          onChange={(e) => handleTaxChange(Number(e.target.value))}
          min="0"
          max="30"
          step="0.01"
        />
      </div>

      {breakdown && (
        <div className="breakdown">
          <h3>Desglose:</h3>
          <p>Base: ${breakdown.base.toLocaleString()}</p>
          <p>IVA ({formData.tax_percentage}%): ${breakdown.tax.toLocaleString()}</p>
          <p>GMF: ${breakdown.gmf.toLocaleString()}</p>
          <p><strong>Total final: ${breakdown.total.toLocaleString()}</strong></p>
        </div>
      )}

      <button type="submit">Crear Transacción</button>
    </form>
  );
};
```

---

## 📝 Validaciones del Frontend

### Validaciones Recomendadas

1. **Total:**
   - Debe ser mayor a 0
   - Debe ser un número válido
   - Mostrar error si está vacío

2. **IVA:**
   - Debe estar entre 0 y 30
   - Es opcional (puede estar vacío)
   - Mostrar error si está fuera de rango

3. **Validación de Modo:**
   - NO permitir enviar `base_amount` y `total_amount` simultáneamente
   - Si se usa el modo nuevo (HU-15), solo enviar `total_amount` + `tax_percentage`

### Mensajes de Error Sugeridos

```typescript
const errorMessages = {
  total_required: 'El total es requerido',
  total_positive: 'El total debe ser mayor a cero',
  tax_range: 'La tasa de IVA debe estar entre 0 y 30%',
  both_amounts: 'No se puede proporcionar base y total simultáneamente',
};
```

---

## 🔄 Flujo Completo

### Crear Transacción con IVA

1. Usuario ingresa **Total**: 119000
2. Usuario ingresa **IVA**: 19%
3. Frontend calcula y muestra desglose:
   - Base: 100000
   - IVA: 19000
   - GMF: 476 (estimado)
   - Total final: 119476
4. Usuario confirma y envía al backend
5. Backend calcula valores exactos y guarda
6. Backend responde con la transacción completa

### Editar Transacción con IVA

1. Frontend carga transacción existente
2. Muestra `total_amount` y `tax_percentage` actuales
3. Usuario modifica valores
4. Frontend recalcula desglose en tiempo real
5. Usuario guarda cambios
6. Backend actualiza y responde

### Ver Detalle de Transacción

1. Frontend obtiene transacción con `GET /api/transactions/{id}/`
2. Muestra todos los campos:
   - `base_amount`
   - `tax_percentage`
   - `taxed_amount`
   - `gmf_amount`
   - `total_amount`
3. Si `tax_percentage` existe, mostrar desglose visual

---

## ⚠️ Consideraciones Importantes

### GMF (Gravamen a los Movimientos Financieros)

- El GMF se calcula automáticamente en el backend
- Solo aplica a:
  - Gastos (type = 2)
  - Transferencias (type = 3)
  - Desde cuentas NO exentas
  - NO aplica a tarjetas de crédito
- El GMF se agrega al `total_amount` final
- El frontend puede mostrar una estimación, pero el valor exacto viene del backend

### Compatibilidad

- El backend mantiene compatibilidad con el modo tradicional
- Si el frontend envía `base_amount` + `tax_percentage`, funciona como antes
- Si el frontend envía `total_amount` + `tax_percentage`, usa el modo nuevo (HU-15)

### Sin IVA

- Si no se envía `tax_percentage` o es `null`, el movimiento funciona normalmente
- El `total_amount` se usa directamente (sin desglose de IVA)
- El GMF se calcula sobre el `total_amount` si aplica

---

## 📊 Ejemplos de Respuestas

### Transacción con IVA

```json
{
  "id": 123,
  "base_amount": 100000,
  "tax_percentage": 19,
  "taxed_amount": 19000,
  "gmf_amount": 476,
  "total_amount": 119476
}
```

### Transacción sin IVA

```json
{
  "id": 124,
  "base_amount": 50000,
  "tax_percentage": null,
  "taxed_amount": 0,
  "gmf_amount": 200,
  "total_amount": 50200
}
```

---

## 🧪 Casos de Prueba

### Caso 1: Crear con IVA
- **Input:** `total_amount: 119000`, `tax_percentage: 19`
- **Esperado:** `base_amount: 100000`, `taxed_amount: 19000`

### Caso 2: Crear sin IVA
- **Input:** `total_amount: 50000`, `tax_percentage: null`
- **Esperado:** `base_amount: 50000`, `taxed_amount: 0`

### Caso 3: IVA fuera de rango
- **Input:** `total_amount: 100000`, `tax_percentage: 35`
- **Esperado:** Error 400: "La tasa de IVA debe estar entre 0 y 30%"

### Caso 4: Total inválido
- **Input:** `total_amount: 0`, `tax_percentage: 19`
- **Esperado:** Error 400: "El monto total debe ser un valor positivo mayor que cero"

### Caso 5: Ambos modos simultáneos
- **Input:** `base_amount: 100000`, `total_amount: 119000`, `tax_percentage: 19`
- **Esperado:** Error 400: "No se puede proporcionar base_amount y total_amount simultáneamente"

---

## 📞 Soporte

Si tienes dudas o encuentras problemas:

1. Revisa los mensajes de error del backend
2. Verifica que los campos estén en el formato correcto
3. Asegúrate de que el token de autenticación sea válido
4. Consulta la documentación de la API general en `/docs/API_REFERENCE.md`

---

## ✅ Checklist de Implementación

- [ ] Formulario con campo "Total"
- [ ] Campo opcional "IVA (%)" con validación 0-30
- [ ] Cálculo en tiempo real del desglose
- [ ] Visualización del desglose (Base, IVA, GMF, Total)
- [ ] Validación de campos antes de enviar
- [ ] Manejo de errores del backend
- [ ] Mostrar desglose en vista de detalle
- [ ] Permitir editar transacciones con IVA
- [ ] Soporte para transacciones sin IVA
- [ ] Pruebas con diferentes valores de IVA

---

**Última actualización:** 2025-01-15
**Versión del API:** 1.0
**HU Implementada:** HU-15

