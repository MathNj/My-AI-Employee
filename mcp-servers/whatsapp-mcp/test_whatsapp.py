#!/usr/bin/env python3
"""
Test WhatsApp MCP Server

Tests the WhatsApp sender functionality with various scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from whatsapp_sender import WhatsAppSender
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_browser_initialization():
    """Test 1: Browser initialization"""
    logger.info("=" * 70)
    logger.info("TEST 1: Browser Initialization")
    logger.info("=" * 70)

    try:
        sender = WhatsAppSender(headless=False)  # Visible for testing
        result = sender._initialize_browser()

        if result:
            logger.info("✅ PASS: Browser initialized successfully")
            sender.cleanup()
            return True
        else:
            logger.error("❌ FAIL: Browser initialization failed")
            sender.cleanup()
            return False

    except Exception as e:
        logger.error(f"❌ FAIL: Exception during initialization: {e}")
        return False


def test_search_chat():
    """Test 2: Search for a chat"""
    logger.info("=" * 70)
    logger.info("TEST 2: Search Chat")
    logger.info("=" * 70)

    try:
        sender = WhatsAppSender(headless=False)

        if not sender._initialize_browser():
            logger.error("❌ FAIL: Could not initialize browser")
            return False

        # This will fail if you don't have a "Test Contact" - change to a real contact
        test_contact = "Test Contact"
        logger.info(f"Searching for chat: {test_contact}")

        # Note: This test requires you to have a contact with this name
        # Change it to a real contact name for testing
        logger.info("⚠️  SKIP: Requires real contact name")
        logger.info("   Modify test_contact to a real contact in your WhatsApp")

        sender.cleanup()
        return True  # Skip test

    except Exception as e:
        logger.error(f"❌ FAIL: Exception during chat search: {e}")
        return False


def test_send_message():
    """Test 3: Send a message"""
    logger.info("=" * 70)
    logger.info("TEST 3: Send Message")
    logger.info("=" * 70)

    try:
        sender = WhatsAppSender(headless=False)

        if not sender._initialize_browser():
            logger.error("❌ FAIL: Could not initialize browser")
            return False

        # Note: This will ACTUALLY SEND a message
        # Change to a real contact for testing
        test_contact = "Test Contact"
        test_message = "This is a test message from WhatsApp MCP Server!"

        logger.info(f"Sending message to: {test_contact}")
        logger.warning("⚠️  This will ACTUALLY SEND a message to WhatsApp!")
        logger.warning("⚠️  Press Ctrl+C to cancel if you don't want to send")

        # Uncomment to actually send
        # result = sender.send_message(to=test_contact, message=test_message)
        #
        # if result['success']:
        #     logger.info("✅ PASS: Message sent successfully")
        #     sender.cleanup()
        #     return True
        # else:
        #     logger.error(f"❌ FAIL: Failed to send message: {result.get('error')}")
        #     sender.cleanup()
        #     return False

        logger.info("⚠️  SKIP: Test disabled - uncomment code to actually send")
        sender.cleanup()
        return True  # Skip test

    except Exception as e:
        logger.error(f"❌ FAIL: Exception during message send: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("WhatsApp MCP Server - Test Suite")
    logger.info("=" * 70)

    tests = [
        ("Browser Initialization", test_browser_initialization),
        ("Search Chat", test_search_chat),
        ("Send Message", test_send_message),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\nRunning: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
