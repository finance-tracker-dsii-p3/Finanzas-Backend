# HU-14 — Comparación Básica entre Períodos - Guía Frontend

## Resumen

Esta guía explica cómo implementar en el frontend la comparación de ingresos y gastos entre dos períodos, mostrando diferencias absolutas y porcentuales.

## Endpoint Disponible

### Comparación entre Períodos

```
GET /api/analytics/compare-periods/
```

**Query Parameters:**
- `period1` - Período base para comparación (requerido)
  - Valores predefinidos: `current_month`, `last_month`, `current_year`, `last_7_days`, `last_30_days`
  - Mes específico: `YYYY-MM` (ej: `2025-09`)
  - Año específico: `YYYY` (ej: `2025`)
  - Rango personalizado: `YYYY-MM-DD,YYYY-MM-DD` (ej: `2025-01-01,2025-01-31`)
- `period2` - Período a comparar contra period1 (requerido)
  - Mismo formato que `period1`
- `mode` - Modo de cálculo (default: `total`)
  - `base` - Solo montos base (sin impuestos)
  - `total` - Montos totales (base + impuestos)

**Ejemplo de Request:**
```typescript
GET /api/analytics/compare-periods/?period1=2025-09&period2=2025-10&mode=total
```

**Respuesta Exitosa:**
```json
{
  "success": true,
  "data": {
    "comparison_summary": {
      "period1": {
        "name": "September 2025",
        "date_range": "01/09/2025 - 30/09/2025",
        "has_data": true,
        "transactions_count": 45
      },
      "period2": {
        "name": "October 2025",
        "date_range": "01/10/2025 - 31/10/2025",
        "has_data": true,
        "transactions_count": 52
      },
      "can_compare": true,
      "mode": "total"
    },
    "period_data": {
      "period1": {
        "income": {
          "amount": 5000000,
          "count": 12,
          "formatted": "$5,000,000"
        },
        "expenses": {
          "amount": 4000000,
          "count": 33,
          "formatted": "$4,000,000"
        },
        "balance": {
          "amount": 1000000,
          "formatted": "$1,000,000",
          "is_positive": true
        },
        "period": {
          "start": "2025-09-01",
          "end": "2025-09-30",
          "days": 30
        },
        "mode": "total",
        "currency": "COP"
      },
      "period2": {
        "income": {
          "amount": 5500000,
          "count": 15,
          "formatted": "$5,500,000"
        },
        "expenses": {
          "amount": 3915000,
          "count": 37,
          "formatted": "$3,915,000"
        },
        "balance": {
          "amount": 1585000,
          "formatted": "$1,585,000",
          "is_positive": true
        },
        "period": {
          "start": "2025-10-01",
          "end": "2025-10-31",
          "days": 31
        },
        "mode": "total",
        "currency": "COP"
      }
    },
    "differences": {
      "income": {
        "absolute": 500000,
        "percentage": 10.0,
        "is_increase": true,
        "is_significant": true,
        "period1_amount": 5000000,
        "period2_amount": 5500000,
        "formatted_absolute": "$500.000",
        "summary": "Ingresos +10.0% (+$500.000)"
      },
      "expenses": {
        "absolute": -85000,
        "percentage": -2.125,
        "is_increase": false,
        "is_significant": false,
        "period1_amount": 4000000,
        "period2_amount": 3915000,
        "formatted_absolute": "$85.000",
        "summary": "Gastos -2.1% (-$85.000)"
      },
      "balance": {
        "absolute": 585000,
        "percentage": 58.5,
        "is_increase": true,
        "is_significant": true,
        "period1_amount": 1000000,
        "period2_amount": 1585000,
        "formatted_absolute": "$585.000",
        "summary": "Balance +58.5% (+$585.000)"
      }
    },
    "insights": {
      "messages": [
        "Excelente: Los ingresos aumentaron 10.0%.",
        "Bien: Los gastos disminuyeron 2.1%.",
        "Situación financiera muy mejorada."
      ],
      "alert_level": "success",
      "has_significant_changes": true
    },
    "metadata": {
      "generated_at": "2025-11-30",
      "comparison_mode": "total",
      "currency": "COP"
    }
  },
  "message": "Comparación completada: September 2025 vs October 2025",
  "executive_summary": [
    "Ingresos +10.0% (+$500.000)",
    "Gastos -2.1% (-$85.000)",
    "Balance +58.5% (+$585.000)"
  ]
}
```

