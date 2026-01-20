#!/usr/bin/env python3
"""
Lightweight Gmail watcher for Oracle Cloud VM (1GB RAM constrained)
Only monitors and creates draft task files - no sending
Optimized for minimal resource usage

Usage:
    python3 watchers/cloud_email_watcher.py <vault_path> <credentials_path>
"""
import time
import sys
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CloudEmailWatcher:
    """Minimal Gmail watcher for resource-constrained cloud VM"""

    def __init__(self, vault_path: str, credentials_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action' / 'email'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Load credentials (should be read-only scope)
        try:
            self.creds = Credentials.from_authorized_user_file(credentials_path)
            self.service = build('gmail', 'v1', credentials=self.creds)
            self.processed_ids = set()
        except Exception as e:
            print(f"Error loading credentials: {e}")
            sys.exit(1)

    def check_for_updates(self):
        """Check for new important emails (limited to reduce memory)"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important OR is:unread from:*@gmail.com',  # Broad query
                maxResults=5  # Limit to 5 to reduce memory
            ).execute()
            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
        except HttpError as e:
            print(f"Gmail API error: {e}")
            return []
        except Exception as e:
            print(f"Error checking emails: {e}")
            return []

    def create_action_file(self, message):
        """Create minimal task file for email"""
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='metadata'  # Use metadata to save bandwidth and memory
            ).execute()

            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}

            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            timestamp = datetime.now().isoformat()

            # Create minimal task file
            filename = f"EMAIL_{message['id'][:8]}_{timestamp[:10].replace('-', '')}.md"
            filepath = self.needs_action / filename

            content = f"""---
type: email
from: {from_email}
subject: {subject}
received: {timestamp}
priority: high
status: pending_approval
zone: cloud
---

# Email From Cloud Watcher

**From:** {from_email}
**Subject:** {subject}
**Received:** {timestamp}
**Message ID:** {message['id']}

## Cloud Detection
This email was detected by the cloud zone Gmail watcher.

## Suggested Action
- [ ] Review email content
- [ ] If action needed, move to /Approved/email/ to trigger response
- [ ] If no action needed, move to /Rejected/email/

## Cloud Analysis
Priority: High (unread + important)
Requires: Local zone review and approval
"""

            filepath.write_text(content)
            self.processed_ids.add(message['id'])
            print(f"[{timestamp[:19]}] Created task: {filename}")
            return filepath

        except Exception as e:
            print(f"Error creating action file: {e}")
            return None

    def run(self):
        """Main loop (optimized for low memory - check every 10 minutes)"""
        print("=" * 60)
        print("Cloud Email Watcher Started")
        print(f"Vault: {self.vault_path}")
        print(f"Output: {self.needs_action}")
        print("Check interval: 10 minutes (600s)")
        print("Mode: DRAFT ONLY (no sending)")
        print("=" * 60)

        while True:
            try:
                messages = self.check_for_updates()
                if messages:
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found {len(messages)} new emails")

                    for msg in messages:
                        self.create_action_file(msg)
                        # Small delay between processing to avoid memory spikes
                        time.sleep(1)
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No new emails")

            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")

            # Check every 10 minutes (600 seconds) - reduced from 5 to save resources
            try:
                time.sleep(600)
            except KeyboardInterrupt:
                print("\nShutting down...")
                break

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 cloud_email_watcher.py <vault_path> <credentials_path>")
        sys.exit(1)

    vault_path = sys.argv[1]
    credentials_path = sys.argv[2]

    watcher = CloudEmailWatcher(vault_path, credentials_path)
    watcher.run()
