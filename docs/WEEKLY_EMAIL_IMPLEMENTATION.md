# Weekly Email Report Implementation

## Overview

The weekly email report feature has been implemented as a modular system that generates and sends automated weekly transaction performance reports. The implementation follows a clean architecture with separation of concerns.

## Architecture

### Module Structure

```
app/
├── reports.py          # Data aggregation and calculation logic
├── email_service.py    # Email template generation and sending
├── schemas.py          # Pydantic models for API requests/responses
└── main.py            # API endpoints
```

### Key Components

#### 1. **reports.py** - Report Generation Module

**Purpose**: Handles all data aggregation, calculation, and report generation logic.

**Key Functions**:
- `get_week_boundaries(week_start_date)` - Calculates week start and end dates
- `calculate_week_metrics(db, start, end)` - Aggregates all metrics for a given week
- `calculate_week_over_week_changes(current, previous)` - Computes percentage changes
- `generate_weekly_performance_report(db, week_start_date)` - Main report generation function

**Features**:
- Calculates transaction counts by status (success, failed, pending, declined, etc.)
- Computes volume and revenue metrics in USD
- Generates top 5 currency breakdown
- Compares current week vs previous week
- Handles currency conversion using rates from recipient JSON

#### 2. **email_service.py** - Email Service Module

**Purpose**: Handles email template generation and sending.

**Key Functions**:
- `generate_html_email(report_data)` - Creates professional HTML email
- `generate_plain_text_email(report_data)` - Creates plain text fallback
- `generate_insights(current, changes)` - Generates dynamic insights based on data
- `send_email(recipients, subject, html_content, ...)` - Sends email via SMTP

**Features**:
- Professional HTML email template with inline CSS
- Mobile-responsive design
- Color-coded metrics (green for positive, red for negative)
- Dynamic insights generation
- Plain text fallback for email clients that don't support HTML
- SMTP email sending with Gmail support

#### 3. **API Endpoints**

##### GET `/api/reports/weekly-performance`

**Purpose**: Get weekly performance report data as JSON.

**Parameters**:
- `week_start_date` (required): Week start date in YYYY-MM-DD format (should be a Monday)

**Response**: Complete report data structure including:
- Period information (start date, end date, week number)
- Current week metrics
- Previous week metrics
- Week-over-week changes

**Example**:
```bash
GET /api/reports/weekly-performance?week_start_date=2026-01-13
```

##### POST `/api/reports/weekly-email`

**Purpose**: Generate and send weekly performance email.

**Request Body**:
```json
{
  "week_start_date": "2026-01-13",
  "recipients": [
    "finance@spennx.com",
    "management@spennx.com"
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Weekly performance email generated successfully",
  "subject": "Weekly Transaction Performance Report - Jan 13 to Jan 19, 2026",
  "recipients": ["finance@spennx.com"],
  "report_summary": {
    "period": {...},
    "total_transactions": 1234,
    "total_volume_usd": "567890.50",
    "total_revenue_usd": "1234.56",
    "success_rate": 92.8
  }
}
```

## Email Template Features

### Design Specifications

- **Color Palette**:
  - Primary: #317CFF (blue)
  - Success: #10B981 (green)
  - Warning: #F59E0B (amber)
  - Error: #EF4444 (red)
  - Neutral: #6B7280 (gray)

- **Layout**:
  - Professional header with branding
  - Card-based metric display
  - Clean table for currency breakdown
  - Color-coded week-over-week comparison
  - Dynamic insights section
  - Professional footer

- **Responsive Design**:
  - Mobile-friendly
  - Email client compatible (Gmail, Outlook, Apple Mail)
  - Inline CSS for maximum compatibility

### Email Sections

1. **Header**: Report title and date range
2. **Greeting**: Professional salutation
3. **Opening Summary**: Brief context about the week
4. **Core Metrics**:
   - Transaction Volume (counts by status)
   - Transaction Value (total and average)
   - Revenue Performance (fees and ratios)
5. **Currency Distribution**: Top 5 currencies table
6. **Week-over-Week Comparison**: Changes with indicators
7. **Key Insights**: 2-4 dynamic insights based on data
8. **Closing Statement**: Professional sign-off
9. **Footer**: Timestamp and company info

### Dynamic Insights

