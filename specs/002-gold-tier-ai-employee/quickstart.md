# Gold Tier Quickstart Guide

**Feature**: 002-gold-tier-ai-employee (Gold Tier Personal AI Employee)
**Estimated Setup Time**: 2-3 hours
**Prerequisites**: Silver Tier (001) must be complete

This guide will help you set up Gold Tier Personal AI Employee with 6+ coordinated watchers, 6+ MCP servers, Ralph Wiggum autonomous loop, CEO briefing, and comprehensive audit logging.

---

## Prerequisites Checklist

Before starting Gold Tier setup, ensure you have:

- ✅ Silver Tier (001) fully operational (2+ watchers, 1+ MCP server, approval workflow)
- ✅ Python 3.13+ installed
- ✅ Node.js v24+ LTS installed
- ✅ Obsidian 1.10.6+ installed with vault at `C:\Users\[User]\Desktop\AI_Employee_Vault`
- ✅ Claude Code installed with active subscription (or Gemini API + Router)
- ✅ Stable internet connection (10+ Mbps recommended)
- ✅ 8GB RAM minimum (16GB recommended for 6 watchers)
- ✅ Windows 10/11+, macOS 12+, or Linux (Ubuntu 20.04+, Debian 11+)

---

## Phase 1: Orchestrator Setup (30 minutes)

### Step 1.1: Create Orchestrator Configuration

Create `watchers/orchestrator_config.json`:

```json
{
  "watchers": {
    "gmail_watcher": {
      "enabled": true,
      "script": "watchers/gmail_watcher.py",
      "check_interval_seconds": 120,
      "priority": "high"
    },
    "whatsapp_watcher": {
      "enabled": true,
      "script": "watchers/whatsapp_watcher.py",
      "check_interval_seconds": 30,
      "priority": "urgent"
    },
    "xero_watcher": {
      "enabled": true,
      "script": "watchers/xero_watcher.py",
      "check_interval_seconds": 300,
      "priority": "high"
    },
    "calendar_watcher": {
      "enabled": true,
      "script": "watchers/calendar_watcher.py",
      "check_interval_seconds": 600,
      "priority": "medium"
    },
    "slack_watcher": {
      "enabled": true,
      "script": "watchers/slack_watcher.py",
      "check_interval_seconds": 60,
      "priority": "medium"
    },
    "filesystem_watcher": {
      "enabled": true,
      "script": "watchers/filesystem_watcher.py",
      "check_interval_seconds": 0,
      "priority": "low",
      "realtime": true
    }
  },
  "health_check_interval_seconds": 60,
  "restart_on_failure": true,
  "max_restart_attempts_per_hour": 3
}
```

### Step 1.2: Start Orchestrator

Run Orchestrator (launches all 6 watchers):

```bash
# Windows
python watchers/orchestrator.py start

# Linux/macOS
python3 watchers/orchestrator.py start
```

**Verify**: Check that all 6 watchers are running:

```bash
python watchers/orchestrator_cli.py status
```

Expected output:
```
Orchestrator: Running (PID: 12345)
Watchers:
  ✓ gmail_watcher: Running (PID: 12346, last check: 2026-01-17 12:34:56)
  ✓ whatsapp_watcher: Running (PID: 12347, last check: 2026-01-17 12:34:50)
  ✓ xero_watcher: Running (PID: 12348, last check: 2026-01-17 12:34:40)
  ✓ calendar_watcher: Running (PID: 12349, last check: 2026-01-17 12:34:30)
  ✓ slack_watcher: Running (PID: 12350, last check: 2026-01-17 12:34:25)
  ✓ filesystem_watcher: Running (PID: 12351, real-time)
```

---

## Phase 2: MCP Server Setup (60-90 minutes)

### Step 2.1: Install MCP Server Dependencies

Navigate to each MCP server directory and install dependencies:

```bash
# Gmail MCP
cd mcp-servers/gmail-mcp
npm install
npm run build

# Xero MCP
cd ../xero-mcp
npm install
npm run build

# LinkedIn MCP
cd ../linkedin-mcp
npm install
npm run build

# X Poster (Twitter/X)
cd ../x-poster
npm install
npm run build

# Facebook MCP
cd ../facebook-mcp
npm install
npm run build

# Instagram MCP
cd ../instagram-mcp
npm install
npm run build
```

### Step 2.2: Configure OAuth Credentials

Create `.env` file in each MCP server directory with OAuth credentials:

**Gmail MCP** (`mcp-servers/gmail-mcp/.env`):
```env
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:3000/callback
```

