# Implementation Plan: Gold Tier Personal AI Employee

**Branch**: `002-gold-tier-ai-employee` | **Date**: 2026-01-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-gold-tier-ai-employee/spec.md`

## Summary

Gold Tier builds upon Silver Tier (feature 001) to deliver a fully autonomous Digital FTE with 6+ coordinated watchers, 6+ MCP servers, comprehensive audit logging, Ralph Wiggum autonomous loop, and CEO briefing generation. The system proactively monitors personal and business domains, correlates cross-domain events, autonomously completes multi-step tasks, and provides weekly business audits with actionable insights.

**Primary Gold Tier Enhancements Over Silver Tier**:

1. **6+ Coordinated Watchers**: Gmail (2 min), WhatsApp (30 sec), Xero (5 min), Calendar (10 min), Slack (1 min), Filesystem (real-time)
2. **6+ MCP Servers**: Gmail send, Xero read/write, LinkedIn post, X/Twitter post, Facebook post, Instagram post
3. **Orchestrator + Watchdog**: Master process management with health monitoring and auto-restart
4. **Ralph Wiggum Loop**: Autonomous multi-step task completion with Stop hook pattern
5. **CEO Briefing**: Weekly Sunday 7 AM autonomous business audit and proactive recommendations
6. **Comprehensive Audit Logging**: 90-day structured JSON audit trail for all actions
7. **Cross-Domain Event Correlation**: Consolidate related events across watchers into unified plans

## Technical Context

**Language/Version**: Python 3.13+ (watchers, orchestrator), Node.js v24+ LTS (MCP servers)
**Primary Dependencies**:
- Python: google-auth, google-api-python-client, playwright, watchdog, requests, pyyaml, psutil
- Node.js: @modelcontextprotocol/sdk (TypeScript), axios, playwright, @slack/web-api
- External APIs: Gmail API, Xero Accounting API, LinkedIn API, Facebook Graph API, Instagram Graph API, Slack API, Google Calendar API
**Storage**: File-based (Obsidian vault markdown + JSON logs) - no database in Gold tier
**Testing**: Manual integration testing per plan.md, end-to-end test in tests/integration/test_gold_end_to_end.py
**Target Platform**: Windows 10/11+, macOS 12+, Linux (Ubuntu 20.04+, Debian 11+)
**Project Type**: Multi-process orchestrator with 6+ independent watcher scripts + MCP server architecture
**Performance Goals**:
- Watcher detection intervals: Gmail (2 min), WhatsApp (30 sec), Xero (5 min), Calendar (10 min), Slack (1 min), Filesystem (real-time <5 sec)
- System uptime: 99%+ over 7-day period (Watchdog auto-restart)
- Action file throughput: 1000+ files per day
- Dashboard update latency: <5 seconds after significant events
- MCP response time: <5 seconds for external actions
**Constraints**:
- CPU usage <30% during normal operation
- RAM usage <4GB with 6 watchers + orchestrator
- Local-first architecture: all data in Obsidian vault (no cloud storage except API calls)
- Human-in-the-loop: ALL sensitive actions (emails, social posts, payments) require approval
- OAuth token refresh every 30 minutes (Xero) or 60 minutes (other services)
**Scale/Scope**:
- 6+ watcher processes running concurrently
- 6+ MCP servers for external actions
- 1000+ action files per day processing capacity
- 90-day audit log retention (~1 GB storage)
- 28 success criteria across 10 user stories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Local-First & Data Sovereignty ✅ PASS

**Validation**: All system state (action files, logs, configuration, audit trail) stored in Obsidian vault on local storage. No cloud dependencies except API calls to external services (Gmail, Xero, Slack, social media). MCP servers run locally with local authentication. User retains full data ownership and can backup entire vault to any storage.

**Evidence**: FR-059 (local-first architecture), FR-056 (credentials stored locally, gitignored), FR-043 (folder structure in vault), FR-037 (audit logs in vault). All watchers create action files in /Needs_Action (local). All MCP servers invoked from local Claude Code instance.

### II. Agent Skills Architecture (MCP Integration) ✅ PASS

**Validation**: All AI functionality implemented as SKILL.md files in .claude/commands/ directory. Skills include: task-processor, approval-processor, dashboard-updater, ceo-briefing-generator, social-media-manager, financial-analyst, business-goals-manager. Each skill documented with input parameters, output format, usage examples, error handling. Claude Code invokes skills by name. Skills can compose other skills (e.g., social-media-manager calls linkedin-poster, facebook-mcp, instagram-mcp).

**Evidence**: FR-016 through FR-023 (all AI as Agent Skills), FR-029 (social-media-manager skill coordinates multi-platform posting). Each MCP server exposes tools with defined schemas for Claude Code to invoke via Agent Skills.

### III. Multi-Tier Incremental Architecture ✅ PASS

**Validation**: Gold Tier (feature 002) builds incrementally on Silver Tier (feature 001) which builds on Bronze Tier (feature 000). Each tier independently testable with clear success criteria. Silver validates: multi-watcher coordination, MCP integration, approval workflow, Plan.md reasoning, scheduled automation. Gold validates: 6+ watcher orchestration, 6+ MCP servers, orchestrator + watchdog, Ralph Wiggum loop, CEO briefing, comprehensive audit logging. No tier can be skipped. No breaking changes from Silver to Gold.

**Evidence**: Spec assumes Silver Tier completion (FR-001 through FR-029 extend Silver FRs). Gold adds: FR-009 through FR-015 (orchestrator + watchdog), FR-020 (CEO briefing), FR-037 through FR-042 (audit logging), FR-021 through FR-022 (Ralph loop). Architecture scales from 2 watchers (Silver) to 6 watchers (Gold) without reimplementation.

### IV. Watcher Pattern: Perception → Action File → Reasoning → Action ✅ PASS

**Validation**: All 6 watchers follow BaseWatcher pattern: check_for_updates() → create_action_file(metadata) → run() main loop. Watchers create action files in /Needs_Action with YAML frontmatter: type, source, priority, status, timestamp, payload. Claude Code processes action files via task-processor skill (Reasoning) and executes via MCP servers (Action). No bypassing Action File workflow.

**Evidence**: FR-001 through FR-008 (Watcher Layer requirements). BaseWatcher class defines standard interface (spec line 106). Action file format defined in spec (line 293). Deduplication via processed IDs (FR-004, spec line 203).

### V. File-Based State Management ✅ PASS

**Validation**: All system state stored as files in Obsidian vault. No database required for Gold tier. Action files (markdown with YAML), configuration (YAML), state tracking (JSON: watchers_state.json, processed IDs), logs (text + JSON), Dashboard.md, Company_Handbook.md, Business_Goals.md. User can inspect any state file with text editor or Obsidian GUI.

**Evidence**: FR-043 through FR-046 (folder structure and file management). Watchers persist processed IDs to JSON files (FR-004). Audit logs stored as daily JSON files (FR-037). Dashboard.md shows system status (FR-042).

### VI. Human-in-the-Loop Approval Workflow ✅ PASS

**Validation**: ALL sensitive actions (emails, social posts, payments, data deletions) route through /Pending_Approval → /Approved or /Rejected → /Done workflow. Approval files include: action details, context, impact, instructions. User reviews in Obsidian GUI, moves file to approve/reject. Approval-processor monitors /Approved every 5 minutes, executes actions via MCP servers. Zero auto-send threshold for Gold Tier (FR-035).

**Evidence**: FR-031 through FR-036 (approval workflow). US-001 acceptance scenario (draft email requires approval, spec line 22). US-003 acceptance scenario (social posts require approval, spec line 54). 100% approval requirement (FR-035).

### VII. Ralph Wiggum Autonomous Loop (Stop Hook Pattern) ✅ PASS

**Validation**: Ralph loop enables autonomous multi-step task completion. Stop hook intercepts Claude exit, checks completion criteria (file moved to /Done or max iterations), re-injects prompt if work remains. Loop continues until task complete or max iterations (default 10) or max duration (default 30 min). Stuck detection: same error 3x = escalate to human. Plan.md tracks execution: step_number, status, actual_time vs estimated_time.

**Evidence**: FR-021 through FR-022 (Ralph loop requirements). US-005 (autonomous multi-step task completion, spec line 76). Stop hook pattern documented in spec (line 193). Safety limits defined (max iterations, max duration, stuck detection).

### VIII. MCP Server External Action Layer ✅ PASS

**Validation**: All external actions execute via MCP servers. Gold Tier includes 6+ MCP servers: gmail-mcp, xero-mcp, linkedin-mcp, x-poster (Twitter/X), facebook-mcp, instagram-mcp. Each MCP server exposes tools with defined schemas. Claude Code Agent Skills invoke MCP tools via subprocess or HTTP. MCP servers handle authentication independently (OAuth 2.0). All MCP actions logged to /Logs/mcp_actions_YYYY-MM-DD.json.

**Evidence**: FR-024 through FR-030 (MCP server requirements). US-003 (multi-platform social media posting, spec line 43). FR-030 (execution only via approval-processor after human approval). MCP server list (spec line 437).

### Constitution Check Summary

**Result**: ✅ ALL PRINCIPLES SATISFIED

**Violations**: None

**Justifications**: Not applicable (no violations)

**Recommendation**: PROCEED to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/002-gold-tier-ai-employee/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── gmail-mcp-schema.json
│   ├── xero-mcp-schema.json
│   ├── linkedin-mcp-schema.json
│   ├── x-poster-mcp-schema.json
│   ├── facebook-mcp-schema.json
│   └── instagram-mcp-schema.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Gold Tier extends Silver Tier structure with orchestrator + 6 watchers + 6 MCP servers

watchers/
├── orchestrator.py              # Master process: launches and monitors all watchers
├── watchdog.py                  # Monitors orchestrator, restarts if crashed
├── orchestrator_cli.py          # CLI: status, stop, restart commands
├── orchestrator_config.json     # Configuration: enable/disable watchers, intervals
├── base_watcher.py              # Base class: check_for_updates(), create_action_file(), run()
├── gmail_watcher.py             # Gmail monitoring (2 min interval)
├── whatsapp_watcher.py          # WhatsApp Web monitoring (30 sec interval)
├── xero_watcher.py              # Xero accounting monitoring (5 min interval)
├── calendar_watcher.py          # Google Calendar monitoring (10 min interval)
├── slack_watcher.py             # Slack channel monitoring (1 min interval)
├── filesystem_watcher.py        # Inbox folder monitoring (real-time)
├── credentials/                 # OAuth tokens and API keys (gitignored)
│   ├── gmail_credentials.json
│   ├── xero_credentials.json
│   ├── slack_credentials.json
│   └── README.md                # Setup instructions for each credential
├── requirements.txt             # Python dependencies
└── logs/                        # Watcher log files with daily rotation
    ├── gmail_watcher_YYYY-MM-DD.log
    ├── whatsapp_watcher_YYYY-MM-DD.log
    ├── xero_watcher_YYYY-MM-DD.log
    ├── calendar_watcher_YYYY-MM-DD.log
    ├── slack_watcher_YYYY-MM-DD.log
    ├── filesystem_watcher_YYYY-MM-DD.log
    ├── orchestrator.log
    └── watchdog.log

mcp-servers/
├── gmail-mcp/                   # Gmail send MCP server (Node.js + TypeScript)
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts             # MCP server initialization
│   │   ├── tools/
│   │   │   └── send_email.ts    # send_email tool implementation
│   │   └── gmail-api.ts         # Gmail API integration
│   └── README.md
├── xero-mcp/                    # Xero accounting MCP server
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   ├── read_invoice.ts
│   │   │   ├── create_invoice.ts
│   │   │   ├── list_overdue.ts
│   │   │   └── query_transactions.ts
│   │   └── xero-api.ts          # Xero Accounting API integration (OAuth 2.0, 30-min refresh)
│   └── README.md
├── linkedin-mcp/                # LinkedIn posting MCP server
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   └── post_linkedin.ts
│   │   └── linkedin-api.ts
│   └── README.md
├── x-poster/                    # Twitter/X posting MCP server (Playwright automation)
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   └── post_tweet.ts
│   │   └── playwright-twitter.ts
│   └── README.md
├── facebook-mcp/                # Facebook posting MCP server
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   └── post_facebook.ts
│   │   └── facebook-api.ts
│   └── README.md
├── instagram-mcp/               # Instagram posting MCP server
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   └── post_instagram.ts
│   │   └── instagram-api.ts
│   └── README.md
└── README.md                    # MCP server setup and configuration guide

.claude/commands/                # Agent Skills (SKILL.md files)
├── task-processor.md            # Read /Needs_Action, consult Company_Handbook.md, create plans
├── approval-processor.md        # Monitor /Approved, execute via MCP servers
├── dashboard-updater.md         # Refresh Dashboard.md with current status
├── ceo-briefing-generator.md    # Weekly Sunday 7 AM business audit and briefing
├── social-media-manager.md      # Coordinate multi-platform posting
├── financial-analyst.md         # Analyze Xero data, cash flow, expenses
├── business-goals-manager.md    # Manage revenue targets, KPIs, active projects
├── email-handler.md             # Process email action files
├── xero-handler.md              # Process Xero action files
├── whatsapp-handler.md          # Process WhatsApp urgent messages
├── calendar-handler.md          # Process calendar events
├── slack-handler.md             # Process Slack keyword matches
└── file-handler.md              # Process filesystem drop zone files

scripts/
├── setup_auto_start.bat         # Windows Task Scheduler configuration
├── setup_auto_start.sh          # Cron configuration (Linux/macOS)
├── setup_credentials.bat        # OAuth credential setup wizard
└── health_check.py              # Manual health check script

tests/
├── integration/
│   └── test_gold_end_to_end.py  # End-to-end integration test
└── README.md                    # Testing guide

AI_Employee_Vault/               # Obsidian vault structure (local)
├── Dashboard.md                 # System status and activity log
├── Company_Handbook.md          # Business rules and decision guidelines
├── Business_Goals.md            # Revenue targets, KPIs, active projects
├── Inbox/                       # Drop zone for files
├── Needs_Action/                # Action files from watchers
├── Plans/                       # Plan.md files for complex tasks
│   ├── active/                  # Currently executing plans
│   └── archive/                 # Completed plans
├── Pending_Approval/            # Awaiting human review
├── Approved/                    # Ready to execute
├── Rejected/                    # Cancelled actions
├── Done/                        # Completed tasks (archive)
├── Failed/                      # Errors and failures
├── Logs/                        # Audit trail
│   ├── YYYY-MM-DD.json          # Daily structured logs
│   └── mcp_actions_YYYY-MM-DD.json
├── Briefings/                   # CEO briefing reports
│   └── YYYY-MM-DD_Monday_Briefing.md
└── Ralph/                       # Ralph Wiggum loop state
    └── active_tasks/            # Currently executing Ralph loops
```

