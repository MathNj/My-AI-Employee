# Research & Technology Decisions: Bronze Tier Foundation

**Feature**: Bronze Tier Foundation - Personal AI Employee
**Date**: 2026-01-17
**Status**: Complete

This document consolidates research findings and technology decisions for Bronze Tier implementation.

## Research Questions & Resolutions

### 1. Gmail API vs File System Watcher Trade-offs

**Question**: Which watcher should be the default recommendation for Bronze tier users?

**Decision**: Recommend **File System Watcher** for beginners, **Gmail Watcher** for users comfortable with OAuth

**Rationale**:
- File System Watcher has zero setup friction - drop file → immediate detection
- Gmail Watcher provides richer real-world use cases (email monitoring) but requires OAuth 2.0 setup
- Bronze tier goal is proving architecture viability, not specific trigger source
- Users can switch watchers without changing core architecture

**Alternatives Considered**:
- **File System only**: Simpler but limits real-world applicability
- **Gmail only**: More powerful but creates setup barrier for hackathon participants
- **Both required**: Too much complexity for 8-12 hour Bronze tier estimate

**Implementation**:
- Provide both implementations (gmail_watcher.py and filesystem_watcher.py)
- Document setup for each in quickstart.md
- Watcher uses abstract base class (base_watcher.py) so implementations are swappable
- User chooses ONE for Bronze tier, can add second in Silver tier

**References**:
- Gmail API Quickstart: https://developers.google.com/gmail/api/quickstart/python
- Python watchdog library: https://python-watchdog.readthedocs.io/

---

### 2. Action File Format: YAML Frontmatter vs Pure JSON

**Question**: What file format should action files use for metadata and payload?

**Decision**: **Markdown with YAML frontmatter**

**Rationale**:
- Human-readable when viewed in Obsidian (GUI) or text editor
- Git-friendly diffs (line-based, not nested JSON)
- Supports rich content in body (full email text, multi-line file contents)
- YAML frontmatter standard in static site generators, familiar to developers
- Obsidian natively renders markdown, making action files viewable in GUI

**Alternatives Considered**:
| Format | Pros | Cons |
|--------|------|------|
| Pure JSON | Machine-parseable, structured | Not human-readable, poor diffs, no rich body content |
| Pure YAML | Clean, readable | Limited body support, less familiar for non-devs |
| XML | Structured | Verbose, outdated, poor readability |
| Markdown + YAML frontmatter | Human-readable, rich content, git-friendly, Obsidian-native | Requires parsing library (python-frontmatter) |

**Schema Design**:
```yaml
---
type: email | file | scheduled
source: Gmail | FileSystem | Manual
timestamp: 2026-01-17T14:30:00Z (ISO 8601)
status: pending | processing | complete | error
payload:
  # Event-specific fields
  # Gmail: sender, subject, message_id, snippet
  # FileSystem: filename, path, size, mime_type
---

# Body content (markdown)
Full email text or file contents...
```

**Implementation**:
- Use python-frontmatter library for parsing
- Validate frontmatter schema in task-processor skill
- Body content supports markdown formatting for readability

**References**:
- python-frontmatter: https://pypi.org/project/python-frontmatter/
- YAML specification: https://yaml.org/spec/1.2.2/

---

### 3. Dashboard.md Update Strategy: Append vs Replace

**Question**: How should Dashboard.md activity log be updated - append new entries or replace entire file?

**Decision**: **Append-only (prepend to activity log section)** with manual archiving

**Rationale**:
- Simpler implementation - no file parsing required, just insert at marker
- Preserves full history (no data loss from rotation logic bugs)
- Faster writes (append is O(1), replace with parsing is O(n))
- Bronze tier appropriate - manual archiving acceptable for 8-12 hour MVP