**Xero MCP** (`mcp-servers/xero-mcp/.env`):
```env
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_client_secret
XERO_REDIRECT_URI=http://localhost:3000/callback
XERO_TENANT_ID=your_xero_tenant_id
```

**LinkedIn MCP** (`mcp-servers/linkedin-mcp/.env`):
```env
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:3000/callback
```

**X Poster** (`mcp-servers/x-poster/.env`):
```env
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
```

**Facebook MCP** (`mcp-servers/facebook-mcp/.env`):
```env
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_PAGE_ID=your_facebook_page_id
```

**Instagram MCP** (`mcp-servers/instagram-mcp/.env`):
```env
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

### Step 2.3: Test MCP Servers

Test each MCP server individually:

```bash
# Test Gmail MCP
cd mcp-servers/gmail-mcp
node dist/index.js test

# Test Xero MCP
cd ../xero-mcp
node dist/index.js test

# (Repeat for all 6 MCP servers)
```

**Expected Output**: Each MCP server should respond with tool definitions and success message.

---

## Phase 3: Configure Claude Code MCP Integration (15 minutes)

### Step 3.1: Update MCP Configuration

Edit `~/.config/claude-code/mcp.json` (Windows: `%APPDATA%\claude-code\mcp.json`):

```json
{
  "mcpServers": {
    "gmail-mcp": {
      "command": "node",
      "args": ["C:/Users/[User]/Desktop/AI_Employee_Vault/mcp-servers/gmail-mcp/dist/index.js"],
      "env": {
        "GMAIL_CLIENT_ID": "your_client_id.apps.googleusercontent.com",
        "GMAIL_CLIENT_SECRET": "your_client_secret"
      }
    },
    "xero-mcp": {
      "command": "node",
      "args": ["C:/Users/[User]/Desktop/AI_Employee_Vault/mcp-servers/xero-mcp/dist/index.js"],
      "env": {
        "XERO_CLIENT_ID": "your_xero_client_id",
        "XERO_CLIENT_SECRET": "your_xero_client_secret",
        "XERO_TENANT_ID": "your_xero_tenant_id"
      }
    },
    "linkedin-mcp": {
      "command": "node",
      "args": ["C:/Users/[User]/Desktop/AI_Employee_Vault/mcp-servers/linkedin-mcp/dist/index.js"],
      "env": {
        "LINKEDIN_CLIENT_ID": "your_linkedin_client_id",
        "LINKEDIN_CLIENT_SECRET": "your_linkedin_client_secret"
      }
    },
    "x-poster": {
      "command": "node",
      "args": ["C:/Users/[User]/Desktop/AI_Employee_Vault/mcp-servers/x-poster/dist/index.js"],
      "env": {
        "TWITTER_USERNAME": "your_twitter_username",
        "TWITTER_PASSWORD": "your_twitter_password"
      }
    },
    "facebook-mcp": {
      "command": "node",
      "args": ["C:/Users/[User]/Desktop/AI_Employee_Vault/mcp-servers/facebook-mcp/dist/index.js"],
      "env": {
        "FACEBOOK_APP_ID": "your_facebook_app_id",
        "FACEBOOK_APP_SECRET": "your_facebook_app_secret",
        "FACEBOOK_PAGE_ID": "your_facebook_page_id"
      }
    },
    "instagram-mcp": {
      "command": "node",
      "args": ["C:/Users/[User]/Desktop/AI_Employee_Vault/mcp-servers/instagram-mcp/dist/index.js"],
      "env": {
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": "your_instagram_business_account_id",
        "FACEBOOK_APP_ID": "your_facebook_app_id",
        "FACEBOOK_APP_SECRET": "your_facebook_app_secret"
      }
    }
  }
}
```

### Step 3.2: Restart Claude Code

Restart Claude Code to load MCP servers:

```bash
# Windows: Close and reopen Claude Code
# Linux/macOS: pkill -f "Claude Code" && open -a "Claude Code"
```

**Verify**: In Claude Code, invoke any MCP tool:

```
/test gmail-mcp send_email
```

Expected output: MCP server responds with tool definition.

---

## Phase 4: Ralph Wiggum Loop Setup (20 minutes)

### Step 4.1: Install Ralph Wiggum Stop Hook

Download and install Ralph Wiggum Stop Hook (see official repo):

```bash
# Clone Ralph Wiggum repo
git clone https://github.com/example/ralph-wiggum.git .claude/plugins/ralph-wiggum

