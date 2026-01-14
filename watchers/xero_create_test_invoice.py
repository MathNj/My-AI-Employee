#!/usr/bin/env python3
"""
Xero - Create Test Invoice
Creates a sample invoice to test the watcher functionality.
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
TOKEN_FILE = CREDENTIALS_DIR / "xero_token.json"
XERO_CREDENTIALS_FILE = CREDENTIALS_DIR / "xero_credentials.json"


def create_test_invoice():
    print("=" * 70)
    print("Xero - Create Test Invoice")
    print("=" * 70)

    # Load credentials and token
    with open(XERO_CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)

    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)

    tenant_id = creds.get('tenant_id')
    tenant_name = creds.get('tenant_name')
    access_token = token_data.get('access_token')

    print(f"\nOrganization: {tenant_name}")
    print(f"Tenant ID: {tenant_id}")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-tenant-id': tenant_id,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Step 1: Create a test contact (customer)
    print("\nStep 1: Creating test contact...")

    # Use timestamp to create unique contact name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    contact_data = {
        "Contacts": [{
            "Name": f"Test Customer AI-{timestamp}",
            "EmailAddress": f"test-{timestamp}@aiemployee.local",
            "ContactStatus": "ACTIVE"
        }]
    }

    try:
        response = requests.put(
            'https://api.xero.com/api.xro/2.0/Contacts',
            headers=headers,
            json=contact_data
        )

        if response.status_code in [200, 201]:
            contact = response.json()['Contacts'][0]
            contact_id = contact['ContactID']
            print(f"  [OK] Contact created: {contact['Name']}")
            print(f"       Contact ID: {contact_id}")
        else:
            print(f"  [ERROR] Failed to create contact: {response.status_code}")
            print(f"  Response: {response.text}")
            return

    except Exception as e:
        print(f"  [ERROR] {e}")
        return

    # Step 2: Create test invoice
    print("\nStep 2: Creating test invoice...")

    due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    invoice_date = datetime.now().strftime('%Y-%m-%d')

    invoice_data = {
        "Invoices": [{
            "Type": "ACCREC",  # Accounts Receivable (Sales Invoice)
            "Contact": {
                "ContactID": contact_id
            },
            "Date": invoice_date,
            "DueDate": due_date,
            "LineAmountTypes": "Exclusive",
            "LineItems": [
                {
                    "Description": "AI Employee Monitoring Service - Test",
                    "Quantity": 1,
                    "UnitAmount": 750.00,
                    "AccountCode": "200",  # Sales account
                    "TaxType": "NONE"
                },
                {
                    "Description": "Setup Fee - Watcher Configuration",
                    "Quantity": 1,
                    "UnitAmount": 250.00,
                    "AccountCode": "200",
                    "TaxType": "NONE"
                }
            ],
            "Status": "AUTHORISED"
        }]
    }

    try:
        response = requests.put(
            'https://api.xero.com/api.xro/2.0/Invoices',
            headers=headers,
            json=invoice_data
        )

        if response.status_code in [200, 201]:
            invoice = response.json()['Invoices'][0]
            print(f"  [OK] Invoice created successfully!")
            print(f"       Invoice Number: {invoice.get('InvoiceNumber', 'N/A')}")
            print(f"       Invoice ID: {invoice['InvoiceID']}")
            print(f"       Amount: ${invoice.get('Total', 0):.2f}")
            print(f"       Due Date: {invoice.get('DueDate', 'N/A')}")
            print(f"       Status: {invoice.get('Status', 'N/A')}")

            print("\n" + "=" * 70)
            print("SUCCESS!")
            print("=" * 70)
            print("\nThe Xero watcher should detect this invoice on its next check")
            print("(within 5 minutes, default check interval: 300 seconds)")
            print("\nTo test immediately, run:")
            print("  python watchers/xero_watcher.py")

        else:
            print(f"  [ERROR] Failed to create invoice: {response.status_code}")
            print(f"  Response: {response.text}")

    except Exception as e:
        print(f"  [ERROR] {e}")


if __name__ == "__main__":
    create_test_invoice()
