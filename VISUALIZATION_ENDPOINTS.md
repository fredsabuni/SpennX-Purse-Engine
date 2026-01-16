# SpennX Dashboard - Visualization Endpoints Guide

## New Endpoints for Frontend Visualizations

### 1. Transaction Overview Table
**Endpoint:** `GET /api/analytics/transaction-overview`

**Purpose:** Display comprehensive transaction data in a table with actual numbers

**Response:**
```json
{
  "total_transactions": 1500,
  "success_count": 1200,
  "success_rate": 80.00,
  "total_volume_usd": 450000.50,
  "total_revenue_usd": 12500.75,
  "avg_transaction_size": 375.00,
  "status_breakdown": {
    "success": {
      "count": 1200,
      "volume_usd": 450000.50,
      "revenue_usd": 12500.75,
      "percentage": 80.00
    },
    "pending": {
      "count": 150,
      "volume_usd": 45000.00,
      "revenue_usd": 1250.00,
      "percentage": 10.00
    },
    "failed": {
      "count": 100,
      "volume_usd": 0.00,
      "revenue_usd": 0.00,
      "percentage": 6.67
    },
    "declined": {
      "count": 30,
      "volume_usd": 0.00,
      "revenue_usd": 0.00,
      "percentage": 2.00
    },
    "reversed": {
      "count": 20,
      "volume_usd": 0.00,
      "revenue_usd": 0.00,
      "percentage": 1.33
    }
  }
}
```

**Use Cases:**
- ✅ Overview table showing all transaction statuses
- ✅ Status highlighting with actual numbers
- ✅ Volume and revenue by status
- ✅ Success rate calculation

**Example Requests:**
```bash
# All time
curl "http://localhost:8000/api/analytics/transaction-overview"

# Today only
curl "http://localhost:8000/api/analytics/transaction-overview?interval=today"

# Custom date range
curl "http://localhost:8000/api/analytics/transaction-overview?start_date=2024-01-01&end_date=2024-01-31"
```

---

### 2. Transaction Status Pie Chart
**Endpoint:** `GET /api/analytics/status-breakdown`

**Purpose:** Get transaction counts and percentages by status for pie chart

**Response:**
```json
{
  "total_transactions": 1500,
  "statuses": {
    "success": {
      "count": 1200,
      "percentage": 80.00
    },
    "pending": {
      "count": 150,
      "percentage": 10.00
    },
    "failed": {
      "count": 100,
      "percentage": 6.67
    },
    "declined": {
      "count": 30,
      "percentage": 2.00
    },
    "reversed": {
      "count": 20,
      "percentage": 1.33
    },
    "processing_swap": {
      "count": 0,
      "percentage": 0.00
    }
  }
}
```

**Use Cases:**
- ✅ Pie chart showing status distribution
- ✅ Donut chart with percentages
- ✅ Status comparison visualization

**Frontend Example (Recharts):**
```typescript
const data = Object.entries(statusBreakdown.statuses).map(([status, data]) => ({
  name: status,
  value: data.count,
  percentage: data.percentage
}));

<PieChart>
  <Pie data={data} dataKey="value" nameKey="name" />
</PieChart>
```

**Example Requests:**
```bash
# All time
curl "http://localhost:8000/api/analytics/status-breakdown"

# This week
curl "http://localhost:8000/api/analytics/status-breakdown?interval=current_week"

# Custom range
curl "http://localhost:8000/api/analytics/status-breakdown?start_date=2024-01-01&end_date=2024-01-31"
```

---

### 3. Currency Volume Bar/Line Chart
**Endpoint:** `GET /api/analytics/currency-breakdown`

**Purpose:** Get transaction volume by currency for bar/line charts

**Response:**
```json
[
  {
    "currency": "USD",
    "transaction_count": 500,
    "total_volume": 150000.00,
    "total_volume_usd": 150000.00,
    "avg_transaction_size": 300.00,
    "percentage_of_total": 45.50
  },
  {
    "currency": "NGN",
    "transaction_count": 400,
    "total_volume": 57344760.00,
    "total_volume_usd": 40000.00,
    "avg_transaction_size": 143361.90,
    "percentage_of_total": 12.12
  },
  {
    "currency": "KES",
    "transaction_count": 300,
    "total_volume": 3759084.54,
    "total_volume_usd": 30000.00,
    "avg_transaction_size": 12530.28,
    "percentage_of_total": 9.09
  },
  {
    "currency": "EUR",
    "transaction_count": 200,
    "total_volume": 16652.45,
    "total_volume_usd": 20000.00,
    "avg_transaction_size": 83.26,
    "percentage_of_total": 6.06
  },
  {
    "currency": "GBP",
    "transaction_count": 100,
    "total_volume": 7213.85,
    "total_volume_usd": 10000.00,
    "avg_transaction_size": 72.14,
    "percentage_of_total": 3.03
  }
]
```

**Use Cases:**
- ✅ Bar chart showing volume by currency
- ✅ Line chart showing currency trends
- ✅ Currency distribution analysis
- ✅ Compare transaction counts across currencies

**Frontend Example (Recharts):**
```typescript
// Bar Chart
<BarChart data={currencyBreakdown}>
  <XAxis dataKey="currency" />
  <YAxis />
  <Bar dataKey="total_volume_usd" fill="#8884d8" />
  <Bar dataKey="transaction_count" fill="#82ca9d" />
</BarChart>

// Line Chart (for trends over time - combine with date filtering)
<LineChart data={currencyBreakdown}>
  <XAxis dataKey="currency" />
  <YAxis />
  <Line type="monotone" dataKey="total_volume_usd" stroke="#8884d8" />
</LineChart>
```

