# Gold Tier Research: Technology Decisions

**Feature**: 002-gold-tier-ai-employee
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document consolidates all technology research decisions for Gold Tier implementation. Each decision includes rationale, alternatives considered, and implementation approach.

---

## Decision 1: Orchestrator Architecture - Process Management vs Threading

**Question**: Should watchers run as independent processes or as threads within orchestrator process?

**Decision**: Independent Python processes (not threads) for each watcher.

### Rationale

- **Process isolation**: If one watcher crashes (e.g., WhatsApp Web disconnect), other watchers continue running. Thread crash would terminate entire orchestrator.
- **Resource monitoring**: Each watcher has independent PID, CPU usage, memory usage tracked by orchestrator. Threads share process resources.
- **Independent restart**: Orchestrator can restart individual crashed watchers without affecting others. Thread crash requires entire process restart.
- **Language compatibility**: Playwright (WhatsApp watcher) runs in browser process, better isolated. Threading would conflict with Playwright's event loop.

### Alternatives Considered

1. **Threading**: Rejected because crashes affect all watchers, difficult to monitor per-thread CPU/memory, Playwright conflicts.
2. **Asyncio**: Rejected because existing watchers are synchronous scripts, would require complete rewrite, complex error handling.
3. **Docker containers**: Rejected for Gold tier (overhead, complexity). Reserved for Platinum tier cloud deployment.

### Implementation

`orchestrator.py` uses `subprocess.Popen` to launch each watcher script as independent process:
```python
process = subprocess.Popen(
    [sys.executable, watcher_script],
    stdout=log_file,
    stderr=log_file
)
```

Orchestrator maintains PID list, performs health checks via `psutil.Process(pid).is_running()` every 60 seconds. Crashed watchers restarted automatically. Watchdog monitors orchestrator PID.

---

## Decision 2: Watchdog Pattern - Separate Process vs Built-in Self-Healing

**Question**: Should watchdog be separate process that monitors orchestrator, or built-in self-healing within orchestrator?

**Decision**: Separate watchdog.py process that monitors orchestrator.py and restarts if crashed.

### Rationale

- **Survivability**: If orchestrator crashes due to bug or exception, separate watchdog can restart it. Built-in self-healing cannot recover from fatal crashes.
- **Simplicity**: Watchdog is simple: check orchestrator PID every 60 seconds, restart if not running. Built-in self-healing requires complex exception handling.
- **Hierarchy**: Watchdog → Orchestrator → Watchers. Single point of failure (watchdog) vs cascading failures.

### Alternatives Considered

1. **Built-in self-healing**: Rejected because fatal crashes (segfault, unhandled exception) terminate process before recovery code runs.
2. **systemd/supervisord**: Rejected because platform-specific (Linux) or requires additional software installation. Pure Python solution cross-platform.
3. **Windows Service**: Rejected because Windows-specific. Gold tier supports Windows, macOS, Linux.

### Implementation

`watchdog.py` runs as independent process. Reads orchestrator PID from `orchestrator.pid` file:
```python
while True:
    if not psutil.Process(orchestrator_pid).is_running():
        subprocess.run([sys.executable, 'orchestrator.py', 'start'])
    time.sleep(60)
```

Watchdog logs all restart attempts to `watchers/watchdog.log`.

---

## Decision 3: Ralph Wiggum Stop Hook - File Modification vs Promise Tag

**Question**: How should Ralph loop detect task completion - check if file moved to /Done, or detect promise tag in response?

**Decision**: File movement completion strategy (check if task file moved to /Done).

### Rationale

- **Explicit completion**: File movement is atomic and unambiguous. Promise tag detection can miss if tag formatting varies.
- **GUI visibility**: User can see files moving between folders in Obsidian. Promise tag is invisible in GUI.
- **Error handling**: If file processing fails, file stays in /Needs_Action (clear indicator). Promise tag requires parsing response text.

### Alternatives Considered

1. **Promise tag detection**: Rejected because tag formatting varies (ralph:done vs @done vs [DONE]), parsing errors, invisible in GUI.
2. **Counter decrement**: Rejected because requires state file, race conditions if multiple loops run concurrently.
3. **Timeout-only**: Rejected because doesn't detect early completion, wastes API calls.

