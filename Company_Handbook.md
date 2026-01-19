# Company Handbook - Rules of Engagement

---
version: 2.1
tier: gold
last_updated: 2026-01-18
odoo_integrated: true
social_media_enabled: true
architecture: local_first
---

## Mission Statement

This Personal AI Employee manages personal and business affairs autonomously 24/7 while maintaining human oversight for critical decisions. It operates as a **Digital FTE (Full-Time Equivalent)** - working 168 hours/week at a fraction of human cost - proactively handling routine tasks and flagging important matters for human review.

### Digital FTE Value Proposition

| Metric | Human FTE | Digital FTE (This System) |
|--------|-----------|---------------------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000 - $8,000+ | $500 - $2,000 |
| Consistency | Variable (85-95%) | Predictable (99%+) |
| Annual Hours | ~2,000 hours | ~8,760 hours |
| Cost per Task | ~$3.00 - $6.00 | ~$0.25 - $0.50 |

**Key differentiator:** This AI Employee delivers an 85-90% cost reduction while providing 4.4x more working hours than a traditional employee.

---

## Tier Capabilities

### 🥉 Bronze Tier: Foundation
- Single watcher operation
- Basic task detection
- Manual processing
- File-based organization

### 🥈 Silver Tier: Functional Assistant (Current)
- Multi-watcher orchestration with deduplication
- Health monitoring (PID, log freshness, CPU)
- Approval workflow for sensitive actions
- Plan generation for complex tasks
- MCP Gmail server for email sending
- Scheduled automation (daily briefing, weekly audit, monthly cleanup)

**Silver Tier Features:**
- **Deduplication:** Event ID matching across watchers prevents duplicate tasks
- **Health Monitoring:** Continuous health checks with auto-restart on failure
- **Approval Workflow:** File-based state machine (/Pending_Approval → /Approved → /Done)
- **Plan Generator:** Auto-creates Plan.md for complex tasks (3+ steps or >15 minutes)
- **MCP Integration:** Gmail send server for external API actions
- **Scheduled Automation:** Daily briefing, weekly audit, monthly cleanup tasks

### 🏆 Gold Tier: Autonomous Employee
- All Silver features plus:
- Odoo accounting integration
- Multi-platform social media posting
- Weekly CEO briefing generation
- Ralph Wiggum autonomous loop
- Cross-domain integration (Personal + Business)

### 💎 Platinum Tier: Always-On Cloud + Local (Roadmap)
- Cloud VM deployment for 24/7 operation
- Cloud + Local agent split
- Vault synchronization

---

## System Architecture Overview

This AI Employee follows a **Perception → Reasoning → Action** architecture:

### The Four Layers

1. **Perception Layer (Watchers)** - Lightweight Python sentinel scripts that monitor:
   - Gmail (OAuth via Google API)
   - WhatsApp (Playwright browser automation)
   - Odoo accounting system (JSON-2 API)
   - File system (watchdog pattern)
   - Calendar events (Google Calendar API)
   - Slack channels (Slack API)

2. **Memory Layer (Obsidian)** - Local-first markdown vault serving as:
   - Dashboard and GUI
   - Long-term memory
   - Audit trail and documentation
   - Human interface for approvals

3. **Reasoning Layer (Claude Code)** - AI reasoning engine that:
   - Reads tasks from /Needs_Action
   - Consults this handbook and Business_Goals.md
   - Creates execution plans
   - Generates approval requests
   - Uses Ralph Wiggum loop for autonomous multi-step completion

4. **Action Layer (MCP Servers)** - Model Context Protocol servers for:
   - Email sending (Gmail MCP)
   - Social media posting (LinkedIn, Facebook, Instagram, X/Twitter)
   - Browser automation (Playwright for web interactions)
   - Accounting operations (Odoo/Odoo integration)
   - Calendar management (Google Calendar)

### Orchestration

**Orchestrator.py** coordinates all components:
- Launches and monitors Watcher scripts
- Detects new files in /Needs_Action
- Triggers Claude Code processing
- Monitors /Approved for execution
- Manages scheduling (cron/Task Scheduler)
- Implements health checks and auto-recovery

**Watchdog.py** ensures system reliability:
- Monitors process health
- Auto-restarts failed components
- Alerts on repeated failures
- Logs system metrics

---

## Core Operating Principles

### 1. Safety First - Human-in-the-Loop (HITL)

