# Implementation Plan: Bronze Tier Foundation - Personal AI Employee

**Branch**: `000-bronze-tier-foundation` | **Date**: 2026-01-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/000-bronze-tier-foundation/spec.md`

**Note**: This plan defines the implementation approach for Bronze Tier - the foundation that validates core architecture before adding Silver/Gold complexity.

## Summary

Bronze Tier establishes the minimum viable Personal AI Employee with three core components:

1. **Memory Layer**: Obsidian vault with Dashboard.md (activity tracking) and Company_Handbook.md (business rules) for local-first knowledge base
2. **Perception Layer**: ONE watcher script (Gmail OR File System) that autonomously detects events and creates action files in /Needs_Action
3. **Reasoning Layer**: Claude Code integration with read/write access to vault, processing action files via Agent Skills

**Technical Approach**: File-based workflow using Obsidian markdown for state management, Python watcher scripts for event detection, Claude Code Agent Skills for reasoning and action. Architecture validates: Perception → Memory → Reasoning → Action pipeline without complexity of multi-watcher orchestration, MCP servers, or approval workflows (deferred to Silver/Gold).

**Success Metric**: End-to-end test showing event detection → action file creation → Claude processing → completion file in /Done, with full activity history in Dashboard.md.

## Technical Context

**Language/Version**: Python 3.13+ (watcher scripts), Markdown (vault format), Claude Code CLI (reasoning engine)

**Primary Dependencies**:
- **Gmail Watcher option**: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
- **File System Watcher option**: watchdog
- **Common**: pyyaml, python-frontmatter, pathlib, logging

**Storage**: File system (local disk) for Obsidian vault, action files, logs. No database required.

**Testing**: Manual integration testing (Bronze tier focus on proving concept), pytest for watcher script unit tests (optional but recommended)

**Target Platform**: Cross-platform (Windows/macOS/Linux) with local Obsidian installation, Python 3.13+ runtime, Claude Code CLI authenticated

**Project Type**: Single project - automation scripts + knowledge base structure. No web/mobile components.

**Performance Goals**:
- Watcher check cycle: <5 seconds for File System, <120 seconds for Gmail
- Action file creation: <30 seconds from event detection
- Claude Code processing: <2 minutes per action file
- Dashboard update: <5 seconds

**Constraints**:
- Bronze tier time budget: 8-12 hours total implementation
- Single watcher only (not multiple)
- Manual watcher startup (no auto-boot)
- No MCP servers (deferred to Silver)
- No approval workflow (deferred to Silver)
- Work hours testing only (not 24/7)

**Scale/Scope**:
- Single user system
- 50 action files per day capacity
- Vault size: <1GB
- Dashboard activity log: <1000 entries before manual archiving
- Watcher logs: <10MB before manual rotation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution template is not populated in this project. Applying general best practices for Bronze Tier foundation:

### Principles Applied

✅ **Simplicity First**: Bronze tier implements minimal viable architecture - ONE watcher, no orchestration, no MCP servers. Proves concept before adding complexity.

✅ **Local-First**: All data stored in local Obsidian vault, no cloud dependencies except API calls (Gmail, Claude). User maintains full data control.

✅ **Testability**: Each component independently testable:
- Obsidian vault: Manual verification of structure
- Watcher: Test event → action file creation
- Claude Code: Test action file → processing → completion
- End-to-end: Full pipeline validation

✅ **Observability**: Comprehensive logging:
- Watcher logs: Check cycles, detections, errors with timestamps
- Error logs: Stack traces, error types, timestamps
- Dashboard.md: Activity history with outcomes
- Action files: Audit trail from detection to completion

✅ **Human-in-the-Loop**: File-based workflow allows manual intervention:
- Visual monitoring via Obsidian GUI
- Manual file movement between folders
- Manual watcher start/stop/restart
- Human-readable action file format

### Gates

✅ **PASS**: No architectural debt in Bronze tier - implements only essential components with clear upgrade path to Silver/Gold

✅ **PASS**: Technology choices justified:
- Python: Standard automation language, rich library ecosystem
- Obsidian: Mature markdown editor, local-first, visual GUI
- Claude Code: Proven reasoning engine with Agent Skills architecture
- File system: Simple, reliable state management for MVP

✅ **PASS**: Security considerations appropriate for Bronze tier:
- OAuth 2.0 for Gmail (if chosen)
- Token refresh handling
- Credentials in .env (documented as non-production)
- Local-only data storage

**Re-evaluation Required After Phase 1**: Verify data model and contracts maintain simplicity and testability principles.

## Project Structure

### Documentation (this feature)

```text
specs/000-bronze-tier-foundation/
├── spec.md                    # Feature requirements (complete)
├── plan.md                    # This file (/sp.plan output)
├── research.md                # Phase 0: Technology research and decisions
├── data-model.md              # Phase 1: Action file format, vault structure
├── quickstart.md              # Phase 1: Setup and testing guide
├── contracts/                 # Phase 1: Action file schemas
│   ├── action-file-schema.yaml
│   ├── dashboard-format.yaml
│   └── watcher-config-schema.yaml
├── checklists/
│   └── requirements.md        # Spec validation (complete)
└── tasks.md                   # Phase 2: /sp.tasks output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Bronze Tier implements single project structure with watchers + skills

