# Weekly Transaction Performance Email Specification

## Overview
Automated weekly email sent every Sunday summarizing the previous week's transaction performance (Monday-Sunday). The email should be professional, data-driven, and visually clean.

---

## Scheduling
- **Trigger**: Every Sunday at 9:00 AM (local time)
- **Reporting Period**: Previous Monday 00:00:00 to Sunday 23:59:59
- **Recipients**: Finance team, management team, stakeholders

---

## Email Structure

### Subject Line Format
```
Weekly Transaction Performance Report - [Week Start Date] to [Week End Date]
```
Example: `Weekly Transaction Performance Report - Jan 13 to Jan 19, 2026`

---

### Email Body Structure

#### 1. Greeting
```
Dear Team,
```

#### 2. Opening Summary (1-2 sentences)
Brief context about the reporting period and overall performance tone.

Example:
> "I am pleased to share our transaction performance for the week of [Date Range]. This week showed [positive/stable/challenging] performance across key metrics."

---

#### 3. Core Metrics Section

**Title**: "Weekly Performance Snapshot"

Present the following metrics in a clean, scannable format:

**Transaction Volume:**
- Total transactions processed
- Successful transactions (count + percentage)
- Failed transactions (count + percentage)
- Pending transactions (count + percentage)
- Declined transactions (count + percentage)
- Other statuses (reversed, processing_swap, onchain) if applicable

**Transaction Value:**
- Total transaction volume (USD)
- Average transaction size (USD)
- Week-over-week growth/decline percentage

**Success Metrics:**
- Overall success rate (%)
- Week-over-week change in success rate

**Revenue Performance:**
- Total fees collected (gross revenue in USD)
- Average fee per transaction (USD)
- Fees-to-value ratio (%)
- Net revenue (if applicable)

---

#### 4. Currency Breakdown Section

**Title**: "Currency Distribution"

Top 5 currencies by:
- Transaction count
- Transaction volume (USD equivalent)
- Percentage of total volume

Format as a clean list or table:
```
1. USD - 1,234 transactions, $456,789 (45.6%)
2. NGN - 987 transactions, $234,567 (23.4%)
...
```

---

#### 5. Comparative Analysis Section

**Title**: "Week-over-Week Comparison"

Compare current week vs previous week:
- Transaction volume change (% and absolute)
- Success rate change
- Revenue change
- Average transaction size change

Use clear indicators:
- ↑ for increases
- ↓ for decreases
- → for stable (< 2% change)

---

#### 6. Notable Observations (Optional)

**Title**: "Key Insights"

Include 2-4 bullet points highlighting:
- Significant trends or patterns
- Anomalies or unusual activity
- Improvements or concerns
- Operational notes (if any)

Example:
- "Success rate improved by 3.2% compared to last week, reflecting enhanced payment gateway stability"
- "Weekend transaction volume increased by 15%, indicating growing user engagement"

---

#### 7. Closing Statement

Professional closing with forward-looking tone:

Example:
> "Thank you for your continued dedication to maintaining our platform's reliability and performance. We remain focused on scaling transaction volumes while optimizing success rates and user experience."

**Sign-off:**
```
Best regards,
[Finance Manager Name]
Finance Team
```

---

## Email Design Specifications

### HTML Email Template Requirements

#### Color Palette
- **Primary Brand Color**: #317CFF (blue)
- **Success/Positive**: #10B981 (green)
- **Warning/Neutral**: #F59E0B (amber)
- **Error/Negative**: #EF4444 (red)
- **Background**: #FFFFFF (white)
- **Text Primary**: #1F2937 (dark gray)
- **Text Secondary**: #6B7280 (medium gray)
- **Borders/Dividers**: #E5E7EB (light gray)

#### Typography
- **Font Family**: Arial, Helvetica, sans-serif (email-safe)
- **Heading 1**: 24px, bold, #1F2937
- **Heading 2**: 18px, semi-bold, #1F2937
- **Body Text**: 14px, regular, #1F2937
- **Metrics/Numbers**: 16px, bold, color-coded by performance
- **Labels**: 12px, medium, #6B7280

#### Layout Structure
```
┌─────────────────────────────────────┐
│  Header (Logo + Title)              │
├─────────────────────────────────────┤
│  Greeting                           │
├─────────────────────────────────────┤
│  Opening Summary                    │
├─────────────────────────────────────┤
│  Core Metrics (Grid/Cards)          │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │Metric│ │Metric│ │Metric│        │
│  └──────┘ └──────┘ └──────┘        │
├─────────────────────────────────────┤
│  Currency Breakdown (Table)         │
├─────────────────────────────────────┤
│  Week-over-Week Comparison          │
├─────────────────────────────────────┤
│  Key Insights (Bullet Points)       │
├─────────────────────────────────────┤
│  Closing Statement                  │
├─────────────────────────────────────┤
│  Footer (Company Info)              │
└─────────────────────────────────────┘
```

