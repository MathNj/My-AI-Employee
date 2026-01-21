#!/usr/bin/env python3
"""
Instagram Watcher - Monitors Instagram for business-related activity

Features:
- Monitors Instagram DMs (Direct Messages)
- Tracks comments on posts
- Keyword detection (urgent, inquiry, order, help, etc.)
- Creates action items in Needs_Action folder
- Email notifications for important activity

Requirements:
- Instagrapi (unofficial Instagram API)
- Instagram credentials (username/password)
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base_watcher import BaseWatcher

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, ChallengeRequired
    INSTAGRAM_AVAILABLE = True
except ImportError:
    INSTAGRAM_AVAILABLE = False
    print("[WARNING] instagrapi not installed. Install with: pip install instagrapi")


class InstagramWatcher(BaseWatcher):
    """
    Watches Instagram for business-related activity

    Monitors:
    - Direct Messages (DMs)
    - Comments on posts
    - Follower activity
    """

    def __init__(self, vault_path: str = None, output_path: str = None):
        super().__init__("instagram", vault_path, output_path)

        # Instagram configuration
        self.username = os.getenv('INSTAGRAM_USERNAME', '')
        self.password = os.getenv('INSTAGRAM_PASSWORD', '')
        self.session_file = os.getenv('INSTAGRAM_SESSION', './credentials/instagram_session.json')
        self.check_interval = int(os.getenv('INSTAGRAM_CHECK_INTERVAL', '180'))  # 3 minutes

        # Monitoring settings
        self.keywords = os.getenv('INSTAGRAM_KEYWORDS', 'urgent,inquiry,order,price,help,question,buy').split(',')
        self.monitored_posts = os.getenv('INSTAGRAM_MONITORED_POSTS', '').split(',')
        self.notification_enabled = os.getenv('INSTAGRAM_NOTIFICATION_ENABLED', 'true').lower() == 'true'
        self.notification_email = os.getenv('INSTAGRAM_NOTIFICATION_EMAIL', '')

        # State tracking
        self.seen_messages = set()
        self.seen_comments = set()
        self.last_check = None

        # Instagram client
        self.client = None

    def setup_client(self):
        """Initialize and authenticate Instagram client"""
        if not INSTAGRAM_AVAILABLE:
            self.logger.error("Instagrapi not available. Install with: pip install instagrapi")
            return False

        try:
            self.client = Client()

            # Load existing session if available
            if os.path.exists(self.session_file):
                try:
                    self.client.load_settings(self.session_file)
                    self.client.login(self.username, self.password)
                    self.logger.info("[OK] Loaded existing Instagram session")
                    return True
                except Exception as e:
                    self.logger.warning(f"Could not load session: {e}")

            # Fresh login
            if self.username and self.password:
                self.client.login(self.username, self.password)

                # Save session for future use
                os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
                self.client.dump_settings(self.session_file)

                self.logger.info("[OK] Instagram authentication successful")
                return True
            else:
                self.logger.error("Instagram credentials not found in .env")
                return False

        except ChallengeRequired as e:
            self.logger.error(f"Instagram challenge required: {e}")
            self.logger.error("Please login manually and complete the challenge")
            return False
        except LoginRequired as e:
            self.logger.error(f"Instagram login required: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Instagram authentication failed: {e}")
            return False

    def check_messages(self) -> List[Dict[str, Any]]:
        """Check for new DMs"""
        if not self.client:
            return []

        new_messages = []

        try:
            # Get threads
            threads = self.client.direct_threads(limit=20)

            for thread in threads:
                for message in thread.messages:
                    # Create unique ID
                    msg_id = f"msg_{message.id}"

                    # Skip if already seen
                    if msg_id in self.seen_messages:
                        continue

                    # Check if it's a text message
                    if hasattr(message, 'text') and message.text:
                        # Check for keywords
                        text_lower = message.text.lower()
                        has_keyword = any(kw.lower() in text_lower for kw in self.keywords)

                        if has_keyword:
                            new_messages.append({
                                'id': msg_id,
                                'type': 'dm',
                                'sender': thread.users[0].username if thread.users else 'Unknown',
                                'text': message.text,
                                'timestamp': datetime.fromtimestamp(message.timestamp).isoformat(),
                                'thread_id': thread.id,
                                'keyword_matched': [kw for kw in self.keywords if kw.lower() in text_lower]
                            })

                            self.seen_messages.add(msg_id)

        except Exception as e:
            self.logger.error(f"Error checking messages: {e}")

        return new_messages

    def check_comments(self) -> List[Dict[str, Any]]:
        """Check for new comments on monitored posts"""
        if not self.client or not self.monitored_posts:
            return []

        new_comments = []

        try:
            for post_id in self.monitored_posts:
                if not post_id.strip():
                    continue

                try:
                    comments = self.client.media_comments(post_id.strip(), limit=20)

                    for comment in comments:
                        # Create unique ID
                        comment_id = f"comment_{comment.pk}"

                        # Skip if already seen
                        if comment_id in self.seen_comments:
                            continue

                        # Check for keywords
                        text_lower = comment.text.lower()
                        has_keyword = any(kw.lower() in text_lower for kw in self.keywords)

                        if has_keyword:
                            new_comments.append({
                                'id': comment_id,
                                'type': 'comment',
                                'post_id': post_id,
                                'commenter': comment.user.username,
                                'text': comment.text,
                                'timestamp': datetime.fromtimestamp(comment.created_at).isoformat(),
                                'keyword_matched': [kw for kw in self.keywords if kw.lower() in text_lower]
                            })

                            self.seen_comments.add(comment_id)

                except Exception as e:
                    self.logger.warning(f"Error checking comments for post {post_id}: {e}")

        except Exception as e:
            self.logger.error(f"Error checking comments: {e}")

        return new_comments

    def create_action_item(self, activity: Dict[str, Any]):
        """Create action item in Needs_Action folder"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"INSTAGRAM_{activity['type'].upper()}_{timestamp}.md"
            filepath = os.path.join(self.output_path, filename)

            if activity['type'] == 'dm':
                content = f"""---
type: instagram_dm
source: instagram
priority: high
created: {datetime.now().isoformat()}
---

# Instagram DM Alert

**From:** @{activity['sender']}
**Time:** {activity['timestamp']}
**Thread ID:** {activity['thread_id']}

## Message

{activity['text']}

## Keywords Matched

{', '.join(activity['keyword_matched'])}

## Action Required

📱 Respond to this DM via Instagram

## Link

https://www.instagram.com/direct/inbox/

---
Created by Instagram Watcher
"""
            else:  # comment
                content = f"""---
type: instagram_comment
source: instagram
priority: medium
created: {datetime.now().isoformat()}
---

# Instagram Comment Alert

**Post:** {activity['post_id']}
**Commenter:** @{activity['commenter']}
**Time:** {activity['timestamp']}

## Comment

{activity['text']}

## Keywords Matched

{', '.join(activity['keyword_matched'])}

## Action Required

💬 Reply to this comment or monitor for follow-up

## Link

https://www.instagram.com/p/{activity['post_id']}/

---
Created by Instagram Watcher
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"[ACTION] Created: {filename}")

        except Exception as e:
            self.logger.error(f"Error creating action item: {e}")

    def send_notification(self, activities: List[Dict[str, Any]]):
        """Send email notification for important activity"""
        if not self.notification_enabled or not self.notification_email:
            return

        try:
            # This would integrate with email-sender skill
            # For now, just log it
            self.logger.info(f"[NOTIFICATION] Would send email to {self.notification_email}")
            self.logger.info(f"[NOTIFICATION] {len(activities)} new activities detected")

        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")

    def run_once(self):
        """Run one check cycle"""
        self.logger.info("=" * 60)
        self.logger.info("Instagram Watcher - Check Cycle")
        self.logger.info("=" * 60)

        if not self.client:
            if not self.setup_client():
                self.logger.error("Cannot proceed without Instagram client")
                return

        # Check for new activity
        new_messages = self.check_messages()
        new_comments = self.check_comments()

        all_activities = new_messages + new_comments

        if all_activities:
            self.logger.info(f"[DETECTED] {len(all_activities)} new activities")

            for activity in all_activities:
                self.create_action_item(activity)

            # Send notification
            if len(all_activities) > 0:
                self.send_notification(all_activities)
        else:
            self.logger.info("[CLEAN] No new activity detected")

        self.last_check = datetime.now()

    def run(self):
        """Main run loop"""
        self.logger.info("=" * 60)
        self.logger.info("Instagram Watcher Started")
        self.logger.info(f"  Username: {self.username}")
        self.logger.info(f"  Check Interval: {self.check_interval} seconds")
        self.logger.info(f"  Keywords: {', '.join(self.keywords)}")
        self.logger.info(f"  Monitored Posts: {len(self.monitored_posts)}")
        self.logger.info("=" * 60)

        try:
            # Initial setup
            if not self.setup_client():
                self.logger.error("Failed to setup Instagram client")
                return

            while True:
                self.run_once()

                # Wait for next check
                self.logger.info(f"Waiting {self.check_interval} seconds until next check...")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("\n[INFO] Instagram Watcher stopped by user")
        except Exception as e:
            self.logger.error(f"[ERROR] Unexpected error: {e}", exc_info=True)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Instagram Watcher')
    parser.add_argument('--test', action='store_true', help='Run single check cycle')
    parser.add_argument('--setup', action='store_true', help='Setup Instagram credentials')
    args = parser.parse_args()

    watcher = InstagramWatcher()

    if args.setup:
        print("Instagram Watcher Setup")
        print("=" * 50)
        print("\nAdd to watchers/.env:")
        print("INSTAGRAM_USERNAME=your_username")
        print("INSTAGRAM_PASSWORD=your_password")
        print("INSTAGRAM_SESSION=./credentials/instagram_session.json")
        print("INSTAGRAM_CHECK_INTERVAL=180")
        print("INSTAGRAM_KEYWORDS=urgent,inquiry,order,price,help")
        print("INSTAGRAM_MONITORED_POSTS=post_id1,post_id2")
        print("\nThen run: python instagram_watcher.py")
        return

    if args.test:
        watcher.run_once()
        return

    watcher.run()


if __name__ == '__main__':
    main()
