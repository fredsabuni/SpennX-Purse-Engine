#!/usr/bin/env python3
"""
Extract OAuth2 tokens for server deployment.

This script reads your local token.pickle file and extracts the necessary
tokens for server deployment. Run this locally, then set the environment
variables on your server.

Usage:
    python extract_tokens.py
"""

import pickle
import os

def extract_tokens():
    """Extract tokens from token.pickle for server deployment."""
    
    token_file = 'token.pickle'
    
    if not os.path.exists(token_file):
        print(f"❌ {token_file} not found!")
        print("Please run the application locally first to generate tokens.")
        return
    
    try:
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
        
        print("🔐 OAuth2 Tokens for Server Deployment")
        print("=" * 50)
        print(f"GMAIL_CLIENT_ID={creds.client_id}")
        print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
        print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
        print("=" * 50)
        print("\n📝 To deploy on server:")
        print("1. Set these as environment variables")
        print("2. Do NOT commit these values to Git")
        print("3. Use a secure method to transfer to server")
        
        # Also create a .env.example file
        with open('.env.server.example', 'w') as f:
            f.write("# Server Environment Variables\n")
            f.write("# Copy these to your server's .env file\n")
            f.write(f"GMAIL_CLIENT_ID={creds.client_id}\n")
            f.write(f"GMAIL_CLIENT_SECRET={creds.client_secret}\n")
            f.write(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}\n")
            f.write("GMAIL_SENDER_EMAIL=your_email@gmail.com\n")
        
        print(f"\n✅ Server environment template saved to: .env.server.example")
        print("⚠️  Remember to add this file to .gitignore!")
        
    except Exception as e:
        print(f"❌ Error reading tokens: {e}")

if __name__ == "__main__":
    extract_tokens()