#### Metric Cards Design
Each metric should be displayed in a card format:
- Light background (#F9FAFB)
- Subtle border (#E5E7EB)
- Padding: 16px
- Border radius: 8px
- Icon or indicator (↑↓→) color-coded
- Large number display
- Small descriptive label below

#### Table Design (for currency breakdown)
- Header row with light background (#F3F4F6)
- Alternating row colors for readability
- Clear borders (#E5E7EB)
- Right-align numbers
- Left-align text labels

---

## Data Requirements

### API Endpoint Needed
Create endpoint: `GET /api/reports/weekly-performance`

**Query Parameters:**
- `week_start_date` (YYYY-MM-DD)
- `week_end_date` (YYYY-MM-DD)

**Response Structure:**
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
    "failed_count": 45,
    "pending_count": 34,
    "declined_count": 10,
    "success_rate": 92.8,
    "total_volume_usd": "567890.50",
    "avg_transaction_size_usd": "460.15",
    "total_revenue_usd": "1234.56",
    "avg_fee_per_transaction_usd": "1.00",
    "fees_to_value_ratio": 0.22,
    "currency_breakdown": [
      {
        "currency": "USD",
        "transaction_count": 456,
        "volume_usd": "234567.00",
        "percentage": 41.3
      }
    ]
  },
  "previous_week": {
    // Same structure as current_week
  },
  "week_over_week_changes": {
    "transaction_volume_change_pct": 5.2,
    "success_rate_change_pct": -0.5,
    "revenue_change_pct": 8.3,
    "avg_transaction_size_change_pct": 2.1
  }
}
```

---

## Implementation Instructions for Backend Claude

### Step 1: Create Weekly Report API Endpoint
1. Create endpoint `/api/reports/weekly-performance`
2. Calculate all metrics for the specified week
3. Compare with previous week's data
4. Return structured JSON response

### Step 2: Create Email Template
1. Design HTML email template following the design specifications above
2. Use inline CSS for maximum email client compatibility
3. Make template responsive (mobile-friendly)
4. Include fallback plain text version

### Step 3: Implement Email Generation Logic
1. Fetch data from weekly performance API
2. Populate email template with actual data
3. Format numbers with proper thousand separators and decimal places
4. Apply color coding based on performance (green for positive, red for negative)
5. Generate dynamic insights based on data patterns

### Step 4: Trigger Email Generation
1.  Endpoint will be called and pass emails from n8n which means we don't have to worry about the trigger / clon job

### Step 5: Email Sending
1. Use appropriate email service (Gmail Service)
2. Set proper sender name and email
3. Include recipients from configuration
4. Handle send failures with retry logic
5. Log all email activities

---

## Testing Checklist

- [ ] API endpoint returns correct data for any given week
- [ ] Email template renders correctly in major email clients (Gmail, Outlook, Apple Mail)
- [ ] Mobile responsive design works on small screens
- [ ] Numbers are formatted correctly (commas, decimals, percentages)
- [ ] Color coding applies correctly based on positive/negative changes
- [ ] Week-over-week calculations are accurate
- [ ] Scheduled task triggers at correct time
- [ ] Email sends successfully to all recipients
- [ ] Plain text fallback works for non-HTML email clients
- [ ] Unsubscribe link included (if required by email regulations)

---

## Example Email Content

**Subject:** Weekly Transaction Performance Report - Jan 13 to Jan 19, 2026

**Body:**

> Dear Team,
>
> I am pleased to share our transaction performance for the week of January 13-19, 2026. This week showed strong performance across key metrics with notable improvements in success rates.
>
> **Weekly Performance Snapshot**
>
> **Transaction Volume:**
> - Total Transactions: 1,234
> - Successful: 1,145 (92.8%) ↑
> - Failed: 45 (3.6%) ↓
> - Pending: 34 (2.8%)
> - Declined: 10 (0.8%)
>
> **Transaction Value:**
> - Total Volume: $567,890.50 ↑ 5.2%
> - Average Transaction: $460.15 ↑ 2.1%
>
> **Revenue Performance:**
> - Total Fees Collected: $1,234.56 ↑ 8.3%
> - Average Fee per Transaction: $1.00
> - Fees-to-Value Ratio: 0.22%
>
> **Currency Distribution**
>
> 1. USD - 456 transactions, $234,567 (41.3%)
> 2. NGN - 345 transactions, $123,456 (21.7%)
> 3. EUR - 234 transactions, $98,765 (17.4%)
> 4. CAD - 123 transactions, $67,890 (12.0%)
> 5. GBP - 76 transactions, $43,212 (7.6%)
>
> **Week-over-Week Comparison**
>
> - Transaction Volume: ↑ 5.2% (+61 transactions)
> - Success Rate: ↑ 0.8 percentage points
> - Revenue: ↑ 8.3% (+$94.67)
> - Average Transaction Size: ↑ 2.1%
>
> **Key Insights**
>
> - Success rate improved to 92.8%, our highest weekly rate this quarter
> - Weekend transaction volume increased by 18%, indicating strong user engagement
> - USD transactions continue to dominate, representing 41% of total volume
> - Failed transaction rate decreased to 3.6%, reflecting improved payment gateway stability
>
> Thank you for your continued dedication to maintaining our platform's reliability and performance. We remain focused on scaling transaction volumes while optimizing success rates and user experience.
>
> Best regards,  
> Finance Team

---

## Configuration Variables

Store these in environment variables or configuration file:

```env
# Email Settings
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
WEEKLY_REPORT_SENDER_NAME=SpennX Finance Team 

# Schedule Settings
WEEKLY_REPORT_DAY=SUNDAY
WEEKLY_REPORT_TIME=09:00
WEEKLY_REPORT_TIMEZONE=UTC

# Branding
COMPANY_NAME=SpennX
COMPANY_LOGO_URL=https://spennx.com/logo.png
COMPANY_WEBSITE=https://spennx.com
```

---

## Notes for Backend Implementation

1. **Data Accuracy**: Ensure all calculations are precise, especially percentages and currency conversions
2. **Time Zones**: Handle time zones correctly when defining week boundaries
3. **Error Handling**: Implement robust error handling for API failures, email send failures
4. **Monitoring**: Log all email sends and track delivery rates
5. **Testing**: Test with various data scenarios (high volume, low volume, all statuses)
6. **Scalability**: Design to handle growing data volumes efficiently
7. **Security**: Ensure sensitive financial data is handled securely
8. **Compliance**: Include required email headers (unsubscribe, company info) per regulations
