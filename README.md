# Personal AI Employee - Autonomous Business Assistant

**Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A fully autonomous AI Employee system that monitors Gmail, Slack, WhatsApp, Google Calendar, file systems, and accounting (Xero) 24/7, creating actionable tasks in your Obsidian vault. Built with Claude Code, orchestrated watchers, and approval workflows.

## System Status

**Current Tier:** Gold Tier - Fully Operational

- ✅ All 6 watchers running automatically
- ✅ Orchestration system with auto-restart
- ✅ Approval workflow for social media posts
- ✅ Obsidian vault as management dashboard
- ✅ Claude Code integration via Agent Skills
- ✅ 24/7 operation with watchdog monitoring

## What This System Does

Your Personal AI Employee operates continuously without manual intervention:

1. **Monitors 6 Input Sources:**
   - Gmail (unread important emails every 2 minutes)
   - Slack (keyword matches every 1 minute)
   - Google Calendar (events 1-48 hours ahead every 5 minutes)
   - WhatsApp (urgent messages every 30 seconds)
   - File System (real-time file drops in Inbox folder)
   - Xero Accounting (financial events every 5 minutes)

2. **Creates Actionable Tasks:**
   - All detected events → Markdown files in `AI_Employee_Vault/Needs_Action/`
   - Formatted with YAML frontmatter for structured processing
   - Includes suggested actions and priority levels

3. **Human-in-the-Loop Approval:**
   - Sensitive actions (social posts, emails) require approval
   - Move files from `/Pending_Approval` → `/Approved` to execute
   - Complete audit trail in activity logs

4. **Automatic Posting:**
   - LinkedIn business updates
   - X/Twitter posts (when implemented)
   - Instagram and Facebook posts
   - All posts go through approval workflow

## Quick Start

### Option 1: Auto-Start on Boot (Recommended)

**Run once to configure:**
```bash
cd watchers
setup_auto_start.bat
```
(Right-click → Run as Administrator)

The watchdog will now start automatically when you log into Windows, ensuring 24/7 operation.

### Option 2: Manual Start

```bash
# Start all watchers via orchestrator
cd watchers
python orchestrator.py

# OR use the batch file
start_ai_employee.bat
```

### Check Status

```bash
cd watchers
python orchestrator_cli.py status
```

Output shows:
- Orchestrator PID and memory usage
- All 6 running watchers with their PIDs
- Health status

### Stop All

```bash
cd watchers
python orchestrator_cli.py stop

# OR use the batch file
stop_ai_employee.bat
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  WINDOWS STARTUP                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │   Windows Task Scheduler         │
        │   Auto-starts: watchdog.py       │
        └──────────────┬───────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  WATCHDOG LAYER                         │
│  Ensures orchestrator stays alive                       │
│  - Checks every 60 seconds                              │
│  - Auto-restarts if crashed                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│               ORCHESTRATOR LAYER                        │
│  Master process manager                                 │
│  - Starts all 6 watchers                                │
│  - Health checks every 60 seconds                       │
│  - Auto-restarts failed watchers                        │
└───┬─────┬─────┬─────┬─────┬─────┬───────────────────────┘
    │     │     │     │     │     │
    ▼     ▼     ▼     ▼     ▼     ▼
 Calendar Slack Gmail WhatsApp File Xero
 Watcher  Watch Watch Watcher  Sys  Watch
                               Watch
```

## The 6 Watchers

### 1. Calendar Watcher
- **Monitors:** Google Calendar events 1-48 hours ahead
- **Interval:** 5 minutes
- **Output:** `CALENDAR_EVENT_[id]_[timestamp].md` in Needs_Action/
- **Use Case:** Prepare for meetings, get reminders

### 2. Slack Watcher
- **Monitors:** #all-ai-employee-slack channel for keywords
- **Keywords:** test, urgent, important, help, issue, problem
- **Interval:** 1 minute
- **Output:** `slack_keyword_match_[timestamp].md` in Needs_Action/
- **Use Case:** Never miss urgent team messages

