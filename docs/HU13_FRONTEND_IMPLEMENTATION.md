# HU-13 — Indicadores y Gráficos del Período - Guía Frontend

## Resumen

Esta guía explica cómo implementar en el frontend la visualización de indicadores financieros y gráficos del período, con soporte para alternar entre valores base y totales (con impuestos).

## Endpoints Disponibles

### 1. Dashboard Completo (Recomendado)

Obtiene todos los datos en una sola llamada: indicadores, gráfico dona y gráfico líneas.

```
GET /api/analytics/dashboard/
```

**Query Parameters:**
- `period` - Período de análisis (default: `current_month`)
  - Valores predefinidos: `current_month`, `last_month`, `current_year`, `last_7_days`, `last_30_days`
  - Mes específico: `YYYY-MM` (ej: `2025-10`)
  - Año específico: `YYYY` (ej: `2025`)
  - Rango personalizado: `YYYY-MM-DD,YYYY-MM-DD` (ej: `2025-01-01,2025-01-31`)
- `mode` - Modo de cálculo (default: `total`)
  - `base` - Solo montos base (sin impuestos)
  - `total` - Montos totales (base + impuestos)
- `others_threshold` - % mínimo para categorías individuales (default: `0.05` = 5%)

**Ejemplo de Request:**
```typescript
GET /api/analytics/dashboard/?period=current_month&mode=total&others_threshold=0.05
```

**Respuesta Exitosa:**
```json
{
  "success": true,
  "data": {
    "indicators": {
      "income": {
        "amount": 5000000,
        "count": 12,
        "formatted": "$5,000,000"
      },
      "expenses": {
        "amount": 3200000,
        "count": 45,
        "formatted": "$3,200,000"
      },
      "balance": {
        "amount": 1800000,
        "formatted": "$1,800,000",
        "is_positive": true
      },
      "period": {
        "start": "2025-11-01",
        "end": "2025-11-30",
        "days": 30
      },
      "mode": "total",
      "currency": "COP"
    },
    "expenses_chart": {
      "chart_data": [
        {
          "category_id": "5",
          "name": "Comida",
          "amount": 1200000,
          "count": 15,
          "percentage": 37.5,
          "color": "#EF4444",
          "icon": "fa-utensils",
          "formatted_amount": "$1,200,000"
        },
        {
          "category_id": "8",
          "name": "Transporte",
          "amount": 800000,
          "count": 20,
          "percentage": 25.0,
          "color": "#3B82F6",
          "icon": "fa-car",
          "formatted_amount": "$800,000"
        },
        {
          "category_id": "others",
          "name": "Otros",
          "amount": 1200000,
          "count": 10,
          "percentage": 37.5,
          "color": "#9CA3AF",
          "icon": "fa-ellipsis-h",
          "formatted_amount": "$1,200,000",
          "is_aggregated": true
        }
      ],
      "others_data": [
        {
          "category_id": "12",
          "name": "Entretenimiento",
          "amount": 600000,
          "count": 5,
          "percentage": 18.75,
          "color": "#8B5CF6",
          "icon": "fa-film",
          "formatted_amount": "$600,000"
        },
        {
          "category_id": "15",
          "name": "Salud",
          "amount": 600000,
          "count": 5,
          "percentage": 18.75,
          "color": "#10B981",
          "icon": "fa-heart",
          "formatted_amount": "$600,000"
        }
      ],
      "total_expenses": 3200000,
      "uncategorized_amount": 0,
      "mode": "total",
      "period_summary": "01/11 - 30/11",
      "categories_count": 5
    },
    "daily_flow_chart": {
      "dates": [
        "2025-11-01",
        "2025-11-02",
        "2025-11-03",
        ...
      ],
      "series": {
        "income": {
          "name": "Ingresos diarios",
          "data": [0, 500000, 0, 300000, ...],
          "color": "#10B981",
          "total": 5000000
        },
        "expenses": {
          "name": "Gastos diarios",
          "data": [150000, 200000, 100000, 180000, ...],
          "color": "#EF4444",
          "total": 3200000
        },
        "balance": {
          "name": "Balance acumulado",
          "data": [-150000, 150000, 50000, 170000, ...],
          "color": "#3B82F6",
          "final": 1800000
        }
      },
      "summary": {
        "period_days": 30,
        "total_income": 5000000,
        "total_expenses": 3200000,
        "final_balance": 1800000,
        "avg_daily_income": 166666.67,
        "avg_daily_expense": 106666.67
      },
      "mode": "total",
      "period": {
        "start": "2025-11-01",
        "end": "2025-11-30"
      }
    },
    "metadata": {
      "generated_at": "2025-11-30",
      "user_id": 1,
      "period_requested": "current_month",
      "mode_used": "total",
      "others_threshold": 0.05
    }
  },
  "message": "Analytics dashboard generado para período current_month en modo total"
}
```