**Structure Decision**: Gold Tier uses Option 1 (Single project structure) with multi-process architecture. Watchers run as independent Python processes managed by orchestrator.py. MCP servers run as independent Node.js processes. All state stored in Obsidian vault (file-based). No database required. This structure aligns with constitutional principles: local-first, file-based state, multi-process isolation for reliability.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

**Constitution Check passed with no violations. No complexity tracking required.**

---

## Phase 0: Research - Technology Decisions

This section documents all technology research decisions for Gold Tier implementation.

### Research Task 1: Orchestrator Architecture - Process Management vs Threading

**Question**: Should watchers run as independent processes or as threads within orchestrator process?

**Decision**: Independent Python processes (not threads) for each watcher.

**Rationale**:
- **Process isolation**: If one watcher crashes (e.g., WhatsApp Web disconnect), other watchers continue running. Thread crash would terminate entire orchestrator.
- **Resource monitoring**: Each watcher has independent PID, CPU usage, memory usage tracked by orchestrator. Threads share process resources.
- **Independent restart**: Orchestrator can restart individual crashed watchers without affecting others. Thread crash requires entire process restart.
- **Language compatibility**: Playwright (WhatsApp watcher) runs in browser process, better isolated. Threading would conflict with Playwright's event loop.

**Alternatives Considered**:
1. **Threading**: Rejected because crashes affect all watchers, difficult to monitor per-thread CPU/memory, Playwright conflicts.
2. **Asyncio**: Rejected because existing watchers are synchronous scripts, would require complete rewrite, complex error handling.
3. **Docker containers**: Rejected for Gold tier (overhead, complexity). Reserved for Platinum tier cloud deployment.