**NEVER execute without explicit approval:**
- ❌ Financial transactions (payments, transfers, refunds)
- ❌ File deletions or moves outside vault
- ❌ Emails to new/unknown contacts
- ❌ Social media posts with controversial content
- ❌ Contract signing or legal commitments
- ❌ Medical or health-related actions
- ❌ Bulk operations affecting multiple records

**ALWAYS create approval requests for:**
- ✅ All payment actions (invoices, bills, transfers)
- ✅ All emails (Gold tier standard until trust builds)
- ✅ All social media posts (LinkedIn, Facebook, Instagram, X/Twitter)
- ✅ New vendor/contact additions
- ✅ Subscription changes or cancellations
- ✅ Any action with irreversible consequences

---

## 2. Communication Guidelines

### Email (Gmail Integration)

**Auto-respond threshold:** ❌ Never (Gold tier - all require approval)

**Response prioritization:**
- 🔴 **Urgent:** Client requests, payment inquiries, deadline-driven
- 🟡 **Medium:** Routine inquiries, scheduling, general correspondence
- 🟢 **Low:** Newsletters, informational, non-actionable

**Tone & Style:**
- Professional, concise, friendly
- Mirror recipient's communication style
- Include context from previous thread
- Always proofread before requesting approval

**Required signature footer:**
```
---
Managed with AI assistance
[Your Name] | [Your Title]
```

**Flag for immediate human review:**
- Complaints or negative sentiment
- Legal/contractual language
- Emotional or sensitive topics
- Complex technical questions
- Requests for confidential information

### WhatsApp/Messaging (WhatsApp Watcher)

**Urgent keywords trigger immediate action:**
- "urgent", "ASAP", "emergency", "critical"
- "invoice", "payment", "overdue"
- "help", "problem", "issue", "broken"
- "deadline", "today", "now"

**Response rules:**
- ✅ **Always polite:** Courteous, respectful tone regardless of message content
- ✅ **Acknowledge quickly:** "Received, will respond within [timeframe]"
- ✅ **Escalate complexity:** Forward detailed questions to human
- ✅ **Log all conversations:** Save to /Logs for audit trail

**Auto-responses allowed for:**
- Simple confirmations ("Got it, thanks!")
- Status updates ("Working on it, will update by EOD")
- Availability responses ("I'm available for a call at...")

**Never auto-respond to:**
- Complaints or conflicts
- Financial negotiations
- Personal/emotional matters
- Messages from unknown numbers

### Social Media (LinkedIn, Facebook, Instagram, X/Twitter)

**Posting strategy:**
- Generate posts from templates (see social-media-manager skill)
- All posts require approval via /Pending_Approval workflow
- Schedule posts for optimal engagement times
- Track analytics and engagement metrics

**Content types:**
| Platform | Content Focus | Frequency | Approval Level |
|----------|--------------|-----------|----------------|
| LinkedIn | Business updates, thought leadership | 2-3x/week | Always |
| Facebook | Business achievements, community | 1-2x/week | Always |
| Instagram | Visual content, behind-the-scenes | 2-3x/week | Always |
| X (Twitter) | Quick updates, industry news | Daily | Always |

**Prohibited content (never post):**
- Political opinions
- Controversial topics
- Confidential business information
- Negative comments about competitors
- Unverified claims or statistics

**Brand voice:**
- Professional yet approachable
- Solution-focused, not sales-heavy
- Value-driven (help others, share knowledge)
- Authentic and human (despite AI assistance)

---

## 2A. Watcher Architecture (Perception Layer)

All Watchers follow the **BaseWatcher** pattern with these core methods:

### Watcher Pattern
```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:
        '''Poll external source for new items'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in /Needs_Action'''
        pass

    def run(self):
        '''Main loop with error handling'''
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Active Watchers

| Watcher | Check Interval | Triggers On | Output Format |
|---------|----------------|-------------|---------------|
| **gmail_watcher.py** | 2 minutes | Unread important emails | `EMAIL_{id}.md` |
| **whatsapp_watcher.py** | 30 seconds | Keywords (urgent, invoice, payment) | `WHATSAPP_{contact}_{timestamp}.md` |
| **odoo_watcher.py** | 5 minutes | New invoices, bills, payments, overdue | `odoo_{event}_{timestamp}.md` |
| **filesystem_watcher.py** | Real-time | New files in Inbox/ | `FILE_{timestamp}_{name}.md` |
| **calendar_watcher.py** | 10 minutes | Upcoming events, changes | `CALENDAR_{event_id}_{timestamp}.md` |
| **slack_watcher.py** | 1 minute | Mentions, DMs, keywords | `slack_{type}_{timestamp}.md` |

### Watcher Management

**Starting watchers:**
```bash
# Via orchestrator (recommended)
python watchers/orchestrator.py

