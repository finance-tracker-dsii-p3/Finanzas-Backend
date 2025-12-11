# HU-12 — Reglas Automáticas - Guía Frontend

## Endpoints Disponibles

### 1. Listar Reglas
```
GET /api/rules/
```

**Query Parameters:**
- `active_only=true` - Solo reglas activas
- `criteria_type=description_contains` - Filtrar por tipo de criterio
- `action_type=assign_category` - Filtrar por tipo de acción
- `search=texto` - Buscar en nombre y palabra clave

**Respuesta:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Uber automático",
      "criteria_type": "description_contains",
      "criteria_type_display": "Descripción contiene texto",
      "keyword": "uber",
      "action_type": "assign_category",
      "action_type_display": "Asignar categoría",
      "target_category": 5,
      "target_category_name": "Transporte",
      "target_category_color": "#FF5733",
      "target_category_icon": "car",
      "target_tag": null,
      "is_active": true,
      "order": 1,
      "applied_count": 15,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 2. Crear Regla
```
POST /api/rules/
```

**Body:**
```json
{
  "name": "Uber automático",
  "criteria_type": "description_contains",
  "keyword": "uber",
  "action_type": "assign_category",
  "target_category": 5,
  "is_active": true,
  "order": 1
}
```

**Respuesta:**
```json
{
  "id": 1,
  "name": "Uber automático",
  "criteria_type": "description_contains",
  "criteria_type_display": "Descripción contiene texto",
  "keyword": "uber",
  "action_type": "assign_category",
  "action_type_display": "Asignar categoría",
  "target_category": 5,
  "target_category_info": {
    "id": 5,
    "name": "Transporte",
    "type": "expense",
    "type_display": "Gasto",
    "color": "#FF5733",
    "icon": "car"
  },
  "target_tag": null,
  "is_active": true,
  "order": 1,
  "statistics": {
    "total_applied": 0,
    "last_applied": null,
    "avg_amount": null
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Actualizar Regla
```
PUT /api/rules/{id}/
PATCH /api/rules/{id}/
```

### 4. Eliminar Regla
```
DELETE /api/rules/{id}/
```

### 5. Activar/Desactivar Regla
```
POST /api/rules/{id}/toggle_active/
```

**Respuesta:**
```json
{
  "message": "Regla \"Uber automático\" activada exitosamente.",
  "rule": { ... }
}
```

### 6. Reordenar Reglas
```
POST /api/rules/reorder/
```

**Body:**
```json
{
  "rule_orders": [
    {"id": 1, "order": 1},
    {"id": 2, "order": 2},
    {"id": 3, "order": 3}
  ]
}
```

### 7. Previsualizar Regla
```
POST /api/rules/preview/
```

**Body:**
```json
{
  "description": "Pago Uber",
  "transaction_type": 2
}
```

**Respuesta:**
```json
{
  "would_match": true,
  "matching_rule": {
    "id": 1,
    "name": "Uber automático",
    "action_type": "assign_category",
    "changes": {
      "category": "Transporte"
    }
  },
  "message": "La regla 'Uber automático' se aplicaría a esta transacción."
}
```

### 8. Estadísticas
```
GET /api/rules/stats/
```

**Respuesta:**
```json
{
  "total_rules": 5,
  "active_rules": 3,
  "inactive_rules": 2,
  "total_applications": 150,
  "most_used_rule": {
    "id": 1,
    "name": "Uber automático",
    "applications": 45
  },
  "recent_applications": [...]
}
```

### 9. Ver Transacciones Afectadas
```
GET /api/rules/{id}/applied_transactions/
```

## Implementación en React/TypeScript

### 1. Servicio de Reglas

```typescript
// services/ruleService.ts

interface Rule {
  id: number;
  name: string;
  criteria_type: 'description_contains' | 'transaction_type';
  criteria_type_display: string;
  keyword?: string;
  target_transaction_type?: number;
  action_type: 'assign_category' | 'assign_tag';
  action_type_display: string;
  target_category?: number;
  target_category_name?: string;
  target_category_color?: string;
  target_category_icon?: string;
  target_tag?: string;
  is_active: boolean;
  order: number;
  applied_count: number;
  created_at: string;
  updated_at: string;
}

interface RuleCreate {
  name: string;
  criteria_type: 'description_contains' | 'transaction_type';
  keyword?: string;
  target_transaction_type?: number;
  action_type: 'assign_category' | 'assign_tag';
  target_category?: number;
  target_tag?: string;
  is_active?: boolean;
  order?: number;
}