**Respuesta Sin Datos en Período 1:**
```json
{
  "success": false,
  "error": "No hay datos en el primer período (2025-08)",
  "code": "NO_DATA_PERIOD1",
  "details": {
    "comparison_summary": {
      "period1": {
        "has_data": false,
        "transactions_count": 0
      },
      "period2": {
        "has_data": true,
        "transactions_count": 45
      },
      "can_compare": false
    },
    "total_user_transactions": 120,
    "suggestion": "Intenta con períodos que tengan transacciones registradas"
  }
}
```

**Respuesta Sin Datos en Período 2:**
```json
{
  "success": false,
  "error": "No hay datos en el segundo período (2025-11)",
  "code": "NO_DATA_PERIOD2",
  "details": {
    "comparison_summary": {
      "period1": {
        "has_data": true,
        "transactions_count": 45
      },
      "period2": {
        "has_data": false,
        "transactions_count": 0
      },
      "can_compare": false
    },
    "total_user_transactions": 120,
    "suggestion": "Intenta con períodos que tengan transacciones registradas"
  }
}
```

**Respuesta Sin Parámetros:**
```json
{
  "success": false,
  "error": "Parámetros period1 y period2 son requeridos",
  "code": "MISSING_PERIODS",
  "details": {
    "provided": {
      "period1": null,
      "period2": null
    },
    "examples": [
      "?period1=2025-09&period2=2025-10&mode=total",
      "?period1=last_month&period2=current_month&mode=base"
    ]
  }
}
```

## Implementación Frontend

### 1. Servicio de Comparación

```typescript
// services/analyticsService.ts (extender el servicio existente)

interface ComparePeriodsParams {
  period1: string;
  period2: string;
  mode?: 'base' | 'total';
}

interface ComparisonResponse {
  success: boolean;
  data?: {
    comparison_summary: {
      period1: {
        name: string;
        date_range: string;
        has_data: boolean;
        transactions_count: number;
      };
      period2: {
        name: string;
        date_range: string;
        has_data: boolean;
        transactions_count: number;
      };
      can_compare: boolean;
      mode: string;
    };
    period_data: {
      period1: {
        income: { amount: number; count: number; formatted: string };
        expenses: { amount: number; count: number; formatted: string };
        balance: { amount: number; formatted: string; is_positive: boolean };
      };
      period2: {
        income: { amount: number; count: number; formatted: string };
        expenses: { amount: number; count: number; formatted: string };
        balance: { amount: number; formatted: string; is_positive: boolean };
      };
    };
    differences: {
      income: {
        absolute: number;
        percentage: number;
        is_increase: boolean;
        is_significant: boolean;
        period1_amount: number;
        period2_amount: number;
        formatted_absolute: string;
        summary: string;
      };
      expenses: {
        absolute: number;
        percentage: number;
        is_increase: boolean;
        is_significant: boolean;
        period1_amount: number;
        period2_amount: number;
        formatted_absolute: string;
        summary: string;
      };
      balance: {
        absolute: number;
        percentage: number;
        is_increase: boolean;
        is_significant: boolean;
        period1_amount: number;
        period2_amount: number;
        formatted_absolute: string;
        summary: string;
      };
    };
    insights: {
      messages: string[];
      alert_level: 'info' | 'warning' | 'success' | 'error';
      has_significant_changes: boolean;
    };
    metadata: {
      generated_at: string;
      comparison_mode: string;
      currency: string;
    };
  };
  error?: string;
  code?: string;
  details?: any;
  message?: string;
  executive_summary?: string[];
}

class AnalyticsService {
  private baseUrl = '/api/analytics';

  async comparePeriods(params: ComparePeriodsParams): Promise<ComparisonResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('period1', params.period1);
    queryParams.append('period2', params.period2);
    if (params.mode) {
      queryParams.append('mode', params.mode);
    }

    const response = await fetch(
      `${this.baseUrl}/compare-periods/?${queryParams.toString()}`,
      {
        headers: {
          'Authorization': `Token ${this.getToken()}`,
          'Content-Type': 'application/json',
        },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Error al comparar períodos');
    }

    return data;
  }

  private getToken(): string {
    return localStorage.getItem('authToken') || '';
  }
}

export const analyticsService = new AnalyticsService();
```