**Implementation**: `orchestrator.py` uses `subprocess.Popen` to launch each watcher script as independent process. Orchestrator maintains PID list, performs health checks via `psutil.Process(pid).is_running()` every 60 seconds. Crashed watchers restarted automatically. Watchdog monitors orchestrator PID.

### Research Task 2: Watchdog Pattern - Separate Process vs Built-in Self-Healing

**Question**: Should watchdog be separate process that monitors orchestrator, or built-in self-healing within orchestrator?

**Decision**: Separate watchdog.py process that monitors orchestrator.py and restarts if crashed.

**Rationale**:
- **Survivability**: If orchestrator crashes due to bug or exception, separate watchdog can restart it. Built-in self-healing cannot recover from fatal crashes.
- **Simplicity**: Watchdog is simple: check orchestrator PID every 60 seconds, restart if not running. Built-in self-healing requires complex exception handling.
- **Hierarchy**: Watchdog → Orchestrator → Watchers. Single point of failure (watchdog) vs cascading failures.

**Alternatives Considered**:
1. **Built-in self-healing**: Rejected because fatal crashes (segfault, unhandled exception) terminate process before recovery code runs.
2. ** systemd/supervisord**: Rejected because platform-specific (Linux) or requires additional software installation. Pure Python solution cross-platform.
3. **Windows Service**: Rejected because Windows-specific. Gold tier supports Windows, macOS, Linux.

