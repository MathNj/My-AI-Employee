#!/usr/bin/env python3
"""
Generate API key for existing Odoo database.
"""

import time
import re
from playwright.sync_api import sync_playwright

ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "admin"
API_KEY_NAME = "AI Employee Integration"


def generate_api_key():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("Logging in to Odoo...")
        page.goto(f"{ODOO_URL}/web/login?db={DB_NAME}")
        time.sleep(2)

        page.fill("input[name='login'], input#login", ADMIN_EMAIL)
        page.fill("input[name='password'], input#password", ADMIN_PASSWORD)
        page.click("button[type='submit']")

        print("Waiting for dashboard...")
        time.sleep(5)

        print(f"Current URL: {page.url}")
        page.screenshot(path="Logs/step1_dashboard.png")

        # Get user menu
        print("Clicking user menu...")
        page.locator(".o_user_menu, [data-menu-username]").first.click()
        time.sleep(2)
        page.screenshot(path="Logs/step2_user_menu.png")

        # Click Preferences
        print("Clicking Preferences...")
        page.locator("a,button").filter(has_text="Preferences").first.click()
        time.sleep(3)
        page.screenshot(path="Logs/step3_preferences.png")

        # Try to find Account Security or API Keys
        print("Looking for Account Security/API Keys...")

        # Try clicking on Account Security
        account_sec = page.locator("*:has-text('Account Security')").first
        if account_sec.count() > 0:
            print("Found Account Security - clicking...")
            account_sec.click()
            time.sleep(2)
        else:
            print("No Account Security found")

        page.screenshot(path="Logs/step4_security.png")

        # Look for New API Key button
        new_key = page.locator("button:has-text('New API Key'), button:has-text('New'), button:has-text('Generate')")

        if new_key.count() > 0:
            print(f"Found {new_key.count()} 'New API Key' buttons")
            new_key.first.click()
            time.sleep(2)
            page.screenshot(path="Logs/step5_new_key.png")

            # Fill name
            inputs = page.locator("input[type='text']").all()
            if inputs:
                inputs[0].fill(API_KEY_NAME)
                print(f"Set API key name to: {API_KEY_NAME}")

            page.screenshot(path="Logs/step6_filled.png")

            # Save
            save = page.locator("button:has-text('Save'), button:has-text('Create'), button:has-text('Generate')").first
            save.click()
            time.sleep(3)
            page.screenshot(path="Logs/step7_created.png")

            # Extract key from page
            content = page.content()
            text = content.decode()

            # Look for JWT token
            match = re.search(r'eyJ[\\w\\-\\.]+', text)
            if match:
                api_key = match.group(0)
                print(f"\n{'='*60}")
                print(f"API KEY: {api_key}")
                print(f"{'='*60}\n")

                with open("Logs/odoo_api_key.txt", "w") as f:
                    f.write(f"ODOO_URL={ODOO_URL}\n")
                    f.write(f"ODOO_DB={DB_NAME}\n")
                    f.write(f"ODOO_API_KEY={api_key}\n")
                    f.write(f"ODOO_ADMIN={ADMIN_EMAIL}:{ADMIN_PASSWORD}\n")

                print("Saved to Logs/odoo_api_key.txt")
                print("\nBrowser will stay open for 30 seconds...")
                time.sleep(30)
                return api_key

        print("Could not find New API Key button")
        print("\nAvailable buttons on page:")
        buttons = page.locator("button").all()
        for i, btn in enumerate(buttons[:15]):
            try:
                text = btn.text_content()
                if text:
                    print(f"  {i}: {text}")
            except:
                pass

        print("\nBrowser will stay open for 60 seconds...")
        time.sleep(60)

        browser.close()
        return None


if __name__ == "__main__":
    generate_api_key()
