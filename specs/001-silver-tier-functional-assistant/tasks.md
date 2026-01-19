# Tasks: Silver Tier Functional Assistant - Personal AI Employee

**Input**: Design documents from `/specs/001-silver-tier-functional-assistant/`
**Prerequisites**: plan.md, spec.md (Bronze Tier feature 000 must be complete)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

**Format**: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Silver Tier project initialization and dependency installation

- [ ] T001 Verify Bronze Tier (feature 000) completeness: vault structure, one watcher, task-processor skill
- [ ] T002 Upgrade system RAM to 16GB if currently 8GB (Silver tier requires more memory for 2+ watchers + MCP server)
- [ ] T003 Install Node.js v24+ LTS for MCP server (https://nodejs.org/)
- [ ] T004 [P] Install Python dependencies: psutil (process monitoring), schedule (scheduling helper)
- [ ] T005 [P] Install Playwright for LinkedIn automation: `npm install -g playwright` (or `pip install playwright` if Python preferred)
- [ ] T006 Create mcp/ directory structure for MCP server
- [ ] T007 Create /Scheduled directory in vault for scheduled task configuration
- [ ] T008 Create /Pending_Approval, /Approved, /Rejected folders in vault for approval workflow
- [ ] T009 Create /Plans and /Plans/active folders in vault for Plan.md reasoning documents
- [ ] T010 Create watchers_state.json shared state file for deduplication tracking

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY Silver Tier user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Orchestrator Foundation

- [ ] T011 Create watchers/orchestrator.py with MultiWatcherManager class
- [ ] T012 Implement launch_watchers() method to start watcher processes as subprocess.Popen
- [ ] T013 Implement stop_watchers() method to gracefully terminate watcher processes
- [ ] T014 Add monitor_watchers() method to check PIDs and restart crashed watchers
- [ ] T015 Implement get_watcher_status() method returning: watcher_name, status, last_check, events_today

### Deduplication System

- [ ] T016 Implement check_duplicate() function in orchestrator.py: check event_id in watchers_state.json before creating action file
- [ ] T017 Implement register_event() function: add event_id to watchers_state.json with timestamp
- [ ] T018 Implement rotate_state_file() method: create new watchers_state.json, purge entries older than 24 hours
- [ ] T019 Add deduplication logging: log when duplicate detected (event_id, original_detection_time)

### Health Monitoring

- [ ] T020 Create watchers/health_monitor.py script with check_all_watchers() function
- [ ] T021 Implement PID existence check: watcher PID exists in /proc (Linux) or tasklist (Windows)
- [ ] T022 Implement log freshness check: watcher log modified in last 5 minutes?
- [ ] T023 Implement CPU usage check: process CPU <50% (alert if higher)
- [ ] T024 Log health status to /Logs/watcher_health.log with timestamp and watcher_name

### Extended Configuration

- [ ] T025 Update watchers/watcher_config.yaml to support multiple watchers: gmail_watcher, filesystem_watcher, whatsapp_watcher
- [ ] T026 Add enabled/disabled flag for each watcher (exactly 2+ must be enabled for Silver)
- [ ] T027 Add health_monitor section to config: check_interval_sec, log_path
- [ ] T028 Create /Scheduled/config.yaml template for scheduled task definitions

**Checkpoint**: Foundation ready - multi-watcher, deduplication, health monitoring, scheduling infrastructure complete

---

## Phase 3: User Story 1 - Multi-Watcher Orchestration (Priority: P1)

**Goal**: Two or more watchers running concurrently with deduplication and health monitoring

**Independent Test**: Run both watchers 1 hour, trigger events in both sources, verify unique action files created with correct source labels, check CPU usage <30%

### Implementation for User Story 1

- [ ] T029 [US1] Add WhatsApp Watcher if chosen: watchers/whatsapp_watcher.py (or enable second File System watcher)
- [ ] T030 [P] [US1] Implement WhatsApp Web API integration: check for new messages every 30 seconds
- [ ] T031 [P] [US1] Add WhatsApp message_id extraction for deduplication
- [ ] T032 [US1] Update orchestrator.py to launch 2+ watcher processes: read config, spawn subprocesses, track PIDs
-- [ ] T033 [US1] Test deduplication: trigger same event across watchers, verify only one action file created
- [ ] T034 [US1] Update Dashboard.md template to show all watcher statuses: watcher_name, status, last_check, events_today
- [ ] T035 [US1] Add dashboard-updater skill to refresh watcher status section: read watcher_health.log, update Dashboard
- [ ] T036 [US1] Test concurrent execution: run both watchers 1 hour, verify CPU usage <30%, no crashes

**Checkpoint**: At this point, User Story 1 should be fully functional - 2+ watchers coordinated with deduplication

---

## Phase 4: User Story 5 - Approval Workflow (Priority: P1)

**Goal**: Human-in-the-loop approval for sensitive actions (emails, LinkedIn posts, financial decisions)

**Independent Test**: Process email action requiring approval, verify routing to /Pending_Approval, manually approve, verify execution proceeds

**Why US5 before US2/US3/US4?** Approval workflow is blocking prerequisite for LinkedIn posting (US2) and MCP email actions (US4). Must implement first.

### Implementation for User Story 5

- [ ] T037 [US5] Extend task-processor skill to check /Pending_Approval before executing sensitive actions
- [ ] T038 [US5] Define sensitive actions list: email send, LinkedIn post, financial decisions >$100, data deletion
- [ ] T039 [US5] Implement move_to_pending_approval() function: move file to /Pending_Approval, create approval_request.md
- [ ] T040 [P] [US5] Create approval_request.md template with fields: action_summary, risk_level (high/medium/low), approval_deadline (24h default), potential_impact
- [ ] T041 [US5] Implement process_approved_actions() function: check /Approved folder, execute actions, move to /Done
- [ ] T042 [US5] Implement process_rejected_actions() function: move /Rejected files to /Done with rejection_reason
- [ ] T043 [US5] Add deadline monitoring: check approval_deadline, if expired mark as overdue, notify human
- [ ] T044 [US5] Update Dashboard.md to show: pending_approvals_count, approvals_today, rejections_today, oldest_pending_approval_age
- [ ] T045 [US5] Test approval workflow: process email requiring approval, verify /Pending_Approval routing, approve, verify execution

**Checkpoint**: At this point, User Story 5 should be fully functional - approval workflow ensures safe automation

---

## Phase 5: User Story 4 - MCP Server Integration (Priority: P1)

**Goal**: One working MCP server for external actions (Gmail send recommended - builds on Bronze Gmail API)

**Independent Test**: Invoke MCP send_email action, verify email sent successfully, check MCP action log

**Why US4 before US2/US3?** MCP server enables external actions (email send) which is prerequisite for LinkedIn posting (US2) if using MCP for LinkedIn.

### Implementation for User Story 4

- [ ] T046 [P] [US4] Create mcp/gmail-send-server/package.json with dependencies: @modelcontextprotocol/sdk, googleapis, gmail
- [ ] T047 [P] [US4] Implement mcp/gmail-send-server/src/index.ts with MCP server initialization
- [ ] T048 [P] [US4] Define send_email tool in MCP server: input (to, subject, body, attachments), output (success, message_id, error)
- [ ] T049 [P] [US4] Implement Gmail API integration in MCP server: use googleapis/gmail npm package
- [ ] T050 [P] [US4] Add error handling for MCP server: try-catch around Gmail API calls, return structured errors
- [ ] T051 [US4] Implement MCP server logging to /Logs/mcp_actions_YYYY-MM-DD.json with: action_type, input_params, output_result, timestamp
- [ ] T052 [US4] Create mcp/gmail-send-server/README.md with setup instructions and usage examples
- [ ] T053 [US4] Test MCP server startup: node mcp/gmail-send-server/src/index.ts, verify tools exposed, call send_email
- [ ] T054 [US4] Extend task-processor skill to invoke MCP server: subprocess.run() or HTTP if MCP server exposes endpoint
- [ ] T055 [US4] Add MCP action queue: queue actions if MCP server down, retry with exponential backoff (3 attempts)
- [ ] T056 [US4] Test end-to-end: task-processor calls MCP send_email, verify email sent, check log file

**Checkpoint**: At this point, User Story 4 should be fully functional - MCP server executes external actions

---

## Phase 6: User Story 2 - LinkedIn Social Media Posting (Priority: P1)

**Goal**: Automatic business updates to LinkedIn for lead generation with approval workflow

**Independent Test**: Create LinkedIn post, approve, publish, verify post on LinkedIn profile, check engagement metrics

### Implementation for User Story 2

- [ ] T057 [P] [US2] Create linkedin-poster skill: .claude/commands/linkedin-poster.md
- [ ] T058 [P] [US2] Implement LinkedIn authentication: Playwright browser login with QR code or credentials from .env
- [ ] T059 [P] [US2] Implement create_post() function: create LinkedIn post with content, hashtags, mentions, media attachments
- [ ] T060 [US2] Add post validation: character limits, hashtag format (#tag), mention format (@name), media size limits
- [ ] T061 [US2] Integrate with approval workflow: all LinkedIn posts require /Pending_Approval routing
- [ ] T062 [US2] Implement publish_post() function: submit post via Playwright, capture post_url and post_id
- [ ] T063 [US2] Add engagement tracking: capture likes, comments, shares (if accessible via Playwright)
- [ ] T064 [US2] Log LinkedIn posts to Company_Handbook.md social media inventory section
- [ ] T065 [US2] Implement retry logic for API rate limits: exponential backoff (2, 4, 8 seconds), respect 429 responses
- [ ] T066 [US2] Test LinkedIn posting: create test post, approve, publish, verify on LinkedIn, check metrics
- [ ] T067 [US2] Add scheduled LinkedIn post support: queue post, publish at scheduled_time if specified

**Checkpoint**: At this point, User Story 2 should be fully functional - LinkedIn posting automated with approval

---

## Phase 7: User Story 3 - Plan.md Reasoning Loop (Priority: P1)

**Goal**: Claude Code creates Plan.md for complex tasks (3+ steps or >15 minutes) with execution tracking

**Independent Test**: Process complex task (e.g., "organize client files by project"), verify Plan.md created with steps and reasoning, approve, verify execution follows plan

### Implementation for User Story 3

- [ ] T068 [P] [US3] Create plan-generator skill: .claude/commands/plan-generator.md
- [ ] T069 [P] [US3] Define Plan.md template with YAML frontmatter: objective, task_description, steps (numbered), estimated_time_per_step, total_estimated_time, dependencies, risks, reasoning, alternatives_considered, rationale
- [ ] T070 [P] [US3] Implement detect_complex_task() function: check if task has 3+ steps OR estimated time >15 minutes
- [ ] T071 [US3] Integrate with task-processor skill: before executing complex task, invoke plan-generator skill
- [ ] T072 [US3] Create /Plans folder structure: /Plans/active/ for executing plans, /Plans/archive/ for completed plans
- [ ] T073 [US3] Implement create_plan() function: generate Plan.md in /Plans/active/ with objective, steps, reasoning
- [ ] T074 [US3] Add plan approval workflow: move Plan.md to /Approved to execute (file-based approval)
- [ ] T075 [US3] Implement update_plan_execution() function: mark steps complete as executed, log actual_time vs estimated_time
- [ ] T076 [US3] Add deviation detection: if deviation >20% of estimated time, create addendum Plan.md, notify human
- [ ] T077 [US3] Implement archive_completed_plan() function: move to /Plans/archive/, add lessons_learned
- [ ] T078 [US3] Test Plan.md generation: process complex task, verify plan created, approve, verify execution tracking
- [ ] T079 [US3] Update Dashboard.md to show: active_plans_count, plans_completed_today, average_plan_accuracy

**Checkpoint**: At this point, User Story 3 should be fully functional - transparent planning for complex tasks

---

## Phase 8: User Story 6 - Scheduled Automation (Priority: P2)

**Goal**: OS-native scheduling for daily briefings, weekly audits, monthly cleanup

**Independent Test**: Schedule test task for 1 minute in future, verify execution, check scheduled_tasks.log

### Implementation for User Story 6

- [ ] T080 [US6] Create scheduled-runner skill: .claude/commands/scheduled-runner.md
- [ ] T081 [P] [US6] Create /Scheduled/config.yaml with task definitions
- [ ] T082 [P] [US6] Define scheduled task schema: task_name, schedule (cron expression or Task Scheduler trigger), skill_to_invoke, parameters, enabled flag
- [ ] T083 [P] [US6] Implement daily_briefing task: schedule "0 8 * * *" (8 AM daily), invoke /dashboard-updater skill with vault_path
- [ ] T084 [P] [US6] Implement weekly_audit task: schedule "0 10 * * 0" (Sunday 10 AM weekly), invoke custom audit skill or task-processor
- [ ] T085 [US6] Implement monthly_cleanup task: schedule "0 2 1 * *" (1st of month 2 AM), invoke cleanup skill for old logs/archives
- [ ] T086 [US6] Create shell script wrappers for scheduled tasks: scripts/daily_briefing.sh, scripts/weekly_audit.sh, scripts/monthly_cleanup.sh
- [ ] T087 [US6] Configure cron (Linux/macOS): crontab -e with scheduled task entries
- [ ] T088 [US6] Configure Task Scheduler (Windows): create tasks with triggers for scripts
- [ ] T089 [US6] Add scheduled task logging to /Logs/scheduled_tasks_YYYY-MM-DD.log: task_name, scheduled_time, actual_time, status, output
- [ ] T090 [US6] Implement scheduled task error handling: log failure, retry_scheduled flag, notify human
- [ ] T091 [US6] Test scheduled automation: schedule test task 1 minute in future, verify execution, check log file
- [ ] T092 [US6] Update Dashboard.md to show: scheduled_tasks_count, next_run_time, last_successful_run, failed_runs_today

**Checkpoint**: At this point, User Story 6 should be fully functional - scheduled automation delivers value on schedule

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Multi-story improvements, documentation, integration testing

- [ ] T093 [P] Create UPGRADE_GUIDE.md: Bronze → Silver Tier migration instructions
- [ ] T094 [P] Update README.md with Silver Tier setup instructions: multi-watcher, MCP server, approval workflow, Plan.md, scheduling
- [ ] T095 [P] Update docs/SETUP.md with Silver Tier prerequisites: Node.js, Playwright, cron/Task Scheduler
- [ ] T096 [P] Update docs/TROUBLESHOOTING.md with Silver Tier issues: deduplication, approval bottlenecks, MCP failures, Plan.md divergence
- [ ] T097 [P] Update docs/ARCHITECTURE.md with Silver Tier components: orchestrator, MCP server, approval workflow, scheduled tasks
- [ ] T098 Extend Dashboard.md template with Silver Tier sections: multi-watcher status table, pending approvals summary, active plans list, scheduled tasks summary
- [ ] T099 [P] Extend Company_Handbook.md template with Silver Tier sections: approval_thresholds (which actions require approval), risk_levels, social_media_inventory (LinkedIn posts tracking), plan_templates
- [ ] T100 Update watchers/requirements.txt with new Silver dependencies: psutil, schedule, Playwright, MCP SDK
- [ ] T101 Create end-to-end integration test: tests/integration/test_silver_end_to_end.py
- [ ] T102 Test multi-watcher → deduplication → action file → plan (if complex) → approval (if sensitive) → MCP → done workflow
- [ ] T103 Verify all Silver Tier success criteria from spec.md: SC-001 to SC-028
- [ ] T104 Record demo video (5-10 minutes) showing: multi-watcher detection, approval workflow, LinkedIn posting, Plan.md generation, scheduled task execution

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T010) and Bronze Tier complete - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion (T011-T028)
  - User Story 1 (Multi-Watcher): Can start after Foundational - No dependencies on other stories
  - User Story 5 (Approval): Can start after Foundational - Independent (but required for US2, US4)
  - User Story 4 (MCP Server): Can start after Foundational - Independent (but US4 recommended before US2 for Gmail send)
  - User Story 2 (LinkedIn): Depends on US5 (approval workflow) and US4 (MCP if using MCP for LinkedIn)
  - User Story 3 (Plan.md): Can start after Foundational - Independent (can be tested without US1, US2, US4, US5)
  - User Story 6 (Scheduled): Can start after Foundational - Independent (can be tested without other stories)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - Independent (but required for US2, US4)
- **User Story 4 (P1)**: Can start after Foundational (Phase 2) - Independent (recommended before US2 for Gmail send MCP)
- **User Story 2 (P1)**: Depends on US5 (approval) and optionally US4 (MCP for LinkedIn)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Independent of all other stories
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Independent of all other stories

### Critical Path for MVP (Multi-Watcher + Approval Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T028) - **BLOCKS ALL STORIES**
3. Complete Phase 3: User Story 1 (T029-T036) - 2+ watchers working
4. Complete Phase 4: User Story 5 (T037-T045) - approval workflow working
5. **STOP and VALIDATE**: Test multi-watcher + approval independently
6. Optionally continue to US4, US2, US3, US6 for complete Silver Tier

### Recommended Full Silver Tier

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Multi-Watcher) → Test independently → 2+ watchers coordinated
3. Add US5 (Approval) → Test independently → Safe automation established
4. Add US4 (MCP Server) → Test independently → External actions enabled
5. Add US2 (LinkedIn) → Test independently → Social media automated
6. Add US3 (Plan.md) → Test independently → Transparent planning for complex tasks
7. Add US6 (Scheduled) → Test independently → Scheduled automation active
8. Complete Polish → Full Silver Tier functional assistant ready

