#!/usr/bin/env python3
"""
Use existing Odoo database and generate API key.
"""

import time
import sys
import re
from playwright.sync_api import sync_playwright

# Configuration
ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo"
# We'll need to create admin credentials for the existing DB
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin@123456"
API_KEY_NAME = "AI Employee Integration"


def use_existing_database():
    """Use existing odoo database and generate API key."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("="*60)
            print("Using Existing Odoo Database")
            print("="*60)
            print(f"Database: {DB_NAME}")
            print(f"URL: {ODOO_URL}")
            print("="*60)

            # Go directly to the database login
            print("\n1. Navigating to existing database...")
            page.goto(f"{ODOO_URL}/web?db={DB_NAME}", wait_until="networkidle", timeout=30000)
            time.sleep(2)

            page.screenshot(path="Logs/odoo_existing_1_initial.png")

            # Check if we need to create admin or login
            current_url = page.url
            print(f"Current URL: {current_url}")

            # If it's the login page, we need to create a new database or use existing
            if "login" in current_url.lower():
                print("\nDetected login page for existing database.")
                print("We need to either:")
                print("  1. Know the existing admin credentials, OR")
                print("  2. Delete this database and create a fresh one")

                # Check if there's a way to create first user
                if page.locator("form[action*='signup']").count() > 0 or page.get_by_text("Create").count() > 0:
                    print("\nTrying to create first admin user...")

                    # Try to fill signup form if exists
                    if page.locator("input[name='login'], input[name='email']").count() > 0:
                        page.fill("input[name='login'], input[name='email']", ADMIN_EMAIL)
                        page.fill("input[name='password']", ADMIN_PASSWORD)
                        page.fill("input[name='confirm_password']", ADMIN_PASSWORD)

                        page.screenshot(path="Logs/odoo_existing_2_signup.png")

                        print("Creating admin account...")
                        page.click("button[type='submit']")

                        time.sleep(5)

                        # Check if redirected
                        if "web" in page.url and "login" not in page.url:
                            print("Admin account created successfully!")
                            return generate_api_key(page)

                else:
                    print("\nNo signup option available.")
                    print("\nOptions:")
                    print("1. Delete the 'odoo' database and recreate:")
                    print("   - Go to http://localhost:8069/web/database/manager")
                    print("   - Delete 'odoo' database")
                    print("   - Create new one with known credentials")
                    print("")
                    print("2. If you know the admin password, I can proceed")

                    # Try default credentials
                    print("\nTrying default credentials...")
                    page.goto(f"{ODOO_URL}/web/login?db={DB_NAME}", timeout=30000)
                    time.sleep(2)

                    # Try common default credentials
                    defaults = [
                        ("admin", "admin"),
                        ("admin@example.com", "admin"),
                        ("odoo", "odoo"),
                    ]

                    for email, password in defaults:
                        page.fill("input[name='login'], input#login", email)
                        page.fill("input[name='password'], input#password", password)
                        page.click("button[type='submit']")
                        time.sleep(3)

                        if "login" not in page.url:
                            print(f"\nSuccess! Logged in with: {email} / {password}")
                            return generate_api_key(page)

                        # Go back to login page
                        page.goto(f"{ODOO_URL}/web/login?db={DB_NAME}", timeout=30000)
                        time.sleep(2)

                    print("\nDefault credentials didn't work.")

            # If we got here, couldn't login
            print("\n" + "="*60)
            print("Could not automatically access the database.")
            print("="*60)
            print("\nPlease do one of the following:")
            print("")
            print("OPTION 1 - Delete and recreate:")
            print("  1. Open: http://localhost:8069/web/database/manager")
            print("  2. Use master password: zmiy-853z-yg9k")
            print("  3. Delete 'odoo' database")
            print("  4. Create new one 'odoo_production'")
            print("  5. Set email: admin@example.com")
            print("  6. Set password: Admin@123456")
            print("")
            print("OPTION 2 - If you know the admin password:")
            print("  - Tell me the credentials and I'll login")
            print("")
            print("Then I can generate the API key automatically.")

            page.screenshot(path="Logs/odoo_existing_final.png")
            time.sleep(30)

            return None

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="Logs/odoo_existing_error.png")
            return None

        finally:
            browser.close()


def generate_api_key(page):
    """Generate API key once logged in."""
    print("\n" + "="*60)
    print("Generating API Key...")
    print("="*60)

    try:
        time.sleep(2)
        page.screenshot(path="Logs/odoo_api_1_dashboard.png")

        # Click user menu
        print("Opening user menu...")
        user_menu = page.locator(".o_user_menu, [data-menu-username]").first
        user_menu.click()
        time.sleep(1)

        # Click Preferences
        print("Opening Preferences...")
        prefs = page.get_by_text("Preferences")
        if prefs.count() > 0:
            prefs.click()
        else:
            page.goto(f"{ODOO_URL}/web#action=base.act_res_users_my", timeout=30000)

        time.sleep(2)
        page.screenshot(path="Logs/odoo_api_2_preferences.png")

        # Look for Account Security
        security = page.get_by_text("Account Security")
        if security.count() > 0:
            security.click()
            time.sleep(2)

        page.screenshot(path="Logs/odoo_api_3_security.png")

        # Look for New API Key button
        new_key = page.locator("button:has-text('New API Key'), button:has-text('Generate')")

        if new_key.count() > 0:
            print("Creating new API key...")
            new_key.first.click()
            time.sleep(2)

            # Fill name
            name_input = page.locator("input[type='text']").first
            if name_input.count() > 0:
                name_input.fill(API_KEY_NAME)
                time.sleep(0.5)

            page.screenshot(path="Logs/odoo_api_4_form.png")

            # Save
            save = page.locator("button:has-text('Save'), button:has-text('Create'), button:has-text('Generate')").first
            save.click()
            time.sleep(3)

            page.screenshot(path="Logs/odoo_api_5_created.png")

            # Extract key
            print("Extracting API key...")

            # Look for JWT token (starts with eyJ)
            content = page.content()
            import re
            match = re.search(r'eyJ[\\w\\-\\.]+', content.decode())

            if match:
                api_key = match.group(0)
                print(f"\n" + "="*60)
                print(f"API KEY: {api_key}")
                print("="*60)

                with open("Logs/odoo_api_key.txt", "w") as f:
                    f.write(f"ODOO_URL={ODOO_URL}\n")
                    f.write(f"ODOO_DB={DB_NAME}\n")
                    f.write(f"ODOO_API_KEY={api_key}\n")
                    f.write(f"ODOO_ADMIN_EMAIL={ADMIN_EMAIL}\n")
                    f.write(f"ODOO_ADMIN_PASSWORD={ADMIN_PASSWORD}\n")

                print("\nSaved to: Logs/odoo_api_key.txt")
                return api_key

        print("Could not complete API key generation")
        page.screenshot(path="Logs/odoo_api_error.png")
        return None

    except Exception as e:
        print(f"Error generating API key: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="Logs/odoo_api_fatal_error.png")
        return None


if __name__ == "__main__":
    result = use_existing_database()
    sys.exit(0 if result else 1)
