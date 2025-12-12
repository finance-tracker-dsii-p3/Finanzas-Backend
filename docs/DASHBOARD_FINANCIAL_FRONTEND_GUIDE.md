# Dashboard Financiero - Guía de Integración Frontend

## 📚 Índice

- [Introducción](#introducción)
- [Estructura de Datos](#estructura-de-datos)
- [Ejemplos React/TypeScript](#ejemplos-reacttypescript)
- [Ejemplos Vue.js](#ejemplos-vuejs)
- [Componentes UI](#componentes-ui)
- [Manejo de Estados](#manejo-de-estados)
- [Filtros y Navegación](#filtros-y-navegación)
- [Gráficos](#gráficos)
- [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Introducción

El dashboard financiero es la vista principal de la aplicación que muestra:

✅ **Totales financieros**: Ingresos, Gastos, Ahorros, IVA, GMF  
✅ **Filtros dinámicos**: Por mes, año y cuenta  
✅ **Movimientos recientes**: Últimas 5 transacciones  
✅ **Gráficos**: Distribución de gastos y flujo diario  
✅ **Estados vacíos**: Mensajes cuando no hay datos

**Endpoint:** `GET /api/dashboard/financial/`

---

## 📊 Estructura de Datos

### TypeScript Interfaces

```typescript
// ========== Interfaces de Respuesta ==========

interface FinancialSummary {
  total_income: number;          // Centavos
  total_expenses: number;        // Centavos
  total_savings: number;         // Centavos
  total_iva: number;             // Centavos
  total_gmf: number;             // Centavos
  net_balance: number;           // Centavos
  currency: 'COP' | 'USD' | 'EUR';
}

interface DashboardFilters {
  year: number | null;
  month: number | null;           // 1-12
  account_id: number | null;
  period_label: string;           // "Diciembre 2025"
}

interface RecentTransaction {
  id: number;
  type: string;                   // "Income", "Expense", etc.
  type_code: number;              // 1, 2, 3, 4
  date: string;                   // ISO format
  description: string;
  amount: number;                 // Centavos
  amount_formatted: string;       // "$3.504"
  currency: string;
  account: string;
  category: string | null;
  category_color: string | null;
  category_icon: string | null;
}

interface UpcomingBill {
  id: number;
  provider: string;
  amount: number;                 // Centavos
  amount_formatted: string;       // "$44.900"
  due_date: string;               // ISO format
  days_until_due: number;         // Negativo si está vencida
  status: 'pending' | 'paid' | 'overdue';
  urgency: 'overdue' | 'today' | 'urgent' | 'soon' | 'normal';
  urgency_label: string;          // "Vencida", "Hoy", "Urgente", etc.
  urgency_color: string;          // Color hex (#EF4444, etc.)
  suggested_account: string | null;
  suggested_account_id: number | null;
  category: string | null;
  category_color: string | null;
  category_icon: string | null;
  description: string;
  is_recurring: boolean;
}

interface CategoryDistribution {
  id: number;
  name: string;
  amount: number;                 // Centavos
  count: number;
  percentage: number;
  color: string;
  icon: string;
  formatted: string;
}

interface ExpenseDistribution {
  categories: CategoryDistribution[];
  total: number;                  // Centavos
  total_formatted?: string;
  has_data: boolean;
}

interface DailyFlow {
  dates: string[];                // ["2025-12-01", "2025-12-02", ...]
  income: number[];               // Centavos por fecha
  expenses: number[];             // Centavos por fecha
  total_income: number;
  total_expenses: number;
  has_data: boolean;
}

interface Charts {
  expense_distribution: ExpenseDistribution;
  daily_flow: DailyFlow;
}

interface AccountsInfo {
  total_accounts: number;
  has_accounts: boolean;
}

interface EmptyState {
  message: string;
  suggestion: string;
  action: 'create_account' | 'create_transaction';
}

interface FinancialDashboardData {
  has_data: boolean;
  summary: FinancialSummary;
  filters: DashboardFilters;
  recent_transactions: RecentTransaction[];
  upcoming_bills: UpcomingBill[];
  charts: Charts;
  accounts_info: AccountsInfo;
  empty_state?: EmptyState;
}

interface DashboardResponse {
  success: boolean;
  data: FinancialDashboardData;
  message: string;
}
```

---

## ⚛️ Ejemplos React/TypeScript

### 1. Hook Personalizado para Dashboard

```typescript
// hooks/useFinancialDashboard.ts
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface DashboardFilters {
  year?: number;
  month?: number;
  accountId?: number;
  all?: boolean;
}

export const useFinancialDashboard = (initialFilters: DashboardFilters = {}) => {
  const [data, setData] = useState<FinancialDashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<DashboardFilters>(initialFilters);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      
      if (filters.all) {
        params.append('all', 'true');
      } else {
        if (filters.year) params.append('year', filters.year.toString());
        if (filters.month) params.append('month', filters.month.toString());
      }
      
      if (filters.accountId) {
        params.append('account_id', filters.accountId.toString());
      }

      const response = await axios.get<DashboardResponse>(
        `/api/dashboard/financial/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        }
      );

      if (response.data.success) {
        setData(response.data.data);
      } else {
        setError('Error al cargar el dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error de conexión');
      console.error('Error fetching dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const updateFilters = (newFilters: Partial<DashboardFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const refresh = () => {
    fetchDashboard();
  };

  return {
    data,
    loading,
    error,
    filters,
    updateFilters,
    refresh
  };
};
```

---

### 2. Componente de Cards Financieras

```typescript
// components/FinancialCards.tsx
import React from 'react';
import { FinancialSummary } from '../types';

interface Props {
  summary: FinancialSummary;
}

const formatCurrency = (cents: number, currency: string): string => {
  const amount = cents / 100;
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

export const FinancialCards: React.FC<Props> = ({ summary }) => {
  const cards = [
    {
      title: 'Total Ingresos',
      value: summary.total_income,
      icon: '💰',
      color: 'bg-green-500',
      textColor: 'text-green-600'
    },
    {
      title: 'Total Gastos',
      value: summary.total_expenses,
      icon: '💸',
      color: 'bg-red-500',
      textColor: 'text-red-600'
    },
    {
      title: 'Total Ahorros',
      value: summary.total_savings,
      icon: '🏦',
      color: 'bg-blue-500',
      textColor: 'text-blue-600'
    },
    {
      title: 'IVA Compras',
      value: summary.total_iva,
      icon: '📄',
      color: 'bg-yellow-500',
      textColor: 'text-yellow-600'
    },
    {
      title: 'GMF (4x1000)',
      value: summary.total_gmf,
      icon: '🏦',
      color: 'bg-orange-500',
      textColor: 'text-orange-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
      {cards.map((card) => (
        <div key={card.title} className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-600 text-sm">{card.title}</span>
            <span className="text-2xl">{card.icon}</span>
          </div>
          <div className={`text-2xl font-bold ${card.textColor}`}>
            {formatCurrency(card.value, summary.currency)}
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

### 3. Componente de Movimientos Recientes

```typescript
// components/RecentTransactions.tsx
import React from 'react';
import { RecentTransaction } from '../types';

interface Props {
  transactions: RecentTransaction[];
  currency: string;
}

export const RecentTransactions: React.FC<Props> = ({ transactions, currency }) => {
  const getTypeColor = (typeCode: number): string => {
    switch (typeCode) {
      case 1: return 'text-green-600 bg-green-100';
      case 2: return 'text-red-600 bg-red-100';
      case 3: return 'text-blue-600 bg-blue-100';
      case 4: return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatAmount = (cents: number): string => {
    const amount = cents / 100;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0
    }).format(amount);
  };

  if (transactions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Movimientos Recientes</h3>
        <p className="text-gray-500 text-center py-8">
          No hay movimientos recientes
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Movimientos Recientes</h3>
      <div className="space-y-3">
        {transactions.map((tx) => (
          <div
            key={tx.id}
            className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition"
          >
            <div className="flex items-center space-x-3 flex-1">
              {tx.category_icon && (
                <span className="text-2xl">{tx.category_icon}</span>
              )}
              <div className="flex-1">
                <p className="font-medium text-gray-900">
                  {tx.description}
                </p>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <span>{tx.account}</span>
                  {tx.category && (
                    <>
                      <span>•</span>
                      <span
                        className="px-2 py-1 rounded text-xs"
                        style={{ backgroundColor: tx.category_color + '20' }}
                      >
                        {tx.category}
                      </span>
                    </>
                  )}
                  <span>•</span>
                  <span>{new Date(tx.date).toLocaleDateString('es-CO')}</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(tx.type_code)}`}>
                {tx.type}
              </span>
              <p className={`font-bold mt-1 ${
                tx.type_code === 1 ? 'text-green-600' : 'text-red-600'
              }`}>
                {tx.type_code === 1 ? '+' : '-'}{formatAmount(tx.amount)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

### 4. Componente de Filtros

```typescript
// components/DashboardFilters.tsx
import React, { useState } from 'react';

interface Props {
  currentFilters: {
    year?: number;
    month?: number;
    accountId?: number;
  };
  accounts: { id: number; name: string }[];
  onFilterChange: (filters: any) => void;
}

export const DashboardFilters: React.FC<Props> = ({
  currentFilters,
  accounts,
  onFilterChange
}) => {
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 10 }, (_, i) => currentYear - i);
  
  const months = [
    { value: 1, label: 'Enero' },
    { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' },
    { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' },
    { value: 12, label: 'Diciembre' }
  ];

  const handleYearChange = (year: string) => {
    if (year === '') {
      onFilterChange({ year: undefined, month: undefined, all: true });
    } else {
      onFilterChange({ year: parseInt(year), all: false });
    }
  };

  const handleMonthChange = (month: string) => {
    if (month === '') {
      onFilterChange({ month: undefined });
    } else {
      onFilterChange({ month: parseInt(month) });
    }
  };

  const handleAccountChange = (accountId: string) => {
    if (accountId === '') {
      onFilterChange({ accountId: undefined });
    } else {
      onFilterChange({ accountId: parseInt(accountId) });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Filtro de Año */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Año
          </label>
          <select
            value={currentFilters.year || ''}
            onChange={(e) => handleYearChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los años</option>
            {years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        {/* Filtro de Mes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mes
          </label>
          <select
            value={currentFilters.month || ''}
            onChange={(e) => handleMonthChange(e.target.value)}
            disabled={!currentFilters.year}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          >
            <option value="">Todos los meses</option>
            {months.map(month => (
              <option key={month.value} value={month.value}>
                {month.label}
              </option>
            ))}
          </select>
        </div>

        {/* Filtro de Cuenta */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cuenta
          </label>
          <select
            value={currentFilters.accountId || ''}
            onChange={(e) => handleAccountChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas las cuentas</option>
            {accounts.map(account => (
              <option key={account.id} value={account.id}>
                {account.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
```

---

### 5. Componente de Facturas Próximas a Vencer

```typescript
// components/UpcomingBills.tsx
import React from 'react';
import { UpcomingBill } from '../types';

interface Props {
  bills: UpcomingBill[];
  currency: string;
}

export const UpcomingBills: React.FC<Props> = ({ bills, currency }) => {
  const formatDaysLabel = (days: number): string => {
    if (days < 0) {
      return `Vencida hace ${Math.abs(days)} ${Math.abs(days) === 1 ? 'día' : 'días'}`;
    } else if (days === 0) {
      return 'Vence hoy';
    } else {
      return `Vence en ${days} ${days === 1 ? 'día' : 'días'}`;
    }
  };

  const formatAmount = (cents: number): string => {
    const amount = cents / 100;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0
    }).format(amount);
  };

  const getUrgencyBadgeClass = (urgency: string): string => {
    switch (urgency) {
      case 'overdue':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'today':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'urgent':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'soon':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (bills.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">📅 Facturas Próximas</h3>
        <div className="text-center py-8">
          <p className="text-gray-500">🎉 No tienes facturas pendientes</p>
          <p className="text-gray-400 text-sm mt-2">Todas tus facturas están al día</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">📅 Facturas Próximas</h3>
        <span className="text-sm text-gray-500">
          {bills.length} {bills.length === 1 ? 'factura' : 'facturas'} pendiente{bills.length !== 1 ? 's' : ''}
        </span>
      </div>
      
      <div className="space-y-3">
        {bills.map((bill) => (
          <div
            key={bill.id}
            className="border rounded-lg p-4 hover:shadow-md transition"
            style={{
              borderLeftWidth: '4px',
              borderLeftColor: bill.urgency_color,
              backgroundColor: bill.urgency_color + '08'
            }}
          >
            {/* Header con proveedor y urgencia */}
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center space-x-2">
                {bill.category_icon && (
                  <span className="text-2xl">{bill.category_icon}</span>
                )}
                <div>
                  <h4 className="font-semibold text-gray-900">{bill.provider}</h4>
                  {bill.category && (
                    <span
                      className="text-xs px-2 py-1 rounded"
                      style={{ 
                        backgroundColor: bill.category_color + '20',
                        color: bill.category_color 
                      }}
                    >
                      {bill.category}
                    </span>
                  )}
                </div>
              </div>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium border ${getUrgencyBadgeClass(bill.urgency)}`}
              >
                {bill.urgency_label}
              </span>
            </div>

            {/* Información de fecha y días */}
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm text-gray-600">
                <p className="font-medium">{formatDaysLabel(bill.days_until_due)}</p>
                <p className="text-xs">
                  Vencimiento: {new Date(bill.due_date).toLocaleDateString('es-CO', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                  })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold" style={{ color: bill.urgency_color }}>
                  {formatAmount(bill.amount)}
                </p>
                {bill.is_recurring && (
                  <span className="text-xs text-gray-500">🔄 Recurrente</span>
                )}
              </div>
            </div>

            {/* Cuenta sugerida y descripción */}
            {(bill.suggested_account || bill.description) && (
              <div className="border-t pt-2 mt-2">
                {bill.suggested_account && (
                  <p className="text-sm text-gray-600">
                    💳 Sugerida: <span className="font-medium">{bill.suggested_account}</span>
                  </p>
                )}
                {bill.description && (
                  <p className="text-xs text-gray-500 mt-1">{bill.description}</p>
                )}
              </div>
            )}

            {/* Botón de acción */}
            <div className="mt-3">
              <button
                className="w-full py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition text-sm font-medium"
                onClick={() => {
                  // Navegar a pantalla de pago
                  console.log(`Pagar factura ${bill.id}`);
                }}
              >
                Pagar Ahora
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Resumen total */}
      <div className="mt-4 pt-4 border-t">
        <div className="flex justify-between items-center">
          <span className="text-gray-600 font-medium">Total Pendiente:</span>
          <span className="text-xl font-bold text-gray-900">
            {formatAmount(bills.reduce((sum, bill) => sum + bill.amount, 0))}
          </span>
        </div>
      </div>
    </div>
  );
};
```

---

### 6. Componente Principal del Dashboard

```typescript
// pages/Dashboard.tsx
import React from 'react';
import { useFinancialDashboard } from '../hooks/useFinancialDashboard';
import { FinancialCards } from '../components/FinancialCards';
import { RecentTransactions } from '../components/RecentTransactions';
import { UpcomingBills } from '../components/UpcomingBills';
import { DashboardFilters } from '../components/DashboardFilters';
import { ExpenseDistributionChart } from '../components/charts/ExpenseDistributionChart';
import { DailyFlowChart } from '../components/charts/DailyFlowChart';
import { EmptyState } from '../components/EmptyState';

export const Dashboard: React.FC = () => {
  const { data, loading, error, filters, updateFilters, refresh } = useFinancialDashboard();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 text-xl mb-4">❌ {error}</p>
          <button
            onClick={refresh}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  // Mostrar estado vacío si no hay datos
  if (!data.has_data) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Dashboard Financiero</h1>
        <EmptyState
          message={data.empty_state?.message || 'No hay datos'}
          suggestion={data.empty_state?.suggestion || ''}
          action={data.empty_state?.action || 'create_account'}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard Financiero</h1>
        <div className="flex items-center space-x-2">
          <span className="text-gray-600">{data.filters.period_label}</span>
          <button
            onClick={refresh}
            className="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            🔄 Actualizar
          </button>
        </div>
      </div>

      {/* Filtros */}
      <DashboardFilters
        currentFilters={filters}
        accounts={[]} // Cargar desde API de cuentas
        onFilterChange={updateFilters}
      />

      {/* Cards Financieras */}
      <FinancialCards summary={data.summary} />

      {/* Grid de Contenido */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Gráfico de Distribución de Gastos */}
        <ExpenseDistributionChart
          data={data.charts.expense_distribution}
          currency={data.summary.currency}
        />

        {/* Gráfico de Flujo Diario */}
        <DailyFlowChart
          data={data.charts.daily_flow}
          currency={data.summary.currency}
        />
      </div>

      {/* Grid de Listas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Movimientos Recientes */}
        <RecentTransactions
          transactions={data.recent_transactions}
          currency={data.summary.currency}
        />

        {/* Facturas Próximas */}
        <UpcomingBills
          bills={data.upcoming_bills}
          currency={data.summary.currency}
        />
      </div>
    </div>
  );
};
```

---

### 7. Componente de Estado Vacío
        currency={data.summary.currency}
      />
    </div>
  );
};
```

---

### 6. Componente de Estado Vacío

```typescript
// components/EmptyState.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

interface Props {
  message: string;
  suggestion: string;
  action: 'create_account' | 'create_transaction';
}

export const EmptyState: React.FC<Props> = ({ message, suggestion, action }) => {
  const navigate = useNavigate();

  const handleAction = () => {
    if (action === 'create_account') {
      navigate('/accounts/create');
    } else if (action === 'create_transaction') {
      navigate('/transactions/create');
    }
  };

  const getIcon = () => {
    return action === 'create_account' ? '🏦' : '💰';
  };

  const getButtonText = () => {
    return action === 'create_account' ? 'Crear Cuenta' : 'Registrar Movimiento';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-12 text-center">
      <div className="text-6xl mb-4">{getIcon()}</div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">{message}</h2>
      <p className="text-gray-600 mb-6">{suggestion}</p>
      <button
        onClick={handleAction}
        className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition font-medium"
      >
        {getButtonText()}
      </button>
    </div>
  );
};
```

---

## 🎨 Componentes de Gráficos

### Gráfico de Dona (Chart.js)

```typescript
// components/charts/ExpenseDistributionChart.tsx
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { ExpenseDistribution } from '../../types';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  data: ExpenseDistribution;
  currency: string;
}

export const ExpenseDistributionChart: React.FC<Props> = ({ data, currency }) => {
  if (!data.has_data || data.categories.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Distribución de gastos</h3>
        <p className="text-gray-500 text-center py-8">No hay datos disponibles</p>
      </div>
    );
  }

  const chartData = {
    labels: data.categories.map(cat => cat.name),
    datasets: [
      {
        data: data.categories.map(cat => cat.amount / 100),
        backgroundColor: data.categories.map(cat => cat.color),
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.parsed;
            const percentage = data.categories[context.dataIndex].percentage;
            return `${context.label}: ${new Intl.NumberFormat('es-CO', {
              style: 'currency',
              currency: currency,
              minimumFractionDigits: 0
            }).format(value)} (${percentage.toFixed(1)}%)`;
          }
        }
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Distribución de gastos</h3>
        <button className="text-sm text-blue-500 hover:text-blue-600">
          Con impuestos
        </button>
      </div>
      <Doughnut data={chartData} options={options} />
      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">Total</p>
        <p className="text-2xl font-bold">
          {new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0
          }).format(data.total / 100)}
        </p>
      </div>
    </div>
  );
};
```

---

### Gráfico de Líneas (Chart.js)

```typescript
// components/charts/DailyFlowChart.tsx
import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { DailyFlow } from '../../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface Props {
  data: DailyFlow;
  currency: string;
}

export const DailyFlowChart: React.FC<Props> = ({ data, currency }) => {
  if (!data.has_data || data.dates.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Ingreso vs Gasto diario</h3>
        <p className="text-gray-500 text-center py-8">No hay datos disponibles</p>
      </div>
    );
  }

  const chartData = {
    labels: data.dates.map(date => {
      const d = new Date(date);
      return `${d.getDate()}/${d.getMonth() + 1}`;
    }),
    datasets: [
      {
        label: 'Ingresos',
        data: data.income.map(amount => amount / 100),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.3
      },
      {
        label: 'Gastos',
        data: data.expenses.map(amount => amount / 100),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.3
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            return `${context.dataset.label}: ${new Intl.NumberFormat('es-CO', {
              style: 'currency',
              currency: currency,
              minimumFractionDigits: 0
            }).format(context.parsed.y)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: any) => {
            return new Intl.NumberFormat('es-CO', {
              style: 'currency',
              currency: currency,
              minimumFractionDigits: 0,
              notation: 'compact'
            }).format(value);
          }
        }
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Ingreso vs Gasto diario</h3>
      <Line data={chartData} options={options} />
      <div className="mt-4 grid grid-cols-2 gap-4 text-center">
        <div>
          <p className="text-sm text-gray-600">Ingresos</p>
          <p className="text-lg font-bold text-green-600">
            {new Intl.NumberFormat('es-CO', {
              style: 'currency',
              currency: currency,
              minimumFractionDigits: 0
            }).format(data.total_income / 100)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Gastos</p>
          <p className="text-lg font-bold text-red-600">
            {new Intl.NumberFormat('es-CO', {
              style: 'currency',
              currency: currency,
              minimumFractionDigits: 0
            }).format(data.total_expenses / 100)}
          </p>
        </div>
      </div>
    </div>
  );
};
```

---

## 🖥️ Ejemplos Vue.js 3

### Composable para Dashboard

```typescript
// composables/useFinancialDashboard.ts
import { ref, computed, watch } from 'vue';
import axios from 'axios';
import type { FinancialDashboardData } from '../types';

interface DashboardFilters {
  year?: number;
  month?: number;
  accountId?: number;
  all?: boolean;
}

export function useFinancialDashboard(initialFilters: DashboardFilters = {}) {
  const data = ref<FinancialDashboardData | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const filters = ref<DashboardFilters>(initialFilters);

  const fetchDashboard = async () => {
    loading.value = true;
    error.value = null;

    try {
      const params = new URLSearchParams();
      
      if (filters.value.all) {
        params.append('all', 'true');
      } else {
        if (filters.value.year) params.append('year', filters.value.year.toString());
        if (filters.value.month) params.append('month', filters.value.month.toString());
      }
      
      if (filters.value.accountId) {
        params.append('account_id', filters.value.accountId.toString());
      }

      const response = await axios.get(
        `/api/dashboard/financial/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        }
      );

      if (response.data.success) {
        data.value = response.data.data;
      } else {
        error.value = 'Error al cargar el dashboard';
      }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Error de conexión';
      console.error('Error fetching dashboard:', err);
    } finally {
      loading.value = false;
    }
  };

  watch(filters, fetchDashboard, { deep: true, immediate: true });

  const updateFilters = (newFilters: Partial<DashboardFilters>) => {
    filters.value = { ...filters.value, ...newFilters };
  };

  return {
    data: computed(() => data.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    filters: computed(() => filters.value),
    updateFilters,
    refresh: fetchDashboard
  };
}
```

---

### Componente Principal Vue

```vue
<!-- pages/Dashboard.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-screen">
      <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center h-screen">
      <div class="text-center">
        <p class="text-red-600 text-xl mb-4">❌ {{ error }}</p>
        <button
          @click="refresh"
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Reintentar
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else-if="!data?.has_data"
      :message="data?.empty_state?.message || 'No hay datos'"
      :suggestion="data?.empty_state?.suggestion || ''"
      :action="data?.empty_state?.action || 'create_account'"
    />

    <!-- Dashboard Content -->
    <template v-else-if="data">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Dashboard Financiero</h1>
        <div class="flex items-center space-x-2">
          <span class="text-gray-600">{{ data.filters.period_label }}</span>
          <button
            @click="refresh"
            class="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            🔄 Actualizar
          </button>
        </div>
      </div>

      <!-- Filtros -->
      <DashboardFilters
        :current-filters="filters"
        :accounts="accounts"
        @filter-change="updateFilters"
      />

      <!-- Cards Financieras -->
      <FinancialCards :summary="data.summary" />

      <!-- Gráficos -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ExpenseDistributionChart
          :data="data.charts.expense_distribution"
          :currency="data.summary.currency"
        />
        <DailyFlowChart
          :data="data.charts.daily_flow"
          :currency="data.summary.currency"
        />
      </div>

      <!-- Movimientos Recientes -->
      <RecentTransactions
        :transactions="data.recent_transactions"
        :currency="data.summary.currency"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { useFinancialDashboard } from '../composables/useFinancialDashboard';
import FinancialCards from '../components/FinancialCards.vue';
import DashboardFilters from '../components/DashboardFilters.vue';
import RecentTransactions from '../components/RecentTransactions.vue';
import ExpenseDistributionChart from '../components/charts/ExpenseDistributionChart.vue';
import DailyFlowChart from '../components/charts/DailyFlowChart.vue';
import EmptyState from '../components/EmptyState.vue';

const accounts = ref([]); // Cargar desde API

const { data, loading, error, filters, updateFilters, refresh } = useFinancialDashboard();
</script>
```

---

## ✅ Mejores Prácticas

### 1. **Siempre Convertir Centavos a Pesos**

```javascript
// ❌ INCORRECTO
<p>${data.summary.total_income}</p>  // Muestra: $15000000

// ✅ CORRECTO
<p>${(data.summary.total_income / 100).toLocaleString()}</p>  // Muestra: $150,000
```

---

### 2. **Usar Intl.NumberFormat para Formateo**

```javascript
const formatCurrency = (cents, currency) => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(cents / 100);
};

// Uso
formatCurrency(15000000, 'COP'); // "$150.000"
formatCurrency(10000, 'USD');    // "$100"
```

---

### 3. **Verificar has_data Antes de Renderizar**

```javascript
// Siempre verificar
if (!data.has_data) {
  return <EmptyState {...data.empty_state} />;
}

// Para gráficos individuales
if (!data.charts.expense_distribution.has_data) {
  return <p>No hay datos de gastos</p>;
}
```

---

### 4. **Manejar Errores Gracefully**

```javascript
try {
  await fetchDashboard();
} catch (error) {
  if (error.response?.status === 401) {
    // Token expirado, redirigir a login
    router.push('/login');
  } else if (error.response?.status === 400) {
    // Error de validación, mostrar mensaje
    setError(error.response.data.error);
  } else {
    // Error genérico
    setError('Error de conexión. Intenta nuevamente.');
  }
}
```

---

### 5. **Optimizar Renders con Memoization**

```typescript
// React
const formattedIncome = useMemo(() => {
  return formatCurrency(data.summary.total_income, data.summary.currency);
}, [data.summary.total_income, data.summary.currency]);

// Vue
const formattedIncome = computed(() => {
  return formatCurrency(data.value.summary.total_income, data.value.summary.currency);
});
```

---

### 6. **Debounce en Filtros**

```javascript
import { debounce } from 'lodash';

const debouncedUpdateFilters = debounce((filters) => {
  updateFilters(filters);
}, 300);

// Uso en onChange
onChange={(value) => debouncedUpdateFilters({ year: value })}
```

---

### 7. **Loading States Específicos**

```javascript
const [loadingCards, setLoadingCards] = useState(true);
const [loadingCharts, setLoadingCharts] = useState(true);
const [loadingTransactions, setLoadingTransactions] = useState(true);

// Mostrar skeletons específicos por sección
```

---

### 8. **Cache de Datos**

```javascript
// React Query
const { data, isLoading } = useQuery(
  ['financial-dashboard', filters],
  () => fetchDashboard(filters),
  {
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000 // 10 minutos
  }
);

// Vue Query / TanStack Query Vue
const { data, isLoading } = useQuery({
  queryKey: ['financial-dashboard', filters],
  queryFn: () => fetchDashboard(filters),
  staleTime: 5 * 60 * 1000
});
```

---

## 🔗 Enlaces Relacionados

- [DASHBOARD_FINANCIAL_API_POSTMAN.md](./DASHBOARD_FINANCIAL_API_POSTMAN.md) - Guía de Postman
- [ANALYTICS_AMOUNTS_FORMAT.md](./ANALYTICS_AMOUNTS_FORMAT.md) - Formato de montos
- [CURRENCY_BASE_CONFIGURATION.md](./CURRENCY_BASE_CONFIGURATION.md) - Configuración de moneda

---

**Última actualización:** 11 de diciembre de 2025  
**Versión:** 1.0  
**Autor:** Backend Team
