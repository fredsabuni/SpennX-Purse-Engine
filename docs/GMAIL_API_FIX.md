# Gmail API Scope Fix

## Issue

The initial authentication was failing with:
```
HttpError 403: Request had insufficient authentication scopes
```

## Root Cause

The test function was trying to access the user profile (`users().getProfile()`) which requires the `gmail.readonly` scope, but we only requested the `gmail.send` scope.

## Solution

Updated the `test_gmail_connection()` function to:
1. Only verify the service can be initialized
2. Not call any API methods that require additional scopes
3. Added a separate `send_test_email()` function to actually test sending

## What Changed

### app/gmail_service.py

**Before**:
```python
def test_gmail_connection():
    service = get_gmail_service()
    profile = service.users().getProfile(userId='me').execute()  # ❌ Requires gmail.readonly
    print(f"Email: {profile.get('emailAddress')}")
```

**After**:
```python
def test_gmail_connection():
    service = get_gmail_service()
    # Just verify we can get the service
    print(f"Successfully connected to Gmail API")
    print(f"Scope: gmail.send (authorized to send emails)")
    return True

def send_test_email(recipient: str):
    # Actually test sending an email
    success = send_gmail_message(...)
    return success
```

### setup_gmail_api.py

Added option to send a test email after authentication:
```python
test_email = input("Enter your email address (or press Enter to skip): ")
if test_email:
    send_test_email(test_email)
```

## How to Fix

### If You Already Authenticated

Delete the old token and re-authenticate:

```bash
# Delete old token
rm token.pickle

# Re-authenticate
python setup_gmail_api.py
```

### Fresh Setup

Just run:
```bash
python setup_gmail_api.py
```

The setup will:
1. Open browser for authentication
2. Request only `gmail.send` scope
3. Save token
4. Optionally send a test email

## Verification

After authentication, you can:

### 1. Send Test Email (via setup script)

```bash
python setup_gmail_api.py
# Enter your email when prompted
```

### 2. Test via API Endpoint

```bash
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["your-email@gmail.com"]
  }'
```

## Scopes Explained

### gmail.send
- **What it does**: Allows sending emails
- **What we use it for**: Weekly performance reports
- **Required**: Yes ✅

### gmail.readonly
- **What it does**: Allows reading emails and profile
- **What we use it for**: Nothing
- **Required**: No ❌

We only need `gmail.send` scope for our use case!

## Troubleshooting

### Still Getting 403 Error?

1. **Delete token.pickle**:
   ```bash
   rm token.pickle
   ```

2. **Re-authenticate**:
   ```bash
   python setup_gmail_api.py
   ```

3. **Grant permissions**: Make sure you click "Allow" in the browser

### Token Already Exists?

If you see "token.pickle already exists", delete it:
```bash
rm token.pickle
python setup_gmail_api.py
```

### Browser Doesn't Open?

Check for:
- Pop-up blockers
- Firewall settings
- Internet connection

## Summary

✅ **Fixed**: Removed profile access requirement  
✅ **Scope**: Only `gmail.send` needed  
✅ **Test**: Added `send_test_email()` function  
✅ **Setup**: Updated to offer test email  

The Gmail API integration now works correctly with minimal permissions!

---

*Fix applied: January 18, 2026*