**Implementation**: `watchdog.py` runs as independent process. Reads orchestrator PID from `orchestrator.pid` file. Checks `psutil.Process(orchestrator_pid).is_running()` every 60 seconds. If orchestrator not running, executes `python orchestrator.py start`. Watchdog logs all restart attempts to `watchers/watchdog.log`.

### Research Task 3: Ralph Wiggum Stop Hook - File Modification vs Promise Tag

**Question**: How should Ralph loop detect task completion - check if file moved to /Done, or detect promise tag in response?

**Decision**: File movement completion strategy (check if task file moved to /Done).

**Rationale**:
- **Explicit completion**: File movement is atomic and unambiguous. Promise tag detection can miss if tag formatting varies.
- **GUI visibility**: User can see files moving between folders in Obsidian. Promise tag is invisible in GUI.
- **Error handling**: If file processing fails, file stays in /Needs_Action (clear indicator). Promise tag requires parsing response text.

**Alternatives Considered**:
1. **Promise tag detection**: Rejected because tag formatting varies (ralph:done vs @done vs [DONE]), parsing errors, invisible in GUI.
2. **Counter decrement**: Rejected because requires state file, race conditions if multiple loops run concurrently.
3. **Timeout-only**: Rejected because doesn't detect early completion, wastes API calls.

**Implementation**: Ralph loop Stop hook installed in Claude Code configuration (see official Ralph Wiggum repo). Stop hook triggers before Claude exit. Hook checks: Is target file in /Done? If yes, allow exit. If no, block exit, re-inject prompt with context: "Task not complete. Continue working until [file] moved to /Done." Loop continues until file moved or max_iterations (10) or max_duration (30 min).

### Research Task 4: Cross-Domain Event Correlation - Real-Time vs Batch Consolidation

**Question**: How should system correlate related events across watchers - real-time consolidation, or batch during processing?

**Decision**: Batch consolidation during Claude Code processing (task-processor skill).

**Rationale**:
- **Simplicity**: Watchers create action files independently. No cross-watcher communication during detection. Claude Code correlates during reasoning.
- **Flexibility**: Claude Code can use context to determine if events are related (e.g., same invoice ID, same customer, same timestamp).
- **Scalability**: Real-time consolidation requires shared state file with locks. Batch consolidation uses Claude's reasoning without locks.

**Alternatives Considered**:
1. **Real-time consolidation**: Rejected because requires shared deduplication state file with file locking, race conditions, complex error handling.
2. **Deduplication by event ID**: Rejected because events from different sources have different ID formats (Gmail message_id vs Xero invoice ID).
3. **Prevent duplicate creation**: Rejected because watchers run independently, cannot know what other watchers detected.

**Implementation**: Watchers create action files independently with unique IDs. Claude Code task-processor skill reads all files in /Needs_Action, correlates related events by context: same customer name, same invoice number, similar timestamp. Consolidates into single Plan.md: "Process invoice #1234 from Xero + related email from Gmail". Logs consolidation action to audit trail.

### Research Task 5: MCP Server Communication - stdio vs HTTP

**Question**: Should Claude Code invoke MCP servers via stdio (subprocess), or HTTP endpoints?

**Decision**: stdio (subprocess) for Gold tier, HTTP reserved for Platinum tier cloud deployment.

**Rationale**:
- **MCP protocol standard**: Model Context Protocol uses stdio by default. Official MCP SDK supports stdio.
- **Simplicity**: No HTTP server setup, no port management, no CORS issues. Subprocess invocation straightforward.
- **Local-only**: Gold tier is local-only (all processes on same machine). stdio optimized for local communication.

**Alternatives Considered**:
1. **HTTP endpoints**: Rejected for Gold tier because adds complexity (HTTP servers, port management, CORS). Reserved for Platinum tier where Cloud Agent communicates with Local Agent via HTTP.
2. **Named pipes**: Rejected because platform-specific (Windows named pipes vs Unix domain sockets).
3. **Message queue (Redis)**: Rejected because adds external dependency, overkill for local-only Gold tier.

**Implementation**: MCP servers implement stdio interface. Claude Code Agent Skills invoke via subprocess: `node mcp-servers/gmail-mcp/dist/index.js`. MCP servers read JSON-RPC requests from stdin, write responses to stdout. Each MCP server runs as independent subprocess per invocation (stateless).

### Research Task 6: Xero Token Refresh - Proactive vs Reactive

**Question**: Should Xero OAuth token refresh proactively (before expiry), or reactively (after 401 error)?

**Decision**: Proactive refresh 5 minutes before 30-minute expiry.

**Rationale**:
- **Reliability**: Proactive refresh prevents failed API calls due to expired tokens. Reactive refresh causes temporary downtime.
- **User experience**: Proactive refresh is invisible to user. Reactive refresh causes brief outage (failed API calls → refresh → retry).
- **Audit trail**: Proactive refresh logged as "token_refresh_success" event. Reactive refresh logged as "auth_error → token_refresh_success".