interface RulePreview {
  description?: string;
  transaction_type?: number;
}

export const ruleService = {
  async getRules(filters?: {
    active_only?: boolean;
    criteria_type?: string;
    action_type?: string;
    search?: string;
  }): Promise<{ count: number; results: Rule[] }> {
    const params = new URLSearchParams();

    if (filters?.active_only) params.append('active_only', 'true');
    if (filters?.criteria_type) params.append('criteria_type', filters.criteria_type);
    if (filters?.action_type) params.append('action_type', filters.action_type);
    if (filters?.search) params.append('search', filters.search);

    const response = await fetch(`/api/rules/?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Error al obtener reglas');
    }

    return response.json();
  },

  async createRule(rule: RuleCreate): Promise<Rule> {
    const response = await fetch('/api/rules/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify(rule),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al crear regla');
    }

    return response.json();
  },

  async updateRule(id: number, rule: Partial<RuleCreate>): Promise<Rule> {
    const response = await fetch(`/api/rules/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify(rule),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al actualizar regla');
    }

    return response.json();
  },

  async deleteRule(id: number): Promise<void> {
    const response = await fetch(`/api/rules/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Error al eliminar regla');
    }
  },

  async toggleActive(id: number): Promise<Rule> {
    const response = await fetch(`/api/rules/${id}/toggle_active/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Error al cambiar estado de la regla');
    }

    const data = await response.json();
    return data.rule;
  },

  async reorderRules(ruleOrders: { id: number; order: number }[]): Promise<Rule[]> {
    const response = await fetch('/api/rules/reorder/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ rule_orders: ruleOrders }),
    });

    if (!response.ok) {
      throw new Error('Error al reordenar reglas');
    }

    const data = await response.json();
    return data.rules;
  },

  async previewRule(preview: RulePreview): Promise<any> {
    const response = await fetch('/api/rules/preview/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify(preview),
    });

    if (!response.ok) {
      throw new Error('Error al previsualizar regla');
    }

    return response.json();
  },

  async getStats(): Promise<any> {
    const response = await fetch('/api/rules/stats/', {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Error al obtener estadísticas');
    }

    return response.json();
  },
};
```

### 2. Componente de Lista de Reglas

```typescript
// components/RuleList.tsx

import React, { useState, useEffect } from 'react';
import { ruleService } from '../services/ruleService';
import { Rule } from '../types';

