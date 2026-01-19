#!/usr/bin/env python3
"""
Gmail API Setup Script

This script helps you authenticate with Gmail API and test the connection.
Run this before using the weekly email feature for the first time.
"""

import os
import sys

def check_credentials():
    """Check if credentials.json exists"""
    if not os.path.exists('credentials.json'):
        print("❌ ERROR: credentials.json not found!")
        print("\nPlease ensure credentials.json is in the project root directory.")
        print("The file should contain your Gmail API OAuth2 credentials.")
        return False
    
    print("✅ credentials.json found")
    return True

def authenticate():
    """Authenticate with Gmail API"""
    try:
        from app.gmail_service import test_gmail_connection, send_test_email
        
        print("\n" + "="*60)
        print("Gmail API Authentication")
        print("="*60)
        print("\nThis will open a browser window for Gmail authentication.")
        print("Please:")
        print("1. Sign in with your Gmail account")
        print("2. Grant the requested permissions (gmail.send)")
        print("3. The token will be saved for future use")
        print("\nPress Enter to continue...")
        input()
        
        print("\nAuthenticating...")
        success = test_gmail_connection()
        
        if success:
            print("\n" + "="*60)
            print("✅ SUCCESS! Gmail API is configured and ready to use.")
            print("="*60)
            print("\nA token.pickle file has been created.")
            print("This file stores your authentication token.")
            
            # Offer to send test email
            print("\n" + "="*60)
            print("Would you like to send a test email?")
            print("="*60)
            test_email = input("\nEnter your email address (or press Enter to skip): ").strip()
            
            if test_email:
                print("\nSending test email...")
                if send_test_email(test_email):
                    print("\n✅ Test email sent! Check your inbox.")
                else:
                    print("\n⚠️  Test email failed. But authentication is complete.")
                    print("You can still use the weekly report endpoint.")
            
            print("\n" + "="*60)
            print("You can now send emails using the weekly report endpoint!")
            print("="*60)
            return True
        else:
            print("\n" + "="*60)
            print("❌ FAILED! Could not authenticate with Gmail API.")
            print("="*60)
            print("\nPlease check:")
            print("1. credentials.json is valid")
            print("2. You have internet connection")
            print("3. You granted all requested permissions")
            return False
            
    except ImportError as e:
        print(f"\n❌ ERROR: Missing required packages")
        print(f"Error: {e}")
        print("\nPlease install required packages:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("Gmail API Setup for Weekly Email Reports")
    print("="*60)
    
    # Check credentials file
    if not check_credentials():
        sys.exit(1)
    
    # Authenticate
    if not authenticate():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start your API server")
    print("2. Test the email endpoint:")
    print("\n   curl -X POST 'http://localhost:8000/api/reports/weekly-email' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "week_start_date": "2026-01-13",')
    print('       "recipients": ["your-email@gmail.com"]')
    print("     }'")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
