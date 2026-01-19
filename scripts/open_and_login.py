#!/usr/bin/env python3
"""
Open Odoo, login, and keep browser open for manual API key creation.
"""

from playwright.sync_api import sync_playwright
import time

ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo"
ADMIN = "admin"
PASSWORD = "admin"

print("="*60)
print("Odoo API Key Setup - Login and Open")
print("="*60)
print(f"\nURL: {ODOO_URL}")
print(f"Database: {DB_NAME}")
print(f"Credentials: {ADMIN} / {PASSWORD}\n")
print("Instructions:")
print("1. Browser will open and login automatically")
print("2. Click your username (top right)")
print("3. Click 'Preferences'")
print("4. Look for 'Account Security' or 'API Keys'")
print("5. Click 'New API Key'")
print("6. Name it: AI Employee Integration")
print("7. Save the key")
print("8. Copy the key to Logs/odoo_api_key.txt")
print("="*60)

input("\nPress Enter to continue...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()

    print("\nLogging in...")
    page.goto(f"{ODOO_URL}/web/login?db={DB_NAME}")
    time.sleep(2)

    page.fill("input[name='login'], input#login", ADMIN)
    page.fill("input[name='password'], input#password", PASSWORD)
    page.click("button[type='submit']")

    print("Waiting for dashboard...")
    time.sleep(5)

    print(f"\nLogged in! URL: {page.url}")
    print("\nBrowser will stay open for you to create the API key.")
    print("Press Ctrl+C when done.\n")

    # Keep browser open
    input("Press Enter when finished...")

    browser.close()

print("\nDone!")
