#!/usr/bin/env python3
"""
Test calendar watcher two-way sync - process Inbox events
"""
import sys
sys.path.insert(0, '/c/Users/Najma-LP/Desktop/AI_Employee_Vault/watchers')

from pathlib import Path
from datetime import datetime, timedelta

# Import and instantiate calendar watcher
from calendar_watcher import CalendarWatcher

# Create watcher instance
vault_path = Path('/c/Users/Najma-LP/Desktop/A_Employee_Vault')
watcher = CalendarWatcher(
    vault_path=str(vault_path),
    check_interval=300,
    hours_ahead=48,
    min_hours_ahead=1
)

print("="*70)
print("Testing Two-Way Calendar Sync")
print("="*70)
print("\n1. Checking Inbox for calendar events to add...")

# Check Inbox and add events to Google Calendar
added_count = watcher.check_for_events_in_inbox()

print(f"\n✓ Processed {added_count} calendar event(s) from Inbox")

if added_count > 0:
    print("\nEvent(s) added to Google Calendar successfully!")
    print("Check your Google Calendar at: https://calendar.google.com")
else:
    print("\nNo events were added. This could be because:")
    print("1. Calendar watcher needs to re-authenticate (old read-only token)")
    print("2. Event file format doesn't match expected format")
    print("3. Authentication failed")

print("\n" + "="*70)