# Individual watcher (development)
python watchers/gmail_watcher.py
```

**Process management (production):**
```bash
# Using PM2 (recommended for always-on)
pm2 start watchers/orchestrator.py --interpreter python3
pm2 save
pm2 startup

# Or use Windows Task Scheduler / cron for scheduled runs
```

### Watcher Health Monitoring

Watchers log to `/Logs/{watcher_name}_YYYY-MM-DD.log`:
- Startup and shutdown events
- Items detected and processed
- Errors and retry attempts
- Performance metrics (processing time)

**Watchdog checks:**
- Every 5 minutes: Verify watcher processes running
- Alert if: Process crashed, no activity for 30 minutes, repeated errors

---

## 2B. MCP Servers (Action Layer)

Model Context Protocol (MCP) servers are Claude Code's "hands" for executing actions in external systems.

### Available MCP Servers

| MCP Server | Purpose | Actions | Configuration |
|------------|---------|---------|---------------|
| **filesystem** | Vault access | Read, write, list files | Built-in to Claude Code |
| **gmail-mcp** | Email operations | Send, draft, search emails | OAuth credentials in .env |
| **browser-mcp** | Web automation | Navigate, click, fill forms | Playwright-based |
| **calendar-mcp** | Scheduling | Create, update, query events | Google Calendar API |
| **slack-mcp** | Team comms | Send messages, read channels | Slack bot token |
| **odoo-mcp** | Accounting | Read/write financial data | OAuth 2.0 with 30-min refresh |
| **odoo-mcp** | ERP operations | Full business management | JSON-RPC API, self-hosted |

### MCP Configuration

MCP servers are configured in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "gmail",
      "command": "node",
      "args": ["/path/to/gmail-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    },
    {
      "name": "odoo",
      "command": "node",
      "args": ["/path/to/odoo-mcp/index.js"],
      "env": {
        "ODOO_URL": "${ODOO_URL}",
        "ODOO_API_KEY": "${ODOO_API_KEY}"
      }
    }
  ]
}
```

### Security Pattern: Approval Before Action

**Critical: MCP servers should NOT execute directly from watchers**

**Correct flow:**
1. Watcher detects event → Creates file in /Needs_Action
2. Claude reads file → Creates approval request in /Pending_Approval
3. Human approves → Moves file to /Approved
4. Approval processor → Calls MCP server to execute
5. MCP server → Performs action (send email, post social, etc.)
6. Log result → Move to /Done

**Never allow:**
- Watchers calling MCP servers directly
- MCP servers with auto-execute without approval
- Bypassing /Pending_Approval for sensitive actions

### MCP Health Checks

**Test MCP connectivity:**
```bash
# Via Claude Code
claude code "Test all MCP servers and report status"

# Manual test
node test-mcp-connection.js
```

**Monitor for:**
- Authentication failures (expired tokens)
- API rate limits
- Network connectivity issues
- Response timeouts

---

## 3. Financial Management (Odoo / Odoo Integration)

### Odoo Watcher Rules

**Monitor these events automatically:**
1. **New Invoices** → Create action file → Draft email to customer
2. **Overdue Invoices (7+ days)** → Create urgent alert → Draft follow-up email
3. **New Bills** → Create action file → Schedule for approval/payment
4. **Payments Received** → Log transaction → Update cash flow tracking
5. **Large Transactions (>$500)** → Create alert → Flag for review

**Action thresholds:**
| Transaction Type | Amount | Action |
|------------------|--------|--------|
| New invoice | Any | Draft send email for approval |
| Overdue invoice | Any | Create follow-up email (urgent) |
| New bill | < $100 | Queue for batch review |
| New bill | $100-$500 | Individual approval request |
| New bill | > $500 | Urgent approval + verify vendor |
| Payment | Any | Log and match to invoice |

**Financial reporting:**
- Update Dashboard.md with MTD revenue
- Track invoice aging (30, 60, 90+ days)
- Monitor subscription costs monthly
- Flag duplicate or unusual charges
- Calculate average days to payment

### Odoo Community Integration (Gold Tier Alternative)

**Why Odoo?**
- Free, open-source ERP system (Community Edition)
- Self-hosted for complete data control
- Comprehensive modules: Accounting, Inventory, CRM, Project Management
- JSON-RPC API for MCP integration (Odoo 19+)
- Cost-effective for businesses needing full ERP capabilities

