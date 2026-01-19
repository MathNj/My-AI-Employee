#!/usr/bin/env python3
"""
Open Odoo to the correct database and login.
"""

from playwright.sync_api import sync_playwright
import time

ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo"
ADMIN = "admin"
PASSWORD = "admin"

print("="*60)
print("Odoo Login - Opening to Database")
print("="*60)
print(f"\nDatabase: {DB_NAME}")
print(f"Credentials: {ADMIN} / {PASSWORD}")

input("\nPress Enter to open browser and login...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()

    print("\nOpening database selector...")
    # First go to the main URL which should show database selector
    page.goto(ODOO_URL, timeout=30000)
    time.sleep(2)
    print(f"Current URL: {page.url}")
    page.screenshot(path="Logs/step1_selector.png")

    # Click on the odoo database link
    print("\nClicking on 'odoo' database...")
    try:
        db_link = page.locator("a[href*='db=odoo'], a:has-text('odoo')").first
        if db_link.count() > 0:
            db_link.click()
            print("Clicked database link")
        else:
            # Try direct URL
            print("Trying direct URL with db parameter...")
            page.goto(f"{ODOO_URL}/web?db={DB_NAME}", timeout=30000)
    except:
        page.goto(f"{ODOO_URL}/web?db={DB_NAME}", timeout=30000)

    time.sleep(3)
    print(f"Current URL after clicking: {page.url}")
    page.screenshot(path="Logs/step2_after_db_click.png")

    # Check if we're on login page now
    if "login" in page.url.lower():
        print("\nOn login page - entering credentials...")
        page.fill("input[name='login'], input#login", ADMIN)
        page.fill("input[name='password'], input#password", PASSWORD)
        page.screenshot(path="Logs/step3_filled.png")

        print("Logging in...")
        page.click("button[type='submit']")

        print("Waiting for dashboard...")
        time.sleep(5)

        print(f"\nCurrent URL: {page.url}")
        page.screenshot(path="Logs/step4_dashboard.png")

        if "login" not in page.url.lower() and "database" not in page.url.lower():
            print("\n" + "="*60)
            print("SUCCESS! Logged in to Odoo!")
            print("="*60)
            print("\nNow create the API key:")
            print("1. Click your username (top right)")
            print("2. Click 'Preferences'")
            print("3. Find 'Account Security' or 'API Keys'")
            print("4. Click 'New API Key'")
            print("5. Name it: AI Employee Integration")
            print("6. Save and copy the key")
            print("\nThen save to Logs/odoo_api_key.txt")
            print("="*60)

            print("\nBrowser staying open for you to create API key...")
            print("Press Enter when done...")
            input()

    else:
        print(f"\nStill on selector page. URL: {page.url}")
        print("Database might not be accessible. Check screenshot.")

    browser.close()

print("\nDone!")
