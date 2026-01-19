# Curl Command Examples

## Issue with Shell Escaping

When using curl with JSON data in the terminal, you need to be careful with quotes and special characters.

### ❌ Wrong (causes errors)

```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["fredmalack15@gmail.com"]
  }'
```

**Errors**:
- `URL rejected: Malformed input to a URL function`
- `nested brace in URL position`

**Why**: The shell interprets the newlines and braces incorrectly.

---

## ✅ Correct Ways to Use Curl

### Option 1: Single Line (Recommended)

```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date":"2026-01-13","recipients":["fredmalack15@gmail.com"]}'
```

### Option 2: Using a File

Create a file `request.json`:
```json
{
  "week_start_date": "2026-01-13",
  "recipients": ["fredmalack15@gmail.com"]
}
```

Then use:
```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d @request.json
```

### Option 3: Using Here-Doc (Multi-line)

```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "week_start_date": "2026-01-13",
  "recipients": ["fredmalack15@gmail.com"]
}
EOF
```

---

## Complete Examples

### Send Weekly Email Report

```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date":"2026-01-13","recipients":["fredmalack15@gmail.com"]}'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Weekly performance email sent successfully via Gmail API",
  "subject": "Weekly Transaction Performance Report - Jan 13 to Jan 19, 2026",
  "recipients": ["fredmalack15@gmail.com"],
  "report_summary": {
    "period": {
      "start_date": "2026-01-13",
      "end_date": "2026-01-19",
      "week_number": 3
    },
    "total_transactions": 1234,
    "total_volume_usd": "567890.50",
    "total_revenue_usd": "1234.56",
    "success_rate": 92.8
  }
}
```

### Get Weekly Report Data (JSON)

```bash
curl "http://localhost:8000/api/reports/weekly-performance?week_start_date=2026-01-13"
```

### Multiple Recipients

```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date":"2026-01-13","recipients":["email1@example.com","email2@example.com","email3@example.com"]}'
```

---

## Using HTTPie (Alternative to Curl)

If you have HTTPie installed, it's much easier:

```bash
# Install HTTPie
pip install httpie

# Send request
http POST localhost:8000/api/reports/weekly-email \
  week_start_date="2026-01-13" \
  recipients:='["fredmalack15@gmail.com"]'
```

---

## Using Postman

1. **Method**: POST
2. **URL**: `http://localhost:8000/api/reports/weekly-email`
3. **Headers**: 
   - `Content-Type: application/json`
4. **Body** (raw JSON):
```json
{
  "week_start_date": "2026-01-13",
  "recipients": ["fredmalack15@gmail.com"]
}
```

---

## Using Python Requests

```python
import requests

url = "http://localhost:8000/api/reports/weekly-email"
payload = {
    "week_start_date": "2026-01-13",
    "recipients": ["fredmalack15@gmail.com"]
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## Common Curl Errors and Fixes

### Error: "Field required"

**Cause**: JSON not properly formatted or not sent

**Fix**: Ensure `-d` flag has valid JSON:
```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date":"2026-01-13","recipients":["test@example.com"]}'
```

### Error: "URL rejected: Malformed input"

**Cause**: Shell interpreting special characters

**Fix**: Use single-line JSON or file input:
```bash
# Single line
curl ... -d '{"key":"value"}'

# Or use file
curl ... -d @file.json
```

### Error: "nested brace in URL"

**Cause**: Braces in multi-line string

**Fix**: Remove newlines from JSON:
```bash
# ❌ Wrong
-d '{
  "key": "value"
}'

# ✅ Correct
-d '{"key":"value"}'
```

---

## Quick Reference

### Basic POST Request
```bash
curl -X POST URL -H "Content-Type: application/json" -d '{"key":"value"}'
```

### With Authentication (if needed)
```bash
curl -X POST URL -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d '{"key":"value"}'
```

### Save Response to File
```bash
curl -X POST URL -H "Content-Type: application/json" -d '{"key":"value"}' -o response.json
```

### Pretty Print Response
```bash
curl -X POST URL -H "Content-Type: application/json" -d '{"key":"value"}' | python -m json.tool
```

### Verbose Output (for debugging)
```bash
curl -v -X POST URL -H "Content-Type: application/json" -d '{"key":"value"}'
```

---

## Testing Checklist

- [ ] Use single-line JSON in curl
- [ ] Escape quotes properly
- [ ] Include Content-Type header
- [ ] Verify URL is correct
- [ ] Check response status code
- [ ] Verify email was sent

---

## Summary

✅ **Email was sent successfully!** (despite curl errors)

The curl errors were just formatting issues with the command, not actual API errors.

**Recommended approach**:
```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date":"2026-01-13","recipients":["fredmalack15@gmail.com"]}'
```

Or use the test script:
```bash
python test_weekly_report.py
```

---

*Curl examples guide - January 18, 2026*
