# HU-11: Metas de Ahorro - Resumen de Implementación Frontend

## 🎯 Resumen Rápido

El backend ya está listo. Solo necesitas consumir estos endpoints desde el frontend.

## 📡 Endpoints Principales

### 1. Listar Metas
```javascript
GET /api/goals/
Headers: { Authorization: "Bearer <token>" }
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Viaje a San Andres",
    "target_amount": 4000000,      // ⚠️ En CENTAVOS (divide por 100)
    "saved_amount": 1200000,        // ⚠️ En CENTAVOS (divide por 100)
    "date": "2024-12-31",
    "description": "Vacaciones",
    "progress_percentage": 30.0,    // ✅ Ya calculado
    "remaining_amount": 2800000,    // ✅ Ya calculado
    "is_completed": false           // ✅ Ya calculado
  }
]
```

### 2. Crear Meta
```javascript
POST /api/goals/
Headers: { 
  Authorization: "Bearer <token>",
  "Content-Type": "application/json"
}
Body: {
  "name": "Viaje a San Andres",
  "target_amount": 4000000,  // ⚠️ En CENTAVOS (multiplica por 100)
  "date": "2024-12-31",
  "description": "Vacaciones"  // opcional
}
```

### 3. Asignar Ahorro a Meta
```javascript
POST /api/transactions/
Headers: { 
  Authorization: "Bearer <token>",
  "Content-Type": "application/json"
}
Body: {
  "type": 4,              // ⚠️ OBLIGATORIO: 4 = Saving
  "origin_account": 1,
  "base_amount": 200000,  // ⚠️ En CENTAVOS
  "date": "2024-01-15",
  "goal": 1,              // ⚠️ ID de la meta
  "description": "Ahorro para viaje"
}
```

## ⚠️ IMPORTANTE: Conversión de Montos

El backend almacena montos en **CENTAVOS** (enteros). El frontend debe convertir:

```javascript
// Backend → Frontend (mostrar al usuario)
const mostrarEnPesos = (centavos) => {
  return (centavos / 100).toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0
  });
};

// Ejemplo: 4000000 centavos → "$4.000.000"
```

```javascript
// Frontend → Backend (enviar al servidor)
const enviarEnCentavos = (pesos) => {
  return Math.round(pesos * 100);
};

// Ejemplo: 4000000 pesos → 400000000 centavos
```

## 🎨 Componentes Necesarios

### 1. Lista de Metas con Barra de Progreso

```jsx
import React, { useState, useEffect } from 'react';

const GoalsList = () => {
  const [goals, setGoals] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    const response = await fetch('/api/goals/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setGoals(data);
  };

  const formatMoney = (centavos) => {
    return (centavos / 100).toLocaleString('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    });
  };

  return (
    <div className="goals-container">
      <h2>Mis Metas de Ahorro</h2>
      
      {goals.length === 0 ? (
        <p>No tienes metas creadas. ¡Crea una nueva!</p>
      ) : (
        goals.map(goal => (
          <div key={goal.id} className="goal-card">
            <h3>{goal.name}</h3>
            {goal.description && <p>{goal.description}</p>}
            
            {/* Barra de progreso */}
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${goal.progress_percentage}%` }}
              />
            </div>
            
            {/* Información */}
            <div className="progress-info">
              <span>
                {formatMoney(goal.saved_amount)} / {formatMoney(goal.target_amount)}
              </span>
              <span className="percentage">
                → {goal.progress_percentage.toFixed(1)}%
              </span>
            </div>
            
            {/* Estado */}
            {goal.is_completed ? (
              <p className="success">¡Meta alcanzada! 🎉</p>
            ) : (
              <p className="remaining">
                Faltan {formatMoney(goal.remaining_amount)}
              </p>
            )}
            
            <p className="date">
              Fecha objetivo: {new Date(goal.date).toLocaleDateString('es-CO')}
            </p>
            
            <div className="actions">
              <button onClick={() => editGoal(goal.id)}>Editar</button>
              <button onClick={() => deleteGoal(goal.id)}>Eliminar</button>
            </div>
          </div>
        ))
      )}
      
      <button onClick={() => showCreateForm()}>+ Crear Nueva Meta</button>
    </div>
  );
};

