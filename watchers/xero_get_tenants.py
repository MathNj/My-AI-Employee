#!/usr/bin/env python3
"""
Xero - Get Available Tenants/Organizations
Fetches the list of organizations the authenticated user has access to.
"""

import json
import requests
from pathlib import Path

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
TOKEN_FILE = CREDENTIALS_DIR / "xero_token.json"
XERO_CREDENTIALS_FILE = CREDENTIALS_DIR / "xero_credentials.json"

CONNECTIONS_URL = "https://api.xero.com/connections"


def main():
    print("=" * 70)
    print("Xero - Fetch Available Organizations")
    print("=" * 70)

    # Load token
    if not TOKEN_FILE.exists():
        print(f"Error: Token file not found at {TOKEN_FILE}")
        print("Please run authentication first.")
        return

    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)

    access_token = token_data.get('access_token')
    if not access_token:
        print("Error: No access token found in token file")
        return

    print(f"\nAccess token: {access_token[:30]}...")
    print("\nFetching connected organizations...")

    # Request headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        # Get connections
        response = requests.get(CONNECTIONS_URL, headers=headers)

        if response.status_code != 200:
            print(f"\nError: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return

        connections = response.json()

        if not connections:
            print("\nNo organizations found.")
            print("Make sure you authorized access to at least one organization.")
            return

        print(f"\n[OK] Found {len(connections)} organization(s):\n")

        for i, conn in enumerate(connections, 1):
            print(f"{i}. {conn.get('tenantName', 'Unknown')}")
            print(f"   Tenant ID: {conn.get('tenantId')}")
            print(f"   Type: {conn.get('tenantType', 'N/A')}")
            print(f"   Created: {conn.get('createdDateUtc', 'N/A')}")
            print()

        # If only one organization, auto-select it
        if len(connections) == 1:
            selected = connections[0]
            tenant_id = selected['tenantId']
            tenant_name = selected.get('tenantName', 'Unknown')

            print("=" * 70)
            print(f"Auto-selecting: {tenant_name}")
            print(f"Tenant ID: {tenant_id}")
            print("=" * 70)

            # Update credentials file with tenant ID
            if XERO_CREDENTIALS_FILE.exists():
                with open(XERO_CREDENTIALS_FILE, 'r') as f:
                    creds = json.load(f)

                creds['tenant_id'] = tenant_id
                creds['tenant_name'] = tenant_name

                with open(XERO_CREDENTIALS_FILE, 'w') as f:
                    json.dump(creds, f, indent=2)

                print(f"\n[OK] Tenant ID saved to credentials file")
                print("\nYou can now run the Xero watcher with real data:")
                print("  python watchers/xero_watcher.py")
            else:
                print(f"\nTenant ID: {tenant_id}")
                print("Manually add this to your xero_credentials.json file")

        else:
            print("=" * 70)
            print("Multiple organizations found.")
            print("Please select one and add its tenant_id to xero_credentials.json")
            print("=" * 70)

    except requests.exceptions.RequestException as e:
        print(f"\nNetwork error: {e}")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