### Implementation

Ralph loop Stop hook installed in Claude Code configuration (see official Ralph Wiggum repo). Stop hook triggers before Claude exit:
```python
# Stop hook pseudo-code
if target_file not in /Done:
    if iteration_count < max_iterations and elapsed_time < max_duration:
        block_exit()
        re_inject_prompt("Continue working until [file] moved to /Done")
    else:
        allow_exit()
        log("Ralph loop stopped: max iterations/duration reached")
```

Loop continues until file moved or max_iterations (10) or max_duration (30 min).

---

## Decision 4: Cross-Domain Event Correlation - Real-Time vs Batch Consolidation

**Question**: How should system correlate related events across watchers - real-time consolidation, or batch during processing?

**Decision**: Batch consolidation during Claude Code processing (task-processor skill).

### Rationale

- **Simplicity**: Watchers create action files independently. No cross-watcher communication during detection. Claude Code correlates during reasoning.
- **Flexibility**: Claude Code can use context to determine if events are related (e.g., same invoice ID, same customer, same timestamp).
- **Scalability**: Real-time consolidation requires shared state file with locks. Batch consolidation uses Claude's reasoning without locks.

### Alternatives Considered

1. **Real-time consolidation**: Rejected because requires shared deduplication state file with file locking, race conditions, complex error handling.
2. **Deduplication by event ID**: Rejected because events from different sources have different ID formats (Gmail message_id vs Xero invoice ID).
3. **Prevent duplicate creation**: Rejected because watchers run independently, cannot know what other watchers detected.

### Implementation

Watchers create action files independently with unique IDs. Claude Code task-processor skill:
1. Reads all files in `/Needs_Action`
2. Correlates related events by context: same customer name, same invoice number, similar timestamp
3. Consolidates into single Plan.md: "Process invoice #1234 from Xero + related email from Gmail"
4. Logs consolidation action to audit trail

---

## Decision 5: MCP Server Communication - stdio vs HTTP

**Question**: Should Claude Code invoke MCP servers via stdio (subprocess), or HTTP endpoints?

**Decision**: stdio (subprocess) for Gold tier, HTTP reserved for Platinum tier cloud deployment.

### Rationale

- **MCP protocol standard**: Model Context Protocol uses stdio by default. Official MCP SDK supports stdio.
- **Simplicity**: No HTTP server setup, no port management, no CORS issues. Subprocess invocation straightforward.
- **Local-only**: Gold tier is local-only (all processes on same machine). stdio optimized for local communication.

### Alternatives Considered

1. **HTTP endpoints**: Rejected for Gold tier because adds complexity (HTTP servers, port management, CORS). Reserved for Platinum tier where Cloud Agent communicates with Local Agent via HTTP.
2. **Named pipes**: Rejected because platform-specific (Windows named pipes vs Unix domain sockets).
3. **Message queue (Redis)**: Rejected because adds external dependency, overkill for local-only Gold tier.

### Implementation

MCP servers implement stdio interface. Claude Code Agent Skills invoke via subprocess:
```bash
node mcp-servers/gmail-mcp/dist/index.js
```

MCP servers read JSON-RPC requests from stdin, write responses to stdout. Each MCP server runs as independent subprocess per invocation (stateless).

---

## Decision 6: Xero Token Refresh - Proactive vs Reactive

**Question**: Should Xero OAuth token refresh proactively (before expiry), or reactively (after 401 error)?

**Decision**: Proactive refresh 5 minutes before 30-minute expiry.

### Rationale

- **Reliability**: Proactive refresh prevents failed API calls due to expired tokens. Reactive refresh causes temporary downtime.
- **User experience**: Proactive refresh is invisible to user. Reactive refresh causes brief outage (failed API calls → refresh → retry).
- **Audit trail**: Proactive refresh logged as "token_refresh_success" event. Reactive refresh logged as "auth_error → token_refresh_success".

### Alternatives Considered

