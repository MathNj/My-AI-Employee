#!/usr/bin/env python3
"""
Slack Watcher for Personal AI Employee

Monitors Slack workspace for important messages and events:
- Direct messages to the bot
- @mentions in channels
- Messages in monitored channels
- Important keywords/phrases
- File uploads requiring action
- Thread replies
- Reactions to specific messages

Creates actionable files in Needs_Action folder for AI Employee to process.

Based on architecture from Requirements.md
Requires Slack Bot Token (OAuth).

Author: Personal AI Employee Project
Created: 2026-01-13
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from base_watcher import BaseWatcher

# Optional: Import Slack SDK if available
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    print("Warning: slack-sdk not installed. Install with: pip install slack-sdk")


class SlackWatcher(BaseWatcher):
    """
    Watcher for Slack workspace.

    Monitors for:
    - Direct messages to bot
    - @mentions of bot
    - Messages in monitored channels
    - Specific keywords/phrases
    - File uploads
    - Thread updates
    - Important reactions
    """

    def __init__(
        self,
        vault_path: str,
        check_interval: int = 60,  # 1 minute default
        credentials_path: Optional[str] = None
    ):
        """
        Initialize Slack watcher.

        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between checks (default: 60 = 1 min)
            credentials_path: Path to Slack credentials file
        """
        super().__init__(
            vault_path=vault_path,
            check_interval=check_interval,
            watcher_name="SlackWatcher"
        )

        # Slack-specific paths (credentials are at project root, not in vault)
        project_root = Path(self.vault_path).parent
        self.credentials_dir = project_root / 'watchers' / 'credentials'
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

        self.credentials_path = credentials_path or (
            self.credentials_dir / 'slack_credentials.json'
        )

        # Configuration
        self.config = self._load_config()

        # Slack connection
        self.slack_client = None
        self.bot_user_id = None
        self._initialize_slack_connection()

        # Track last check timestamp
        self.last_check_time = datetime.now()

        self.logger.info("Slack Watcher initialized")
        self.logger.info(f"  Monitoring: DMs, Mentions, Channels, Keywords")
        self.logger.info(f"  Keywords: {', '.join(self.config['keywords'][:5])}...")

    def _load_config(self) -> Dict[str, Any]:
        """Load watcher configuration."""
        project_root = Path(self.vault_path).parent
        config_path = project_root / 'watchers' / 'slack_config.json'

        default_config = {
            'monitored_channels': [],  # Channel IDs or names to monitor
            'keywords': [  # Keywords that trigger alerts
                'urgent', 'important', 'help', 'issue', 'problem',
                'asap', 'critical', 'emergency', 'bug', 'broken'
            ],
            'monitor_dms': True,  # Monitor direct messages
            'monitor_mentions': True,  # Monitor @mentions
            'monitor_files': True,  # Monitor file uploads
            'monitor_threads': True,  # Monitor thread replies
            'ignore_bots': True,  # Ignore messages from other bots
            'min_message_length': 10,  # Minimum message length to process
            'reaction_triggers': ['eyes', 'point_up', 'fire']  # Reactions that trigger action
        }

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Error loading config, using defaults: {e}")

        return default_config

    def _initialize_slack_connection(self):
        """Initialize connection to Slack API."""
        if not SLACK_AVAILABLE:
            self.logger.warning("Slack SDK not available - using mock mode")
            self.slack_client = None
            return

        # Check for credentials
        if not self.credentials_path.exists():
            self.logger.warning(
                f"Slack credentials not found at {self.credentials_path}\n"
                "Please set up Slack Bot Token. See: SLACK_SETUP.md"
            )
            self.slack_client = None
            return

        try:
            # Load credentials
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)

            bot_token = creds_data.get('bot_token')
            if not bot_token:
                raise ValueError("bot_token not found in credentials")

            # Initialize Slack client
            self.slack_client = WebClient(token=bot_token)

            # Get bot user ID
            response = self.slack_client.auth_test()
            self.bot_user_id = response['user_id']

            self.logger.info(f"✓ Connected to Slack (Bot ID: {self.bot_user_id})")

        except Exception as e:
            self.logger.error(f"Failed to connect to Slack: {e}")
            self.logger.warning("Running in mock mode")
            self.slack_client = None

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Slack for new messages and events.

        Returns:
            List of Slack events requiring action
        """
        events = []

        try:
            # Calculate time window (since last check)
            oldest_timestamp = self.last_check_time.timestamp()

            # Check different event types
            if self.config['monitor_dms']:
                events.extend(self._check_direct_messages(oldest_timestamp))

            if self.config['monitor_mentions']:
                events.extend(self._check_mentions(oldest_timestamp))

            if self.config['monitored_channels']:
                events.extend(self._check_channels(oldest_timestamp))

            if self.config['monitor_files']:
                events.extend(self._check_file_uploads(oldest_timestamp))

            # Update last check time
            self.last_check_time = datetime.now()

            # Filter out already processed events
            new_events = [
                event for event in events
                if not self.is_processed(event['id'])
            ]

            if new_events:
                self.logger.info(f"Found {len(new_events)} new Slack event(s)")

            return new_events

        except Exception as e:
            self.logger.error(f"Error checking Slack: {e}", exc_info=True)
            return []

    def _check_direct_messages(self, oldest: float) -> List[Dict]:
        """Check for new direct messages."""
        events = []

        try:
            if self.slack_client:
                # Get list of DM conversations
                response = self.slack_client.conversations_list(
                    types='im',
                    limit=100
                )

                for channel in response['channels']:
                    # Get recent messages in this DM
                    history = self.slack_client.conversations_history(
                        channel=channel['id'],
                        oldest=str(oldest),
                        limit=50
                    )

                    for message in history.get('messages', []):
                        # Skip bot messages if configured
                        if self.config['ignore_bots'] and message.get('bot_id'):
                            continue

                        # Skip messages from self
                        if message.get('user') == self.bot_user_id:
                            continue

                        events.append(self._create_message_event(
                            message, channel['id'], 'direct_message'
                        ))
            else:
                # Mock data
                events.extend(self._get_mock_dms())

        except Exception as e:
            self.logger.error(f"Error checking DMs: {e}")

        return events

    def _check_mentions(self, oldest: float) -> List[Dict]:
        """Check for @mentions of the bot."""
        events = []

        try:
            if self.slack_client and self.bot_user_id:
                # Search for mentions
                query = f"<@{self.bot_user_id}>"

                response = self.slack_client.search_messages(
                    query=query,
                    sort='timestamp',
                    sort_dir='desc',
                    count=50
                )

                for match in response.get('messages', {}).get('matches', []):
                    # Check if message is recent
                    ts = float(match.get('ts', 0))
                    if ts > oldest:
                        events.append(self._create_message_event(
                            match, match.get('channel', {}).get('id'), 'mention'
                        ))
            else:
                # Mock data
                events.extend(self._get_mock_mentions())

        except Exception as e:
            self.logger.error(f"Error checking mentions: {e}")

        return events

    def _check_channels(self, oldest: float) -> List[Dict]:
        """Check monitored channels for important messages."""
        events = []

        try:
            for channel_id in self.config['monitored_channels']:
                if self.slack_client:
                    try:
                        # Get recent messages from channel
                        history = self.slack_client.conversations_history(
                            channel=channel_id,
                            oldest=str(oldest),
                            limit=100
                        )

                        for message in history.get('messages', []):
                            # Skip bot messages if configured
                            if self.config['ignore_bots'] and message.get('bot_id'):
                                continue

                            # Check for keywords
                            text = message.get('text', '').lower()
                            if any(keyword.lower() in text for keyword in self.config['keywords']):
                                events.append(self._create_message_event(
                                    message, channel_id, 'keyword_match'
                                ))

                    except SlackApiError as e:
                        self.logger.error(f"Error checking channel {channel_id}: {e}")
                else:
                    # Mock data
                    events.extend(self._get_mock_channel_messages())

        except Exception as e:
            self.logger.error(f"Error checking channels: {e}")

        return events

    def _check_file_uploads(self, oldest: float) -> List[Dict]:
        """Check for file uploads that need processing."""
        events = []

        try:
            if self.slack_client:
                # Get recent files
                response = self.slack_client.files_list(
                    ts_from=str(oldest),
                    count=50
                )

                for file_obj in response.get('files', []):
                    # Check if file is in monitored channels or DMs
                    events.append({
                        'id': f"file_{file_obj['id']}",
                        'type': 'file_upload',
                        'event_type': 'file_upload',
                        'file_id': file_obj['id'],
                        'filename': file_obj['name'],
                        'filetype': file_obj.get('filetype'),
                        'size': file_obj.get('size'),
                        'url': file_obj.get('url_private'),
                        'user': file_obj.get('user'),
                        'timestamp': file_obj.get('timestamp'),
                        'title': file_obj.get('title'),
                        'channel': file_obj.get('channels', [None])[0]
                    })
            else:
                # Mock data
                events.extend(self._get_mock_files())

        except Exception as e:
            self.logger.error(f"Error checking files: {e}")

        return events

    def _create_message_event(self, message: Dict, channel_id: str, event_type: str) -> Dict:
        """Create standardized event dictionary from Slack message."""
        msg_id = f"{channel_id}_{message.get('ts', '')}"

        return {
            'id': msg_id,
            'type': event_type,
            'event_type': event_type,
            'channel_id': channel_id,
            'user_id': message.get('user'),
            'text': message.get('text', ''),
            'timestamp': message.get('ts'),
            'thread_ts': message.get('thread_ts'),
            'permalink': self._get_permalink(channel_id, message.get('ts')) if self.slack_client else None,
            'reactions': message.get('reactions', []),
            'files': message.get('files', [])
        }

    def _get_permalink(self, channel_id: str, timestamp: str) -> Optional[str]:
        """Get permalink for a message."""
        try:
            if self.slack_client:
                response = self.slack_client.chat_getPermalink(
                    channel=channel_id,
                    message_ts=timestamp
                )
                return response.get('permalink')
        except:
            pass
        return None

    def _get_user_info(self, user_id: str) -> Dict:
        """Get user information."""
        try:
            if self.slack_client:
                response = self.slack_client.users_info(user=user_id)
                user = response.get('user', {})
                return {
                    'name': user.get('real_name', user.get('name')),
                    'display_name': user.get('profile', {}).get('display_name'),
                    'email': user.get('profile', {}).get('email')
                }
        except:
            pass
        return {'name': f'User {user_id}', 'display_name': '', 'email': ''}

    def _get_channel_info(self, channel_id: str) -> Dict:
        """Get channel information."""
        try:
            if self.slack_client:
                response = self.slack_client.conversations_info(channel=channel_id)
                channel = response.get('channel', {})
                return {
                    'name': channel.get('name'),
                    'is_private': channel.get('is_private', False),
                    'is_im': channel.get('is_im', False)
                }
        except:
            pass
        return {'name': f'Channel {channel_id}', 'is_private': False, 'is_im': False}

    def create_action_file(self, event: Dict[str, Any]) -> Optional[Path]:
        """
        Create actionable file for Slack event.

        Args:
            event: Slack event dictionary

        Returns:
            Path to created file
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            event_type = event['event_type']
            filename = f"slack_{event_type}_{timestamp}.md"
            filepath = self.needs_action / filename

            # Create markdown content based on event type
            content = self._create_event_content(event)

            # Write file
            filepath.write_text(content, encoding='utf-8')

            # Mark as processed
            self.mark_as_processed(event['id'])

            # Log action
            self.log_action(
                action_type=f"slack_{event_type}",
                details={
                    'event_id': event['id'],
                    'type': event_type,
                    'user': event.get('user_id'),
                    'channel': event.get('channel_id'),
                    'text_preview': event.get('text', '')[:100]
                },
                task_filename=filename
            )

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}", exc_info=True)
            return None

    def _create_event_content(self, event: Dict) -> str:
        """Create markdown content for event."""
        event_type = event['event_type']
        timestamp = datetime.now().isoformat()

        # Get user and channel info
        user_info = self._get_user_info(event.get('user_id', ''))
        channel_info = self._get_channel_info(event.get('channel_id', ''))

        # Common frontmatter
        content = f"""---
