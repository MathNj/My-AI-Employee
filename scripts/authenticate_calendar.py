#!/usr/bin/env python3
"""
Simple script to authenticate Google Calendar with write permissions
"""
import sys
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add watchers to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'watchers'))

print("\n" + "="*70)
print("Google Calendar Authentication")
print("="*70)
print("\nThis script will:")
print("1. Open a browser window for Google OAuth")
print("2. Ask you to grant calendar permissions (READ + WRITE)")
print("3. Save the authentication token for future use")
print("\nPlease click 'Allow' in the browser window that opens.")
print("\n" + "="*70 + "\n")

try:
    from calendar_watcher import CalendarWatcher

    # Create watcher instance (will trigger OAuth)
    vault_path = Path(__file__).parent.parent
    watcher = CalendarWatcher(
        vault_path=str(vault_path),
        check_interval=300,
        hours_ahead=48,
        min_hours_ahead=1
    )

    print("\n" + "="*70)
    print("✅ Authentication Successful!")
    print("="*70)
    print(f"\nToken saved to: {watcher.token_path}")
    print("\nYou can now add events to Google Calendar!")
    print("\nNext steps:")
    print("1. Run: python scripts/add_calendar_event.py")
    print("2. Or restart the orchestrator to auto-add events from Inbox")
    print("\n" + "="*70 + "\n")

except Exception as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you clicked 'Allow' in the browser")
    print("2. Check that the calendar_credentials.json file exists")
    print("3. Try running this script again")
    print("\n" + "="*70 + "\n")
    sys.exit(1)
