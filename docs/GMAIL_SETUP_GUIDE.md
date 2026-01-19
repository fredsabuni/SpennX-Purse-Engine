# Gmail App Password Setup Guide

## Overview

To send emails via Gmail SMTP, you need to generate an **App Password** instead of using your regular Gmail password. This is more secure and required when 2-Factor Authentication is enabled.

---

## Step-by-Step Setup

### Step 1: Enable 2-Factor Authentication

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google", click on **2-Step Verification**
4. Follow the prompts to enable 2FA (if not already enabled)

### Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
   - Or navigate: Google Account → Security → 2-Step Verification → App passwords

2. You may need to sign in again

3. Under "Select app", choose **Mail**

4. Under "Select device", choose **Other (Custom name)**

5. Enter a name like: **SpennX Weekly Reports**

6. Click **Generate**

7. Google will display a 16-character password like: `abcd efgh ijkl mnop`

8. **Copy this password** (you won't be able to see it again)

### Step 3: Update .env File

Open your `.env` file and update the email configuration:

```env
WEEKLY_REPORT_SENDER_EMAIL=your-email@gmail.com
WEEKLY_REPORT_SENDER_PASSWORD=abcdefghijklmnop
WEEKLY_REPORT_SMTP_SERVER=smtp.gmail.com
WEEKLY_REPORT_SMTP_PORT=587
```

**Important Notes**:
- Replace `your-email@gmail.com` with your actual Gmail address
- Replace `abcdefghijklmnop` with the 16-character App Password (remove spaces)
- Keep the quotes if your password contains special characters

### Step 4: Restart the Server

After updating `.env`, restart your application:

```bash
# If using Docker
docker-compose restart

# If running directly
# Stop the server (Ctrl+C) and restart:
python -m uvicorn app.main:app --reload
```

---

## Testing Email Sending

### Test 1: Send to Yourself

```bash
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["your-email@gmail.com"]
  }'
```

### Test 2: Check Response

**Success Response**:
```json
{
  "success": true,
  "message": "Weekly performance email sent successfully",
  "subject": "Weekly Transaction Performance Report - Jan 13 to Jan 19, 2026",
  "recipients": ["your-email@gmail.com"],
  "report_summary": {...}
}
```

**Error Response** (if credentials not configured):
```json
{
  "detail": "Email credentials not configured. Set WEEKLY_REPORT_SENDER_PASSWORD environment variable with a valid Gmail App Password."
}
```

### Test 3: Check Your Inbox

1. Check your Gmail inbox
2. Look for email with subject: "Weekly Transaction Performance Report - ..."
3. Verify the email looks professional and all data is correct
4. Check on mobile to verify responsive design

---

## Troubleshooting

### Error: "Email credentials not configured"

**Cause**: Password not set or still has placeholder value

**Solution**:
1. Verify `.env` has the correct App Password
2. Make sure there are no spaces in the password
3. Restart the server after updating `.env`

### Error: "Failed to send email"

**Possible Causes**:
1. **Invalid App Password**: Generate a new one
2. **2FA not enabled**: Enable 2FA first
3. **Wrong email address**: Verify sender email is correct
4. **Network issues**: Check internet connection
5. **Gmail blocking**: Check Gmail security settings

**Solutions**:
1. Check server logs for detailed error message
2. Verify App Password is correct (try generating a new one)
3. Ensure 2FA is enabled on your Google Account
4. Check that sender email matches your Gmail address
5. Try sending to a different recipient

### Error: "Authentication failed"

**Cause**: Wrong password or 2FA not enabled

**Solution**:
1. Delete the old App Password in Google Account
2. Generate a new App Password
3. Update `.env` with the new password
4. Restart server

### Email Not Received

**Check**:
1. Spam/Junk folder
2. Gmail "Promotions" or "Updates" tab
3. Email filters/rules
4. Recipient email address is correct

**Test**:
- Send to a different email address (non-Gmail)
- Check server logs for send confirmation

### Gmail Daily Sending Limit

**Limit**: 500 emails per day for regular Gmail accounts

**If you hit the limit**:
- Wait 24 hours
- Consider using Google Workspace (higher limits)
- Use a dedicated email service (SendGrid, AWS SES, etc.)

---

## Security Best Practices

### ✅ Do's

- ✅ Use App Passwords (never your regular password)
- ✅ Store credentials in `.env` file (not in code)
- ✅ Add `.env` to `.gitignore`
- ✅ Use different App Passwords for different applications
- ✅ Revoke App Passwords you're not using
- ✅ Enable 2FA on your Google Account

### ❌ Don'ts

- ❌ Don't commit `.env` to version control
- ❌ Don't share your App Password
- ❌ Don't use your regular Gmail password
- ❌ Don't hardcode credentials in code
- ❌ Don't reuse App Passwords across projects

---

## Alternative Email Services

If Gmail doesn't work for your use case, consider:

### SendGrid
- Free tier: 100 emails/day
- Better deliverability
- More features (templates, analytics)
- Setup: https://sendgrid.com/

### AWS SES
- Pay-as-you-go pricing
- High volume support
- Requires AWS account
- Setup: https://aws.amazon.com/ses/

### Mailgun
- Free tier: 5,000 emails/month
- Good for transactional emails
- Setup: https://www.mailgun.com/

### To switch email service:

Update `app/email_service.py` `send_email()` function to use the new service's API.

---

## Gmail SMTP Settings Reference

```
Server: smtp.gmail.com
Port: 587 (TLS) or 465 (SSL)
Security: TLS/STARTTLS
Authentication: Required
Username: your-email@gmail.com
Password: 16-character App Password
```

---

## Verification Checklist

Before going to production:

- [ ] 2FA enabled on Google Account
- [ ] App Password generated
- [ ] `.env` file updated with correct credentials
- [ ] `.env` file in `.gitignore`
- [ ] Server restarted after configuration
- [ ] Test email sent successfully
- [ ] Email received and looks correct
- [ ] Email renders correctly on mobile
- [ ] Email renders correctly in different clients (Gmail, Outlook)
- [ ] Spam score checked (use mail-tester.com)
- [ ] Production recipient list configured
- [ ] Error handling tested
- [ ] Monitoring set up for email delivery

---

## Support

### Google Account Help
- App Passwords: https://support.google.com/accounts/answer/185833
- 2-Step Verification: https://support.google.com/accounts/answer/185839
- Gmail SMTP: https://support.google.com/mail/answer/7126229

### Project Documentation
- `WEEKLY_EMAIL_IMPLEMENTATION.md` - Technical documentation
- `WEEKLY_EMAIL_QUICK_START.md` - Quick start guide
- `test_weekly_report.py` - Test script

### Testing
```bash
# Run automated tests
python test_weekly_report.py

# Check server logs
docker-compose logs -f
# or
tail -f server.log
```

---

## Quick Reference

### Current Configuration (.env)
```env
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
WEEKLY_REPORT_SENDER_PASSWORD=your_gmail_app_password_here
WEEKLY_REPORT_SMTP_SERVER=smtp.gmail.com
WEEKLY_REPORT_SMTP_PORT=587
```

### Test Command
```bash
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["your-email@gmail.com"]
  }'
```

### Restart Server
```bash
docker-compose restart
# or
python -m uvicorn app.main:app --reload
```

---

**Ready to send emails!** 📧

Once you've completed the setup, your weekly email reports will be sent automatically via Gmail SMTP.
