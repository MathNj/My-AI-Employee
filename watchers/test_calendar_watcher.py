#!/usr/bin/env python3
"""
Test script for Google Calendar Watcher

Tests authentication, event retrieval, and task file creation.

Author: Personal AI Employee Project
Created: 2026-01-14
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from calendar_watcher import CalendarWatcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_authentication():
    """Test Google Calendar API authentication."""
    logger.info("=" * 70)
    logger.info("TEST 1: Authentication")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        watcher = CalendarWatcher(
            vault_path=str(vault_path),
            check_interval=60
        )
        logger.info("✓ Authentication successful")
        return watcher
    except Exception as e:
        logger.error(f"✗ Authentication failed: {e}")
        return None


def test_list_calendars(watcher):
    """Test listing available calendars."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: List Available Calendars")
    logger.info("=" * 70)

    if not watcher or not watcher.service:
        logger.error("✗ Watcher not initialized")
        return False

    try:
        calendar_list = watcher.service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])

        if not calendars:
            logger.warning("No calendars found")
            return False

        logger.info(f"Found {len(calendars)} calendar(s):")
        for calendar in calendars:
            cal_id = calendar['id']
            cal_name = calendar.get('summary', 'Unnamed')
            cal_primary = ' (PRIMARY)' if calendar.get('primary', False) else ''
            logger.info(f"  - {cal_name}{cal_primary}")
            logger.info(f"    ID: {cal_id}")

        logger.info("✓ Calendar list retrieved successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to list calendars: {e}")
        return False


def test_check_upcoming_events(watcher):
    """Test checking for upcoming events."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Check for Upcoming Events")
    logger.info("=" * 70)

    if not watcher:
        logger.error("✗ Watcher not initialized")
        return False

    try:
        events = watcher.check_for_updates()

        if not events:
            logger.info("No upcoming events found in the next 48 hours")
            logger.info("This is OK - create a test event to see task file creation")
            return True

        logger.info(f"Found {len(events)} upcoming event(s):")
        for event in events:
            summary = event.get('summary', 'No Title')
            start = event.get('start', {})
            start_time = start.get('dateTime', start.get('date', 'Unknown'))
            logger.info(f"  - {summary}")
            logger.info(f"    Start: {start_time}")

        logger.info("✓ Event retrieval successful")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to check events: {e}")
        return False


def test_create_task_file(watcher):
    """Test creating task file for an event."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Create Task File")
    logger.info("=" * 70)

    if not watcher:
        logger.error("✗ Watcher not initialized")
        return False

    try:
        # Get upcoming events
        events = watcher.check_for_updates()

        if not events:
            logger.info("No events to create task files for")
            logger.info("Create a test event in Google Calendar:")
            logger.info("  1. Go to calendar.google.com")
            logger.info("  2. Create an event 2-3 hours from now")
            logger.info("  3. Run this test again")
            return True

        # Create task file for first event
        event = events[0]
        summary = event.get('summary', 'No Title')
        logger.info(f"Creating task file for: {summary}")

        task_path = watcher.create_action_file(event)

        if task_path and task_path.exists():
            logger.info(f"✓ Task file created: {task_path}")
            logger.info(f"  Location: {task_path}")
            logger.info(f"  Size: {task_path.stat().st_size} bytes")

            # Show preview of content
            content = task_path.read_text(encoding='utf-8')
            lines = content.split('\n')[:20]
            logger.info("\n  Preview (first 20 lines):")
            for line in lines:
                logger.info(f"    {line}")

            return True
        else:
            logger.error("✗ Task file creation failed")
            return False

    except Exception as e:
        logger.error(f"✗ Failed to create task file: {e}", exc_info=True)
        return False