### 2. Componente de Comparación de Períodos

```typescript
// components/PeriodComparison.tsx

import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';

interface PeriodComparisonProps {
  defaultPeriod1?: string;
  defaultPeriod2?: string;
  defaultMode?: 'base' | 'total';
}

export const PeriodComparison: React.FC<PeriodComparisonProps> = ({
  defaultPeriod1 = 'last_month',
  defaultPeriod2 = 'current_month',
  defaultMode = 'total',
}) => {
  const [period1, setPeriod1] = useState(defaultPeriod1);
  const [period2, setPeriod2] = useState(defaultPeriod2);
  const [mode, setMode] = useState<'base' | 'total'>(defaultMode);
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (period1 && period2) {
      loadComparison();
    }
  }, [period1, period2, mode]);

  const loadComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await analyticsService.comparePeriods({
        period1,
        period2,
        mode,
      });

      if (response.success && response.data) {
        setComparison(response.data);
      } else {
        setError(response.error || 'No se pudo realizar la comparación');
        setComparison(null);
      }
    } catch (err: any) {
      setError(err.message || 'Error al cargar comparación');
      setComparison(null);
    } finally {
      setLoading(false);
    }
  };

  const handleModeToggle = () => {
    setMode(mode === 'base' ? 'total' : 'base');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-500">Cargando comparación...</p>
        </div>
      </div>
    );
  }

  if (error && !comparison) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center mb-2">
          <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold text-red-800">Error</h3>
        </div>
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  if (!comparison) {
    return null;
  }

  const { comparison_summary, period_data, differences, insights } = comparison;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <h2 className="text-2xl font-bold">Comparación de Períodos</h2>

          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <label className="block text-sm font-medium text-gray-700">
                Período 1:
              </label>
              <select
                value={period1}
                onChange={(e) => setPeriod1(e.target.value)}
                className="border rounded px-3 py-2 text-sm"
              >
                <option value="last_month">Mes anterior</option>
                <option value="current_month">Mes actual</option>
                <option value="current_year">Año actual</option>
                <option value="last_7_days">Últimos 7 días</option>
                <option value="last_30_days">Últimos 30 días</option>
              </select>
            </div>

            <div className="flex gap-2">
              <label className="block text-sm font-medium text-gray-700">
                Período 2:
              </label>
              <select
                value={period2}
                onChange={(e) => setPeriod2(e.target.value)}
                className="border rounded px-3 py-2 text-sm"
              >
                <option value="current_month">Mes actual</option>
                <option value="last_month">Mes anterior</option>
                <option value="current_year">Año actual</option>
                <option value="last_7_days">Últimos 7 días</option>
                <option value="last_30_days">Últimos 30 días</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Modo:</label>
              <button
                onClick={handleModeToggle}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  mode === 'base'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                Solo Base
              </button>
              <button
                onClick={handleModeToggle}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  mode === 'total'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                Base + Impuestos
              </button>
            </div>
          </div>
        </div>

        {!comparison_summary.can_compare && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-yellow-800">
              {error || 'No se puede realizar la comparación. Verifica que ambos períodos tengan datos.'}
            </p>
          </div>
        )}

        {comparison_summary.can_compare && (
          <>
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-gray-700 mb-2">
                  {comparison_summary.period1.name}
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  {comparison_summary.period1.date_range}
                </p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Ingresos:</span>
                    <span className="font-semibold text-green-600">
                      {period_data.period1.income.formatted}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gastos:</span>
                    <span className="font-semibold text-red-600">
                      {period_data.period1.expenses.formatted}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Balance:</span>
                    <span
                      className={`font-semibold ${
                        period_data.period1.balance.is_positive
                          ? 'text-blue-600'
                          : 'text-orange-600'
                      }`}
                    >
                      {period_data.period1.balance.formatted}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    {comparison_summary.period1.transactions_count} transacciones
                  </div>
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <h3 className="font-semibold text-gray-700 mb-2">
                  {comparison_summary.period2.name}
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  {comparison_summary.period2.date_range}
                </p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Ingresos:</span>
                    <span className="font-semibold text-green-600">
                      {period_data.period2.income.formatted}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gastos:</span>
                    <span className="font-semibold text-red-600">
                      {period_data.period2.expenses.formatted}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Balance:</span>
                    <span
                      className={`font-semibold ${
                        period_data.period2.balance.is_positive
                          ? 'text-blue-600'
                          : 'text-orange-600'
                      }`}
                    >
                      {period_data.period2.balance.formatted}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    {comparison_summary.period2.transactions_count} transacciones
                  </div>
                </div>
              </div>
            </div>

            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">Diferencias</h3>
              <div className="grid grid-cols-3 gap-4">
                <ComparisonMetric
                  label="Ingresos"
                  difference={differences.income}
                  positiveColor="green"
                />
                <ComparisonMetric
                  label="Gastos"
                  difference={differences.expenses}
                  positiveColor="red"
                  invertLogic={true}
                />
                <ComparisonMetric
                  label="Balance"
                  difference={differences.balance}
                  positiveColor="blue"
                />
              </div>
            </div>

            {insights && insights.messages.length > 0 && (
              <div className={`mt-6 p-4 rounded-lg border ${
                insights.alert_level === 'success' ? 'bg-green-50 border-green-200' :
                insights.alert_level === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                insights.alert_level === 'error' ? 'bg-red-50 border-red-200' :
                'bg-blue-50 border-blue-200'
              }`}>
                <h4 className="font-semibold mb-2">Análisis</h4>
                <ul className="space-y-1">
                  {insights.messages.map((message, index) => (
                    <li key={index} className="text-sm">
                      {message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

interface ComparisonMetricProps {
  label: string;
  difference: {
    absolute: number;
    percentage: number;
    is_increase: boolean;
    is_significant: boolean;
    formatted_absolute: string;
    summary: string;
  };
  positiveColor: 'green' | 'red' | 'blue';
  invertLogic?: boolean;
}

const ComparisonMetric: React.FC<ComparisonMetricProps> = ({
  label,
  difference,
  positiveColor,
  invertLogic = false,
}) => {
  const isPositive = invertLogic ? !difference.is_increase : difference.is_increase;
  const colorClass =
    positiveColor === 'green'
      ? isPositive
        ? 'text-green-600'
        : 'text-red-600'
      : positiveColor === 'red'
      ? isPositive
        ? 'text-red-600'
        : 'text-green-600'
      : isPositive
      ? 'text-blue-600'
      : 'text-orange-600';

  const bgColorClass =
    positiveColor === 'green'
      ? isPositive
        ? 'bg-green-50 border-green-200'
        : 'bg-red-50 border-red-200'
      : positiveColor === 'red'
      ? isPositive
        ? 'bg-red-50 border-red-200'
        : 'bg-green-50 border-green-200'
      : isPositive
      ? 'bg-blue-50 border-blue-200'
      : 'bg-orange-50 border-orange-200';

  return (
    <div className={`border rounded-lg p-4 ${bgColorClass}`}>
      <div className="text-sm font-medium text-gray-700 mb-2">{label}</div>
      <div className="flex items-center gap-2 mb-1">
        {difference.is_increase ? (
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        )}
        <span className={`text-xl font-bold ${colorClass}`}>
          {difference.percentage > 0 ? '+' : ''}
          {difference.percentage.toFixed(1)}%
        </span>
      </div>
      <div className={`text-sm ${colorClass}`}>
        {difference.is_increase ? '+' : '-'}
        {difference.formatted_absolute}
      </div>
      {difference.is_significant && (
        <div className="text-xs text-gray-500 mt-1">Cambio significativo</div>
      )}
    </div>
  );
};
```

