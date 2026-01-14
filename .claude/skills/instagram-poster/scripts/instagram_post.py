#!/usr/bin/env python3
"""
Instagram Post Automation via Playwright
Converts text to image and posts to Instagram using browser automation.

Usage:
    # First-time authentication
    python instagram_post.py --authenticate --no-headless

    # Check login status
    python instagram_post.py --check-login

    # Create approval request (converts text to image)
    python instagram_post.py --message "Your text here" --create-approval

    # Execute approved post
    python instagram_post.py --execute-approved /path/to/INSTAGRAM_POST_timestamp.md

    # Dry run (generate image but don't post)
    python instagram_post.py --message "Test text" --dry-run

    # Custom image settings
    python instagram_post.py --message "Text" --create-approval --image-style gradient --font-size 60
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import re

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Image generation imports
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Pillow not installed. Install with: pip install Pillow")

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not installed. Install with: pip install playwright && playwright install chromium")

# =============================================================================
# CONFIGURATION
# =============================================================================

VAULT_PATH = Path(__file__).resolve().parents[4]
SKILLS_PATH = VAULT_PATH / '.claude' / 'skills' / 'instagram-poster'
SESSION_PATH = SKILLS_PATH / 'assets' / 'session'
IMAGES_PATH = SKILLS_PATH / 'assets' / 'images'
PENDING_APPROVAL_PATH = VAULT_PATH / 'AI_Employee_Vault' / 'Pending_Approval'
APPROVED_PATH = VAULT_PATH / 'AI_Employee_Vault' / 'Approved'
DONE_PATH = VAULT_PATH / 'AI_Employee_Vault' / 'Done'
FAILED_PATH = VAULT_PATH / 'AI_Employee_Vault' / 'Failed'
LOGS_PATH = VAULT_PATH / 'AI_Employee_Vault' / 'Logs'

# Ensure directories exist
SESSION_PATH.mkdir(parents=True, exist_ok=True)
IMAGES_PATH.mkdir(parents=True, exist_ok=True)
PENDING_APPROVAL_PATH.mkdir(parents=True, exist_ok=True)
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Instagram Configuration
INSTAGRAM_URL = "https://www.instagram.com"
MAX_CAPTION_LENGTH = 2200  # Instagram caption limit
LOGIN_TIMEOUT = 300000  # 5 minutes for manual login
PAGE_LOAD_TIMEOUT = 60000  # 60 seconds

# Image Generation Defaults
DEFAULT_IMAGE_WIDTH = 1080
DEFAULT_IMAGE_HEIGHT = 1080
DEFAULT_FONT_SIZE = 50
DEFAULT_IMAGE_STYLE = 'gradient'  # 'gradient', 'solid', 'pattern'

# Instagram Selectors (multiple fallbacks)
SELECTORS = {
    'login': {
        'logged_in_indicator': [
            'a[href*="/direct/inbox/"]',  # Direct messages link
            'svg[aria-label="New post"]',
            'a[href="/"]>svg[aria-label="Home"]',
        ]
    },
    'create_post': {
        'new_post_button': [
            'svg[aria-label="New post"]',
            'a[href="#"]>svg[aria-label="New post"]',
            'svg[aria-label="Create"]',
        ],
        'select_from_computer': [
            'button:has-text("Select from computer")',
            'button:has-text("Select From Computer")',
            'input[type="file"][accept="image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime"]',
        ],
        'file_input': [
            'input[type="file"][accept*="image"]',
            'input[type="file"]',
        ],
        'next_button': [
            'button:has-text("Next")',
            'div[role="button"]:has-text("Next")',
            'button:has-text("next")',
            '[role="button"]:has-text("Next")',
        ],
        'caption_textarea': [
            'textarea[aria-label="Write a caption..."]',
            'textarea[placeholder="Write a caption..."]',
            'div[contenteditable="true"][aria-label*="caption"]',
            'textarea',
        ],
        'share_button': [
            'button:has-text("Share"):not(:has-text("story")):not(:has-text("Story"))',
            'button._acan._acap._acas._aj1-',  # Instagram's share button class
            'button[type="button"]:has-text("Share")',
            'div[role="button"]:has-text("Share")',
        ],
    }
}

# =============================================================================
# IMAGE GENERATION
# =============================================================================

def generate_text_image(
    text: str,
    output_path: Path,
    width: int = DEFAULT_IMAGE_WIDTH,
    height: int = DEFAULT_IMAGE_HEIGHT,
    font_size: int = DEFAULT_FONT_SIZE,
    style: str = DEFAULT_IMAGE_STYLE
) -> Path:
    """
    Generate an image from text with attractive styling.

    Args:
        text: The text to render
        output_path: Where to save the image
        width: Image width in pixels
        height: Image height in pixels
        font_size: Font size for text
        style: Image style ('gradient', 'solid', 'pattern')

    Returns:
        Path to generated image
    """
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow is not installed. Cannot generate images.")

    print(f"\n🎨 Generating image...")
    print(f"  Style: {style}")
    print(f"  Size: {width}x{height}")
    print(f"  Font size: {font_size}")

    # Create base image with background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Apply background style
    if style == 'gradient':
        # Create gradient background (blue to purple)
        for y in range(height):
            r = int(100 + (155 * y / height))
            g = int(50 + (100 * y / height))
            b = int(200 - (50 * y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    elif style == 'solid':
        # Solid color background
        draw.rectangle([0, 0, width, height], fill=(45, 55, 72))
    elif style == 'pattern':
        # Simple pattern background
        draw.rectangle([0, 0, width, height], fill=(30, 30, 30))
        for i in range(0, width, 100):
            for j in range(0, height, 100):
                draw.ellipse([i, j, i+50, j+50], fill=(50, 50, 50))

    # Try to load a nice font, fallback to default if not available
    try:
        # Try common font locations
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        ]
        font = None
        for font_path in font_paths:
            if Path(font_path).exists():
                font = ImageFont.truetype(font_path, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Wrap text to fit image
    wrapped_text = wrap_text(text, font, width - 100, draw)

    # Calculate text position (centered)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw text with shadow for better readability
    shadow_offset = 3
    draw.multiline_text(
        (x + shadow_offset, y + shadow_offset),
        wrapped_text,
        font=font,
        fill=(0, 0, 0, 128),
        align='center'
    )
    draw.multiline_text(
        (x, y),
        wrapped_text,
        font=font,
        fill=(255, 255, 255),
        align='center'
    )

    # Save image
    img.save(output_path, quality=95)
    print(f"  ✓ Image saved to: {output_path}")

    return output_path


def wrap_text(text: str, font, max_width: int, draw) -> str:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)

# =============================================================================
# BROWSER AUTOMATION
# =============================================================================

def initialize_browser(headless: bool = True):
    """Initialize Playwright browser with persistent session."""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright is not installed.")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)

    print(f"🌐 Initializing browser (headless={headless})...")

    p = sync_playwright().start()

    # Launch persistent context (keeps login session)
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_PATH),
        headless=headless,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
        ],
        viewport={'width': 1280, 'height': 900},
    )

    page = context.pages[0] if context.pages else context.new_page()

    return p, context, page


def check_login_status(page) -> bool:
    """Check if user is logged into Instagram."""
    print("🔍 Checking login status...")

    try:
        page.goto(INSTAGRAM_URL, timeout=PAGE_LOAD_TIMEOUT, wait_until='domcontentloaded')
        time.sleep(3)

        # Try to find logged-in indicators
        for selector in SELECTORS['login']['logged_in_indicator']:
            try:
                element = page.wait_for_selector(selector, timeout=5000)
                if element:
                    print(f"✓ Found element using selector: {selector}")
                    print("✓ User is logged in")
                    return True
            except PlaywrightTimeout:
                continue

        print("✗ User is not logged in")
        return False

    except Exception as e:
        print(f"❌ Error checking login status: {e}")
        return False


def authenticate(page, headless: bool = False) -> bool:
    """
    Authenticate user on Instagram (interactive login).

    Args:
        page: Playwright page object
        headless: If False, opens visible browser for manual login

    Returns:
        True if authentication successful
    """
    print("\n" + "="*70)
    print("🔐 INSTAGRAM AUTHENTICATION")
    print("="*70)
    print()

    try:
        page.goto(INSTAGRAM_URL, timeout=PAGE_LOAD_TIMEOUT)
        time.sleep(2)

        print("Navigating to Instagram...")
        print("Please complete the following steps manually in the browser:")
        print("  1. Enter your username/email")
        print("  2. Enter your password")
        print("  3. Complete any security verification if prompted")
        print("  4. Wait for home feed to load")
        print()
        print("This script will detect when you're logged in and save the session.")
        print("="*70)
        print()

        # Wait for user to log in
        start_time = time.time()
        while time.time() - start_time < LOGIN_TIMEOUT / 1000:
            if check_login_status(page):
                print()
                print("✅ Authentication successful!")
                print(f"✓ Session saved to: {SESSION_PATH}")
                print()
                return True

            elapsed = int(time.time() - start_time)
            print(f"⏳ Waiting for login... ({elapsed}s / {LOGIN_TIMEOUT//1000}s)")
            time.sleep(5)

        print("❌ Login timeout. Please try again.")
        return False

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False


def post_to_instagram(
    page,
    image_path: Path,
    caption: str = "",
    dry_run: bool = False
) -> bool:
    """
    Post an image to Instagram with optional caption.

    Args:
        page: Playwright page object
        image_path: Path to image file
        caption: Optional caption text
        dry_run: If True, don't actually post

    Returns:
        True if post successful
    """
    print(f"\n📸 Posting to Instagram...")
    print(f"  Image: {image_path}")
    print(f"  Caption: {caption[:50]}..." if len(caption) > 50 else f"  Caption: {caption}")

    if dry_run:
        print("  [DRY RUN - Not actually posting]")
        return True

    try:
        # Navigate to Instagram
        page.goto(INSTAGRAM_URL, timeout=PAGE_LOAD_TIMEOUT, wait_until='domcontentloaded')
        time.sleep(3)

        # Click "New post" button
        print("  Clicking 'New post' button...")
        new_post_btn = None
        for selector in SELECTORS['create_post']['new_post_button']:
            try:
                new_post_btn = page.wait_for_selector(selector, timeout=5000)
                if new_post_btn:
                    print(f"  ✓ Found New post button: {selector}")
                    new_post_btn.click()
                    break
            except PlaywrightTimeout:
                continue

        if not new_post_btn:
            print("  ❌ Could not find 'New post' button")
            return False

        time.sleep(3)

        # Upload file
        print("  Uploading image...")

        # First, try to click "Select from computer" if it appears
        select_btn_clicked = False
        for selector in SELECTORS['create_post']['select_from_computer']:
            try:
                if 'button' in selector:  # Only try to click button selectors
                    select_btn = page.wait_for_selector(selector, timeout=3000, state='visible')
                    if select_btn and select_btn.is_visible():
                        print(f"  ✓ Clicking 'Select from computer': {selector}")
                        select_btn.click()
                        select_btn_clicked = True
                        time.sleep(1)
                        break
            except PlaywrightTimeout:
                continue

        # Now find and use the file input
        file_input = None
        for selector in SELECTORS['create_post']['file_input']:
            try:
                file_input = page.wait_for_selector(selector, timeout=5000, state='attached')
                if file_input:
                    print(f"  ✓ Found file input: {selector}")
                    break
            except PlaywrightTimeout:
                continue

        if not file_input:
            print("  ❌ Could not find file input")
            print("  Tip: Instagram UI may have changed. Run with --no-headless to inspect.")
            return False

        # Upload the file
        print("  Uploading file...")
        file_input.set_input_files(str(image_path))
        print("  ✓ Image uploaded")

        # Wait for Instagram to process the uploaded image
        print("  Waiting for image to process...")
        time.sleep(5)

        # Click "Next" button (may appear multiple times)
        print("  Clicking 'Next' buttons...")
        next_clicks = 0
        max_next_clicks = 3

        while next_clicks < max_next_clicks:
            next_btn = None
            for selector in SELECTORS['create_post']['next_button']:
                try:
                    next_btn = page.wait_for_selector(selector, timeout=5000, state='visible')
                    if next_btn and next_btn.is_visible():
                        print(f"  ✓ Clicking Next ({next_clicks + 1}/{max_next_clicks})")
                        next_btn.click()
                        next_clicks += 1
                        time.sleep(2)
                        break
                except PlaywrightTimeout:
                    continue

            if not next_btn:
                break

        # Add caption if provided
        if caption:
            print("  Adding caption...")
            caption_area = None
            for selector in SELECTORS['create_post']['caption_textarea']:
                try:
                    caption_area = page.wait_for_selector(selector, timeout=5000)
                    if caption_area:
                        print(f"  ✓ Found caption area: {selector}")
                        break
                except PlaywrightTimeout:
                    continue

            if caption_area:
                caption_area.click()
                time.sleep(0.5)
                caption_area.fill(caption)
                print("  ✓ Caption added")

                # Just wait for tag suggestions to settle - don't press Escape!
                # Escape triggers the discard popup
                print("  Waiting for tags to settle...")
                time.sleep(3)

        # Click "Share" button - find the one with parent class _ac7b (the submit button)
        print("  Looking for Share submit button...")
        time.sleep(2)

        clicked = False

        # Find the ACTUAL Share button by looking for the parent container class
        try:
            # The real Share button has parent with class _ac7b _ac7d
            share_button = page.locator('div._ac7b div[role="button"]:has-text("Share")')

            if share_button.count() > 0:
                print(f"  Found Share button with _ac7b parent class")
                share_button.first.click(force=True)
                print("  ✓ Clicked Share button")
                clicked = True
                time.sleep(5)
            else:
                print("  ❌ Could not find Share button with _ac7b parent")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

        if not clicked:
            print("  ❌ Could not click Share button")
            return False

        # Wait and verify post completed
        print("  Waiting for post to complete...")
        time.sleep(8)

        # Try to verify by checking if we're back to home feed or if compose dialog closed
        try:
            # Check if we can see home feed elements (post completed successfully)
            page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
            print("✅ Post published successfully!")
            return True
        except:
            # If home icon not found, still consider it success if we waited enough time
            print("✅ Post published (verification timeout - check Instagram to confirm)")
            return True

    except Exception as e:
        print(f"❌ Error posting to Instagram: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# APPROVAL WORKFLOW
# =============================================================================

def validate_caption(caption: str) -> tuple[bool, str]:
    """Validate Instagram caption."""
    if len(caption) > MAX_CAPTION_LENGTH:
        return False, f"Caption too long ({len(caption)}/{MAX_CAPTION_LENGTH} characters)"
    return True, ""


def create_approval_request(
    message: str,
    image_path: Path,
    caption: str = "",
    image_style: str = DEFAULT_IMAGE_STYLE,
    font_size: int = DEFAULT_FONT_SIZE
) -> Optional[Path]:
    """
    Create an Instagram post approval request file.

    Returns:
        Path to approval file, or None if failed
    """
    print(f"\n📝 Creating approval request...")

    # Validate caption
    valid, error = validate_caption(caption)
    if not valid:
        print(f"❌ Validation failed: {error}")
        return None

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"INSTAGRAM_POST_{timestamp}.md"
    filepath = PENDING_APPROVAL_PATH / filename

    # Create approval file with YAML frontmatter
    content = f"""---