**Alternatives Considered**:
1. **Reactive refresh**: Rejected because causes API call failures, temporary downtime, poor user experience.
2. **Every API call refresh**: Rejected because Xero has rate limits (1000 requests per day), unnecessary refresh wastes quota.
3. **Extend token lifetime**: Rejected because Xero OAuth 2.0 token expiry is 30 minutes (fixed by Xero, cannot extend).

**Implementation**: Xero MCP server tracks token acquisition timestamp. Before each API call, check if `(current_time - token_acquisition_time) > 25 minutes` (5 minutes before 30 min expiry). If yes, use refresh_token to obtain new access_token. Log refresh attempt to `/Logs/mcp_actions_YYYY-MM-DD.json`. If refresh fails (401, 400), create alert in /Needs_Action: "Xero authentication expired. Please re-authenticate."

### Research Task 7: CEO Briefing Data Sources - Real-Time Query vs Cached State

**Question**: Should CEO briefing query live data from Xero API and /Done folder, or build from cached state files?

**Decision**: Query live data from Xero API and scan /Done folder (real-time).

**Rationale**:
- **Accuracy**: Live query ensures briefing uses current data (latest invoices, payments, revenue). Cached state may be stale.
- **No additional complexity**: No need to build/maintain state files. Xero API provides needed data. /Done folder already exists.
- **Weekly execution**: CEO briefing runs weekly (Sunday 7 AM). API overhead is minimal (1 query per week).

**Alternatives Considered**:
1. **Cached state files**: Rejected because requires maintaining state files, risk of staleness, additional complexity.
2. **Incremental updates**: Rejected because requires tracking last briefing timestamp, delta computation, complex error handling.
3. **User-provided data**: Rejected because manual data entry defeats purpose of autonomous briefing.

**Implementation**: `ceo-briefing-generator` skill invoked every Sunday 7:00 AM via scheduled task (cron/Task Scheduler). Skill queries Xero API: `GET /Invoices?where=Date>=DateTime(-7days)`, `GET /Payments`, `GET /Revenue`. Scans `/Done` folder for completed tasks (markdown files). Scans `/Logs` for errors and warnings. Reads `Business_Goals.md` for targets. Generates `YYYY-MM-DD_Monday_Briefing.md` in `/Briefings` folder with sections: Executive Summary, Weekly Revenue (total + MTD vs target + trend), Completed Tasks (count by category), Bottlenecks, Proactive Suggestions.

### Research Task 8: Social Media Posting - Unified Approval vs Per-Platform Approval

**Question**: Should multi-platform posting use single approval file (unified), or separate approval per platform?

**Decision**: Single unified approval file with platform-specific sections.

**Rationale**:
- **User convenience**: User reviews one approval file, sees all platforms, approves once. Separate approvals require multiple reviews.
- **Consistency**: Same content posted to all platforms simultaneously. Separate approvals risk inconsistent content.
- **Audit trail**: Single approval file contains all platform decisions. Separate files scatter audit trail.

**Alternatives Considered**:
1. **Separate approvals per platform**: Rejected because user must review/approve multiple times, risk of inconsistency.
2. **Automatic cross-posting**: Rejected because user may want platform-specific edits (e.g., Instagram visual-focused, Twitter concise).
3. **Sequential approval**: Rejected because delays posting (approve LinkedIn → wait → approve Facebook → wait).

**Implementation**: `social-media-manager` skill generates single approval file in `/Pending_Approval`: `social_post_YYYY-MM-DDTHH-MM-SS.md`. Approval file contains: common content (title, body, hashtags), platform-specific sections (LinkedIn: professional header, Instagram: image attachment, Twitter: character count validation, Facebook: community tagging). User edits as needed, moves to `/Approved`. `approval-processor` reads file, posts to all platforms via respective MCP servers, moves file to `/Done` with platform-specific post IDs and timestamps.

### Research Task 9: WhatsApp Session Persistence - Browser Profile vs QR Rescan

**Question**: How should WhatsApp Watcher handle session persistence - use persistent browser profile, or require QR rescan on each restart?

**Decision**: Persistent browser profile (user data directory) with QR scan only on first run.

**Rationale**:
- **Convenience**: User scans QR code once, session persists across browser restarts. QR rescan on every restart is impractical (30 sec check interval = 48 scans per day).
- **Reliability**: Playwright persists authenticated session in user data directory. Session remains valid until logout from phone.
- **User experience**: Background browser window stays open (visible mode per Xero TOS requirement). Session persists if browser restarts (crash, reboot).

**Alternatives Considered**:
1. **QR rescan on each restart**: Rejected because impractical (48 scans per day), poor UX, high friction.
2. **Headless mode with cookie persistence**: Rejected because Xero TOS requires visible browser (audit trail). WhatsApp Web also requires visible mode for hackathon compliance.
3. **WhatsApp Business API**: Rejected because requires business account verification, API approval process, API costs.

**Implementation**: WhatsApp Watcher uses Playwright with persistent context: `browser = playwright.chromium.launch_persistent_context(user_data_dir="./whatsapp_profile")`. On first run, script prompts user to scan QR code (browser window opens to WhatsApp Web QR page). After scan, session saved to `whatsapp_profile` directory. On subsequent runs, browser loads saved session, automatically logged in. If session expired (remote logout), script detects QR code page, creates alert in /Needs_Action, waits for user to rescan.

### Research Task 10: Audit Log Retention - Daily Rotation vs Single File

**Question**: Should audit logs use daily rotation (separate file per day), or single growing log file?

**Decision**: Daily rotation with 90-day retention (separate file per day: `YYYY-MM-DD.json`).

**Rationale**:
- **Performance**: Daily files prevent single large file (1000 actions/day × 90 days = 90,000 lines). Small files load faster.
- **Archive simplicity**: Delete files older than 90 days (file deletion). Single file requires parsing and truncation.
- **Query efficiency**: Query specific day by loading single file. Single file requires parsing entire file to filter by date.

