#!/usr/bin/env python3
"""
Add calendar event to Google Calendar
"""
import sys
sys.path.insert(0, '/c/Users/Najma-LP/Desktop/AI_Employee_Vault/watchers')

from pathlib import Path
from datetime import datetime, timedelta
from calendar_watcher import CalendarWatcher

# Create watcher instance
vault_path = Path('/c/Users/Najma-LP/Desktop/AI_Employee_Vault')
watcher = CalendarWatcher(
    vault_path=str(vault_path),
    check_interval=300,
    hours_ahead=48,
    min_hours_ahead=1
)

print("="*70)
print("Adding Calendar Event to Google Calendar")
print("="*70)

# Event details
title = "Social Media Campaign Review"
date = "2026-01-20"
time = "10:00"
duration = 60  # minutes

# Parse date and time
date_parts = date.split('-')
year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
time_parts = time.split(':')
hour, minute = int(time_parts[0]), int(time_parts[1])

start_datetime = datetime(year, month, day, hour, minute)
end_datetime = start_datetime + timedelta(minutes=duration)

description = """Review AI Employee v1.0 social media campaign engagement metrics

Platforms:
• LinkedIn: Full announcement post
• X/Twitter: Optimized tweet (278 chars)
• Facebook: Complete announcement
• Instagram: Custom image + caption

Metrics to track:
- Likes and reactions
- Comments and engagement
- Shares and retweets
- Profile views and follows
- Overall reach and impressions

Action Items:
- Check each platform for engagement
- Respond to comments and messages
- Document metrics in Dashboard.md
- Identify top performing content
- Plan follow-up content

Location: Desk with computer access"""

location = "Desk with computer access"

print(f"\nEvent: {title}")
print(f"Date: {date}")
print(f"Time: {time}")
print(f"Duration: {duration} minutes")
print(f"Start: {start_datetime.strftime('%Y-%m-%d %H:%M')}")
print(f"End: {end_datetime.strftime('%Y-%m-%d %H:%M')}")

# Add event
print("\nAdding to Google Calendar...")
event_id = watcher.add_event_to_calendar(
    title=title,
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    description=description,
    location=location,
    reminders=True
)

if event_id:
    print(f"\n✅ SUCCESS! Event added to Google Calendar")
    print(f"   Event ID: {event_id}")
    print(f"   View: https://calendar.google.com")
    print("\nEvent Details:")
    print(f"   📅 Date: January 20, 2026 (Tomorrow)")
    print(f"   ⏰ Time: 10:00 AM - 11:00 AM")
    print(f"   📊 Review: LinkedIn, X/Twitter, Facebook, Instagram")

    # Move the calendar event file from Inbox to Plans
    inbox_file = vault_path / "Inbox" / "calendar_event_social_media_review_20260120.txt"
    if inbox_file.exists():
        plans_path = vault_path / "Plans"
        plans_path.mkdir(exist_ok=True)
        target = plans_path / inbox_file.name
        inbox_file.rename(target)
        print(f"\n✓ Moved calendar file to Plans folder")
else:
    print("\n❌ Failed to add event. This could be due to:")
    print("   1. Old token needs to be refreshed")
    print("   2. Re-authentication required (check for browser popup)")
    print("   3. Insufficient permissions")
    print("\nPlease add manually at: https://calendar.google.com")

print("\n" + "="*70)
