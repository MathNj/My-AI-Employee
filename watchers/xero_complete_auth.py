#!/usr/bin/env python3
"""
Xero OAuth 2.0 - Complete Authentication
Exchanges authorization code for access token.

Usage:
    python xero_complete_auth.py <authorization_code>
"""

import sys
import json
import os
from pathlib import Path
from xero.auth import OAuth2Credentials

# Allow OAuth over HTTP for localhost (development only)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "xero_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "xero_token.json"


def main():
    if len(sys.argv) < 2:
        print("Usage: python xero_complete_auth.py <authorization_code>")
        print("\nTo get the authorization code:")
        print("1. Visit the authorization URL")
        print("2. After authorizing, copy the 'code' parameter from the redirect URL")
        sys.exit(1)

    auth_code = sys.argv[1].strip()

    print("=" * 70)
    print("Xero OAuth 2.0 - Completing Authentication")
    print("=" * 70)

    # Load credentials
    if not CREDENTIALS_FILE.exists():
        print(f"Error: Credentials file not found at {CREDENTIALS_FILE}")
        sys.exit(1)

    with open(CREDENTIALS_FILE, 'r') as f:
        creds_data = json.load(f)

    client_id = creds_data['client_id']
    client_secret = creds_data['client_secret']
    redirect_uri = creds_data.get('redirect_uri', 'http://localhost:8080')

    print(f"\nClient ID: {client_id[:20]}...")
    print(f"Authorization code: {auth_code[:20]}...")

    # Create OAuth2 credentials
    credentials = OAuth2Credentials(
        client_id=client_id,
        client_secret=client_secret,
        callback_uri=redirect_uri,
        scope='accounting.transactions accounting.settings'
    )

    print("\nExchanging authorization code for access token...")

    try:
        # Exchange code for token
        credentials.verify(auth_code)
        token = credentials.token

        print(f"\n✓ Access token received!")
        print(f"  Token type: {token.get('token_type', 'N/A')}")
        print(f"  Expires in: {token.get('expires_in', 'N/A')} seconds")

        # Save token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token, f, indent=2)

        print(f"\n✓ Token saved to: {TOKEN_FILE}")

        print("\n" + "=" * 70)
        print("SUCCESS! Xero authentication complete")
        print("=" * 70)
        print("\nYou can now run the Xero watcher:")
        print("  python watchers/xero_watcher.py")

    except Exception as e:
        print(f"\nError exchanging code for token: {e}")
        print("\nPossible issues:")
        print("- The authorization code may have expired (they're single-use)")
        print("- The redirect URI might not match what's configured in Xero")
        print("- The code may have been copied incorrectly")
        sys.exit(1)


if __name__ == "__main__":
    main()