export default GoalsList;
```

### 2. Formulario para Crear Meta

```jsx
const CreateGoalForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    target_amount: '',
    date: '',
    description: ''
  });
  const token = localStorage.getItem('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Convertir pesos a centavos
    const payload = {
      name: formData.name,
      target_amount: Math.round(parseFloat(formData.target_amount) * 100),
      date: formData.date,
      description: formData.description || undefined
    };
    
    try {
      const response = await fetch('/api/goals/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        alert('Meta creada exitosamente');
        onSuccess(); // Recargar lista
        // Limpiar formulario
        setFormData({ name: '', target_amount: '', date: '', description: '' });
      } else {
        const error = await response.json();
        alert('Error: ' + JSON.stringify(error));
      }
    } catch (error) {
      alert('Error al crear meta: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="goal-form">
      <h3>Crear Nueva Meta</h3>
      
      <div>
        <label>Nombre de la meta *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
          maxLength={100}
          placeholder="Ej: Viaje a San Andres"
        />
      </div>
      
      <div>
        <label>Monto objetivo (en pesos) *</label>
        <input
          type="number"
          value={formData.target_amount}
          onChange={(e) => setFormData({...formData, target_amount: e.target.value})}
          required
          min="1"
          step="0.01"
          placeholder="4000000"
        />
        <small>El sistema convertirá automáticamente a centavos</small>
      </div>
      
      <div>
        <label>Fecha objetivo *</label>
        <input
          type="date"
          value={formData.date}
          onChange={(e) => setFormData({...formData, date: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Descripción (opcional)</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          rows={3}
          placeholder="Describe tu meta..."
        />
      </div>
      
      <button type="submit">Crear Meta</button>
      <button type="button" onClick={() => onSuccess()}>Cancelar</button>
    </form>
  );
};
```

### 3. Asignar Ahorro a Meta (al crear transacción)

```jsx
const CreateSavingTransaction = ({ goalId, onSuccess }) => {
  const [formData, setFormData] = useState({
    origin_account: '',
    base_amount: '',
    date: new Date().toISOString().split('T')[0],
    description: ''
  });
  const [accounts, setAccounts] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    // Cargar cuentas del usuario
    fetch('/api/accounts/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setAccounts(data));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      type: 4, // ⚠️ OBLIGATORIO: 4 = Saving
      origin_account: parseInt(formData.origin_account),
      base_amount: Math.round(parseFloat(formData.base_amount) * 100), // Convertir a centavos
      date: formData.date,
      goal: goalId, // ⚠️ ID de la meta
      description: formData.description || undefined
    };
    
    try {
      const response = await fetch('/api/transactions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        alert('Ahorro registrado y asignado a la meta exitosamente');
        // El backend automáticamente:
        // 1. Actualiza el saved_amount de la meta
        // 2. Envía notificación si se acerca o alcanza la meta
        onSuccess();
      } else {
        const error = await response.json();
        alert('Error: ' + JSON.stringify(error));
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Registrar Ahorro para Meta</h3>
      
      <div>
        <label>Cuenta *</label>
        <select
          value={formData.origin_account}
          onChange={(e) => setFormData({...formData, origin_account: e.target.value})}
          required
        >
          <option value="">Seleccionar cuenta</option>
          {accounts.map(acc => (
            <option key={acc.id} value={acc.id}>{acc.name}</option>
          ))}
        </select>
      </div>
      
      <div>
        <label>Monto a ahorrar (en pesos) *</label>
        <input
          type="number"
          value={formData.base_amount}
          onChange={(e) => setFormData({...formData, base_amount: e.target.value})}
          required
          min="0.01"
          step="0.01"
          placeholder="200000"
        />
      </div>
      
      <div>
        <label>Fecha *</label>
        <input
          type="date"
          value={formData.date}
          onChange={(e) => setFormData({...formData, date: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Descripción (opcional)</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          rows={2}
        />
      </div>
      
      <button type="submit">Registrar Ahorro</button>
    </form>
  );
};
```

### 4. Selector de Meta al Crear Ingreso

```jsx
const CreateIncomeWithGoal = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    origin_account: '',
    base_amount: '',
    date: new Date().toISOString().split('T')[0],
    category: '',
    assign_to_goal: false,
    goal_id: '',
    saving_amount: ''
  });
  const [goals, setGoals] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    // Cargar metas disponibles
    fetch('/api/goals/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setGoals(data));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 1. Crear el ingreso
    const incomePayload = {
      type: 1, // Income
      origin_account: parseInt(formData.origin_account),
      base_amount: Math.round(parseFloat(formData.base_amount) * 100),
      date: formData.date,
      category: parseInt(formData.category)
    };
    
    try {
      const incomeResponse = await fetch('/api/transactions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(incomePayload)
      });
      
      if (!incomeResponse.ok) {
        throw new Error('Error al crear ingreso');
      }
      
      // 2. Si el usuario quiere asignar parte a una meta, crear transacción Saving
      if (formData.assign_to_goal && formData.goal_id && formData.saving_amount) {
        const savingPayload = {
          type: 4, // Saving
          origin_account: parseInt(formData.origin_account),
          base_amount: Math.round(parseFloat(formData.saving_amount) * 100),
          date: formData.date,
          goal: parseInt(formData.goal_id),
          description: `Ahorro asignado desde ingreso`
        };
        
        const savingResponse = await fetch('/api/transactions/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(savingPayload)
        });
        
        if (!savingResponse.ok) {
          throw new Error('Error al asignar ahorro a meta');
        }
      }
      
      alert('Transacción registrada exitosamente');
      onSuccess();
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Registrar Ingreso</h3>
      
      {/* Campos normales del ingreso */}
      <div>
        <label>Cuenta *</label>
        <select
          value={formData.origin_account}
          onChange={(e) => setFormData({...formData, origin_account: e.target.value})}
          required
        >
          {/* Opciones de cuentas */}
        </select>
      </div>
      
      <div>
        <label>Monto (en pesos) *</label>
        <input
          type="number"
          value={formData.base_amount}
          onChange={(e) => setFormData({...formData, base_amount: e.target.value})}
          required
        />
      </div>
      
      {/* Selector de meta */}
      <div>
        <label>
          <input
            type="checkbox"
            checked={formData.assign_to_goal}
            onChange={(e) => setFormData({...formData, assign_to_goal: e.target.checked})}
          />
          Asignar parte a una meta
        </label>
      </div>
      
      {formData.assign_to_goal && (
        <>
          <div>
            <label>Seleccionar meta</label>
            <select
              value={formData.goal_id}
              onChange={(e) => setFormData({...formData, goal_id: e.target.value})}
            >
              <option value="">Seleccionar meta</option>
              {goals.map(goal => (
                <option key={goal.id} value={goal.id}>
                  {goal.name} ({goal.progress_percentage.toFixed(1)}% completado)
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label>Monto a asignar a la meta (en pesos)</label>
            <input
              type="number"
              value={formData.saving_amount}
              onChange={(e) => setFormData({...formData, saving_amount: e.target.value})}
              min="0.01"
              step="0.01"
              placeholder="200000"
            />
          </div>
        </>
      )}
      
      <button type="submit">Registrar</button>
    </form>
  );
};
```

## 📱 Flujo de Usuario Completo

### Escenario 1: Usuario crea meta y luego ahorra

1. **Usuario crea meta:**
   ```
   POST /api/goals/
   { name: "Viaje", target_amount: 4000000, date: "2024-12-31" }
   ```
   → Meta creada con `saved_amount = 0`

2. **Usuario registra ahorro:**
   ```
   POST /api/transactions/
   { type: 4, base_amount: 200000, goal: 1 }
   ```
   → Backend automáticamente:
   - Actualiza `saved_amount` de la meta (0 → 200000)
   - Calcula `progress_percentage` (0% → 5%)
   - Si falta poco, envía notificación

3. **Usuario ve progreso:**
   ```
   GET /api/goals/1/
   ```
   → Ve: "$200.000 / $4.000.000 → 5%"

### Escenario 2: Usuario recibe ingreso y asigna parte a meta

1. **Usuario registra ingreso:**
   ```
   POST /api/transactions/
   { type: 1, base_amount: 1000000, category: 5 }
   ```
   → Ingreso creado

2. **Usuario asigna parte a meta:**
   ```
   POST /api/transactions/
   { type: 4, base_amount: 300000, goal: 1 }
   ```
   → Backend actualiza la meta automáticamente

## 🎨 Estilos CSS Sugeridos

```css
.goals-container {
  padding: 20px;
}

.goal-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.progress-bar {
  width: 100%;
  height: 30px;
  background-color: #e0e0e0;
  border-radius: 15px;
  overflow: hidden;
  margin: 15px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  font-size: 18px;
}

.percentage {
  font-weight: bold;
  color: #4CAF50;
}

.remaining {
  color: #666;
  font-style: italic;
}

.success {
  color: #4CAF50;
  font-weight: bold;
  font-size: 18px;
}
```

## ✅ Checklist de Implementación

- [ ] Componente de lista de metas
- [ ] Formulario para crear meta
- [ ] Formulario para editar meta
- [ ] Botón para eliminar meta
- [ ] Barra de progreso visual
- [ ] Mostrar porcentaje y monto restante
- [ ] Formulario para registrar ahorro asignado a meta
- [ ] Selector de meta al crear ingreso
- [ ] Conversión correcta de montos (pesos ↔ centavos)
- [ ] Manejo de errores
- [ ] Mostrar notificaciones del backend
- [ ] Validaciones en frontend

## 🚨 Errores Comunes a Evitar

1. ❌ **No convertir montos:** Siempre multiplicar por 100 al enviar, dividir por 100 al mostrar
2. ❌ **Asignar goal a transacción no-Saving:** Solo type=4 puede tener goal
3. ❌ **Intentar editar saved_amount:** Este campo es solo lectura, se actualiza automáticamente
4. ❌ **Olvidar el token:** Todas las peticiones requieren Authorization header

## 📚 Documentación Completa

Para más detalles, ver: `docs/HU11_METAS_AHORRO_FRONTEND.md`

