# HU-10 — Búsqueda y Filtros - Guía Frontend

## Endpoints Disponibles

### 1. Listar con Filtros
```
GET /api/transactions/
```

**Query Parameters:**
- `search` - Búsqueda de texto (tag, description, note, category name)
- `category` - ID de categoría
- `origin_account` - ID de cuenta origen
- `destination_account` - ID de cuenta destino
- `type` - Tipo (1=Income, 2=Expense, 3=Transfer, 4=Saving)
- `start_date` - Fecha desde (YYYY-MM-DD)
- `end_date` - Fecha hasta (YYYY-MM-DD)
- `ordering` - Ordenar por campos (ej: `date`, `-total_amount`)

**Respuesta:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "type": 2,
      "total_amount": 500000000,
      "date": "2024-11-30",
      "tag": "uber",
      "description": "Viaje en Uber",
      "note": "Casa a oficina",
      "category": 5,
      "category_name": "Transporte",
      ...
    }
  ]
}
```

### 2. Eliminación Múltiple
```
POST /api/transactions/bulk_delete/
```

**Body:**
```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**Respuesta exitosa:**
```json
{
  "message": "Se eliminaron 5 transacciones exitosamente.",
  "deleted_count": 5
}
```

**Respuesta con errores:**
```json
{
  "message": "Se eliminaron 3 transacciones, pero hubo 2 errores.",
  "deleted_count": 3,
  "errors": [
    {"transaction_id": 4, "error": "..."},
    {"transaction_id": 5, "error": "..."}
  ]
}
```

## Implementación en React/TypeScript

### 1. Servicio de Transacciones

```typescript
// services/transactionService.ts

interface TransactionFilters {
  search?: string;
  category?: number;
  origin_account?: number;
  destination_account?: number;
  type?: number;
  start_date?: string;
  end_date?: string;
  ordering?: string;
}

interface TransactionListResponse {
  count: number;
  results: Transaction[];
}

export const transactionService = {
  // Listar con filtros
  async getTransactions(filters: TransactionFilters = {}): Promise<TransactionListResponse> {
    const params = new URLSearchParams();
    
    if (filters.search) params.append('search', filters.search);
    if (filters.category) params.append('category', filters.category.toString());
    if (filters.origin_account) params.append('origin_account', filters.origin_account.toString());
    if (filters.destination_account) params.append('destination_account', filters.destination_account.toString());
    if (filters.type) params.append('type', filters.type.toString());
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const response = await fetch(`/api/transactions/?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Error al obtener transacciones');
    }
    
    return response.json();
  },

  // Eliminación múltiple
  async bulkDelete(ids: number[]): Promise<{ message: string; deleted_count: number; errors?: any[] }> {
    const response = await fetch('/api/transactions/bulk_delete/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ ids }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al eliminar transacciones');
    }
    
    return response.json();
  },
};
```

### 2. Componente de Filtros

```typescript
// components/TransactionFilters.tsx

import React, { useState } from 'react';

interface TransactionFiltersProps {
  onFilterChange: (filters: TransactionFilters) => void;
  categories: Category[];
  accounts: Account[];
}