### 3. Componente Simplificado (Solo Diferencias)

```typescript
// components/SimplePeriodComparison.tsx

import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';

export const SimplePeriodComparison: React.FC = () => {
  const [period1, setPeriod1] = useState('last_month');
  const [period2, setPeriod2] = useState('current_month');
  const [mode, setMode] = useState<'base' | 'total'>('total');
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadComparison();
  }, [period1, period2, mode]);

  const loadComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await analyticsService.comparePeriods({
        period1,
        period2,
        mode,
      });

      if (response.success && response.data) {
        setComparison(response.data);
      } else {
        setError(response.error || 'No se pudo realizar la comparación');
        setComparison(null);
      }
    } catch (err: any) {
      setError(err.message || 'Error al cargar comparación');
      setComparison(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Cargando comparación...</div>;
  }

  if (error && !comparison) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4">
        <p className="text-red-800">{error}</p>
        <p className="text-sm text-red-600 mt-2">
          Verifica que ambos períodos tengan transacciones registradas.
        </p>
      </div>
    );
  }

  if (!comparison || !comparison.comparison_summary.can_compare) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
        <p className="text-yellow-800">
          No hay información disponible para comparar estos períodos.
        </p>
      </div>
    );
  }

  const { differences, comparison_summary } = comparison;

  return (
    <div className="space-y-4">
      <div className="flex gap-4 items-center">
        <select
          value={period1}
          onChange={(e) => setPeriod1(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="last_month">Mes anterior</option>
          <option value="current_month">Mes actual</option>
        </select>
        <span className="text-gray-500">vs</span>
        <select
          value={period2}
          onChange={(e) => setPeriod2(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="current_month">Mes actual</option>
          <option value="last_month">Mes anterior</option>
        </select>
        <button
          onClick={() => setMode(mode === 'base' ? 'total' : 'base')}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          {mode === 'base' ? 'Solo Base' : 'Base + Impuestos'}
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">
          {comparison_summary.period1.name} vs {comparison_summary.period2.name}
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="font-medium">Ingresos:</span>
            <span
              className={`font-semibold ${
                differences.income.is_increase ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {differences.income.summary}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="font-medium">Gastos:</span>
            <span
              className={`font-semibold ${
                differences.expenses.is_increase ? 'text-red-600' : 'text-green-600'
              }`}
            >
              {differences.expenses.summary}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="font-medium">Balance:</span>
            <span
              className={`font-semibold ${
                differences.balance.is_increase ? 'text-blue-600' : 'text-orange-600'
              }`}
            >
              {differences.balance.summary}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### 4. Componente con Gráfico de Comparación

```typescript
// components/ComparisonChart.tsx

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ComparisonChartProps {
  period1Name: string;
  period2Name: string;
  period1Data: {
    income: number;
    expenses: number;
    balance: number;
  };
  period2Data: {
    income: number;
    expenses: number;
    balance: number;
  };
}

export const ComparisonChart: React.FC<ComparisonChartProps> = ({
  period1Name,
  period2Name,
  period1Data,
  period2Data,
}) => {
  const chartData = [
    {
      name: 'Ingresos',
      [period1Name]: period1Data.income,
      [period2Name]: period2Data.income,
    },
    {
      name: 'Gastos',
      [period1Name]: period1Data.expenses,
      [period2Name]: period2Data.expenses,
    },
    {
      name: 'Balance',
      [period1Name]: period1Data.balance,
      [period2Name]: period2Data.balance,
    },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip
          formatter={(value: number) => `$${value.toLocaleString()}`}
        />
        <Legend />
        <Bar dataKey={period1Name} fill="#3B82F6" />
        <Bar dataKey={period2Name} fill="#10B981" />
      </BarChart>
    </ResponsiveContainer>
  );
};
```

### 5. Página Completa de Comparación

```typescript
// pages/PeriodComparisonPage.tsx

import React, { useState } from 'react';
import { PeriodComparison } from '../components/PeriodComparison';

export const PeriodComparisonPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Comparación de Períodos</h1>
        <p className="text-gray-600">
          Compara tus ingresos y gastos entre dos períodos para identificar cambios en tus finanzas.
        </p>
      </div>

      <PeriodComparison
        defaultPeriod1="last_month"
        defaultPeriod2="current_month"
        defaultMode="total"
      />
    </div>
  );
};
```

## Manejo de Estados y Errores

### Estados a Manejar

1. **Cargando**: Muestra spinner o skeleton mientras se carga la comparación
2. **Sin datos en período 1**: Muestra mensaje específico
3. **Sin datos en período 2**: Muestra mensaje específico
4. **Sin datos en ambos**: Muestra mensaje general
5. **Error de validación**: Muestra error de formato de período
6. **Error de conexión**: Muestra error de red con opción de reintentar

### Ejemplo de Manejo de Errores Completo

```typescript
const handleComparison = async () => {
  try {
    setLoading(true);
    setError(null);

    if (!period1 || !period2) {
      setError('Debes seleccionar ambos períodos');
      return;
    }

    const response = await analyticsService.comparePeriods({
      period1,
      period2,
      mode,
    });

    if (!response.success) {
      switch (response.code) {
        case 'NO_DATA_PERIOD1':
          setError(`No hay información para el primer período (${period1})`);
          break;
        case 'NO_DATA_PERIOD2':
          setError(`No hay información para el segundo período (${period2})`);
          break;
        case 'NO_DATA_IN_PERIODS':
          setError('Ninguno de los períodos tiene transacciones');
          break;
        case 'MISSING_PERIODS':
          setError('Debes seleccionar ambos períodos');
          break;
        case 'INVALID_PERIOD_FORMAT':
          setError('Formato de período inválido');
          break;
        default:
          setError(response.error || 'Error desconocido');
      }
      setComparison(null);
    } else {
      setComparison(response.data);
      setError(null);
    }
  } catch (err: any) {
    if (err.message.includes('Network')) {
      setError('Error de conexión. Verifica tu internet e intenta nuevamente.');
    } else {
      setError(err.message || 'Error al realizar la comparación');
    }
    setComparison(null);
  } finally {
    setLoading(false);
  }
};
```

## Consideraciones Importantes

### 1. Formato de Montos

Los montos vienen en **centavos** desde el backend, pero el backend ya envía campos `formatted` que puedes usar directamente. Si necesitas formatear manualmente:

```typescript
const formatAmount = (amountInCents: number): string => {
  const pesos = amountInCents / 100;
  return `$${pesos.toLocaleString('es-CO')}`;
};
```

### 2. Lógica de Colores

- **Ingresos**: Verde para aumento, rojo para disminución
- **Gastos**: Rojo para aumento, verde para disminución (lógica invertida)
- **Balance**: Azul para positivo, naranja para negativo

### 3. Indicadores Visuales

- Usa flechas (↑↓) o iconos para mostrar dirección del cambio
- Usa colores consistentes con la lógica financiera
- Destaca cambios significativos (>= 5%)

### 4. Selectores de Período

Puedes usar:
- Selectores simples con opciones predefinidas
- Calendarios para selección de fechas personalizadas
- Inputs de texto para formatos específicos (YYYY-MM)

### 5. Actualización Automática

Cuando cambies período o modo, la comparación debe actualizarse automáticamente:

```typescript
useEffect(() => {
  if (period1 && period2) {
    loadComparison();
  }
}, [period1, period2, mode]);
```

## Ejemplos de Uso

### Ejemplo 1: Comparación Simple

```typescript
<SimplePeriodComparison />
```

### Ejemplo 2: Comparación Completa

```typescript
<PeriodComparison
  defaultPeriod1="2025-09"
  defaultPeriod2="2025-10"
  defaultMode="total"
/>
```

### Ejemplo 3: Integración en Dashboard

```typescript
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <AnalyticsDashboard period="current_month" mode="total" />
  <PeriodComparison
    defaultPeriod1="last_month"
    defaultPeriod2="current_month"
    defaultMode="total"
  />
</div>
```

## Checklist de Implementación

- [ ] Extender `analyticsService` con método `comparePeriods`
- [ ] Crear componente `PeriodComparison` o `SimplePeriodComparison`
- [ ] Implementar selectores de período
- [ ] Implementar toggle base/total
- [ ] Mostrar datos de ambos períodos lado a lado
- [ ] Mostrar diferencias con indicadores visuales
- [ ] Mostrar porcentajes y valores absolutos
- [ ] Manejar casos sin datos (período 1, período 2, ambos)
- [ ] Manejar errores de validación
- [ ] Mostrar insights automáticos
- [ ] Agregar gráfico de comparación (opcional)
- [ ] Probar con diferentes períodos
- [ ] Probar con períodos sin datos
- [ ] Verificar formato de montos
- [ ] Optimizar rendimiento

## Notas Finales

- El backend valida automáticamente que los períodos existan y tengan formato válido
- Los cálculos son consistentes: usa el mismo modo (base/total) para ambos períodos
- Las diferencias se calculan como: `period2 - period1`
- Los porcentajes se calculan basándose en el valor del período 1
- Un cambio se considera significativo si es >= 5%
- El backend excluye automáticamente las transferencias de los cálculos
- Los insights se generan automáticamente según los cambios detectados

