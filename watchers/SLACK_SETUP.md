# Slack Watcher Setup Guide

Complete guide to set up the Slack watcher for your Personal AI Employee.

---

## Overview

The Slack watcher monitors your Slack workspace for important messages and events:

- **Direct Messages** - Messages sent directly to your bot
- **@Mentions** - Times when your bot is @mentioned in channels
- **Channel Messages** - Messages in monitored channels with important keywords
- **File Uploads** - Files shared that may need processing
- **Thread Replies** - Responses in conversation threads

When events are detected, actionable files are created in `Needs_Action/` for the AI Employee to process.

---

## Prerequisites

- Slack workspace (admin or app management permissions)
- Python 3.8+ installed
- Personal AI Employee vault set up

---

## Step 1: Install Python Dependencies

```bash
# Install Slack SDK
pip install slack-sdk

# Or add to your project requirements
pip install slack-sdk requests
```

---

## Step 2: Create Slack App

### 2.1: Go to Slack API Portal

1. Visit: https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. **App Name:** Personal AI Employee
5. **Workspace:** Select your workspace
6. Click "Create App"

### 2.2: Configure Bot Token Scopes

1. In the left sidebar, click **OAuth & Permissions**
2. Scroll to **Bot Token Scopes**
3. Add these scopes:

**Required Scopes:**
- `channels:history` - Read messages in public channels
- `channels:read` - View basic channel information
- `chat:write` - Send messages
- `files:read` - View files
- `groups:history` - Read messages in private channels
- `groups:read` - View private channels
- `im:history` - Read direct messages
- `im:read` - View DM information
- `mpim:history` - Read group DMs
- `mpim:read` - View group DM info
- `users:read` - View user information
- `search:read` - Search messages

**Optional (but recommended):**
- `reactions:read` - View reactions
- `emoji:read` - View custom emoji

### 2.3: Install App to Workspace

1. Scroll to top of **OAuth & Permissions** page
2. Click **Install to Workspace**
3. Review permissions
4. Click **Allow**
5. **Copy the Bot User OAuth Token** (starts with `xoxb-`)
   - This is your `bot_token`
   - Keep it secret!

### 2.4: Enable Event Subscriptions (Optional)

For real-time updates instead of polling:

1. Go to **Event Subscriptions**
2. Toggle **Enable Events** to On
3. Enter your **Request URL** (requires HTTPS endpoint)
   - Example: `https://your-domain.com/slack/events`
4. Subscribe to bot events:
   - `message.im` - DMs to bot
   - `message.channels` - Public channel messages
   - `message.groups` - Private channel messages
   - `app_mention` - @mentions
5. Click **Save Changes**

*Note: Event subscriptions require a web server. Start with polling mode first.*

---

## Step 3: Configure Watcher

Create credentials file:

**File:** `watchers/credentials/slack_credentials.json`

```json
{
  "bot_token": "xoxb-YOUR-BOT-TOKEN-HERE",
  "app_token": "xapp-YOUR-APP-TOKEN-HERE",
  "signing_secret": "YOUR-SIGNING-SECRET-HERE"
}
```

**Important:** Replace the tokens with your actual values from Step 2.3.

**Where to find tokens:**
- **bot_token:** OAuth & Permissions page (starts with `xoxb-`)
- **app_token:** Basic Information > App-Level Tokens (optional)
- **signing_secret:** Basic Information > App Credentials

---

## Step 4: Configure Watcher Settings

Create or edit configuration file:

**File:** `watchers/slack_config.json`

```json
{
  "monitored_channels": [
    "C12345ABC",
    "C67890DEF"
  ],
  "keywords": [
    "urgent",
    "important",
    "help",
    "issue",
    "problem",
    "asap",
    "critical",
    "emergency",
    "bug",
    "broken"
  ],
  "monitor_dms": true,
  "monitor_mentions": true,
  "monitor_files": true,
  "monitor_threads": true,
  "ignore_bots": true,
  "min_message_length": 10,
  "reaction_triggers": ["eyes", "point_up", "fire"]
}
```

**Configuration Options:**

| Setting | Default | Description |
|---------|---------|-------------|
| `monitored_channels` | [] | Channel IDs to monitor (get from channel details) |
| `keywords` | [...] | Keywords that trigger alerts |
| `monitor_dms` | true | Monitor direct messages to bot |
| `monitor_mentions` | true | Monitor @mentions of bot |
| `monitor_files` | true | Monitor file uploads |
| `monitor_threads` | true | Monitor thread replies |
| `ignore_bots` | true | Ignore messages from other bots |
| `min_message_length` | 10 | Minimum message length to process |
| `reaction_triggers` | [...] | Emoji reactions that trigger action |

