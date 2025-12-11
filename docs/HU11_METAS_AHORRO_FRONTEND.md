# HU-11: Metas de Ahorro - Guía de Implementación Frontend

## Resumen

Esta guía describe cómo implementar la funcionalidad de **Metas de Ahorro** en el frontend, basándose en la API del backend que ya está implementada.

## Endpoints Disponibles

### Base URL
```
/api/goals/
```

### Operaciones CRUD

#### 1. Listar todas las metas del usuario
```http
GET /api/goals/
Authorization: Bearer <token>
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "user": 1,
    "name": "Viaje a San Andres",
    "target_amount": 4000000,
    "saved_amount": 1200000,
    "date": "2024-12-31",
    "description": "Vacaciones de fin de año",
    "progress_percentage": 30.0,
    "remaining_amount": 2800000,
    "is_completed": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T15:45:00Z"
  }
]
```

**Respuesta cuando no hay metas:**
```json
{
  "count": 0,
  "message": "No tienes metas creadas.",
  "results": []
}
```

#### 2. Obtener una meta específica
```http
GET /api/goals/{id}/
Authorization: Bearer <token>
```

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "user": 1,
  "name": "Viaje a San Andres",
  "target_amount": 4000000,
  "saved_amount": 1200000,
  "date": "2024-12-31",
  "description": "Vacaciones de fin de año",
  "progress_percentage": 30.0,
  "remaining_amount": 2800000,
  "is_completed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T15:45:00Z"
}
```

#### 3. Crear una nueva meta
```http
POST /api/goals/
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Viaje a San Andres",
  "target_amount": 4000000,
  "date": "2024-12-31",
  "description": "Vacaciones de fin de año"
}
```

**Nota:** `saved_amount` se inicializa automáticamente en 0, no es necesario enviarlo.

**Respuesta exitosa (201):**
```json
{
  "id": 1,
  "user": 1,
  "name": "Viaje a San Andres",
  "target_amount": 4000000,
  "saved_amount": 0,
  "date": "2024-12-31",
  "description": "Vacaciones de fin de año"
}
```

#### 4. Actualizar una meta
```http
PATCH /api/goals/{id}/
Authorization: Bearer <token>
Content-Type: application/json
```

**Body (campos opcionales):**
```json
{
  "name": "Viaje a San Andres - Actualizado",
  "target_amount": 5000000,
  "date": "2025-01-31",
  "description": "Nueva descripción"
}
```

**Nota:** No se puede actualizar `saved_amount` directamente. Este campo se actualiza automáticamente cuando se asignan transacciones tipo Saving a la meta.

#### 5. Eliminar una meta
```http
DELETE /api/goals/{id}/
Authorization: Bearer <token>
```

**Respuesta exitosa (204):** Sin contenido

## Asignar Transacciones a Metas

### Crear transacción tipo Saving asignada a una meta

```http
POST /api/transactions/
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "type": 4,
  "origin_account": 1,
  "base_amount": 200000,
  "date": "2024-01-15",
  "goal": 1,
  "description": "Ahorro para viaje"
}
```

**Tipos de transacción:**
- `1`: Income (Ingreso)
- `2`: Expense (Gasto)
- `3`: Transfer (Transferencia)
- `4`: Saving (Ahorro) ← **Usar este tipo para asignar a metas**

**Nota importante:**
- Solo las transacciones tipo `Saving` (type=4) pueden tener un `goal` asignado.
- Cuando se crea una transacción tipo Saving con un `goal`, el backend automáticamente:
  1. Actualiza el `saved_amount` de la meta
  2. Envía notificaciones si se acerca o alcanza la meta

### Ver transacciones de una meta

Las transacciones asignadas a una meta se pueden obtener a través de la relación inversa:

```http
GET /api/goals/{id}/transactions/
```

**Nota:** Este endpoint no está implementado directamente, pero puedes filtrar transacciones:

```http
GET /api/transactions/?goal={goal_id}
Authorization: Bearer <token>
```

## Campos Importantes

### Campos de la Meta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único de la meta |
| `name` | string | Nombre de la meta (requerido) |
| `target_amount` | integer | Monto objetivo en centavos (requerido) |
| `saved_amount` | integer | Monto ahorrado en centavos (calculado automáticamente) |
| `date` | date | Fecha objetivo para alcanzar la meta (formato: YYYY-MM-DD) |
| `description` | string | Descripción opcional |
| `progress_percentage` | float | Porcentaje de progreso (0-100) - **calculado** |
| `remaining_amount` | integer | Monto restante para alcanzar la meta - **calculado** |
| `is_completed` | boolean | Indica si la meta ha sido alcanzada - **calculado** |

### Conversión de Montos

**IMPORTANTE:** El backend almacena los montos en **centavos** (enteros). El frontend debe convertir:

- **Backend → Frontend:** Dividir por 100
  ```javascript
  const amountInPesos = goal.target_amount / 100;
  ```

- **Frontend → Backend:** Multiplicar por 100
  ```javascript
  const amountInCents = Math.round(amountInPesos * 100);
  ```

## Notificaciones

El backend envía notificaciones automáticamente cuando:

1. **Se alcanza una meta:**
   - Título: "¡Meta alcanzada! 🎉"
   - Mensaje: "Has alcanzado tu meta '{nombre}'. ¡Felicidades!"

2. **Se acerca a la meta (faltan $300.000 o menos):**
   - Título: "¡Casi lo logras! 💪"
   - Mensaje: "Te faltan ${monto} para alcanzar tu meta '{nombre}'"

Para obtener notificaciones:

```http
GET /api/notifications/
Authorization: Bearer <token>
```

Filtrar por tipo relacionado con metas si es necesario.

## Ejemplos de Implementación

### 1. Componente de Lista de Metas

```typescript
// Ejemplo en React/TypeScript
interface Goal {
  id: number;
  name: string;
  target_amount: number;
  saved_amount: number;
  date: string;
  description?: string;
  progress_percentage: number;
  remaining_amount: number;
  is_completed: boolean;
}

