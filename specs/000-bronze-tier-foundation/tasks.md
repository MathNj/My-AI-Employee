# Tasks: Bronze Tier Foundation - Personal AI Employee

**Input**: Design documents from `/specs/000-bronze-tier-foundation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are optional for Bronze tier - manual integration testing focus per quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Watcher scripts**: `watchers/` at repository root
- **Agent Skills**: `.claude/commands/` at repository root
- **Obsidian Vault**: User-specified location (typically `vault/` or absolute path)
- **Tests**: `tests/` at repository root
- **Documentation**: `docs/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create watchers/ directory structure at repository root
- [ ] T002 Create .claude/commands/ directory for Agent Skills
- [ ] T003 Create tests/ directory with tests/integration/ subdirectory
- [ ] T004 Create docs/ directory for setup and architecture documentation
- [ ] T005 Create vault/ directory as default Obsidian vault location (user can override with absolute path)
- [ ] T006 Create watchers/requirements.txt with pyyaml==6.0.1, python-frontmatter==1.1.0, watchdog==4.0.0
- [ ] T007 [P] Create watchers/requirements.txt with Gmail dependencies (google-auth==2.27.0, google-auth-oauthlib==1.2.0, google-auth-httplib2==0.2.0, google-api-python-client==2.116.0) - for Gmail watcher option
- [ ] T008 [P] Create watchers/.env.example template for Gmail credentials (GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_USER_EMAIL)
- [ ] T009 Create Python virtual environment setup guide in docs/SETUP.md
- [ ] T010 Create watchers/watcher_config.yaml template with both Gmail and filesystem_watcher sections (disabled by default)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Logging Infrastructure

- [ ] T011 Create watchers/watcher_logger.py with configure_logging() function using Python logging module with file rotation support
- [ ] T012 Implement log format: "%(asctime)s | %(levelname)s | %(message)s" with date format "%Y-%m-%d %H:%M:%S"
- [ ] T013 Add log level support (DEBUG, INFO, WARNING, ERROR, CRITICAL) configurable via watcher_config.yaml

### Action File Format

- [ ] T014 Create watchers/action_file.py with create_action_file() function that generates markdown files with YAML frontmatter
- [ ] T015 Implement action file naming convention: {SOURCE}_{YYYYMMDD}_{HHMMSS}_{identifier}.md
- [ ] T016 Add frontmatter schema with required fields: type, source, timestamp, status, payload, processing_metadata
- [ ] T017 Implement payload schemas for each type: email (sender, subject, message_id, snippet), file (filename, path, size_bytes), scheduled (task_description, priority)

### Configuration Management

- [ ] T018 Create watchers/config.py with load_config() function that parses watcher_config.yaml
- [ ] T019 Implement validation for vault_path (must exist and be absolute)
- [ ] T020 Add validation for check_interval_sec (minimum values: 60 for Gmail, 10 for filesystem)
- [ ] T021 Implement exactly-one-watcher-enabled validation (Gmail OR File System, not both)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Obsidian Vault Initialization (Priority: P1) 🎯 MVP

**Goal**: Initialize Obsidian vault with Dashboard.md, Company_Handbook.md, and folder structure (/Inbox, /Needs_Action, /Done, /Errors, /Logs)

**Independent Test**: Open Obsidian, verify all folders exist, verify Dashboard.md has YAML frontmatter and sections (Current Status, Activity Log, Task Summary), verify Company_Handbook.md has business rules sections

### Implementation for User Story 1

- [ ] T022 [P] [US1] Create vault folder structure in vault-setup skill: vault/Inbox/, vault/Needs_Action/, vault/Done/, vault/Errors/, vault/Logs/
- [ ] T023 [P] [US1] Create Dashboard.md template in vault-setup skill with YAML frontmatter (last_updated, vault_version: bronze_tier_v1)
- [ ] T024 [P] [US1] Create Dashboard.md sections: # AI Employee Dashboard, ## Current Status, ## Activity Log, ## Task Summary (Last 24 Hours)
- [ ] T025 [P] [US1] Create Company_Handbook.md template with sections: ## Business Overview, ## Decision-Making Guidelines, ## Key Contacts, ## Business Rules, ## Subscription Inventory, ## Project Context
- [ ] T026 [US1] Implement .claude/commands/vault-setup.md Agent Skill with vault_path input parameter
- [ ] T027 [US1] Add vault-setup skill usage example: /vault-setup --vault_path "/path/to/vault"
- [ ] T028 [US1] Add vault-setup skill error handling: create directories if missing, prompt user if files exist, exit with clear error if permissions denied
- [ ] T029 [US1] Test vault-setup skill: invoke skill, verify all folders created, verify Dashboard.md and Company_Handbook.md have correct structure

