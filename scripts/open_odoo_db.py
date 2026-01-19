#!/usr/bin/env python3
"""
Open browser to odoo database and login.
"""

import webbrowser
import time

ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo"
ADMIN = "admin"
PASSWORD = "admin"

print("="*60)
print("Odoo Login - 'odoo' Database")
print("="*60)
print(f"\nDatabase: {DB_NAME}")
print(f"Credentials: {ADMIN} / {PASSWORD}")
print("\nOpening browser to database...")

# Open directly to the database
url = f"{ODOO_URL}/web?db={DB_NAME}"
webbrowser.open(url)

print("\n" + "="*60)
print("Browser opened!")
print("="*60)
print("\nIf you see a login page:")
print("  Username: admin")
print("  Password: admin")
print("\nOnce logged in, create API key:")
print("  1. Click your username (top right)")
print("  2. Click 'Preferences'")
print("  3. Find 'Account Security' or 'API Keys'")
print("  4. Click 'New API Key'")
print("  5. Name it: AI Employee Integration")
print("  6. Save the key")
print("\nThen save to: Logs/odoo_api_key.txt")
print("="*60)