export const RuleList: React.FC = () => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    active_only: false,
    search: '',
  });

  useEffect(() => {
    loadRules();
  }, [filters]);

  const loadRules = async () => {
    setLoading(true);
    try {
      const response = await ruleService.getRules(filters);
      setRules(response.results);
    } catch (error) {
      console.error('Error al cargar reglas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (id: number) => {
    try {
      const updatedRule = await ruleService.toggleActive(id);
      setRules(rules.map(r => r.id === id ? updatedRule : r));
    } catch (error) {
      console.error('Error al cambiar estado:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('¿Eliminar esta regla?')) return;

    try {
      await ruleService.deleteRule(id);
      setRules(rules.filter(r => r.id !== id));
    } catch (error) {
      console.error('Error al eliminar:', error);
    }
  };

  return (
    <div className="rule-list">
      <div className="filters">
        <input
          type="text"
          placeholder="Buscar reglas..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <label>
          <input
            type="checkbox"
            checked={filters.active_only}
            onChange={(e) => setFilters({ ...filters, active_only: e.target.checked })}
          />
          Solo activas
        </label>
      </div>

      {loading ? (
        <p>Cargando...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Criterio</th>
              <th>Acción</th>
              <th>Aplicada</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {rules.map(rule => (
              <tr key={rule.id}>
                <td>{rule.name}</td>
                <td>
                  {rule.criteria_type_display}
                  {rule.keyword && `: "${rule.keyword}"`}
                  {rule.target_transaction_type && `: Tipo ${rule.target_transaction_type}`}
                </td>
                <td>
                  {rule.action_type_display}
                  {rule.target_category_name && ` → ${rule.target_category_name}`}
                  {rule.target_tag && ` → "${rule.target_tag}"`}
                </td>
                <td>{rule.applied_count} veces</td>
                <td>
                  <span className={rule.is_active ? 'active' : 'inactive'}>
                    {rule.is_active ? 'Activa' : 'Inactiva'}
                  </span>
                </td>
                <td>
                  <button onClick={() => handleToggleActive(rule.id)}>
                    {rule.is_active ? 'Desactivar' : 'Activar'}
                  </button>
                  <button onClick={() => handleEdit(rule.id)}>Editar</button>
                  <button onClick={() => handleDelete(rule.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {rules.length === 0 && !loading && (
        <p>No hay reglas configuradas. ¡Crea una para automatizar la categorización!</p>
      )}
    </div>
  );
};
```

### 3. Componente de Crear/Editar Regla

```typescript
// components/RuleForm.tsx

import React, { useState, useEffect } from 'react';
import { ruleService } from '../services/ruleService';
import { categoryService } from '../services/categoryService';

interface RuleFormProps {
  ruleId?: number;
  onSave: () => void;
  onCancel: () => void;
}

export const RuleForm: React.FC<RuleFormProps> = ({ ruleId, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    criteria_type: 'description_contains' as 'description_contains' | 'transaction_type',
    keyword: '',
    target_transaction_type: undefined as number | undefined,
    action_type: 'assign_category' as 'assign_category' | 'assign_tag',
    target_category: undefined as number | undefined,
    target_tag: '',
    is_active: true,
    order: 1,
  });

  const [categories, setCategories] = useState<any[]>([]);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCategories();
    if (ruleId) {
      loadRule();
    }
  }, [ruleId]);

  const loadCategories = async () => {
    try {
      const response = await categoryService.getCategories();
      setCategories(response.results);
    } catch (error) {
      console.error('Error al cargar categorías:', error);
    }
  };

  const loadRule = async () => {
    try {
      const rule = await ruleService.getRule(ruleId!);
      setFormData({
        name: rule.name,
        criteria_type: rule.criteria_type,
        keyword: rule.keyword || '',
        target_transaction_type: rule.target_transaction_type,
        action_type: rule.action_type,
        target_category: rule.target_category,
        target_tag: rule.target_tag || '',
        is_active: rule.is_active,
        order: rule.order,
      });
    } catch (error) {
      console.error('Error al cargar regla:', error);
    }
  };

  const handlePreview = async () => {
    if (formData.criteria_type === 'description_contains' && !formData.keyword) {
      alert('Ingresa una palabra clave para previsualizar');
      return;
    }

    try {
      const previewData: any = {};
      if (formData.criteria_type === 'description_contains') {
        previewData.description = formData.keyword;
      } else {
        previewData.transaction_type = formData.target_transaction_type;
      }

      const result = await ruleService.previewRule(previewData);
      setPreview(result);
    } catch (error) {
      console.error('Error al previsualizar:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (ruleId) {
        await ruleService.updateRule(ruleId, formData);
      } else {
        await ruleService.createRule(formData);
      }
      onSave();
    } catch (error) {
      console.error('Error al guardar regla:', error);
      alert('Error al guardar la regla');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rule-form">
      <h2>{ruleId ? 'Editar Regla' : 'Crear Regla Automática'}</h2>

      <div className="form-group">
        <label>Nombre de la regla *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          placeholder="Ej: Uber automático"
        />
      </div>

      <div className="form-group">
        <label>Tipo de criterio *</label>
        <select
          value={formData.criteria_type}
          onChange={(e) => setFormData({
            ...formData,
            criteria_type: e.target.value as any
          })}
        >
          <option value="description_contains">Descripción contiene texto</option>
          <option value="transaction_type">Tipo de transacción</option>
        </select>
      </div>

      {formData.criteria_type === 'description_contains' && (
        <div className="form-group">
          <label>Palabra clave *</label>
          <input
            type="text"
            value={formData.keyword}
            onChange={(e) => setFormData({ ...formData, keyword: e.target.value })}
            required
            placeholder="Ej: uber"
          />
          <small>La regla se aplicará si la descripción contiene este texto (insensible a mayúsculas)</small>
        </div>
      )}

      {formData.criteria_type === 'transaction_type' && (
        <div className="form-group">
          <label>Tipo de transacción *</label>
          <select
            value={formData.target_transaction_type || ''}
            onChange={(e) => setFormData({
              ...formData,
              target_transaction_type: parseInt(e.target.value)
            })}
            required
          >
            <option value="">Selecciona...</option>
            <option value="1">Ingresos</option>
            <option value="2">Gastos</option>
            <option value="3">Transferencias</option>
            <option value="4">Ahorros</option>
          </select>
        </div>
      )}

      <div className="form-group">
        <label>Tipo de acción *</label>
        <select
          value={formData.action_type}
          onChange={(e) => setFormData({
            ...formData,
            action_type: e.target.value as any
          })}
        >
          <option value="assign_category">Asignar categoría</option>
          <option value="assign_tag">Asignar etiqueta</option>
        </select>
      </div>

      {formData.action_type === 'assign_category' && (
        <div className="form-group">
          <label>Categoría objetivo *</label>
          <select
            value={formData.target_category || ''}
            onChange={(e) => setFormData({
              ...formData,
              target_category: parseInt(e.target.value)
            })}
            required
          >
            <option value="">Selecciona una categoría...</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>
      )}

      {formData.action_type === 'assign_tag' && (
        <div className="form-group">
          <label>Etiqueta objetivo *</label>
          <input
            type="text"
            value={formData.target_tag}
            onChange={(e) => setFormData({ ...formData, target_tag: e.target.value })}
            required
            placeholder="Ej: transporte"
          />
        </div>
      )}

      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={formData.is_active}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          />
          Regla activa
        </label>
      </div>

      <div className="form-actions">
        <button type="button" onClick={handlePreview}>Previsualizar</button>
        <button type="button" onClick={onCancel}>Cancelar</button>
        <button type="submit" disabled={loading}>
          {loading ? 'Guardando...' : ruleId ? 'Actualizar' : 'Crear'}
        </button>
      </div>

      {preview && (
        <div className="preview-result">
          <h3>Previsualización</h3>
          {preview.would_match ? (
            <div className="preview-match">
              <p>✅ La regla se aplicaría:</p>
              <p><strong>{preview.matching_rule.name}</strong></p>
              <p>{preview.message}</p>
              {preview.matching_rule.changes && (
                <ul>
                  {Object.entries(preview.matching_rule.changes).map(([key, value]) => (
                    <li key={key}>{key}: {value}</li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <div className="preview-no-match">
              <p>❌ Ninguna regla coincidiría con esta transacción.</p>
            </div>
          )}
        </div>
      )}
    </form>
  );
};
```

### 4. Mostrar Regla Aplicada en Transacción

```typescript
// components/TransactionDetail.tsx

interface Transaction {
  id: number;
  description: string;
  category_name?: string;
  tag?: string;
  applied_rule?: number;
  applied_rule_name?: string;
  // ... otros campos
}

export const TransactionDetail: React.FC<{ transaction: Transaction }> = ({ transaction }) => {
  return (
    <div className="transaction-detail">
      <h3>Detalle de Transacción</h3>

      <div className="transaction-info">
        <p><strong>Descripción:</strong> {transaction.description}</p>

        {transaction.applied_rule_name && (
          <div className="applied-rule">
            <p><strong>Regla aplicada:</strong> {transaction.applied_rule_name}</p>
            {transaction.category_name && (
              <p className="rule-result">
                ✅ Categoría asignada automáticamente: <strong>{transaction.category_name}</strong>
              </p>
            )}
            {transaction.tag && (
              <p className="rule-result">
                ✅ Etiqueta asignada automáticamente: <strong>{transaction.tag}</strong>
              </p>
            )}
          </div>
        )}

        {!transaction.applied_rule_name && transaction.category_name && (
          <p><strong>Categoría:</strong> {transaction.category_name} (asignada manualmente)</p>
        )}
      </div>
    </div>
  );
};
```

### 5. Reordenar Reglas (Drag & Drop)

```typescript
// components/RuleReorder.tsx

import React, { useState } from 'react';
import { ruleService } from '../services/ruleService';
import { Rule } from '../types';

export const RuleReorder: React.FC<{ rules: Rule[]; onReorder: () => void }> = ({
  rules,
  onReorder
}) => {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();

    if (draggedIndex === null) return;

    const newRules = [...rules];
    const [removed] = newRules.splice(draggedIndex, 1);
    newRules.splice(dropIndex, 0, removed);

    const ruleOrders = newRules.map((rule, index) => ({
      id: rule.id,
      order: index + 1,
    }));

    try {
      await ruleService.reorderRules(ruleOrders);
      onReorder();
    } catch (error) {
      console.error('Error al reordenar:', error);
    }

    setDraggedIndex(null);
  };

  return (
    <div className="rule-reorder">
      <h3>Reordenar Reglas (arrastra para cambiar prioridad)</h3>
      <ul>
        {rules.map((rule, index) => (
          <li
            key={rule.id}
            draggable
            onDragStart={() => handleDragStart(index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDrop={(e) => handleDrop(e, index)}
            className={draggedIndex === index ? 'dragging' : ''}
          >
            <span>{index + 1}.</span>
            <span>{rule.name}</span>
            <span className="priority">Prioridad: {rule.order}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
```

## Flujo de Usuario

### 1. Crear Regla

1. Usuario hace clic en "Crear Regla"
2. Completa el formulario:
   - Nombre: "Uber automático"
   - Criterio: "Descripción contiene texto"
   - Palabra clave: "uber"
   - Acción: "Asignar categoría"
   - Categoría: "Transporte"
3. Opcional: Hace clic en "Previsualizar" para ver si funcionaría
4. Guarda la regla
5. La regla aparece en la lista

### 2. Aplicación Automática

1. Usuario crea una transacción con descripción "Pago Uber"
2. Al guardar, el backend aplica automáticamente la regla
3. La transacción queda con:
   - `category`: "Transporte"
   - `applied_rule`: ID de la regla
   - `applied_rule_name`: "Uber automático"
4. En el detalle de la transacción se muestra:
   - "Regla aplicada: Uber automático"
   - "✅ Categoría asignada automáticamente: Transporte"

### 3. Activar/Desactivar

1. Usuario ve lista de reglas
2. Hace clic en "Desactivar" en una regla
3. La regla se marca como inactiva
4. Las nuevas transacciones no aplicarán esta regla
5. Las transacciones ya procesadas mantienen su categoría

## Consideraciones Importantes

### 1. Orden de Aplicación
- Las reglas se aplican en orden de prioridad (`order`)
- Solo se aplica la primera regla que coincide
- Si varias reglas coinciden, gana la de menor `order`

### 2. Previsualización
- Usar antes de crear/editar reglas
- Ayuda a verificar que la regla funcionará
- Muestra qué cambios se aplicarían

### 3. Indicadores Visuales
- Mostrar claramente cuando una categoría/etiqueta fue asignada por regla
- Distinguir entre asignación manual y automática
- Mostrar nombre de la regla aplicada

### 4. Manejo de Errores
- Validar que la categoría pertenezca al usuario
- Validar campos requeridos según criterio/acción
- Mostrar mensajes claros de error

### 5. UX/UI
- Mostrar contador de aplicaciones por regla
- Permitir reordenar fácilmente (drag & drop)
- Mostrar estado activo/inactivo claramente
- Filtrar por estado y tipo

## Ejemplo Completo de Uso

```typescript
// Página principal de reglas
const RulesPage = () => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingRule, setEditingRule] = useState<number | null>(null);

  const loadRules = async () => {
    const response = await ruleService.getRules({ active_only: false });
    setRules(response.results);
  };

  useEffect(() => {
    loadRules();
  }, []);

  return (
    <div>
      <h1>Reglas Automáticas</h1>

      <button onClick={() => setShowForm(true)}>Crear Nueva Regla</button>

      {showForm && (
        <RuleForm
          ruleId={editingRule || undefined}
          onSave={() => {
            setShowForm(false);
            setEditingRule(null);
            loadRules();
          }}
          onCancel={() => {
            setShowForm(false);
            setEditingRule(null);
          }}
        />
      )}

      <RuleList
        rules={rules}
        onEdit={(id) => {
          setEditingRule(id);
          setShowForm(true);
        }}
        onDelete={loadRules}
        onToggle={loadRules}
      />

      <RuleReorder rules={rules} onReorder={loadRules} />
    </div>
  );
};
```

## Checklist de Implementación

- [ ] Servicio de reglas (CRUD completo)
- [ ] Lista de reglas con filtros
- [ ] Formulario de crear/editar regla
- [ ] Previsualización de reglas
- [ ] Activar/desactivar reglas
- [ ] Reordenar reglas (drag & drop)
- [ ] Mostrar regla aplicada en detalle de transacción
- [ ] Indicadores visuales de asignación automática
- [ ] Estadísticas de reglas
- [ ] Manejo de errores y validaciones