The system automatically generates insights based on:
- Success rate changes (>2% threshold)
- Volume changes (>10% threshold)
- Revenue changes (>5% threshold)
- Top currency dominance
- Failed transaction rate concerns

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Weekly Email Report Configuration
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
WEEKLY_REPORT_SENDER_PASSWORD=your_email_password_here
WEEKLY_REPORT_SMTP_SERVER=smtp.gmail.com
WEEKLY_REPORT_SMTP_PORT=587
```

### Gmail Setup

If using Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password as `WEEKLY_REPORT_SENDER_PASSWORD`

## Usage

### 1. Get Report Data (JSON)

```bash
curl -X GET "http://localhost:8000/api/reports/weekly-performance?week_start_date=2026-01-13"
```

### 2. Send Email Report

```bash
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["finance@spennx.com", "management@spennx.com"]
  }'
```

### 3. Integration with n8n

The endpoints are designed to be called by n8n for automation:

**n8n Workflow**:
1. **Schedule Trigger**: Every Sunday at 9:00 AM
2. **HTTP Request Node**: POST to `/api/reports/weekly-email`
3. **Set Parameters**:
   - Calculate previous week's Monday date
   - Set recipient list from configuration
4. **Error Handling**: Send notification if email fails

**Example n8n HTTP Request**:
```json
{
  "method": "POST",
  "url": "http://your-api-url/api/reports/weekly-email",
  "body": {
    "week_start_date": "{{ $now.minus({days: 7}).startOf('week').format('YYYY-MM-DD') }}",
    "recipients": ["finance@spennx.com"]
  }
}
```

## Testing

### Test Report Generation

```python
# Test with a specific week
GET /api/reports/weekly-performance?week_start_date=2026-01-13
```

### Test Email Generation (without sending)

The email generation can be tested by:
1. Calling the endpoint with email sending code commented out (default)
2. Reviewing the returned HTML in the response
3. Checking the report summary data

### Test Email Sending

1. Configure email credentials in `.env`
2. Uncomment the email sending code in `main.py` (lines marked with comments)
3. Call the endpoint with test recipients
4. Verify email delivery

## Data Calculations

### Metrics Included

**Transaction Counts**:
- Total transactions (all statuses)
- Success count and percentage
- Failed count and percentage
- Pending count and percentage
- Declined count and percentage
- Other statuses (reversed, processing_swap, etc.)

**Financial Metrics** (USD converted):
- Total volume (successful transactions only)
- Average transaction size
- Total revenue (fees collected)
- Average fee per transaction
- Fees-to-value ratio

**Currency Breakdown**:
- Top 5 currencies by volume
- Transaction count per currency
- Volume in USD per currency
- Percentage of total volume

**Week-over-Week Changes**:
- Transaction volume change (% and absolute)
- Success rate change (percentage points)
- Revenue change (% and absolute)
- Average transaction size change (%)

### Currency Conversion

All amounts are converted to USD using:
1. Rate from `recipient.rate` field in transaction JSON (if available)
2. Fallback to predefined rates in `currency_rates.py`
3. Assumes 1:1 for USD

## Error Handling

The implementation includes:
- Date format validation
- Database query error handling
- Email sending error handling
- Graceful fallbacks for missing data
- Detailed error messages in API responses

## Performance Considerations

- Efficient database queries with aggregation
- Minimal data transfer (only necessary fields)
- Batch processing for currency conversion
- Optimized for weekly data volumes

## Future Enhancements

Potential improvements:
1. **Scheduling**: Add built-in scheduler (APScheduler) instead of relying on n8n
2. **Templates**: Support multiple email templates
3. **Customization**: Allow custom date ranges and metrics
4. **Attachments**: Add PDF report generation
5. **Analytics**: Track email open rates and engagement
6. **Localization**: Support multiple languages
7. **Charts**: Embed chart images in email
8. **Recipients Management**: Database-driven recipient lists

## Troubleshooting

### Email Not Sending

1. Check SMTP credentials in `.env`
2. Verify email sending code is uncommented in `main.py`
3. Check firewall/network allows SMTP connections
4. Review server logs for detailed error messages
5. Test SMTP connection separately

### Incorrect Data

1. Verify `week_start_date` is a Monday
2. Check database has data for the specified week
3. Verify currency conversion rates are configured
4. Review transaction status values in database

### Email Formatting Issues

1. Test in multiple email clients
2. Verify HTML is valid
3. Check inline CSS is properly applied
4. Test plain text fallback

## Security Considerations

- Email credentials stored in environment variables (not in code)
- Input validation on all API parameters
- SQL injection prevention via SQLAlchemy ORM
- Rate limiting recommended for production
- HTTPS recommended for API endpoints

## Maintenance

Regular maintenance tasks:
1. Monitor email delivery rates
2. Update currency conversion rates
3. Review and update insights logic
4. Test email rendering in new email clients
5. Update recipient lists as needed
6. Monitor API performance and optimize queries

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Verify configuration in `.env`
3. Test endpoints individually
4. Review this documentation
5. Check database connectivity and data quality
