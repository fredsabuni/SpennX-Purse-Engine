# Weekly Email Report - System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         n8n Automation                          │
│                    (Schedule: Sunday 9:00 AM)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP POST
                             │ /api/reports/weekly-email
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              app/main.py (API Endpoints)                  │ │
│  │                                                           │ │
│  │  GET  /api/reports/weekly-performance                    │ │
│  │  POST /api/reports/weekly-email                          │ │
│  └─────────────────┬─────────────────────┬───────────────────┘ │
│                    │                     │                     │
│                    ▼                     ▼                     │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐ │
│  │   app/reports.py        │  │  app/email_service.py       │ │
│  │                         │  │                             │ │
│  │ • Week boundaries       │  │ • HTML template generation  │ │
│  │ • Metrics calculation   │  │ • Plain text fallback       │ │
│  │ • Currency conversion   │  │ • Dynamic insights          │ │
│  │ • WoW comparison        │  │ • SMTP email sending        │ │
│  └───────────┬─────────────┘  └─────────────────────────────┘ │
│              │                                                 │
│              ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Database (MySQL)                           │  │
│  │                                                         │  │
│  │  • transactions table                                   │  │
│  │  • Query by date range                                  │  │
│  │  • Aggregate by status, currency                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ SMTP
                             ▼
                    ┌─────────────────┐
                    │  Gmail Server   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Recipients    │
                    │                 │
                    │ • Finance Team  │
                    │ • Management    │
                    │ • Stakeholders  │
                    └─────────────────┘
```

## Data Flow

### 1. Report Generation Flow

```
Request
  │
  ├─> Validate week_start_date
  │
  ├─> Calculate week boundaries
  │     ├─> Current week: Monday 00:00 to Sunday 23:59
  │     └─> Previous week: Previous Monday to Previous Sunday
  │
  ├─> Query database for current week
  │     ├─> Get all transactions in date range
  │     ├─> Count by status
  │     ├─> Calculate volumes (USD conversion)
  │     ├─> Calculate revenue
  │     └─> Group by currency (top 5)
  │
  ├─> Query database for previous week
  │     └─> Same calculations as current week
  │
  ├─> Calculate week-over-week changes
  │     ├─> Transaction volume change (%)
  │     ├─> Success rate change (pp)
  │     ├─> Revenue change (%)
  │     └─> Avg transaction size change (%)
  │
  └─> Return report data structure
```

### 2. Email Generation Flow

```
Report Data
  │
  ├─> Generate HTML email
  │     ├─> Format dates and numbers
  │     ├─> Apply color coding
  │     │     ├─> Green for positive changes
  │     │     ├─> Red for negative changes
  │     │     └─> Gray for neutral
  │     ├─> Build metric cards
  │     ├─> Build currency table
  │     ├─> Generate dynamic insights
  │     └─> Assemble complete HTML
  │
  ├─> Generate plain text fallback
  │     └─> Same content, text format
  │
  └─> Send via SMTP
        ├─> Connect to Gmail
        ├─> Authenticate
        ├─> Send to recipients
        └─> Return success/failure