1. **Reactive refresh**: Rejected because causes API call failures, temporary downtime, poor user experience.
2. **Every API call refresh**: Rejected because Xero has rate limits (1000 requests per day), unnecessary refresh wastes quota.
3. **Extend token lifetime**: Rejected because Xero OAuth 2.0 token expiry is 30 minutes (fixed by Xero, cannot extend).

### Implementation

Xero MCP server tracks token acquisition timestamp. Before each API call:
```python
if (current_time - token_acquisition_time) > 25 minutes:
    refresh_token()
    log("token_refresh_success")
```

If refresh fails (401, 400), create alert in `/Needs_Action`: "Xero authentication expired. Please re-authenticate."

---

## Decision 7: CEO Briefing Data Sources - Real-Time Query vs Cached State

**Question**: Should CEO briefing query live data from Xero API and /Done folder, or build from cached state files?

**Decision**: Query live data from Xero API and scan /Done folder (real-time).

### Rationale

- **Accuracy**: Live query ensures briefing uses current data (latest invoices, payments, revenue). Cached state may be stale.
- **No additional complexity**: No need to build/maintain state files. Xero API provides needed data. /Done folder already exists.
- **Weekly execution**: CEO briefing runs weekly (Sunday 7 AM). API overhead is minimal (1 query per week).

### Alternatives Considered

1. **Cached state files**: Rejected because requires maintaining state files, risk of staleness, additional complexity.
2. **Incremental updates**: Rejected because requires tracking last briefing timestamp, delta computation, complex error handling.
3. **User-provided data**: Rejected because manual data entry defeats purpose of autonomous briefing.

### Implementation

`ceo-briefing-generator` skill invoked every Sunday 7:00 AM via scheduled task (cron/Task Scheduler):
```python
# Query Xero API
invoices = xero_api.get_invoices(where="Date>=DateTime(-7days)")
payments = xero_api.get_payments()
revenue = xero_api.get_revenue()

# Scan /Done folder
completed_tasks = scan_folder("/Done")

# Scan /Logs
errors = scan_logs("/Logs", level="error")

# Read Business_Goals.md
targets = parse_business_goals()

# Generate briefing
briefing = generate_briefing(invoices, payments, revenue, completed_tasks, errors, targets)
save("/Briefings/YYYY-MM-DD_Monday_Briefing.md", briefing)
```

---

## Decision 8: Social Media Posting - Unified Approval vs Per-Platform Approval

**Question**: Should multi-platform posting use single approval file (unified), or separate approval per platform?

**Decision**: Single unified approval file with platform-specific sections.

### Rationale

- **User convenience**: User reviews one approval file, sees all platforms, approves once. Separate approvals require multiple reviews.
- **Consistency**: Same content posted to all platforms simultaneously. Separate approvals risk inconsistent content.
- **Audit trail**: Single approval file contains all platform decisions. Separate files scatter audit trail.

### Alternatives Considered

1. **Separate approvals per platform**: Rejected because user must review/approve multiple times, risk of inconsistency.
2. **Automatic cross-posting**: Rejected because user may want platform-specific edits (e.g., Instagram visual-focused, Twitter concise).
3. **Sequential approval**: Rejected because delays posting (approve LinkedIn → wait → approve Facebook → wait).

### Implementation

`social-media-manager` skill generates single approval file in `/Pending_Approval`:
```markdown
# Social Post: Announcement Title

## Common Content
**Title**: Business Achievement Announcement
**Body**: We're excited to announce...
**Hashtags**: #business #growth

## Platform-Specific Sections

### LinkedIn
**Header**: Professional header text
**Body**: [Common Content]
**Visibility**: Public

### Instagram
**Image Attachment**: /path/to/image.jpg
**Caption**: [Common Content]
**Hashtags**: #business #growth #visual

### Twitter/X
**Tweet**: [Common Content - character limited to 280]
**Character Count**: 245/280

### Facebook
**Post**: [Common Content]
**Community Tagging**: @BusinessPage
**Visibility**: Public

## Instructions
Move this file to /Approved to post to all platforms, or /Rejected to cancel.
```

---

## Decision 9: WhatsApp Session Persistence - Browser Profile vs QR Rescan