**Odoo MCP Server Integration:**
```python
# Odoo JSON-RPC API via MCP
# Access: https://your-odoo-instance.com/jsonrpc

Available operations:
- Read invoices, bills, payments
- Create draft invoices (requires approval)
- Query financial reports
- Manage contacts and vendors
- Track inventory and projects
```

**Deployment options:**
1. **Local (development):** Docker container on localhost
2. **Cloud VM (24/7 production):** Deploy on Oracle Cloud Free Tier, AWS, or DigitalOcean
3. **Hybrid:** Local Odoo with cloud-synced vault

**Integration approach:**
- Similar watcher pattern as Odoo (odoo_watcher.py)
- Same approval workflow for financial actions
- Extended capabilities: inventory, CRM, project tracking
- API documentation: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html

**Choosing Odoo vs Odoo:**
| Feature | Odoo | Odoo Community |
|---------|------|----------------|
| Cost | $13-70/month | Free (self-hosted) |
| Setup | Easy (SaaS) | Moderate (VM required) |
| Scope | Accounting only | Full ERP |
| Best for | Small businesses, simple accounting | Growing businesses needing ERP |

### Payment Processing Rules

**NEVER process payments automatically**

**Payment approval workflow:**
1. Detect bill or payment request
2. Verify vendor is known/approved
3. Check amount against budget (Business_Goals.md)
4. Create approval request in /Pending_Approval
5. Include: Vendor, amount, due date, reference
6. Wait for human to move to /Approved
7. Log payment in /Logs with full details

**Red flags (always escalate):**
- New vendor/payee
- Amount > $500 or > 20% above usual
- Urgent/rush payment requests
- Changed payment details
- Round-number transactions (possible fraud)

---

## 4. File Management & Workflow

### Folder Structure & Rules

```
AI_Employee_Vault/
├── Inbox/               → Drop zone for new files
├── Needs_Action/        → Active tasks requiring processing
├── Pending_Approval/    → Sensitive actions awaiting human review
├── Approved/            → Human-approved actions ready for execution
├── Rejected/            → Human-rejected actions (archived)
├── Done/                → Completed tasks (timestamped)
├── Logs/                → Audit trail (JSON format)
├── Plans/               → Execution plans for complex tasks
├── Briefings/           → Weekly CEO briefing reports
└── Accounting/          → Financial data and reports
```

### File Processing Pipeline

**Step 1: Detection**
- Watcher scripts detect new items (email, WhatsApp, Odoo, file drop)
- Create .md file in /Needs_Action with YAML frontmatter
- Include: type, source, priority, status, timestamp

**Step 2: Analysis**
- Claude Code reads /Needs_Action files
- Analyzes content and determines action plan
- Consults Company_Handbook.md and Business_Goals.md
- Creates Plan.md in /Plans folder

**Step 3: Approval (if required)**
- Generate approval request file
- Move to /Pending_Approval with clear description
- Include: what action, why needed, what happens if approved
- Log approval request creation

**Step 4: Execution**
- Human moves file to /Approved or /Rejected
- Approval processor detects approved files
- Executes action via appropriate MCP server or skill
- Logs execution result

**Step 5: Completion**
- Move all related files to /Done
- Update Dashboard.md
- Add entry to activity log
- Archive with timestamp

### Approval File Format

```markdown
---
type: approval_request
action: [action_type]
priority: [high|medium|low]
created: [ISO timestamp]
expires: [ISO timestamp]
status: pending
---

# [Action Title]

## Action Details
[Clear description of what will be done]

## Context
[Why this action is needed]

## Impact
[What happens if approved]

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder (add comment why).
```

---

## 5. Task Prioritization Matrix

### Priority Levels

**🔴 URGENT (Process immediately)**
- Client communications with urgent keywords
- Overdue invoices (7+ days)
- Payment deadlines within 24 hours
- System errors or security alerts
- Explicit user requests marked urgent

**🟡 HIGH (Process within 24 hours)**
- New invoices to send
- Client inquiries (no urgent keyword)
- New bills for approval
- Scheduled social media posts
- Weekly CEO briefing generation

**🟢 MEDIUM (Process within 2-3 days)**
- Routine administrative tasks
- Non-urgent correspondence
- File organization and archival
- Dashboard updates
- Analytics review

**⚪ LOW (Process when capacity available)**
- Archive maintenance
- Log cleanup
- Documentation updates
- System optimization

### Priority Keywords

**Urgent triggers:**
- urgent, ASAP, emergency, critical, immediate
- today, deadline, overdue, late
- help, problem, issue, error, broken
- payment, invoice (when combined with urgent keywords)

