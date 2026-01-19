# AI Employee Complete Workflow

## System Overview

Your Personal AI Employee is now fully automated with **zero manual intervention required**. All watchers and posters run 24/7 through the orchestration system.

## Complete Workflow Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                    WINDOWS STARTUP                                │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │   Windows Task Scheduler               │
        │   Auto-starts: watchdog.py             │
        └────────────────┬───────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                    WATCHDOG LAYER                                 │
│  watchdog.py - Ensures orchestrator stays alive                   │
│  - Checks every 60 seconds                                        │
│  - Auto-restarts orchestrator if crashed                          │
│  - Logs all restart events                                        │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR LAYER                               │
│  orchestrator.py - Master process manager                         │
│  - Starts all enabled watchers                                    │
│  - Health checks every 60 seconds                                 │
│  - Auto-restarts failed watchers                                  │
│  - Manages graceful shutdown                                      │
└─────────┬─────────────────────────────────────────────────────────┘
          │
          │    Manages 6 Watchers:
          │
    ┌─────┴─────────┬──────────┬──────────┬──────────┬──────────┐
    ▼               ▼          ▼          ▼          ▼          ▼
┌─────────┐   ┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────┐ ┌──────┐
│Calendar │   │ Slack   │ │ Gmail  │ │WhatsApp │ │File  │ │ Xero │
│Watcher  │   │ Watcher │ │Watcher │ │ Watcher │ │System│ │Watch │
│         │   │         │ │        │ │         │ │Watch │ │      │
│5min     │   │1min     │ │2min    │ │30sec    │ │Real  │ │5min  │
│interval │   │interval │ │interval│ │interval │ │-time │ │inter.│
└────┬────┘   └────┬────┘ └───┬────┘ └────┬────┘ └──┬───┘ └──┬───┘
     │             │          │           │         │        │
     │  Monitors:  │          │           │         │        │
     │  - Events   │  - Msgs  │  - Emails │  - Msgs │ - Files│ - $$$
     │  1-48hrs    │  w/keys  │  unread   │  w/keys │ drop in│ events
     │  ahead      │  words   │  import.  │  words  │ Inbox  │
     │             │          │           │         │        │
     └─────────────┴──────────┴───────────┴─────────┴────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   Creates .md files in:       │
              │   AI_Employee_Vault/          │
              │   Needs_Action/               │
              └───────────────┬───────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ /Needs_Action/                                              │ │
│  │  - slack_keyword_match_TIMESTAMP.md                         │ │
│  │  - CALENDAR_EVENT_ID_TIMESTAMP_title.md                     │ │
│  │  - EMAIL_MESSAGE_ID.md                                      │ │
│  │  - whatsapp_urgent_TIMESTAMP.md                             │ │
│  │  - FILE_filename.md                                         │ │
│  │  - xero_new_invoice_TIMESTAMP.md                            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Dashboard.md - Real-time overview                           │ │
│  │ Company_Handbook.md - Rules & policies                      │ │
│  │ Business_Goals.md - Targets & metrics                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │   MANUAL REVIEW    │
                    │   Check Dashboard  │
                    │   Process Tasks    │
                    └────────────────────┘
```

## Daily Operation Flow

### 1. Morning (Automatic)

```
8:00 AM → Calendar Watcher detects today's events
       → Creates task files in Needs_Action/
       → You open Obsidian Dashboard
       → Review upcoming events
```

### 2. Throughout Day (Automatic)

```
Continuous → Slack messages with keywords detected
          → Gmail important emails captured
          → WhatsApp urgent messages logged
          → Files dropped in Inbox processed
          → Xero financial events tracked

          → All create task files in Needs_Action/
```

### 3. Evening (Manual Review)

```
6:00 PM → Open Obsidian
        → Review Needs_Action/ folder
        → Process tasks:
          - Reply to messages
          - Review calendar prep
          - Check financial events
        → Move completed to Done/
