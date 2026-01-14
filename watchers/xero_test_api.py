#!/usr/bin/env python3
"""
Xero API Test - Verify connection and data access
"""

import json
import requests
from pathlib import Path

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
TOKEN_FILE = CREDENTIALS_DIR / "xero_token.json"
XERO_CREDENTIALS_FILE = CREDENTIALS_DIR / "xero_credentials.json"


def test_xero_api():
    print("=" * 70)
    print("Xero API Connection Test")
    print("=" * 70)

    # Load credentials
    with open(XERO_CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)

    tenant_id = creds.get('tenant_id')
    tenant_name = creds.get('tenant_name')

    # Load token
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)

    access_token = token_data.get('access_token')

    print(f"\nOrganization: {tenant_name}")
    print(f"Tenant ID: {tenant_id}")
    print(f"Access Token: {access_token[:30]}...")

    # Headers for API requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-tenant-id': tenant_id,
        'Accept': 'application/json'
    }

    # Test endpoints
    endpoints = {
        'Invoices': 'https://api.xero.com/api.xro/2.0/Invoices',
        'Contacts': 'https://api.xero.com/api.xro/2.0/Contacts',
        'Accounts': 'https://api.xero.com/api.xro/2.0/Accounts',
        'Organisation': 'https://api.xero.com/api.xro/2.0/Organisation'
    }

    print("\n" + "=" * 70)
    print("Testing API Endpoints")
    print("=" * 70)

    for name, url in endpoints.items():
        print(f"\n{name}:")
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if name == 'Organisation':
                    orgs = data.get('Organisations', [])
                    if orgs:
                        org = orgs[0]
                        print(f"  [OK] Organisation: {org.get('Name')}")
                        print(f"       Version: {org.get('Version', 'N/A')}")
                        print(f"       Country: {org.get('CountryCode', 'N/A')}")
                else:
                    items_key = name
                    items = data.get(items_key, [])
                    print(f"  [OK] Found {len(items)} {name.lower()}")

                    if items and len(items) > 0:
                        print(f"       Sample: {items[0].get('Name', items[0].get('ContactID', 'N/A'))}")
            else:
                print(f"  [ERROR] Status {response.status_code}")
                print(f"  Response: {response.text[:200]}")

        except Exception as e:
            print(f"  [ERROR] {e}")

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    test_xero_api()
