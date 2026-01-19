# Server Email Setup Guide

## Security Warning
⚠️ **Never upload `token.pickle` or `credentials.json` to your repository or server via Git!**

## Production Deployment Options

### Option 1: Service Account (Recommended)
1. Create a Google Service Account in Google Cloud Console
2. Enable Gmail API for the service account
3. Download the service account JSON key
4. Use service account authentication instead of OAuth2

### Option 2: Secure Token Transfer
1. Generate `token.pickle` locally using your current setup
2. Securely transfer it to server via:
   - SCP/SFTP
   - Environment variables (base64 encoded)
   - Cloud secret management (AWS Secrets Manager, Azure Key Vault, etc.)

### Option 3: Environment Variables
Store authentication data as environment variables:

```bash
# On your server
export GMAIL_CLIENT_ID="your_client_id"
export GMAIL_CLIENT_SECRET="your_client_secret"
export GMAIL_REFRESH_TOKEN="your_refresh_token"
```

## Server Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file on the server (not in Git):
```
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
GMAIL_SENDER_EMAIL=your_email@gmail.com
```

### 3. Modify Gmail Service for Environment Variables
Update `app/gmail_service.py` to use environment variables when `token.pickle` is not available.

### 4. Test Email Functionality
```bash
python -m pytest tests/test_email_gen.py -v
```

## Security Checklist
- [ ] `credentials.json` is in `.gitignore`
- [ ] `token.pickle` is in `.gitignore`
- [ ] `.env` is in `.gitignore`
- [ ] Sensitive data transferred securely to server
- [ ] Server has restricted access permissions
- [ ] Regular rotation of credentials/tokens