**Alternatives Considered**:
1. **Single growing log file**: Rejected because performance degradation (file grows to 100+ MB), complex truncation, slow queries.
2. **Weekly rotation**: Rejected because weekly files still large (7000 actions), 90-day retention = 13 files.
3. **Database (SQLite)**: Rejected because violates file-based state principle (constitution), adds dependency, overkill for Gold tier.

**Implementation**: MCP servers and watchers log to `/Logs/audit_YYYY-MM-DD.json` (daily file). File created on first action of day. Log entry format: JSON object with `timestamp` (ISO 8601), `action_type`, `actor`, `target`, `parameters`, `approval_status`, `result`, `file_created`. Scheduled cleanup task (runs daily at 3 AM) scans `/Logs/`, deletes files older than 90 days, optionally compresses files older than 30 days to `/Logs/Archive/YYYY-MM.tar.gz`.

### Research Summary

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
- Local-First: All processes run locally, no cloud deployment
- File-Based State: Logs stored as files, no database
- Multi-Tier Incremental: Builds on Silver tier architecture
- Human-in-the-Loop: Approval workflow maintained
- MCP External Action: All external actions via MCP servers

---

## Phase 1: Design - Data Model & Contracts

This section will be generated after Phase 0 research is complete. Expected outputs:

- `research.md`: Consolidated research decisions (already documented in Phase 0 section above)
- `data-model.md`: Entity definitions, relationships, validation rules
- `contracts/`: MCP server tool schemas (JSON-RPC)
- `quickstart.md`: Setup and configuration guide

### Data Model (Draft)

**Entities to Define**:

1. **Action File** (spec line 293)
2. **Approval Request** (spec line 295)
3. **Plan** (spec line 297)
4. **Audit Log Entry** (spec line 299)
5. **Watcher Process** (spec line 301)
6. **Business Goal** (spec line 303)

**Relationships**:
- Action File → Approval Request (many-to-one: multiple action files can require approval)
- Action File → Plan (many-to-one: multiple action files consolidated into single plan)
- Plan → Audit Log Entry (one-to-many: plan execution generates multiple audit entries)
- Watcher Process → Action File (one-to-many: watcher creates multiple action files)
- Business Goal → CEO Briefing (many-to-many: briefing references multiple goals)

### MCP Server Contracts (Draft)

**MCP Servers to Define**:

1. **gmail-mcp**: `send_email` tool
2. **xero-mcp**: `read_invoice`, `create_invoice`, `list_overdue`, `query_transactions` tools
3. **linkedin-mcp**: `post_linkedin` tool
4. **x-poster**: `post_tweet` tool
5. **facebook-mcp**: `post_facebook` tool
6. **instagram-mcp**: `post_instagram` tool

**Tool Schema Format** (JSON-RPC):
```json
{
  "name": "send_email",
  "description": "Send email via Gmail API",
  "inputSchema": {
    "type": "object",
    "properties": {
      "to": {"type": "string", "description": "Recipient email address"},
      "subject": {"type": "string", "description": "Email subject"},
      "body": {"type": "string", "description": "Email body (HTML or plain text)"},
      "attachments": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to attach"}
    },
    "required": ["to", "subject", "body"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "message_id": {"type": "string"},
      "error": {"type": "string"}
    }
  }
}
```

---

## Implementation Sequence

**Gold Tier Implementation Phases** (40+ hours total):

### Phase 1: Orchestrator & Watchdog Foundation (6-8 hours)
**Goal**: Launch and monitor 6 watcher processes with auto-restart

**Tasks**:
- Implement `orchestrator.py` with `MultiWatcherManager` class
- Implement `watchdog.py` with orchestrator monitoring
- Implement `orchestrator_cli.py` with status/stop/restart commands
- Create `orchestrator_config.json` with enable/disable and interval settings
- Add health checks (PID validation, log freshness, CPU usage)
- Test orchestrator launches all 6 watchers
- Test watcher crash detection and auto-restart
- Test watchdog detects orchestrator crash and restarts

**Deliverables**:
- `watchers/orchestrator.py` (200 lines)
- `watchers/watchdog.py` (100 lines)
- `watchers/orchestrator_cli.py` (150 lines)
- `watchers/orchestrator_config.json` (50 lines)
- Health monitoring logic (CPU, PID, logs)

### Phase 2: Complete All 6 Watchers (10-12 hours)
**Goal**: 6 independent watchers detecting events and creating action files

**Tasks**:
- Implement `calendar_watcher.py` (10 min interval, 1-48 hours ahead events)
- Implement `slack_watcher.py` (1 min interval, keyword monitoring)
- Enhance existing watchers (Gmail, WhatsApp, Xero, Filesystem) from Silver tier
- Add deduplication logic (processed IDs tracking)
- Add health status reporting to orchestrator
- Test each watcher independently
- Test all 6 watchers running concurrently
- Test deduplication (same event from multiple watchers)

**Deliverables**:
- `watchers/calendar_watcher.py` (150 lines)
- `watchers/slack_watcher.py` (150 lines)
- Enhanced `gmail_watcher.py`, `whatsapp_watcher.py`, `xero_watcher.py`, `filesystem_watcher.py`
- Deduplication logic in orchestrator
- Integration tests for all 6 watchers

### Phase 3: Implement 6 MCP Servers (12-15 hours)
**Goal**: 6 MCP servers for external actions (Gmail, Xero, LinkedIn, Twitter, Facebook, Instagram)