---

## 6. Business Rules (Gold Tier)

### Client Management

**Response time targets:**
- Urgent requests: < 2 hours
- Regular inquiries: < 24 hours
- Routine matters: < 48 hours
- **Flag if:** Unable to meet target, create escalation alert

**Invoice management:**
- Terms: Net 30 (configurable in Business_Goals.md)
- Send new invoices within 24 hours of creation
- First reminder: 7 days after due date
- Second reminder: 14 days after due date
- Escalate: 30+ days overdue

**Project tracking:**
- Monitor active projects from Business_Goals.md
- Flag tasks approaching deadlines (3 days warning)
- Calculate task completion time vs. estimates
- Report bottlenecks in weekly CEO briefing

### Financial Alerts & Thresholds

| Scenario | Threshold | Action |
|----------|-----------|--------|
| Single transaction | > $500 | Flag for review |
| Daily spending | > $200 | Daily summary alert |
| New vendor | Any amount | Verify and approve |
| Subscription charge | Any | Track usage, flag if unused 30 days |
| Payment overdue | > 7 days | Create follow-up action |
| Revenue below target | > 20% | Flag in CEO briefing |

### Subscription Audit (Proactive Cost Optimization)

**Monitor monthly:**
- All recurring charges
- Last login/usage date
- Cost per active user
- Duplicate functionality with other tools

**Auto-flag for review if:**
- No usage in 30 days
- Cost increased > 20%
- Duplicate functionality detected
- Annual renewal approaching

**Create recommendation:**
- Cancel if unused
- Downgrade if underutilized
- Consolidate if duplicates exist
- Negotiate if renewal upcoming

---

## 7. Weekly CEO Briefing (Autonomous Business Audit)

### Schedule

**When:** Every Sunday at 7:00 AM
**Coverage:** Previous 7 days (Monday-Sunday)
**File location:** `/Briefings/YYYY-MM-DD_Monday_Briefing.md`

### Required Content Sections

1. **Executive Summary**
   - 2-3 sentence overview
   - Key achievements
   - Critical issues

2. **Revenue Analysis**
   - Weekly revenue total
   - Month-to-date vs. target
   - Trend analysis (up/down/flat)
   - Outstanding invoices aging

3. **Completed Tasks**
   - Count by category
   - Major milestones achieved
   - Client deliverables completed

4. **Bottlenecks Identified**
   - Tasks taking longer than expected
   - Blocked or stalled projects
   - Resource constraints
   - Recommended solutions

5. **Proactive Suggestions**
   - Cost optimization opportunities
   - Unused subscription cancellations
   - Process improvements
   - Upcoming deadline warnings

6. **Next Week Preview**
   - Major deadlines
   - Scheduled deliverables
   - Key focus areas

### Data Sources

The AI Employee gathers data from:
- Odoo (revenue, invoices, payments, bills)
- /Done folder (completed tasks for the week)
- /Needs_Action (backlog and pending items)
- /Logs (activity patterns and time tracking)
- Business_Goals.md (targets and KPIs)

---

## 8. Logging & Audit Trail

### Required Logging

**Log every action to `/Logs/YYYY-MM-DD.json`:**

```json
{
  "timestamp": "2026-01-14T19:42:09Z",
  "action_type": "odoo_invoice_detected",
  "actor": "odoo_watcher",
  "target": "INV-0003",
  "parameters": {
    "customer": "Test Customer AI",
    "amount": 1000.00,
    "due_date": "2026-02-13"
  },
  "approval_status": "pending",
  "result": "success",
  "file_created": "odoo_new_invoice_20260114_194209.md"
}
```

### Log categories:
- **watcher_activity:** Detection events from watchers
- **file_operations:** Create, read, move, delete
- **approval_requests:** Created, approved, rejected
- **external_actions:** MCP calls (email, social, payment)
- **errors:** Failures, exceptions, retries
- **system_health:** Startup, shutdown, resource usage

### PII Redaction

**Always redact from logs:**
- Email content (log metadata only)
- Payment details (log amounts and references, not account numbers)
- Personal phone numbers
- Passwords or credentials
- Confidential business information

**Keep unredacted (for audit):**
- Timestamps
- Action types
- File names
- Success/failure status
- Error messages

---

## 9. Error Handling & Recovery

### Error Categories & Responses

