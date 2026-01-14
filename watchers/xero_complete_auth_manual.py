#!/usr/bin/env python3
"""
Complete Xero OAuth authentication with manual code.
"""

import json
import requests
from pathlib import Path

def complete_auth(auth_code):
    """Complete OAuth flow with authorization code."""

    # Paths
    creds_path = Path(__file__).parent / 'credentials' / 'xero_credentials.json'
    token_path = Path(__file__).parent / 'credentials' / 'xero_token.json'

    # Load credentials
    with open(creds_path, 'r') as f:
        creds = json.load(f)

    client_id = creds['client_id']
    client_secret = creds['client_secret']
    redirect_uri = creds.get('redirect_uri', 'http://localhost:8080')

    print("=" * 70)
    print("Xero OAuth - Completing Authentication")
    print("=" * 70)
    print(f"Authorization code: {auth_code[:20]}...")
    print()

    # Exchange code for token
    print("Exchanging authorization code for access token...")

    url = "https://identity.xero.com/connect/token"

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }

    auth = (client_id, client_secret)

    try:
        response = requests.post(url, data=data, auth=auth)
        response.raise_for_status()

        token_data = response.json()

        print("[OK] Token received successfully!")
        print()
        print(f"Access token: {token_data['access_token'][:20]}...")
        print(f"Expires in: {token_data['expires_in']} seconds")
        print(f"Refresh token: {token_data['refresh_token'][:20]}...")
        print()

        # Save token
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)

        print(f"[OK] Token saved to: {token_path}")
        print()

        # Get tenant/organization info
        print("Fetching Xero organizations...")

        connections_url = "https://api.xero.com/connections"
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'Content-Type': 'application/json'
        }

        conn_response = requests.get(connections_url, headers=headers)
        conn_response.raise_for_status()

        connections = conn_response.json()

        print(f"[OK] Found {len(connections)} organization(s):")
        print()

        for idx, conn in enumerate(connections, 1):
            print(f"{idx}. {conn['tenantName']}")
            print(f"   Tenant ID: {conn['tenantId']}")
            print(f"   Type: {conn['tenantType']}")
            print()

        if connections:
            # Save first tenant to credentials
            creds['tenant_id'] = connections[0]['tenantId']
            creds['tenant_name'] = connections[0]['tenantName']

            with open(creds_path, 'w') as f:
                json.dump(creds, f, indent=2)

            print(f"[OK] Using tenant: {connections[0]['tenantName']}")
            print(f"[OK] Tenant ID saved to credentials")

        print()
        print("=" * 70)
        print("Authentication Complete!")
        print("=" * 70)
        print("You can now use the Xero watcher.")

        return True

    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    # The authorization code from the redirect URL
    auth_code = "OeoMnEHKEvXK5Fv1BdpQdbZYe_UpvCyWpfSQEOsePkw"
    complete_auth(auth_code)
