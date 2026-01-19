# Gmail API Setup Guide

## Overview

The weekly email report feature now uses **Gmail API** instead of SMTP. This is more reliable, secure, and doesn't require App Passwords.

Your `credentials.json` file is already in place! ✅

---

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`

### Step 2: Authenticate with Gmail API

```bash
python setup_gmail_api.py
```

This will:
1. Open a browser window
2. Ask you to sign in with your Gmail account
3. Request permission to send emails
4. Save authentication token to `token.pickle`

**Important**: Sign in with the Gmail account you want to send emails from (e.g., finance@spennx.com)

### Step 3: Test Email Sending

```bash
# Start your server
python -m uvicorn app.main:app --reload

# In another terminal, test the endpoint
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["your-email@gmail.com"]
  }'
```

---

## How It Works

### Authentication Flow

1. **First Time**:
   - Run `setup_gmail_api.py`
   - Browser opens for Gmail sign-in
   - Grant permissions
   - Token saved to `token.pickle`

2. **Subsequent Uses**:
   - API automatically uses `token.pickle`
   - No browser interaction needed
   - Token auto-refreshes when expired

### Files

- **`credentials.json`** ✅ (Already present)
  - OAuth2 client credentials
  - Contains client ID and secret
  - Safe to commit (doesn't contain passwords)

- **`token.pickle`** (Created after authentication)
  - User's access and refresh tokens
  - **DO NOT commit to git** (add to `.gitignore`)
  - Automatically refreshed when expired

---

## Detailed Setup Instructions

### Prerequisites

1. ✅ `credentials.json` file (already present)
2. Gmail account to send from
3. Python 3.8+ installed
4. Internet connection

### Step-by-Step Setup

#### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

**Packages installed**:
```
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.116.0
```

#### 2. Run Authentication Script

```bash
python setup_gmail_api.py
```

**What happens**:
```
Gmail API Setup for Weekly Email Reports
============================================================
✅ credentials.json found

Gmail API Authentication
============================================================

This will open a browser window for Gmail authentication.
Please:
1. Sign in with your Gmail account
2. Grant the requested permissions
3. The token will be saved for future use

Press Enter to continue...
```

Press Enter, then:

1. **Browser opens** with Google sign-in
2. **Sign in** with your Gmail account (e.g., finance@spennx.com)
3. **Grant permissions**:
   - "Send email on your behalf"
   - Click "Allow"
4. **Success message** appears

**Output**:
```
✅ SUCCESS! Gmail API is configured and ready to use.
============================================================

A token.pickle file has been created.
This file stores your authentication token.

You can now send emails using the weekly report endpoint!
```

#### 3. Verify Setup

Check that `token.pickle` was created:

```bash
ls -la token.pickle
```

You should see:
```
-rw-r--r--  1 user  staff  1234 Jan 18 10:30 token.pickle
```

#### 4. Test Email Sending

**Start the server**:
```bash
python -m uvicorn app.main:app --reload
```

**Send test email**:
```bash
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["your-email@gmail.com"]
  }'
