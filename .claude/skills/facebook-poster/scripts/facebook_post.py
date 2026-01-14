#!/usr/bin/env python3
"""
Facebook Post Automation via Playwright
Posts text or text-to-image to Facebook using browser automation.

Usage:
    # First-time authentication
    python facebook_post.py --authenticate --no-headless

    # Check login status
    python facebook_post.py --check-login

    # Post text only
    python facebook_post.py --text "Your post text here"

    # Post with image (text converted to image)
    python facebook_post.py --message "Text for image" --text "Post caption"

    # Create approval request
    python facebook_post.py --message "Text" --text "Caption" --create-approval

    # Execute approved post
    python facebook_post.py --execute-approved /path/to/FACEBOOK_POST_timestamp.md
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
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
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# =============================================================================
# CONFIGURATION
# =============================================================================

VAULT_PATH = Path(__file__).resolve().parents[4]
SKILLS_PATH = VAULT_PATH / '.claude' / 'skills' / 'facebook-poster'
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

# Facebook Configuration
FACEBOOK_URL = "https://www.facebook.com"
MAX_POST_LENGTH = 63206  # Facebook text limit
LOGIN_TIMEOUT = 300000  # 5 minutes
PAGE_LOAD_TIMEOUT = 60000

# Image Generation Defaults
DEFAULT_IMAGE_WIDTH = 1200
DEFAULT_IMAGE_HEIGHT = 630
DEFAULT_FONT_SIZE = 50
DEFAULT_IMAGE_STYLE = 'gradient'

# Facebook Selectors
SELECTORS = {
    'login': {
        'logged_in_indicator': [
            'div[aria-label="Account"]',
            'div[aria-label="Your profile"]',
            'svg[aria-label="Your profile"]',
        ]
    },
    'create_post': {
        'whats_on_mind': [
            'span:has-text("What\'s on your mind")',
            'div[role="button"]:has-text("What\'s on your mind")',
            'span:has-text("Write something")',
        ],
        'post_textarea': [
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
        ],
        'photo_video_button': [
            'div[aria-label="Photo/video"]',
            'div:has-text("Photo/video")',
        ],
        'file_input': [
            'input[type="file"][accept*="image"]',
            'input[type="file"]',
        ],
        'post_button': [
            'div[aria-label="Post"]',
            'div[role="button"]:has-text("Post")',
        ],
    }
}

# =============================================================================
# IMAGE GENERATION (Same as Instagram)
# =============================================================================

def generate_text_image(
    text: str,
    output_path: Path,
    width: int = DEFAULT_IMAGE_WIDTH,
    height: int = DEFAULT_IMAGE_HEIGHT,
    font_size: int = DEFAULT_FONT_SIZE,
    style: str = DEFAULT_IMAGE_STYLE
) -> Path:
    """Generate an image from text with attractive styling."""
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow is not installed. Cannot generate images.")

    print(f"\n🎨 Generating image...")
    print(f"  Style: {style}")
    print(f"  Size: {width}x{height}")

    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Apply background style
    if style == 'gradient':
        for y in range(height):
            r = int(100 + (155 * y / height))
            g = int(50 + (100 * y / height))
            b = int(200 - (50 * y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    elif style == 'solid':
        draw.rectangle([0, 0, width, height], fill=(45, 55, 72))
    elif style == 'pattern':
        draw.rectangle([0, 0, width, height], fill=(30, 30, 30))
        for i in range(0, width, 100):
            for j in range(0, height, 100):
                draw.ellipse([i, j, i+50, j+50], fill=(50, 50, 50))

    # Load font
    try:
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        font = None
        for font_path in font_paths:
            if Path(font_path).exists():
                font = ImageFont.truetype(font_path, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Wrap text
    wrapped_text = wrap_text(text, font, width - 100, draw)

    # Center text
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw shadow
    shadow_offset = 3
    draw.multiline_text(
        (x + shadow_offset, y + shadow_offset),
        wrapped_text,
        font=font,
        fill=(0, 0, 0, 128),
        align='center'
    )
    # Draw text
    draw.multiline_text(
        (x, y),
        wrapped_text,
        font=font,
        fill=(255, 255, 255),
        align='center'
    )

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
        sys.exit(1)

    print(f"🌐 Initializing browser (headless={headless})...")

    p = sync_playwright().start()
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_PATH),
        headless=headless,
        args=['--disable-blink-features=AutomationControlled'],
        viewport={'width': 1280, 'height': 900},
    )

    page = context.pages[0] if context.pages else context.new_page()
    return p, context, page


def check_login_status(page) -> bool:
    """Check if user is logged into Facebook."""
    print("🔍 Checking login status...")

    try:
        page.goto(FACEBOOK_URL, timeout=PAGE_LOAD_TIMEOUT, wait_until='domcontentloaded')
        time.sleep(3)

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
    """Authenticate user on Facebook (interactive login)."""
    print("\n" + "="*70)
    print("🔐 FACEBOOK AUTHENTICATION")
    print("="*70)
    print()

    try:
        page.goto(FACEBOOK_URL, timeout=PAGE_LOAD_TIMEOUT)
        time.sleep(2)

        print("Please complete the following steps manually in the browser:")
        print("  1. Enter your email/phone")
        print("  2. Enter your password")
        print("  3. Complete any 2FA if prompted")
        print("  4. Wait for home feed to load")
        print()
        print("This script will detect when you're logged in and save the session.")
        print("="*70)
        print()

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


def post_to_facebook(
    page,
    text: str = "",
    image_path: Optional[Path] = None,
    dry_run: bool = False
) -> bool:
    """Post to Facebook with optional text and image."""
    print(f"\n📘 Posting to Facebook...")
    if image_path:
        print(f"  Image: {image_path}")
    print(f"  Text: {text[:50]}..." if len(text) > 50 else f"  Text: {text}")

    if dry_run:
        print("  [DRY RUN - Not actually posting]")
        return True

    try:
        # Navigate to Facebook
        page.goto(FACEBOOK_URL, timeout=PAGE_LOAD_TIMEOUT, wait_until='domcontentloaded')
        time.sleep(3)

        # Click "What's on your mind" to open post composer
        print("  Opening post composer...")
        composer_opened = False
        for selector in SELECTORS['create_post']['whats_on_mind']:
            try:
                composer = page.wait_for_selector(selector, timeout=5000)
                if composer:
                    print(f"  ✓ Found composer button: {selector}")
                    composer.click()
                    composer_opened = True
                    time.sleep(2)
                    break
            except PlaywrightTimeout:
                continue

        if not composer_opened:
            print("  ❌ Could not open post composer")
            return False

        # Add image if provided
        if image_path:
            print("  Adding photo...")
            try:
                # Click Photo/Video button
                photo_btn = None
                for selector in SELECTORS['create_post']['photo_video_button']:
                    try:
                        photo_btn = page.wait_for_selector(selector, timeout=3000)
                        if photo_btn:
                            print(f"  ✓ Found Photo/Video button: {selector}")
                            photo_btn.click()
                            time.sleep(2)
                            break
                    except PlaywrightTimeout:
                        continue

                # Find and use file input
                file_input = None
                for selector in SELECTORS['create_post']['file_input']:
                    try:
                        file_input = page.wait_for_selector(selector, timeout=5000, state='attached')
                        if file_input:
                            print(f"  ✓ Found file input")
                            break
                    except PlaywrightTimeout:
                        continue

                if file_input:
                    file_input.set_input_files(str(image_path))
                    print("  ✓ Image uploaded")
                    time.sleep(3)
                else:
                    print("  ⚠️  Could not upload image")

            except Exception as e:
                print(f"  ⚠️  Image upload failed: {e}")

        # Add text
        if text:
            print("  Adding text...")
            text_area = None
            for selector in SELECTORS['create_post']['post_textarea']:
                try:
                    text_area = page.wait_for_selector(selector, timeout=5000)
                    if text_area:
                        print(f"  ✓ Found text area")
                        break
                except PlaywrightTimeout:
                    continue

            if text_area:
                text_area.click()
                time.sleep(0.5)
                text_area.fill(text)
                print("  ✓ Text added")
                time.sleep(2)

        # Click Post button
        print("  Clicking Post button...")
        post_btn = None
        for selector in SELECTORS['create_post']['post_button']:
            try:
                post_btn = page.wait_for_selector(selector, timeout=5000, state='visible')
                if post_btn and post_btn.is_visible():
                    print(f"  ✓ Found Post button: {selector}")
                    post_btn.click(force=True)
                    break
            except PlaywrightTimeout:
                continue

        if not post_btn:
            print("  ❌ Could not find Post button")
            return False

        print("  ✓ Clicked Post button")
        time.sleep(5)

        print("✅ Post published successfully!")
        return True

    except Exception as e:
        print(f"❌ Error posting to Facebook: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# APPROVAL WORKFLOW
# =============================================================================

def create_approval_request(
    text: str = "",
    message: str = "",
    image_path: Optional[Path] = None,
    image_style: str = DEFAULT_IMAGE_STYLE,
    font_size: int = DEFAULT_FONT_SIZE
) -> Optional[Path]:
    """Create a Facebook post approval request file."""
    print(f"\n📝 Creating approval request...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FACEBOOK_POST_{timestamp}.md"
    filepath = PENDING_APPROVAL_PATH / filename

    content = f"""---
