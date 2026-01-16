# SpennX Dashboard API - Testing Guide

## Base URL
```
http://localhost:8000
```

## Quick Test Commands (cURL)

### 1. Health Check
```bash
curl http://localhost:8000/
```

### 2. Dashboard Stats
```bash
curl http://localhost:8000/api/dashboard/stats
```

### 3. Transactions Live View (All Time Intervals)
```bash
curl http://localhost:8000/api/live-view
```

### 4. Transaction Pulse (Real-time Metrics)
```bash
curl http://localhost:8000/api/transaction-pulse
```

### 5. Net Income Statistics
```bash
curl http://localhost:8000/api/net-income
```

### 6. Get All Transactions (Paginated)
```bash
curl "http://localhost:8000/api/transactions?skip=0&limit=50"
```

### 7. Get Transactions by Date Range
```bash
# Using date only (YYYY-MM-DD)
curl "http://localhost:8000/api/transactions?start_date=2024-01-01&end_date=2024-01-31&limit=50"

# Using date and time (YYYY-MM-DD HH:MM:SS)
curl "http://localhost:8000/api/transactions?start_date=2024-01-15%2009:00:00&end_date=2024-01-15%2018:00:00&limit=50"

# Combine with status filter
curl "http://localhost:8000/api/transactions?start_date=2024-01-01&end_date=2024-01-31&status=success&limit=100"
```

### 8. Get Transactions by Status
```bash
# Completed transactions
curl "http://localhost:8000/api/transactions?status=completed&limit=50"

# Pending transactions
curl "http://localhost:8000/api/transactions?status=pending&limit=50"

# Failed transactions
curl "http://localhost:8000/api/transactions?status=failed&limit=50"
```

### 9. Get Transactions by Time Interval
```bash
# Today's transactions
curl "http://localhost:8000/api/transactions?interval=today&limit=50"

# Previous day
curl "http://localhost:8000/api/transactions?interval=previous_day&limit=50"

# Current week
curl "http://localhost:8000/api/transactions?interval=current_week&limit=50"

# Previous week
curl "http://localhost:8000/api/transactions?interval=previous_week&limit=50"

# Current month
curl "http://localhost:8000/api/transactions?interval=current_month&limit=50"

# Previous month
curl "http://localhost:8000/api/transactions?interval=previous_month&limit=50"

# Year to date
curl "http://localhost:8000/api/transactions?interval=year_to_date&limit=50"
```

### 10. Combined Filters (Status + Time Interval)
```bash
# Today's completed transactions
curl "http://localhost:8000/api/transactions?interval=today&status=success&limit=100"

# This week's pending transactions
curl "http://localhost:8000/api/transactions?interval=current_week&status=pending&limit=100"
```

### 11. Custom Date Range Analytics
```bash
# Get analytics for January 2024
curl "http://localhost:8000/api/analytics/custom-range?start_date=2024-01-01&end_date=2024-01-31"

# Get analytics for a specific week
curl "http://localhost:8000/api/analytics/custom-range?start_date=2024-01-15&end_date=2024-01-21"

# Get analytics with time precision
curl "http://localhost:8000/api/analytics/custom-range?start_date=2024-01-15%2009:00:00&end_date=2024-01-15%2018:00:00"
```

### 12. Get Specific Transaction by ID
```bash
curl "http://localhost:8000/api/transactions/YOUR_TRANSACTION_ID"
```

### 13. Get Transactions by Status (Alternative Endpoint)
```bash
# Pending
curl "http://localhost:8000/api/transactions/status/pending?limit=50"

# Failed
curl "http://localhost:8000/api/transactions/status/failed?limit=50"

# With date range
curl "http://localhost:8000/api/transactions/status/success?start_date=2024-01-01&end_date=2024-01-31"
```

## Date Range Filtering

### Supported Date Formats

1. **Date Only** (YYYY-MM-DD)
   - Example: `2024-01-15`
   - When used as end_date, automatically sets time to 23:59:59