**Checkpoint**: At this point, User Story 1 should be fully functional - Obsidian vault ready for AI Employee operations

---

## Phase 4: User Story 2 - Single Watcher Implementation (Priority: P1)

**Goal**: Implement ONE watcher script (Gmail OR File System) that detects events and creates action files in /Needs_Action with standardized metadata

**Independent Test**: Run watcher script, trigger event (send email or drop file in /Inbox), verify action file created in /Needs_Action with correct YAML frontmatter (type, source, timestamp, status: pending, payload)

### Implementation for User Story 2

#### Base Watcher Class (Shared Infrastructure)

- [ ] T030 [US2] Create watchers/base_watcher.py with abstract BaseWatcher class
- [ ] T031 [US2] Implement BaseWatcher.check_interval loop with configurable sleep between checks
- [ ] T032 [US2] Add BaseWatcher.log_check_cycle() method to log each check cycle with timestamp
- [ ] T033 [US2] Implement BaseWatcher.handle_error() with retry logic for transient errors, crash for critical errors
- [ ] T034 [US2] Add BaseWatcher.create_action_file() method using action_file.py create_action_file() function

#### File System Watcher (Option A - Recommended for Bronze)

- [ ] T035 [P] [US2] Create watchers/filesystem_watcher.py extending BaseWatcher
- [ ] T036 [P] [US2] Implement FileSystemWatcher.check_for_new_files() using watchdog library for real-time file system monitoring
- [ ] T037 [P] [US2] Add file filtering: check file_filters from watcher_config.yaml (*.pdf, *.docx, *.txt, *.md)
- [ ] T038 [P] [US2] Implement ignore_patterns logic (.*, *.tmp, *.swp)
- [ ] T039 [P] [US2] Add file size validation: ignore files < min_file_size_bytes (default 100)
- [ ] T040 [P] [US2] Implement settle_time_sec logic: wait 2 seconds after file modification before processing (avoid incomplete copies)
- [ ] T041 [US2] Add FileSystemWatcher.extract_file_metadata() to get filename, path, size_bytes, mime_type, created_at
- [ ] T042 [US2] Implement FileSystemWatcher.run() main loop with check_interval_sec (default 30 seconds)
- [ ] T043 [US2] Add main entry point: if __name__ == "__main__": FileSystemWatcher(config).run()

#### Gmail Watcher (Option B - Advanced)

- [ ] T044 [P] [US2] Create watchers/gmail_watcher.py extending BaseWatcher
- [ ] T045 [P] [US2] Implement GmailWatcher.authenticate() using OAuth 2.0 with google-auth-oauthlib
- [ ] T046 [P] [US2] Add token.json storage and automatic token refresh on expiration
- [ ] T047 [P] [US2] Implement GmailWatcher.check_for_new_emails() using gmail.users().messages().list() API call
- [ ] T048 [P] [US2] Add labels filtering from watcher_config.yaml (default: INBOX)
- [ ] T049 [P] [US2] Implement max_results limit (default 10 emails per check)
- [ ] T050 [P] [US2] Add GmailWatcher.extract_email_metadata() to get sender, subject, message_id, snippet, labels, has_attachments
- [ ] T051 [P] [US2] Implement GmailWatcher.run() main loop with check_interval_sec (default 120 seconds - 2 minutes)
- [ ] T052 [P] [US2] Add exponential backoff on API rate limit (429 response): wait 2, 4, 8 seconds before retry
- [ ] T053 [P] [US2] Add main entry point: if __name__ == "__main__": GmailWatcher(config).run()

**Checkpoint**: At this point, User Story 2 should be fully functional - watcher detecting events and creating action files

---

## Phase 5: User Story 3 - Claude Code Vault Integration (Priority: P1)

**Goal**: Enable Claude Code to read from and write to Obsidian vault, parse action files, update Dashboard.md, move files to /Done

**Independent Test**: Run Claude Code in vault directory, test read (cat Dashboard.md), test write (append to activity log), test action file processing (parse file, update metadata, move to /Done)