type: facebook_post
action: post_to_facebook
text: "{text}"
message: "{message}"
image_path: "{image_path if image_path else ''}"
image_style: "{image_style}"
font_size: {font_size}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=7)).isoformat()}
status: pending
---

# Facebook Post Approval Request

## Post Content
{text}

"""

    if image_path:
        content += f"""## Image Preview
![Generated Image]({image_path})

## Message on Image
{message}

## Image Details
- **Style**: {image_style}
- **Font Size**: {font_size}
- **Dimensions**: {DEFAULT_IMAGE_WIDTH}x{DEFAULT_IMAGE_HEIGHT}

"""

    content += f"""---

**To approve**: Move this file to `{APPROVED_PATH.name}/`
**To reject**: Move this file to a `Rejected/` folder or delete it
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Approval request created: {filepath}")
    return filepath


def execute_approved_post(approval_file_path: Path) -> bool:
    """Execute an approved Facebook post."""
    print(f"\n🚀 Executing approved Facebook post...")
    print(f"  File: {approval_file_path}")

    try:
        content = approval_file_path.read_text(encoding='utf-8')
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            print("❌ Invalid approval file format")
            return False

        yaml_content = yaml_match.group(1)

        def extract_field(field_name: str) -> str:
            match = re.search(rf'^{field_name}:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
            return match.group(1) if match else ""

        text = extract_field('text')
        image_path_str = extract_field('image_path')
        image_path = Path(image_path_str) if image_path_str and image_path_str != '' else None

        if image_path and not image_path.exists():
            print(f"⚠️  Image not found: {image_path}")
            image_path = None

        # Initialize browser and post
        p, context, page = initialize_browser(headless=True)

        try:
            if not check_login_status(page):
                print("❌ Not logged in. Run with --authenticate first.")
                return False

            success = post_to_facebook(page, text=text, image_path=image_path, dry_run=False)

            if success:
                done_file = DONE_PATH / approval_file_path.name
                approval_file_path.rename(done_file)
                print(f"✅ Moved to: {done_file}")

                log_activity('post_executed', {
                    'file': str(approval_file_path),
                    'text_length': len(text),
                    'has_image': image_path is not None,
                    'success': True
                })
            else:
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
    log_file = LOGS_PATH / f"facebook_activity_{datetime.now().strftime('%Y%m%d')}.json"

    entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details
    }

    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        except:
            logs = []

    logs.append(entry)
    log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Facebook Post Automation via Playwright')

    # Authentication
    parser.add_argument('--authenticate', action='store_true',
                        help='Perform initial authentication')
    parser.add_argument('--check-login', action='store_true',
                        help='Check if logged in')

    # Posting
    parser.add_argument('--text', type=str,
                        help='Post text content')
    parser.add_argument('--message', type=str,
                        help='Text to convert to image')
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

    # Options
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without posting')
    parser.add_argument('--no-headless', action='store_true',
                        help='Run browser in visible mode')

    args = parser.parse_args()

    headless = not args.no_headless

    # Handle commands
    if args.authenticate:
        p, context, page = initialize_browser(headless=False)
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

    elif args.text or args.message:
        # Generate image if message provided
        image_path = None
        if args.message:
            if not PIL_AVAILABLE:
                print("❌ Pillow required for image generation")
                sys.exit(1)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"facebook_{timestamp}.png"
            image_path = IMAGES_PATH / image_filename

            try:
                generate_text_image(
                    text=args.message,
                    output_path=image_path,
                    font_size=args.font_size,
                    style=args.image_style
                )
            except Exception as e:
                print(f"❌ Failed to generate image: {e}")
                sys.exit(1)

        # Create approval request or post directly
        if args.create_approval:
            approval_file = create_approval_request(
                text=args.text or "",
                message=args.message or "",
                image_path=image_path,
                image_style=args.image_style,
                font_size=args.font_size
            )
            sys.exit(0 if approval_file else 1)
        else:
            # Post directly
            p, context, page = initialize_browser(headless=headless)
            try:
                if not check_login_status(page):
                    print("❌ Not logged in. Run with --authenticate first.")
                    sys.exit(1)

                success = post_to_facebook(page, text=args.text or "", image_path=image_path, dry_run=args.dry_run)
                sys.exit(0 if success else 1)
            finally:
                context.close()
                p.stop()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
