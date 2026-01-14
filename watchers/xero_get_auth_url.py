#!/usr/bin/env python3
"""
Generate Xero OAuth Authorization URL
"""

import json
from pathlib import Path
from xero.auth import OAuth2Credentials

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "xero_credentials.json"

# Load credentials
with open(CREDENTIALS_FILE, 'r') as f:
    creds_data = json.load(f)

# Create OAuth2 credentials with full read/write scopes
credentials = OAuth2Credentials(
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret'],
    callback_uri=creds_data.get('redirect_uri', 'http://localhost:8080'),
    scope='accounting.transactions accounting.transactions.read accounting.contacts accounting.settings offline_access'
)

# Generate authorization URL
auth_url = credentials.generate_url()

print("=" * 70)
print("Xero OAuth Authorization URL")
print("=" * 70)
print("\nVisit this URL in your browser:")
print(f"\n{auth_url}\n")
print("=" * 70)
print("\nAfter authorizing, you'll be redirected to:")
print("http://localhost:8080/?code=XXXXX&...")
print("\nCopy the entire URL and provide it to complete authentication.")
print("=" * 70)