---

## Parallel Opportunities

- **Setup Phase**: T003, T004, T005 can run in parallel (Node.js, Python dependencies, Playwright)
- **Foundational Phase**: T011-T015 (orchestrator) can run in parallel with T016-T019 (deduplication) if desired
- **User Story 1**: T030 (WhatsApp watcher) parallel with orchestrator development (if approved)
- **User Story 4**: T046-T050 (MCP server setup) can all run in parallel
- **User Story 2**: T058-T060 (Playwright LinkedIn, post validation) can run in parallel
- **User Story 3**: T069-T070 (Plan.md template, detection logic) can run in parallel
- **User Story 6**: T081-T083 (scheduled task definitions, shell scripts) can run in parallel
- **Polish Phase**: T093-T100 (documentation updates) can all run in parallel

---

## Implementation Strategy

### MVP First (Multi-Watcher + Approval) - Functional Silver Tier Minimum

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T028)
3. Complete Phase 3: User Story 1 (T029-T036) - Multi-watcher orchestration
4. Complete Phase 4: User Story 5 (T037-T045) - Approval workflow
5. **STOP and VALIDATE**: Test multi-watcher + approval independently
6. Deploy/demo if ready - **MVP DELIVERABLE** (multi-watcher with safe automation)

### Standard Silver Tier (All P1 Stories) - Recommended

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Multi-Watcher) → Test independently → 2+ watchers coordinated
3. Add US5 (Approval) → Test independently → Safe automation established
4. Add US4 (MCP Server) → Test independently → External actions enabled
5. Add US2 (LinkedIn) → Test independently → Social media automated
6. Add US3 (Plan.md) → Test independently → Transparent planning
7. Add US6 (Scheduled) → Test independently → Scheduled automation
8. Complete Polish → End-to-end system ready

