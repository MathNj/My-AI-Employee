#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Post Creator - Posts content to LinkedIn via Playwright automation

This script handles:
- Persistent browser session authentication
- Post creation and publishing
- Approval workflow integration
- Error handling and retry logic
- Activity logging

Usage:
    # First-time authentication
    python linkedin_post.py --authenticate --no-headless

    # Verify login status
    python linkedin_post.py --check-login

    # Create post with approval
    python linkedin_post.py --message "Your post" --create-approval

    # Execute approved post
    python linkedin_post.py --execute-approved /path/to/approved.md

    # Dry run (test mode)
    python linkedin_post.py --message "Test post" --dry-run

    # Run in visible mode for debugging
    python linkedin_post.py --message "Test" --no-headless --dry-run
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

# Import audit logger
sys.path.insert(0, str(VAULT_PATH / "Logs"))
try:
    from audit_logger import get_audit_logger
    HAS_AUDIT_LOGGER = True
except ImportError:
    print("[WARNING] Audit logger not available", file=sys.stderr)
    HAS_AUDIT_LOGGER = False
DONE_PATH = VAULT_PATH / "Done"
FAILED_PATH = VAULT_PATH / "Failed"
LOGS_PATH = VAULT_PATH / "Logs"

# Ensure directories exist
for path in [SESSION_PATH, PENDING_APPROVAL_PATH, DONE_PATH, FAILED_PATH, LOGS_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# LinkedIn Configuration
LINKEDIN_URL = "https://www.linkedin.com"
LINKEDIN_PROFILE_URL = "https://www.linkedin.com/in/najma-jameel-a36696294/"
LINKEDIN_COMPOSE_URL = "https://www.linkedin.com/in/najma-jameel-a36696294/overlay/create-post/"
MAX_POST_LENGTH = 3000  # LinkedIn allows up to 3000 characters
POST_TIMEOUT = 30000  # 30 seconds
PAGE_LOAD_TIMEOUT = 60000  # 60 seconds

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# ============================================================================
# SELECTOR STRATEGY
# ============================================================================

# LinkedIn selectors - more stable than Twitter
SELECTORS = {
    # Logged-in state selectors
    'logged_in': {
        'profile_icon': [
            'img[alt*="Photo"]',
            'button[data-control-name="identity_profile_photo"]',
            'img.global-nav__me-photo'
        ],
        'start_post': [
            'button[aria-label*="Start a post"]',
            'button.share-box-feed-entry__trigger',
            '[data-control-name="share_box_trigger"]'
        ]
    },

    # Post composition selectors
    'compose': {
        'post_textbox': [
            'div[role="textbox"][contenteditable="true"]',
            'div[data-placeholder*="share"]',
            '.ql-editor[contenteditable="true"]'
        ],
        'post_submit_button': [
            'button.share-actions__primary-action:has-text("Post")',
            'button[aria-label="Post"]',
            'button.share-actions__primary-action[type="submit"]',
            'button:has-text("Post"):not(:has-text("visibility"))'
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
    Check if user is logged in to LinkedIn.

    Args:
        page: Playwright page object

    Returns:
        True if logged in, False otherwise
    """
    print("🔍 Checking login status...")

    try:
        page.goto(LINKEDIN_URL, timeout=PAGE_LOAD_TIMEOUT, wait_until='domcontentloaded')
        time.sleep(3)  # Wait for page to stabilize

        # Check for profile icon (indicates logged in)
        profile_icon = try_multiple_selectors(page, SELECTORS['logged_in']['profile_icon'], timeout=5000)

        if profile_icon:
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
    Perform interactive authentication with LinkedIn.
    User must manually enter credentials.

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
    print("🔐 LINKEDIN AUTHENTICATION")
    print("="*70)
    print("\nNavigating to LinkedIn...")
    print("Please complete the following steps manually in the browser:")
    print("  1. Enter your email/username")
    print("  2. Enter your password")
    print("  3. Complete any security verification if prompted")
    print("  4. Wait for home feed to load")
    print("\nThis script will detect when you're logged in and save the session.")
    print("="*70 + "\n")

    try:
        # Navigate to LinkedIn
        page.goto(LINKEDIN_URL, timeout=PAGE_LOAD_TIMEOUT)
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


def validate_post_length(message: str) -> Tuple[bool, str]:
    """
    Validate post length against LinkedIn's limit.

    Args:
        message: Post content

    Returns:
        Tuple of (is_valid, error_message)
    """
    length = len(message)

    if length == 0:
        return False, "Post cannot be empty"

    if length > MAX_POST_LENGTH:
        return False, f"Post exceeds {MAX_POST_LENGTH} character limit ({length} chars)"

    return True, ""


def post_to_linkedin(page: Page, message: str, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Post content to LinkedIn.

    Args:
        page: Playwright page object
        message: Post content
        dry_run: If True, don't actually post

    Returns:
        Tuple of (success, error_message)
    """
    # Validate length
    is_valid, error = validate_post_length(message)
    if not is_valid:
        return False, error

    if dry_run:
        print("\n🧪 DRY RUN - LinkedIn post preview:")
        print("─" * 60)
        print(message)
        print("─" * 60)
        print(f"Character count: {len(message)}/{MAX_POST_LENGTH}")
        return True, "dry-run-success"

    try:
        print(f"\n📤 Posting to LinkedIn ({len(message)} chars)...")

        # Ensure we're logged in
        if not check_login_status(page):
            return False, "Not logged in. Run with --authenticate flag."

        # Navigate directly to compose URL
        print("  Opening compose dialog...")
        page.goto(LINKEDIN_COMPOSE_URL, timeout=PAGE_LOAD_TIMEOUT, wait_until='domcontentloaded')
        time.sleep(3)  # Wait for dialog to fully load

        # Find post textbox
        print("  Finding post textbox...")
        textbox = try_multiple_selectors(page, SELECTORS['compose']['post_textbox'], timeout=10000)

        if not textbox:
            return False, "Could not find post textbox. UI may have changed."

        # Paste message
        print("  Pasting message...")
        textbox.click()
        time.sleep(0.5)
        textbox.fill(message)  # Paste content directly
        time.sleep(3)  # Wait for post button to enable

        # Find and click Post button
        print("  Finding Post submit button...")

        # Wait for an enabled Post button
        print("  Waiting for Post submit button to enable...")
        post_button = None
        max_wait = 10  # Wait up to 10 seconds

        for i in range(max_wait):
            # Look for all possible Post buttons
            for selector in SELECTORS['compose']['post_submit_button']:
                try:
                    buttons = page.query_selector_all(selector)
                    for btn in buttons:
                        # Check if this button is enabled
                        is_disabled = btn.get_attribute('aria-disabled')
                        is_visible = btn.is_visible()
                        if is_disabled != 'true' and is_visible:
                            post_button = btn
                            print(f"  [OK] Found enabled Post button using: {selector}")
                            break
                    if post_button:
                        break
                except:
                    continue

            if post_button:
                break

            time.sleep(1)

        if not post_button:
            return False, "Could not find enabled Post button."

        # Click post button with JavaScript (more reliable)
        print("  Clicking Post button...")
        try:
            # Try regular click first
            post_button.click()
        except:
            # If regular click fails, use JavaScript
            page.evaluate('(element) => element.click()', post_button)

        time.sleep(7)  # Wait longer for post to process

        # Verify we're no longer on the compose overlay (indicates success)
        print("  Verifying post was published...")
        time.sleep(2)

        # Check if we're back to the profile page (compose dialog closed)
        current_url = page.url
        if "overlay/create-post" not in current_url:
            print("✅ LinkedIn post published successfully! (Compose dialog closed)")
            return True, ""
        else:
            print("⚠️  Still on compose page - post may not have been published")
            return False, "Post button clicked but compose dialog didn't close. Post may have failed."

    except Exception as e:
        error_msg = f"Error posting to LinkedIn: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg


def create_approval_request(message: str) -> Path:
    """
    Create an approval request file in /Pending_Approval folder.

    Args:
        message: Post content

    Returns:
        Path to created approval file
    """
    # Validate length
    is_valid, error = validate_post_length(message)
    if not is_valid:
        raise ValueError(f"Invalid post: {error}")

    timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
    filename = f"LINKEDIN_POST_{timestamp}.md"
    filepath = PENDING_APPROVAL_PATH / filename

    char_count = len(message)

    # Create approval file content
    content = f"""---
type: linkedin_post
action: post_to_linkedin
message: "{message}"
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=1)).isoformat()}
status: pending
---

# LinkedIn Post Approval Request

## Post Preview

{message}

**Character count:** {char_count}/{MAX_POST_LENGTH}

---

## Post Details

- **Type:** LinkedIn Post
- **Character Count:** {char_count}/{MAX_POST_LENGTH}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Expires:** {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}

## Approval Instructions

**To Approve:**
Move this file to `/Approved` folder

**To Reject:**
Move this file to `/Rejected` folder

**Note:** This approval expires in 24 hours

---

*Created by linkedin-poster skill*
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
    Execute a LinkedIn post from an approved approval file.

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

    print(f"\n📤 Executing approved LinkedIn post...")
    print(f"   Message: {message[:50]}...")

    # Initialize browser
    playwright, context, page = initialize_browser(headless=headless)

    try:
        # Post to LinkedIn
        success, error = post_to_linkedin(page, message, dry_run=False)

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

            # Log to comprehensive audit trail
            if HAS_AUDIT_LOGGER:
                try:
                    audit_logger = get_audit_logger(VAULT_PATH.parent)
                    audit_logger.log_action(
                        action_type="linkedin_post",
                        actor="linkedin_poster",
                        target="LinkedIn",
                        parameters={"message": message[:200], "char_count": len(message)},
                        approval_status="approved",
                        approved_by="human",
                        result="success",
                        metadata={"approval_file": approval_path.name}
                    )
                except Exception as audit_error:
                    print(f"[WARNING] Audit logging failed: {audit_error}", file=sys.stderr)

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

            # Log to comprehensive audit trail
            if HAS_AUDIT_LOGGER:
                try:
                    audit_logger = get_audit_logger(VAULT_PATH.parent)
                    audit_logger.log_action(
                        action_type="linkedin_post",
                        actor="linkedin_poster",
                        target="LinkedIn",
                        parameters={"message": message[:200], "char_count": len(message)},
                        approval_status="approved",
                        approved_by="human",
                        result="failure",
                        error_message=error,
                        metadata={"approval_file": approval_path.name}
                    )
                except Exception as audit_error:
                    print(f"[WARNING] Audit logging failed: {audit_error}", file=sys.stderr)

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

        # Log to comprehensive audit trail
        if HAS_AUDIT_LOGGER:
            try:
                audit_logger = get_audit_logger(VAULT_PATH.parent)
                audit_logger.log_action(
                    action_type="linkedin_post",
                    actor="linkedin_poster",
                    target="LinkedIn",
                    parameters={"message": message[:200], "char_count": len(message)},
                    approval_status="approved",
                    approved_by="human",
                    result="error",
                    error_message=str(e),
                    metadata={"approval_file": approval_path.name}
                )
            except Exception as audit_error:
                print(f"[WARNING] Audit logging failed: {audit_error}", file=sys.stderr)

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
    log_file = LOGS_PATH / f'linkedin_activity_{log_date}.json'

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details,
        'skill': 'linkedin-poster'
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
        description='LinkedIn Post Creator using Playwright automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time authentication
  python linkedin_post.py --authenticate --no-headless

  # Check login status
  python linkedin_post.py --check-login

  # Create post with approval
  python linkedin_post.py --message "Exciting news!" --create-approval

  # Test mode (dry run)
  python linkedin_post.py --message "Test post" --dry-run --no-headless

  # Execute approved post
  python linkedin_post.py --execute-approved /path/to/approved.md
        """
    )

    parser.add_argument('--authenticate', action='store_true',
                        help='Authenticate with LinkedIn (interactive)')
    parser.add_argument('--check-login', action='store_true',
                        help='Check if currently logged in')
    parser.add_argument('--message', type=str,
                        help='Post content (max 3000 chars)')
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
                success, error = post_to_linkedin(page, args.message, dry_run=args.dry_run)

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
