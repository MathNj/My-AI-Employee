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
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

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
    """Process approved actions"""

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

        logger.info("ApprovalProcessor initialized")
        logger.info(f"  Monitoring: {self.approved}")
        logger.info(f"  Done: {self.done}")

    def get_approved_actions(self):
        """Get all approved action files"""
        try:
            action_files = list(self.approved.glob('*.md'))
            return sorted(action_files, key=lambda x: x.stat().st_mtime)
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
                return self.execute_email(action_file, metadata)
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

    def execute_email(self, action_file, metadata):
        """Execute email action (log only - requires SMTP/MCP)"""
        to = metadata.get('to', 'unknown')
        subject = metadata.get('subject', 'no subject')

        logger.info(f"  Email to: {to}")
        logger.info(f"  Subject: {subject}")
        logger.info(f"  Note: Email sending requires manual action or SMTP setup")

        # For now, just move to Done with note
        self.move_to_done(action_file, note="Email requires manual sending")
        return True

    def execute_social_post(self, action_file, metadata, platform):
        """Execute social media post (log only - already posted)"""
        logger.info(f"  {platform} post - already published")
        self.move_to_done(action_file)
        return True

    def move_to_done(self, action_file, note=""):
        """Move action file to Done"""
        try:
            done_file = self.done / action_file.name

            # Add completion note if needed
            if note:
                content = action_file.read_text(encoding='utf-8')
                content += f"\n\n---\n**Completed:** {datetime.now().isoformat()}\n**Note:** {note}\n"
                done_file.write_text(content, encoding='utf-8')
                action_file.unlink()
            else:
                action_file.rename(done_file)

            logger.info(f"  Moved to Done: {done_file.name}")
            return True

        except Exception as e:
            logger.error(f"Error moving to Done: {e}")
            return False

    def move_to_failed(self, action_file):
        """Move action file to Failed"""
        try:
            failed_file = self.failed / action_file.name
            action_file.rename(failed_file)
            logger.info(f"  Moved to Failed: {failed_file.name}")
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
