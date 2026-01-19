#!/usr/bin/env python3
"""
Automated Odoo 19 setup and API key generation using Playwright.
This script:
1. Opens Odoo web interface
2. Creates admin account
3. Initializes database
4. Generates API key
"""

import time
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configuration
ODOO_URL = "http://localhost:8069"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin@123456"
DB_NAME = "odoo_production"
API_KEY_NAME = "AI Employee Integration"


def setup_odoo():
    """Main function to setup Odoo and generate API key."""

    with sync_playwright() as p:
        # Launch browser in headful mode so we can see what's happening
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        try:
            print(f"Navigating to Odoo at {ODOO_URL}...")
            page.goto(ODOO_URL, wait_until="networkidle", timeout=60000)

            # Take screenshot to see current state
            page.screenshot(path="Logs/odoo_setup_1_initial.png")

            # Check if we need to create database or if it's the login page
            current_url = page.url
            print(f"Current URL: {current_url}")

            # Look for database management page
            if "database/manager" in page.url or page.locator("select[name='db_name']").count() > 0:
                print("Detected database selection/creation page")
                return create_database(page)

            # Look for login form
            elif page.locator("input[name='login']").count() > 0:
                print("Detected login page - database may already exist")
                page.screenshot(path="Logs/odoo_setup_login.png")
                # Try to access database manager directly
                print("Trying to access database manager...")
                page.goto(f"{ODOO_URL}/web/database/manager", timeout=30000)
                time.sleep(2)

                # Check if we're now on database manager page
                if page.locator("button:has-text('Create')").count() > 0 or page.locator(".o_database_action").count() > 0:
                    print("Successfully accessed database manager")
                    # Create new database
                    return create_database_from_manager(page)
                else:
                    print("Could not access database manager - checking if login required")
                    return None

            # Look for database creation form
            elif page.locator("input#db_name").count() > 0 or page.locator("input[name='db_create']").count() > 0:
                print("Detected database creation page")
                return create_database(page)

            # Check if already logged in
            elif page.locator(".o_user_menu, [data-menu-username]").count() > 0:
                print("Already logged in! Generating API key...")
                return generate_api_key(page)

            else:
                print(f"Unknown page state. URL: {page.url}")
                page.screenshot(path="Logs/odoo_setup_unknown.png")
                print("Please check the screenshot and complete setup manually")
                return None

        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}")
            page.screenshot(path="Logs/odoo_setup_timeout.png")
            return None
        except Exception as e:
            print(f"Error during setup: {e}")
            page.screenshot(path="Logs/odoo_setup_error.png")
            return None
        finally:
            # Keep browser open briefly to see what happened, then close
            time.sleep(2)
            browser.close()


