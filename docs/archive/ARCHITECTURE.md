# Personal AI Employee - Architecture Documentation

**Gold Tier Requirement 11: Architecture Documentation**

**Date:** 2026-01-14
**Version:** 1.0 (Gold Tier)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architectural Principles](#architectural-principles)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Patterns](#design-patterns)
7. [Integration Points](#integration-points)
8. [Security Architecture](#security-architecture)
9. [Scalability & Performance](#scalability--performance)
10. [Trade-offs & Decisions](#trade-offs--decisions)

---

## System Overview

### Purpose
The Personal AI Employee is a **fully autonomous business assistant** that monitors multiple input sources 24/7, creates actionable tasks, and executes approved actions through a human-in-the-loop workflow.

### Core Philosophy
- **Local-first:** All data stored locally in Obsidian vault
- **Agent-driven:** Claude Code provides reasoning and execution
- **Human-in-the-loop:** Sensitive actions require explicit approval
- **Fault-tolerant:** Auto-restart on failures, graceful degradation
- **Audit-first:** Comprehensive logging of all actions

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PERCEPTION LAYER                        │
│  6 Watchers monitoring external sources (24/7)             │
├─────────────────────────────────────────────────────────────┤
│  Calendar │ Slack │ Gmail │ WhatsApp │ Filesystem │ Xero  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                       │
│  Process management + health monitoring                     │
├─────────────────────────────────────────────────────────────┤
│  Watchdog → Orchestrator → 6 Watcher Processes             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE LAYER                     │
│  Local-first markdown storage (Obsidian vault)             │
├─────────────────────────────────────────────────────────────┤
│  /Needs_Action │ /Pending_Approval │ /Approved │ /Done    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     REASONING LAYER                         │
│  Claude Code Agent Skills                                   │
├─────────────────────────────────────────────────────────────┤
│  Task Processor │ Approval Processor │ Dashboard Updater   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      ACTION LAYER                           │
│  Execution with approval workflow                           │
├─────────────────────────────────────────────────────────────┤
│  LinkedIn Poster │ Email Sender │ X Poster │ Social Media  │
└─────────────────────────────────────────────────────────────┘
```

---

## Architectural Principles

### 1. **Separation of Concerns**
Each layer has a single, well-defined responsibility:
- **Perception:** Detect events
- **Orchestration:** Manage processes
- **Knowledge:** Store data
- **Reasoning:** Make decisions
- **Action:** Execute approved actions

### 2. **Fail-Safe Design**
- Watchers can crash without affecting others
- Orchestrator auto-restarts failed watchers
- Watchdog monitors orchestrator itself
- No single point of failure

### 3. **Human-in-the-Loop**
- All sensitive actions require explicit approval
- Move file from `/Pending_Approval` → `/Approved` to execute
- Clear audit trail of who approved what

### 4. **Local-First**
- All data stored locally in Obsidian vault
- No cloud dependencies for core functionality
- Privacy-preserving by default

### 5. **Composability**
- Each watcher is independent
- Each skill is self-contained
- Easy to add/remove components

### 6. **Observability**
- Comprehensive audit logging
- Activity logs per watcher
- Health monitoring
- Error tracking

---

## Core Components

### 1. Perception Layer (Watchers)

**Purpose:** Monitor external sources and create task files

**Components:**
- `calendar_watcher.py` - Google Calendar events (5 min interval)
- `slack_watcher.py` - Slack keyword matches (1 min interval)
- `gmail_watcher.py` - Important emails (2 min interval)
- `whatsapp_watcher.py` - Urgent messages (30 sec interval, visible mode)
- `filesystem_watcher.py` - File drops (real-time)
- `xero_watcher.py` - Financial events (5 min interval)

**Pattern:**
```python
class BaseWatcher(ABC):
    def check_for_updates() -> list:
        """Check external source for new items"""
        pass

    def create_action_file(item) -> Path:
        """Create .md file in Needs_Action/"""
        pass

    def run():
        """Main loop with error handling"""
        while True:
            items = check_for_updates()
            for item in items:
                create_action_file(item)
            time.sleep(check_interval)
```

**Design Decision:**
- Each watcher is a separate process (not threads) for true isolation
- Polling-based (not webhooks) to avoid port opening and firewall issues
- YAML frontmatter for structured metadata

### 2. Orchestration Layer

**Purpose:** Ensure all watchers stay running 24/7

**Components:**
```
watchdog.py (monitors orchestrator)
    ↓
orchestrator.py (manages 6 watchers)
    ↓
orchestrator_cli.py (user control)
orchestrator_config.json (configuration)
```

**Health Check Logic:**
```python
def health_check():
    for process in watchers:
        if not process.is_running():
            if process.restart_on_fail:
                process.start()  # Auto-restart
                log_event('restart', process.name)
```

**Design Decision:**
- Orchestrator is a long-running process (not systemd/service)
- Watchdog monitors orchestrator (watchdog for the watchdog)
- 60-second health check interval (balance between responsiveness and overhead)

### 3. Knowledge Base Layer (Obsidian Vault)

**Purpose:** Local-first markdown storage for all data

**Folder Structure:**
```
AI_Employee_Vault/
├── Inbox/                 # Drop files here
├── Needs_Action/          # Tasks created by watchers
├── Plans/                 # Action plans (future)
├── Pending_Approval/      # Actions awaiting approval
├── Approved/              # Approved actions (auto-executed)
├── Done/                  # Completed tasks
├── Failed/                # Failed actions
├── Rejected/              # Rejected approvals
├── Expired/               # Expired approvals
├── Logs/                  # Activity + audit logs
├── Dashboard.md           # Real-time overview
├── Company_Handbook.md    # Business rules
└── Business_Goals.md      # Targets and metrics
```

**File Format (YAML Frontmatter + Markdown):**
```markdown
---
type: email
from: sender@example.com
subject: Important Topic
priority: high
status: pending
---

## Email Content
Email snippet here...

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to team
```

**Design Decision:**
- Markdown for human readability and editability
- YAML frontmatter for machine-parseable metadata
- File-based state management (no database)

### 4. Reasoning Layer (Claude Code Agent Skills)

**Purpose:** AI-powered task processing and decision making

**Core Skills:**
- `approval-processor` - Process approval workflow
- `task-processor` - Process tasks from Needs_Action
- `dashboard-updater` - Update Dashboard.md
- `vault-setup` - Initialize vault structure
- `watcher-manager` - Manage watcher scripts

**Skill Pattern:**
```python
#!/usr/bin/env python3
"""
Skill: approval-processor

Process files in /Approved folder and execute actions.
"""

def main():
    for approval_file in APPROVED.glob("*.md"):
        metadata = parse_frontmatter(approval_file)
        action_type = metadata['type']

        # Route to executor
        success = execute_action(action_type, metadata)

        # Move to Done or Failed
        if success:
            move_to_done(approval_file)
        else:
            move_to_failed(approval_file)
```

**Design Decision:**
- Agent Skills for discoverability (Claude Code integration)
- Self-contained scripts (no complex dependencies)
- CLI-first (easy to test and automate)

### 5. Action Layer (Execution Skills)

**Purpose:** Execute approved actions via automation

**Components:**
- `linkedin-poster` - Playwright browser automation
- `x-poster` - Playwright browser automation
- `email-sender` - SMTP or Gmail API
- `instagram-poster` - Playwright browser automation
- `facebook-poster` - Playwright browser automation
- `social-media-manager` - Unified multi-platform

**Execution Pattern:**
```python
def execute_approved_post(approval_file: str) -> bool:
    # 1. Read approval file
    metadata = parse_frontmatter(approval_file)
    message = metadata['message']

    # 2. Execute action
    success, error = post_to_platform(message)

    # 3. Log to audit trail
    audit_logger.log_action(
        action_type="linkedin_post",
        actor="linkedin_poster",
        target="LinkedIn",
        parameters={"message": message[:200]},
        approval_status="approved",
        approved_by="human",
        result="success" if success else "failure",
        error_message=error
    )

    # 4. Move file
    if success:
        move_to_done(approval_file)
    else:
        move_to_failed(approval_file)

    return success
```

**Design Decision:**
- Playwright over APIs (no API costs, avoid rate limits)
- Persistent browser sessions (login once, stay logged in)
- Visible mode for WhatsApp (anti-automation detection)

---

## Data Flow

### Flow 1: Event Detection → Task Creation

```
1. External Source (Gmail/Slack/etc.)
   ↓
2. Watcher polls API/checks status
   ↓
3. New item detected
   ↓
4. Watcher creates .md file in /Needs_Action
   ↓
5. Watcher logs activity to actions_YYYY-MM-DD.json
   ↓
6. User reviews Dashboard.md (manual or scheduled)
```

### Flow 2: Approval Workflow → Action Execution

```
1. Skill creates approval request in /Pending_Approval
   ↓
2. Human reviews approval request
   ↓
3. Human moves file to /Approved (approval) or /Rejected (denial)
   ↓
4. Approval Processor detects file in /Approved
   ↓
5. Approval Processor routes to executor (LinkedIn, Email, etc.)
   ↓
6. Executor performs action via automation
   ↓
7. Executor logs to audit trail (audit_YYYY-MM-DD.json)
   ↓
8. Approval Processor moves file to /Done or /Failed
```

### Flow 3: Health Monitoring → Auto-Restart

```
1. Watchdog checks if orchestrator is running (every 60s)
   ↓
2. If orchestrator crashed:
   a. Watchdog restarts orchestrator
   b. Watchdog logs restart event
   ↓
3. Orchestrator checks if watchers are running (every 60s)
   ↓
4. If watcher crashed:
   a. Orchestrator restarts watcher
   b. Orchestrator logs restart event
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Reason |
|-----------|-----------|--------|
| Reasoning Engine | Claude Code (Sonnet 4.5) | Best-in-class coding agent |
| Knowledge Base | Obsidian (Markdown) | Local-first, human-readable |
| Process Management | Python `subprocess` | Simple, cross-platform |
| Browser Automation | Playwright (Python) | Reliable, no API costs |
| File Watching | watchdog library | Real-time file system events |
| APIs | Google, Slack, Xero SDKs | Official client libraries |

### Language & Runtime

- **Python 3.13+** - All watchers, skills, orchestration
- **Batch Scripts** - Windows convenience wrappers
- **JSON** - Configuration and logs
- **Markdown** - Task files and documentation
- **YAML** - Frontmatter metadata

### External Services

- Google Calendar API - Event monitoring
- Gmail API - Email monitoring
- Slack API - Message monitoring
- Xero API - Accounting integration
- LinkedIn (web) - Social media posting
- X/Twitter (web) - Social media posting
- WhatsApp Web - Message monitoring

---

## Design Patterns

### 1. **Base Class Pattern** (Watchers)

```python
class BaseWatcher(ABC):
    @abstractmethod
    def check_for_updates() -> list:
        pass

    @abstractmethod
    def create_action_file(item) -> Path:
        pass

    def run(self):
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                logger.error(f"Error: {e}")
            time.sleep(self.check_interval)
```

**Why:** Consistent interface, reusable error handling, easy to extend

### 2. **State File Pattern** (Approval Workflow)

Instead of database, use file location as state:
- `/Pending_Approval/` = waiting for approval
- `/Approved/` = approved, ready to execute
- `/Rejected/` = denied by human
- `/Done/` = successfully completed
- `/Failed/` = execution failed

**Why:** No database overhead, visual state, easy to debug

### 3. **Process Manager Pattern** (Orchestration)

```python
class Process:
    def start(self):
        self.process = subprocess.Popen([...])
        self.start_count += 1

    def is_running(self) -> bool:
        return self.process.poll() is None

    def restart(self):
        if self.is_running():
            self.stop()
        self.start()
```

**Why:** Encapsulates process lifecycle, enables health monitoring

### 4. **Singleton Pattern** (Audit Logger)

```python
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
```

**Why:** Single log file handle, thread-safe access, easy to use

### 5. **Retry with Exponential Backoff** (Action Execution)

```python
RETRY_DELAYS = [0, 30, 60]  # seconds

for attempt in range(MAX_RETRIES):
    if attempt > 0:
        time.sleep(RETRY_DELAYS[attempt])

    result = execute_action()
    if result.success:
        return True
```

**Why:** Handle transient failures, avoid overwhelming services

---

## Integration Points

### 1. Google Calendar API
- **OAuth 2.0** authentication
- **Scopes:** `calendar.readonly`
- **Polling:** Every 5 minutes
- **Filter:** Events 1-48 hours ahead

### 2. Gmail API
- **OAuth 2.0** authentication
- **Scopes:** `gmail.readonly`
- **Polling:** Every 2 minutes
- **Filter:** `is:unread is:important`

### 3. Slack API
- **OAuth 2.0** authentication
- **Scopes:** `channels:history`, `channels:read`
- **Polling:** Every 1 minute
- **Filter:** Keyword matches in monitored channel

### 4. Xero API
- **OAuth 2.0** authentication
- **Scopes:** Accounting read/write
- **Polling:** Every 5 minutes
- **Events:** New invoices, bills, payments, large transactions

### 5. WhatsApp Web (Playwright)
- **No API** - browser automation
- **Authentication:** QR code scan (once)
- **Session:** Persistent in `assets/session/`
- **Polling:** Every 30 seconds
- **Requirement:** Visible browser (anti-automation detection)

### 6. LinkedIn (Playwright)
- **No API** - browser automation
- **Authentication:** Username/password (once)
- **Session:** Persistent in `assets/session/`
- **Character Limit:** 3000 characters
- **Approval:** Required for all posts

---

## Security Architecture

### 1. Credential Management
- **Storage:** `watchers/credentials/` (gitignored)
- **Format:** JSON files with OAuth tokens
- **Refresh:** Automatic token refresh via refresh_token
- **Access:** Read-only by watchers, never committed to git

### 2. Approval Workflow (Human-in-the-Loop)
- **Trigger:** All social media posts, emails, payments
- **Process:** File in `/Pending_Approval` until human moves to `/Approved`
- **Timeout:** 24 hours default expiration
- **Audit:** All approvals logged to audit trail

### 3. Audit Logging
- **Format:** `audit_YYYY-MM-DD.json`
- **Content:** Every action with timestamp, actor, target, parameters, result
- **Retention:** 90 days minimum
- **Access:** Read-only logs, append-only writes

### 4. No Sensitive Data in Logs
- **DO log:** Action types, targets, timestamps, results
- **DON'T log:** Passwords, API keys, full email/message content
- **Truncate:** Message previews to 200 characters

### 5. Process Isolation
- Each watcher runs in separate process
- Failure of one watcher doesn't affect others
- Orchestrator restart doesn't kill watchers (separate processes)

---

## Scalability & Performance

### Current Capacity
- **6 concurrent watchers** running 24/7
- **~100 tasks/day** created across all watchers
- **~10 approvals/week** processed
- **Memory footprint:** ~15 MB per watcher
- **Total memory:** ~100 MB for full system

### Bottlenecks
1. **Polling intervals** - Lower intervals = more API calls
2. **File I/O** - Many small file operations (acceptable for current scale)
3. **Browser automation** - Playwright can be resource-intensive

### Scaling Strategies

**Horizontal Scaling:**
- Add more watchers for new sources
- Each watcher is independent
- No shared state between watchers

**Vertical Scaling:**
- Reduce polling intervals for faster detection
- Increase retry limits for reliability
- Add more concurrent approval processors

**Performance Optimizations:**
- Batch file operations when possible
- Cache API responses where appropriate
- Use headless mode for browser automation (except WhatsApp)

---

## Trade-offs & Decisions

### 1. Polling vs Webhooks
**Decision:** Polling
**Trade-off:**
- ✅ Pro: No port opening, no firewall issues, simpler setup
- ❌ Con: Higher latency (minutes), more API calls

### 2. File-based State vs Database
**Decision:** File-based state (markdown files)
**Trade-off:**
- ✅ Pro: Human-readable, easily editable, no DB overhead
- ❌ Con: Not suitable for high-volume (>10k tasks/day)

### 3. Playwright vs APIs
**Decision:** Playwright for social media
**Trade-off:**
- ✅ Pro: No API costs, avoid rate limits, no developer approval needed
- ❌ Con: More fragile (UI changes break it), higher resource usage

### 4. Separate Processes vs Threads
**Decision:** Separate processes for watchers
**Trade-off:**
- ✅ Pro: True isolation, one crash doesn't affect others
- ❌ Con: Higher memory overhead (~15 MB per process)

### 5. Local-first vs Cloud-based
**Decision:** Local-first (Obsidian vault)
**Trade-off:**
- ✅ Pro: Privacy-preserving, no cloud costs, works offline
- ❌ Con: Not accessible from other devices, manual backups needed

### 6. Auto-restart vs Manual Intervention
**Decision:** Auto-restart failed watchers
**Trade-off:**
- ✅ Pro: Self-healing, minimal manual intervention
- ❌ Con: Can mask underlying issues (repeated crashes)

### 7. Visible Browser for WhatsApp
**Decision:** Visible mode required
**Trade-off:**
- ✅ Pro: Only way to avoid WhatsApp anti-automation detection
- ❌ Con: Browser window visible on screen, can't run fully headless

---

## Conclusion

This architecture prioritizes:
1. **Reliability** - Auto-restart, fault tolerance, graceful degradation
2. **Privacy** - Local-first, no unnecessary cloud dependencies
3. **Simplicity** - File-based state, polling over webhooks
4. **Safety** - Human-in-the-loop for sensitive actions
5. **Observability** - Comprehensive logging and monitoring

The system successfully achieves Gold Tier status with full cross-domain integration, autonomous operation, and comprehensive audit logging.

---

**Architecture Version:** 1.0 (Gold Tier)
**Last Updated:** 2026-01-14
**Maintainer:** Personal AI Employee Project
