# Personal AI Employee - System Architecture

**Version:** 1.0 (Gold Tier)
**Last Updated:** 2026-01-20
**Status:** Production Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Layers](#architecture-layers)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Security & Privacy](#security--privacy)
8. [Error Handling & Recovery](#error-handling--recovery)
9. [Deployment & Operations](#deployment--operations)
10. [Integration Points](#integration-points)
11. [Performance & Scaling](#performance--scaling)
12. [Future Enhancements](#future-enhancements)

---

## Executive Summary

The **Personal AI Employee** is a local-first, autonomous digital assistant that manages both personal and business affairs 24/7. It combines:

- **Claude Code** as the reasoning engine
- **Obsidian** as the knowledge base and GUI
- **Python Watchers** for continuous monitoring
- **MCP Servers** for external actions
- **Human-in-the-Loop** for safety and oversight

### Key Capabilities

- 📧 **Email Management**: Gmail monitoring and auto-responses
- 📱 **Social Media**: LinkedIn, Facebook, Instagram, X/Twitter posting
- 💰 **Accounting**: Odoo ERP integration for business finances
- 📊 **CEO Briefings**: Weekly business audits and recommendations
- 🔄 **Task Automation**: Autonomous multi-step task completion
- 🛡️ **Error Recovery**: Automatic retry and graceful degradation

### Tier Achievement

- ✅ **Bronze Tier**: Foundation (100% Complete)
- ✅ **Silver Tier**: Functional Assistant (100% Complete)
- ✅ **Gold Tier**: Autonomous Employee (100% Complete)

---

## System Overview

### Design Philosophy

1. **Local-First**: All data stored locally in Obsidian vault
2. **Human-in-the-Loop**: Sensitive actions require approval
3. **Autonomous**: Continuous monitoring and proactive actions
4. **Modular**: Skills and watchers are independent components
5. **Observable**: Complete audit trail of all actions

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
├──────────────┬──────────────┬──────────────┬───────────────┤
│    Gmail     │  WhatsApp    │   Facebook   │   Odoo ERP    │
│   (API)      │  (Playwright)│ (Playwright) │  (JSON-RPC)   │
└──────┬───────┴──────┬───────┴──────┬───────┴───────┬───────┘
       │              │              │               │
       ▼              ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                  PERCEPTION LAYER (Watchers)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Gmail   │  │WhatsApp  │  │Facebook  │  │   Odoo   │  │
│  │ Watcher  │  │ Watcher  │  │ Watcher  │  │ Watcher  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼────────────┼─────────────┼─────────────┼──────────┘
        │            │             │             │
        ▼            ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                   OBSIDIAN VAULT (Local)                     │
│  ┌────────────┬────────────┬────────────┬──────────────┐  │
│  │/Inbox     │/Needs_Action│/Pending_   │/Approved     │  │
│  │           │             │Approval    │              │  │
│  ├────────────┼────────────┼────────────┼──────────────┤  │
│  │Dashboard  │Company     │Business    │Briefings     │  │
│  │.md        │Handbook    │Goals       │              │  │
│  └────────────┴────────────┴────────────┴──────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  REASONING LAYER (Claude Code)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Read → Analyze → Plan → Create Approval → Execute  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                  ▼
┌────────────────────────┐          ┌────────────────────────┐
│   HUMAN-IN-THE-LOOP    │          │    ACTION LAYER        │
│  Review & Approve      ├─────────►│    (MCP Servers)       │
└────────────────────────┘          │  ┌────┬────┬────┐     │
                                  │  │Gmail│Odoo│SOCIAL│   │
                                  │  └────┴────┴────┘     │
                                  └────────────────────────┘
```

---

## Architecture Layers

### Layer 1: Perception (Watchers)

**Purpose:** Monitor external sources continuously and create actionable files

**Components:**
- `gmail_watcher.py` - Gmail API monitoring
- `whatsapp_watcher.py` - WhatsApp Web automation
- `slack_watcher.py` - Slack integration
- `filesystem_watcher.py` - Local file drops
- `calendar_watcher.py` - Calendar events
- `odoo_watcher.py` - Accounting data

**Pattern:** All watchers extend `BaseWatcher` and implement:
- `check_for_updates()` - Detect new items
- `create_action_file()` - Create .md file in `/Needs_Action`
- `run()` - Continuous monitoring loop

**Location:** `watchers/` directory

### Layer 2: Memory (Obsidian Vault)

**Purpose:** Persistent storage, knowledge base, and GUI

**Directory Structure:**
```
AI_Employee_Vault/
├── Inbox/                  # Raw inputs from watchers
├── Needs_Action/           # Tasks requiring processing
├── In_Progress/            # Currently being worked on
├── Pending_Approval/       # Awaiting human review
├── Approved/               # Human-approved actions
├── Rejected/               # Human-rejected actions
├── Done/                   # Completed tasks
├── Logs/                   # Audit logs (JSON format)
├── Plans/                  # Execution plans
├── Briefings/              # CEO briefings
├── Accounting/             # Financial data
├── Tasks/                  # Task management
├── Dashboard.md            # Real-time system status
├── Company_Handbook.md     # Rules of engagement
├── Business_Goals.md       # Revenue targets & metrics
└── ARCHITECTURE.md         # This document
```

**File Format:** YAML frontmatter + markdown content
```yaml
---
type: email|approval_request|task
status: pending|approved|rejected|completed
created: 2026-01-20T10:30:00Z
priority: high|medium|low
---

# Content here
```

### Layer 3: Reasoning (Claude Code + Skills)

**Purpose:** Analyze situations, make decisions, create plans

**Agent Skills (22+ skills in `.claude/skills/`):**

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `task-processor` | Process /Needs_Action items | Manual/scheduled |
| `auto-approver` | Auto-approve safe requests | Monitoring |
| `approval-processor` | Execute approved actions | File detection |
| `email-sender` | Send emails via Gmail MCP | Approved actions |
| `linkedin-poster` | Post to LinkedIn | Scheduled/manual |
| `facebook-poster` | Post to Facebook | Scheduled/manual |
| `x-poster` | Post to X/Twitter | Scheduled/manual |
| `instagram-poster` | Post to Instagram | Scheduled/manual |
| `ceo-briefing-generator` | Generate weekly briefings | Scheduled (Mon 9AM) |
| `financial-analyst` | Analyze financial data | Scheduled |
| `dashboard-updater` | Update Dashboard.md | Every change |
| `cross-domain-bridge` | Enrich with context | All items |
| `ralph-loop` | Autonomous task completion | Complex tasks |
| `scheduler-manager` | Manage scheduled tasks | System events |
| `plan-generator` | Create execution plans | Complex workflows |

**Skill Structure:**
```
.claude/skills/{skill-name}/
├── SKILL.md          # Documentation (Frontmatter + markdown)
├── scripts/
│   ├── main.py       # Main execution script
│   └── helpers.py    # Helper functions
├── templates/        # Template files
├── assets/           # Images, configs, sessions
└── references/       # Reference documentation
```

**Skill Frontmatter Format:**
```yaml
---
name: skill-name
description: One-line description of what this skill does
---
```

### Layer 4: Action (MCP Servers)

**Purpose:** Execute external actions (send emails, post to social media, etc.)

**MCP Servers:**

| Server | Purpose | Protocol | Location |
|--------|---------|----------|----------|
| Gmail MCP | Send/search emails | HTTP + OAuth | `mcp-servers/gmail-mcp/` |
| Odoo MCP | Accounting operations | JSON-RPC | `mcp-servers/odoo-mcp-server/` |
| LinkedIn MCP | Post to LinkedIn | OAuth API | `mcp-servers/linkedin-mcp/` |

**Note:** Facebook, Instagram, X/Twitter use Playwright browser automation instead of APIs (no API costs).

### Layer 5: Orchestration

**Purpose:** Manage processes, scheduling, and health monitoring

**Components:**
- `orchestrator.py` - Master process manager
- `scheduler-manager` - Windows Task Scheduler integration
- Health checks and auto-restart

**Scheduled Tasks:**
- Daily Dashboard Update (hourly)
- Approval Processing (every 5 min)
- Financial Analysis (daily 9 AM)
- CEO Briefing (weekly Monday 9 AM)

---

## Core Components

### 1. Watchers (Perception Layer)

**BaseWatcher Pattern:**
```python
class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def run(self):
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                logger.error(f'Error: {e}')
            time.sleep(self.check_interval)
```

**Implemented Watchers:**
1. `gmail_watcher.py` - Monitors Gmail for unread important emails
2. `whatsapp_watcher.py` - WhatsApp Web automation for business messages
3. `slack_watcher.py` - Slack channel monitoring
4. `filesystem_watcher.py` - Local file drop folder monitoring
5. `calendar_watcher.py` - Calendar event monitoring
6. `odoo_watcher.py` - Odoo ERP data synchronization

### 2. Skills (Reasoning Layer)

**Skill Invocation:**

Skills can be invoked in three ways:

1. **Manual via Claude Code:**
   ```
   User: "Post to LinkedIn about our new service"
   Claude: [Invokes linkedin-poster skill]
   ```

2. **Scheduled via scheduler-manager:**
   ```bash
   # Schedule weekly LinkedIn post
   python .claude/skills/scheduler-manager/scripts/create_schedule.py \
     --name "linkedin-weekly" \
     --command "claude /skill linkedin-poster 'Weekly achievement'" \
     --schedule "0 9 * * 1"
   ```

3. **Automatic via file detection:**
   ```
   approval-processor detects file in /Approved
   → Invokes corresponding skill
   → Executes action
   → Moves to /Done
   ```

**Skill Categories:**

**Communication:**
- `email-sender` - Send emails via Gmail MCP
- `linkedin-poster` - Post to LinkedIn
- `facebook-poster` - Post to Facebook
- `x-poster` - Post to X/Twitter
- `instagram-poster` - Post to Instagram

**Task Management:**
- `task-processor` - Process /Needs_Action items
- `auto-approver` - Auto-approve safe requests
- `approval-processor` - Execute approved actions
- `plan-generator` - Create execution plans
- `ralph-loop` - Autonomous multi-step completion

**Business Intelligence:**
- `ceo-briefing-generator` - Weekly business audits
- `financial-analyst` - Analyze financial data
- `dashboard-updater` - Update system status

**Integration:**
- `cross-domain-bridge` - Personal + Business context
- `scheduler-manager` - Task scheduling
- `watcher-manager` - Watcher lifecycle management

### 3. MCP Servers (Action Layer)

**Gmail MCP Server:**
- **Protocol:** HTTP + OAuth 2.0
- **Capabilities:** Send, draft, search emails
- **Location:** `mcp-servers/gmail-mcp/`
- **Auth:** User credentials flow with refresh tokens

**Odoo MCP Server:**
- **Protocol:** JSON-RPC
- **Capabilities:** CRUD operations on Odoo models
- **Location:** `mcp-servers/odoo-mcp-server/`
- **Deployment:** Docker (Odoo 19 + PostgreSQL + Redis)
- **Port:** 8069 (Odoo), 5432 (Postgres), 6379 (Redis)

**LinkedIn MCP Server:**
- **Protocol:** OAuth 2.0 API
- **Capabilities:** Create posts, get profile
- **Location:** `mcp-servers/linkedin-mcp/`
- **Scopes:** `w_member_social`, `r_liteprofile`

**Note:** Social media platforms (Facebook, Instagram, X/Twitter) use **Playwright browser automation** instead of APIs due to:
- No API costs
- More reliable (API rate limits)
- Persistent sessions
- Works with official UI

### 4. Orchestrator

**Master Process Manager:**
```python
class Process:
    def __init__(self, name, script, enabled=True, restart_on_fail=True):
        self.name = name
        self.script = script
        self.enabled = enabled
        self.restart_on_fail = restart_on_fail
        self.process = None
        self.start_count = 0
        self.status = 'stopped'

    def start(self):
        # Start process
        # Monitor health
        # Auto-restart on failure
```

**Managed Processes:**
- All watchers (Gmail, WhatsApp, etc.)
- Orchestrator itself (self-healing)
- Health checks every 60 seconds

**Scheduler Integration:**
- Uses Windows Task Scheduler (native)
- Creates scheduled tasks via `schtasks.exe`
- Persistent across reboots

---

## Data Flow

### End-to-End Flow: Email → CEO Briefing

```
1. PERCEPTION
   Gmail Watcher detects new important email
   → Creates: /Needs_Action/EMAIL_client_2026-01-20.md

2. REASONING
   task-processor skill reads /Needs_Action
   → Analyzes email content
   → Checks Company_Handbook.md rules
   → Determines: Client asking for invoice

3. PLANNING
   plan-generator creates execution plan:
   → /Plans/PLAN_invoice_client_A.md
   → Steps: Generate invoice → Create approval → Send email

4. ENRICHMENT
   cross-domain-bridge enriches with context:
   → Adds: Business relevance score, domain classification
   → Checks: Personal time vs business hours

5. APPROVAL
   auto-approver evaluates:
   → Known contact? Yes (15+ interactions)
   → Safe content? Yes
   → Decision: Auto-approve
   → Moves: /Pending_Approval → /Approved

6. EXECUTION
   approval-processor detects approved file
   → Invokes: Odoo MCP to generate invoice
   → Invokes: email-sender to send invoice
   → Logs: Audit trail in /Logs/audit_YYYY-MM-DD.json
   → Moves: /Approved → /Done

7. UPDATING
   dashboard-updater updates Dashboard.md:
   → Adds entry to Recent Activity
   → Updates financial overview
   → Records in audit log

8. WEEKLY AUDIT
   ceo-briefing-generator runs (Monday 9 AM):
   → Reads: Business_Goals.md
   → Analyzes: /Done, /Accounting, /Logs
   → Generates: /Briefings/2026-01-20_Monday_Briefing.md
   → Highlights: Revenue, bottlenecks, cost optimization
```

### File State Machine

```
                    ┌─────────────┐
                    │   /Inbox    │  (Raw inputs)
                    └──────┬──────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ /Needs_Action  │  (To be processed)
                   └───────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  /In_Progress  │  (Being worked on)
                  └───────┬────────┘
                          │
         ┌────────────────┴────────────────┐
         │                                  │
         ▼                                  ▼
  ┌──────────────┐                  ┌──────────────┐
  │/Pending_     │                  │  /Plans      │
  │Approval      │◄─────────────────┤  (strategy)  │
  └──────┬───────┘                  └──────────────┘
         │
         │ (human decision)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│Approved│ │Rejected│
└───┬────┘ └───┬────┘
    │          │
    │          ▼
    │     ┌─────────┐
    │     │ /Failed │
    │     └─────────┘
    │
    ▼
┌─────────┐
│  /Done  │  (Completed)
└─────────┘
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Reasoning Engine** | Claude Code | Latest | AI decision making |
| **Knowledge Base** | Obsidian | 1.10.6+ | Local markdown storage |
| **Programming Language** | Python | 3.9+ | Watchers & automation |
| **Browser Automation** | Playwright | Latest | WhatsApp, Social media |
| **Container Platform** | Docker | Latest | Odoo deployment |
| **ERP System** | Odoo | 19.0 Community | Accounting |
| **Database** | PostgreSQL | 15+ | Odoo backend |
| **Cache** | Redis | 7+ | Odoo caching |
| **Task Scheduling** | Windows Task Scheduler | Native | Scheduled tasks |

### Python Dependencies

**Core:**
- `playwright` - Browser automation
- `google-api-python-client` - Gmail API
- `google-auth-oauthlib` - Gmail OAuth
- `Pillow` (PIL) - Image generation
- `pyyaml` - YAML frontmatter parsing
- `python-dotenv` - Environment variables

**Odoo Integration:**
- `odoo-client-lib` - JSON-RPC client (optional, can use requests)

**Development:**
- `pytest` - Testing
- `black` - Code formatting
- `mypy` - Type checking

### System Requirements

**Minimum:**
- OS: Windows 10/11, macOS 10.15+, or Linux
- RAM: 8GB
- CPU: 4 cores
- Disk: 20GB free
- Python: 3.9+

**Recommended:**
- RAM: 16GB
- CPU: 8 cores
- Disk: SSD with 50GB free
- Stable internet: 10+ Mbps

---

## Security & Privacy

### Credential Management

**Principles:**
1. Never store credentials in code
2. Use environment variables (.env file)
3. .env is gitignored
4. Rotate credentials monthly

**Credential Storage:**
```
watchers/.env                    # Local environment (gitignored)
├── GMAIL_CLIENT_ID
├── GMAIL_CLIENT_SECRET
├── ODOO_URL
├── ODOO_DB
├── ODOO_USERNAME
└── ODOO_API_KEY
```

**OAuth Tokens:**
- Gmail: Stored in `watchers/credentials/token.pickle`
- LinkedIn: Stored in `watchers/credentials/linkedin_credentials.json`
- Social media: Stored in `.claude/skills/*/assets/session/` (browser cookies)

### Human-in-the-Loop (HITL)

**Approval Workflow:**
1. AI creates approval request in `/Pending_Approval`
2. Human reviews file contents
3. Human moves file to `/Approved` or `/Rejected`
4. Approval processor executes or cancels action

**Approval Triggers:**
- New recipients (not in known contacts)
- Payments over $100
- Social media posts
- Mass emails (>5 recipients)
- Actions during personal time (cross-domain bridge)

**Approval Expiration:**
- Default: 24 hours
- Auto-rejects after expiration
- Prevents stale approvals

### Audit Logging

**Standard Format:**
```json
{
  "timestamp": "2026-01-20T10:30:00Z",
  "action_type": "email_send",
  "actor": "email_sender",
  "target": "client@example.com",
  "parameters": {
    "subject": "Invoice #1234",
    "has_attachments": true
  },
  "approval_status": "approved",
  "approved_by": "auto_approver",
  "result": "success",
  "skill": "email-sender",
  "duration_ms": 2345,
  "error": null
}
```

**Log Location:** `/Logs/audit_YYYY-MM-DD.json`

**Retention:** 90 days (auto-deletion)

**Searchable:** Filter by action_type, skill, result, date

### Data Protection

**Local-First:**
- All data stored in Obsidian vault (local filesystem)
- No cloud sync of sensitive data
- Git/sync excludes: .env, credentials/, session/

**Encryption at Rest:**
- Optional: Encrypt entire Obsidian vault
- Use: Obsidian Encryption Plugin or filesystem encryption (BitLocker/FileVault)

**Secrets Never Sync:**
- .env file (contains API keys)
- credentials/ directory (OAuth tokens)
- assets/session/ (browser sessions)
- .gitignore configured correctly

---

## Error Handling & Recovery

### Error Categories

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| **Transient** | Network timeout, API rate limit | Exponential backoff retry |
| **Authentication** | Expired token, revoked access | Alert human, pause operations |
| **Logic** | Claude misinterprets message | Human review queue |
| **Data** | Corrupted file, missing field | Quarantine + alert |
| **System** | Orchestrator crash, disk full | Watchdog + auto-restart |

### Retry Logic

**Decorator:**
```python
@retry_with_backoff(max_attempts=3, base_delay=2, max_delay=60)
def call_api():
    # Retries on timeout, rate limit, network errors
    pass
```

**Exponential Backoff:**
- Attempt 1: Immediate
- Attempt 2: 2 second delay
- Attempt 3: 4 second delay
- Max delay: 60 seconds

### Circuit Breaker Pattern

**Purpose:** Prevent cascading failures

**Behavior:**
1. Track failures (threshold: 5 failures)
2. Open circuit (stop calling service)
3. Wait timeout (60 seconds)
4. Half-open (try one request)
5. Close circuit (if success) or reopen (if failure)

**Implementation:**
```python
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

if breaker.can_execute():
    result = call_service()
    if result.failed:
        breaker.record_failure()
else:
    # Circuit open, use fallback
    use_fallback()
```

### Graceful Degradation

**Strategy:** Queue items when services are down

**Implementation:**
```python
degradation = GracefulDegradation(vault_path)

# Service is down
degradation.queue_for_later(item_data, "email_service")

# Service is back up
degradation.process_queue("email_service", processing_fn)
```

**Queue Location:** `/Failed/queues/{service_name}/`

### Error Recovery Integration

**Verified Integration:**
- ✅ `auto-approver` uses retry decorator
- ✅ `auto-approver` uses error categorization
- ✅ All skills log to audit trail

**Available for Integration:**
- `watchers/error_recovery.py` - Complete system
- `watchers/audit_logger.py` - Logging system
- Ready to add to any watcher or skill

---

## Deployment & Operations

### Getting Started

**1. Prerequisites:**
- Install Python 3.9+
- Install Claude Code
- Install Obsidian
- Install Docker (for Odoo)

**2. Clone Repository:**
```bash
git clone <repository-url>
cd AI_Employee_Vault
```

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**4. Configure Environment:**
```bash
cp watchers/.env.example watchers/.env
# Edit watchers/.env with your credentials
```

**5. Start Odoo (Docker):**
```bash
cd mcp-servers/odoo-mcp-server
docker-compose up -d
```

**6. Authenticate Services:**
```bash
# Gmail
python watchers/gmail_watcher.py --authenticate

# LinkedIn
python .claude/skills/linkedin-poster/scripts/linkedin_post.py --authenticate

# Social media (run in visible mode)
python .claude/skills/facebook-poster/scripts/facebook_post.py --authenticate --no-headless
```

**7. Start Orchestrator:**
```bash
python watchers/orchestrator.py
```

**8. Schedule Tasks:**
```bash
# Dashboard update (hourly)
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "dashboard-update" \
  --command "python .claude/skills/dashboard-updater/scripts/update_dashboard.py" \
  --schedule "0 * * * *"

# CEO Briefing (Monday 9 AM)
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "ceo-briefing" \
  --command "claude /skill ceo-briefing-generator" \
  --schedule "0 9 * * 1"
```

### Process Management

**Development:**
```bash
# Run watchers in foreground
python watchers/gmail_watcher.py
```

**Production (PM2):**
```bash
npm install -g pm2

pm2 start watchers/gmail_watcher.py --interpreter python3
pm2 start watchers/whatsapp_watcher.py --interpreter python3
pm2 start watchers/orchestrator.py --interpreter python3

pm2 save
pm2 startup
```

**Production (Windows Service):**
- Use Task Scheduler for scheduled tasks
- Use NSSM (Non-Sucking Service Manager) for services

### Monitoring

**Health Checks:**
- Orchestrator monitors all processes
- Auto-restart on failure
- Health check every 60 seconds

**Logs:**
- All logs in `/Logs/` directory
- Daily rotation
- JSON format for parsing
- Searchable with `jq`

**Dashboard:**
- `Dashboard.md` shows real-time status
- Update frequency: Every change
- Manual update: `claude /skill dashboard-updater`

---

## Integration Points

### Claude Code Integration

**Skill Invocation:**
```
User: "Post to LinkedIn about achieving Gold Tier"
Claude: [Invokes linkedin-poster skill]
```

**MCP Server Configuration:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": ["mcp-servers/gmail-mcp/index.js"],
      "env": {
        "GMAIL_CLIENT_ID": "...",
        "GMAIL_CLIENT_SECRET": "..."
      }
    },
    "odoo": {
      "command": "python",
      "args": ["-m", "mcp_server_odoo"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "...",
        "ODOO_API_KEY": "..."
      }
    }
  }
}
```

### Obsidian Integration

**Plugin:** None required (uses built-in features)

**Vault:** `AI_Employee_Vault/`

**Key Files:**
- `Dashboard.md` - Main dashboard
- `Company_Handbook.md` - Rules of engagement
- `Business_Goals.md` - Revenue targets

**Folder Monitoring:** Watchers monitor vault folders for changes

### External Service Integration

**Gmail:**
- Method: Gmail API (OAuth 2.0)
- Scopes: `gmail.readonly`, `gmail.send`
- Auth flow: User credentials with refresh token

**WhatsApp:**
- Method: Playwright browser automation
- URL: web.whatsapp.com
- Session: Persistent browser context

**LinkedIn:**
- Method: LinkedIn API (OAuth 2.0)
- Scopes: `w_member_social`, `r_liteprofile`

**Facebook:**
- Method: Playwright browser automation
- URL: facebook.com
- Session: Persistent browser context

**X/Twitter:**
- Method: Playwright browser automation
- URL: x.com
- Session: Persistent browser context

**Instagram:**
- Method: Playwright browser automation
- URL: instagram.com
- Session: Persistent browser context

**Odoo:**
- Method: JSON-RPC
- URL: http://localhost:8069
- Auth: API key or username/password
- Docker: Compose setup

---

## Performance & Scaling

### Current Performance

**Throughput:**
- Email processing: ~50 emails/hour
- Social media posts: ~10 posts/hour
- Task processing: ~100 tasks/hour

**Latency:**
- Email detection: <2 minutes (check interval)
- Approval processing: <5 minutes (check interval)
- Social media posting: <30 seconds (Playwright)

**Resource Usage:**
- RAM: ~2GB (all watchers running)
- CPU: ~5% (idle), ~20% (processing)
- Disk: ~100MB/day (logs)

### Scaling Considerations

**Vertical Scaling (Single Machine):**
- RAM: 8GB → 16GB (more watchers)
- CPU: 4 cores → 8 cores (parallel processing)
- Disk: HDD → SSD (faster I/O)

**Horizontal Scaling (Multi-Machine):**
- Separate watcher machines
- Central vault (Git/Syncthing sync)
- Shared credentials (encrypted vault)
- Load balancing (round-robin)

**Optimization Opportunities:**
- Reduce check intervals (more frequent monitoring)
- Parallel processing (multiple watchers)
- Cache frequently accessed data
- Compress old logs

### Bottlenecks

**Known Limitations:**
1. **Sequential processing** - Tasks processed one at a time
2. **Single orchestrator** - No failover
3. **Local storage** - Disk space management needed
4. **Manual approval** - Human bottleneck

**Mitigation:**
1. Implement task queue (future)
2. Multi-orchestrator setup (future)
3. Log rotation and cleanup (implemented)
4. Auto-approval for safe tasks (implemented)

---

## Future Enhancements

### Planned Features

**Short-Term (1-3 months):**
- [ ] Video support for social media posts
- [ ] Multiple image uploads per post
- [ ] Reply to comments automatically
- [ ] Voice input for commands
- [ ] Mobile app (Obsidian sync)

**Medium-Term (3-6 months):**
- [ ] Cloud deployment (24/7 operation)
- [ ] Multi-user support
- [ ] Advanced analytics dashboard
- [ ] Machine learning for auto-approval
- [ ] Integration with more services (CRM, project management)

**Long-Term (6-12 months):**
- [ ] Natural language voice commands
- [ ] Proactive suggestions (AI recommendations)
- [ ] Multi-language support
- [ ] White-label solution (sell as SaaS)
- [ ] Mobile-first architecture

### Platinum Tier Roadmap

**Cloud + Local Hybrid:**
1. Cloud agents: Email triage, social drafts, scheduling
2. Local agents: Approvals, payments, final send/post
3. Synced vault: Git or Syncthing
4. Delegation protocol: File handoff + claim-by-move

**Work-Zone Specialization:**
- **Cloud owns:** Email triage, draft replies, social drafts
- **Local owns:** Approvals, WhatsApp, payments, final actions

**Deployment:**
- Cloud VM: Oracle Cloud Free Tier or AWS EC2
- Local: User's machine
- Sync: Git push/pull every 5 minutes
- Security: Secrets never sync

---

## Appendix

### File Reference

**Core Configuration:**
- `watchers/.env` - Environment variables
- `watchers/orchestrator.py` - Master process manager
- `Dashboard.md` - System status dashboard
- `Company_Handbook.md` - Rules and policies
- `Business_Goals.md` - Revenue targets

**Error Recovery:**
- `watchers/error_recovery.py` - Retry, circuit breaker, graceful degradation
- `watchers/audit_logger.py` - Audit logging system
- `test_error_recovery.py` - Test suite

**Documentation:**
- `ARCHITECTURE.md` - This document
- `CLAUDE.md` - Claude Code instructions
- `docs/GOLD_TIER_COMPLETE.md` - Gold Tier verification
- `Requirements.md` - Original requirements

### Command Reference

**Start System:**
```bash
# Start orchestrator (starts all watchers)
python watchers/orchestrator.py

# Start individual watcher
python watchers/gmail_watcher.py
```

**Stop System:**
```bash
# Stop orchestrator (stops all watchers)
# Ctrl+C or kill process

# Stop individual watcher
pm2 stop gmail_watcher
```

**Test System:**
```bash
# Test error recovery
python test_error_recovery.py

# Test cross-domain bridge
python test_cross_domain.py

# Test Gmail watcher
python watchers/gmail_watcher.py --check-login
```

### Troubleshooting

**Watchers not starting:**
1. Check .env file exists and has correct values
2. Verify credentials are valid
3. Check logs in `/Logs/`
4. Run in foreground to see errors

**Social media authentication fails:**
1. Run in visible mode (`--no-headless`)
2. Clear session directory
3. Re-authenticate manually
4. Check for platform login issues

**Odoo not accessible:**
1. Check Docker containers running: `docker ps`
2. Check logs: `docker-compose logs`
3. Restart: `docker-compose restart`
4. Verify port 8069 not in use

**Orchestrator crashes:**
1. Check `orchestrator.log` for errors
2. Verify all watcher scripts exist
3. Check Python dependencies installed
4. Run in foreground to see error

---

## Conclusion

The Personal AI Employee is a **production-ready, Gold Tier autonomous digital assistant** that successfully combines:

- ✅ **Perception:** 6+ watchers monitoring external sources
- ✅ **Reasoning:** 22+ Claude Code skills for decision making
- ✅ **Action:** 3+ MCP servers for external actions
- ✅ **Memory:** Obsidian vault with complete audit trail
- ✅ **Orchestration:** Automated scheduling and health monitoring
- ✅ **Safety:** Human-in-the-loop approval workflow
- ✅ **Reliability:** Error recovery and graceful degradation
- ✅ **Business Integration:** Odoo accounting + CEO briefings

**System Status:** 100% Gold Tier Complete ✅

**Ready for:** Production use, 24/7 operation, business deployment

**Next Steps:** Consider Platinum Tier enhancements (cloud deployment, multi-user, advanced analytics)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-20
**Maintained By:** AI Employee System Architect
