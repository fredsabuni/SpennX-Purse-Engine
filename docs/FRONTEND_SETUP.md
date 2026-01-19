# SpennX Live Pulse Dashboard - Frontend Setup Guide

## Recommended Tech Stack

### Core Framework
- **Next.js 14+** (App Router) - React framework with SSR/SSG
- **TypeScript** - Type safety for API responses

### Data Fetching & State Management
- **TanStack Query (React Query)** - Best for API data fetching, caching, and real-time updates
- **Axios** - HTTP client for API calls

### Charts & Visualization
- **Recharts** - Simple, composable charts (Recommended for ease of use)
- **Chart.js with react-chartjs-2** - Powerful and flexible
- **Tremor** - Pre-built dashboard components with charts
- **shadcn/ui** - Beautiful UI components

### UI Components
- **shadcn/ui** - Customizable component library
- **Tailwind CSS** - Utility-first CSS
- **Lucide React** - Icons

### Real-time Updates
- **TanStack Query** with polling/refetch intervals

---

## Step 1: Create Next.js Project

```bash
npx create-next-app@latest spennx-dashboard
# Choose:
# ✅ TypeScript
# ✅ ESLint
# ✅ Tailwind CSS
# ✅ App Router
# ✅ src/ directory (optional)
# ❌ Turbopack (optional)

cd spennx-dashboard
```

---

## Step 2: Install Dependencies

```bash
# Core dependencies
npm install @tanstack/react-query axios

# Charts (choose one or use multiple)
npm install recharts
# OR
npm install chart.js react-chartjs-2
# OR
npm install @tremor/react

# UI Components
npm install @radix-ui/react-slot class-variance-authority clsx tailwind-merge
npm install lucide-react

# Date handling
npm install date-fns

# Optional: shadcn/ui setup
npx shadcn-ui@latest init
```

---

## Step 3: Project Structure

```
spennx-dashboard/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── dashboard/
│   │       ├── page.tsx
│   │       ├── live-view/
│   │       ├── pulse/
│   │       └── income/
│   ├── components/
│   │   ├── ui/              # shadcn components
│   │   ├── charts/          # Chart components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   └── layout/          # Layout components
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── types.ts         # TypeScript types
│   │   └── utils.ts         # Utility functions
│   └── hooks/
│       └── useSpennxData.ts # Custom hooks for data fetching
├── public/
└── package.json
```

---

## Step 4: Setup API Client

### `src/lib/api.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const spennxApi = {
  // Dashboard Stats
  getDashboardStats: () => apiClient.get('/api/dashboard/stats'),
  
  // Live View (all time intervals)
  getLiveView: () => apiClient.get('/api/live-view'),
  
  // Transaction Pulse (real-time)
  getTransactionPulse: () => apiClient.get('/api/transaction-pulse'),
  
  // Net Income
  getNetIncome: () => apiClient.get('/api/net-income'),
  
  // Transactions
  getTransactions: (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    interval?: string;
  }) => apiClient.get('/api/transactions', { params }),
  
  // Single transaction
  getTransaction: (id: string) => apiClient.get(`/api/transactions/${id}`),
  
  // Transactions by status
  getTransactionsByStatus: (status: string, params?: {
    skip?: number;
    limit?: number;
  }) => apiClient.get(`/api/transactions/status/${status}`, { params }),
};
```

---

## Step 5: TypeScript Types

### `src/lib/types.ts`

```typescript
export interface DashboardStats {
  total_transactions: number;
  total_volume: number;
  pending_count: number;
  completed_count: number;
  failed_count: number;
  avg_transaction_amount: number;
}

export interface PeriodStats {
  period_name: string;
  start_date: string;
  end_date: string;
  total_transactions: number;
  total_volume: number;
  total_revenue: number;
  net_revenue: number;
  avg_transaction_amount: number;
  avg_revenue_per_transaction: number;
  error_rate: number;
}

export interface TransactionsLiveView {
  today: PeriodStats;
  previous_day: PeriodStats;
  current_week: PeriodStats;
  previous_week: PeriodStats;
  current_month: PeriodStats;
  previous_month: PeriodStats;
  year_to_date: PeriodStats;
}