**Tasks**:
- Create `gmail-mcp` server with `send_email` tool
- Create `xero-mcp` server with `read_invoice`, `create_invoice`, `list_overdue`, `query_transactions` tools
- Create `linkedin-mcp` server with `post_linkedin` tool
- Create `x-poster` server with `post_tweet` tool (Playwright automation)
- Create `facebook-mcp` server with `post_facebook` tool
- Create `instagram-mcp` server with `post_instagram` tool
- Add OAuth 2.0 authentication (Gmail, Xero, LinkedIn, Facebook, Instagram)
- Add error handling and logging to `/Logs/mcp_actions_YYYY-MM-DD.json`
- Test each MCP server independently with MCP Client
- Test approval-processor invokes MCP servers correctly

**Deliverables**:
- 6 MCP server packages (Node.js + TypeScript)
- OAuth authentication for all services
- MCP server README files with setup instructions
- Integration tests for MCP server invocation

### Phase 4: Ralph Wiggum Loop Implementation (4-5 hours)
**Goal**: Autonomous multi-step task completion with Stop hook

**Tasks**:
- Install Ralph Wiggum Stop hook (see official repo)
- Configure Stop hook with completion criteria (file movement to /Done)
- Add safety limits (max_iterations=10, max_duration=30 min)
- Add stuck detection (same error 3x = escalate)
- Create test Plan.md with 3+ steps
- Test Ralph loop autonomously completes all steps
- Test max_iterations stops loop
- Test stuck detection escalates to human

**Deliverables**:
- Ralph Wiggum Stop hook installed
- Stop hook configuration file
- Test Plan.md files
- Ralph loop integration tests

### Phase 5: CEO Briefing Generator (5-6 hours)
**Goal**: Weekly Sunday 7 AM autonomous business audit and briefing

**Tasks**:
- Implement `ceo-briefing-generator` Agent Skill
- Query Xero API for weekly revenue, invoices, payments
- Scan `/Done` folder for completed tasks
- Scan `/Logs` for errors and warnings
- Read `Business_Goals.md` for targets and KPIs
- Generate briefing sections: Executive Summary, Weekly Revenue, Completed Tasks, Bottlenecks, Proactive Suggestions
- Create scheduled task (cron/Task Scheduler) for Sunday 7 AM execution
- Test briefing generation with test data
- Test scheduled execution

**Deliverables**:
- `.claude/commands/ceo-briefing-generator.md` Agent Skill
- CEO briefing template
- Scheduled task configuration
- Sample briefing output

### Phase 6: Comprehensive Audit Logging (3-4 hours)
**Goal**: 90-day structured audit trail for all actions

**Tasks**:
- Define audit log entry schema (JSON format)
- Implement audit logging in all MCP servers
- Implement audit logging in all watchers
- Implement audit logging in orchestrator
- Implement daily log rotation (`audit_YYYY-MM-DD.json`)
- Implement 90-day retention cleanup task
- Test audit log completeness (100% actions logged)
- Test log rotation and cleanup

**Deliverables**:
- Audit log schema specification
- Audit logging code in all components
- Daily log rotation logic
- Cleanup scheduled task
- Audit log query tool (CLI)

### Phase 7: Polish, Documentation & Testing (5-6 hours)
**Goal**: Complete documentation, end-to-end testing, demo preparation

**Tasks**:
- Create `data-model.md` with entity definitions
- Create `contracts/` with MCP server schemas
- Create `quickstart.md` with setup guide
- Update README.md with Gold Tier content
- Create end-to-end integration test
- Verify all 28 success criteria from spec.md
- Record demo video (10-15 minutes) showing full Gold Tier workflow
- Create UPGRADE_GUIDE.md: Silver → Gold migration

**Deliverables**:
- `specs/002-gold-tier-ai-employee/data-model.md`
- `specs/002-gold-tier-ai-employee/contracts/*` (6 MCP schemas)
- `specs/002-gold-tier-ai-employee/quickstart.md`
- Updated README.md
- Integration test suite
- Demo video
- UPGRADE_GUIDE.md

**Total Estimated Time**: 40-50 hours (aligns with Gold Tier estimate in Requirements2.md)

---

## Risk Mitigation

**High-Severity Risks from Spec** (lines 503-542):

### RISK-001: OAuth Token Expiration Leading to System Downtime
**Mitigation**:
- Proactive token refresh 5 minutes before expiry (Xero: 25 min, others: 55 min)
- Log all refresh attempts to `/Logs/mcp_actions_YYYY-MM-DD.json`
- Create high-priority alert in Dashboard.md if refresh fails
- Send email notification (if Gmail MCP still functional)
- Graceful degradation: pause watcher, queue events locally, retry hourly

### RISK-002: Accidental Posting of Sensitive Information to Social Media
**Mitigation**:
- Keyword scanning in `social-media-manager` skill for sensitive terms (configurable in `Company_Handbook.md`)
- Prominent warning in approval file if sensitive keywords detected
- Require explicit checkbox: "☐ I confirm this post contains no confidential information"
- User must edit post to remove sensitive terms before approval

### RISK-003: WhatsApp Session Logout Causing Missed Urgent Messages
**Mitigation**:
- Watcher detects logout within 30 seconds (QR code page appears)
- Creates urgent alert in `/Needs_Action` with notification
- Dashboard.md shows prominent "WhatsApp Disconnected" alert
- Consider SMS/email backup notification if available
- Persistent browser profile reduces rescans to once (session persists across restarts)

### RISK-004: Corrupted Vault Files Due to Concurrent Access
**Mitigation**:
- Atomic file writes (write to temp file, then move)
- File locking where possible (use `fcntl` on Unix, `msvcrt.locking` on Windows)
- Retry on write failures with exponential backoff (1s, 2s, 4s up to 60s)
- Maintain file checksums for critical files (`Company_Handbook.md`, `Business_Goals.md`)

**Additional Gold Tier Risks**:

### RISK-GOLD-001: Orchestrator Crash Causing All Watchers to Stop
**Mitigation**: Watchdog monitors orchestrator PID, restarts within 60 seconds. Orchestrator logs crash reason to `orchestrator.log`. User alerted via Dashboard.md.

