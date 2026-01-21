#!/usr/bin/env python3
"""
Google Calendar Watcher for Personal AI Employee

Monitors Google Calendar for upcoming events in the next 24-48 hours
and creates actionable task files in Needs_Action folder.

Uses Google Calendar API v3 with OAuth 2.0 authentication.
Follows the BaseWatcher pattern for consistency with other watchers.

Author: Personal AI Employee Project
Created: 2026-01-14
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pickle
import sys
import os

# Add parent directory to path to import BaseWatcher
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


# Google Calendar API scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events.readonly'
]

# Default configuration
DEFAULT_CHECK_INTERVAL = 300  # 5 minutes
DEFAULT_HOURS_AHEAD = 48  # Look 48 hours ahead for upcoming events
DEFAULT_MIN_HOURS_AHEAD = 1  # Minimum 1 hour ahead (don't notify for events starting immediately)


class CalendarWatcher(BaseWatcher):
    """
    Google Calendar watcher that monitors for upcoming events.

    Creates task files in Needs_Action folder for events approaching
    in the next 24-48 hours to give the AI Employee time to prepare.
    """

    def __init__(
        self,
        vault_path: str,
        credentials_path: Optional[str] = None,
        check_interval: int = DEFAULT_CHECK_INTERVAL,
        hours_ahead: int = DEFAULT_HOURS_AHEAD,
        min_hours_ahead: int = DEFAULT_MIN_HOURS_AHEAD,
        calendar_ids: Optional[List[str]] = None
    ):
        """
        Initialize Google Calendar watcher.

        Args:
            vault_path: Absolute path to the Obsidian vault root
            credentials_path: Path to Google Calendar API credentials file
            check_interval: Time in seconds between checks (default: 300)
            hours_ahead: How many hours ahead to look for events (default: 48)
            min_hours_ahead: Minimum hours ahead to notify (default: 1)
            calendar_ids: List of calendar IDs to monitor (default: ['primary'])
        """
        # Initialize base watcher
        super().__init__(
            vault_path=vault_path,
            check_interval=check_interval,
            watcher_name='CalendarWatcher'
        )

        # Configuration
        self.hours_ahead = hours_ahead
        self.min_hours_ahead = min_hours_ahead
        self.calendar_ids = calendar_ids or ['primary']

        # Credentials setup
        self.credentials_dir = Path(__file__).parent / 'credentials'
        self.credentials_dir.mkdir(exist_ok=True)

        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            self.credentials_path = self.credentials_dir / 'calendar_credentials.json'

        self.token_path = self.credentials_dir / 'calendar_token.pickle'

        # Google Calendar service
        self.service = None

        # Authentication
        if not self._authenticate():
            raise RuntimeError("Failed to authenticate with Google Calendar API")

        self.logger.info(f"  Hours ahead: {self.hours_ahead}")
        self.logger.info(f"  Min hours ahead: {self.min_hours_ahead}")
        self.logger.info(f"  Monitoring calendars: {', '.join(self.calendar_ids)}")

    def _authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API using OAuth 2.0.

        Returns:
            True if authentication successful, False otherwise
        """
        creds = None

        # Load token from file if it exists
        if self.token_path.exists():
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                self.logger.info("Loaded existing credentials from token file")
            except Exception as e:
                self.logger.error(f"Error loading token file: {e}")

        # If no valid credentials, refresh or initiate OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    self.logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                    self.logger.info("Credentials refreshed successfully")
                except Exception as e:
                    self.logger.error(f"Error refreshing credentials: {e}")
                    creds = None

            # Run OAuth flow if needed
            if not creds:
                if not self.credentials_path.exists():
                    self.logger.error(f"Credentials file not found: {self.credentials_path}")
                    self.logger.error("Please set up Google Calendar API credentials first.")
                    self.logger.error("See watchers/CALENDAR_SETUP.md for instructions.")
                    return False

                try:
                    self.logger.info("Starting OAuth 2.0 flow...")
                    self.logger.info("Your browser will open for authentication...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                    self.logger.info("OAuth flow completed successfully")
                except Exception as e:
                    self.logger.error(f"OAuth 2.0 flow failed: {e}")
                    return False

            # Save credentials for next run
            try:
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                self.logger.info("Credentials saved to token file")
            except Exception as e:
                self.logger.error(f"Error saving credentials: {e}")

        # Build Google Calendar service
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            self.logger.info("[OK] Google Calendar API authenticated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error building Calendar service: {e}")
            return False

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Google Calendar for upcoming events.

        Returns:
            List of upcoming event dictionaries
        """
        if not self.service:
            self.logger.error("Calendar service not initialized")
            return []

        try:
            # Calculate time window
            now = datetime.utcnow()
            time_min = now + timedelta(hours=self.min_hours_ahead)
            time_max = now + timedelta(hours=self.hours_ahead)

            # Format as RFC3339 timestamp
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'

            self.logger.debug(f"Checking events from {time_min_str} to {time_max_str}")

            upcoming_events = []

            # Check each configured calendar
            for calendar_id in self.calendar_ids:
                try:
                    events_result = self.service.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min_str,
                        timeMax=time_max_str,
                        singleEvents=True,
                        orderBy='startTime',
                        maxResults=50  # Limit to 50 events per calendar
                    ).execute()

                    events = events_result.get('items', [])

                    # Filter out already processed events
                    for event in events:
                        event_id = event.get('id')
                        if event_id and not self.is_processed(event_id):
                            # Add calendar ID to event for reference
                            event['calendarId'] = calendar_id
                            upcoming_events.append(event)

                    self.logger.debug(f"Found {len(events)} events in calendar: {calendar_id}")

                except HttpError as e:
                    self.logger.error(f"HTTP error checking calendar {calendar_id}: {e}")
                except Exception as e:
                    self.logger.error(f"Error checking calendar {calendar_id}: {e}")

            if upcoming_events:
                self.logger.info(f"Found {len(upcoming_events)} new upcoming event(s)")
            else:
                self.logger.debug("No new upcoming events")

            return upcoming_events

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}", exc_info=True)
            return []

    def create_action_file(self, event: Dict[str, Any]) -> Optional[Path]:
        """
        Create a task file in Needs_Action folder for the event.

        Args:
            event: Google Calendar event dictionary

        Returns:
            Path to created task file or None if error
        """
        try:
            # Extract event details
            event_id = event.get('id', 'unknown')
            summary = event.get('summary', 'No Title')
            description = event.get('description', '')
            location = event.get('location', '')
            calendar_id = event.get('calendarId', 'primary')

            # Parse event times
            start = event.get('start', {})
            end = event.get('end', {})

            # Handle all-day events vs timed events
            if 'dateTime' in start:
                start_time = self._parse_datetime(start['dateTime'])
                end_time = self._parse_datetime(end['dateTime'])
                is_all_day = False
            else:
                start_time = self._parse_date(start.get('date', ''))
                end_time = self._parse_date(end.get('date', ''))
                is_all_day = True

            # Calculate time until event
            now = datetime.now()
            time_until = start_time - now
            hours_until = int(time_until.total_seconds() / 3600)

            # Determine priority based on time until event
            priority = self._determine_priority(hours_until, summary)

            # Get attendees
            attendees = event.get('attendees', [])
            attendee_list = [a.get('email', 'Unknown') for a in attendees]

            # Get event link
            event_link = event.get('htmlLink', '')

            # Format times for display
            if is_all_day:
                start_display = start_time.strftime('%Y-%m-%d (All Day)')
                end_display = end_time.strftime('%Y-%m-%d')
                duration = f"{(end_time - start_time).days} day(s)"
            else:
                start_display = start_time.strftime('%Y-%m-%d %H:%M')
                end_display = end_time.strftime('%Y-%m-%d %H:%M')
                duration_mins = int((end_time - start_time).total_seconds() / 60)
                duration = f"{duration_mins} minutes"

            # Create task filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_summary = self._sanitize_filename(summary)
            task_filename = f"CALENDAR_{event_id}_{timestamp}_{safe_summary}.md"
            task_path = self.needs_action / task_filename

            # Build task content
            task_content = f"""---
type: calendar_event
event_id: {event_id}
calendar_id: {calendar_id}
summary: {summary}
start_time: {start_time.isoformat()}
end_time: {end_time.isoformat()}
is_all_day: {is_all_day}
hours_until: {hours_until}
priority: {priority}
status: pending
created: {datetime.now().isoformat()}
---

# Upcoming Event: {summary}

## Event Details
- **Event:** {summary}
- **Start:** {start_display}
- **End:** {end_display}
- **Duration:** {duration}
- **Location:** {location if location else 'No location specified'}
- **Calendar:** {calendar_id}
- **Time Until Event:** {hours_until} hour(s)
- **Priority:** {priority}

## Description
{description if description else 'No description provided'}

## Attendees
"""

            # Add attendees
            if attendee_list:
                for attendee in attendee_list:
                    task_content += f"- {attendee}\n"
            else:
                task_content += "- No attendees listed\n"

            task_content += f"""

## Preparation Actions
- [ ] Review event details and agenda
- [ ] Prepare necessary materials or documents
- [ ] Check location and travel time (if applicable)
- [ ] Review attendee list and context
- [ ] Set reminders if needed
- [ ] Confirm attendance if required

## Pre-Event Research
- [ ] Research attendees' backgrounds
- [ ] Review previous communications
- [ ] Prepare questions or talking points
- [ ] Gather relevant reports or data

## Notes
Add preparation notes and context here.

## Links
- [View in Google Calendar]({event_link})

---

*Task created by Calendar Watcher*
*Created: {datetime.now().isoformat()}*
*Event ID: {event_id}*
"""

            # Write task file
            task_path.write_text(task_content, encoding='utf-8')

            # Mark as processed
            self.mark_as_processed(event_id)

            # Log the action
            self.log_action(
                action_type='calendar_event_detected',
                details={
                    'event_id': event_id,
                    'summary': summary,
                    'start_time': start_time.isoformat(),
                    'hours_until': hours_until,
                    'location': location,
                    'attendees_count': len(attendee_list),
                    'priority': priority
                },
                task_filename=task_filename
            )

            self.logger.info(f"[OK] Created task for event: {summary} (in {hours_until}h)")
            return task_path

        except Exception as e:
            self.logger.error(f"Error creating action file for event {event.get('id', 'unknown')}: {e}", exc_info=True)
            return None

    def _parse_datetime(self, dt_string: str) -> datetime:
        """
        Parse RFC3339 datetime string to datetime object.

        Args:
            dt_string: RFC3339 formatted datetime string

        Returns:
            datetime object
        """
        # Remove timezone info for simplicity (convert to local time conceptually)
        # Format: 2026-01-14T10:00:00-07:00
        try:
            if 'T' in dt_string:
                # Parse ISO format
                if dt_string.endswith('Z'):
                    return datetime.fromisoformat(dt_string[:-1])
                # Remove timezone offset
                if '+' in dt_string or dt_string.count('-') > 2:
                    dt_string = dt_string[:19]
                return datetime.fromisoformat(dt_string)
        except Exception as e:
            self.logger.error(f"Error parsing datetime {dt_string}: {e}")
            return datetime.now()

    def _parse_date(self, date_string: str) -> datetime:
        """
        Parse date string to datetime object (for all-day events).

        Args:
            date_string: Date string in YYYY-MM-DD format

        Returns:
            datetime object
        """
        try:
            return datetime.strptime(date_string, '%Y-%m-%d')
        except Exception as e:
            self.logger.error(f"Error parsing date {date_string}: {e}")
            return datetime.now()

    def _determine_priority(self, hours_until: int, summary: str) -> str:
        """
        Determine event priority based on time until event and content.

        Args:
            hours_until: Hours until event starts
            summary: Event title/summary

        Returns:
            Priority level (urgent, high, medium, low)
        """
        summary_lower = summary.lower()

        # Urgent keywords
        urgent_keywords = ['urgent', 'asap', 'critical', 'emergency', 'deadline']
        if any(keyword in summary_lower for keyword in urgent_keywords):
            return 'urgent'

        # High priority if event is soon
        if hours_until <= 3:
            return 'high'

        # High priority keywords
        high_keywords = [
            'meeting', 'interview', 'presentation', 'demo', 'call',
            'client', 'board', 'conference', 'review', 'deadline'
        ]
        if any(keyword in summary_lower for keyword in high_keywords):
            return 'high' if hours_until <= 12 else 'medium'

        # Medium priority for events within 24 hours
        if hours_until <= 24:
            return 'medium'

        # Low priority for events further out
        return 'low'

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Sanitize text for use in filename.

        Args:
            text: Text to sanitize
            max_length: Maximum length of sanitized text

        Returns:
            Sanitized filename-safe string
        """
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '_')

        # Replace spaces and multiple underscores
        text = '_'.join(text.split())
        text = '_'.join(filter(None, text.split('_')))

        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length]

        return text.strip('_')