type: slack_event
event_type: {event_type}
source: slack_watcher
created: {timestamp}
status: pending
priority: high
channel_id: {event.get('channel_id', '')}
user_id: {event.get('user_id', '')}
"""

        if event.get('thread_ts'):
            content += f"thread_ts: {event['thread_ts']}\n"

        content += "---\n\n"

        # Event-specific content
        if event_type == 'direct_message':
            content += f"""# Direct Message from {user_info['name']}

## Message Details
- **From:** {user_info['name']} ({user_info.get('display_name', 'N/A')})
- **Email:** {user_info.get('email', 'N/A')}
- **Time:** {self._format_timestamp(event.get('timestamp'))}
- **Channel:** Direct Message
"""
            if event.get('permalink'):
                content += f"- **Link:** {event['permalink']}\n"

            content += f"\n## Message Content\n\n{event.get('text', '')}\n\n"

            if event.get('files'):
                content += "## Attached Files\n\n"
                for file_obj in event['files']:
                    content += f"- {file_obj.get('name')} ({file_obj.get('filetype', 'unknown')})\n"
                content += "\n"

            content += """## Action Required
A direct message was received. This may require a response or action.

**Suggested Actions:**
1. Read and understand the message
2. Draft appropriate response
3. Take any requested actions
4. Follow up if needed

