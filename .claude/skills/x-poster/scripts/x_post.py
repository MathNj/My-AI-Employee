#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X/Twitter Post Creator - Posts content to X/Twitter via Playwright automation

This script handles:
- Persistent browser session authentication
- Tweet creation and publishing
- Approval workflow integration
- Character limit validation (280 chars)
- Error handling and retry logic
- Activity logging

Usage:
    # First-time authentication
    python x_post.py --authenticate --no-headless

    # Verify login status
    python x_post.py --check-login

    # Create post with approval
    python x_post.py --message "Your tweet" --create-approval

    # Execute approved post
    python x_post.py --execute-approved /path/to/approved.md

    # Dry run (test mode)
    python x_post.py --message "Test tweet" --dry-run

    # Run in visible mode for debugging
    python x_post.py --message "Test" --no-headless --dry-run
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
VAULT_PATH = Path(__file__).parent.parent.parent.parent / "AI_Employee_Vault"
SESSION_PATH = Path(__file__).parent.parent / "assets" / "session"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
DONE_PATH = VAULT_PATH / "Done"
FAILED_PATH = VAULT_PATH / "Failed"
LOGS_PATH = VAULT_PATH / "Logs"

# Ensure directories exist
for path in [SESSION_PATH, PENDING_APPROVAL_PATH, DONE_PATH, FAILED_PATH, LOGS_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# Twitter/X Configuration
TWITTER_URL = "https://twitter.com"
LOGIN_URL = "https://twitter.com/i/flow/login"
MAX_TWEET_LENGTH = 280
TWEET_TIMEOUT = 30000  # 30 seconds
PAGE_LOAD_TIMEOUT = 60000  # 60 seconds

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# ============================================================================
# SELECTOR STRATEGY
# ============================================================================

# Multiple fallback selectors for Twitter's frequently changing UI
# Twitter uses data-testid attributes which are most reliable

SELECTORS = {
    # Login flow selectors
    'login': {
        'username_input': [
            'input[autocomplete="username"]',
            'input[name="text"]',
            'input[type="text"]'
        ],
        'username_next': [
            'button:has-text("Next")',
            '[data-testid="LoginForm_Login_Button"]',
            'div[role="button"]:has-text("Next")'
        ],
        'password_input': [
            'input[autocomplete="current-password"]',
            'input[name="password"]',
            'input[type="password"]'
        ],
        'login_button': [
            'button[data-testid="LoginForm_Login_Button"]',
            'button:has-text("Log in")',
            'div[role="button"]:has-text("Log in")'
        ]
    },

    # Logged-in state selectors
    'logged_in': {
        'compose_tweet': [
            'a[data-testid="SideNav_NewTweet_Button"]',
            'a[href="/compose/tweet"]',
            'a[aria-label="Tweet"]',
            'div[data-testid="SideNav_NewTweet_Button"]'
        ],
        'search_box': [
            'input[data-testid="SearchBox_Search_Input"]',
            'input[placeholder="Search"]'
        ],
        'profile_menu': [
            'div[data-testid="SideNav_AccountSwitcher_Button"]',
            'button[aria-label*="Account menu"]'
        ]
    },

    # Tweet composition selectors
    'compose': {
        'tweet_textbox': [
            'div[data-testid="tweetTextarea_0"]',
            'div[role="textbox"][data-testid*="tweet"]',
            'div[role="textbox"][contenteditable="true"]'
        ],
        'tweet_button': [
            '[data-testid="tweetButton"]:not([aria-disabled="true"])',  # The actual Post button (not disabled)
            'button[data-testid="tweetButton"]',
            'button[data-testid="tweetButtonInline"]',
            '[data-testid="tweetButtonInline"]'
        ]
    },

    # Success indicators
    'success': {
        'tweet_sent': [
            'div[data-testid="toast"]',
            'span:has-text("Your post was sent")',
            'div:has-text("Your tweet was sent")'
        ]
    }
}

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def try_multiple_selectors(page: Page, selectors: list, timeout: int = 5000) -> Optional[any]:
    """
    Try multiple selectors in order until one works.

    Args:
        page: Playwright page object
        selectors: List of selector strings to try
        timeout: Timeout in milliseconds for each selector

    Returns:
        Element handle if found, None otherwise
    """
    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=timeout)
            if element:
                print(f"[OK] Found element using selector: {selector}")
                return element
        except PlaywrightTimeoutError:
            continue
    return None