def create_database_from_manager(page):
    """Create database from the database manager page."""
    print("\n=== Creating Database from Manager ===")

    try:
        page.screenshot(path="Logs/odoo_db_manager.png")

        # Click "Create" button
        create_button = page.get_by_role("button", name="Create")
        if create_button.count() > 0:
            print("Clicking Create database button...")
            create_button.click()
            time.sleep(2)
        else:
            # Look for link with "Create"
            page.locator("a:has-text('Create')").first.click()
            time.sleep(2)

        page.screenshot(path="Logs/odoo_db_create_form.png")

        # Fill the create database form
        print(f"Setting database name: {DB_NAME}")
        page.fill("input#name, input[name='name'], input[placeholder*='database']", DB_NAME)

        print(f"Setting admin email: {ADMIN_EMAIL}")
        page.fill("input[name='email'], input[placeholder*='email']", ADMIN_EMAIL)

        print("Setting admin password")
        page.fill("input[name='password'], input[placeholder*='password']", ADMIN_PASSWORD)

        # Set language
        if page.locator("select[name='lang']").count() > 0:
            page.select_option("select[name='lang']", "en_US")

        # Set country
        if page.locator("select[name='country']").count() > 0:
            page.select_option("select[name='country']", "US")

        page.screenshot(path="Logs/odoo_db_before_create.png")

        # Submit
        print("Creating database...")
        page.click("button[type='submit'], button:has-text('Create database')")

        # Wait for creation to complete - this takes a while
        print("Waiting for database creation (may take 2-3 minutes)...")
        page.wait_for_url("**/web/login", timeout=180000)
        time.sleep(3)

        page.screenshot(path="Logs/odoo_db_created.png")
        print("Database created successfully!")

        # Now log in and generate API key
        return login_and_generate_key(page)

    except Exception as e:
        print(f"Error creating database from manager: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="Logs/odoo_db_manager_error.png")
        return None


def login_and_generate_key(page):
    """Login to Odoo and generate API key."""
    print("\n=== Logging in and Generating API Key ===")

    try:
        # Navigate to login
        page.goto(f"{ODOO_URL}/web/login", timeout=30000)
        time.sleep(1)

        # Fill login form
        page.fill("input[name='login'], input#login", ADMIN_EMAIL)
        page.fill("input[name='password'], input#password", ADMIN_PASSWORD)

        page.screenshot(path="Logs/odoo_login_filled.png")

        # Submit
        print("Logging in...")
        page.click("button[type='submit'], button:has-text('Log in')")

        # Wait for dashboard
        page.wait_for_url("**/web", timeout=60000)
        time.sleep(3)

        page.screenshot(path="Logs/odoo_logged_in.png")
        print("Login successful!")

        # Generate API key
        return generate_api_key(page)

    except Exception as e:
        print(f"Error logging in: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="Logs/odoo_login_error.png")
        return None


def create_database(page):
    """Handle database creation."""
    print("\n=== Creating Database ===")

    try:
        # Look for master password field (first-time setup)
        if page.locator("input#master_password").count() > 0:
            print("Setting master password...")
            page.fill("input#master_password", "Admin@123")
            page.click("button:has-text('Continue')")
            time.sleep(2)

        # Fill database creation form
        if page.locator("input#db_name, input[name='db_name'], input#name").count() > 0:
            print(f"Creating database: {DB_NAME}")
            db_input = page.locator("input#db_name, input[name='db_name'], input#name").first
            db_input.fill(DB_NAME)
            page.screenshot(path="Logs/odoo_setup_db_name.png")

        # Fill email
        if page.locator("input[name='email'], input#email").count() > 0:
            print(f"Setting admin email: {ADMIN_EMAIL}")
            page.fill("input[name='email'], input#email", ADMIN_EMAIL)

        # Fill password
        if page.locator("input[name='password'], input#password").count() > 0:
            print("Setting admin password")
            page.fill("input[name='password'], input#password", ADMIN_PASSWORD)
            page.fill("input[name='confirm_password']", ADMIN_PASSWORD)

        # Select language
        if page.locator("select[name='lang']").count() > 0:
            page.select_option("select[name='lang']", "en_US")

        # Select country
        if page.locator("select[name='country']").count() > 0:
            page.select_option("select[name='country']", "US")

        page.screenshot(path="Logs/odoo_setup_before_submit.png")

        # Submit the form
        print("Submitting database creation...")
        page.click("button[type='submit'], button:has-text('Create'), button:has-text('Continue')")

        # Wait for database creation to complete
        print("Waiting for database initialization (this may take a minute)...")
        page.wait_for_url("**/web", timeout=120000)
        time.sleep(5)

        page.screenshot(path="Logs/odoo_setup_db_created.png")
        print("Database created successfully!")

        # Now generate API key
        return generate_api_key(page)

    except Exception as e:
        print(f"Error creating database: {e}")
        page.screenshot(path="Logs/odoo_setup_db_error.png")
        return None


def create_admin_account(page):
    """Create admin account if needed."""
    print("\n=== Creating Admin Account ===")

    try:
        # Fill signup form
        page.fill("input[name='login'], input[name='email']", ADMIN_EMAIL)
        page.fill("input[name='password']", ADMIN_PASSWORD)
        page.fill("input[name='confirm_password']", ADMIN_PASSWORD)

        page.screenshot(path="Logs/odoo_setup_admin_before.png")

        # Submit
        page.click("button[type='submit']")

        print("Waiting for account creation...")
        time.sleep(5)

        page.screenshot(path="Logs/odoo_setup_admin_after.png")

        # Generate API key
        return generate_api_key(page)

    except Exception as e:
        print(f"Error creating admin account: {e}")
        return None


def generate_api_key(page):
    """Generate API key through the Odoo interface."""
    print("\n=== Generating API Key ===")

    try:
        # Make sure we're logged in and on a page
        page.wait_for_load_state("networkidle", timeout=30000)

        # Click on user menu (top right)
        print("Opening user menu...")
        user_menu = page.locator(".o_user_menu, [data-menu-username], .oe_topbar_name").first
        user_menu.click()
        time.sleep(1)

        page.screenshot(path="Logs/odoo_api_user_menu.png")

        # Look for Preferences/Account Security
        # In Odoo 19, API keys are in: Preferences -> Account Security
        preferences_link = page.get_by_text("Preferences").or_(
            page.get_by_text("My Account")
        ).or_(
            page.get_by_text("Account Security")
        )

        if preferences_link.count() > 0:
            preferences_link.first.click()
            print("Opened Preferences/Account page")
            time.sleep(2)
        else:
            # Try direct navigation
            print("Trying direct navigation to preferences...")
            page.goto(f"{ODOO_URL}/web#action=base.res_users_act_my", timeout=30000)
            time.sleep(2)

        page.screenshot(path="Logs/odoo_api_preferences.png")

        # Look for Account Security tab or API Keys section
        account_security = page.get_by_text("Account Security").or_(
            page.get_by_text("API Keys")
        )

        if account_security.count() > 0:
            account_security.first.click()
            time.sleep(1)

        page.screenshot(path="Logs/odoo_api_account_security.png")

        # Click "New API Key" or "Generate" button
        new_key_button = page.get_by_role("button", name="New API Key").or_(
            page.get_by_role("button", name="Generate")
        ).or_(
            page.get_by_text("New")
        )

        if new_key_button.count() > 0:
            print("Clicking 'New API Key' button...")
            new_key_button.first.click()
            time.sleep(2)

            page.screenshot(path="Logs/odoo_api_new_key.png")

            # Fill in key details
            # Look for name/description field
            name_input = page.locator("input[name='name'], input[placeholder*='name'], input#name").first
            if name_input.count() > 0:
                name_input.fill(API_KEY_NAME)

            # Submit/Save
            save_button = page.get_by_role("button", name="Save").or_(
                page.get_by_role("button", name="Create")
            ).or_(
                page.get_by_role("button", name="Generate")
            )

            if save_button.count() > 0:
                print("Generating API key...")
                save_button.first.click()
                time.sleep(3)

                page.screenshot(path="Logs/odoo_api_key_created.png")

                # Look for the generated key
                # The key is usually displayed in a modal or on the page
                api_key_text = page.locator("code, .api-key, [data-api-key], input[readonly]").first

                if api_key_text.count() > 0:
                    api_key = api_key_text.input_value() or api_key_text.text_content()
                    print(f"\n{'='*60}")
                    print(f"API KEY GENERATED: {api_key}")
                    print(f"{'='*60}\n")

                    # Save to file
                    with open("Logs/odoo_api_key.txt", "w") as f:
                        f.write(f"ODOO_URL={ODOO_URL}\n")
                        f.write(f"ODOO_DB={DB_NAME}\n")
                        f.write(f"ODOO_API_KEY={api_key}\n")
                        f.write(f"ODOO_ADMIN_EMAIL={ADMIN_EMAIL}\n")
                        f.write(f"ODOO_ADMIN_PASSWORD={ADMIN_PASSWORD}\n")

                    print("API key saved to: Logs/odoo_api_key.txt")
                    return api_key
                else:
                    print("Could not find API key in response")
                    return None
        else:
            print("Could not find 'New API Key' button")
            print("Available buttons:")
            buttons = page.locator("button").all()
            for btn in buttons[:10]:
                print(f"  - {btn.text_content()}")
            return None

    except Exception as e:
        print(f"Error generating API key: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="Logs/odoo_api_error.png")
        return None


if __name__ == "__main__":
    print("="*60)
    print("Odoo 19 Automated Setup")
    print("="*60)
    print(f"Target: {ODOO_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print(f"Database: {DB_NAME}")
    print("="*60)

    result = setup_odoo()

    if result:
        print(f"\nSetup completed successfully!")
        print(f"API Key: {result}")
    else:
        print("\nSetup could not be completed automatically.")
        print("Please complete the setup manually in the browser.")