```

**Expected response**:
```json
{
  "success": true,
  "message": "Weekly performance email sent successfully via Gmail API",
  "subject": "Weekly Transaction Performance Report - Jan 13 to Jan 19, 2026",
  "recipients": ["your-email@gmail.com"],
  "report_summary": {...}
}
```

**Check your inbox** for the email!

---

## Configuration

### Environment Variables

Update your `.env` file:

```env
# Weekly Email Report Configuration (Gmail API)
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
```

**Note**: No password needed! Gmail API uses OAuth2 authentication.

### Sender Email

The sender email is optional. If not specified, the API uses the authenticated Gmail account.

To specify a sender:
```env
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
```

---

## Troubleshooting

### Issue: "credentials.json not found"

**Cause**: File is missing or in wrong location

**Solution**:
1. Ensure `credentials.json` is in project root
2. Check file name is exactly `credentials.json`
3. Verify file contains valid JSON

### Issue: "Failed to authenticate"

**Cause**: Browser didn't open or permissions not granted

**Solution**:
1. Check internet connection
2. Try running `setup_gmail_api.py` again
3. Ensure you click "Allow" in the browser
4. Check for browser pop-up blockers

### Issue: "Token expired"

**Cause**: Authentication token expired

**Solution**:
- Token auto-refreshes automatically
- If issues persist, delete `token.pickle` and re-authenticate:
  ```bash
  rm token.pickle
  python setup_gmail_api.py
  ```

### Issue: "Email not sent"

**Possible causes**:
1. Token not valid
2. No internet connection
3. Gmail API quota exceeded

**Solutions**:
1. Re-authenticate: `python setup_gmail_api.py`
2. Check internet connection
3. Check Gmail API quotas in Google Cloud Console
4. Check server logs for detailed error

### Issue: "Permission denied"

**Cause**: Gmail API not enabled or insufficient permissions

**Solution**:
1. Ensure Gmail API is enabled in Google Cloud Console
2. Re-authenticate with correct permissions
3. Check OAuth consent screen configuration

---

## Gmail API Quotas

### Free Tier Limits

- **Sending quota**: 100 emails per day (for testing)
- **Production quota**: Request higher limits in Google Cloud Console

### Quota Management

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Navigate to: APIs & Services → Gmail API → Quotas
4. Request quota increase if needed

---

## Security Best Practices

### ✅ Do's

- ✅ Keep `credentials.json` secure
- ✅ Add `token.pickle` to `.gitignore`
- ✅ Use OAuth2 (no passwords in code)
- ✅ Regularly review authorized apps in Gmail
- ✅ Use service accounts for production

### ❌ Don'ts

- ❌ Don't commit `token.pickle` to git
- ❌ Don't share `token.pickle` file
- ❌ Don't hardcode credentials in code
- ❌ Don't use personal Gmail for production

---

## Production Deployment

### Recommended Setup

1. **Use Service Account** (for automated sending)
   - Create service account in Google Cloud Console
   - Download service account key
   - Use domain-wide delegation

2. **Or Use OAuth2 with Refresh Token**
   - Authenticate once
   - Store refresh token securely
   - Auto-refresh access tokens

### Service Account Setup

1. Go to Google Cloud Console
2. Create service account
3. Enable domain-wide delegation
4. Grant Gmail send permissions
5. Download key file
6. Update code to use service account

---

## File Structure

```
project/
├── credentials.json          # OAuth2 credentials (✅ present)
├── token.pickle             # Auth token (created after setup)
├── setup_gmail_api.py       # Setup script
├── app/
│   ├── gmail_service.py     # Gmail API service
│   ├── email_service.py     # Email template & sending
│   └── main.py              # API endpoints
└── .env                     # Configuration
```

---

## Testing Checklist

- [ ] `credentials.json` present in project root
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Authenticated with Gmail (`python setup_gmail_api.py`)
- [ ] `token.pickle` created
- [ ] Server starts without errors
- [ ] Test email sent successfully
- [ ] Email received in inbox
- [ ] Email looks professional
- [ ] Mobile view works

---

## Comparison: Gmail API vs SMTP

| Feature | Gmail API | SMTP |
|---------|-----------|------|
| Authentication | OAuth2 | Password/App Password |
| Security | ✅ More secure | ⚠️ Less secure |
| Setup | Browser auth once | Password in .env |
| Reliability | ✅ Higher | ⚠️ Lower |
| Rate Limits | 100/day (free) | 500/day |
| Token Refresh | ✅ Automatic | N/A |
| Production Ready | ✅ Yes | ⚠️ Not recommended |

---

## Support

### Documentation
- Gmail API: https://developers.google.com/gmail/api
- Python Client: https://github.com/googleapis/google-api-python-client
- OAuth2: https://developers.google.com/identity/protocols/oauth2

### Project Documentation
- `WEEKLY_EMAIL_IMPLEMENTATION.md` - Technical docs
- `WEEKLY_EMAIL_QUICK_START.md` - Quick start guide
- `GMAIL_API_SETUP.md` - This file

### Testing
```bash
# Test Gmail API connection
python setup_gmail_api.py

# Test email endpoint
python test_weekly_report.py

# Check server logs
tail -f server.log
```

---

## Quick Reference

### Setup Command
```bash
python setup_gmail_api.py
```

### Test Email
```bash
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["test@example.com"]
  }'
```

### Re-authenticate
```bash
rm token.pickle
python setup_gmail_api.py
```

### Check Token
```bash
ls -la token.pickle
```

---

## Summary

✅ **Gmail API is configured and ready!**

**Next steps**:
1. Run `python setup_gmail_api.py` to authenticate
2. Test email sending
3. Set up n8n automation (optional)

**Advantages**:
- More secure (OAuth2)
- No passwords in code
- Automatic token refresh
- Better reliability
- Production-ready

---

*Setup guide for Gmail API integration*  
*Updated: January 18, 2026*