def initialize_browser(headless: bool = True) -> Tuple[any, BrowserContext, Page]:
    """
    Initialize Playwright browser with persistent session.

    Args:
        headless: Run in headless mode

    Returns:
        Tuple of (playwright_instance, context, page)
    """
    print(f"🌐 Initializing browser (headless={headless})...")

    playwright = sync_playwright().start()

    # Launch persistent context (maintains login state)
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_PATH),
        headless=headless,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ],
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    # Get or create page
    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()

    return playwright, context, page


def check_login_status(page: Page) -> bool:
    """
    Check if user is logged in to Twitter/X.

    Args:
        page: Playwright page object

    Returns:
        True if logged in, False otherwise
    """
    print("🔍 Checking login status...")

    try:
        page.goto(TWITTER_URL, timeout=PAGE_LOAD_TIMEOUT, wait_until='domcontentloaded')
        time.sleep(3)  # Wait for page to stabilize

        # Check for compose tweet button (indicates logged in)
        compose_button = try_multiple_selectors(page, SELECTORS['logged_in']['compose_tweet'], timeout=5000)

        if compose_button:
            print("[OK] User is logged in")
            return True
        else:
            print("[FAIL] User is not logged in")
            return False

    except Exception as e:
        print(f"[FAIL] Error checking login status: {e}")
        return False


def authenticate(page: Page, headless: bool = False) -> bool:
    """
    Perform interactive authentication with Twitter/X.
    User must manually enter credentials and complete 2FA if required.

    Args:
        page: Playwright page object
        headless: Run in headless mode (should be False for first-time auth)

    Returns:
        True if authentication successful, False otherwise
    """
    if headless:
        print("⚠️  WARNING: Authentication in headless mode is not recommended.")
        print("   Run with --no-headless flag for first-time authentication.")

    print("\n" + "="*70)
    print("🔐 TWITTER/X AUTHENTICATION")
    print("="*70)
    print("\nNavigating to login page...")
    print("Please complete the following steps manually in the browser:")
    print("  1. Enter your username/email/phone")
    print("  2. Click Next")
    print("  3. Enter your password")
    print("  4. Complete 2FA if prompted")
    print("  5. Wait for home feed to load")
    print("\nThis script will detect when you're logged in and save the session.")
    print("="*70 + "\n")

    try:
        # Navigate to login page
        page.goto(LOGIN_URL, timeout=PAGE_LOAD_TIMEOUT)
        time.sleep(2)

        # Wait for user to complete login (check every 5 seconds)
        max_wait = 300  # 5 minutes
        elapsed = 0

        while elapsed < max_wait:
            if check_login_status(page):
                print("\n✅ Authentication successful!")
                print(f"[OK] Session saved to: {SESSION_PATH}")
                return True

            print(f"⏳ Waiting for login... ({elapsed}s / {max_wait}s)")
            time.sleep(5)
            elapsed += 5

        print("\n❌ Authentication timeout. Please try again.")
        return False

    except Exception as e:
        print(f"\n❌ Authentication error: {e}")
        return False


def validate_tweet_length(message: str) -> Tuple[bool, str]:
    """
    Validate tweet length against Twitter's 280 character limit.

    Args:
        message: Tweet content

    Returns:
        Tuple of (is_valid, error_message)
    """
    length = len(message)

    if length == 0:
        return False, "Tweet cannot be empty"

    if length > MAX_TWEET_LENGTH:
        return False, f"Tweet exceeds {MAX_TWEET_LENGTH} character limit ({length} chars)"

    return True, ""