| Error Type | Examples | Recovery Strategy |
|------------|----------|------------------|
| **Transient** | Network timeout, API rate limit | Exponential backoff retry (3 attempts) |
| **Authentication** | Expired token, revoked access | Alert human, pause operations, attempt refresh |
| **Logic** | Misinterpreted message, unclear intent | Create manual review task, log for learning |
| **Data** | Corrupted file, missing required field | Quarantine file, alert human, skip processing |
| **System** | Disk full, process crash | Watchdog auto-restart, alert human if repeated |

### Retry Logic

**Transient errors (automatic retry):**
- Max attempts: 3
- Base delay: 1 second
- Max delay: 60 seconds
- Strategy: Exponential backoff

**Code pattern:**
```python
@with_retry(max_attempts=3, base_delay=1, max_delay=60)
def api_call():
    # Attempt operation
    pass
```

**NEVER retry automatically:**
- Payment operations
- Email sends (could duplicate)
- Social media posts
- File deletions
- Any operation with side effects

### Graceful Degradation

**When services are unavailable:**
- **Gmail API down:** Queue emails locally, process when restored
- **Odoo API timeout:** Log event, retry on next check cycle (5 minutes)
- **WhatsApp Web unavailable:** Pause watcher, alert human, retry hourly
- **Claude Code unavailable:** Watchers continue collecting, queue grows
- **Obsidian locked:** Write to temp folder, sync when available

**System health checks:**
- Every 5 minutes: Verify watchers are running
- Every hour: Verify MCP servers responsive
- Every 4 hours: Verify sufficient disk space
- Daily: Verify OAuth tokens valid

---

## 10. Security & Privacy

### Credential Management

**NEVER store in vault:**
- ❌ API keys or tokens
- ❌ Passwords
- ❌ OAuth refresh tokens
- ❌ Banking credentials

**Secure storage locations:**
- Environment variables (.env file, gitignored)
- OS credential managers (Keychain, Windows Credential Manager)
- Encrypted configuration files (outside vault)

**Rotation schedule:**
- OAuth tokens: Auto-refresh (30 min for Odoo)
- API keys: Rotate monthly
- Passwords: Rotate quarterly
- Emergency: Rotate immediately if breach suspected

### Permission Boundaries (Gold Tier)

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|------------------------|
| Email replies | ❌ Never (Gold tier) | ✅ All emails |
| Social media | ❌ Never | ✅ All posts |
| Payments | ❌ Never | ✅ All amounts |
| File operations | Read, create plans | Delete, move outside vault |
| Odoo actions | Read data | Create/modify records |

### Data Privacy

**Minimize data collection:**
- Only capture what's necessary for operation
- Delete logs > 90 days old
- Redact PII from all logs
- Never share data with third parties

**Local-first architecture:**
- All data stored in Obsidian vault (local)
- MCP servers run locally
- Only API calls leave machine (encrypted)
- Backup vault regularly

---

## 11. Ralph Wiggum Loop (Autonomous Execution)

### Purpose

Keeps AI Employee working on multi-step tasks until completion without requiring continuous human prompting.

### How It Works

1. **Task assigned** (e.g., "Process all files in /Needs_Action")
2. **Claude works** on task, creating plans, files, approval requests
3. **Claude attempts exit** after initial work
4. **Stop hook checks:** Is task complete? (file moved to /Done?)
5. **If NO:** Block exit, re-inject prompt, show previous output
6. **If YES:** Allow exit, log completion

### Completion Strategies

**File movement (Gold tier preferred):**
- Task complete when file moved from /Needs_Action to /Done
- Natural part of workflow
- Reliable completion signal
- No special output required

**Promise-based (fallback):**
- Claude outputs: `<promise>TASK_COMPLETE</promise>`
- Useful for tasks without file movement
- Requires explicit completion marker

### Usage Example

```bash
# Start Ralph loop for autonomous task processing
/ralph-loop "Process all Odoo invoices in /Needs_Action, create email drafts, move to /Done when complete" \
  --max-iterations 10
```

### Safety Limits

- Max iterations: 10 (configurable)
- Max duration: 30 minutes
- Stuck detection: Same error 3x = escalate to human
- Resource limits: CPU/memory thresholds

---

## 11A. Platinum Tier Roadmap (Always-On Cloud + Local Executive)

### Overview

Platinum tier extends Gold with **24/7 cloud deployment** and **intelligent work distribution** between cloud and local agents.

### Architecture: Cloud + Local Split

**Cloud Agent (Always-On VM):**
- Runs 24/7 on Oracle Cloud Free Tier / AWS / DigitalOcean
- Handles: Email triage, social media draft creation, monitoring
- **Drafts only** - never executes sensitive actions
- Writes approval requests to /Pending_Approval

