#!/usr/bin/env python3
"""
WhatsApp Watcher for Personal AI Employee

Monitors WhatsApp Web for important messages using Playwright browser automation.
Detects messages containing specific keywords and creates task files in Needs_Action.

IMPORTANT: This uses WhatsApp Web automation. Be aware of WhatsApp's terms of service.
Use responsibly and ensure you comply with WhatsApp's policies.

Requirements:
- Playwright installed: pip install playwright
- Playwright browsers: playwright install chromium
- WhatsApp Web authenticated session

Author: Personal AI Employee Project
Created: 2026-01-12
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import json
import time

# Add parent directory to path for base_watcher import
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("WARNING: Playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install chromium")


# Configuration
VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
CHECK_INTERVAL = 30  # Check every 30 seconds (more frequent for messaging)

# Keywords to detect in messages (case-insensitive)
URGENT_KEYWORDS = [
    'urgent', 'asap', 'emergency', 'critical', 'help',
    'invoice', 'payment', 'pay', 'bill',
    'deadline', 'today', 'now', 'immediately',
    'important', 'priority', 'attention'
]


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Web watcher that monitors for important messages.

    Uses Playwright to automate WhatsApp Web and detect messages
    containing urgent keywords. Creates task files for AI to process.

    Features:
    - Persistent browser session (stays logged in)
    - Keyword-based filtering
    - Unread message detection
    - Automatic screenshot capture
    - Group and individual chat support
    """

    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        headless: bool = True
    ):
        """
        Initialize WhatsApp watcher.

        Args:
            vault_path: Path to vault root
            session_path: Path to persistent browser session data
            keywords: List of keywords to monitor (default: URGENT_KEYWORDS)
            headless: Run browser in headless mode (default: True)
        """
        # Initialize base watcher
        super().__init__(vault_path, check_interval=CHECK_INTERVAL, watcher_name="WhatsAppWatcher")

        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required. Install with: pip install playwright")

        # Configuration
        self.keywords = keywords or URGENT_KEYWORDS
        self.headless = headless
        self.session_path = Path(session_path) if session_path else (
            Path(__file__).parent / "whatsapp_session"
        )

        # Create session directory
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Browser context
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self.logger.info(f"Keywords: {', '.join(self.keywords)}")
        self.logger.info(f"Session path: {self.session_path}")
        self.logger.info(f"Headless mode: {self.headless}")

    def initialize_browser(self) -> bool:
        """
        Initialize Playwright browser with persistent session.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing browser...")

            self.playwright = sync_playwright().start()

            # Launch persistent context (maintains login state)
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                ],
                viewport={'width': 1280, 'height': 720}
            )

            # Get or create page
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()

            # Navigate to WhatsApp Web
            self.logger.info("Navigating to WhatsApp Web...")
            self.page.goto('https://web.whatsapp.com', timeout=60000)

            # Give page time to start loading
            self.logger.info("Waiting for page to load...")
            time.sleep(3)

            # Wait for network to settle
            try:
                self.page.wait_for_load_state('networkidle', timeout=30000)
            except PlaywrightTimeoutError:
                self.logger.warning("Network still loading, continuing anyway...")

            # Wait for either QR code or chat list (already logged in)
            self.logger.info("Detecting WhatsApp Web interface...")

            # Try multiple selectors for chat list (WhatsApp changes these)
            chat_selectors = [
                '[data-testid="chat-list"]',  # Original selector
                'div[aria-label="Chat list"]',  # ARIA label
                'div[role="grid"]',  # Chat list container
                'input[title="Search or start a new chat"]',  # Search box (indicates loaded)
                'span:has-text("Search or start a new chat")',  # Search placeholder
                'button[title="New chat"]',  # New chat button
                'div:has-text("Message notifications are off")',  # Notification banner
            ]

            chat_loaded = False
            for selector in chat_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000)
                    self.logger.info(f"✓ WhatsApp Web loaded successfully (found: {selector})")
                    chat_loaded = True
                    break
                except PlaywrightTimeoutError:
                    continue

            if chat_loaded:
                return True

            # If chat list not detected, check for QR code
            self.logger.info("Chat list not found, checking for QR code...")

            # Try multiple selectors for QR code (WhatsApp changes these)
            qr_selectors = [
                'canvas[aria-label="Scan this QR code to link a device!"]',
                'canvas[aria-label*="QR code"]',
                'canvas[aria-label*="Scan"]',
                'div[data-ref] canvas',  # QR code canvas
                'canvas'  # Any canvas (last resort)
            ]

            qr_code = None
            for selector in qr_selectors:
                try:
                    qr_code = self.page.wait_for_selector(selector, timeout=5000)
                    if qr_code:
                        self.logger.info(f"✓ QR code detected using selector: {selector}")
                        break
                except PlaywrightTimeoutError:
                    continue

            if qr_code:
                self.logger.warning("=" * 70)
                self.logger.warning("AUTHENTICATION REQUIRED")
                self.logger.warning("Please scan the QR code in the browser window")
                self.logger.warning("Waiting for authentication...")
                self.logger.warning("=" * 70)

                # Wait for authentication (chat list appears)
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                self.logger.info("✓ Authentication successful!")
                return True

            else:
                self.logger.error("Could not detect WhatsApp Web interface")
                self.logger.error("The page may not have loaded correctly")
                self.logger.error("Current URL: " + self.page.url)

                # Try to take a diagnostic screenshot
                try:
                    debug_screenshot = self.session_path / "debug_screenshot.png"
                    self.page.screenshot(path=str(debug_screenshot))
                    self.logger.error(f"Diagnostic screenshot saved to: {debug_screenshot}")
                except:
                    pass

                return False

        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}", exc_info=True)
            return False

    def check_for_updates(self) -> List[Dict]:
        """
        Check WhatsApp Web for new messages with urgent keywords.

        Returns:
            List of message dictionaries with details
        """
        if not self.page:
            self.logger.error("Browser not initialized")
            return []

        try:
            # Find all unread chat elements
            unread_chats = self.page.query_selector_all('[data-testid="cell-frame-container"] [aria-label*="unread message"]')

            if not unread_chats:
                self.logger.debug("No unread messages")
                return []

            self.logger.info(f"Found {len(unread_chats)} unread chat(s)")

            urgent_messages = []

            # Check each unread chat for keywords
            for chat_element in unread_chats:
                try:
                    # Get chat name
                    chat_name_elem = chat_element.query_selector('[data-testid="cell-frame-title"]')
                    chat_name = chat_name_elem.inner_text() if chat_name_elem else "Unknown"

                    # Get last message preview
                    message_preview_elem = chat_element.query_selector('[data-testid="last-msg-text"]')
                    message_preview = message_preview_elem.inner_text() if message_preview_elem else ""

                    # Check if message contains urgent keywords
                    message_lower = message_preview.lower()
                    matched_keywords = [kw for kw in self.keywords if kw in message_lower]

                    if matched_keywords:
                        # Create unique ID from chat name and timestamp
                        message_id = f"{chat_name}_{int(time.time())}"

                        # Skip if already processed
                        if self.is_processed(message_id):
                            continue

                        # Get timestamp if available
                        time_elem = chat_element.query_selector('[data-testid="cell-frame-secondary"] span')
                        timestamp_str = time_elem.inner_text() if time_elem else "Unknown"

                        urgent_messages.append({
                            'id': message_id,
                            'chat_name': chat_name,
                            'preview': message_preview,
                            'timestamp': timestamp_str,
                            'matched_keywords': matched_keywords,
                            'is_group': self._is_group_chat(chat_element)
                        })

                        self.logger.info(f"Urgent message from: {chat_name}")
                        self.logger.info(f"  Keywords: {', '.join(matched_keywords)}")

                except Exception as e:
                    self.logger.error(f"Error processing chat element: {e}")
                    continue

            return urgent_messages

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}", exc_info=True)
            return []

    def _is_group_chat(self, chat_element) -> bool:
        """
        Determine if a chat is a group chat.

        Args:
            chat_element: Chat element from WhatsApp Web

        Returns:
            True if group chat, False otherwise
        """
        try:
            # Check for group icon or participant count
            group_indicators = chat_element.query_selector('[data-icon="group"]')
            return group_indicators is not None
        except:
            return False

    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create task file for the WhatsApp message.

        Args:
            message: Dictionary with message details

        Returns:
            Path to created task file or None if failed
        """
        try:
            timestamp = datetime.now().isoformat()
            safe_chat_name = "".join(c for c in message['chat_name'] if c.isalnum() or c in (' ', '_', '-'))
            safe_timestamp = timestamp.replace(':', '-').replace('.', '-')

            # Create filename
            task_filename = f"WHATSAPP_{safe_chat_name}_{safe_timestamp}.md"
            task_path = self.needs_action / task_filename

            # Determine priority based on keywords
            priority = self._determine_priority(message['matched_keywords'])

            # Take screenshot if possible
            screenshot_path = None
            try:
                screenshot_filename = f"screenshot_{safe_timestamp}.png"
                screenshot_path = self.needs_action / screenshot_filename
                self.page.screenshot(path=str(screenshot_path), full_page=False)
                self.logger.info(f"✓ Screenshot saved: {screenshot_filename}")
            except Exception as e:
                self.logger.warning(f"Could not capture screenshot: {e}")

            # Create task content
            task_content = f"""---
type: whatsapp
chat_name: {message['chat_name']}
message_id: {message['id']}
received: {timestamp}
whatsapp_timestamp: {message['timestamp']}
priority: {priority}
status: pending
is_group: {message['is_group']}
matched_keywords: {', '.join(message['matched_keywords'])}
---

# WhatsApp Message: {message['chat_name']}

## Message Information
- **From:** {message['chat_name']}
- **Type:** {"Group" if message['is_group'] else "Individual"}
- **Received:** {timestamp}
- **WhatsApp Time:** {message['timestamp']}
- **Priority:** {priority}
- **Keywords Matched:** {', '.join(message['matched_keywords'])}

## Message Preview
{message['preview']}

## Why This Was Flagged
This message was automatically detected because it contains urgent keywords:
- **Matched:** {', '.join(message['matched_keywords'])}

## Suggested Actions
- [ ] Open WhatsApp Web and read full message
- [ ] Reply to sender
- [ ] Take requested action
- [ ] Archive after processing
- [ ] Update status in this file

## Processing Notes
Add notes here about actions taken on this message.

## Screenshots
{f'![Screenshot]({screenshot_filename})' if screenshot_path else 'No screenshot available'}

## How to Access
1. Open WhatsApp Web: https://web.whatsapp.com
2. Search for: {message['chat_name']}
3. Read the full conversation context

---

*Task created by WhatsApp Watcher*
*Timestamp: {timestamp}*
*Auto-detected from keyword monitoring*
"""

            # Write task file
            task_path.write_text(task_content, encoding='utf-8')

            # Mark as processed
            self.mark_as_processed(message['id'])

            # Log the action
            self.log_action(
                action_type='whatsapp_message_detected',
                details={
                    'chat_name': message['chat_name'],
                    'keywords': message['matched_keywords'],
                    'is_group': message['is_group'],
                    'preview': message['preview'][:50]
                },
                task_filename=task_filename
            )

            return task_path

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}", exc_info=True)
            return None

    def _determine_priority(self, keywords: List[str]) -> str:
        """
        Determine message priority based on matched keywords.

        Args:
            keywords: List of matched keywords

        Returns:
            Priority level (high, medium, low)
        """
        high_priority = ['urgent', 'asap', 'emergency', 'critical', 'now', 'immediately']

        if any(kw in keywords for kw in high_priority):
            return 'high'

        return 'medium'

    def run(self):
        """
        Main monitoring loop with browser initialization.
        """
        try:
            # Initialize browser
            if not self.initialize_browser():
                self.logger.error("Failed to initialize browser. Exiting.")
                sys.exit(1)

            # Run the base watcher loop
            super().run()

        except KeyboardInterrupt:
            self._shutdown()

        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            self._cleanup_browser()
            sys.exit(1)

    def _shutdown(self):
        """Override shutdown to cleanup browser resources."""
        self.logger.info("Shutting down WhatsApp watcher...")
        self._cleanup_browser()
        super()._shutdown()

    def _cleanup_browser(self):
        """Clean up browser resources."""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("✓ Browser resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up browser: {e}")


def main():
    """
    Main entry point for WhatsApp watcher.
    """
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Web Watcher for Personal AI Employee')
    parser.add_argument('--session-path', help='Path to browser session data')
    parser.add_argument('--visible', action='store_true', help='Run browser in visible mode (not headless)')
    parser.add_argument('--keywords', help='Comma-separated keywords to monitor')

    args = parser.parse_args()

    # Parse keywords if provided
    keywords = None
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]

    # Create watcher
    watcher = WhatsAppWatcher(
        vault_path=str(VAULT_PATH),
        session_path=args.session_path,
        keywords=keywords,
        headless=not args.visible
    )

    # Start monitoring
    watcher.run()


if __name__ == "__main__":
    main()