---

## Step 5: Find Channel IDs

To monitor specific channels, you need their IDs:

### Method 1: From Slack Web/Desktop

1. Open the channel in Slack
2. Click the channel name at the top
3. Scroll down in the "About" tab
4. Copy the **Channel ID** (e.g., `C12345ABC`)

### Method 2: Using Python Script

```python
from slack_sdk import WebClient

client = WebClient(token="xoxb-YOUR-TOKEN")
response = client.conversations_list()

for channel in response['channels']:
    print(f"{channel['name']}: {channel['id']}")
```

### Method 3: From URL

When viewing a channel, the URL shows the ID:
```
https://workspace.slack.com/archives/C12345ABC
                                      └─ This is the Channel ID
```

Add these IDs to `monitored_channels` in `slack_config.json`.

---

## Step 6: Invite Bot to Channels

The bot must be a member of channels you want to monitor:

1. Open the channel in Slack
2. Type: `/invite @Personal AI Employee`
3. Press Enter
4. Bot is now a member and can read messages

*Repeat for each channel in `monitored_channels`.*

---

## Step 7: Test the Watcher

### Run in Mock Mode (No credentials needed)

```bash
cd watchers
python slack_watcher.py
```

Mock mode generates test events so you can see how the watcher works.

### Run with Real Slack

After configuring credentials:

```bash
cd watchers
python slack_watcher.py
```

You should see:
```
======================================================================
Personal AI Employee - Slack Watcher
======================================================================
Vault: C:\Users\YourName\Desktop\My Vault
Monitoring: DMs, Mentions, Channels, Files
Press Ctrl+C to stop
======================================================================

2026-01-13 15:30:00 - SlackWatcher - INFO - ✓ Connected to Slack (Bot ID: U12345)
2026-01-13 15:30:00 - SlackWatcher - INFO - SlackWatcher started
```

### Test with Real Messages

1. **Send DM to bot:** Open DM with your bot, send a message
2. **@Mention bot:** In a channel, type `@Personal AI Employee test`
3. **Upload file:** Share a file in a monitored channel
4. **Use keyword:** Send message with "urgent" or another keyword

Wait up to 1 minute (check interval) and verify files appear in `Needs_Action/`.

---

## Step 8: Schedule Watcher (Optional)

### Windows (Task Scheduler)

```powershell
# Run every minute
schtasks /create /tn "AI_Employee_Slack" /tr "python C:\path\to\watchers\slack_watcher.py" /sc minute /mo 1
```

### Linux/Mac (Cron)

```bash
# Add to crontab (runs every minute)
* * * * * cd /path/to/watchers && python slack_watcher.py >> /tmp/slack_watcher.log 2>&1
```

---

## What Gets Created

When the watcher detects events, it creates markdown files in `Needs_Action/`:

### Example: Direct Message Detected

**File:** `Needs_Action/slack_direct_message_20260113_153045.md`

```markdown
---
type: slack_event
event_type: direct_message
source: slack_watcher
created: 2026-01-13T15:30:45Z
status: pending
priority: high
channel_id: D12345
user_id: U12345
---

# Direct Message from John Doe

## Message Details
- **From:** John Doe (john)
- **Email:** john@company.com
- **Time:** 2026-01-13 15:30:22
- **Channel:** Direct Message
- **Link:** https://workspace.slack.com/archives/D12345/p1234567890

## Message Content

Hey, can you help me with the quarterly report?

## Action Required
A direct message was received. This may require a response or action.

**Suggested Actions:**
1. Read and understand the message
2. Draft appropriate response
3. Take any requested actions
...
```

The AI Employee can then:
- Process these files automatically
- Draft responses
- Create tasks
- Flag for approval if needed
- Send replies via Slack or email

---

## Troubleshooting

### "slack-sdk not installed"

```bash
pip install slack-sdk
```

### "Slack credentials not found"

- Verify `watchers/credentials/slack_credentials.json` exists
- Check file path is correct
- Ensure JSON is valid
- Confirm bot_token is present

### "Failed to connect to Slack"

- Check bot_token is correct (starts with `xoxb-`)
- Verify app is installed to workspace
- Ensure bot has required scopes
- Check internet connection

### No Events Detected

1. **DMs not working:**
   - Send test DM to bot
   - Check `monitor_dms: true` in config
   - Verify bot has `im:history` scope

2. **Mentions not working:**
   - Use `@botname` not just botname
   - Check `monitor_mentions: true`
   - Verify bot has `search:read` scope

3. **Channel messages not working:**
   - Add channel ID to `monitored_channels`
   - Invite bot to channel: `/invite @botname`
   - Use keywords from config
   - Check bot has `channels:history` scope