**Respuesta Sin Datos:**
```json
{
  "success": false,
  "error": "No tienes transacciones registradas",
  "code": "NO_DATA_AVAILABLE",
  "details": {
    "message": "Para generar analytics necesitas al menos una transacción",
    "suggestions": [
      "Crea algunas transacciones de ingresos y gastos",
      "Asigna categorías a tus gastos para mejores gráficos"
    ]
  }
}
```

### 2. Indicadores Individuales (KPIs)

Obtiene solo los indicadores (ingresos, gastos, balance).

```
GET /api/analytics/indicators/
```

**Query Parameters:**
- `period` - Período (mismo formato que dashboard)
- `mode` - `base` o `total`

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "income": {
      "amount": 5000000,
      "count": 12,
      "formatted": "$5,000,000"
    },
    "expenses": {
      "amount": 3200000,
      "count": 45,
      "formatted": "$3,200,000"
    },
    "balance": {
      "amount": 1800000,
      "formatted": "$1,800,000",
      "is_positive": true
    },
    "period": {
      "start": "2025-11-01",
      "end": "2025-11-30",
      "days": 30
    },
    "mode": "total",
    "currency": "COP",
    "context": {
      "total_user_transactions": 150,
      "period_transactions": 57,
      "period_range": "01/11/2025 - 30/11/2025"
    }
  }
}
```

### 3. Gráfico de Dona por Categorías

Obtiene solo los datos del gráfico de dona.

```
GET /api/analytics/expenses-chart/
```

**Query Parameters:**
- `period` - Período
- `mode` - `base` o `total`
- `others_threshold` - % mínimo para categorías (default: 0.05)

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "chart_data": [...],
    "others_data": [...],
    "total_expenses": 3200000,
    "uncategorized_amount": 0,
    "mode": "total",
    "period_summary": "01/11 - 30/11",
    "categories_count": 5
  }
}
```

### 4. Gráfico de Líneas (Flujo Diario)

Obtiene solo los datos del gráfico de líneas.

```
GET /api/analytics/daily-flow-chart/
```

**Query Parameters:**
- `period` - Período
- `mode` - `base` o `total`

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "dates": ["2025-11-01", "2025-11-02", ...],
    "series": {
      "income": {...},
      "expenses": {...},
      "balance": {...}
    },
    "summary": {...},
    "mode": "total",
    "period": {...}
  }
}
```

### 5. Transacciones por Categoría (Drill-down)

Obtiene transacciones filtradas por categoría al hacer clic en la dona.

```
GET /api/analytics/category/{category_id}/transactions/
```

**Path Parameters:**
- `category_id` - ID de categoría (número) o `uncategorized` para sin categoría

**Query Parameters:**
- `period` - Período
- `mode` - `base` o `total`
- `limit` - Límite de transacciones (default: 50)

**Ejemplo:**
```
GET /api/analytics/category/5/transactions/?period=current_month&mode=total&limit=20
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": 123,
        "date": "2025-11-15",
        "description": "Almuerzo en restaurante",
        "amount": 45000,
        "formatted_amount": "$45,000",
        "account": "Cuenta Principal",
        "tag": "comida",
        "category": {
          "id": 5,
          "name": "Comida",
          "color": "#EF4444",
          "icon": "fa-utensils"
        }
      },
      ...
    ],
    "total_count": 15,
    "showing_count": 15,
    "category_name": "Comida",
    "total_amount": 1200000,
    "formatted_total": "$1,200,000",
    "period": {
      "start": "2025-11-01",
      "end": "2025-11-30"
    },
    "mode": "total",
    "has_more": false
  }
}
```

### 6. Períodos Disponibles

Obtiene lista de períodos sugeridos.

```
GET /api/analytics/periods/
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "available_periods": [
      {
        "key": "current_month",
        "name": "Mes actual",
        "description": "November 2025"
      },
      {
        "key": "last_month",
        "name": "Mes anterior",
        "description": "Mes completo anterior"
      },
      ...
    ],
    "data_range": {
      "min_date": "2024-01-15",
      "max_date": "2025-11-30"
    }
  }
}
```

## Implementación Frontend

### 1. Servicio de Analytics

```typescript
// services/analyticsService.ts