# Install dependencies
cd .claude/plugins/ralph-wiggum
npm install
npm run build
```

### Step 4.2: Configure Ralph Loop

Create `.claude/plugins/ralph-wiggum/config.json`:

```json
{
  "enabled": true,
  "max_iterations": 10,
  "max_duration_minutes": 30,
  "stuck_detection_threshold": 3,
  "completion_criteria": "file_movement",
  "completion_target_folder": "/Done"
}
```

### Step 4.3: Test Ralph Loop

Create test Plan.md in `/Plans/active/`:

```markdown
# Test Plan: Ralph Loop Verification

## Objective
Verify Ralph loop autonomously completes 3 steps without additional prompts.

## Steps
- [ ] Step 1: Create test file in /Inbox
- [ ] Step 2: Move test file to /Needs_Action
- [ ] Step 3: Move test file to /Done

## Completion Criteria
All steps completed, test file in /Done.
```

In Claude Code, invoke Ralph loop:

```
/ralph Execute plan: /Plans/active/TEST_RALPH_LOOP.md until completion
```

**Expected Output**: Claude autonomously completes all 3 steps without additional prompts, then exits.

---

## Phase 5: CEO Briefing Setup (30 minutes)

### Step 5.1: Configure Scheduled Task

**Windows** (Task Scheduler):

Create `scripts/setup_ceo_briefing.bat`:

```batch
schtasks /create /tn "CEO Briefing" /tr "python C:\Users\[User]\Desktop\AI_Employee_Vault\scripts\trigger_ceo_briefing.py" /sc weekly /d SUN /st 07:00
```

**Linux/macOS** (cron):

```bash
# Edit crontab
crontab -e

# Add line
0 7 * * 0 cd /home/user/Desktop/AI_Employee_Vault && python3 scripts/trigger_ceo_briefing.py
```

### Step 5.2: Create Business Goals

Create `AI_Employee_Vault/Business_Goals.md`:

```markdown
# Business Goals

## Q1 2026 Revenue Target
- **Metric Type**: Revenue
- **Target Value**: $100,000
- **Current Value**: $85,000
- **Unit**: $
- **Period**: Quarterly
- **Start Date**: 2026-01-01
- **End Date**: 2026-03-31
- **Status**: at_risk
- **Alert Threshold**: $90,000

## Monthly Invoice Payment Rate
- **Metric Type**: Invoice Payment Rate
- **Target Value**: 90%
- **Current Value**: 85%
- **Unit**: %
- **Period**: Monthly
- **Start Date**: 2026-01-01
- **End Date**: 2026-01-31
- **Status**: on_track
- **Alert Threshold**: 80%
```

### Step 5.3: Test CEO Briefing

Manually trigger CEO briefing:

```bash
python scripts/trigger_ceo_briefing.py
```

**Expected Output**: CEO briefing created at `/Briefings/YYYY-MM-DD_Monday_Briefing.md` with sections:
- Executive Summary
- Weekly Revenue (total + MTD vs target + trend)
- Completed Tasks (count by category)
- Bottlenecks
- Proactive Suggestions

---

## Phase 6: Audit Logging Setup (15 minutes)

### Step 6.1: Configure Log Rotation

Create `scripts/setup_log_rotation.bat` (Windows) or `.sh` (Linux/macOS):

**Windows**:
```batch
schtasks /create /tn "Log Rotation" /tr "python C:\Users\[User]\Desktop\AI_Employee_Vault\scripts\rotate_logs.py" /sc daily /st 03:00
```

**Linux/macOS**:
```bash
# Add to crontab
0 3 * * * cd /home/user/Desktop/AI_Employee_Vault && python3 scripts/rotate_logs.py
```

### Step 6.2: Verify Audit Logging

Trigger a test action (send email via approval workflow):

1. Move approval file to `/Approved`
2. Approval-processor executes action via Gmail MCP
3. Check `/Logs/mcp_actions_YYYY-MM-DD.json`

**Expected Output**: Audit log entry with all required fields:
```json
{
  "timestamp": "2026-01-17T12:34:56Z",
  "action_type": "external_action",
  "actor": "approval-processor",
  "target": "recipient@example.com",
  "parameters": {
    "subject": "Test Email",
    "body": "This is a test email"
  },
  "approval_status": "approved",
  "result": "success",
  "file_created": "/Done/EMAIL_test_20260117_123456.md"
}
```

---

## Phase 7: Auto-Start Configuration (15 minutes)

### Step 7.1: Configure Auto-Start on Boot

**Windows** (Task Scheduler):

Run `scripts/setup_auto_start.bat`:

```batch
schtasks /create /tn "AI Employee Orchestrator" /tr "python C:\Users\[User]\Desktop\AI_Employee_Vault\watchers\orchestrator.py start" /sc onlogon /ru "[User]"
schtasks /create /tn "AI Employee Watchdog" /tr "python C:\Users\[User]\Desktop\AI_Employee_Vault\watchers\watchdog.py" /sc onlogon /ru "[User]"
```

**Linux/macOS** (systemd or cron):

Create systemd service (`/etc/systemd/system/ai-employee.service`):
```ini
[Unit]
Description=AI Employee Orchestrator
After=network.target

