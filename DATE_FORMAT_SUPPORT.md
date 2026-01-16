# Date Format Support - Updated

## ✅ Now Supports ISO 8601 Format

The API now accepts date parameters in multiple formats, including the ISO 8601 format that JavaScript/TypeScript frontends typically send.

### Supported Date Formats

1. **ISO 8601 with milliseconds and timezone (Z)**
   - Format: `YYYY-MM-DDTHH:MM:SS.sssZ`
   - Example: `2025-12-31T21:00:00.000Z`
   - ✅ **This is what your frontend sends**

2. **ISO 8601 with timezone (Z)**
   - Format: `YYYY-MM-DDTHH:MM:SSZ`
   - Example: `2025-12-31T21:00:00Z`

3. **ISO 8601 without timezone**
   - Format: `YYYY-MM-DDTHH:MM:SS`
   - Example: `2025-12-31T21:00:00`

4. **Standard datetime format**
   - Format: `YYYY-MM-DD HH:MM:SS`
   - Example: `2025-12-31 21:00:00`

5. **Date only**
   - Format: `YYYY-MM-DD`
   - Example: `2025-12-31`
   - Note: When used as `end_date`, automatically sets time to 23:59:59

---

## Frontend Integration

### No Changes Needed!

Your frontend can continue sending dates in ISO 8601 format (the JavaScript standard):

```typescript
// JavaScript Date object
const startDate = new Date('2025-12-31');
const endDate = new Date('2026-01-14');

// Convert to ISO string (automatically includes timezone)
const params = {
  start_date: startDate.toISOString(), // "2025-12-31T21:00:00.000Z"
  end_date: endDate.toISOString()      // "2026-01-14T21:00:00.000Z"
};

// Make API call
fetch(`/api/analytics/currency-breakdown?start_date=${params.start_date}&end_date=${params.end_date}`);
```

### React Query Example

```typescript
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';

export const useCurrencyBreakdown = (startDate: Date, endDate: Date) => {
  return useQuery({
    queryKey: ['currency-breakdown', startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString()
      });
      
      const response = await fetch(`/api/analytics/currency-breakdown?${params}`);
      return response.json();
    }
  });
};
```

### Date Range Picker Example

```typescript
import { DateRangePicker } from '@/components/ui/date-range-picker';

function DashboardFilters() {
  const [dateRange, setDateRange] = useState({
    from: new Date(2025, 11, 31), // December 31, 2025
    to: new Date(2026, 0, 14)     // January 14, 2026
  });

  const { data } = useCurrencyBreakdown(dateRange.from, dateRange.to);

  return (
    <div>
      <DateRangePicker
        value={dateRange}
        onChange={setDateRange}
      />
      <CurrencyChart data={data} />
    </div>
  );
}
```

---

## Testing

### Test with ISO 8601 Format (Frontend Format)

```bash
# Test currency breakdown
curl "http://localhost:8000/api/analytics/currency-breakdown?start_date=2025-12-31T21:00:00.000Z&end_date=2026-01-14T21:00:00.000Z"

# Test transaction overview
curl "http://localhost:8000/api/analytics/transaction-overview?start_date=2025-12-31T21:00:00.000Z&end_date=2026-01-14T21:00:00.000Z"

# Test status breakdown
curl "http://localhost:8000/api/analytics/status-breakdown?start_date=2025-12-31T21:00:00.000Z&end_date=2026-01-14T21:00:00.000Z"
```

### Test with Standard Format

```bash
# Date only
curl "http://localhost:8000/api/analytics/currency-breakdown?start_date=2025-12-31&end_date=2026-01-14"

# Date and time
curl "http://localhost:8000/api/analytics/currency-breakdown?start_date=2025-12-31%2021:00:00&end_date=2026-01-14%2021:00:00"
```

---

## All Endpoints Support These Formats

✅ `/api/transactions`
✅ `/api/transactions/status/{status}`
✅ `/api/analytics/custom-range`
✅ `/api/analytics/transaction-overview`
✅ `/api/analytics/status-breakdown`
✅ `/api/analytics/currency-breakdown`

---

## Error Handling

If an invalid date format is provided, the API returns a clear error message:

```json
{
  "detail": "Invalid date format: 2025/12/31. Supported formats: YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, or ISO 8601 (2025-12-31T21:00:00.000Z)"
}
```

---

## Implementation Details

The backend uses a smart `parse_datetime()` function that:

1. Detects ISO 8601 format (contains 'T')
2. Removes milliseconds (`.000`)
3. Removes timezone indicator (`Z`)
4. Parses the datetime
5. Falls back to standard formats if ISO 8601 fails

This ensures maximum compatibility with all frontend frameworks and date libraries.

---

## Summary

✅ **Your frontend doesn't need any changes**
✅ **ISO 8601 format is fully supported**
✅ **All date endpoints work with frontend date format**
✅ **Backward compatible with standard formats**

The 400 Bad Request error is now fixed! 🎉