```

## Module Responsibilities

### app/reports.py

**Purpose**: Data aggregation and business logic

**Responsibilities**:
- Calculate week boundaries from start date
- Query database for transaction data
- Aggregate metrics by status and currency
- Convert all amounts to USD
- Calculate week-over-week changes
- Return structured data

**Key Functions**:
```python
get_week_boundaries(week_start_date) -> (start, end)
calculate_week_metrics(db, start, end) -> dict
calculate_week_over_week_changes(current, previous) -> dict
generate_weekly_performance_report(db, week_start_date) -> dict
```

### app/email_service.py

**Purpose**: Email template and delivery

**Responsibilities**:
- Generate professional HTML email
- Create plain text fallback
- Generate dynamic insights
- Format numbers and dates
- Apply color coding
- Send email via SMTP

**Key Functions**:
```python
generate_html_email(report_data) -> str
generate_plain_text_email(report_data) -> str
generate_insights(current, changes) -> list
send_email(recipients, subject, html, text) -> bool
```

### app/main.py

**Purpose**: API endpoints and request handling

**Responsibilities**:
- Define API routes
- Validate input parameters
- Handle errors
- Return responses
- Coordinate between modules

**Endpoints**:
```python
GET  /api/reports/weekly-performance
POST /api/reports/weekly-email
```

## Database Schema

### transactions table

```sql
CREATE TABLE transactions (
    id VARCHAR(36) PRIMARY KEY,
    amount BIGINT NOT NULL,
    currency VARCHAR(10) NOT NULL,
    human_readable_amount DECIMAL(15,2) NOT NULL,
    charge BIGINT NOT NULL,
    human_readable_charge DECIMAL(15,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    recipient JSON,
    -- other fields...
);
```

**Key Fields for Reports**:
- `created_at`: Filter by date range
- `status`: Group by status
- `currency`: Group by currency
- `human_readable_amount`: Transaction volume
- `human_readable_charge`: Revenue (fees)
- `recipient.rate`: Currency conversion rate

## API Request/Response

### GET /api/reports/weekly-performance

**Request**:
```http
GET /api/reports/weekly-performance?week_start_date=2026-01-13
```

**Response**:
```json
{
  "period": {
    "start_date": "2026-01-13",
    "end_date": "2026-01-19",
    "week_number": 3
  },
  "current_week": {
    "total_transactions": 1234,
    "success_count": 1145,
    "success_rate": 92.8,
    "total_volume_usd": "567890.50",
    "total_revenue_usd": "1234.56",
    "currency_breakdown": [...]
  },
  "previous_week": {...},
  "week_over_week_changes": {
    "transaction_volume_change_pct": 5.2,
    "success_rate_change_pct": -0.5,
    "revenue_change_pct": 8.3
  }
}
```

### POST /api/reports/weekly-email

**Request**:
```http
POST /api/reports/weekly-email
Content-Type: application/json

{
  "week_start_date": "2026-01-13",
  "recipients": ["finance@spennx.com"]
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
    "success_rate": 92.8
  }
}
```

## Email Template Structure

```
┌─────────────────────────────────────┐
│  Header (Blue #317CFF)              │
│  • Report Title                     │
│  • Date Range                       │
├─────────────────────────────────────┤
│  Greeting                           │
│  "Dear Team,"                       │
├─────────────────────────────────────┤
│  Opening Summary                    │
│  Brief context paragraph            │
├─────────────────────────────────────┤
│  Core Metrics                       │
│  ┌───────────────────────────────┐  │
│  │ Transaction Volume (Card)     │  │
│  │ • Total, Success, Failed, etc │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Transaction Value (Card)      │  │
│  │ • Total Volume, Avg Size      │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Revenue Performance (Card)    │  │
│  │ • Fees, Avg Fee, Ratio        │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│  Currency Distribution              │
│  ┌───────────────────────────────┐  │
│  │ Currency | Txns | Vol | %     │  │
│  ├───────────────────────────────┤  │
│  │ USD      | 456  | $234K | 41% │  │
│  │ NGN      | 345  | $123K | 22% │  │
│  │ ...                            │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│  Week-over-Week Comparison          │
│  • Volume: ↑ 5.2% (+61 txns)       │
│  • Success Rate: ↑ 0.8 pp          │
│  • Revenue: ↑ 8.3% (+$94.67)       │
├─────────────────────────────────────┤
│  Key Insights                       │
│  • Insight 1                        │
│  • Insight 2                        │
│  • Insight 3                        │
├─────────────────────────────────────┤
│  Closing Statement                  │
│  Professional sign-off              │
├─────────────────────────────────────┤
│  Footer (Gray #F3F4F6)              │
│  • Company info                     │
│  • Timestamp                        │
└─────────────────────────────────────┘
```

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db

# Email
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
WEEKLY_REPORT_SENDER_PASSWORD=app_password
WEEKLY_REPORT_SMTP_SERVER=smtp.gmail.com
WEEKLY_REPORT_SMTP_PORT=587
```

### Gmail App Password Setup

1. Enable 2FA on Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate App Password
4. Use in `WEEKLY_REPORT_SENDER_PASSWORD`

## Deployment Considerations

### Production Checklist

- [ ] Configure email credentials
- [ ] Uncomment email sending code
- [ ] Set up n8n workflow
- [ ] Test with real data
- [ ] Verify email delivery
- [ ] Monitor API performance
- [ ] Set up error alerting
- [ ] Configure recipient lists
- [ ] Test in multiple email clients
- [ ] Set up logging

### Scaling Considerations

- Database query optimization for large datasets
- Email sending rate limits (Gmail: 500/day)
- API rate limiting
- Caching for repeated requests
- Async email sending for multiple recipients
- Queue system for email delivery

### Monitoring

**Metrics to Track**:
- API response time
- Email delivery rate
- Email open rate (if tracking enabled)
- Database query performance
- Error rate
- Report generation time

**Logging**:
- All API requests
- Email send attempts
- Errors and exceptions
- Database query times
- Currency conversion issues

## Security

### Best Practices Implemented

- ✅ Email credentials in environment variables
- ✅ Input validation on all parameters
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Error messages don't expose sensitive data
- ✅ HTTPS recommended for production
- ✅ Rate limiting recommended

### Additional Recommendations

- Implement API authentication
- Add rate limiting per IP
- Use secrets management service
- Enable HTTPS only
- Implement audit logging
- Add email recipient validation
- Implement DKIM/SPF for emails

## Testing Strategy

### Unit Tests
- Test week boundary calculations
- Test metric calculations
- Test currency conversion
- Test week-over-week changes
- Test insight generation

### Integration Tests
- Test database queries
- Test API endpoints
- Test email generation
- Test SMTP connection

### End-to-End Tests
- Test complete report generation
- Test email delivery
- Test n8n integration
- Test error scenarios

## Maintenance

### Regular Tasks

**Weekly**:
- Monitor email delivery rates
- Check for errors in logs
- Verify data accuracy

**Monthly**:
- Review currency conversion rates
- Update insights logic if needed
- Check email template rendering

**Quarterly**:
- Review recipient lists
- Update documentation
- Optimize database queries
- Review security practices

## Future Enhancements

### Potential Features

1. **Scheduling**: Built-in scheduler (APScheduler)
2. **Templates**: Multiple email templates
3. **Customization**: Custom metrics and date ranges
4. **Attachments**: PDF report generation
5. **Analytics**: Email engagement tracking
6. **Localization**: Multi-language support
7. **Charts**: Embedded chart images
8. **Recipients**: Database-driven lists
9. **Notifications**: Slack/Teams integration
10. **Dashboard**: Web UI for report preview

## Support Resources

- **Documentation**: `WEEKLY_EMAIL_IMPLEMENTATION.md`
- **Quick Start**: `WEEKLY_EMAIL_QUICK_START.md`
- **Testing**: `test_weekly_report.py`
- **API Docs**: http://localhost:8000/docs
- **Postman**: `Weekly_Email_Report.postman_collection.json`