2. **Date and Time** (YYYY-MM-DD HH:MM:SS)
   - Example: `2024-01-15 14:30:00`
   - Provides precise time filtering

### Date Range Examples

```bash
# Last 7 days
curl "http://localhost:8000/api/transactions?start_date=2024-01-08&end_date=2024-01-15"

# Specific month
curl "http://localhost:8000/api/transactions?start_date=2024-01-01&end_date=2024-01-31"

# Business hours only (9 AM to 6 PM)
curl "http://localhost:8000/api/transactions?start_date=2024-01-15%2009:00:00&end_date=2024-01-15%2018:00:00"

# Year to date (manual)
curl "http://localhost:8000/api/transactions?start_date=2024-01-01&end_date=2024-12-31"

# Get analytics for custom range
curl "http://localhost:8000/api/analytics/custom-range?start_date=2024-01-01&end_date=2024-01-31"
```

### Priority of Filters

When multiple filters are provided:
1. **Custom date range** (start_date/end_date) takes highest priority
2. **Predefined interval** (today, current_week, etc.) is used if no custom dates
3. **Status filter** works with both date ranges and intervals

## Pretty Print JSON (with jq)
If you have `jq` installed, you can format the output:

```bash
curl http://localhost:8000/api/live-view | jq '.'
curl http://localhost:8000/api/transaction-pulse | jq '.'
curl http://localhost:8000/api/net-income | jq '.'
```

## Interactive API Documentation

### Swagger UI
Open in browser: http://localhost:8000/docs

### ReDoc
Open in browser: http://localhost:8000/redoc

## Postman Collection

Import the `SpennX_Dashboard_API.postman_collection.json` file into Postman to test all endpoints with a nice UI.

### Steps to Import:
1. Open Postman
2. Click "Import" button
3. Select the `SpennX_Dashboard_API.postman_collection.json` file
4. All endpoints will be available in the collection

## Time Intervals Available

- `today` - Today (resets at 23:59)
- `previous_day` - Previous day (00:00–23:59)
- `current_week` - Current week (Monday 00:00 – Sunday 23:59)
- `previous_week` - Previous week
- `current_month` - Current month (from 1st 00:00 – last day 23:59)
- `previous_month` - Previous month
- `year_to_date` - Year to date (from January 1st 00:00 – current day 23:59)

## Status Values

- `pending` - Transaction is pending
- `completed` - Transaction completed successfully
- `failed` - Transaction failed
- `declined` - Transaction was declined

## Response Examples

### Live View Response Structure
```json
{
  "today": {
    "period_name": "Today",
    "start_date": "2026-01-14T00:00:00",
    "end_date": "2026-01-14T23:59:59",
    "total_transactions": 150,
    "total_volume": 45000.50,
    "total_revenue": 1250.75,
    "net_revenue": 1219.48,
    "avg_transaction_amount": 300.00,
    "avg_revenue_per_transaction": 8.34,
    "error_rate": 2.5
  },
  "previous_day": { ... },
  "current_week": { ... },
  ...
}
```

### Transaction Pulse Response
```json
{
  "transactions_per_minute": 2.5,
  "transactions_per_hour": 150,
  "transactions_per_day": 3600,
  "transaction_volume_usd": 1080000.00,
  "avg_transaction_size": 300.00,
  "error_rate": 2.5,
  "active_users_today": 450,
  "active_users_week": 2100,
  "active_users_month": 8500,
  "new_users_today": 45
}
```

### Net Income Response
```json
{
  "income_per_minute": 25.50,
  "income_per_hour": 1530.00,
  "income_per_day": 36720.00,
  "total_value_moved_usd": 1080000.00,
  "avg_amount_sent": 300.00,
  "error_rate": 2.5,
  "top_countries": [
    {
      "country": "United States",
      "currency": null,
      "volume": 450000.00,
      "transaction_count": 1500
    }
  ],
  "top_currencies": [
    {
      "country": null,
      "currency": "USD",
      "volume": 800000.00,
      "transaction_count": 2667
    }
  ],
  "accumulated_revenue_ytd": 520000.00
}
```
