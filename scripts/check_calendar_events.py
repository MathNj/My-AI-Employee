#!/usr/bin/env python3
"""
Check Google Calendar for upcoming events
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google Calendar API not installed")
    print("Install: pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

def check_calendar_events():
    """Check and display Google Calendar events"""

    # Load credentials
    token_path = Path(__file__).parent.parent / "watchers" / "credentials" / "calendar_token.pickle"

    if not token_path.exists():
        print(f"ERROR: Calendar token not found at {token_path}")
        print("Please authenticate first")
        return

    try:
        # Load credentials from pickle file
        import pickle
        with open(token_path, 'rb') as f:
            credentials = pickle.load(f)

        # Build Calendar service
        service = build('calendar', 'v3', credentials=credentials)

        # Get current time and end of tomorrow
        now = datetime.utcnow()
        end_of_tomorrow = now.replace(hour=23, minute=59, second=59) + timedelta(days=1)

        # Fetch events
        print(f"\n{'='*70}")
        print(f"GOOGLE CALENDAR EVENTS")
        print(f"{'='*70}")
        print(f"Checking: {now.strftime('%Y-%m-%d %H:%M')} to {end_of_tomorrow.strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*70}\n")

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end_of_tomorrow.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print("No upcoming events found in your Google Calendar")
            print("\nTo add the 'Social Media Campaign Review' event:")
            print("1. Go to https://calendar.google.com")
            print("2. Click on January 20, 2026 at 10:00 AM")
            print("3. Create event: 'Social Media Campaign Review'")
            print("4. Set duration: 1 hour")
            print("5. Save")
        else:
            print(f"Found {len(events)} event(s):\n")

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                title = event.get('summary', 'No title')
                description = event.get('description', '')

                # Parse datetime
                try:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))

                    print(f"📅 {title}")
                    print(f"   Start: {start_dt.strftime('%Y-%m-%d %I:%M %p')}")
                    print(f"   End:   {end_dt.strftime('%Y-%m-%d %I:%M %p')}")

                    if description:
                        print(f"   Description: {description[:100]}...")

                    print()

                except:
                    print(f"📅 {title}")
                    print(f"   Time: {start} - {end}")
                    print()

        print(f"{'='*70}\n")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_calendar_events()
