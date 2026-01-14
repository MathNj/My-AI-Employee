#!/usr/bin/env python3
"""
Xero OAuth 2.0 - Direct Token Exchange
Uses direct API calls to exchange authorization code for token.
"""

import sys
import json
import requests
from pathlib import Path

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "xero_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "xero_token.json"

TOKEN_URL = "https://identity.xero.com/connect/token"


def main():
    if len(sys.argv) < 2:
        print("Usage: python xero_direct_auth.py <authorization_code>")
        sys.exit(1)

    auth_code = sys.argv[1].strip()

    print("=" * 70)
    print("Xero OAuth 2.0 - Direct Token Exchange")
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
    print(f"Redirect URI: {redirect_uri}")

    print("\nExchanging authorization code for access token...")

    # Prepare token request
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }

    try:
        # Make token request
        response = requests.post(TOKEN_URL, data=token_data)

        if response.status_code != 200:
            print(f"\nError: Token request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)

        token = response.json()

        print(f"\n[OK] Access token received!")
        print(f"  Token type: {token.get('token_type', 'N/A')}")
        print(f"  Expires in: {token.get('expires_in', 'N/A')} seconds")
        print(f"  Scope: {token.get('scope', 'N/A')}")

        # Save token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token, f, indent=2)

        print(f"\n[OK] Token saved to: {TOKEN_FILE}")

        print("\n" + "=" * 70)
        print("SUCCESS! Xero authentication complete")
        print("=" * 70)
        print("\nYou can now run the Xero watcher:")
        print("  python watchers/xero_watcher.py")

    except requests.exceptions.RequestException as e:
        print(f"\nNetwork error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