```

## Watcher Details

### 1. Calendar Watcher (calendar_watcher.py)

**What it monitors:**
- Google Calendar events 1-48 hours ahead
- All-day events
- Timed appointments
- Event reminders

**Check interval:** 5 minutes (300 seconds)

**Output format:**
```markdown
---
type: calendar_event
event_id: abc123
summary: Client Meeting
start_time: 2026-01-15T14:00:00
priority: medium
---

# Upcoming Event: Client Meeting

## Preparation Actions
- [ ] Review agenda
- [ ] Prepare materials
...
```

**When it creates tasks:**
- Event is 1-48 hours ahead
- Not already processed
- Not all-day events scheduled far in advance

---

### 2. Slack Watcher (slack_watcher.py)

**What it monitors:**
- Messages in #all-ai-employee-slack channel
- Keyword matches: test, urgent, important, help, issue, problem

**Check interval:** 1 minute (60 seconds)

**Output format:**
```markdown
---
type: slack_event
event_type: keyword_match
channel_id: C0A8FMJJ2QM
user_id: U0A8NNB4BTN
priority: high
---

# Keyword Match in #all-ai-employee-slack

## Message Content
test message here

## Matched Keywords
test
```

**When it creates tasks:**
- Message contains monitored keywords
- Not from bot itself
- New message (not already processed)

---

### 3. Gmail Watcher (gmail_watcher.py)

**What it monitors:**
- Unread important emails
- OAuth authenticated with Gmail API

**Check interval:** 2 minutes (120 seconds)

**Output format:**
```markdown
---
type: email
from: sender@example.com
subject: Important Topic
priority: high
---

## Email Content
Email snippet here...

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to team
...
```

**When it creates tasks:**
- Email is unread
- Marked as important
- Not already processed

---

### 4. WhatsApp Watcher (whatsapp_watcher.py)

**What it monitors:**
- WhatsApp Web messages
- Keywords: urgent, asap, emergency, critical, help, invoice, payment, etc.

**Check interval:** 30 seconds

**Special requirements:**
- Runs in visible browser mode
- Uses Playwright browser automation
- Session persists in watchers/whatsapp_session/

**Output format:**
```markdown
---
type: whatsapp_event
event_type: urgent_message
priority: high
---

# WhatsApp Urgent Message

## Message Details
Content with urgent keyword...
```

**When it creates tasks:**
- Message contains monitored keywords
- From unread chats
- Not from broadcast lists

---

### 5. Filesystem Watcher (filesystem_watcher.py)

**What it monitors:**
- AI_Employee_Vault/Inbox/ folder
- Any file dropped into this folder

**Check interval:** Real-time (watchdog pattern)

**Output format:**
```markdown
---
type: file_drop
original_name: document.pdf
size: 1024000
---

# New File Dropped

File: document.pdf
Requires processing...
```

**When it creates tasks:**
- New file appears in Inbox/
- Immediately detected
- Metadata file created alongside

---

### 6. Xero Watcher (xero_watcher.py)

**What it monitors:**
- New invoices
- New bills
- Payments received
- Large transactions (>$500)
- Overdue invoices

**Check interval:** 5 minutes (300 seconds)

**Authentication:** OAuth 2.0 with Xero API

**Output format:**
```markdown
---
type: xero_event
event_type: new_invoice
amount: 1500.00
priority: high
---

# New Xero Invoice

## Invoice Details
Amount: $1,500.00
Client: Client A
...
```

**When it creates tasks:**
- New financial event detected
- Transaction exceeds alert threshold
- Invoice becomes overdue
- Not already processed

---

## Control Commands

### Check Status
```bash
python orchestrator_cli.py status
```

### Start Manually
```bash
python orchestrator.py
```

### Stop All
```bash
python orchestrator_cli.py stop
```

### Restart Everything
```bash
python orchestrator_cli.py restart
```

### Enable/Disable Specific Watchers

Edit `orchestrator_config.json`:
```json
{
  "processes": {
    "whatsapp": {
      "enabled": false
    }
  }
}
```

Then restart orchestrator.

---

## Auto-Start Setup (One-Time)

### Windows Task Scheduler Setup

1. Run as Administrator:
   ```bash
   setup_auto_start.bat
   ```

2. The watchdog will now start on every Windows login

3. The watchdog ensures orchestrator stays running

4. Orchestrator manages all 6 watchers

Result: **Fully automatic 24/7 operation**

---

## Monitoring & Logs

### Log Files

- `orchestrator.log` - Master orchestrator activity
- `watchdog.log` - Watchdog monitoring events
- Individual watcher logs (calendar_watcher.log, etc.)

### Check Logs

```bash
# View orchestrator activity
type watchers\orchestrator.log

