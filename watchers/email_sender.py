#!/usr/bin/env python3
"""
Email Sender - Sends emails using Gmail API

Integrates with approval workflow to send approved emails.
Uses OAuth 2.0 authentication (same as Gmail watcher).
"""

import sys
import io
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import logging
import json

# UTF-8 support for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import googleapiclient.http
except ImportError as e:
    print(f"ERROR: Missing required libraries: {e}")
    print("Install: pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails using Gmail API"""

    def __init__(self, credentials_path: str, token_path: str):
        """
        Initialize Gmail API client with OAuth 2.0

        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to OAuth token JSON
        """
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth 2.0

        Returns:
            True if successful, False otherwise
        """
        try:
            creds = None

            # Load existing token if available
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    'token',
                    ['https://www.googleapis.com/auth/gmail.send']
                )

            # If no valid credentials, flow would need to run
            # For now, we'll use the same credentials as Gmail watcher
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    logger.error("No valid Gmail credentials found")
                    logger.error("Please run Gmail watcher authentication first")
                    return False

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API authenticated successfully")
            return True

        except Exception as e:
            logger.error(f"Gmail API authentication failed: {e}")
            return False

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: str = None,
        html: bool = False
    ) -> dict:
        """
        Send an email using Gmail API

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            thread_id: Optional thread ID to reply to
            html: Whether body is HTML (default: False)

        Returns:
            Dict with success status and message ID
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {
                        'success': False,
                        'error': 'Gmail API not authenticated'
                    }

            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to
            message['Subject'] = subject

            # Add body
            if html:
                part = MIMEText(body, 'html')
            else:
                part = MIMEText(body, 'plain')
            message.attach(part)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send via Gmail API
            send_kwargs = {'userId': 'me', 'body': {'raw': raw_message}}
            if thread_id:
                send_kwargs['body']['threadId'] = thread_id

            result = self.service.users().messages().send(**send_kwargs).execute()

            logger.info(f"Email sent successfully to {to}")
            logger.info(f"  Message ID: {result.get('id')}")
            logger.info(f"  Thread ID: {result.get('threadId')}")

            return {
                'success': True,
                'message_id': result.get('id'),
                'thread_id': result.get('threadId')
            }

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: str = None
    ) -> dict:
        """
        Create an email draft in Gmail

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            thread_id: Optional thread ID to reply to

        Returns:
            Dict with success status and draft ID
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {
                        'success': False,
                        'error': 'Gmail API not authenticated'
                    }

            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to
            message['Subject'] = subject

            # Add body
            part = MIMEText(body, 'plain')
            message.attach(part)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Create draft
            draft_kwargs = {'userId': 'me', 'body': {'message': {'raw': raw_message}}}
            if thread_id:
                draft_kwargs['body']['threadId'] = thread_id

            result = self.service.users().drafts().create(**draft_kwargs).execute()

            logger.info(f"Draft created successfully for {to}")
            logger.info(f"  Draft ID: {result.get('id')}")

            return {
                'success': True,
                'draft_id': result.get('id'),
                'message': 'Draft created'
            }

        except Exception as e:
            logger.error(f"Failed to create draft: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Test email sending"""
    import argparse

    parser = argparse.ArgumentParser(description='Send email via Gmail API')
    parser.add_argument('--to', required=True, help='Recipient email')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', required=True, help='Email body')
    parser.add_argument('--html', action='store_true', help='Send as HTML')

    args = parser.parse_args()

    # Setup paths
    vault_path = Path(__file__).parent.parent
    creds_path = vault_path / 'watchers' / 'credentials' / 'credentials.json'
    token_path = vault_path / 'watchers' / 'credentials' / 'token.json'

    # Create sender
    sender = EmailSender(str(creds_path), str(token_path))

    # Send email
    result = sender.send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        html=args.html
    )

    if result['success']:
        print(f"✓ Email sent successfully!")
        print(f"  Message ID: {result['message_id']}")
    else:
        print(f"✗ Failed to send email: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