### Implementation for User Story 3

#### Action File Parsing

- [ ] T054 [US3] Implement task-processor skill to read action files from /Needs_Action using python-frontmatter
- [ ] T055 [US3] Add validate_action_file() function in task-processor skill: check required fields (type, source, timestamp, status, payload)
- [ ] T056 [US3] Implement chronological sorting: sort action files by timestamp (oldest first)
- [ ] T057 [US3] Add batch size limit: process max_files (default 50) per invocation

#### Dashboard Updates

- [ ] T058 [US3] Implement update_dashboard_activity_log() function to append entry after "## Activity Log" marker
- [ ] T059 [US3] Add entry format: "- {timestamp} | {task_type} | {summary} | {status_icon} {outcome}"
- [ ] T060 [US3] Implement update_dashboard_status() function to refresh Current Status section (watcher status, pending count, completed today, error rate)
- [ ] T061 [US3] Add calculate_error_rate() function: count ❌ vs ✅ in activity log for last 24 hours

#### File Movement

- [ ] T062 [US3] Implement move_to_done() function to append processing_metadata (started_at, completed_at, processing_time_sec, claude_model, outcome)
- [ ] T063 [US3] Add move_to_errors() function for malformed files with validation error details
- [ ] T064 [US3] Implement atomic file moves using Path.rename() with FileNotFoundError handling

#### Task Processor Skill

- [ ] T065 [US3] Create .claude/commands/task-processor.md Agent Skill with vault_path and max_files input parameters
- [ ] T066 [US3] Add task-processor skill usage example: /task-processor --vault_path "/path/to/vault" --max_files 10
- [ ] T067 [US3] Implement error handling: vault locked (wait/retry 3 times), file not found (log and skip), permission denied (exit with error)
- [ ] T068 [US3] Add processing loop: for each action file in /Needs_Action (sorted chronologically), parse, validate, process task, update metadata, move to /Done

**Checkpoint**: At this point, User Story 3 should be fully functional - Claude Code reading/writing vault, processing action files

---

## Phase 6: User Story 4 - Basic Folder Workflow (Priority: P2)

**Goal**: Enable file-based workflow using /Inbox, /Needs_Action, /Done folders for visual tracking and manual intervention

**Independent Test**: Drop file in /Inbox, verify watcher creates action file in /Needs_Action, verify Claude Code moves to /Done with processing metadata, verify /Errors folder catches malformed files

### Implementation for User Story 4

- [ ] T069 [US4] Document folder workflow in quickstart.md: /Inbox (drop zone) → Watcher → /Needs_Action (queue) → task-processor → /Done (archive)
- [ ] T070 [US4] Add /Errors folder handling in task-processor skill: move malformed files with error details
- [ ] T071 [US4] Implement file name preservation when moving: keep original filename, add processing metadata as frontmatter
- [ ] T072 [US4] Add visual status indicators in Dashboard: status_icon (✅ Complete, ❌ Error, ⏸️ Pending Approval)
- [ ] T073 [US4] Document manual intervention options: user can manually move files between folders, edit action files, add priority flags
- [ ] T074 [US4] Add troubleshooting section to TROUBLESHOOTING.md for common workflow issues (files not moving, validation errors, permission issues)

**Checkpoint**: At this point, User Story 4 should be fully functional - complete file-based workflow with manual oversight

---

## Phase 7: User Story 5 - Agent Skills Implementation (Priority: P1)

**Goal**: Implement all AI functionality as Agent Skills (SKILL.md files) with reusable, documented capabilities

**Independent Test**: Invoke vault-setup skill, verify vault created; invoke task-processor skill, verify files processed; invoke dashboard-updater skill, verify status refreshed

### Implementation for User Story 5

#### Vault Setup Skill (Already created in US1 - enhance if needed)

- [ ] T075 [US5] Enhance .claude/commands/vault-setup.md skill if needed: add comprehensive error handling, user prompts for overwrite confirmation
- [ ] T076 [US5] Add vault-setup skill documentation: skill name, description, input parameters (vault_path), output (folder structure, template files), usage examples

#### Task Processor Skill (Already created in US3 - enhance if needed)

- [ ] T077 [US5] Enhance .claude/commands/task-processor.md skill if needed: add batch processing details, error handling flow
- [ ] T078 [US5] Add task-processor skill documentation: input parameters (vault_path, max_files), output (Dashboard update, file movement), usage examples, edge cases

