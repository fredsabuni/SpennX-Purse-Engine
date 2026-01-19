"""
Gmail API Service Module

Handles Gmail API authentication and email sending using OAuth2 credentials.
"""

import os
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Paths
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'


def get_gmail_service():
    """
    Get authenticated Gmail API service.
    
    Returns:
        Gmail API service object
    """
    creds = None
    
    # Check if token.pickle exists (stores user's access and refresh tokens)
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                # Delete invalid token and re-authenticate
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file '{CREDENTIALS_FILE}' not found. "
                    "Please ensure credentials.json is in the project root."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        raise


def create_message(sender: str, to: List[str], subject: str, html_content: str, plain_text_content: str):
    """
    Create a message for an email.
    
    Args:
        sender: Email address of the sender
        to: List of recipient email addresses
        subject: Email subject
        html_content: HTML email content
        plain_text_content: Plain text email content
    
    Returns:
        An object containing a base64url encoded email object
    """
    message = MIMEMultipart('alternative')
    message['to'] = ', '.join(to)
    message['from'] = sender
    message['subject'] = subject
    
    # Attach plain text and HTML versions
    part1 = MIMEText(plain_text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    
    message.attach(part1)
    message.attach(part2)
    
    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def send_gmail_message(
    recipients: List[str],
    subject: str,
    html_content: str,
    plain_text_content: str,
    sender_email: str = None
) -> bool:
    """
    Send email using Gmail API.
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        html_content: HTML email content
        plain_text_content: Plain text email content
        sender_email: Sender email address (optional, uses 'me' if not provided)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Get Gmail service
        service = get_gmail_service()
        
        # Use 'me' as sender if not specified (authenticated user)
        if not sender_email:
            sender_email = 'me'
        
        # Create message
        message = create_message(
            sender=sender_email,
            to=recipients,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text_content
        )
        
        # Send message
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        print(f"Email sent successfully. Message ID: {sent_message['id']}")
        return True
        
    except HttpError as error:
        print(f'An error occurred while sending email: {error}')
        return False
    except FileNotFoundError as error:
        print(f'Credentials file not found: {error}')
        return False
    except Exception as error:
        print(f'Unexpected error while sending email: {error}')
        return False


def test_gmail_connection():
    """
    Test Gmail API connection by attempting to get the service.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        service = get_gmail_service()
        
        # Just verify we can get the service
        # We don't need to call any API methods since we only have send scope
        print(f"Successfully connected to Gmail API")
        print(f"Scope: gmail.send (authorized to send emails)")
        print(f"Service initialized successfully")
        
        return True
    except Exception as e:
        print(f"Failed to connect to Gmail API: {e}")
        return False


def send_test_email(recipient: str) -> bool:
    """
    Send a test email to verify Gmail API is working.
    
    Args:
        recipient: Email address to send test email to
    
    Returns:
        True if test email sent successfully, False otherwise
    """
    try:
        print(f"\nSending test email to {recipient}...")
        
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #317CFF;">Gmail API Test Email</h2>
                <p>This is a test email from your SpennX Dashboard API.</p>
                <p>If you received this email, your Gmail API integration is working correctly! ✅</p>
                <hr>
                <p style="color: #6B7280; font-size: 12px;">
                    Sent via Gmail API using OAuth2 authentication
                </p>
            </body>
        </html>
        """
        
        plain_text = """
        Gmail API Test Email
        
        This is a test email from your SpennX Dashboard API.
        
        If you received this email, your Gmail API integration is working correctly!
        
        ---
        Sent via Gmail API using OAuth2 authentication
        """
        
        success = send_gmail_message(
            recipients=[recipient],
            subject="Gmail API Test - SpennX Dashboard",
            html_content=html_content,
            plain_text_content=plain_text,
            sender_email=None  # Uses authenticated user
        )
        
        if success:
            print(f"✅ Test email sent successfully to {recipient}")
            print(f"Please check your inbox to confirm delivery.")
            return True
        else:
            print(f"❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False
