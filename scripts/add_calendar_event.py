#!/usr/bin/env python3
"""
Add event to Google Calendar
"""
import sys
from datetime import datetime, timedelta

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import pickle
    from pathlib import Path
except ImportError:
    print("ERROR: Required libraries not installed")
    sys.exit(1)

def add_calendar_event():
    """Add event to Google Calendar"""

    # Load credentials
    token_path = Path(__file__).parent.parent / "watchers" / "credentials" / "calendar_token.pickle"

    if not token_path.exists():
        print(f"ERROR: Calendar token not found at {token_path}")
        return

    try:
        # Load credentials
        with open(token_path, 'rb') as f:
            credentials = pickle.load(f)

        # Build Calendar service
        service = build('calendar', 'v3', credentials=credentials)

        # Create event
        event = {
            'summary': 'Social Media Campaign Review',
            'location': 'Desk with computer access',
            'description': '''Review AI Employee v1.0 social media campaign engagement metrics

Platforms:
- LinkedIn: Full announcement post
- X/Twitter: Optimized tweet (278 chars)
- Facebook: Complete announcement
- Instagram: Custom image + caption

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
- Plan follow-up content''',
            'start': {
                'dateTime': '2026-01-20T10:00:00',
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': '2026-01-20T11:00:00',
                'timeZone': 'America/New_York',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }

        # Add event
        print("\n" + "="*70)
        print("Adding event to Google Calendar...")
        print("="*70 + "\n")

        event = service.events().insert(calendarId='primary', body=event).execute()

        print(f"✅ Event created successfully!")
        print(f"\nEvent ID: {event['id']}")
        print(f"Title: {event['summary']}")
        print(f"Start: 2026-01-20 at 10:00 AM")
        print(f"End: 2026-01-20 at 11:00 AM")
        print(f"\nView in Google Calendar:")
        print(f"https://calendar.google.com/calendar/r/eventedit?eid={event['id']}")

        print("\n" + "="*70)
        print("Event Details")
        print("="*70)
        print("\n📅 Social Media Campaign Review")
        print("   Date: January 20, 2026 (Tomorrow)")
        print("   Time: 10:00 AM - 11:00 AM")
        print("\n📊 Review Platforms:")
        print("   • LinkedIn - Full announcement")
        print("   • X/Twitter - Optimized tweet")
        print("   • Facebook - Complete announcement")
        print("   • Instagram - Image + caption")
        print("\n✅ Action Items:")
        print("   • Check engagement metrics")
        print("   • Respond to comments")
        print("   • Document in Dashboard.md")
        print("   • Plan follow-up content")
        print("\n" + "="*70 + "\n")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_calendar_event()