export interface TransactionPulse {
  transactions_per_minute: number;
  transactions_per_hour: number;
  transactions_per_day: number;
  transaction_volume_usd: number;
  avg_transaction_size: number;
  error_rate: number;
  active_users_today: number;
  active_users_week: number;
  active_users_month: number;
  new_users_today: number;
}

export interface CountryCurrencyVolume {
  country: string | null;
  currency: string | null;
  volume: number;
  transaction_count: number;
}

export interface NetIncomeStats {
  income_per_minute: number;
  income_per_hour: number;
  income_per_day: number;
  total_value_moved_usd: number;
  avg_amount_sent: number;
  error_rate: number;
  top_countries: CountryCurrencyVolume[];
  top_currencies: CountryCurrencyVolume[];
  accumulated_revenue_ytd: number;
}

export interface RecipientData {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  country?: string;
  currency_code?: string;
  bank_name?: string;
  account_number?: string;
}

export interface Transaction {
  id: string;
  amount: number;
  currency: string;
  human_readable_amount: number;
  charge: number;
  human_readable_charge: number;
  status: string;
  decline_reason?: string;
  mode: string;
  type: string;
  description?: string;
  created_at: string;
  recipient?: RecipientData;
}
```

---

## Step 6: Custom Hooks with React Query

### `src/hooks/useSpennxData.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { spennxApi } from '@/lib/api';
import type {
  DashboardStats,
  TransactionsLiveView,
  TransactionPulse,
  NetIncomeStats,
  Transaction,
} from '@/lib/types';

// Dashboard Stats
export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboardStats'],
    queryFn: async () => {
      const { data } = await spennxApi.getDashboardStats();
      return data as DashboardStats;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

// Live View
export const useLiveView = () => {
  return useQuery({
    queryKey: ['liveView'],
    queryFn: async () => {
      const { data } = await spennxApi.getLiveView();
      return data as TransactionsLiveView;
    },
    refetchInterval: 60000, // Refetch every minute
  });
};

// Transaction Pulse (Real-time)
export const useTransactionPulse = () => {
  return useQuery({
    queryKey: ['transactionPulse'],
    queryFn: async () => {
      const { data } = await spennxApi.getTransactionPulse();
      return data as TransactionPulse;
    },
    refetchInterval: 10000, // Refetch every 10 seconds for real-time feel
  });
};

// Net Income
export const useNetIncome = () => {
  return useQuery({
    queryKey: ['netIncome'],
    queryFn: async () => {
      const { data } = await spennxApi.getNetIncome();
      return data as NetIncomeStats;
    },
    refetchInterval: 30000,
  });
};

// Transactions
export const useTransactions = (params?: {
  skip?: number;
  limit?: number;
  status?: string;
  interval?: string;
}) => {
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: async () => {
      const { data } = await spennxApi.getTransactions(params);
      return data as Transaction[];
    },
    refetchInterval: 30000,
  });
};

// Single Transaction
export const useTransaction = (id: string) => {
  return useQuery({
    queryKey: ['transaction', id],
    queryFn: async () => {
      const { data } = await spennxApi.getTransaction(id);
      return data as Transaction;
    },
    enabled: !!id,
  });
};
```

---

## Step 7: Setup React Query Provider

### `src/app/providers.tsx`

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: true,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Update `src/app/layout.tsx`

```typescript
import { Providers } from './providers';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

---

## Step 8: Environment Variables

### `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 9: Example Dashboard Components

### `src/components/dashboard/StatsCard.tsx`

```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export function StatsCard({ title, value, icon: Icon, description, trend }: StatsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
        {trend && (
          <p className={`text-xs ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </p>
        )}
      </CardContent>
    </Card>
  );
}
```

### `src/components/charts/VolumeChart.tsx` (Using Recharts)

```typescript
'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface VolumeChartProps {
  data: Array<{
    name: string;
    volume: number;
    revenue: number;
  }>;
}