### 3. Gmail Watcher
- **Monitors:** Unread important emails
- **Interval:** 2 minutes
- **Output:** `EMAIL_[message_id].md` in Needs_Action/
- **Use Case:** Auto-triage important emails

### 4. WhatsApp Watcher
- **Monitors:** WhatsApp Web messages with keywords
- **Keywords:** urgent, asap, emergency, critical, help, invoice, payment
- **Interval:** 30 seconds
- **Special:** Runs in visible browser mode (WhatsApp Web blocks headless)
- **Output:** `whatsapp_urgent_[timestamp].md` in Needs_Action/
- **Use Case:** Capture urgent client messages

### 5. Filesystem Watcher
- **Monitors:** AI_Employee_Vault/Inbox/ folder
- **Interval:** Real-time (immediate detection)
- **Output:** `FILE_[filename].md` in Needs_Action/
- **Use Case:** Process dropped documents, invoices, files

### 6. Xero Watcher
- **Monitors:** Xero accounting events
- **Events:** New invoices, bills, payments, large transactions (>$500), overdue invoices
- **Interval:** 5 minutes
- **Output:** `xero_[event_type]_[timestamp].md` in Needs_Action/
- **Use Case:** Track financial activity automatically

## Folder Structure

```
My Vault/
├── AI_Employee_Vault/
│   ├── Inbox/                    # Drop files here for processing
│   ├── Needs_Action/              # Auto-created task files
│   ├── Plans/                     # Action plans (when using task-processor)
│   ├── Done/                      # Completed tasks
│   ├── Pending_Approval/          # Actions awaiting approval
│   ├── Approved/                  # Approved actions (auto-executed)
│   ├── Failed/                    # Failed actions (review required)
│   ├── Logs/                      # Activity logs
│   ├── Dashboard.md               # System dashboard
│   ├── Company_Handbook.md        # Rules and policies
│   └── Business_Goals.md          # Targets and metrics
├── watchers/
│   ├── orchestrator.py            # Master process manager
│   ├── watchdog.py                # Health monitor for orchestrator
│   ├── orchestrator_cli.py        # CLI for management
│   ├── orchestrator_config.json   # Configuration file
│   ├── calendar_watcher.py        # Google Calendar watcher
│   ├── slack_watcher.py           # Slack watcher
│   ├── gmail_watcher.py           # Gmail watcher
│   ├── whatsapp_watcher.py        # WhatsApp watcher
│   ├── filesystem_watcher.py      # File system watcher
│   ├── xero_watcher.py            # Xero accounting watcher
│   ├── credentials/               # API credentials (gitignored)
│   ├── start_ai_employee.bat      # Easy start script
│   ├── stop_ai_employee.bat       # Easy stop script
│   └── setup_auto_start.bat       # Auto-start configuration
├── .claude/skills/                # Claude Code Agent Skills
│   ├── approval-processor/        # Approval workflow processor
│   ├── linkedin-poster/           # LinkedIn posting skill
│   ├── x-poster/                  # Twitter/X posting skill
│   ├── social-media-manager/      # Multi-platform social media
│   └── [other skills]/
├── README.md                      # This file
├── QUICKSTART.md                  # Quick start guide
├── AI_EMPLOYEE_WORKFLOW.md        # Complete workflow documentation
├── watchers/README_ORCHESTRATION.md  # Orchestration system docs
└── Requirements1.md               # Full architectural specification
```

## Agent Skills

All AI functionality is implemented as [Claude Code Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview):

- **approval-processor** - Process approved actions automatically
- **dashboard-updater** - Update Dashboard.md with current status
- **task-processor** - Process tasks from Needs_Action folder
- **vault-setup** - Initialize vault structure
- **watcher-manager** - Create and manage watcher scripts
- **linkedin-poster** - Post business updates to LinkedIn
- **x-poster** - Post tweets to Twitter/X
- **social-media-manager** - Unified multi-platform posting
- **financial-analyst** - Analyze financial data and generate insights
- **ceo-briefing-generator** - Generate weekly CEO briefings
- **business-goals-manager** - Manage business goals and metrics
- **xero-integrator** - Xero accounting integration
- **web-researcher** - Safe external knowledge access
- **scheduler-manager** - Cross-platform task scheduling

