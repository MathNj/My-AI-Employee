#!/usr/bin/env python3
"""
Simple script to refresh Xero OAuth token using refresh token.
"""

import json
import requests
from pathlib import Path

def refresh_xero_token():
    """Refresh the Xero access token using the refresh token."""

    # Paths
    creds_path = Path(__file__).parent / 'credentials' / 'xero_credentials.json'
    token_path = Path(__file__).parent / 'credentials' / 'xero_token.json'

    # Load credentials
    with open(creds_path, 'r') as f:
        creds = json.load(f)

    # Load current token
    with open(token_path, 'r') as f:
        token_data = json.load(f)

    client_id = creds['client_id']
    client_secret = creds['client_secret']
    refresh_token = token_data['refresh_token']

    print("=" * 70)
    print("Xero Token Refresh")
    print("=" * 70)
    print(f"Client ID: {client_id[:20]}...")
    print(f"Refresh Token: {refresh_token[:20]}...")
    print()

    # Request new token
    print("Refreshing token...")

    url = "https://identity.xero.com/connect/token"

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    auth = (client_id, client_secret)

    try:
        response = requests.post(url, data=data, auth=auth)
        response.raise_for_status()

        new_token = response.json()

        print("[OK] Token refreshed successfully!")
        print()
        print(f"New access token: {new_token['access_token'][:20]}...")
        print(f"Expires in: {new_token['expires_in']} seconds")
        print(f"New refresh token: {new_token['refresh_token'][:20]}...")
        print()

        # Save new token
        with open(token_path, 'w') as f:
            json.dump(new_token, f, indent=2)

        print(f"[OK] Token saved to: {token_path}")
        print()
        print("=" * 70)
        print("Token refresh complete!")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR] Error refreshing token: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

    return True

if __name__ == "__main__":
    refresh_xero_token()
