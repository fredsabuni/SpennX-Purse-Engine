# Weekly Email Report - Quick Start Guide

## What Was Implemented

A complete weekly transaction performance email report system with:
- ✅ Data aggregation and calculation module (`app/reports.py`)
- ✅ Professional HTML email template with responsive design (`app/email_service.py`)
- ✅ Two API endpoints for report generation and email sending
- ✅ Week-over-week comparison analytics
- ✅ Dynamic insights generation
- ✅ Currency conversion to USD
- ✅ Top 5 currency breakdown

## Quick Test

### 1. Get Report Data (JSON)

```bash
# Get report for week starting Jan 13, 2026
curl "http://localhost:8000/api/reports/weekly-performance?week_start_date=2026-01-13"
```

**Response includes**:
- Current week metrics (transactions, volume, revenue)
- Previous week metrics
- Week-over-week changes
- Top 5 currencies breakdown

### 2. Generate Email (Preview Mode)

```bash
# Generate email without sending (default mode)
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["finance@spennx.com"]
  }'
```

**Returns**:
- Success confirmation
- Email subject line
- Report summary
- Note about email sending being disabled

## Enable Email Sending

### Step 1: Configure Email Credentials

Add to your `.env` file:

```env
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
WEEKLY_REPORT_SENDER_PASSWORD=your_app_password_here
WEEKLY_REPORT_SMTP_SERVER=smtp.gmail.com
WEEKLY_REPORT_SMTP_PORT=587
```

**For Gmail**:
1. Go to https://myaccount.google.com/apppasswords
2. Generate an App Password
3. Use that password (not your regular Gmail password)

### Step 2: Uncomment Email Sending Code

In `app/main.py`, find the `/api/reports/weekly-email` endpoint and uncomment these lines:

```python
from os import getenv
sender_email = getenv("WEEKLY_REPORT_SENDER_EMAIL", "finance@spennx.com")
sender_password = getenv("WEEKLY_REPORT_SENDER_PASSWORD")

if not sender_password:
    raise HTTPException(
        status_code=500,
        detail="Email credentials not configured."
    )

success = send_email(
    recipients=request.recipients,
    subject=subject,
    html_content=html_content,
    plain_text_content=plain_text_content,
    sender_email=sender_email,
    sender_password=sender_password
)

if not success:
    raise HTTPException(
        status_code=500,
        detail="Failed to send email."
    )
```

### Step 3: Restart Server

```bash
# If using Docker
docker-compose restart

# If running directly
# Stop the server (Ctrl+C) and restart
python -m uvicorn app.main:app --reload
```

### Step 4: Send Test Email

```bash
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["your-email@example.com"]
  }'
```

## Integration with n8n

### Workflow Setup

1. **Create New Workflow** in n8n

2. **Add Schedule Trigger**:
   - Trigger: Schedule
   - Mode: Every Week
   - Day: Sunday
   - Hour: 9
   - Minute: 0

3. **Add HTTP Request Node**:
   - Method: POST
   - URL: `http://your-api-url:8000/api/reports/weekly-email`
   - Body Content Type: JSON
   - Body:
   ```json
   {
     "week_start_date": "{{ $now.minus({days: 7}).startOf('week').format('YYYY-MM-DD') }}",
     "recipients": ["finance@spennx.com", "management@spennx.com"]
   }
   ```

4. **Add Error Handling** (optional):
   - Add an IF node to check response
   - Add notification on failure

### Calculate Week Start Date

The week start date should be the **previous Monday**. n8n expression:

```javascript
{{ $now.minus({days: 7}).startOf('week').format('YYYY-MM-DD') }}
```

Or use a Function node:

```javascript
// Get last Monday
const now = new Date();
const dayOfWeek = now.getDay();
const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // Monday = 1
const lastMonday = new Date(now);
lastMonday.setDate(now.getDate() - daysToSubtract - 7);

return {
  week_start_date: lastMonday.toISOString().split('T')[0]
};
```

## Email Preview

The email includes:

### Header
- Professional blue header with report title
- Date range display

### Core Metrics
- **Transaction Volume**: Total, success, failed, pending, declined counts
- **Transaction Value**: Total volume and average in USD
- **Revenue Performance**: Total fees, average fee, fees-to-value ratio

### Currency Distribution
- Top 5 currencies by volume
- Transaction count per currency
- Volume in USD
- Percentage of total

### Week-over-Week Comparison
- Transaction volume change (with ↑↓→ indicators)
- Success rate change
- Revenue change
- Average transaction size change

### Key Insights
- 2-4 automatically generated insights based on data
- Examples:
  - "Success rate improved to 92.8%, up 3.2 percentage points"
  - "Transaction volume surged by 15%, indicating strong user engagement"
  - "USD transactions continue to dominate, representing 41% of total volume"

## API Endpoints Reference

### GET `/api/reports/weekly-performance`

**Parameters**:
- `week_start_date` (required): YYYY-MM-DD format, should be a Monday

**Response**: JSON with complete report data

**Use case**: Get raw data for custom processing or dashboards

### POST `/api/reports/weekly-email`

**Body**:
```json
{
  "week_start_date": "2026-01-13",
  "recipients": ["email1@example.com", "email2@example.com"]
}
```

**Response**: Success confirmation with report summary

**Use case**: Generate and send email report

## Troubleshooting

### "Invalid date format" error
- Ensure date is in YYYY-MM-DD format
- Verify it's a Monday (week start)

### "Email credentials not configured" error
- Check `.env` file has email settings
- Verify environment variables are loaded
- Restart server after updating `.env`

### Email not received
- Check spam folder
- Verify SMTP credentials are correct
- Check server logs for detailed error
- Test with a different email address

### No data in report
- Verify database has transactions for that week
- Check date range is correct
- Ensure transactions have proper status values

## Testing Checklist

- [ ] GET endpoint returns valid JSON
- [ ] POST endpoint generates email successfully
- [ ] Email HTML renders correctly in Gmail
- [ ] Email HTML renders correctly in Outlook
- [ ] Mobile view looks good
- [ ] All metrics calculate correctly
- [ ] Currency conversion works
- [ ] Week-over-week changes are accurate
- [ ] Insights are relevant and accurate
- [ ] Plain text fallback works

## Next Steps

1. **Test with real data**: Use actual week dates from your database
2. **Configure recipients**: Set up proper recipient list
3. **Enable email sending**: Uncomment code and configure SMTP
4. **Set up n8n automation**: Create scheduled workflow
5. **Monitor delivery**: Check email logs and delivery rates

## Support

For detailed documentation, see:
- `WEEKLY_EMAIL_IMPLEMENTATION.md` - Complete technical documentation
- `weekly-email-specification.md` - Original requirements specification

For issues:
1. Check server logs: `docker-compose logs -f` or check `server.log`
2. Verify database connectivity
3. Test endpoints individually
4. Review configuration in `.env`