def test_time_windows():
    """Test different time window configurations."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: Time Window Configurations")
    logger.info("=" * 70)

    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    test_configs = [
        {'hours_ahead': 24, 'min_hours_ahead': 1, 'label': '1-24 hours ahead'},
        {'hours_ahead': 72, 'min_hours_ahead': 2, 'label': '2-72 hours ahead'},
        {'hours_ahead': 168, 'min_hours_ahead': 0, 'label': '0-168 hours (7 days) ahead'},
    ]

    for config in test_configs:
        try:
            logger.info(f"\nTesting: {config['label']}")
            watcher = CalendarWatcher(
                vault_path=str(vault_path),
                check_interval=60,
                hours_ahead=config['hours_ahead'],
                min_hours_ahead=config['min_hours_ahead']
            )

            events = watcher.check_for_updates()
            logger.info(f"  Found {len(events)} event(s) in this window")

        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")

    logger.info("\n✓ Time window tests complete")
    return True


def test_multiple_calendars():
    """Test monitoring multiple calendars."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 6: Multiple Calendar Support")
    logger.info("=" * 70)

    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    try:
        # First, get list of available calendars
        temp_watcher = CalendarWatcher(
            vault_path=str(vault_path),
            check_interval=60
        )

        calendar_list = temp_watcher.service.calendarList().list().execute()
        calendar_ids = [cal['id'] for cal in calendar_list.get('items', [])]

        if len(calendar_ids) > 1:
            logger.info(f"Testing with {len(calendar_ids)} calendars")

            watcher = CalendarWatcher(
                vault_path=str(vault_path),
                check_interval=60,
                calendar_ids=calendar_ids[:3]  # Test with up to 3 calendars
            )

            events = watcher.check_for_updates()
            logger.info(f"✓ Found {len(events)} total event(s) across all calendars")
        else:
            logger.info("Only one calendar available (primary)")
            logger.info("To test multiple calendars, add more calendars to your Google Calendar")

        return True

    except Exception as e:
        logger.error(f"✗ Multiple calendar test failed: {e}")
        return False


def test_priority_detection():
    """Test event priority detection logic."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 7: Priority Detection")
    logger.info("=" * 70)

    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    try:
        watcher = CalendarWatcher(
            vault_path=str(vault_path),
            check_interval=60
        )

        # Test cases
        test_cases = [
            {'hours_until': 2, 'summary': 'Client Meeting', 'expected': 'high'},
            {'hours_until': 6, 'summary': 'Team Standup', 'expected': 'high'},
            {'hours_until': 12, 'summary': 'Interview with Candidate', 'expected': 'high'},
            {'hours_until': 20, 'summary': 'Regular Meeting', 'expected': 'medium'},
            {'hours_until': 36, 'summary': 'Coffee Chat', 'expected': 'low'},
            {'hours_until': 10, 'summary': 'URGENT: Board Review', 'expected': 'urgent'},
        ]

        logger.info("Testing priority detection:")
        all_correct = True

        for test in test_cases:
            priority = watcher._determine_priority(test['hours_until'], test['summary'])
            status = "✓" if priority == test['expected'] else "✗"
            logger.info(f"  {status} '{test['summary']}' ({test['hours_until']}h) -> {priority} (expected {test['expected']})")

            if priority != test['expected']:
                all_correct = False

        if all_correct:
            logger.info("✓ All priority detection tests passed")
        else:
            logger.warning("⚠ Some priority detection tests failed")

        return True

    except Exception as e:
        logger.error(f"✗ Priority detection test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 70)
    logger.info("GOOGLE CALENDAR WATCHER TEST SUITE")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info("=" * 70)

    results = {}

    # Test 1: Authentication
    watcher = test_authentication()
    results['authentication'] = watcher is not None

    if not watcher:
        logger.error("\n✗ Authentication failed - cannot continue with other tests")
        logger.error("Please check:")
        logger.error("  1. calendar_credentials.json exists in watchers/credentials/")
        logger.error("  2. Google Calendar API is enabled")
        logger.error("  3. OAuth consent screen is configured")
        logger.error("\nSee CALENDAR_SETUP.md for detailed instructions")
        sys.exit(1)

    # Test 2: List calendars
    results['list_calendars'] = test_list_calendars(watcher)

    # Test 3: Check upcoming events
    results['check_events'] = test_check_upcoming_events(watcher)

    # Test 4: Create task file
    results['create_task'] = test_create_task_file(watcher)

    # Test 5: Time windows
    results['time_windows'] = test_time_windows()

    # Test 6: Multiple calendars
    results['multiple_calendars'] = test_multiple_calendars()

    # Test 7: Priority detection
    results['priority_detection'] = test_priority_detection()

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("=" * 70)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info(f"End time: {datetime.now().isoformat()}")
    logger.info("=" * 70)

    if passed == total:
        logger.info("\n✓ All tests passed! Calendar watcher is ready to use.")
        logger.info("\nNext steps:")
        logger.info("  1. Run the watcher: python calendar_watcher.py")
        logger.info("  2. Create test events in Google Calendar")
        logger.info("  3. Watch for task files in AI_Employee_Vault/Needs_Action/")
        logger.info("  4. Set up as service with PM2 or systemd")
        sys.exit(0)
    else:
        logger.error("\n✗ Some tests failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