**Next Steps:**
- [ ] Review message content
- [ ] Draft response
- [ ] Verify any claims or requests
- [ ] Send reply via email-sender or LinkedIn if needed
- [ ] Mark as complete
"""

        elif event_type == 'mention':
            content += f"""# @Mention from {user_info['name']} in #{channel_info['name']}

## Message Details
- **From:** {user_info['name']}
- **Channel:** #{channel_info['name']}
- **Time:** {self._format_timestamp(event.get('timestamp'))}
"""
            if event.get('thread_ts'):
                content += "- **Type:** Thread Reply\n"
            if event.get('permalink'):
                content += f"- **Link:** {event['permalink']}\n"

            content += f"\n## Message Content\n\n{event.get('text', '')}\n\n"

            content += """## Action Required
You were mentioned in a Slack message. This may require your attention or response.

**Suggested Actions:**
1. Read the message in context
2. Determine if action is needed
3. Respond in thread or channel
4. Complete any requested tasks

**Next Steps:**
- [ ] Review full conversation context
- [ ] Identify required action
- [ ] Draft response if needed
- [ ] Delegate to appropriate team member
- [ ] Follow up to ensure completion
"""

        elif event_type == 'keyword_match':
            content += f"""# Keyword Match in #{channel_info['name']}

## Message Details
- **From:** {user_info['name']}
- **Channel:** #{channel_info['name']}
- **Time:** {self._format_timestamp(event.get('timestamp'))}
- **Matched Keywords:** {', '.join([kw for kw in self.config['keywords'] if kw.lower() in event.get('text', '').lower()])}
"""
            if event.get('permalink'):
                content += f"- **Link:** {event['permalink']}\n"

            content += f"\n## Message Content\n\n{event.get('text', '')}\n\n"

            content += """## Action Required