4. **Files not detected:**
   - Check `monitor_files: true`
   - Verify bot has `files:read` scope
   - Upload file in monitored channel or DM

### Check Logs

```bash
# View watcher log
cat Logs/slackwatcher_$(date +%Y-%m-%d).log

# View action log
cat Logs/actions_$(date +%Y-%m-%d).json | python -m json.tool

# View processed items
cat Logs/slackwatcher_processed.json
```

---

## Configuration Examples

### High Alert (Monitor Everything)

```json
{
  "monitored_channels": ["C12345", "C67890", "C11111"],
  "keywords": [
    "urgent", "important", "help", "issue", "critical",
    "bug", "error", "down", "broken", "emergency",
    "asap", "problem", "failure", "alert"
  ],
  "monitor_dms": true,
  "monitor_mentions": true,
  "monitor_files": true,
  "monitor_threads": true,
  "ignore_bots": true,
  "min_message_length": 5
}
```

### Mentions Only (Minimal)

```json
{
  "monitored_channels": [],
  "keywords": [],
  "monitor_dms": false,
  "monitor_mentions": true,
  "monitor_files": false,
  "monitor_threads": false,
  "ignore_bots": true,
  "min_message_length": 10
}
```

### Specific Team Channel

```json
{
  "monitored_channels": ["C12345ABC"],
  "keywords": ["deploy", "release", "production", "urgent"],
  "monitor_dms": true,
  "monitor_mentions": true,
  "monitor_files": true,
  "monitor_threads": true,
  "ignore_bots": true,
  "min_message_length": 10
}
```

---

## Security Best Practices

1. **Never commit tokens to git:**
   ```bash
   # Add to .gitignore
   watchers/credentials/slack_credentials.json
   ```

2. **Restrict bot permissions:**
   - Only add scopes actually needed
   - Don't grant `chat:write:user` (posts as user)
   - Avoid admin scopes unless necessary

3. **Rotate tokens periodically:**
   - Regenerate bot token every 6 months
   - Update credentials file
   - Restart watcher

4. **Monitor bot usage:**
   - Review Slack app analytics
   - Check for unusual API calls
   - Audit bot activity logs

5. **Limit channel access:**
   - Only invite bot to necessary channels
   - Use private channels for sensitive data
   - Remove bot from channels when no longer needed

---

## Advanced Features

### Custom Keywords

Add industry or company-specific terms:

```json
{
  "keywords": [
    "urgent", "important",
    "customer complaint", "refund", "chargeback",
    "server down", "outage", "incident",
    "legal", "compliance", "audit",
    "revenue", "contract", "deal"
  ]
}
```

### Reaction Triggers

Monitor specific emoji reactions:

```json
{
  "reaction_triggers": [
    "eyes",        // 👀 Someone is watching
    "point_up",    // ☝️ Important
    "fire",        // 🔥 Hot/urgent
    "warning",     // ⚠️ Warning
    "sos",         // 🆘 Emergency
    "white_check_mark"  // ✅ Approved
  ]
}
```

### Thread Monitoring

The watcher automatically detects thread replies. Enable with:

```json
{
  "monitor_threads": true
}
```

---

## Integration with AI Employee

The Slack watcher integrates seamlessly with your AI Employee workflow:

```
Slack Workspace
    ↓
Slack Watcher (polls every 1 min)
    ↓
Needs_Action/ (creates .md files)
    ↓
Task Processor (AI reads and analyzes)
    ↓
Action Plans (creates execution plans)
    ↓
Approval Workflow (if needed)
    ↓
Execute Actions:
    - Email Sender (notify via email)
    - Dashboard Updater (log activity)
    - LinkedIn Poster (share updates)
    - Financial Analyst (if invoice/payment)
    ↓
Done/ (completed and logged)
```

---

## Support and Resources

- **Slack API Docs:** https://api.slack.com/
- **slack-sdk Python:** https://slack.dev/python-slack-sdk/
- **Bot Token Scopes:** https://api.slack.com/scopes
- **Event Types:** https://api.slack.com/events
- **Rate Limits:** https://api.slack.com/docs/rate-limits

---

## Next Steps

1. ✅ Complete this setup
2. ✅ Test watcher with mock data
3. ✅ Configure real Slack credentials
4. ✅ Test with real messages
5. ✅ Schedule watcher to run continuously
6. Configure AI Employee to process Slack events
7. Set up approval workflow for responses
8. Integrate with email-sender for notifications
9. Connect to dashboard for activity tracking

---

**Slack Watcher Setup Complete!** 🎉

Your AI Employee is now monitoring your Slack workspace and will alert you to important messages and events automatically.
