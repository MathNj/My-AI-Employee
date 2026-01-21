#!/usr/bin/env python3
"""
Gmail Watcher for Personal AI Employee

Monitors Gmail inbox for new unread important emails and creates
task files in Needs_Action folder.

Based on the architecture from Requirements.md
Requires Gmail API credentials setup.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
from datetime import datetime, timedelta
import logging
import time
import json
import sys
import os
import pickle


# Configuration
VAULT_PATH = Path(__file__).parent.parent  # Root of the vault
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"
CREDENTIALS_DIR = Path(__file__).parent / "credentials"

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Check interval (in seconds)
CHECK_INTERVAL = 120  # 2 minutes

# How many days back to check for emails (prevents processing old unread emails)
DAYS_BACK_TO_CHECK = 1  # Only check emails from last 24 hours

# Setup logging
LOGS_PATH.mkdir(exist_ok=True)
log_file = LOGS_PATH / f'gmail_watcher_{datetime.now().strftime("%Y-%m-%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GmailWatcher:
    """
    Gmail watcher that monitors inbox for new important emails.

    Uses Gmail API to check for unread important messages and creates
    task files in Needs_Action folder.
    """

    def __init__(self, vault_path: str, credentials_path: str = None):
        """
        Initialize Gmail watcher.

        Args:
            vault_path: Path to the vault root
            credentials_path: Path to Gmail API credentials file
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_path = self.vault_path / 'Logs'

        # Ensure directories exist
        self.needs_action.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

        # Track processed message IDs to avoid duplicates
        self.processed_ids = self.load_processed_ids()

        # Credentials
        self.credentials_path = credentials_path or (CREDENTIALS_DIR / 'credentials.json')
        self.token_path = CREDENTIALS_DIR / 'token.pickle'

        # Gmail service
        self.service = None

        logger.info("Gmail Watcher initialized")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Output to: {self.needs_action}")

    def load_processed_ids(self):
        """Load previously processed message IDs from file."""
        processed_file = self.logs_path / 'gmail_processed_ids.json'
        if processed_file.exists():
            try:
                data = json.loads(processed_file.read_text())
                logger.info(f"Loaded {len(data)} processed message IDs")
                return set(data)
            except Exception as e:
                logger.error(f"Error loading processed IDs: {e}")
                return set()
        return set()

    def save_processed_ids(self):
        """Save processed message IDs to file."""
        processed_file = self.logs_path / 'gmail_processed_ids.json'
        try:
            processed_file.write_text(json.dumps(list(self.processed_ids)))
        except Exception as e:
            logger.error(f"Error saving processed IDs: {e}")

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2.

        Returns:
            True if authentication successful, False otherwise
        """
        creds = None

        # Load token from file if it exists
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    creds = None

            if not creds:
                if not self.credentials_path.exists():
                    logger.error(f"Credentials file not found: {self.credentials_path}")
                    logger.error("Please set up Gmail API credentials first.")
                    logger.error("See watchers/GMAIL_SETUP.md for instructions.")
                    return False

                try:
                    logger.info("Starting OAuth2 flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"OAuth2 flow failed: {e}")
                    return False

            # Save credentials for next run
            CREDENTIALS_DIR.mkdir(exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("Credentials saved")

        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("[OK] Gmail API authenticated successfully")
            return True
        except Exception as e:
            logger.error(f"Error building Gmail service: {e}")
            return False

    def check_for_updates(self):
        """
        Check Gmail for new unread important messages.

        Returns:
            List of new message objects
        """
        try:
            # Calculate date cutoff (only check recent emails)
            cutoff_date = datetime.now() - timedelta(days=DAYS_BACK_TO_CHECK)
            date_filter = cutoff_date.strftime('%Y/%m/%d')

            # Query for unread important emails from the last N days
            query = f'is:unread is:important after:{date_filter}'
            logger.debug(f"Gmail query: {query}")

            results = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed messages
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]

            if new_messages:
                logger.info(f"Found {len(new_messages)} new important email(s)")
            else:
                logger.debug("No new important emails")

            return new_messages

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return []

    def create_action_file(self, message):
        """
        Create a task file in Needs_Action for the email.

        Args:
            message: Gmail message object

        Returns:
            Path to created task file or None if error
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}

            # Get email details
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', 'Unknown')
            snippet = msg.get('snippet', '')

            # Determine priority based on subject
            priority = self.determine_priority(subject, from_email)

            # Create task file
            timestamp = datetime.now().isoformat()
            task_filename = f"EMAIL_{message['id']}.md"
            task_path = self.needs_action / task_filename

            task_content = f"""---
type: email
message_id: {message['id']}
from: {from_email}
subject: {subject}
received: {timestamp}
email_date: {date}
priority: {priority}
status: pending
---

# New Email: {subject}

## Email Information
- **From:** {from_email}
- **Subject:** {subject}
- **Date:** {date}
- **Received:** {timestamp}
- **Priority:** {priority}

## Email Preview
{snippet}

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Add to calendar if needed

## Processing Notes
Add notes here about actions taken on this email.

## Gmail Link
https://mail.google.com/mail/u/0/#inbox/{message['id']}

---

*Task created by Gmail Watcher*
*Timestamp: {timestamp}*
"""

            # Write task file
            task_path.write_text(task_content, encoding='utf-8')

            # Mark as processed
            self.processed_ids.add(message['id'])
            self.save_processed_ids()

            # Log the action
            self.log_action(from_email, subject, task_filename)

            logger.info(f"[OK] Created task for email from: {from_email}")
            return task_path

        except Exception as e:
            logger.error(f"Error creating action file for message {message['id']}: {e}")
            return None

    def determine_priority(self, subject: str, from_email: str) -> str:
        """
        Determine email priority based on subject and sender.

        Args:
            subject: Email subject line
            from_email: Sender email address

        Returns:
            Priority level (high, medium, low)
        """
        subject_lower = subject.lower()

        # High priority keywords
        high_priority_keywords = [
            'urgent', 'asap', 'critical', 'important', 'emergency',
            'invoice', 'payment', 'overdue', 'deadline', 'action required'
        ]

        if any(keyword in subject_lower for keyword in high_priority_keywords):
            return 'high'

        # Medium priority for client/business emails
        business_indicators = ['re:', 'fwd:', 'meeting', 'schedule', 'proposal']
        if any(indicator in subject_lower for indicator in business_indicators):
            return 'medium'

        # Default priority
        return 'medium'

    def log_action(self, from_email: str, subject: str, task_filename: str):
        """
        Log the email detection to the actions log.

        Args:
            from_email: Sender email
            subject: Email subject
            task_filename: Created task file name
        """
        log_date = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_path / f'actions_{log_date}.json'

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "email_detected",
            "details": {
                "from": from_email,
                "subject": subject,
                "task_created": task_filename,
                "watcher": "gmail_watcher"
            }
        }

        try:
            # Read existing logs or create new list
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            else:
                logs = []

            # Append new entry
            logs.append(log_entry)

            # Write back
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error(f"Error writing to action log: {e}")

    def run(self):
        """
        Main monitoring loop.
        """
        logger.info("=" * 60)
        logger.info("Gmail Watcher started")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds ({CHECK_INTERVAL // 60} minutes)")
        logger.info("Monitoring for: unread important emails")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        try:
            while True:
                # Check for new emails
                new_messages = self.check_for_updates()

                # Create task for each new message
                for message in new_messages:
                    self.create_action_file(message)

                # Wait before next check
                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Stopping Gmail watcher...")
            logger.info(f"Total emails processed: {len(self.processed_ids)}")
            logger.info("[OK] Gmail watcher stopped successfully")
            logger.info("=" * 60)
            sys.exit(0)
        except Exception as e:
            logger.error(f"Gmail watcher error: {e}")
            sys.exit(1)


def main():
    """
    Main entry point for Gmail watcher.
    """
    # Check for credentials path argument
    credentials_path = None
    if len(sys.argv) > 1:
        credentials_path = sys.argv[1]

    # Create watcher
    watcher = GmailWatcher(VAULT_PATH, credentials_path)

    # Authenticate
    if not watcher.authenticate():
        logger.error("Authentication failed. Exiting.")
        sys.exit(1)

    # Start monitoring
    watcher.run()


if __name__ == "__main__":
    main()
