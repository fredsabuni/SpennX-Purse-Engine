# Email Testing Guide

Quick guide for testing the weekly performance email feature.

---

## Test Email Template Locally

Generate and preview the email template without sending:

```bash
./venv/bin/python test_email_template.py
```

This will create:
- `test_email_output.html` - Open in browser to preview
- `test_email_output.txt` - Plain text version

---

## Send Test Email via API

### Using curl (single line):

```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date": "2026-01-13", "recipients": ["your-email@example.com"]}'
```

### Using HTTPie:

```bash
http POST http://localhost:8000/api/reports/weekly-email \
  week_start_date="2026-01-13" \
  recipients:='["your-email@example.com"]'
```

### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/reports/weekly-email",
    json={
        "week_start_date": "2026-01-13",
        "recipients": ["your-email@example.com"]
    }
)

print(response.json())
```

---

## Test Different Scenarios

### 1. High Volume Week
```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date": "2026-01-06", "recipients": ["test@example.com"]}'
```

### 2. Low Volume Week
```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date": "2025-12-23", "recipients": ["test@example.com"]}'
```

### 3. Multiple Recipients
```bash
curl -X POST http://localhost:8000/api/reports/weekly-email \
  -H "Content-Type: application/json" \
  -d '{"week_start_date": "2026-01-13", "recipients": ["user1@example.com", "user2@example.com", "user3@example.com"]}'
```

---

## Verify Email Rendering

### Email Clients to Test

1. **Gmail** (Web & Mobile)
   - Most common client
   - Good support for modern CSS

2. **Outlook** (Desktop & Web)
   - More restrictive CSS support
   - Test both versions

3. **Apple Mail** (macOS & iOS)
   - Excellent CSS support
   - Native font rendering

4. **Mobile Devices**
   - Test on iOS and Android
   - Verify responsive design

### What to Check

- ✅ Primary color (#317CFF) displays correctly
- ✅ System fonts render properly
- ✅ Gradient backgrounds show
- ✅ Tables are readable
- ✅ Numbers format with commas
- ✅ Color coding (green/red/amber) works
- ✅ Mobile responsive layout
- ✅ All sections display properly

---

## Common Issues & Solutions

### Issue: Email not sending
**Solution**: Check Gmail API authentication
```bash
./venv/bin/python setup_gmail_api.py
```

### Issue: Colors not showing
**Solution**: Some email clients strip CSS. The template uses inline styles which should work everywhere.

### Issue: Fonts look different
**Solution**: System fonts render differently on each platform. This is expected and provides a native look.

### Issue: Currency conversion incorrect
**Solution**: Verify rates in `app/currency_rates.py` or check `recipient.rate` in transaction data.

---

## Preview Tools

### Online Email Testing Tools

1. **Litmus** - https://litmus.com
   - Test across 90+ email clients
   - Screenshot previews

2. **Email on Acid** - https://www.emailonacid.com
   - Comprehensive testing
   - Spam filter testing

3. **Mailtrap** - https://mailtrap.io
   - Safe email testing environment
   - No risk of sending to real users

### Browser Testing

Simply open `test_email_output.html` in:
- Chrome
- Firefox
- Safari
- Edge

---

## Performance Metrics

Monitor these when testing:

1. **Email Generation Time**
   - Should be < 1 second
   - Check server logs

2. **Email Send Time**
   - Gmail API typically < 2 seconds
   - Check for rate limits

3. **Email Size**
   - HTML should be < 100KB
   - Images should be optimized

---

## Automated Testing

Create a test suite for email generation:

```python
# test_email_generation.py
import pytest
from app.email_service import generate_html_email, generate_plain_text_email

def test_email_generation():
    """Test that email generates without errors"""
    report_data = {...}  # Mock data
    
    html = generate_html_email(report_data)
    text = generate_plain_text_email(report_data)
    
    assert len(html) > 0
    assert len(text) > 0
    assert "#317CFF" in html  # Primary color present
    assert "Weekly Performance Report" in html
```

---

## Troubleshooting

### Check Gmail API Status
```bash
./venv/bin/python -c "from app.gmail_service import test_gmail_connection; test_gmail_connection()"
```

### Verify Database Connection
```bash
./venv/bin/python -c "from app.database import get_db; next(get_db())"
```

### Test Report Generation
```bash
curl http://localhost:8000/api/reports/weekly-performance?week_start_date=2026-01-13
```

---

## Next Steps

After successful testing:

1. Schedule automated sending (via n8n or cron)
2. Monitor delivery rates
3. Collect feedback from recipients
4. Iterate on design based on feedback
5. Add more metrics if needed

---

## Support

For issues or questions:
- Check `docs/WEEKLY_EMAIL_QUICK_START.md`
- Review `docs/EMAIL_TEMPLATE_IMPROVEMENTS.md`
- Check server logs in `server.log`