**Alternatives Considered**:
| Strategy | Pros | Cons |
|----------|------|------|
| Append-only | Simple, fast, preserves history | Unbounded growth (mitigated by manual archiving) |
| Replace with rotation | Auto-archiving, bounded size | Complex parsing, risk of data loss, slower |
| Database | Structured queries, scalable | Overkill for Bronze, adds dependency |

**Implementation**:
```python
# Pseudocode for Dashboard update
def update_dashboard(entry):
    dashboard_path = vault_path / "Dashboard.md"
    content = dashboard_path.read_text()

    # Find activity log marker
    marker = "## Activity Log"
    insert_pos = content.find(marker) + len(marker) + 1

    # Prepend new entry (newest first)
    new_entry = f"\n- {entry.timestamp} | {entry.task_type} | {entry.outcome}\n"
    updated_content = content[:insert_pos] + new_entry + content[insert_pos:]

    # Atomic write
    dashboard_path.write_text(updated_content)
```

**Manual Archiving Process** (documented in TROUBLESHOOTING.md):
1. When Dashboard.md exceeds 1000 entries, create Logs/dashboard_archive_YYYY-MM-DD.md
2. Cut old entries from Dashboard.md, paste into archive
3. Keep most recent 100 entries in Dashboard.md for quick reference

---

### 4. Watcher Error Recovery: Retry vs Crash

**Question**: How should watcher scripts handle errors - retry indefinitely, crash immediately, or selective recovery?

**Decision**: **Log and continue** for transient errors, **crash on critical failures**

**Rationale**:
- Resilience to network glitches, API timeouts (common in real-world scenarios)
- Fail fast on configuration errors, permissions issues (user must fix these)
- Bronze tier includes manual monitoring - user checks logs and restarts if needed

**Error Classification**:

| Error Type | Recovery Strategy | Rationale |
|-----------|-------------------|-----------|
| Network timeout | Retry with exponential backoff | Transient, likely to resolve |
| API rate limit (429) | Exponential backoff + log | Expected behavior, not fatal |
| Authentication failure (OAuth expired) | Crash with clear error | Requires user intervention |
| Config file missing | Crash with instructions | User must create config |
| Permissions denied | Crash with diagnostics | User must fix filesystem/API permissions |
| Malformed API response | Log and skip, continue | Individual event failure, don't stop watcher |

**Implementation**:
```python
# Pseudocode for watcher main loop
while True:
    try:
        events = check_for_events()
        for event in events:
            try:
                create_action_file(event)
            except Exception as e:
                log_error(f"Failed to create action file: {e}")
                # Continue processing other events
    except CriticalError as e:
        log_error(f"CRITICAL: {e}")
        sys.exit(1)  # Crash with non-zero exit code
    except TransientError as e:
        log_error(f"Transient error: {e}, retrying...")
        backoff_sleep()
        continue

    sleep(check_interval)
```

**References**:
- Exponential backoff best practices: https://cloud.google.com/iot/docs/how-tos/exponential-backoff
- Python exception handling: https://docs.python.org/3/tutorial/errors.html

---

### 5. Claude Code Invocation: Manual vs Automated

**Question**: Should Claude Code be invoked automatically (orchestrator polling) or manually by user?

**Decision**: **Manual invocation** for Bronze tier

**Rationale**:
- Simpler - no orchestrator process to implement and debug
- Allows user to learn the system, inspect action files before processing
- Supports debugging - user can test one action file at a time
- Bronze tier time budget (8-12 hours) insufficient for orchestrator implementation
- Gold tier will add orchestrator + Ralph Wiggum loop for automation

**Workflow**:
1. Watcher creates action files in /Needs_Action
2. User opens Claude Code in vault directory
3. User invokes: `/task-processor` (Agent Skill)
4. Claude Code processes all action files, moves to /Done
5. User checks Dashboard.md for results

**Upgrade Path to Gold**:
- Silver tier: Add basic scheduling (cron/Task Scheduler runs task-processor hourly)
- Gold tier: Orchestrator polls /Needs_Action, invokes Claude Code automatically, Ralph Wiggum loop for multi-step tasks