# View recent errors
type watchers\orchestrator.log | findstr ERROR

# View watchdog restarts
type watchers\watchdog.log | findstr restart
```

---

## Failure Scenarios & Recovery

### Scenario 1: Watcher Crashes

**What happens:**
1. Watcher process terminates unexpectedly
2. Orchestrator detects failure within 60 seconds
3. Orchestrator automatically restarts watcher
4. Event logged to orchestrator.log

**Manual intervention:** None required

---

### Scenario 2: Orchestrator Crashes

**What happens:**
1. Orchestrator process terminates
2. Watchdog detects failure within 60 seconds
3. Watchdog automatically restarts orchestrator
4. Orchestrator restarts all watchers
5. Event logged to watchdog.log

**Manual intervention:** None required

---

### Scenario 3: System Reboot

**What happens:**
1. Windows boots up
2. Task Scheduler starts watchdog.py
3. Watchdog starts orchestrator.py
4. Orchestrator starts all 6 watchers
5. System resumes normal operation

**Manual intervention:** None required (if auto-start is configured)

---

### Scenario 4: API Credentials Expire

**What happens:**
1. Watcher fails authentication
2. Creates error in log
3. Watcher continues retrying

**Manual intervention:** Required - re-authenticate the specific service

---

## Best Practices

1. **Check Dashboard Daily**
   - Morning: Review upcoming calendar events
   - Evening: Process Needs_Action tasks

2. **Review Logs Weekly**
   - Check for repeated failures
   - Monitor restart counts
   - Verify all watchers running

3. **Audit Monthly**
   - Review all processed tasks
   - Check credential expiration dates
   - Update keywords/configurations
   - Optimize check intervals

4. **Backup Configuration**
   - Save orchestrator_config.json
   - Keep credentials backed up securely
   - Document any custom modifications

---

## Troubleshooting

### Problem: Orchestrator not starting

**Solution:**
```bash
# Check if already running
python orchestrator_cli.py status

# View logs for errors
type watchers\orchestrator.log

# Start manually to see errors
cd watchers
python orchestrator.py
```

### Problem: Specific watcher keeps crashing

**Solution:**
1. Identify watcher from logs
2. Test watcher manually:
   ```bash
   cd watchers
   python calendar_watcher.py
   ```
3. Fix authentication or configuration issue
4. Restart orchestrator

### Problem: No tasks being created

**Solution:**
1. Check watchers are running:
   ```bash
   python orchestrator_cli.py status
   ```
2. Verify watcher is enabled in config
3. Check watcher-specific logs for errors
4. Test data source (send test email, etc.)

---

## Summary

✅ **Zero Manual Intervention Required**
- Watchdog ensures orchestrator stays running
- Orchestrator manages all 6 watchers
- Auto-restart on failures
- Auto-start on boot (when configured)

✅ **24/7 Monitoring**
- Calendar: Events 1-48 hours ahead
- Slack: Keyword messages every minute
- Gmail: Important emails every 2 minutes
- WhatsApp: Urgent messages every 30 seconds
- Filesystem: Real-time file drops
- Xero: Financial events every 5 minutes

✅ **Automatic Task Creation**
- All watchers create .md files in Needs_Action/
- Formatted with YAML frontmatter
- Ready for Claude Code processing
- Includes suggested actions

✅ **Fault Tolerant**
- Auto-restart failed watchers
- Watchdog monitors orchestrator
- Comprehensive error logging
- Graceful degradation

Your Personal AI Employee is now fully autonomous! 🎉