### RISK-GOLD-002: MCP Server Unreachable Causing Approval Failures
**Mitigation**: Approval-processor queues failed actions, retries with exponential backoff (3 attempts). Moves to `/Failed` after retries exhausted. Logs all failures to audit trail.

### RISK-GOLD-003: Ralph Loop Infinite Iteration Causing API Cost Overrun
**Mitigation**: Max iterations (10) and max duration (30 min) hard limits. Stuck detection (same error 3x = escalate). Dashboard shows active Ralph loops with iteration count.

### RISK-GOLD-004: CEO Briefing Generation Failure Due to Xero API Downtime
**Mitigation**: Scheduled task retries 3 times with 5-minute delays. If all retries fail, creates alert in `/Needs_Action`, logs error, waits until next week.

---

## Success Criteria Validation

**All 28 Success Criteria from spec.md** (lines 305-350):

### Core Functionality (Must-Have)
- ✅ **SC-001**: All 6 Watchers detect events within specified intervals (tested in Phase 2)
- ✅ **SC-002**: 99%+ uptime for Watcher processes over 7-day period (tested in Phase 1)
- ✅ **SC-003**: Action files created in correct format with valid YAML frontmatter (tested in Phase 2)
- ✅ **SC-004**: Approval workflow completes end-to-end within 10 minutes (tested in Phase 3)
- ✅ **SC-005**: Ralph Wiggum loop completes multi-step tasks 95%+ of time (tested in Phase 4)
- ✅ **SC-006**: All actions (100%) logged to audit trail (tested in Phase 6)
- ✅ **SC-007**: OAuth tokens refresh automatically 99%+ of time (tested in Phase 3)

### Business Value (ROI Metrics)
- ✅ **SC-008**: User spends <30 min/day reviewing Dashboard and approvals (measured during testing)
- ✅ **SC-009**: Email response time improves by 50% (baseline established during testing)
- ✅ **SC-010**: Zero missed financial deadlines (tested with Xero watcher overdue detection)
- ✅ **SC-011**: CEO briefing generated every Sunday 7 AM with complete data (tested in Phase 5)
- ✅ **SC-012**: Social media consistency improves to 3+ posts/week (tested in Phase 3)
- ✅ **SC-013**: System identifies 1+ cost optimization opportunity/month (tested in Phase 5)

### Quality & Reliability
- ✅ **SC-014**: Error recovery succeeds 90%+ of time (tested in Phase 6)
- ✅ **SC-015**: Zero duplicate action files for same event (tested in Phase 2)
- ✅ **SC-016**: Zero accidental executions without approval (tested in Phase 3)
- ✅ **SC-017**: Dashboard.md updated within 5 minutes of significant event (tested in Phase 1)
- ✅ **SC-018**: Log files remain under 10 MB/day (tested in Phase 6)
- ✅ **SC-019**: System handles peak load of 100+ events/day (load testing in Phase 7)

### User Experience
- ✅ **SC-020**: User can start all watchers with single command (tested in Phase 1)
- ✅ **SC-021**: Approval requests clear and actionable (usability testing in Phase 7)
- ✅ **SC-022**: 90%+ of social posts require minimal editing (quality testing in Phase 3)
- ✅ **SC-023**: Users complete setup in under 2 hours (documented in quickstart.md)
- ✅ **SC-024**: System startup after reboot <2 minutes (tested in Phase 1)

### Scalability & Maintainability
- ✅ **SC-025**: Adding new Watcher requires <200 lines of Python code (documented in Phase 7)
- ✅ **SC-026**: Individual Watchers disabled via config (tested in Phase 1)
- ✅ **SC-027**: Architecture supports Platinum tier upgrade (validated in design)
- ✅ **SC-028**: Audit logs queryable by date/action/actor/result (tested in Phase 6)

---

## Upgrade Path to Platinum Tier

**Gold Tier (002) → Platinum Tier (003)**:

**Platinum Tier Adds** (from Requirements2.md lines 180-200):
1. **24/7 Cloud Deployment**: Oracle/AWS cloud VM with always-on watchers
2. **Work-Zone Specialization**:
   - Cloud owns: Email triage + draft replies + social post drafts/scheduling
   - Local owns: approvals, WhatsApp session, payments/banking, final send/post actions
3. **Vault Synchronization**: Git or Syncthing sync between Cloud Agent and Local Agent
4. **Claim-by-Move Rule**: `/In_Progress/<agent>/` folder prevents double-work
5. **Odoo Community ERP**: Self-hosted local accounting (alternative to Xero)

**Gold Tier Architecture Ready for Platinum Upgrade**:
- ✅ File-based state (easily syncable via Git/Syncthing)
- ✅ Agent Skills (Cloud Agent and Local Agent share same skills)
- ✅ MCP servers (Cloud invokes local MCP via HTTP for sensitive actions)
- ✅ Audit logging (both Cloud and Local maintain audit trails)
- ✅ Approval workflow (Cloud creates drafts, Local approves/executes)

**Migration Complexity**: Low to Medium (estimated 20-30 hours for Gold → Platinum upgrade)

---

**Plan Status**: ✅ COMPLETE

**Next Steps**:
1. Generate Phase 1 artifacts: `data-model.md`, `contracts/`, `quickstart.md`
2. Update agent context via `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
3. Run `/sp.tasks` for Gold Tier to generate task breakdown
4. Begin implementation following Phase 1-7 sequence

**Branch**: `002-gold-tier-ai-employee`

**Plan File**: `specs/002-gold-tier-ai-employee/plan.md`

**Constitution**: `.specify/memory/constitution.md` (Version 1.0.0)

**Tier Progression**: Bronze (000) → Silver (001) → Gold (002) → Platinum (003)