**Example Requests:**
```bash
# All successful transactions (default)
curl "http://localhost:8000/api/analytics/currency-breakdown"

# Today only
curl "http://localhost:8000/api/analytics/currency-breakdown?interval=today"

# Include all statuses
curl "http://localhost:8000/api/analytics/currency-breakdown?status=all"

# Custom date range
curl "http://localhost:8000/api/analytics/currency-breakdown?start_date=2024-01-01&end_date=2024-01-31"
```

---

## Summary: Which Endpoint for Which Visualization?

| Visualization | Endpoint | Key Data |
|--------------|----------|----------|
| **Overview Table** | `/api/analytics/transaction-overview` | All statuses with counts, volumes, percentages |
| **Pie Chart** | `/api/analytics/status-breakdown` | Status distribution with percentages |
| **Bar Chart (Currency)** | `/api/analytics/currency-breakdown` | Volume by currency in USD |
| **Line Chart (Currency)** | `/api/analytics/currency-breakdown` | Same data, visualized as trends |
| **Transaction List** | `/api/transactions` | Individual transactions with all details |

---

## Common Query Parameters

All analytics endpoints support:

- `start_date` - Custom start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `end_date` - Custom end date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `interval` - Predefined intervals:
  - `today`
  - `previous_day`
  - `current_week`
  - `previous_week`
  - `current_month`
  - `previous_month`
  - `year_to_date`

---

## Frontend Implementation Examples

### 1. Transaction Overview Table (React)

```typescript
import { useQuery } from '@tanstack/react-query';

function TransactionOverviewTable() {
  const { data } = useQuery({
    queryKey: ['transaction-overview'],
    queryFn: () => fetch('/api/analytics/transaction-overview').then(r => r.json())
  });

  return (
    <table>
      <thead>
        <tr>
          <th>Status</th>
          <th>Count</th>
          <th>Volume (USD)</th>
          <th>Revenue (USD)</th>
          <th>Percentage</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(data?.status_breakdown || {}).map(([status, metrics]) => (
          <tr key={status} className={status === 'success' ? 'bg-green-50' : ''}>
            <td className="font-semibold">{status.toUpperCase()}</td>
            <td>{metrics.count}</td>
            <td>${metrics.volume_usd}</td>
            <td>${metrics.revenue_usd}</td>
            <td>{metrics.percentage}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### 2. Status Pie Chart (Recharts)

```typescript
import { PieChart, Pie, Cell, Legend, Tooltip } from 'recharts';

const COLORS = {
  success: '#10b981',
  pending: '#f59e0b',
  failed: '#ef4444',
  declined: '#dc2626',
  reversed: '#9333ea',
  processing_swap: '#6366f1'
};

function StatusPieChart() {
  const { data } = useQuery({
    queryKey: ['status-breakdown'],
    queryFn: () => fetch('/api/analytics/status-breakdown').then(r => r.json())
  });

  const chartData = Object.entries(data?.statuses || {})
    .filter(([_, metrics]) => metrics.count > 0)
    .map(([status, metrics]) => ({
      name: status,
      value: metrics.count,
      percentage: metrics.percentage
    }));

  return (
    <PieChart width={400} height={400}>
      <Pie
        data={chartData}
        dataKey="value"
        nameKey="name"
        cx="50%"
        cy="50%"
        outerRadius={100}
        label={({ name, percentage }) => `${name}: ${percentage}%`}
      >
        {chartData.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
        ))}
      </Pie>
      <Tooltip />
      <Legend />
    </PieChart>
  );
}
```

### 3. Currency Bar Chart (Recharts)

```typescript
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function CurrencyBarChart() {
  const { data } = useQuery({
    queryKey: ['currency-breakdown'],
    queryFn: () => fetch('/api/analytics/currency-breakdown').then(r => r.json())
  });

  return (
    <BarChart width={600} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="currency" />
      <YAxis />
      <Tooltip 
        formatter={(value: number) => `$${value.toLocaleString()}`}
      />
      <Legend />
      <Bar dataKey="total_volume_usd" fill="#8884d8" name="Volume (USD)" />
      <Bar dataKey="transaction_count" fill="#82ca9d" name="Transactions" />
    </BarChart>
  );
}
```

---

## Testing the Endpoints

```bash
# Test all three endpoints
curl "http://localhost:8000/api/analytics/transaction-overview?interval=today"
curl "http://localhost:8000/api/analytics/status-breakdown?interval=today"
curl "http://localhost:8000/api/analytics/currency-breakdown?interval=today"

# With custom date range
curl "http://localhost:8000/api/analytics/transaction-overview?start_date=2024-01-01&end_date=2024-01-31"
curl "http://localhost:8000/api/analytics/status-breakdown?start_date=2024-01-01&end_date=2024-01-31"
curl "http://localhost:8000/api/analytics/currency-breakdown?start_date=2024-01-01&end_date=2024-01-31"
```

---

## All Available Endpoints Summary

1. ✅ `/api/dashboard/stats` - Overall stats
2. ✅ `/api/live-view` - All time intervals
3. ✅ `/api/transaction-pulse` - Real-time metrics
4. ✅ `/api/net-income` - Income statistics
5. ✅ `/api/transactions` - Transaction list with filters
6. ✅ `/api/transactions/{id}` - Single transaction
7. ✅ `/api/transactions/status/{status}` - By status
8. ✅ `/api/analytics/custom-range` - Custom date analytics
9. ✅ **NEW** `/api/analytics/transaction-overview` - Overview table data
10. ✅ **NEW** `/api/analytics/status-breakdown` - Pie chart data
11. ✅ **NEW** `/api/analytics/currency-breakdown` - Bar/line chart data

You now have everything you need to build comprehensive visualizations! 🎉