#### Dashboard Updater Skill (New)

- [ ] T079 [P] [US5] Create .claude/commands/dashboard-updater.md Agent Skill with vault_path input parameter
- [ ] T080 [P] [US5] Implement refresh_current_status() function: check watcher log for last check timestamp, count /Needs_Action files, count today's completed tasks
- [ ] T081 [P] [US5] Add calculate_task_summary() function: group activity log entries by task_type (EMAIL, FILE, MANUAL), calculate success rate
- [ ] T082 [P] [US5] Implement update_task_summary_table() function: regenerate markdown table with Type | Count | Success Rate
- [ ] T083 [P] [US5] Add dashboard-updater skill usage example: /dashboard-updater --vault_path "/path/to/vault"
- [ ] T084 [P] [US5] Add error handling: watcher log missing (report "Unknown" status), Dashboard.md missing (recreate from template), parse error (manual inspection needed)

**Checkpoint**: At this point, User Story 5 should be fully functional - all AI functionality as documented Agent Skills

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T085 [P] Create comprehensive docs/SETUP.md with 6-phase setup guide (environment, vault, watcher, dependencies, testing, Claude integration)
- [ ] T086 [P] Create docs/TROUBLESHOOTING.md with common issues and solutions (watcher not detecting, invalid action file format, OAuth expired, Claude cannot write, log growth)
- [ ] T087 [P] Create docs/ARCHITECTURE.md with Perception → Memory → Reasoning → Action pipeline diagram and component descriptions
- [ ] T088 Update README.md with Bronze Tier status, feature summary, setup instructions, demo video link
- [ ] T089 Add end-to-end integration test in tests/integration/test_end_to_end.py: event → action file → processing → done
- [ ] T090 Implement graceful shutdown handling: watch for SIGINT/SIGTERM, flush logs, exit cleanly
- [ ] T091 Add file locking for Dashboard.md updates to prevent corruption from concurrent writes (document single Claude instance limitation)
- [ ] T092 Add log rotation guidance to TROUBLESHOOTING.md: manual archiving when logs exceed 10MB
- [ ] T093 Validate all Bronze tier success criteria from spec.md: vault init <2 min, watcher runs 24 hours, 95% detection accuracy, 90% processing success, Dashboard updates <5 sec
- [ ] T094 Record 5-10 minute demo video showing: watcher startup, event detection, action file creation, Claude processing, Dashboard update, file movement to /Done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T010) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion (T011-T021) - No dependencies on other user stories
- **User Story 2 (Phase 4)**: Depends on Foundational completion (T011-T021) - Independent of US1, US3, US4, US5
- **User Story 3 (Phase 5)**: Depends on Foundational completion (T011-T021) AND US1 for vault structure - Independent of US2, US4
- **User Story 4 (Phase 6)**: Depends on US2 (watcher) AND US3 (task-processor) - Integrates both stories
- **User Story 5 (Phase 7)**: Depends on US1 (vault-setup created), US3 (task-processor created) - Independent of US2, US4
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MVP SCOPE**
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1, US3, US4, US5
- **User Story 3 (P1)**: Depends on US1 (vault structure) but independent of US2, US4, US5
- **User Story 4 (P2)**: Depends on US2 (watcher) AND US3 (task-processor) - Integration story
- **User Story 5 (P1)**: Depends on US1 (vault-setup) AND US3 (task-processor) but independent of US2, US4

### Critical Path for MVP (US1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T021) - **BLOCKS ALL STORIES**
3. Complete Phase 3: User Story 1 (T022-T029)
4. **STOP and VALIDATE**: Test US1 independently (vault structure ready)
5. Optionally continue to US2, US3, US4, US5 for complete Bronze Tier

### Within Each User Story

- Models/entities before services
- Services before skills/endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: T007 (Gmail requirements) and T008 (.env.example) can run in parallel with T006 (base requirements)
- **Foundational Phase**: T011-T021 (logging, action file format, config) can run in parallel once Setup complete
- **User Story 2**: T035-T043 (File System Watcher) can run in parallel with T044-T053 (Gmail Watcher) - but only implement ONE for Bronze Tier
- **User Story 5**: T079-T084 (dashboard-updater skill) can run in parallel once US3 complete
- **Polish Phase**: T085-T088 (documentation) can all run in parallel