export const TransactionFilters: React.FC<TransactionFiltersProps> = ({
  onFilterChange,
  categories,
  accounts,
}) => {
  const [filters, setFilters] = useState<TransactionFilters>({
    search: '',
    category: undefined,
    origin_account: undefined,
    type: undefined,
    start_date: '',
    end_date: '',
  });

  const handleChange = (key: keyof TransactionFilters, value: any) => {
    const newFilters = { ...filters, [key]: value || undefined };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters: TransactionFilters = {
      search: '',
      category: undefined,
      origin_account: undefined,
      type: undefined,
      start_date: '',
      end_date: '',
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  return (
    <div className="transaction-filters">
      {/* Búsqueda de texto */}
      <input
        type="text"
        placeholder="Buscar (tag, descripción, nota, categoría)..."
        value={filters.search || ''}
        onChange={(e) => handleChange('search', e.target.value)}
        className="filter-input"
      />

      {/* Filtro por categoría */}
      <select
        value={filters.category || ''}
        onChange={(e) => handleChange('category', e.target.value ? parseInt(e.target.value) : undefined)}
      >
        <option value="">Todas las categorías</option>
        {categories.map(cat => (
          <option key={cat.id} value={cat.id}>{cat.name}</option>
        ))}
      </select>

      {/* Filtro por cuenta */}
      <select
        value={filters.origin_account || ''}
        onChange={(e) => handleChange('origin_account', e.target.value ? parseInt(e.target.value) : undefined)}
      >
        <option value="">Todas las cuentas</option>
        {accounts.map(acc => (
          <option key={acc.id} value={acc.id}>{acc.name}</option>
        ))}
      </select>

      {/* Filtro por tipo */}
      <select
        value={filters.type || ''}
        onChange={(e) => handleChange('type', e.target.value ? parseInt(e.target.value) : undefined)}
      >
        <option value="">Todos los tipos</option>
        <option value="1">Ingresos</option>
        <option value="2">Gastos</option>
        <option value="3">Transferencias</option>
        <option value="4">Ahorros</option>
      </select>

      {/* Filtro por fecha desde */}
      <input
        type="date"
        value={filters.start_date || ''}
        onChange={(e) => handleChange('start_date', e.target.value)}
      />

      {/* Filtro por fecha hasta */}
      <input
        type="date"
        value={filters.end_date || ''}
        onChange={(e) => handleChange('end_date', e.target.value)}
      />

      {/* Botón limpiar filtros */}
      <button onClick={clearFilters}>Limpiar filtros</button>
    </div>
  );
};
```

### 3. Componente de Lista con Selección Múltiple

```typescript
// components/TransactionList.tsx

import React, { useState, useEffect } from 'react';
import { transactionService } from '../services/transactionService';
import { TransactionFilters } from './TransactionFilters';

export const TransactionList: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(0);

  useEffect(() => {
    loadTransactions();
  }, [filters]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const response = await transactionService.getTransactions(filters);
      setTransactions(response.results);
      setCount(response.count);
      setSelectedIds([]); // Limpiar selección al cambiar filtros
    } catch (error) {
      console.error('Error al cargar transacciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(transactions.map(t => t.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectTransaction = (id: number, checked: boolean) => {
    if (checked) {
      setSelectedIds([...selectedIds, id]);
    } else {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      alert('Selecciona al menos una transacción');
      return;
    }

    if (!confirm(`¿Eliminar ${selectedIds.length} transacción(es)?`)) {
      return;
    }

    try {
      const result = await transactionService.bulkDelete(selectedIds);
      
      if (result.errors && result.errors.length > 0) {
        alert(`Se eliminaron ${result.deleted_count} transacciones, pero hubo ${result.errors.length} errores.`);
      } else {
        alert(`Se eliminaron ${result.deleted_count} transacciones exitosamente.`);
      }
      
      setSelectedIds([]);
      loadTransactions(); // Recargar lista
    } catch (error) {
      console.error('Error al eliminar transacciones:', error);
      alert('Error al eliminar transacciones');
    }
  };

  return (
    <div className="transaction-list">
      <TransactionFilters onFilterChange={setFilters} />
      
      {/* Contador y acciones */}
      <div className="list-header">
        <div>
          {count === 0 ? (
            <p>No hay transacciones que coincidan con los filtros.</p>
          ) : (
            <p>{count} transacción(es) encontrada(s)</p>
          )}
        </div>
        
        {selectedIds.length > 0 && (
          <div className="bulk-actions">
            <span>{selectedIds.length} seleccionada(s)</span>
            <button onClick={handleBulkDelete} className="btn-danger">
              Eliminar seleccionadas
            </button>
          </div>
        )}
      </div>

      {/* Tabla de transacciones */}
      {loading ? (
        <p>Cargando...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  checked={selectedIds.length === transactions.length && transactions.length > 0}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                />
              </th>
              <th>Fecha</th>
              <th>Descripción</th>
              <th>Categoría</th>
              <th>Monto</th>
              <th>Tipo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map(transaction => (
              <tr key={transaction.id}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(transaction.id)}
                    onChange={(e) => handleSelectTransaction(transaction.id, e.target.checked)}
                  />
                </td>
                <td>{transaction.date}</td>
                <td>{transaction.description || transaction.tag || '-'}</td>
                <td>{transaction.category_name || '-'}</td>
                <td>{formatMoney(transaction.total_amount / 100, transaction.origin_account_currency)}</td>
                <td>{getTypeDisplay(transaction.type)}</td>
                <td>
                  <button onClick={() => handleEdit(transaction.id)}>Editar</button>
                  <button onClick={() => handleDelete(transaction.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
```

### 4. Hook Personalizado para Filtros

```typescript
// hooks/useTransactionFilters.ts

import { useState, useCallback, useEffect } from 'react';
import { transactionService } from '../services/transactionService';

export const useTransactionFilters = () => {
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const loadTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await transactionService.getTransactions(filters);
      setTransactions(response.results);
      setCount(response.count);
    } catch (err) {
      setError('Error al cargar transacciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  const updateFilters = useCallback((newFilters: Partial<TransactionFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  return {
    filters,
    transactions,
    loading,
    count,
    error,
    updateFilters,
    clearFilters,
    reload: loadTransactions,
  };
};
```

### 5. Búsqueda con Debounce

```typescript
// hooks/useDebounce.ts

import { useState, useEffect } from 'react';

export const useDebounce = <T,>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Uso en componente
const [searchText, setSearchText] = useState('');
const debouncedSearch = useDebounce(searchText, 500);

useEffect(() => {
  updateFilters({ search: debouncedSearch });
}, [debouncedSearch]);
```

## Flujo de Usuario

### 1. Filtrar → Seleccionar → Eliminar

```typescript
// Ejemplo completo del flujo

const TransactionPage = () => {
  const { filters, transactions, count, updateFilters, reload } = useTransactionFilters();
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  // 1. Usuario aplica filtros
  const handleFilterChange = (newFilters: TransactionFilters) => {
    updateFilters(newFilters);
    setSelectedIds([]); // Limpiar selección
  };

  // 2. Usuario selecciona transacciones
  const handleSelect = (id: number) => {
    setSelectedIds(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id)
        : [...prev, id]
    );
  };

  // 3. Usuario elimina seleccionadas
  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;
    
    try {
      await transactionService.bulkDelete(selectedIds);
      setSelectedIds([]);
      reload(); // Recargar lista filtrada
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <TransactionFilters onFilterChange={handleFilterChange} />
      
      {count === 0 ? (
        <p>No hay transacciones que coincidan con los filtros.</p>
      ) : (
        <>
          <p>{count} transacción(es) encontrada(s)</p>
          {selectedIds.length > 0 && (
            <button onClick={handleBulkDelete}>
              Eliminar {selectedIds.length} seleccionada(s)
            </button>
          )}
          <TransactionTable 
            transactions={transactions}
            selectedIds={selectedIds}
            onSelect={handleSelect}
          />
        </>
      )}
    </div>
  );
};
```

## Consideraciones Importantes

### 1. Búsqueda de Texto
- El backend busca en: `tag`, `description`, `note`, `category.name`
- Usa debounce para no hacer requests en cada tecla
- Muestra mensaje cuando no hay resultados

### 2. Filtros Combinados
- Todos los filtros se pueden combinar
- La lista se actualiza automáticamente al cambiar cualquier filtro
- Guardar filtros en URL (opcional) para compartir/enlaces

### 3. Eliminación Múltiple
- Validar que haya selección antes de permitir eliminar
- Mostrar confirmación antes de eliminar
- Manejar errores parciales (algunas se eliminan, otras no)
- Recargar lista después de eliminar

### 4. UX/UI
- Mostrar loading mientras carga
- Mostrar mensaje cuando `count === 0`
- Checkbox "Seleccionar todo" que respete los filtros actuales
- Contador de seleccionadas visible
- Botón de eliminar solo visible cuando hay selección

## Ejemplo de URL con Filtros

```
/api/transactions/?search=uber&category=5&start_date=2024-01-01&end_date=2024-12-31&type=2&ordering=-date
```

Esto busca "uber" en texto, filtra por categoría 5, rango de fechas, tipo 2 (gastos) y ordena por fecha descendente.