def main():
    """
    Main entry point for Google Calendar watcher.
    """
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Google Calendar Watcher for Personal AI Employee'
    )
    parser.add_argument(
        '--vault-path',
        default=str(Path(__file__).parent.parent),
        help='Path to Obsidian vault (default: root directory)'
    )
    parser.add_argument(
        '--credentials',
        help='Path to Google Calendar API credentials JSON file'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=DEFAULT_CHECK_INTERVAL,
        help=f'Check interval in seconds (default: {DEFAULT_CHECK_INTERVAL})'
    )
    parser.add_argument(
        '--hours-ahead',
        type=int,
        default=DEFAULT_HOURS_AHEAD,
        help=f'Hours ahead to look for events (default: {DEFAULT_HOURS_AHEAD})'
    )
    parser.add_argument(
        '--min-hours-ahead',
        type=int,
        default=DEFAULT_MIN_HOURS_AHEAD,
        help=f'Minimum hours ahead to notify (default: {DEFAULT_MIN_HOURS_AHEAD})'
    )
    parser.add_argument(
        '--calendars',
        nargs='+',
        default=['primary'],
        help='Calendar IDs to monitor (default: primary)'
    )

    args = parser.parse_args()

    try:
        # Create watcher
        watcher = CalendarWatcher(
            vault_path=args.vault_path,
            credentials_path=args.credentials,
            check_interval=args.interval,
            hours_ahead=args.hours_ahead,
            min_hours_ahead=args.min_hours_ahead,
            calendar_ids=args.calendars
        )

        # Start monitoring
        watcher.run()

    except KeyboardInterrupt:
        print("\nWatcher stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