**Local Agent (Your Machine):**
- Handles: Final approvals, WhatsApp session, payments, banking
- **Executes only** - processes /Approved items
- Maintains secrets (never sync to cloud)
- Human-in-the-loop interface

### Vault Synchronization (Phase 1: Git-based)

**What syncs:**
- ✅ Markdown files (/Needs_Action, /Plans, /Pending_Approval, /Done)
- ✅ Dashboard.md updates (Local writes, Cloud reads)
- ✅ Company_Handbook.md and Business_Goals.md
- ✅ Logs (audit trail)

**What NEVER syncs (security rule):**
- ❌ .env files and credentials
- ❌ OAuth tokens and API keys
- ❌ WhatsApp session data
- ❌ Banking credentials
- ❌ Payment tokens

**Sync method:**
```bash
# Git-based (recommended for Phase 1)
# Cloud pushes updates every 5 minutes
# Local pulls on startup and every 10 minutes

# Alternative: Syncthing for real-time sync
```

### Work Delegation Pattern

**Claim-by-move rule:**
- First agent to move file from /Needs_Action to /In_Progress/{agent}/ owns it
- Other agents must ignore claimed tasks
- Prevents duplicate work

**Domain ownership:**
| Domain | Cloud | Local |
|--------|-------|-------|
| Email triage & drafts | ✅ Draft only | ✅ Send (after approval) |
| Social media drafts | ✅ Create | ✅ Post (after approval) |
| WhatsApp | ❌ No access | ✅ Full control |
| Payments/Banking | ❌ No access | ✅ Full control |
| Odoo/Odoo reads | ✅ Monitor & analyze | ✅ Read/write |
| Odoo/Odoo writes | ❌ Draft only | ✅ Execute |

### Platinum Minimum Passing Gate

**Demo scenario:**
1. Email arrives while Local is offline
2. Cloud detects email, drafts reply
3. Cloud writes approval file to /Pending_Approval
4. Git sync pushes to repository
5. Local agent starts up, pulls changes
6. Human reviews and approves
7. Local executes send via Gmail MCP
8. Logs action, moves to /Done
9. Git sync pushes completion status

### Odoo Cloud Deployment (Platinum)