**Implementation**:
- task-processor skill accepts vault_path as parameter
- Skill processes ALL action files in /Needs_Action (batch mode)
- User can run skill multiple times per day as needed

---

### 6. Python Dependency Management: venv vs Poetry vs pip

**Question**: What Python dependency management approach should Bronze tier use?

**Decision**: **Standard venv + requirements.txt**

**Rationale**:
- Universal compatibility - works on Windows, macOS, Linux without additional tools
- Minimal learning curve - Python developers already know venv
- Sufficient for Bronze tier - single watchers/ directory, few dependencies
- No complex dependency resolution needed (libraries are mature, stable)

**Alternatives Considered**:
| Tool | Pros | Cons |
|------|------|------|
| venv + requirements.txt | Universal, simple, standard | Manual version pinning, no lock file |
| Poetry | Lock files, dependency resolution, modern | Extra tool to install, learning curve |
| Conda | Environment + packages | Heavyweight, slow, not Python-specific |
| pip global | No setup needed | Conflicts, pollutes system Python |

**Implementation**:
```bash
# Setup documented in quickstart.md
cd watchers
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**requirements.txt contents**:
```
# Gmail Watcher option
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.116.0

# File System Watcher option
watchdog==4.0.0

# Common dependencies
pyyaml==6.0.1
python-frontmatter==1.1.0

# Testing (optional)
pytest==8.0.0
```

**Upgrade Path**: If Silver/Gold tier adds complexity (multiple packages, version conflicts), consider Poetry or Docker containers

---

### 7. Obsidian Vault Structure: Flat vs Nested

**Question**: Should Obsidian vault use flat folder structure or nested organization?

**Decision**: **Flat structure** with /Inbox, /Needs_Action, /Done, /Errors, /Logs at root

**Rationale**:
- Simplicity principle - Bronze tier validates architecture, not folder organization
- Easy file movement - drag/drop between folders in Obsidian GUI
- Simple file paths in watcher scripts - no need to traverse nested directories
- Aligns with Kanban board mental model (Inbox → Needs Action → Done)

**Alternatives Considered**:
| Structure | Pros | Cons |
|-----------|------|------|
| Flat (root-level folders) | Simple navigation, easy file movement | All files at root level (acceptable for Bronze scale) |
| Nested by date (/Done/2026/01/file.md) | Auto-organization, prevents clutter | Premature optimization, complex file paths |
| Tagged (Obsidian tags) | Flexible categorization | Requires Obsidian plugin, not visible in file system |
| Linked (Obsidian links between notes) | Rich relationships | Complex to maintain, not needed for Bronze |

**Vault Structure**:
```
[Vault Root]/
├── Dashboard.md               # Always at root for easy access
├── Company_Handbook.md        # Always at root for easy access
├── Inbox/                     # Drop zone for file system watcher
├── Needs_Action/              # Queue (watcher writes here)
├── Done/                      # Archive (Claude moves here)
├── Errors/                    # Malformed files (validation failures)
└── Logs/                      # Watcher logs, error logs
```

**Upgrade Path**: Silver/Gold tiers can add nested structure if volume grows:
- /Done/2026-01/ (monthly archives)
- /Needs_Action/priority_high/ (urgency-based routing)
- /Logs/watcher_name/ (per-watcher log directories)

---

### 8. Watcher Check Intervals: Aggressive vs Conservative

**Question**: How frequently should watchers check for new events?

**Decision**: **Conservative intervals** - File System: 30 sec, Gmail: 2-5 min

**Rationale**:
- Bronze tier is testing/learning environment, not production
- Avoids Gmail API quota issues (10,000 units/day = ~720 checks at 5 min intervals)
- Reduces battery drain on laptops, CPU load
- 30 sec file system check is responsive enough for manual testing
- 2-5 min email check covers most use cases (urgent emails use phone notifications anyway)

**Quota Analysis**:
```
Gmail API Quota: 10,000 units/day
Gmail check cost: ~5 units (list messages + metadata)
Max checks/day at intervals:
- 1 min: 1440 checks = 7,200 units (72% quota)
- 2 min: 720 checks = 3,600 units (36% quota) ← recommended
- 5 min: 288 checks = 1,440 units (14% quota) ← safe default
```

**Alternatives Considered**:
| Interval | Pros | Cons |
|----------|------|------|
| Aggressive (1 sec / 30 sec) | Near real-time | High CPU, API quota risk, battery drain |
| Conservative (30 sec / 2-5 min) | Resource-efficient, quota-safe | Slight detection delay (acceptable for Bronze) |
| Adaptive (adjust based on activity) | Optimal resource usage | Complex logic, premature optimization |

**Implementation**:
```yaml
# watcher_config.yaml
filesystem_watcher:
  check_interval_sec: 30
  watched_path: /path/to/vault/Inbox