## Configuration

### Enable/Disable Watchers

Edit `watchers/orchestrator_config.json`:

```json
{
  "processes": {
    "calendar": {"enabled": true},
    "slack": {"enabled": true},
    "gmail": {"enabled": true},
    "whatsapp": {"enabled": false},  // Disable WhatsApp
    "filesystem": {"enabled": true},
    "xero": {"enabled": true}
  }
}
```

Then restart orchestrator:
```bash
cd watchers
python orchestrator_cli.py restart
```

### Customize Check Intervals

Override individual watcher check intervals:

```json
{
  "processes": {
    "slack": {
      "enabled": true,
      "check_interval_override": 30  // Check every 30 seconds instead of 60
    }
  }
}
```

## Daily Workflow

### Morning (Automatic)
1. Calendar Watcher detects today's events
2. Creates task files in Needs_Action/
3. You review Dashboard.md in Obsidian
4. See upcoming events and prepare

### Throughout Day (Automatic)
1. All watchers continuously monitor
2. Detected events → task files in Needs_Action/
3. Check Dashboard.md periodically
4. Process urgent tasks as they arrive

### Evening (Manual Review)
1. Open Obsidian
2. Review Needs_Action/ folder
3. Process tasks (reply to messages, etc.)
4. Move completed tasks to Done/

## Monitoring & Logs

### Log Files

All logs in `watchers/` directory:
- `orchestrator.log` - Master orchestrator activity
- `watchdog.log` - Watchdog monitoring events
- `calendar_watcher.log` - Calendar watcher activity
- `slack_watcher.log` - Slack watcher activity
- `gmail_watcher.log` - Gmail watcher activity
- `whatsapp_watcher.log` - WhatsApp watcher activity
- `filesystem_watcher.log` - Filesystem watcher activity
- `xero_watcher.log` - Xero watcher activity

### Check Recent Activity

```bash
# View orchestrator activity
type watchers\orchestrator.log

# View recent errors
type watchers\orchestrator.log | findstr ERROR

# View watchdog restarts
type watchers\watchdog.log | findstr restart

# Check specific watcher
type watchers\gmail_watcher.log
```

## Troubleshooting

### Orchestrator won't start

```bash
# Check if already running
cd watchers
python orchestrator_cli.py status

# View logs for errors
type orchestrator.log

# Start manually to see errors
python orchestrator.py
```

### Specific watcher keeps crashing

1. Check orchestrator log for errors
2. Test watcher manually:
   ```bash
   cd watchers
   python calendar_watcher.py
   ```
3. Fix authentication or configuration issue
4. Restart orchestrator

### No tasks being created

1. Check watchers are running:
   ```bash
   python orchestrator_cli.py status
   ```
2. Verify watcher is enabled in config
3. Check watcher-specific logs for errors
4. Test data source (send test email, etc.)

### WhatsApp watcher not working

WhatsApp Web blocks headless browsers, so the watcher must run in visible mode:
- You'll see a browser window open
- Keep it running (can minimize)
- Session persists across restarts

To disable if not needed:
```json
{"processes": {"whatsapp": {"enabled": false}}}
```

## Authentication Setup

### Gmail Watcher
1. Enable Gmail API in Google Cloud Console
2. Create OAuth credentials
3. Run authentication: `python gmail_watcher.py`
4. Follow browser OAuth flow
5. Credentials saved in `watchers/credentials/gmail_token.json`

### Slack Watcher
1. Create Slack App at api.slack.com
2. Add OAuth scopes: channels:history, channels:read
3. Install app to workspace
4. Save credentials to `watchers/credentials/slack_credentials.json`