[Service]
Type=simple
User=[User]
WorkingDirectory=/home/user/Desktop/AI_Employee_Vault
ExecStart=/usr/bin/python3 watchers/orchestrator.py start
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable ai-employee.service
sudo systemctl start ai-employee.service
```

### Step 7.2: Verify Auto-Start

Reboot computer and verify:

```bash
python watchers/orchestrator_cli.py status
```

**Expected Output**: All 6 watchers running after boot.

---

## Verification Checklist

After completing all phases, verify Gold Tier is operational:

- ✅ Orchestrator launches all 6 watchers
- ✅ All 6 watchers detecting events (check log files in `watchers/logs/`)
- ✅ Action files created in `/Needs_Action` with valid YAML frontmatter
- ✅ All 6 MCP servers respond to tool invocations
- ✅ Claude Code can invoke MCP tools
- ✅ Approval workflow working (/Pending_Approval → /Approved → /Done)
- ✅ Ralph loop autonomously completes multi-step tasks
- ✅ CEO briefing generates weekly (or manually triggered)
- ✅ Audit logs created in `/Logs/` with all required fields
- ✅ Dashboard.md updates within 5 minutes of significant events
- ✅ Auto-start on boot configured and working

---

## Troubleshooting

### Issue: Orchestrator fails to start watchers

**Solution**: Check `orchestrator_config.json` syntax. Verify watcher scripts exist at specified paths. Check Python dependencies installed (`pip install -r watchers/requirements.txt`).

### Issue: MCP server not responding

**Solution**: Verify OAuth credentials in `.env` files. Check MCP server built (`npm run build`). Restart Claude Code to reload MCP configuration.

### Issue: Ralph loop not stopping

**Solution**: Check completion criteria in Ralph config. Verify target file moved to `/Done`. If stuck, kill Claude Code process and restart.

### Issue: CEO briefing not generating

**Solution**: Verify scheduled task configured correctly. Check `Business_Goals.md` exists. Manually run `trigger_ceo_briefing.py` to test.

### Issue: Audit logs not created

**Solution**: Verify `/Logs/` directory exists. Check MCP server logging configuration. Test with manual action (send email) to trigger log entry.

---

## Next Steps

After Gold Tier setup is complete:

1. **Monitor System**: Check Dashboard.md daily for system status
2. **Process Approvals**: Review `/Pending_Approval` folder regularly
3. **Review Briefings**: Read CEO briefings every Monday morning
4. **Audit Logs**: Periodically review `/Logs/` for errors and patterns
5. **Tune Thresholds**: Adjust `Business_Goals.md` targets based on actual performance

---

## Support Resources

- **Constitution**: `.specify/memory/constitution.md` (architectural principles)
- **Spec**: `specs/002-gold-tier-ai-employee/spec.md` (requirements)
- **Plan**: `specs/002-gold-tier-ai-employee/plan.md` (implementation details)
- **Data Model**: `specs/002-gold-tier-ai-employee/data-model.md` (entity definitions)
- **MCP Contracts**: `specs/002-gold-tier-ai-employee/contracts/` (tool schemas)

---

## Upgrade to Platinum Tier

When ready for Platinum Tier (24/7 cloud deployment + local specialization):

1. Review Platinum Tier requirements in `Requirements2.md`
2. Set up cloud VM (Oracle Cloud Free Tier or AWS)
3. Deploy Cloud Agent (email triage, social drafts)
4. Configure vault synchronization (Git or Syncthing)
5. Implement claim-by-move rule (`/In_Progress/<agent>/`)
6. Separate Cloud and Local work zones
7. Estimate time: 60+ hours

---

**Congratulations!** You now have a fully autonomous Gold Tier Personal AI Employee with 6+ coordinated watchers, 6+ MCP servers, Ralph Wiggum autonomous loop, CEO briefing, and comprehensive audit logging.

**Estimated Time Savings**: 85-90% vs human FTE (Digital FTE works 168 hours/week vs human 40 hours/week)

**Next Review**: Monitor system for 1 week, then tune thresholds and configurations based on actual performance.