A message containing important keywords was detected.

**Suggested Actions:**
1. Assess urgency based on keywords
2. Read full context
3. Determine appropriate response
4. Escalate if critical

**Next Steps:**
- [ ] Evaluate urgency level
- [ ] Review conversation thread
- [ ] Identify stakeholders
- [ ] Take appropriate action
- [ ] Document resolution
"""

        elif event_type == 'file_upload':
            content += f"""# File Upload from {user_info['name']}

## File Details
- **Filename:** {event.get('filename')}
- **Type:** {event.get('filetype', 'unknown')}
- **Size:** {self._format_size(event.get('size', 0))}
- **Uploaded by:** {user_info['name']}
- **Time:** {self._format_timestamp(event.get('timestamp'))}
"""
            if event.get('title'):
                content += f"- **Title:** {event['title']}\n"
            if event.get('url'):
                content += f"- **Download:** {event['url']}\n"

            content += """\n## Action Required
A file was uploaded to Slack that may require processing.

**Suggested Actions:**
1. Download and review file
2. Determine file purpose
3. Process or archive as needed
4. Respond to uploader if needed

**Next Steps:**
- [ ] Download file
- [ ] Verify file type and content
- [ ] Process with appropriate tool
- [ ] Store in correct location
- [ ] Notify uploader of completion
"""

        content += f"\n---\n\n**Slack Event ID:** {event['id']}\n"
        content += f"**Detected:** {timestamp}\n"

        return content

    def _format_timestamp(self, ts: Any) -> str:
        """Format Slack timestamp to readable date."""
        try:
            if isinstance(ts, str):
                ts = float(ts)
            dt = datetime.fromtimestamp(ts)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(ts)

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    # Mock data methods for testing

    def _get_mock_dms(self) -> List[Dict]:
        """Get mock DM data for testing."""
        return [
            {
                'id': 'dm_001',
                'type': 'direct_message',
                'event_type': 'direct_message',
                'channel_id': 'D12345',
                'user_id': 'U12345',
                'text': 'Hey, can you help me with the quarterly report?',
                'timestamp': str(datetime.now().timestamp()),
                'thread_ts': None,
                'permalink': 'https://workspace.slack.com/archives/D12345/p1234567890',
                'reactions': [],
                'files': []
            }
        ]

    def _get_mock_mentions(self) -> List[Dict]:
        """Get mock mention data for testing."""
        return [
            {
                'id': 'mention_001',
                'type': 'mention',
                'event_type': 'mention',
                'channel_id': 'C12345',
                'user_id': 'U23456',
                'text': 'Hey @ai-employee, urgent issue with the deployment!',
                'timestamp': str(datetime.now().timestamp()),
                'thread_ts': None,
                'permalink': 'https://workspace.slack.com/archives/C12345/p1234567891',
                'reactions': [],
                'files': []
            }
        ]

    def _get_mock_channel_messages(self) -> List[Dict]:
        """Get mock channel message data for testing."""
        return [
            {
                'id': 'channel_001',
                'type': 'keyword_match',
                'event_type': 'keyword_match',
                'channel_id': 'C12345',
                'user_id': 'U34567',
                'text': 'This is urgent - the production server is down!',
                'timestamp': str(datetime.now().timestamp()),
                'thread_ts': None,
                'permalink': 'https://workspace.slack.com/archives/C12345/p1234567892',
                'reactions': [],
                'files': []
            }
        ]

    def _get_mock_files(self) -> List[Dict]:
        """Get mock file upload data for testing."""
        return [
            {
                'id': 'file_001',
                'type': 'file_upload',
                'event_type': 'file_upload',
                'file_id': 'F12345',
                'filename': 'quarterly_report.pdf',
                'filetype': 'pdf',
                'size': 1024000,
                'url': 'https://files.slack.com/files-pri/T12345/quarterly_report.pdf',
                'user': 'U45678',
                'timestamp': str(datetime.now().timestamp()),
                'title': 'Q4 2025 Report',
                'channel': 'C12345'
            }
        ]


def main():
    """Main entry point for Slack watcher."""
    # Determine vault path
    vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"

    print("=" * 70)
    print("Personal AI Employee - Slack Watcher")
    print("=" * 70)
    print(f"Vault: {vault_path}")
    print(f"Monitoring: DMs, Mentions, Channels, Files")
    print(f"Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Create and run watcher
    try:
        watcher = SlackWatcher(
            vault_path=str(vault_path),
            check_interval=60  # Check every minute
        )
        watcher.run()

    except KeyboardInterrupt:
        print("\n\nSlack watcher stopped by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