export function VolumeChart({ data }: VolumeChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Transaction Volume & Revenue</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip 
              formatter={(value: number) => `$${value.toLocaleString()}`}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="volume" 
              stroke="#8884d8" 
              strokeWidth={2}
              name="Volume"
            />
            <Line 
              type="monotone" 
              dataKey="revenue" 
              stroke="#82ca9d" 
              strokeWidth={2}
              name="Revenue"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

### `src/app/dashboard/page.tsx`

```typescript
'use client';

import { useDashboardStats, useLiveView, useTransactionPulse } from '@/hooks/useSpennxData';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { VolumeChart } from '@/components/charts/VolumeChart';
import { DollarSign, TrendingUp, Users, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: liveView, isLoading: liveViewLoading } = useLiveView();
  const { data: pulse, isLoading: pulseLoading } = useTransactionPulse();

  if (statsLoading || liveViewLoading || pulseLoading) {
    return <div>Loading...</div>;
  }

  // Prepare chart data
  const chartData = liveView ? [
    { name: 'Today', volume: liveView.today.total_volume, revenue: liveView.today.total_revenue },
    { name: 'Yesterday', volume: liveView.previous_day.total_volume, revenue: liveView.previous_day.total_revenue },
    { name: 'This Week', volume: liveView.current_week.total_volume, revenue: liveView.current_week.total_revenue },
    { name: 'Last Week', volume: liveView.previous_week.total_volume, revenue: liveView.previous_week.total_revenue },
    { name: 'This Month', volume: liveView.current_month.total_volume, revenue: liveView.current_month.total_revenue },
    { name: 'Last Month', volume: liveView.previous_month.total_volume, revenue: liveView.previous_month.total_revenue },
  ] : [];

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold">SpennX Live Pulse Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Volume"
          value={`$${stats?.total_volume.toLocaleString() || 0}`}
          icon={DollarSign}
          description="All successful transactions"
        />
        <StatsCard
          title="Total Transactions"
          value={stats?.total_transactions.toLocaleString() || 0}
          icon={TrendingUp}
          description={`${stats?.completed_count || 0} completed`}
        />
        <StatsCard
          title="Active Users Today"
          value={pulse?.active_users_today.toLocaleString() || 0}
          icon={Users}
          description={`${pulse?.new_users_today || 0} new users`}
        />
        <StatsCard
          title="Error Rate"
          value={`${pulse?.error_rate.toFixed(2) || 0}%`}
          icon={AlertCircle}
          description={`${stats?.failed_count || 0} failed transactions`}
        />
      </div>

      {/* Volume Chart */}
      <VolumeChart data={chartData} />

      {/* Real-time Pulse */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Transactions/Minute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{pulse?.transactions_per_minute || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Transactions/Hour</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{pulse?.transactions_per_hour || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Avg Transaction Size</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${pulse?.avg_transaction_size.toFixed(2) || 0}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

---

## Step 10: Run the Development Server

```bash
npm run dev
```

Visit `http://localhost:3000/dashboard`

---

## Best Practices

### 1. **Error Handling**
```typescript
const { data, isLoading, error } = useDashboardStats();

if (error) {
  return <ErrorComponent message={error.message} />;
}
```

### 2. **Loading States**
```typescript
if (isLoading) {
  return <Skeleton />;
}
```

### 3. **Real-time Updates**
- Use `refetchInterval` for polling
- Consider WebSockets for true real-time (future enhancement)

### 4. **Caching Strategy**
- React Query handles caching automatically
- Adjust `staleTime` based on data freshness needs

### 5. **Performance**
- Use `React.memo` for expensive components
- Implement virtual scrolling for large transaction lists
- Use Next.js Image optimization

---

## Recommended Chart Libraries Comparison

| Library | Pros | Cons | Best For |
|---------|------|------|----------|
| **Recharts** | Easy to use, composable, good docs | Limited customization | Quick dashboards |
| **Chart.js** | Very powerful, many chart types | More complex setup | Complex visualizations |
| **Tremor** | Pre-built dashboard components | Less flexible | Rapid prototyping |
| **Victory** | Highly customizable, React-native support | Steeper learning curve | Custom designs |

**Recommendation: Start with Recharts** for ease of use, then migrate to Chart.js if you need more advanced features.

---

## Next Steps

1. ✅ Setup authentication (if needed)
2. ✅ Add data export functionality (CSV, PDF)
3. ✅ Implement filters and date range pickers
4. ✅ Add transaction detail modals
5. ✅ Create mobile-responsive layouts
6. ✅ Add dark mode support
7. ✅ Implement WebSocket for real-time updates
8. ✅ Add notification system for alerts

---

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TanStack Query](https://tanstack.com/query/latest)
- [Recharts Documentation](https://recharts.org/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