interface DashboardParams {
  period?: string;
  mode?: 'base' | 'total';
  others_threshold?: number;
}

interface DashboardResponse {
  success: boolean;
  data: {
    indicators: {
      income: { amount: number; count: number; formatted: string };
      expenses: { amount: number; count: number; formatted: string };
      balance: { amount: number; formatted: string; is_positive: boolean };
      period: { start: string; end: string; days: number };
      mode: string;
      currency: string;
    };
    expenses_chart: {
      chart_data: Array<{
        category_id: string;
        name: string;
        amount: number;
        count: number;
        percentage: number;
        color: string;
        icon: string;
        formatted_amount: string;
        is_aggregated?: boolean;
      }>;
      others_data: Array<{...}>;
      total_expenses: number;
      uncategorized_amount: number;
      mode: string;
      period_summary: string;
      categories_count: number;
    };
    daily_flow_chart: {
      dates: string[];
      series: {
        income: { name: string; data: number[]; color: string; total: number };
        expenses: { name: string; data: number[]; color: string; total: number };
        balance: { name: string; data: number[]; color: string; final: number };
      };
      summary: {
        period_days: number;
        total_income: number;
        total_expenses: number;
        final_balance: number;
        avg_daily_income: number;
        avg_daily_expense: number;
      };
      mode: string;
      period: { start: string; end: string };
    };
    metadata: {
      generated_at: string;
      user_id: number;
      period_requested: string;
      mode_used: string;
      others_threshold: number;
    };
  };
  message?: string;
}

class AnalyticsService {
  private baseUrl = '/api/analytics';