gmail_watcher:
  check_interval_sec: 120  # 2 minutes
  max_results: 10  # Limit API response size
```

**Configurable**: User can adjust intervals in watcher_config.yaml for their use case (e.g., 1 min for urgent testing, 5 min for normal operation)

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| **Watcher Scripts** | Python | 3.13+ | Rich ecosystem (gmail API, watchdog), cross-platform, easy to learn, mature async support |
| **Memory/GUI** | Obsidian | 1.10.6+ | Local-first, markdown-native, visual GUI, mature plugin ecosystem, cross-platform |
| **Reasoning Engine** | Claude Code | Latest | Agent Skills architecture, proven for automation, good token efficiency, official CLI |
| **Action File Format** | Markdown + YAML | - | Human-readable, git-friendly, Obsidian-native, supports rich content |
| **Logging** | Python logging | Built-in | File rotation, configurable levels, standard library |
| **Configuration** | YAML | 1.2 | Human-readable, comments support, standard for Python projects |
| **Gmail API** | google-api-python-client | 2.116.0 | Official Google library, OAuth 2.0 support, well-documented |
| **File Watching** | watchdog | 4.0.0 | Cross-platform, event-driven, low CPU overhead, mature library |
| **Frontmatter Parsing** | python-frontmatter | 1.1.0 | Standard library for YAML frontmatter in markdown |
| **Testing** | pytest | 8.0.0 | De facto standard for Python testing, rich plugin ecosystem |

---

## Key Architectural Decisions

### 1. File-Based State Management

**Decision**: All state stored in file system (action files, logs, Dashboard.md), no database

**Justification**:
- Simpler to implement and debug (files are visible, inspectable)
- More transparent - user can see exactly what's happening
- Git-friendly - entire vault can be version controlled
- Validates Bronze tier assumption: file-based approach scales to 50 files/day
- No database setup friction (PostgreSQL install, schema migrations, connection pooling)

**Trade-offs**:
- Pros: Simple, transparent, debuggable, git-friendly, zero setup
- Cons: No structured queries, manual archiving, potential race conditions (mitigated by single Claude instance)

**Upgrade Path**: If Silver/Gold tier hits file system limits (>1000 files/day, complex queries needed), consider SQLite (embedded) or PostgreSQL (production)

### 2. Pull-Based Processing

**Decision**: Watcher creates action files, user invokes Claude Code to process (pull), not push

**Justification**:
- Bronze tier time budget (8-12 hours) insufficient for orchestrator
- Allows user to learn system, inspect action files before processing
- Supports debugging - process one file at a time, check results
- User maintains control - no autonomous behavior until Gold tier

**Trade-offs**:
- Pros: Simple, debuggable, user control, no orchestrator process
- Cons: Manual invocation required (acceptable for Bronze learning phase)

**Upgrade Path**:
- Silver tier: Basic scheduling (cron runs task-processor hourly)
- Gold tier: Orchestrator + watchdog for fully autonomous operation

### 3. Agent Skills Architecture

**Decision**: All Claude Code functionality implemented as SKILL.md files per hackathon rules

**Justification**:
- Hackathon requirement (all AI functionality must be Agent Skills)
- Provides structure, documentation, reusability
- Skills are invocable with consistent interface (skill name + parameters)
- Skills can be shared across projects (vault-setup skill reusable for any Obsidian setup)

**Skills for Bronze Tier**:
1. **vault-setup**: Initialize Obsidian vault structure (folders, Dashboard, Company_Handbook)
2. **task-processor**: Process action files from /Needs_Action, move to /Done
3. **dashboard-updater**: Refresh Dashboard.md with current status summary

**Trade-offs**:
- Pros: Structured, documented, reusable, hackathon-compliant, testable
- Cons: SKILL.md format has learning curve (but templates provided)

### 4. Local-First Philosophy

**Decision**: Obsidian vault on local disk, watchers run locally, Claude Code accesses local files

**Justification**:
- User maintains data sovereignty (no cloud storage required)
- Privacy - sensitive emails, business data stay on user's machine
- Offline-capable - system works without internet (except API calls)
- Aligns with hackathon emphasis on local-first architecture

**External Dependencies**:
- Gmail API (optional, only if Gmail watcher chosen)
- Claude API (required, for reasoning engine)
- No other cloud dependencies

**Trade-offs**:
- Pros: Privacy, offline-capable, user control, no subscription costs (except Claude)
- Cons: Not accessible from multiple devices (acceptable for Bronze single-user system)

### 5. Manual Scaling

**Decision**: No auto-rotation for logs, no auto-archiving for Dashboard, no auto-restart for watchers

**Justification**:
- Bronze tier is learning/testing phase, not production
- Manual management appropriate for 8-12 hour MVP
- Simpler implementation (no background jobs, no scheduled tasks)
- User learns system behavior through manual operations

**Manual Operations**:
- Log rotation: User manually archives when logs exceed 10MB
- Dashboard archiving: User manually cuts old entries when >1000 lines
- Watcher restart: User manually starts/stops watcher scripts

**Upgrade Path**: Silver/Gold tiers add automated log rotation, Dashboard archiving, watchdog process for auto-restart

---

## Risks & Mitigation

See plan.md Risk Mitigation Strategies section for comprehensive risk analysis.

**Critical Risks Addressed in Research**:
1. OAuth token expiration → Automatic refresh implemented in gmail_watcher.py
2. Gmail API quota → Conservative 2-5 min check interval (36% quota usage)
3. Watcher crashes → Comprehensive error logging with retry logic
4. File format incompatibility → YAML frontmatter (standard, well-supported)

---

## References

**Gmail API**:
- Quickstart: https://developers.google.com/gmail/api/quickstart/python
- OAuth 2.0: https://developers.google.com/gmail/api/auth/about-auth
- Python client: https://github.com/googleapis/google-api-python-client

**File System Watching**:
- watchdog docs: https://python-watchdog.readthedocs.io/
- Cross-platform events: https://python-watchdog.readthedocs.io/en/stable/api.html

**Obsidian**:
- Help docs: https://help.obsidian.md/
- Markdown format: https://help.obsidian.md/Editing+and+formatting/Basic+formatting+syntax

**Claude Code**:
- Agent Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- CLI docs: https://docs.anthropic.com/claude-code

**Python Libraries**:
- python-frontmatter: https://pypi.org/project/python-frontmatter/
- PyYAML: https://pyyaml.org/wiki/PyYAMLDocumentation
- Python logging: https://docs.python.org/3/library/logging.html

---

**Research Complete**: All technology decisions documented with rationale, alternatives, and implementation guidance. Ready for Phase 1 (design artifacts).