### Calendar Watcher
1. Enable Google Calendar API
2. Create OAuth credentials (same as Gmail)
3. Run authentication: `python calendar_watcher.py`
4. Credentials saved in `watchers/credentials/calendar_token.json`

### WhatsApp Watcher
1. No API setup required
2. First run: `python whatsapp_watcher.py --visible`
3. Scan QR code in browser to log in
4. Session persists in `watchers/whatsapp_session/`

### Xero Watcher
1. Create Xero App at developer.xero.com
2. Configure OAuth redirect URI
3. Run: `python watchers/xero_complete_auth_manual.py`
4. Complete 2FA setup if required
5. Credentials saved in `watchers/credentials/xero_credentials.json`

## Security

- All credentials stored locally in `watchers/credentials/` (gitignored)
- OAuth tokens refresh automatically
- Approval workflow prevents unauthorized actions
- Complete audit trail in activity logs
- No credentials stored in Obsidian vault

## Tech Stack

- **Knowledge Base:** Obsidian (local markdown)
- **Reasoning Engine:** Claude Code
- **Orchestration:** Python subprocess management
- **Watchers:** Python scripts with API integrations
- **Browser Automation:** Playwright (WhatsApp)
- **APIs:** Google (Gmail, Calendar), Slack, Xero
- **MCP Servers:** Model Context Protocol for actions

## Next Steps

### Enhance Your AI Employee

1. **Add More Watchers:**
   - Banking API integration
   - Twitter/X mentions
   - Instagram DMs
   - Facebook messages

2. **Automate More Actions:**
   - Auto-reply to common emails
   - Schedule social media posts
   - Generate weekly CEO briefings
   - Auto-categorize expenses

3. **Improve Intelligence:**
   - Better keyword detection
   - Priority classification
   - Context-aware responses
   - Multi-step task planning

4. **Scale Up:**
   - Deploy to cloud VM for 24/7 operation
   - Add team collaboration features
   - Integrate with more business tools
   - Build custom MCP servers

## Documentation

### Core Documentation
- **Quick Start:** `QUICKSTART.md` - Get started in 5 minutes
- **Architecture:** `ARCHITECTURE.md` - System architecture and design decisions
- **Lessons Learned:** `LESSONS_LEARNED.md` - Implementation insights and best practices
- **Complete Workflow:** `AI_EMPLOYEE_WORKFLOW.md` - Full system workflow
- **Requirements:** `Requirements1.md` - Full architectural specification

### Technical Documentation
- **Orchestration:** `watchers/README_ORCHESTRATION.md` - Orchestration system
- **Cross-Domain Integration:** `GOLD_TIER_REQUIREMENT_2_STATUS.md` - Personal + Business integration status
- **Audit Logging:** `GOLD_TIER_REQUIREMENT_9_STATUS.md` - Comprehensive audit logging status
- **Ralph Loop:** `GOLD_TIER_REQUIREMENT_10_STATUS.md` - Autonomous multi-step task completion
- **Audit Integration:** `AI_Employee_Vault/Logs/AUDIT_LOGGING_INTEGRATION_GUIDE.md` - How to add audit logging
- **Skills:** `.claude/skills/*/SKILL.md` - Individual skill documentation

## Support

- **Research Meetings:** Every Wednesday 10:00 PM on Zoom
- **GitHub Issues:** Report bugs and request features
- **Documentation:** Comprehensive docs in this repo
- **Community:** Panaversity Zoom sessions and YouTube

## License

This is a hackathon project for educational purposes. See individual component licenses for details.

---

**🎉 Your Personal AI Employee is Running 24/7!**

*Zero manual intervention required. Just review the Dashboard.md daily and approve sensitive actions.*

---

**Built with:** Claude Code, Obsidian, Python, Playwright, Google APIs, Slack API, Xero API

**Current Version:** Gold Tier - Fully Autonomous

**Last Updated:** 2026-01-14