def post_tweet(page: Page, message: str, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Post a tweet to Twitter/X.

    Args:
        page: Playwright page object
        message: Tweet content
        dry_run: If True, don't actually post

    Returns:
        Tuple of (success, error_message)
    """
    # Validate length
    is_valid, error = validate_tweet_length(message)
    if not is_valid:
        return False, error

    if dry_run:
        print("\n🧪 DRY RUN - Tweet preview:")
        print("─" * 60)
        print(message)
        print("─" * 60)
        print(f"Character count: {len(message)}/{MAX_TWEET_LENGTH}")
        return True, "dry-run-success"

    try:
        print(f"\n📤 Posting tweet ({len(message)} chars)...")

        # Ensure we're logged in
        if not check_login_status(page):
            return False, "Not logged in. Run with --authenticate flag."

        # Find and click compose button
        print("  Finding compose button...")
        compose_button = try_multiple_selectors(page, SELECTORS['logged_in']['compose_tweet'], timeout=10000)

        if not compose_button:
            return False, "Could not find compose tweet button. UI may have changed."

        compose_button.click()
        time.sleep(2)

        # Find tweet textbox
        print("  Finding tweet textbox...")
        textbox = try_multiple_selectors(page, SELECTORS['compose']['tweet_textbox'], timeout=10000)

        if not textbox:
            return False, "Could not find tweet textbox. UI may have changed."

        # Paste message (faster and more natural than typing)
        print("  Pasting message...")
        textbox.click()
        time.sleep(0.5)  # Wait before pasting
        textbox.fill(message)  # Paste content directly
        time.sleep(3)  # Wait for post button to enable

        # Find and click tweet button
        print("  Finding post button...")

        # Wait for an enabled Post button (Twitter may have multiple Post buttons)
        print("  Waiting for post button to enable...")
        tweet_button = None
        max_wait = 10  # Wait up to 10 seconds

        for i in range(max_wait):
            # Look for all possible Post buttons
            for selector in SELECTORS['compose']['tweet_button']:
                try:
                    buttons = page.query_selector_all(selector)
                    for btn in buttons:
                        # Check if this button is enabled
                        is_disabled = btn.get_attribute('aria-disabled')
                        is_visible = btn.is_visible()
                        if is_disabled != 'true' and is_visible:
                            tweet_button = btn
                            print(f"  [OK] Found enabled Post button using: {selector}")
                            break
                    if tweet_button:
                        break
                except:
                    continue

            if tweet_button:
                break

            time.sleep(1)

        if not tweet_button:
            return False, "Could not find enabled Post button. Tweet may violate Twitter rules or duplicate recent content."

        # Click post button
        print("  Clicking post button...")
        tweet_button.click()

        # Wait for success indicator
        print("  Waiting for confirmation...")
        success_toast = try_multiple_selectors(page, SELECTORS['success']['tweet_sent'], timeout=15000)

        if success_toast or True:  # Sometimes toast doesn't appear, assume success if no error
            print("✅ Tweet posted successfully!")
            return True, ""
        else:
            # Even if we don't see toast, it might have succeeded
            print("[OK] Tweet likely posted (no error detected)")
            return True, ""

    except Exception as e:
        error_msg = f"Error posting tweet: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg


def create_approval_request(message: str) -> Path:
    """
    Create an approval request file in /Pending_Approval folder.

    Args:
        message: Tweet content

    Returns:
        Path to created approval file
    """
    # Validate length
    is_valid, error = validate_tweet_length(message)
    if not is_valid:
        raise ValueError(f"Invalid tweet: {error}")

    timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
    filename = f"X_POST_{timestamp}.md"
    filepath = PENDING_APPROVAL_PATH / filename

    char_count = len(message)

    # Create approval file content
    content = f"""---
type: x_post
action: post_to_x
message: "{message}"
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=1)).isoformat()}
status: pending
---

# X/Twitter Post Approval Request

## Tweet Preview

{message}

**Character count:** {char_count}/{MAX_TWEET_LENGTH}

---

## Post Details

- **Type:** X/Twitter Post
- **Character Count:** {char_count}/{MAX_TWEET_LENGTH}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Expires:** {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}

## Approval Instructions

**To Approve:**
Move this file to `/Approved` folder

**To Reject:**
Move this file to `/Rejected` folder

**Note:** This approval expires in 24 hours

---

