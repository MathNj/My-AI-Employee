#!/usr/bin/env python3
"""
Approval Processor - Processes approved actions from Approved folder
Monitors folder, executes approved actions, moves to Done
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import traceback
import subprocess

# Fix encoding for Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Import email sender for Gmail integration
try:
    from email_sender import EmailSender
    EMAIL_SENDER_AVAILABLE = True
except ImportError:
    EMAIL_SENDER_AVAILABLE = False
    logging.warning("Email sender not available - emails will require manual sending")

# Import WhatsApp sender
WHATSAPP_SENDER_AVAILABLE = False
try:
    whatsapp_mcp_path = Path(__file__).parent.parent / 'mcp-servers' / 'whatsapp-mcp'
    if whatsapp_mcp_path.exists():
        sys.path.insert(0, str(whatsapp_mcp_path))
        from whatsapp_sender import WhatsAppSender
        WHATSAPP_SENDER_AVAILABLE = True
        logging.info("WhatsApp sender imported successfully")
    else:
        logging.warning(f"WhatsApp MCP server not found at {whatsapp_mcp_path}")
except ImportError as e:
    logging.warning(f"WhatsApp sender import failed: {e}")
    WHATSAPP_SENDER_AVAILABLE = False
except Exception as e:
    logging.warning(f"WhatsApp sender initialization error: {e}")
    WHATSAPP_SENDER_AVAILABLE = False

# Configuration
VAULT_PATH = Path(__file__).parent.parent
APPROVED_PATH = VAULT_PATH / "Approved"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
DONE_PATH = VAULT_PATH / "Done"
FAILED_PATH = VAULT_PATH / "Failed"
LOGS_PATH = VAULT_PATH / "Logs"

# Setup logging
LOGS_PATH.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ApprovalProcessor - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / 'approval_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ApprovalProcessor:
    """Process approved actions with email sending support"""

    def __init__(self):
        self.approved = APPROVED_PATH
        self.pending = PENDING_APPROVAL_PATH
        self.done = DONE_PATH
        self.failed = FAILED_PATH

        # Ensure directories exist
        self.approved.mkdir(exist_ok=True)
        self.pending.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)
        self.failed.mkdir(exist_ok=True)

        # Initialize email sender if available
        self.email_sender = None
        if EMAIL_SENDER_AVAILABLE:
            vault_path = Path(__file__).parent.parent
            creds_path = vault_path / 'watchers' / 'credentials' / 'credentials.json'
            token_path = vault_path / 'watchers' / 'credentials' / 'token.json'

            if creds_path.exists():
                self.email_sender = EmailSender(str(creds_path), str(token_path))
                logger.info("Email sender initialized")
            else:
                logger.warning("Gmail credentials not found - emails will require manual sending")
        else:
            logger.info("Email sender not available - emails will require manual sending")

        # Initialize WhatsApp sender if available
        self.whatsapp_sender = None
        if WHATSAPP_SENDER_AVAILABLE:
            try:
                self.whatsapp_sender = WhatsAppSender(
                    session_path=None,  # Use default (same as watcher)
                    headless=True  # Run in headless mode
                )
                logger.info("WhatsApp sender initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize WhatsApp sender: {e}")
        else:
            logger.info("WhatsApp sender not available - WhatsApp messages will require manual sending")

        logger.info("ApprovalProcessor initialized")
        logger.info(f"  Monitoring: {self.approved}")
        logger.info(f"  Done: {self.done}")

    def get_approved_actions(self):
        """Get all approved action files including subdirectories"""
        try:
            # Get all .md files in root
            action_files = list(self.approved.glob('*.md'))

            # Get all .md files in subdirectories recursively
            action_files.extend(self.approved.rglob('*.md'))

            # Remove duplicates and sort
            action_files = list(set(action_files))
            action_files.sort(key=lambda x: x.stat().st_mtime)

            return action_files
        except Exception as e:
            logger.error(f"Error reading approved actions: {e}")
            return []

    def parse_action_metadata(self, action_file):
        """Parse action metadata from file"""
        try:
            content = action_file.read_text(encoding='utf-8')

            # Parse frontmatter
            metadata = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = parts[1].strip()
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"')

            return metadata, content

        except Exception as e:
            logger.error(f"Error parsing {action_file.name}: {e}")
            return {}, ""

    def execute_action(self, action_file, metadata, content):
        """Execute approved action"""
        action_type = metadata.get('type', 'unknown')
        action = metadata.get('action', '')

        logger.info(f"Executing {action_type}: {action}")

        try:
            if action_type == 'email':
                return self.execute_email(action_file, metadata, content)
            elif action_type == 'whatsapp':
                return self.execute_whatsapp(action_file, metadata, content)
            elif action_type in ['linkedin_post', 'x_post', 'facebook_post', 'instagram_post']:
                return self.execute_social_post(action_file, metadata, action_type)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                # Move to Done anyway (approved)
                self.move_to_done(action_file)
                return True

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            traceback.print_exc()
            self.move_to_failed(action_file)
            return False

    def execute_email(self, action_file, metadata, content):
        """
        Execute email action using Gmail API

        Reads email content from the approved action file and sends it.
        """
        to = metadata.get('to', metadata.get('recipient', ''))
        subject = metadata.get('subject', '')
        message_id = metadata.get('message_id', '')

        # Extract email body from content (after frontmatter)
        # Look for ## Email Reply or similar section
        body_lines = []
        in_reply_section = False
        for line in content.split('\n'):
            if line.startswith('## Email Reply') or line.startswith('## Reply'):
                in_reply_section = True
                continue
            if in_reply_section and (line.startswith('#') or line.startswith('---')):
                break
            if in_reply_section:
                body_lines.append(line)

        body = '\n'.join(body_lines).strip()

        # If no reply section, use entire content after frontmatter
        if not body:
            # Find content after frontmatter ends
            parts = content.split('---', 2)
            if len(parts) > 1:
                body = parts[1].strip()
            else:
                body = content

        logger.info(f"  Email to: {to}")
        logger.info(f"  Subject: {subject}")

        # Try to send via Gmail API
        if self.email_sender and to and subject:
            logger.info("  Attempting to send via Gmail API...")

            result = self.email_sender.send_email(
                to=to,
                subject=subject,
                body=body,
                thread_id=message_id if message_id != 'unknown' else None
            )

            if result['success']:
                self.move_to_done(action_file, note=f"Email sent successfully via Gmail API. Message ID: {result.get('message_id')}")
                logger.info(f"  [OK] Email sent successfully!")
                return True
            else:
                logger.error(f"  Failed to send email: {result.get('error')}")
                logger.info("  Moving to Done with note for manual sending")
                self.move_to_done(action_file, note=f"Email sending failed: {result.get('error')}\nPlease send manually:\nTo: {to}\nSubject: {subject}\n\n{body}")
                return False
        else:
            logger.info("  Email sender not available - requires manual sending")
            self.move_to_done(action_file, note="Email requires manual sending via Gmail\n\nPlease send:\nTo: {to}\nSubject: {subject}\n\n{body}")
            return True

    def execute_whatsapp(self, action_file, metadata, content):
        """
        Execute WhatsApp message action

        Reads WhatsApp message content from the approved action file and sends it.
        """
        to = metadata.get('to', metadata.get('recipient', ''))
        message_id = metadata.get('message_id', '')

        # Extract message body from content (after frontmatter)
        # Look for ## Message or similar section
        body_lines = []
        in_message_section = False
        for line in content.split('\n'):
            if line.startswith('## Message') or line.startswith('## WhatsApp Message'):
                in_message_section = True
                continue
            if in_message_section and (line.startswith('#') or line.startswith('---')):
                break
            if in_message_section:
                body_lines.append(line)

        message = '\n'.join(body_lines).strip()

        # If no message section, use entire content after frontmatter
        if not message:
            # Find content after frontmatter ends
            parts = content.split('---', 2)
            if len(parts) > 1:
                message = parts[1].strip()
            else:
                message = content

        logger.info(f"  WhatsApp to: {to}")
        logger.info(f"  Message length: {len(message)} chars")

        # Try to send via WhatsApp sender
        if self.whatsapp_sender and to and message:
            logger.info("  Attempting to send via WhatsApp sender...")

            result = self.whatsapp_sender.send_message(
                to=to,
                message=message
            )

            if result['success']:
                self.move_to_done(action_file, note=f"WhatsApp message sent successfully via Playwright automation.\nRecipient: {result.get('recipient')}\nTimestamp: {result.get('timestamp')}")
                logger.info(f"  [OK] WhatsApp message sent successfully!")
                return True
            else:
                logger.error(f"  Failed to send WhatsApp message: {result.get('error')}")
                logger.info("  Moving to Done with note for manual sending")
                self.move_to_done(action_file, note=f"WhatsApp sending failed: {result.get('error')}\n\nPlease send manually:\nTo: {to}\n\n{message}")
                return False
        else:
            logger.info("  WhatsApp sender not available - requires manual sending")
            self.move_to_done(action_file, note=f"WhatsApp message requires manual sending\n\nPlease send:\nTo: {to}\n\n{message}")
            return True

    def execute_social_post(self, action_file, metadata, platform):
        """Execute social media post (log only - already posted)"""
        logger.info(f"  {platform} post - already published")
        self.move_to_done(action_file)
        return True

    def move_to_done(self, action_file, note=""):
        """Move action file to Done, preserving subdirectory structure"""
        try:
            # Preserve subdirectory structure
            relative_path = action_file.relative_to(self.approved)
            done_file = self.done / relative_path

            # Create parent directory if needed
            done_file.parent.mkdir(parents=True, exist_ok=True)

            # Add completion note if needed
            if note:
                content = action_file.read_text(encoding='utf-8')
                content += f"\n\n---\n**Completed:** {datetime.now().isoformat()}\n**Note:** {note}\n"
                done_file.write_text(content, encoding='utf-8')
                action_file.unlink()
            else:
                action_file.rename(done_file)

            logger.info(f"  Moved to Done: {relative_path}")
            return True

        except Exception as e:
            logger.error(f"Error moving to Done: {e}")
            return False

    def move_to_failed(self, action_file):
        """Move action file to Failed, preserving subdirectory structure"""
        try:
            # Preserve subdirectory structure
            relative_path = action_file.relative_to(self.approved)
            failed_file = self.failed / relative_path

            # Create parent directory if needed
            failed_file.parent.mkdir(parents=True, exist_ok=True)

            action_file.rename(failed_file)
            logger.info(f"  Moved to Failed: {relative_path}")
        except Exception as e:
            logger.error(f"Error moving to Failed: {e}")

    def run_once(self):
        """Run one processing cycle"""
        logger.info("Checking for approved actions...")

        actions = self.get_approved_actions()

        if not actions:
            logger.info("No approved actions found")
            return

        logger.info(f"Found {len(actions)} approved action(s)")

        processed = 0
        for action_file in actions:
            metadata, content = self.parse_action_metadata(action_file)

            if self.execute_action(action_file, metadata, content):
                processed += 1

        logger.info(f"Processed {processed}/{len(actions)} actions")

    def run(self, interval=30):
        """Run continuously"""
        logger.info("ApprovalProcessor started")
        logger.info(f"Check interval: {interval} seconds")

        try:
            while True:
                self.run_once()
                logger.info(f"Waiting {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("ApprovalProcessor stopped by user")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Approval Processor')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')

    args = parser.parse_args()

    processor = ApprovalProcessor()

    if args.once:
        processor.run_once()
    else:
        processor.run(args.interval)


if __name__ == "__main__":
    main()