watchers/
├── base_watcher.py            # Abstract base class for watcher pattern
├── gmail_watcher.py           # Gmail API polling (option 1)
├── filesystem_watcher.py      # File system monitoring (option 2)
├── watcher_config.yaml        # Configuration (check intervals, paths)
└── requirements.txt           # Python dependencies

.claude/
└── commands/                  # Agent Skills (SKILL.md files)
    ├── vault-setup.md         # Initialize Obsidian vault structure
    ├── task-processor.md      # Process action files from /Needs_Action
    └── dashboard-updater.md   # Refresh Dashboard.md with status

# Obsidian vault structure (created by vault-setup skill)
[Vault Root - user specified location]/
├── Dashboard.md               # Activity log, current status, task summary
├── Company_Handbook.md        # Business rules, decision guidelines
├── Inbox/                     # Drop zone for file system watcher
├── Needs_Action/              # Queue of action files awaiting processing
├── Done/                      # Archive of completed action files
├── Errors/                    # Malformed action files moved here
└── Logs/                      # Watcher logs, error logs, processing history

tests/
├── test_action_file_format.py    # Validate action file metadata parsing
├── test_watcher_gmail.py          # Gmail watcher unit tests (if chosen)
├── test_watcher_filesystem.py    # File system watcher unit tests (if chosen)
└── integration/
    └── test_end_to_end.py         # Full pipeline validation