  async getDashboard(params: DashboardParams = {}): Promise<DashboardResponse> {
    const queryParams = new URLSearchParams();
    if (params.period) queryParams.append('period', params.period);
    if (params.mode) queryParams.append('mode', params.mode);
    if (params.others_threshold !== undefined) {
      queryParams.append('others_threshold', params.others_threshold.toString());
    }

    const response = await fetch(
      `${this.baseUrl}/dashboard/?${queryParams.toString()}`,
      {
        headers: {
          'Authorization': `Token ${this.getToken()}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al obtener dashboard');
    }

    return response.json();
  }

  async getIndicators(period?: string, mode: 'base' | 'total' = 'total') {
    const queryParams = new URLSearchParams();
    if (period) queryParams.append('period', period);
    queryParams.append('mode', mode);

    const response = await fetch(
      `${this.baseUrl}/indicators/?${queryParams.toString()}`,
      {
        headers: {
          'Authorization': `Token ${this.getToken()}`,
        },
      }
    );

    return response.json();
  }

  async getExpensesChart(period?: string, mode: 'base' | 'total' = 'total', othersThreshold = 0.05) {
    const queryParams = new URLSearchParams();
    if (period) queryParams.append('period', period);
    queryParams.append('mode', mode);
    queryParams.append('others_threshold', othersThreshold.toString());

    const response = await fetch(
      `${this.baseUrl}/expenses-chart/?${queryParams.toString()}`,
      {
        headers: {
          'Authorization': `Token ${this.getToken()}`,
        },
      }
    );

    return response.json();
  }

  async getDailyFlowChart(period?: string, mode: 'base' | 'total' = 'total') {
    const queryParams = new URLSearchParams();
    if (period) queryParams.append('period', period);
    queryParams.append('mode', mode);

    const response = await fetch(
      `${this.baseUrl}/daily-flow-chart/?${queryParams.toString()}`,
      {
        headers: {
          'Authorization': `Token ${this.getToken()}`,
        },
      }
    );

    return response.json();
  }

  async getCategoryTransactions(
    categoryId: string | number,
    period?: string,
    mode: 'base' | 'total' = 'total',
    limit = 50
  ) {
    const queryParams = new URLSearchParams();
    if (period) queryParams.append('period', period);
    queryParams.append('mode', mode);
    queryParams.append('limit', limit.toString());

    const response = await fetch(
      `${this.baseUrl}/category/${categoryId}/transactions/?${queryParams.toString()}`,
      {
        headers: {
          'Authorization': `Token ${this.getToken()}`,
        },
      }
    );

    return response.json();
  }

  async getAvailablePeriods() {
    const response = await fetch(`${this.baseUrl}/periods/`, {
      headers: {
        'Authorization': `Token ${this.getToken()}`,
      },
    });

    return response.json();
  }

  private getToken(): string {
    return localStorage.getItem('authToken') || '';
  }
}

export const analyticsService = new AnalyticsService();
```

### 2. Componente de Indicadores (KPIs)

```typescript
// components/AnalyticsIndicators.tsx

import React from 'react';
import { analyticsService } from '../services/analyticsService';

interface AnalyticsIndicatorsProps {
  period: string;
  mode: 'base' | 'total';
}

export const AnalyticsIndicators: React.FC<AnalyticsIndicatorsProps> = ({
  period,
  mode,
}) => {
  const [indicators, setIndicators] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    loadIndicators();
  }, [period, mode]);

  const loadIndicators = async () => {
    try {
      setLoading(true);
      const response = await analyticsService.getIndicators(period, mode);
      if (response.success) {
        setIndicators(response.data);
      }
    } catch (error) {
      console.error('Error cargando indicadores:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Cargando indicadores...</div>;
  }

  if (!indicators) {
    return <div>No hay datos disponibles</div>;
  }

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="bg-green-50 p-6 rounded-lg border border-green-200">
        <div className="text-sm text-green-600 font-medium">Ingresos</div>
        <div className="text-2xl font-bold text-green-700 mt-2">
          {indicators.income.formatted}
        </div>
        <div className="text-xs text-green-500 mt-1">
          {indicators.income.count} transacciones
        </div>
      </div>

      <div className="bg-red-50 p-6 rounded-lg border border-red-200">
        <div className="text-sm text-red-600 font-medium">Gastos</div>
        <div className="text-2xl font-bold text-red-700 mt-2">
          {indicators.expenses.formatted}
        </div>
        <div className="text-xs text-red-500 mt-1">
          {indicators.expenses.count} transacciones
        </div>
      </div>

      <div
        className={`p-6 rounded-lg border ${
          indicators.balance.is_positive
            ? 'bg-blue-50 border-blue-200'
            : 'bg-orange-50 border-orange-200'
        }`}
      >
        <div
          className={`text-sm font-medium ${
            indicators.balance.is_positive ? 'text-blue-600' : 'text-orange-600'
          }`}
        >
          Balance
        </div>
        <div
          className={`text-2xl font-bold mt-2 ${
            indicators.balance.is_positive ? 'text-blue-700' : 'text-orange-700'
          }`}
        >
          {indicators.balance.formatted}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          {indicators.period.days} días
        </div>
      </div>
    </div>
  );
};
```

### 3. Componente de Gráfico de Dona

```typescript
// components/ExpensesDonutChart.tsx

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { analyticsService } from '../services/analyticsService';

interface ExpensesDonutChartProps {
  period: string;
  mode: 'base' | 'total';
  onCategoryClick?: (categoryId: string) => void;
}

export const ExpensesDonutChart: React.FC<ExpensesDonutChartProps> = ({
  period,
  mode,
  onCategoryClick,
}) => {
  const [chartData, setChartData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    loadChartData();
  }, [period, mode]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      const response = await analyticsService.getExpensesChart(period, mode);
      if (response.success) {
        setChartData(response.data);
      }
    } catch (error) {
      console.error('Error cargando gráfico:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Cargando gráfico...</div>;
  }

  if (!chartData || chartData.chart_data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No hay gastos categorizados en este período
      </div>
    );
  }

  const pieData = chartData.chart_data.map((item: any) => ({
    name: item.name,
    value: item.amount,
    percentage: item.percentage,
    categoryId: item.category_id,
    color: item.color,
  }));

  const handleClick = (data: any) => {
    if (onCategoryClick && data.categoryId !== 'others') {
      onCategoryClick(data.categoryId);
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-semibold">{data.name}</p>
          <p className="text-sm text-gray-600">
            {data.payload.formatted_amount || `$${data.value.toLocaleString()}`}
          </p>
          <p className="text-xs text-gray-500">
            {data.payload.percentage.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (percent < 0.05) return null;

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-xs font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Gastos por Categoría</h3>
        <p className="text-sm text-gray-500">
          {chartData.period_summary} • Total: ${chartData.total_expenses.toLocaleString()}
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={CustomLabel}
            outerRadius={120}
            innerRadius={60}
            fill="#8884d8"
            dataKey="value"
            onClick={handleClick}
            style={{ cursor: 'pointer' }}
          >
            {pieData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry: any) => {
              const item = pieData.find((d: any) => d.name === value);
              return `${value} (${item?.percentage.toFixed(1)}%)`;
            }}
          />
        </PieChart>
      </ResponsiveContainer>

      {chartData.others_data && chartData.others_data.length > 0 && (
        <div className="mt-4 p-3 bg-gray-50 rounded text-sm">
          <p className="font-medium mb-2">Categorías en "Otros":</p>
          <ul className="space-y-1">
            {chartData.others_data.map((item: any) => (
              <li key={item.category_id} className="flex justify-between">
                <span>{item.name}</span>
                <span className="font-medium">{item.formatted_amount}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
```

### 4. Componente de Gráfico de Líneas

```typescript
// components/DailyFlowChart.tsx

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { analyticsService } from '../services/analyticsService';

interface DailyFlowChartProps {
  period: string;
  mode: 'base' | 'total';
}

export const DailyFlowChart: React.FC<DailyFlowChartProps> = ({
  period,
  mode,
}) => {
  const [chartData, setChartData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    loadChartData();
  }, [period, mode]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      const response = await analyticsService.getDailyFlowChart(period, mode);
      if (response.success) {
        setChartData(response.data);
      }
    } catch (error) {
      console.error('Error cargando gráfico:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Cargando gráfico...</div>;
  }

  if (!chartData || chartData.dates.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No hay datos para este período
      </div>
    );
  }

  const formattedData = chartData.dates.map((date: string, index: number) => ({
    date: new Date(date).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
    }),
    ingresos: chartData.series.income.data[index],
    gastos: chartData.series.expenses.data[index],
    balance: chartData.series.balance.data[index],
  }));

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Flujo Diario</h3>
        <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
          <div>
            <span className="text-gray-500">Ingresos totales: </span>
            <span className="font-semibold text-green-600">
              ${chartData.summary.total_income.toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Gastos totales: </span>
            <span className="font-semibold text-red-600">
              ${chartData.summary.total_expenses.toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Balance final: </span>
            <span
              className={`font-semibold ${
                chartData.summary.final_balance >= 0
                  ? 'text-blue-600'
                  : 'text-orange-600'
              }`}
            >
              ${chartData.summary.final_balance.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            angle={-45}
            textAnchor="end"
            height={80}
            interval="preserveStartEnd"
          />
          <YAxis />
          <Tooltip
            formatter={(value: number) => `$${value.toLocaleString()}`}
            labelFormatter={(label) => `Fecha: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="ingresos"
            stroke={chartData.series.income.color}
            strokeWidth={2}
            name={chartData.series.income.name}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="gastos"
            stroke={chartData.series.expenses.color}
            strokeWidth={2}
            name={chartData.series.expenses.name}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="balance"
            stroke={chartData.series.balance.color}
            strokeWidth={2}
            name={chartData.series.balance.name}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
```

### 5. Componente Principal del Dashboard

```typescript
// pages/AnalyticsDashboard.tsx

import React, { useState } from 'react';
import { AnalyticsIndicators } from '../components/AnalyticsIndicators';
import { ExpensesDonutChart } from '../components/ExpensesDonutChart';
import { DailyFlowChart } from '../components/DailyFlowChart';
import { CategoryTransactionsModal } from '../components/CategoryTransactionsModal';
import { analyticsService } from '../services/analyticsService';

export const AnalyticsDashboard: React.FC = () => {
  const [period, setPeriod] = useState('current_month');
  const [mode, setMode] = useState<'base' | 'total'>('total');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showTransactionsModal, setShowTransactionsModal] = useState(false);

  const handleCategoryClick = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setShowTransactionsModal(true);
  };

  const handlePeriodChange = (newPeriod: string) => {
    setPeriod(newPeriod);
  };

  const handleModeToggle = () => {
    setMode(mode === 'base' ? 'total' : 'base');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-4">Analytics Financieros</h1>

        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Período
            </label>
            <select
              value={period}
              onChange={(e) => handlePeriodChange(e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="current_month">Mes actual</option>
              <option value="last_month">Mes anterior</option>
              <option value="current_year">Año actual</option>
              <option value="last_7_days">Últimos 7 días</option>
              <option value="last_30_days">Últimos 30 días</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="block text-sm font-medium text-gray-700">
              Modo:
            </label>
            <button
              onClick={handleModeToggle}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                mode === 'base'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Solo Base
            </button>
            <button
              onClick={handleModeToggle}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                mode === 'total'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Base + Impuestos
            </button>
          </div>

          <div className="text-sm text-gray-500">
            {mode === 'base'
              ? 'Mostrando montos base (sin impuestos)'
              : 'Mostrando montos totales (con impuestos)'}
          </div>
        </div>
      </div>

      <div className="mb-8">
        <AnalyticsIndicators period={period} mode={mode} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <ExpensesDonutChart
            period={period}
            mode={mode}
            onCategoryClick={handleCategoryClick}
          />
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <DailyFlowChart period={period} mode={mode} />
        </div>
      </div>

      {showTransactionsModal && selectedCategory && (
        <CategoryTransactionsModal
          categoryId={selectedCategory}
          period={period}
          mode={mode}
          onClose={() => {
            setShowTransactionsModal(false);
            setSelectedCategory(null);
          }}
        />
      )}
    </div>
  );
};
```

### 6. Modal de Transacciones por Categoría

```typescript
// components/CategoryTransactionsModal.tsx

import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';

interface CategoryTransactionsModalProps {
  categoryId: string;
  period: string;
  mode: 'base' | 'total';
  onClose: () => void;
}

export const CategoryTransactionsModal: React.FC<CategoryTransactionsModalProps> = ({
  categoryId,
  period,
  mode,
  onClose,
}) => {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryInfo, setCategoryInfo] = useState<any>(null);

  useEffect(() => {
    loadTransactions();
  }, [categoryId, period, mode]);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const response = await analyticsService.getCategoryTransactions(
        categoryId,
        period,
        mode
      );
      if (response.success) {
        setTransactions(response.data.transactions);
        setCategoryInfo({
          name: response.data.category_name,
          total: response.data.formatted_total,
          count: response.data.total_count,
        });
      }
    } catch (error) {
      console.error('Error cargando transacciones:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold">
              Transacciones: {categoryInfo?.name || 'Cargando...'}
            </h2>
            {categoryInfo && (
              <p className="text-sm text-gray-500">
                {categoryInfo.count} transacciones • Total: {categoryInfo.total}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">Cargando transacciones...</div>
          ) : transactions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No hay transacciones en esta categoría para el período seleccionado
            </div>
          ) : (
            <div className="space-y-3">
              {transactions.map((tx) => (
                <div
                  key={tx.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-medium">{tx.description || 'Sin descripción'}</div>
                      <div className="text-sm text-gray-500 mt-1">
                        {new Date(tx.date).toLocaleDateString('es-ES', {
                          day: '2-digit',
                          month: 'long',
                          year: 'numeric',
                        })}
                      </div>
                      {tx.tag && (
                        <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                          {tx.tag}
                        </span>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-red-600">
                        {tx.formatted_amount}
                      </div>
                      <div className="text-xs text-gray-500">{tx.account}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
```

## Manejo de Estados y Errores

### Estados a Manejar

1. **Cargando**: Muestra skeleton o spinner mientras se cargan los datos
2. **Sin datos**: Muestra mensaje amigable cuando no hay transacciones
3. **Error**: Muestra mensaje de error con opción de reintentar
4. **Datos vacíos en período**: Muestra mensaje indicando que el período no tiene datos

### Ejemplo de Manejo de Errores

```typescript
const [error, setError] = useState<string | null>(null);

try {
  const response = await analyticsService.getDashboard({ period, mode });
  if (!response.success) {
    if (response.code === 'NO_DATA_AVAILABLE') {
      setError('No tienes transacciones registradas');
    } else if (response.code === 'INVALID_PERIOD') {
      setError('Período inválido');
    } else {
      setError(response.error || 'Error desconocido');
    }
  } else {
    setData(response.data);
    setError(null);
  }
} catch (err) {
  setError('Error de conexión. Intenta nuevamente.');
}
```

## Consideraciones Importantes

### 1. Formato de Montos

Los montos vienen en **centavos** desde el backend. Si necesitas mostrarlos en pesos:

```typescript
const formatAmount = (amountInCents: number): string => {
  const pesos = amountInCents / 100;
  return `$${pesos.toLocaleString('es-CO')}`;
};
```

Sin embargo, el backend ya envía `formatted` en algunos campos, que puedes usar directamente.

### 2. Actualización Automática

Cuando cambies el período o el modo, todos los componentes deben actualizarse automáticamente. Usa `useEffect` con dependencias:

```typescript
useEffect(() => {
  loadData();
}, [period, mode]);
```

### 3. Clic en Categorías

Al hacer clic en una categoría del gráfico de dona:
- Si `category_id === 'others'`: No hacer nada o mostrar mensaje
- Si `category_id === 'uncategorized'`: Usar `'uncategorized'` como ID
- Si es un número: Usar el número directamente

### 4. Librerías de Gráficos Recomendadas

- **Recharts** (React): Fácil de usar, buena documentación
- **Chart.js**: Popular, muchas opciones
- **ApexCharts**: Muy completo, buenos gráficos interactivos
- **Victory**: Buena para gráficos complejos

### 5. Optimización

- Usa el endpoint `/dashboard/` para cargar todo de una vez
- Cachea los datos si el usuario cambia rápidamente entre períodos
- Implementa debounce para cambios de período si usas input personalizado

## Ejemplo de Integración Completa

```typescript
// App.tsx o Router

import { AnalyticsDashboard } from './pages/AnalyticsDashboard';

function App() {
  return (
    <Routes>
      <Route path="/analytics" element={<AnalyticsDashboard />} />
      {/* otras rutas */}
    </Routes>
  );
}
```

## Checklist de Implementación

- [ ] Crear servicio `analyticsService.ts`
- [ ] Implementar componente `AnalyticsIndicators`
- [ ] Implementar componente `ExpensesDonutChart` con interacción
- [ ] Implementar componente `DailyFlowChart`
- [ ] Implementar componente principal `AnalyticsDashboard`
- [ ] Implementar modal `CategoryTransactionsModal`
- [ ] Agregar selector de período
- [ ] Agregar toggle base/total
- [ ] Manejar estados de carga y error
- [ ] Manejar casos sin datos
- [ ] Probar con diferentes períodos
- [ ] Probar clic en categorías
- [ ] Verificar formato de montos
- [ ] Optimizar rendimiento

## Notas Finales

- El backend excluye automáticamente las transferencias (type=3) de los cálculos
- Los gráficos se actualizan automáticamente al cambiar período o modo
- El modo `base` muestra solo `base_amount`, el modo `total` muestra `total_amount` (con impuestos)
- Las categorías pequeñas se agrupan en "Otros" según el `others_threshold` (default 5%)
- El drill-down muestra hasta 50 transacciones por defecto (configurable con `limit`)