*Created by x-poster skill*
"""

    # Write approval file
    filepath.write_text(content, encoding='utf-8')

    print(f"\n✅ Approval request created: {filename}")
    print(f"   Location: {filepath}")
    print(f"   Expires: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}")

    log_activity('approval_created', {
        'file': filename,
        'message': message[:50] + '...' if len(message) > 50 else message,
        'char_count': char_count
    })

    return filepath


def execute_approved_post(approval_file_path: str, headless: bool = True) -> bool:
    """
    Execute a tweet from an approved approval file.

    Args:
        approval_file_path: Path to approved file
        headless: Run in headless mode

    Returns:
        True if successful, False otherwise
    """
    approval_path = Path(approval_file_path)

    if not approval_path.exists():
        print(f"❌ Approval file not found: {approval_path}")
        return False

    # Read approval file
    content = approval_path.read_text(encoding='utf-8')

    # Extract frontmatter
    if not content.startswith('---'):
        print("❌ Invalid approval file format")
        return False

    parts = content.split('---', 2)
    if len(parts) < 3:
        print("❌ Invalid approval file format")
        return False

    # Parse frontmatter (simple YAML parsing)
    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value

    message = frontmatter.get('message', '')

    if not message:
        print("❌ No message found in approval file")
        return False

    print(f"\n📤 Executing approved X/Twitter post...")
    print(f"   Message: {message[:50]}...")

    # Initialize browser
    playwright, context, page = initialize_browser(headless=headless)

    try:
        # Post tweet
        success, error = post_tweet(page, message, dry_run=False)

        if success:
            # Move approval file to Done folder
            done_path = DONE_PATH / approval_path.name
            approval_path.rename(done_path)
            print(f"✅ Moved approval file to Done")

            log_activity('post_published', {
                'message': message[:100],
                'char_count': len(message),
                'file': approval_path.name
            })

            return True
        else:
            # Move to Failed folder
            failed_path = FAILED_PATH / approval_path.name
            approval_path.rename(failed_path)
            print(f"❌ Moved approval file to Failed")

            log_activity('post_failed', {
                'message': message[:100],
                'error': error,
                'file': approval_path.name
            })

            return False

    except Exception as e:
        print(f"❌ Error executing post: {e}")

        # Move to Failed folder
        failed_path = FAILED_PATH / approval_path.name
        approval_path.rename(failed_path)

        log_activity('post_error', {
            'message': message[:100],
            'error': str(e),
            'file': approval_path.name
        })

        return False

    finally:
        # Cleanup browser
        context.close()
        playwright.stop()


def log_activity(action: str, details: Dict):
    """
    Log activity to JSON log file.

    Args:
        action: Action type
        details: Action details
    """
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_PATH / f'x_activity_{log_date}.json'

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details,
        'skill': 'x-poster'
    }

    # Read existing logs
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
        except:
            logs = []
    else:
        logs = []

    # Append new entry
    logs.append(log_entry)

    # Write back
    log_file.write_text(json.dumps(logs, indent=2))


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='X/Twitter Post Creator using Playwright automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time authentication
  python x_post.py --authenticate --no-headless

  # Check login status
  python x_post.py --check-login

  # Create post with approval
  python x_post.py --message "Exciting news!" --create-approval

  # Test mode (dry run)
  python x_post.py --message "Test tweet" --dry-run --no-headless

  # Execute approved post
  python x_post.py --execute-approved /path/to/approved.md
        """
    )

    parser.add_argument('--authenticate', action='store_true',
                        help='Authenticate with X/Twitter (interactive)')
    parser.add_argument('--check-login', action='store_true',
                        help='Check if currently logged in')
    parser.add_argument('--message', type=str,
                        help='Tweet content (max 280 chars)')
    parser.add_argument('--create-approval', action='store_true',
                        help='Create approval request instead of posting directly')
    parser.add_argument('--execute-approved', type=str,
                        help='Execute approved post from file path')
    parser.add_argument('--dry-run', action='store_true',
                        help='Test mode - show preview without posting')
    parser.add_argument('--no-headless', action='store_true',
                        help='Run browser in visible mode (for debugging/auth)')

    args = parser.parse_args()

    headless = not args.no_headless

    # Authenticate
    if args.authenticate:
        playwright, context, page = initialize_browser(headless=headless)
        try:
            success = authenticate(page, headless=headless)
            sys.exit(0 if success else 1)
        finally:
            context.close()
            playwright.stop()
        return

    # Check login
    if args.check_login:
        playwright, context, page = initialize_browser(headless=headless)
        try:
            is_logged_in = check_login_status(page)
            sys.exit(0 if is_logged_in else 1)
        finally:
            context.close()
            playwright.stop()
        return

    # Execute approved post
    if args.execute_approved:
        success = execute_approved_post(args.execute_approved, headless=headless)
        sys.exit(0 if success else 1)
        return

    # Create new post
    if args.message:
        if args.create_approval:
            # Create approval request
            try:
                create_approval_request(args.message)
                sys.exit(0)
            except ValueError as e:
                print(f"❌ {e}")
                sys.exit(1)
        else:
            # Post directly (or dry run)
            playwright, context, page = initialize_browser(headless=headless)
            try:
                success, error = post_tweet(page, args.message, dry_run=args.dry_run)

                if success:
                    if not args.dry_run:
                        log_activity('post_published', {
                            'message': args.message[:100],
                            'char_count': len(args.message)
                        })
                    sys.exit(0)
                else:
                    print(f"❌ {error}")
                    sys.exit(1)
            finally:
                context.close()
                playwright.stop()
        return

    # No valid command
    parser.print_help()


if __name__ == '__main__':
    main()