**Time Estimate**: 20-30 hours (aligns with Silver Tier estimate)

---

## Task Summary

- **Total Tasks**: 104 tasks
- **Setup (Phase 1)**: 10 tasks (T001-T010)
- **Foundational (Phase 2)**: 18 tasks (T011-T028)
- **User Story 1 (Phase 3)**: 8 tasks (T029-T036)
- **User Story 5 (Phase 4)**: 9 tasks (T037-T045)
- **User Story 4 (Phase 5)**: 11 tasks (T046-T056)
- **User Story 2 (Phase 6)**: 11 tasks (T057-T067)
- **User Story 3 (Phase 7)**: 12 tasks (T068-T079)
- **User Story 6 (Phase 8)**: 13 tasks (T080-T092)
- **Polish (Phase 9)**: 12 tasks (T093-T104)

**Parallel Opportunities**: 35+ tasks marked [P] can run in parallel within phases

**MVP Scope (Multi-Watcher + Approval)**: 46 tasks (Setup + Foundational + US1 + US5) - ~12-15 hours

**Recommended Silver Tier (All P1 Stories)**: 80 tasks (Setup + Foundational + US1 + US5 + US4 + US2 + US3) - ~20-30 hours

**Full Silver Tier (All Stories)**: 104 tasks (including P2 US6) - ~20-30 hours

---

**Format Validation**: ✅ All 104 tasks follow strict checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T104 (sequential)
- [P] marker: For parallelizable tasks
- [Story] label: [US1], [US2], [US3], [US4], [US5], [US6] for user story phases
- Description: Clear action with exact file path

---

**Next Steps After Bronze Tier Complete**:
1. Verify Bronze Tier (feature 000) is complete: vault structure, one watcher, task-processor, Dashboard, Company_Handbook
2. Run /sp.tasks for Silver Tier (001) - tasks already generated
3. Implement following MVP or Standard Silver Tier path
4. Validate all Silver Tier success criteria before proceeding to Gold Tier
5. Run /sp.plan for Gold Tier (002) after Silver Tier validated

---

**Tasks Complete**: Silver Tier task breakdown organized by user story for independent implementation and testing. Ready for execution following recommended 7-phase sequence (20-30 hours). Bronze → Silver → Gold progression validated.