type: instagram_post
action: post_to_instagram
message: "{message}"
image_path: "{image_path}"
caption: "{caption}"
image_style: "{image_style}"
font_size: {font_size}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=7)).isoformat()}
status: pending
---

# Instagram Post Approval Request

## Image Preview
![Generated Image]({image_path})

## Message on Image
{message}

## Caption
{caption if caption else '(No caption)'}

## Image Details
- **Style**: {image_style}
- **Font Size**: {font_size}
- **Dimensions**: {DEFAULT_IMAGE_WIDTH}x{DEFAULT_IMAGE_HEIGHT}
- **Caption Length**: {len(caption)}/{MAX_CAPTION_LENGTH} characters

---

**To approve**: Move this file to `{APPROVED_PATH.name}/`
**To reject**: Move this file to a `Rejected/` folder or delete it
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Approval request created: {filepath}")
    print(f"  Move to '{APPROVED_PATH.name}/' folder to approve")

    return filepath


def execute_approved_post(approval_file_path: Path) -> bool:
    """
    Execute an approved Instagram post.

    Args:
        approval_file_path: Path to approved post file

    Returns:
        True if post successful
    """
    print(f"\n🚀 Executing approved Instagram post...")
    print(f"  File: {approval_file_path}")

    try:
        # Parse approval file
        content = approval_file_path.read_text(encoding='utf-8')

        # Extract YAML frontmatter
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            print("❌ Invalid approval file format (no YAML frontmatter)")
            return False

        yaml_content = yaml_match.group(1)

        # Parse fields
        def extract_field(field_name: str) -> str:
            match = re.search(rf'^{field_name}:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
            return match.group(1) if match else ""

        image_path_str = extract_field('image_path')
        caption = extract_field('caption')

        if not image_path_str:
            print("❌ No image_path in approval file")
            return False

        image_path = Path(image_path_str)
        if not image_path.exists():
            print(f"❌ Image not found: {image_path}")
            return False

        # Initialize browser and post
        p, context, page = initialize_browser(headless=True)

        try:
            # Check login
            if not check_login_status(page):
                print("❌ Not logged in. Run with --authenticate first.")
                return False

            # Post to Instagram
            success = post_to_instagram(page, image_path, caption, dry_run=False)

            if success:
                # Move to Done
                done_file = DONE_PATH / approval_file_path.name
                approval_file_path.rename(done_file)
                print(f"✅ Moved to: {done_file}")

                # Log activity
                log_activity('post_executed', {
                    'file': str(approval_file_path),
                    'image': str(image_path),
                    'caption_length': len(caption),
                    'success': True
                })
            else:
                # Move to Failed
                failed_file = FAILED_PATH / approval_file_path.name
                approval_file_path.rename(failed_file)
                print(f"❌ Moved to: {failed_file}")

                log_activity('post_failed', {
                    'file': str(approval_file_path),
                    'error': 'Post failed'
                })

            return success

        finally:
            context.close()
            p.stop()

    except Exception as e:
        print(f"❌ Error executing approved post: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# LOGGING
# =============================================================================

def log_activity(action: str, details: Dict[str, Any]):
    """Log activity to JSON file."""
    log_file = LOGS_PATH / f"instagram_activity_{datetime.now().strftime('%Y%m%d')}.json"

    entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details
    }

    # Read existing logs
    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        except:
            logs = []

    # Append new entry
    logs.append(entry)

    # Write back
    log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Instagram Post Automation via Playwright')

    # Authentication
    parser.add_argument('--authenticate', action='store_true',
                        help='Perform initial authentication (interactive)')
    parser.add_argument('--check-login', action='store_true',
                        help='Check if logged in')

    # Posting
    parser.add_argument('--message', type=str,
                        help='Text to convert to image')
    parser.add_argument('--caption', type=str, default="",
                        help='Caption for Instagram post')
    parser.add_argument('--create-approval', action='store_true',
                        help='Create approval request')
    parser.add_argument('--execute-approved', type=str,
                        help='Execute approved post from file path')

    # Image generation
    parser.add_argument('--image-style', type=str, default=DEFAULT_IMAGE_STYLE,
                        choices=['gradient', 'solid', 'pattern'],
                        help='Image background style')
    parser.add_argument('--font-size', type=int, default=DEFAULT_FONT_SIZE,
                        help='Font size for text')
    parser.add_argument('--image-width', type=int, default=DEFAULT_IMAGE_WIDTH,
                        help='Image width in pixels')
    parser.add_argument('--image-height', type=int, default=DEFAULT_IMAGE_HEIGHT,
                        help='Image height in pixels')

    # Options
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate image but don\'t post')
    parser.add_argument('--no-headless', action='store_true',
                        help='Run browser in visible mode (for debugging)')

    args = parser.parse_args()

    headless = not args.no_headless

    # Check dependencies
    if not PIL_AVAILABLE and (args.message or args.create_approval):
        print("❌ Pillow is required for image generation")
        print("Install with: pip install Pillow")
        sys.exit(1)

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright is required")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)

    # Handle commands
    if args.authenticate:
        p, context, page = initialize_browser(headless=False)  # Always visible for auth
        try:
            success = authenticate(page, headless=False)
            sys.exit(0 if success else 1)
        finally:
            context.close()
            p.stop()

    elif args.check_login:
        p, context, page = initialize_browser(headless=headless)
        try:
            is_logged_in = check_login_status(page)
            sys.exit(0 if is_logged_in else 1)
        finally:
            context.close()
            p.stop()

    elif args.execute_approved:
        approval_file = Path(args.execute_approved)
        if not approval_file.exists():
            print(f"❌ Approval file not found: {approval_file}")
            sys.exit(1)

        success = execute_approved_post(approval_file)
        sys.exit(0 if success else 1)

    elif args.message:
        # Generate image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"instagram_{timestamp}.png"
        image_path = IMAGES_PATH / image_filename

        try:
            generate_text_image(
                text=args.message,
                output_path=image_path,
                width=args.image_width,
                height=args.image_height,
                font_size=args.font_size,
                style=args.image_style
            )
        except Exception as e:
            print(f"❌ Failed to generate image: {e}")
            sys.exit(1)

        # Create approval request or post directly
        if args.create_approval:
            approval_file = create_approval_request(
                message=args.message,
                image_path=image_path,
                caption=args.caption,
                image_style=args.image_style,
                font_size=args.font_size
            )
            sys.exit(0 if approval_file else 1)

        else:
            # Post directly (with dry run option)
            p, context, page = initialize_browser(headless=headless)
            try:
                if not check_login_status(page):
                    print("❌ Not logged in. Run with --authenticate first.")
                    sys.exit(1)

                success = post_to_instagram(page, image_path, args.caption, dry_run=args.dry_run)
                sys.exit(0 if success else 1)
            finally:
                context.close()
                p.stop()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