const GoalsList = () => {
  const [goals, setGoals] = useState<Goal[]>([]);

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    const response = await fetch('/api/goals/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    setGoals(data);
  };

  return (
    <div>
      {goals.map(goal => (
        <GoalCard key={goal.id} goal={goal} />
      ))}
    </div>
  );
};
```

### 2. Componente de Tarjeta de Meta con Barra de Progreso

```typescript
const GoalCard = ({ goal }: { goal: Goal }) => {
  const targetInPesos = goal.target_amount / 100;
  const savedInPesos = goal.saved_amount / 100;
  const remainingInPesos = goal.remaining_amount / 100;

  return (
    <div className="goal-card">
      <h3>{goal.name}</h3>
      {goal.description && <p>{goal.description}</p>}

      {/* Barra de progreso */}
      <div className="progress-bar-container">
        <div
          className="progress-bar-fill"
          style={{ width: `${goal.progress_percentage}%` }}
        />
      </div>

      {/* Información de progreso */}
      <div className="progress-info">
        <span>
          ${savedInPesos.toLocaleString()} / ${targetInPesos.toLocaleString()}
        </span>
        <span className="percentage">
          → {goal.progress_percentage.toFixed(1)}%
        </span>
      </div>

      {/* Monto restante */}
      {!goal.is_completed && (
        <p className="remaining">
          Faltan ${remainingInPesos.toLocaleString()}
        </p>
      )}

      {goal.is_completed && (
        <p className="completed">¡Meta alcanzada! 🎉</p>
      )}

      <p>Fecha objetivo: {new Date(goal.date).toLocaleDateString()}</p>
    </div>
  );
};
```

### 3. Formulario para Crear Meta

```typescript
const CreateGoalForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    target_amount: '',
    date: '',
    description: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      name: formData.name,
      target_amount: Math.round(parseFloat(formData.target_amount) * 100), // Convertir a centavos
      date: formData.date,
      description: formData.description || undefined
    };

    const response = await fetch('/api/goals/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      // Meta creada exitosamente
      // Redirigir o actualizar lista
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Nombre de la meta"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        required
      />

      <input
        type="number"
        placeholder="Monto objetivo (en pesos)"
        value={formData.target_amount}
        onChange={(e) => setFormData({...formData, target_amount: e.target.value})}
        required
        min="1"
        step="0.01"
      />

      <input
        type="date"
        value={formData.date}
        onChange={(e) => setFormData({...formData, date: e.target.value})}
        required
      />

      <textarea
        placeholder="Descripción (opcional)"
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
      />

      <button type="submit">Crear Meta</button>
    </form>
  );
};
```

### 4. Asignar Transacción a Meta

```typescript
const CreateSavingTransaction = ({ goalId }: { goalId: number }) => {
  const [formData, setFormData] = useState({
    origin_account: '',
    base_amount: '',
    date: new Date().toISOString().split('T')[0],
    description: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      type: 4, // Saving
      origin_account: parseInt(formData.origin_account),
      base_amount: Math.round(parseFloat(formData.base_amount) * 100), // Convertir a centavos
      date: formData.date,
      goal: goalId, // Asignar a la meta
      description: formData.description || undefined
    };

    const response = await fetch('/api/transactions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      // Transacción creada y asignada a la meta
      // El backend actualizará automáticamente el saved_amount de la meta
      // Y enviará notificaciones si corresponde
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <select
        value={formData.origin_account}
        onChange={(e) => setFormData({...formData, origin_account: e.target.value})}
        required
      >
        <option value="">Seleccionar cuenta</option>
        {/* Opciones de cuentas */}
      </select>

      <input
        type="number"
        placeholder="Monto a ahorrar (en pesos)"
        value={formData.base_amount}
        onChange={(e) => setFormData({...formData, base_amount: e.target.value})}
        required
        min="0.01"
        step="0.01"
      />

      <input
        type="date"
        value={formData.date}
        onChange={(e) => setFormData({...formData, date: e.target.value})}
        required
      />

      <textarea
        placeholder="Descripción (opcional)"
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
      />

      <button type="submit">Registrar Ahorro</button>
    </form>
  );
};
```

### 5. Selector de Meta al Crear Transacción de Ingreso

```typescript
const CreateIncomeWithGoal = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<number | null>(null);

  useEffect(() => {
    // Cargar metas del usuario
    fetch('/api/goals/')
      .then(res => res.json())
      .then(data => setGoals(data));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Primero crear el ingreso
    const incomePayload = {
      type: 1, // Income
      origin_account: formData.origin_account,
      base_amount: Math.round(parseFloat(formData.base_amount) * 100),
      date: formData.date,
      category: formData.category
    };

    const incomeResponse = await fetch('/api/transactions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(incomePayload)
    });

    if (incomeResponse.ok && selectedGoal) {
      // Luego crear una transacción de ahorro asignada a la meta
      const savingPayload = {
        type: 4, // Saving
        origin_account: formData.origin_account,
        base_amount: Math.round(parseFloat(formData.saving_amount) * 100),
        date: formData.date,
        goal: selectedGoal,
        description: `Ahorro asignado desde ingreso`
      };

      await fetch('/api/transactions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(savingPayload)
      });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Campos del ingreso */}

      <div>
        <label>¿Asignar parte a una meta?</label>
        <select
          value={selectedGoal || ''}
          onChange={(e) => setSelectedGoal(e.target.value ? parseInt(e.target.value) : null)}
        >
          <option value="">No asignar</option>
          {goals.map(goal => (
            <option key={goal.id} value={goal.id}>
              {goal.name}
            </option>
          ))}
        </select>
      </div>

      {selectedGoal && (
        <input
          type="number"
          placeholder="Monto a asignar a la meta"
          name="saving_amount"
          min="0.01"
          step="0.01"
        />
      )}

      <button type="submit">Registrar</button>
    </form>
  );
};
```

## Validaciones del Frontend

1. **Al crear una meta:**
   - `name`: Requerido, máximo 100 caracteres
   - `target_amount`: Requerido, debe ser mayor que 0
   - `date`: Requerido, debe ser una fecha válida

2. **Al asignar transacción a meta:**
   - Solo transacciones tipo `Saving` (type=4) pueden tener `goal`
   - El `goal` debe pertenecer al usuario autenticado
   - El monto no puede exceder el `remaining_amount` de la meta (validación opcional en frontend)

## Manejo de Errores

### Errores comunes:

1. **400 Bad Request:** Datos inválidos
   ```json
   {
     "target_amount": ["El monto objetivo debe ser un valor positivo mayor que cero."]
   }
   ```

2. **400 Bad Request:** Intentar asignar goal a transacción no-Saving
   ```json
   {
     "goal": ["Solo se pueden asignar metas a transacciones tipo Saving (type=4)."]
   }
   ```

3. **404 Not Found:** Meta no existe o no pertenece al usuario

4. **401 Unauthorized:** Token inválido o expirado

## Flujo Completo de Usuario

1. **Usuario crea una meta:**
   - Completa formulario con nombre, monto objetivo, fecha y descripción opcional
   - Backend crea la meta con `saved_amount = 0`

2. **Usuario registra un ingreso:**
   - Opcionalmente puede elegir "Asignar a meta"
   - Si elige asignar, se crea una transacción tipo Saving con el monto especificado
   - Backend actualiza automáticamente el `saved_amount` de la meta

3. **Usuario ve el progreso:**
   - La lista de metas muestra el progreso con barra visual
   - Muestra: "$1.200.000 / $4.000.000 → 30%"
   - Muestra monto restante: "Faltan $2.800.000"

4. **Notificaciones automáticas:**
   - Cuando faltan $300.000 o menos: "¡Casi lo logras! Te faltan $X para alcanzar tu meta"
   - Cuando se alcanza: "¡Meta alcanzada! 🎉"

5. **Usuario puede editar o eliminar metas:**
   - Editar: nombre, monto objetivo, fecha, descripción
   - Eliminar: se elimina la meta (las transacciones asociadas mantienen el historial pero ya no actualizan la meta)

## Notas Adicionales

- Los montos se almacenan en **centavos** (enteros) en el backend
- El frontend debe convertir entre pesos (decimales) y centavos (enteros)
- El `saved_amount` se actualiza automáticamente, no se puede editar manualmente
- Las notificaciones se envían automáticamente por el backend
- El cálculo de `progress_percentage`, `remaining_amount` e `is_completed` se hace automáticamente en el backend

## Testing

### Casos de prueba recomendados:

1. ✅ Crear una meta con todos los campos
2. ✅ Crear una meta sin descripción
3. ✅ Listar metas (con y sin metas)
4. ✅ Ver detalle de una meta
5. ✅ Actualizar una meta
6. ✅ Eliminar una meta
7. ✅ Crear transacción Saving asignada a meta
8. ✅ Verificar que el progreso se actualiza automáticamente
9. ✅ Verificar notificaciones cuando se acerca a la meta
10. ✅ Verificar notificaciones cuando se alcanza la meta
11. ✅ Intentar asignar goal a transacción no-Saving (debe fallar)
12. ✅ Verificar conversión de montos (pesos ↔ centavos)