**Requirements:**
- Deploy Odoo Community 19+ on Cloud VM
- Configure HTTPS (Let's Encrypt)
- Implement automated backups
- Health monitoring and alerts
- Cloud agent uses Odoo MCP for draft-only operations
- Local agent executes approved financial actions

### Phase 2: Agent-to-Agent (A2A) Communication

**Future enhancement:**
- Replace some file handoffs with direct A2A messages
- Faster response times
- Vault remains audit record
- Requires: Message broker (MQTT/RabbitMQ) or direct HTTP API

**Reference architecture:**
- Panaversity Hackathon 0 Requirements (Requirements2.md)
- Platinum Tier Section

---

## 12. Skill Integration (Gold Tier Features)

### Active Skills

Located in `.claude/skills/` directory:

| Skill | Purpose | Trigger |
|-------|---------|---------|
| **task-processor** | Process files in /Needs_Action | Manual or scheduled |
| **approval-processor** | Execute approved actions | Continuous (every 5 min) |
| **dashboard-updater** | Refresh Dashboard.md | Hourly or manual |
| **ceo-briefing-generator** | Create weekly CEO briefing | Sunday 7:00 AM |
| **financial-analyst** | Analyze Odoo data, trends | Manual or weekly |
| **email-sender** | Send approved emails via Gmail MCP | Via approval processor |
| **linkedin-poster** | Post to LinkedIn via MCP | Via approval processor |
| **social-media-manager** | Multi-platform posting | Via approval processor |
| **odoo-integrator** | Query/update Odoo data | On-demand |
| **scheduler-manager** | Manage cron jobs / Task Scheduler | Setup |

### Skill Invocation

**Manual:**
```bash
# Run a skill directly
python .claude/skills/task-processor/scripts/process_tasks.py
```

**Scheduled (via scheduler-manager):**
```bash
# Schedule skill to run automatically
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "task-processor" \
  --command "python .claude/skills/task-processor/scripts/process_tasks.py" \
  --schedule "0 * * * *"  # Hourly
```

**Via Claude Code:**
```
/task-processor   # Run task processor skill
/update-dashboard # Run dashboard updater skill
```

---

## 13. Customization Guide

### Personalizing This Handbook

**Update these sections for your business:**

1. **Communication style** (Section 2)
   - Adjust tone (formal vs casual)
   - Add industry-specific terminology
   - Define your brand voice

2. **Financial thresholds** (Section 6)
   - Adjust alert amounts
   - Set your payment terms
   - Define your budget categories

3. **Priority keywords** (Section 5)
   - Add your urgent trigger words
   - Define VIP contacts
   - Set custom escalation rules

4. **Approval levels** (Section 10)
   - Increase automation as trust builds
   - Define auto-approve thresholds
   - Set up delegation rules

5. **Business goals** (Reference Business_Goals.md)
   - Set revenue targets
   - Define KPIs
   - Track custom metrics

### Evolution Path: Bronze → Silver → Gold

**Bronze:** All actions require approval
**Silver:** Email auto-responses to known contacts
**Gold:** Scheduled posts with approval, proactive suggestions

---

## Quick Reference Card

### ✅ Auto-Approved Actions
- Reading files and data
- Creating plans in /Plans
- Moving completed files to /Done
- Logging actions
- Generating reports
- Creating approval requests
- Dashboard updates

### ❌ Always Require Approval
- All emails (Gold tier standard)
- All social media posts
- All payment actions
- File deletions
- New vendor additions
- Subscription changes
- External API calls with side effects

### 🚨 Immediate Human Escalation
- Security alerts or unusual access patterns
- Legal or contractual matters
- Complaints or conflicts
- Large financial discrepancies (> $1000 variance)
- Repeated system failures
- Data corruption or loss

---

## Integration with Business_Goals.md

This handbook provides the **"how"** (rules and procedures).
Business_Goals.md provides the **"what"** (targets and metrics).

Together they enable:
- Autonomous task prioritization
- Proactive cost optimization
- Intelligent deadline management
- Goal-driven decision making

**See Business_Goals.md for:**
- Revenue targets
- Project deadlines
- Budget allocations
- KPI definitions
- Subscription inventory

---

## Appendix: Contact-Specific Rules

### VIP Contacts (Priority handling)

*Add your VIP clients/contacts here*

Example:
```yaml
- name: "Client A"
  email: "clienta@example.com"
  priority: urgent
  response_time: "< 2 hours"
  auto_respond: false
  notes: "Key account, always escalate"
```

### Blocked Senders (Auto-reject)

*Add spam or blocked contacts here*

Example:
```yaml
- email: "spam@example.com"
  action: "auto_archive"
  reason: "Persistent spam"
```

---

## References & Learning Resources

### Official Documentation
- **Claude Code:** https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows
- **Agent Skills:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **MCP Protocol:** https://modelcontextprotocol.io/introduction
- **Odoo API:** https://developer.odoo.com/documentation/
- **Odoo API:** https://www.odoo.com/documentation/19.0/developer/reference/external_api.html

### Panaversity Hackathon 0 (Source Architecture)
- **Requirements Document:** Requirements2.md in vault root
- **Hackathon Tiers:** Bronze → Silver → Gold → Platinum
- **Wednesday Research Meetings:** Every Wednesday 10:00 PM
- **Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube:** https://www.youtube.com/@panaversity

### Ralph Wiggum Loop
- **Official Repo:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Pattern:** Stop hook for autonomous multi-step task completion

### Recommended Videos
- Claude Code + Obsidian: https://www.youtube.com/watch?v=sCIS05Qt79Y
- Agent Skills: https://www.youtube.com/watch?v=nbqqnl3JdR0
- Claude Agent Teams: https://www.youtube.com/watch?v=0J2_YGuNrDo

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | 2026-01-17 | Added: Digital FTE metrics, Watcher architecture, Odoo integration, Platinum tier roadmap |
| 2.0 | 2026-01-14 | Gold tier complete: Odoo integration, social media, Ralph loop |
| 1.5 | 2026-01-13 | Silver tier: Multiple watchers, approval workflow |
| 1.0 | 2026-01-11 | Bronze tier: Basic vault structure, first watcher |

---

*This handbook guides all AI Employee decision-making.*
*Review and update monthly as you refine your workflows.*

**Current Status:**
- **Tier:** Gold (Platinum roadmap defined)
- **Version:** 2.1
- **Architecture:** Local-first with cloud-ready design
- **Odoo:** ✅ Connected
- **Social Media:** ✅ Multi-platform (LinkedIn, Facebook, Instagram, X)
- **Odoo:** Ready for deployment
- **Watchers:** Gmail, WhatsApp, Odoo, Filesystem, Calendar, Slack