---

## Parallel Example: User Story 2 (Choosing File System Watcher)

```bash
# Launch all File System Watcher components together:
Task: "T035 Create watchers/filesystem_watcher.py extending BaseWatcher"
Task: "T036 Implement FileSystemWatcher.check_for_new_files() using watchdog"
Task: "T037 Add file filtering: check file_filters from watcher_config.yaml"
Task: "T038 Implement ignore_patterns logic (.*, *.tmp, *.swp)"
Task: "T039 Add file size validation: ignore files < min_file_size_bytes"
Task: "T040 Implement settle_time_sec logic: wait 2 seconds after modification"
Task: "T041 Add FileSystemWatcher.extract_file_metadata() to get file details"
```

**Note**: If implementing Gmail Watcher instead, parallelize T044-T053 similarly

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Minimum Bronze Tier

1. Complete Phase 1: Setup (T001-T010) - 30 minutes
2. Complete Phase 2: Foundational (T011-T021) - 1.5 hours
3. Complete Phase 3: User Story 1 (T022-T029) - 2 hours
4. **STOP and VALIDATE**: Test US1 independently - vault structure ready
5. Deploy/demo if ready - **MVP DELIVERABLE**

**Time Estimate**: 4 hours for MVP (vault setup only, no watcher, no processing)

### Standard Bronze Tier (User Stories 1, 2, 3, 5) - Recommended

1. Complete Setup + Foundational → Foundation ready (2 hours)
2. Add User Story 1 → Test independently → Vault structure complete (2 hours)
3. Add User Story 2 → Test independently → Watcher detecting events (3-4 hours)
4. Add User Story 3 → Test independently → Claude processing tasks (2-3 hours)
5. Add User Story 5 → Test independently → Agent Skills complete (2 hours)
6. Complete Polish → End-to-end system ready (1-2 hours)

**Time Estimate**: 10-13 hours for complete Bronze Tier (matches spec.md estimate of 8-12 hours)

### Full Bronze Tier (All User Stories 1-5)

1. Complete Standard Bronze Tier above (US1, US2, US3, US5)
2. Add User Story 4 → Test workflow → File-based workflow with manual oversight (1 hour)
3. Complete Polish → Full system validation (1-2 hours)

**Time Estimate**: 12-16 hours for full Bronze Tier with all features

### Incremental Delivery Options

- **MVP (US1 only)**: Vault structure ready - can demo Obsidian setup
- **Basic (US1 + US2)**: Vault + Watcher - can demo event detection and action file creation
- **Functional (US1 + US2 + US3)**: Vault + Watcher + Processing - can demo complete pipeline (event → action file → processing → done)
- **Complete (US1 + US2 + US3 + US5)**: All core features - can demo fully functional Bronze Tier
- **Full (US1-5)**: All Bronze Tier features - can demo with manual workflow oversight

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (e.g., after each user story phase)
- Stop at any checkpoint to validate story independently
- **Bronze Tier Rule**: Implement ONE watcher (US2), not both File System and Gmail watchers
- Tests are manual/integration focus per quickstart.md - no automated unit tests required for Bronze tier
- Validate success criteria from spec.md after each user story completion
- For faster MVP delivery: Complete US1 only, then demo vault structure
- For hackathon submission: Complete US1, US2, US3, US5 (US4 is nice-to-have P2)

---

## Task Summary

- **Total Tasks**: 94 tasks
- **Setup (Phase 1)**: 10 tasks
- **Foundational (Phase 2)**: 11 tasks
- **User Story 1 (Phase 3)**: 8 tasks
- **User Story 2 (Phase 4)**: 24 tasks (File System: T035-T043 OR Gmail: T044-T053, plus base class T030-T034)
- **User Story 3 (Phase 5)**: 15 tasks
- **User Story 4 (Phase 6)**: 6 tasks
- **User Story 5 (Phase 7)**: 10 tasks
- **Polish (Phase 8)**: 10 tasks

**Parallel Opportunities**: 30+ tasks marked [P] can run in parallel within phases

**MVP Scope (US1 only)**: 29 tasks (Setup + Foundational + US1) - ~4 hours

**Recommended Bronze Tier (US1, US2, US3, US5)**: 78 tasks - ~10-13 hours

**Full Bronze Tier (US1-5)**: 84 tasks - ~12-16 hours