docs/
├── SETUP.md                   # Installation and configuration guide
├── ARCHITECTURE.md            # Perception → Memory → Reasoning → Action
└── TROUBLESHOOTING.md         # Common issues and solutions
```

**Structure Decision**: Single project with watchers/ directory for perception layer, .claude/commands/ for reasoning layer (Agent Skills), and Obsidian vault (user-specified location) for memory layer. No backend/frontend split needed - this is automation scripts + knowledge base, not web application. Tests organized by component with integration/ subdirectory for end-to-end validation.

**Vault Location**: User specifies absolute path to Obsidian vault directory. Watcher scripts and Claude Code configured with this path. Allows flexibility for user's preferred vault location (could be in Dropbox, OneDrive, or local-only).

## Complexity Tracking

No violations - Bronze tier intentionally minimal to validate architecture before adding complexity.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Gmail API vs File System Watcher Trade-offs**
   - **Decision**: Recommend File System Watcher for Bronze tier beginners, Gmail for users comfortable with OAuth
   - **Rationale**: File system has zero setup friction (drop file → detect), Gmail requires OAuth setup but provides richer use cases
   - **Alternatives**: File system (simpler), Gmail (more powerful)
   - **Recommendation**: Start with File System Watcher, optionally upgrade to Gmail in Silver tier

2. **Action File Format: YAML Frontmatter vs Pure JSON**
   - **Decision**: Markdown with YAML frontmatter
   - **Rationale**: Human-readable in Obsidian GUI, git-friendly diffs, supports rich content (body can contain full email text or file contents)
   - **Alternatives**: Pure JSON (less readable), Pure YAML (no body content), XML (verbose)
   - **Schema**: YAML frontmatter for metadata (type, source, timestamp, status), Markdown body for payload

3. **Dashboard.md Update Strategy: Append vs Replace**
   - **Decision**: Append-only with manual archiving
   - **Rationale**: Simpler (no file parsing), preserves full history, faster writes
   - **Alternatives**: Replace with rotation (complex), Database (overkill for Bronze)
   - **Implementation**: New entries prepended to activity log section, user manually archives when >1000 entries

4. **Watcher Error Recovery: Retry vs Crash**
   - **Decision**: Log and continue for most errors, crash on critical failures (config missing, permissions denied)
   - **Rationale**: Resilience to transient network errors, but fail fast on unrecoverable issues
   - **Alternatives**: Always retry (infinite loops), Always crash (too fragile)
   - **Implementation**: Try-except around each check cycle, log to file, exponential backoff for API rate limits

5. **Claude Code Invocation: Manual vs Automated**
   - **Decision**: Manual invocation for Bronze tier
   - **Rationale**: Simpler (no orchestrator needed), allows debugging, user maintains control
   - **Alternatives**: Automated polling (Gold tier feature), Event-driven hooks (complex)
   - **Implementation**: User runs Claude Code, invokes /task-processor skill, points to vault path

6. **Python Dependency Management: venv vs Poetry vs pip**
   - **Decision**: Standard venv + requirements.txt
   - **Rationale**: Universal compatibility, minimal learning curve, sufficient for Bronze tier
   - **Alternatives**: Poetry (overkill), Conda (heavyweight), pip global (conflicts risk)
   - **Implementation**: Document venv setup in quickstart.md

7. **Obsidian Vault Structure: Flat vs Nested**
   - **Decision**: Flat structure with /Inbox, /Needs_Action, /Done, /Errors, /Logs at root
   - **Rationale**: Simple navigation, easy file movement, aligns with Bronze tier simplicity principle
   - **Alternatives**: Nested by date (premature), Tagged (requires plugin), Linked (complex)
   - **Implementation**: vault-setup skill creates folders, Dashboard.md, Company_Handbook.md at root

8. **Watcher Check Intervals: Aggressive vs Conservative**
   - **Decision**: Conservative - File System: 30 sec, Gmail: 2-5 min
   - **Rationale**: Bronze tier is testing/learning, not production. Avoid API quota issues, battery drain, CPU load.
   - **Alternatives**: Aggressive (1 sec / 30 sec) - wastes resources, Adaptive (complex)
   - **Implementation**: Configurable in watcher_config.yaml with recommended defaults

### Technology Stack Summary

| Component | Technology | Justification |
|-----------|------------|---------------|
| Watcher Scripts | Python 3.13+ | Rich ecosystem (gmail API, watchdog), cross-platform, easy to learn |
| Memory/GUI | Obsidian | Local-first, markdown-native, visual GUI, mature ecosystem |
| Reasoning Engine | Claude Code | Agent Skills architecture, proven for automation, good token efficiency |
| Action File Format | Markdown + YAML frontmatter | Human-readable, git-friendly, Obsidian-native, rich content support |
| Logging | Python logging module | Built-in, file rotation support, configurable levels |
| Configuration | YAML | Human-readable, comments support, standard for Python projects |
| Gmail API (optional) | google-api-python-client | Official Google library, OAuth 2.0 support, well-documented |
| File Watching (optional) | watchdog | Cross-platform, event-driven, low CPU overhead |

### Key Architectural Decisions

1. **File-Based State Management**: No database - all state in file system (action files, logs, Dashboard.md). Simpler, more transparent, easier to debug. Validates Bronze tier assumption that file-based approach scales to 50 files/day.

2. **Pull-Based Processing**: Watcher creates action files, Claude Code processes on-demand (user invokes skill). Push-based (orchestrator) deferred to Gold tier. Keeps Bronze tier simple and debuggable.

3. **Agent Skills Architecture**: All Claude Code functionality as SKILL.md files per hackathon rules. Provides structure, documentation, reusability. Three skills: vault-setup, task-processor, dashboard-updater.

4. **Local-First Philosophy**: Obsidian vault on local disk, watchers run locally, Claude Code accesses local files. Only external dependencies: Gmail API (optional), Claude API (required). User maintains data sovereignty.

5. **Manual Scaling**: No auto-rotation for logs, no auto-archiving for Dashboard, no auto-restart for watchers. User manually manages system health. Appropriate for Bronze tier learning/testing phase.

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions, relationships, and validation rules.

**Key Entities**:
1. **Action File**: Markdown file with YAML frontmatter representing detected event
2. **Dashboard Entry**: Single line in activity log showing task completion
3. **Watcher Process**: Python script monitoring for events (Gmail or File System)
4. **Skill Definition**: SKILL.md file defining Claude Code capability
5. **Company Handbook**: Central rules document for AI decision-making

### API Contracts

See [contracts/](./contracts/) directory for complete schemas.

**Core Contracts**:
1. **action-file-schema.yaml**: YAML frontmatter structure for action files
2. **dashboard-format.yaml**: Dashboard.md structure and update protocol
3. **watcher-config-schema.yaml**: Configuration format for watchers

**Note**: Bronze tier has no REST/GraphQL APIs - all "contracts" are file format specifications since architecture is file-based, not API-based.

### Quickstart Guide

See [quickstart.md](./quickstart.md) for detailed setup instructions, testing steps, and troubleshooting tips.

**Setup Summary**:
1. Install prerequisites (Obsidian, Python 3.13+, Claude Code)
2. Clone repository, create venv, install dependencies
3. Choose watcher (Gmail or File System), configure credentials if Gmail
4. Run vault-setup skill to initialize Obsidian vault structure
5. Start watcher script in background
6. Test: Trigger event → verify action file created
7. Invoke task-processor skill → verify file moved to /Done
8. Check Dashboard.md for activity entry

## Phase 2: Task Breakdown

**IMPORTANT**: Phase 2 (task breakdown) is handled by the `/sp.tasks` command, NOT `/sp.plan`. This plan provides the architectural foundation and design artifacts. Once approved, run `/sp.tasks` to generate the detailed task list with test cases and implementation steps.

**Expected Task Categories** (for `/sp.tasks` to expand):
1. Vault structure setup and templates
2. Watcher script implementation (base class + chosen implementation)
3. Action file format and parsing
4. Claude Code Agent Skills (vault-setup, task-processor, dashboard-updater)
5. Logging and error handling
6. Configuration management
7. Integration testing
8. Documentation (SETUP.md, ARCHITECTURE.md, TROUBLESHOOTING.md)

## Implementation Sequence

**Recommended Order** (from spec.md Implementation Notes):

### Phase 1 - Vault Setup (2 hours)
- Create vault-setup Agent Skill
- Generate Dashboard.md and Company_Handbook.md templates
- Create folder structure (/Inbox, /Needs_Action, /Done, /Errors, /Logs)
- Test: Claude Code can read/write vault files

### Phase 2 - Watcher Script (3-4 hours)
- Choose Gmail OR File System watcher
- Implement base_watcher.py abstract class
- Implement chosen watcher (gmail_watcher.py or filesystem_watcher.py)
- Implement action file creation with metadata
- Add logging and error handling
- Test: Watcher runs 1 hour continuously without crashes, creates action files on events

### Phase 3 - Claude Integration (2-3 hours)
- Create task-processor Agent Skill
- Implement action file parsing and validation
- Implement Dashboard.md update logic (prepend to activity log)
- Implement file movement from /Needs_Action to /Done
- Test: Process 10 test action files, verify all moved to /Done with metadata

### Phase 4 - Additional Skills (2 hours)
- Create dashboard-updater Agent Skill (refresh status summary)
- Document each skill with usage examples and expected inputs/outputs
- Test: Invoke each skill, verify expected behavior

### Phase 5 - Testing & Documentation (1-2 hours)
- End-to-end integration test: Event → Action File → Processing → Done
- Verify all Bronze tier success criteria from spec.md
- Write SETUP.md, ARCHITECTURE.md, TROUBLESHOOTING.md
- Record demo video showing key workflow

**Total Estimated Time**: 8-12 hours (aligns with Bronze tier estimate)

## Architecture Validation

Bronze Tier must prove these principles (from spec.md):

1. ✅ **Perception → Memory → Reasoning → Action** pipeline works end-to-end
   - **Validation**: Watcher detects event → creates action file → Claude processes → updates Dashboard

2. ✅ **File-based state management** is viable for AI automation
   - **Validation**: 50 action files processed without performance degradation, Dashboard maintains complete history

3. ✅ **Claude Code can reliably parse and update** Obsidian markdown
   - **Validation**: 90% of action files processed successfully, Dashboard updates within 5 seconds

4. ✅ **Watcher pattern enables autonomous triggering** (not just reactive chat)
   - **Validation**: Events detected without user typing prompts, action files created automatically

5. ✅ **Agent Skills provide reusable structure** for AI capabilities
   - **Validation**: Three skills (vault-setup, task-processor, dashboard-updater) work consistently across multiple invocations

**Failure Criteria**: If any principle fails validation during Bronze tier implementation, Silver/Gold tiers will compound the problems. Bronze is the foundation that validates the entire approach. If file-based state management proves inadequate, consider database for Silver tier. If Claude Code cannot reliably parse markdown, consider structured JSON format.

## Risk Mitigation Strategies

From spec.md Risks section, prioritized for Phase 1 implementation:

### High Severity (must address in Phase 1)

1. **OAuth token expiration breaking Gmail Watcher**
   - **Mitigation**: Implement automatic token refresh in gmail_watcher.py, store refresh token in .env, graceful error handling with retry

2. **Obsidian vault corruption from concurrent writes**
   - **Mitigation**: Document single Claude Code instance limitation, implement file locking for Dashboard.md updates, atomic write operations

3. **Gmail API quota exceeded**
   - **Mitigation**: Conservative check interval (2-5 min), exponential backoff on 429 responses, quota monitoring in logs

### Medium Severity (monitor during testing)

4. **Watcher script crashes without visibility**
   - **Mitigation**: Comprehensive error logging, include health check section in watcher logs (last successful check timestamp)

5. **Claude Code token budget exhaustion**
   - **Mitigation**: Document estimated token costs per action file, recommend batching for large volumes, monitor usage

### Low Severity (acceptable for Bronze tier)

6. **Dashboard.md grows unbounded**
   - **Mitigation**: Document manual archiving process in TROUBLESHOOTING.md, warn at 1000 entries

## Success Criteria Mapping

Bronze tier implementation must satisfy success criteria from spec.md. Key metrics with implementation strategy:

| Success Criteria | Implementation Strategy | Validation Method |
|------------------|------------------------|-------------------|
| SC-001: Vault init <2 min | vault-setup skill uses templates, no heavy computation | Time script execution |
| SC-002: Watcher runs 24 hours | Robust error handling, logging, retry logic | Run overnight, check logs |
| SC-003: 95% detection accuracy | Test with 20 events, verify 19+ action files created | Integration test |
| SC-004: 90% processing success | Test with 20 action files, verify 18+ moved to /Done | Integration test |
| SC-005: Dashboard updates <5 sec | Append-only writes, no parsing required | Time Dashboard update operations |
| SC-006: Verify watcher status | Watcher logs show last check timestamp | Manual log inspection |
| SC-007: Manual file processed <2 min | File system watcher detects in 30 sec + Claude processes <90 sec | End-to-end test |
| SC-016: 100% functionality as Agent Skills | vault-setup, task-processor, dashboard-updater implemented as SKILL.md | Code review |
| SC-017: Standardized action file format | action-file-schema.yaml defines structure, validation in task-processor | Schema validation test |

## Upgrade Path to Silver Tier

Bronze tier intentionally excludes features deferred to Silver/Gold. Clear upgrade path:

**Silver Tier Additions** (on top of Bronze foundation):
- Add second watcher (both Gmail AND File System)
- Implement first MCP server (e.g., Gmail send for replies)
- Add human-in-the-loop approval workflow (/Pending_Approval folder)
- Implement Plan.md generation with reasoning loop
- Add cron/Task Scheduler for automated watcher startup
- Extend Agent Skills: approval-processor, plan-generator

**Gold Tier Additions** (on top of Silver):
- Add 4 more watchers (WhatsApp, Xero, Calendar, Slack) = 6 total
- Implement orchestrator + watchdog for health monitoring
- Add Ralph Wiggum autonomous loop (stop hook pattern)
- Implement comprehensive audit logging (180-day retention)
- Add CEO Briefing generation skill
- Integrate Xero/Odoo accounting via MCP

**Architecture Continuity**: Bronze validates the core file-based Perception → Memory → Reasoning → Action pipeline. Silver adds more watchers + MCP servers + approval workflow. Gold adds orchestration + audit + business intelligence. Each tier builds incrementally on proven foundation.

---

## Next Steps

1. **Review this plan** with user/stakeholders
2. **Generate Phase 0 artifacts**: research.md (technology decisions documented above)
3. **Generate Phase 1 artifacts**: data-model.md, contracts/, quickstart.md
4. **Run `/sp.tasks`** to generate detailed task breakdown with test cases
5. **Implement tasks** following recommended 5-phase sequence
6. **Validate Bronze tier** against success criteria before proceeding to Silver

**Approval Required**: This plan must be approved before proceeding to `/sp.tasks` command.
