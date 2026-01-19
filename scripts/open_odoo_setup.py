#!/usr/bin/env python3
"""
Simple script to open Odoo setup in browser for manual completion.
"""

import webbrowser
import time

ODOO_URL = "http://localhost:8069"
DB_MANAGER_URL = f"{ODOO_URL}/web/database/manager"

print("="*60)
print("Odoo 19 Setup - Browser Launcher")
print("="*60)
print()
print("This will open your browser to the Odoo database manager.")
print()
print("Steps to complete:")
print("1. Click 'Create Database'")
print("2. Fill in:")
print("   - Database name: odoo_production")
print("   - Email: admin@example.com")
print("   - Password: Admin@123456")
print("   - Language: English")
print("   - Country: United States")
print("3. Click 'Create' and wait 2-3 minutes")
print("4. Log in with the credentials you created")
print("5. Go to: Preferences -> Account Security -> New API Key")
print("6. Name it 'AI Employee Integration' and save the key")
print()
print(f"Database Manager URL: {DB_MANAGER_URL}")
print("="*60)
print()

input("Press Enter to open browser...")

# Open browser to database manager
print(f"Opening {DB_MANAGER_URL}...")
webbrowser.open(DB_MANAGER_URL)

print()
print("Browser opened! Please complete the setup following the steps above.")
print()
print("Once you have the API key, save it to: Logs/odoo_api_key.txt")
print("Format:")
print("  ODOO_URL=http://localhost:8069")
print("  ODOO_DB=odoo_production")
print("  ODOO_API_KEY=your_api_key_here")
print("  ODOO_ADMIN_EMAIL=admin@example.com")
print("  ODOO_ADMIN_PASSWORD=Admin@123456")
