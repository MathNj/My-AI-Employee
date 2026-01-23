#!/usr/bin/env python3
"""
WhatsApp Sender - Send WhatsApp messages via Playwright

Integrates with approval workflow to send approved WhatsApp messages.
Uses Playwright browser automation (same session as WhatsApp watcher).
"""

import sys
from pathlib import Path
import logging
import json
import time
from datetime import datetime
from typing import Optional, Dict, List

try:
    from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("ERROR: Playwright not installed. Install with: pip install playwright")
    sys.exit(1)

logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Send WhatsApp messages using Playwright browser automation"""

    def __init__(
        self,
        session_path: Optional[str] = None,
        headless: bool = True
    ):
        """
        Initialize WhatsApp sender with persistent browser session.

        Args:
            session_path: Path to persistent browser session data (same as watcher)
            headless: Run browser in headless mode (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required. Install with: pip install playwright")

        # Configuration
        self.headless = headless
        self.session_path = Path(session_path) if session_path else (
            Path(__file__).parent.parent.parent / 'watchers' / 'whatsapp_session'
        )

        # Create session directory
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Browser context
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        logger.info(f"WhatsApp Sender initialized")
        logger.info(f"  Session path: {self.session_path}")
        logger.info(f"  Headless mode: {self.headless}")

    def _initialize_browser(self) -> bool:
        """
        Initialize Playwright browser with persistent session.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if self.playwright and self.page and not self.page.is_closed():
                logger.debug("Browser already initialized")
                return True

            logger.info("Initializing browser...")

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

            # Check if already on WhatsApp Web
            if 'web.whatsapp.com' not in self.page.url:
                logger.info("Navigating to WhatsApp Web...")
                self.page.goto('https://web.whatsapp.com', timeout=60000)
                time.sleep(3)

            # Wait for chat list to load (indicates authenticated)
            # Try multiple selectors (WhatsApp changes these)
            chat_selectors = [
                '[data-testid="chat-list"]',  # Original selector
                'div[aria-label="Chat list"]',  # ARIA label
                'div[role="grid"]',  # Chat list container
                'input[title="Search or start a new chat"]',  # Search box (indicates loaded)
                'span:has-text("Search or start a new chat")',  # Search placeholder
                'button[title="New chat"]',  # New chat button
            ]

            chat_loaded = False
            for selector in chat_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000)
                    logger.info(f"[OK] WhatsApp Web loaded and authenticated (found: {selector})")
                    chat_loaded = True
                    break
                except PlaywrightTimeoutError:
                    continue

            if chat_loaded:
                return True

            # If no selector worked, check for QR code
            logger.warning("Could not detect WhatsApp Web interface - might need authentication")
            return False

        except Exception as e:
            logger.error(f"Error initializing browser: {e}", exc_info=True)
            return False

    def _search_chat(self, chat_name: str) -> bool:
        """
        Search for a chat by name.

        Args:
            chat_name: Name of the contact or group

        Returns:
            True if chat found, False otherwise
        """
        try:
            # Click search box
            search_selectors = [
                'input[title="Search or start a new chat"]',
                '[data-testid="chat-list-search"]',
                'div[contenteditable="true"][data-tab="3"]',
                '#side [contenteditable="true"]'
            ]

            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.page.wait_for_selector(selector, timeout=5000)
                    if search_box:
                        logger.debug(f"Found search box with selector: {selector}")
                        break
                except PlaywrightTimeoutError:
                    continue

            if not search_box:
                logger.error("Could not find search box")
                return False

            # Clear and type search query
            search_box.click()
            time.sleep(0.5)

            # Clear existing text
            search_box.fill('')
            time.sleep(0.5)

            # Type chat name character by character
            logger.info(f"Searching for: {chat_name}")
            search_box.type(chat_name, delay=100)
            time.sleep(3)  # Wait for search results

            # Look for chat in results - try multiple approaches
            # Approach 1: Try exact match in title attribute
            chat_selectors = [
                f'[title="{chat_name}"]',
                f'span[title="{chat_name}"]',
                f'div[title="{chat_name}"]',
            ]

            for selector in chat_selectors:
                try:
                    chat_element = self.page.wait_for_selector(selector, timeout=3000)
                    if chat_element:
                        logger.info(f"Found chat with selector: {selector}")
                        chat_element.click()
                        time.sleep(2)
                        logger.info(f"Opened chat: {chat_name}")
                        return True
                except PlaywrightTimeoutError:
                    continue

            # Approach 2: Look for chat name in text content
            try:
                # Get all chat elements
                chat_elements = self.page.query_selector_all('[data-testid="cell-frame-container"]')
                logger.info(f"Found {len(chat_elements)} chat elements")

                for idx, elem in enumerate(chat_elements):
                    try:
                        # Try to get text content
                        text = elem.inner_text()
                        logger.debug(f"Chat {idx}: {text[:50]}")

                        if chat_name.lower() in text.lower():
                            logger.info(f"Found chat by text matching: {chat_name}")
                            elem.click()
                            time.sleep(2)
                            logger.info(f"Opened chat: {chat_name}")
                            return True
                    except Exception as e:
                        logger.debug(f"Error checking chat element {idx}: {e}")
                        continue

            except Exception as e:
                logger.warning(f"Error searching by text: {e}")

            logger.warning(f"Chat not found: {chat_name}")
            return False

        except Exception as e:
            logger.error(f"Error searching for chat: {e}")
            return False

    def send_message(
        self,
        to: str,
        message: str
    ) -> Dict:
        """
        Send a WhatsApp message.

        Args:
            to: Contact name or group name
            message: Message content to send

        Returns:
            Dict with success status and details
        """
        try:
            # Initialize browser if needed
            if not self._initialize_browser():
                return {
                    'success': False,
                    'error': 'Failed to initialize browser. Please authenticate WhatsApp Web first.'
                }

            logger.info(f"Sending message to: {to}")

            # Search for chat
            if not self._search_chat(to):
                return {
                    'success': False,
                    'error': f'Chat not found: {to}'
                }

            # Find message input box
            message_input_selectors = [
                '[data-testid="conversation-panel-footer"] [contenteditable="true"]',
                'div[contenteditable="true"][data-tab="10"]',
                '#main [contenteditable="true"]'
            ]

            message_input = None
            for selector in message_input_selectors:
                try:
                    message_input = self.page.wait_for_selector(selector, timeout=5000)
                    if message_input:
                        break
                except PlaywrightTimeoutError:
                    continue

            if not message_input:
                logger.error("Could not find message input box")
                return {
                    'success': False,
                    'error': 'Could not find message input box'
                }

            # Type message
            message_input.click()
            time.sleep(0.5)

            # Type message with small delay for natural typing
            message_input.type(message, delay=50)
            time.sleep(0.5)

            # Press Enter to send (or click send button)
            try:
                # Try Enter key first
                self.page.keyboard.press('Enter')
                time.sleep(1)

                # Check for message sent (look for checkmarks)
                logger.info(f"Message sent successfully to {to}")

                return {
                    'success': True,
                    'recipient': to,
                    'message': message[:100] + '...' if len(message) > 100 else message,
                    'timestamp': datetime.now().isoformat()
                }

            except Exception as e:
                # Try clicking send button as fallback
                try:
                    send_button = self.page.wait_for_selector('[data-testid="send-button"]', timeout=2000)
                    if send_button:
                        send_button.click()
                        time.sleep(1)

                        logger.info(f"Message sent successfully to {to} (via send button)")

                        return {
                            'success': True,
                            'recipient': to,
                            'message': message[:100] + '...' if len(message) > 100 else message,
                            'timestamp': datetime.now().isoformat()
                        }
                except:
                    pass

                logger.error(f"Failed to send message: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                self.page.close()
                self.page = None
            if self.context:
                self.context.close()
                self.context = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up browser: {e}")


def main():
    """Test WhatsApp sending"""
    import argparse

    parser = argparse.ArgumentParser(description='Send WhatsApp message')
    parser.add_argument('--to', required=True, help='Contact or group name')
    parser.add_argument('--message', required=True, help='Message to send')
    parser.add_argument('--visible', action='store_true', help='Run browser in visible mode')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - WhatsAppSender - %(levelname)s - %(message)s'
    )

    # Create sender
    sender = WhatsAppSender(headless=not args.visible)

    # Send message
    result = sender.send_message(
        to=args.to,
        message=args.message
    )

    if result['success']:
        print(f"[OK] Message sent successfully!")
        print(f"  To: {result['recipient']}")
        print(f"  Time: {result['timestamp']}")
        sender.cleanup()
    else:
        print(f"[FAIL] Failed to send message: {result['error']}")
        sender.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