**Question**: How should WhatsApp Watcher handle session persistence - use persistent browser profile, or require QR rescan on each restart?

**Decision**: Persistent browser profile (user data directory) with QR scan only on first run.

### Rationale

- **Convenience**: User scans QR code once, session persists across browser restarts. QR rescan on every restart is impractical (30 sec check interval = 48 scans per day).
- **Reliability**: Playwright persists authenticated session in user data directory. Session remains valid until logout from phone.
- **User experience**: Background browser window stays open (visible mode per Xero TOS requirement). Session persists if browser restarts (crash, reboot).

### Alternatives Considered

1. **QR rescan on each restart**: Rejected because impractical (48 scans per day), poor UX, high friction.
2. **Headless mode with cookie persistence**: Rejected because Xero TOS requires visible browser (audit trail). WhatsApp Web also requires visible mode for hackathon compliance.
3. **WhatsApp Business API**: Rejected because requires business account verification, API approval process, API costs.

### Implementation

WhatsApp Watcher uses Playwright with persistent context:
```python
browser = playwright.chromium.launch_persistent_context(
    user_data_dir="./whatsapp_profile",
    headless=False
)
```

On first run, script prompts user to scan QR code. After scan, session saved to `whatsapp_profile` directory. On subsequent runs, browser loads saved session, automatically logged in.

---

## Decision 10: Audit Log Retention - Daily Rotation vs Single File

**Question**: Should audit logs use daily rotation (separate file per day), or single growing log file?

**Decision**: Daily rotation with 90-day retention (separate file per day: `YYYY-MM-DD.json`).

### Rationale

- **Performance**: Daily files prevent single large file (1000 actions/day × 90 days = 90,000 lines). Small files load faster.
- **Archive simplicity**: Delete files older than 90 days (file deletion). Single file requires parsing and truncation.
- **Query efficiency**: Query specific day by loading single file. Single file requires parsing entire file to filter by date.

### Alternatives Considered

1. **Single growing log file**: Rejected because performance degradation (file grows to 100+ MB), complex truncation, slow queries.
2. **Weekly rotation**: Rejected because weekly files still large (7000 actions), 90-day retention = 13 files.
3. **Database (SQLite)**: Rejected because violates file-based state principle (constitution), adds dependency, overkill for Gold tier.

### Implementation

MCP servers and watchers log to `/Logs/audit_YYYY-MM-DD.json` (daily file):
```python
log_entry = {
    "timestamp": "2026-01-17T12:34:56Z",
    "action_type": "send_email",
    "actor": "approval-processor",
    "target": "user@example.com",
    "parameters": {"subject": "Test", "body": "..."},
    "approval_status": "approved",
    "result": "success",
    "file_created": "/Done/EMAIL_123.md"
}

log_file = f"/Logs/audit_{datetime.now().strftime('%Y-%m-%d')}.json"
append_json(log_file, log_entry)
```

Scheduled cleanup task (runs daily at 3 AM):
```python
for log_file in glob("/Logs/audit_*.json"):
    if file_age_days(log_file) > 90:
        delete_file(log_file)
```

---

## Summary

**Total Technology Decisions**: 10

**Decision Distribution**:
- Orchestrator Architecture: 2 decisions (process management, watchdog pattern)
- Ralph Loop: 1 decision (completion detection)
- Event Correlation: 1 decision (batch consolidation)
- MCP Communication: 1 decision (stdio vs HTTP)
- Xero Integration: 1 decision (token refresh strategy)
- CEO Briefing: 1 decision (data source)
- Social Media: 1 decision (unified approval)
- WhatsApp: 1 decision (session persistence)
- Audit Logging: 1 decision (log rotation)

**All decisions aligned with constitutional principles**:
- ✅ Local-First: All processes run locally, no cloud deployment
- ✅ File-Based State: Logs stored as files, no database
- ✅ Multi-Tier Incremental: Builds on Silver tier architecture
- ✅ Human-in-the-Loop: Approval workflow maintained
- ✅ MCP External Action: All external actions via MCP servers

**Next Step**: Generate Phase 1 artifacts (data-model.md, contracts/, quickstart.md)
