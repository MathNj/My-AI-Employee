# Gold Tier Task Breakdown

**Feature**: 002-gold-tier-ai-employee (Gold Tier Personal AI Employee)
**Branch**: 002-gold-tier-ai-employee
**Date**: 2026-01-17
**Status**: Draft

## Overview

This document breaks down Gold Tier implementation into actionable tasks organized by user story. Each user story is independently testable with clear acceptance criteria.

**Total Tasks**: 138 tasks across 9 phases

**User Stories** (10 stories from spec.md):
- **US-01** (P1): Autonomous Email Monitoring and Response Drafting
- **US-02** (P1): Financial Event Detection and Invoice Management
- **US-03** (P2): Multi-Platform Social Media Posting with Approval Workflow
- **US-04** (P2): WhatsApp Urgent Message Detection
- **US-05** (P1): Autonomous Multi-Step Task Completion with Ralph Wiggum Loop
- **US-06** (P2): Weekly CEO Briefing with Business Audit
- **US-07** (P3): Calendar Event Preparation and Reminders
- **US-08** (P3): Slack Team Communication Monitoring
- **US-09** (P3): File System Drop Zone Processing
- **US-10** (P1): Comprehensive Audit Logging for All Actions

**Task Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Phase 1: Setup & Prerequisites (10 tasks, T001-T010)

**Goal**: Verify Silver Tier completion, install dependencies, create directory structure

**Independent Test**: Run `python watchers/orchestrator_cli.py status` and verify no errors, all dependencies installed

### Implementation

- [ ] T001 Verify Silver Tier (feature 001) completion and operational status
- [ ] T002 [P] Upgrade system RAM to 16GB if currently 8GB (6 watchers require more memory)
- [ ] T003 [P] Install Python 3.13+ if not already installed
- [ ] T004 [P] Install Node.js v24+ LTS for MCP servers
- [ ] T005 [P] Install Python dependencies: psutil, google-auth, google-api-python-client, playwright, watchdog, requests, pyyaml
- [ ] T006 [P] Install Playwright browsers: `playwright install chromium`
- [ ] T007 [P] Create Orchestrator directory structure in watchers/
- [ ] T008 [P] Create MCP servers directory structure: mcp-servers/gmail-mcp, mcp-servers/xero-mcp, mcp-servers/linkedin-mcp, mcp-servers/x-poster, mcp-servers/facebook-mcp, mcp-servers/instagram-mcp
- [ ] T009 [P] Create vault folder structure: /Briefings, /Plans/active, /Plans/archive, /In_Progress (for Ralph loop)
- [ ] T010 Verify all prerequisites installed and directories created

---

## Phase 2: Foundational - Orchestrator & Watchdog (18 tasks, T011-T028)

**Goal**: Build orchestrator and watchdog for managing 6 watcher processes with health monitoring and auto-restart

**Independent Test**: Start orchestrator with `python watchers/orchestrator.py start`, verify all 6 watchers launch, kill one watcher, verify auto-restart within 60 seconds

**BLOCKS**: All user stories (US1-US10) - Orchestrator is foundation for Gold Tier

### Implementation

- [ ] T011 Create watchers/base_watcher.py with BaseWatcher class (check_for_updates, create_action_file, run methods)
- [ ] T012 [P] Create watchers/orchestrator.py with MultiWatcherManager class
- [ ] T013 [P] Implement watcher launch logic in orchestrator.py using subprocess.Popen
- [ ] T014 [P] Implement health check loop in orchestrator.py (every 60 seconds)
- [ ] T015 [P] Implement PID tracking in orchestrator.py (maintain PID list for all watchers)
- [ ] T016 [P] Implement watcher restart logic in orchestrator.py (crashed watcher auto-restart)
- [ ] T017 [P] Implement error count tracking in orchestrator.py (consecutive errors, pause after 3)
- [ ] T018 [P] Create watchers/watchdog.py to monitor orchestrator.py process
- [ ] T019 [P] Implement PID file creation in orchestrator.py (write orchestrator.pid on startup)
- [ ] T020 [P] Implement orchestrator PID monitoring in watchdog.py (read orchestrator.pid, check if running)
- [ ] T021 [P] Implement orchestrator restart logic in watchdog.py (restart if crashed)
- [ ] T022 [P] Create watchers/orchestrator_cli.py with status, stop, restart commands
- [ ] T023 [P] Implement status command in orchestrator_cli.py (show all watcher PIDs, health, uptime)
- [ ] T024 [P] Implement stop command in orchestrator_cli.py (graceful shutdown of all watchers)
- [ ] T025 [P] Implement restart command in orchestrator_cli.py (stop + start)
- [ ] T026 Create watchers/orchestrator_config.json with enable/disable and interval settings for all 6 watchers
- [ ] T027 Create watchers/orchestrator_state.json for persisting watcher state (PID, last check, error count)
- [ ] T028 Test orchestrator and watchdog: launch all 6 watchers, kill one, verify auto-restart, verify watchdog detects orchestrator crash

---

## Phase 3: User Story 1 - Email Monitoring (P1) (8 tasks, T029-T036)

**Goal**: Gmail Watcher detects unread important emails within 2 minutes, creates action files with complete metadata

**Independent Test**: Send test email to monitored Gmail account, verify watcher creates EMAIL_[id].md in /Needs_Action within 2 minutes with valid YAML frontmatter (from, subject, snippet, message_id, labels)

**Prerequisites**: Phase 2 complete (orchestrator running)

### Implementation

- [ ] T029 [P] [US1] Enhance watchers/gmail_watcher.py for Gold Tier (filter for "unread important" emails only)
- [ ] T030 [P] [US1] Implement 2-minute check interval in gmail_watcher.py (per orchestrator_config.json)
- [ ] T031 [US1] Implement action file creation in gmail_watcher.py with YAML frontmatter (type: email, source: gmail_watcher, priority, status, timestamp, metadata)
- [ ] T032 [US1] Implement deduplication in gmail_watcher.py (track processed message_ids in gmail_processed_ids.json)
- [ ] T033 [US1] Add health status reporting to gmail_watcher.py (report to orchestrator every check)
- [ ] T034 [US1] Test gmail_watcher detects emails within 2 minutes (send test email, verify action file created)
- [ ] T035 [US1] Test email action file format (verify YAML frontmatter valid, all required fields present)
- [ ] T036 [US1] Test gmail_watcher integration with orchestrator (verify health status reporting, auto-restart on crash)

---

## Phase 4: User Story 2 - Financial Event Detection (P1) (10 tasks, T037-T046)

**Goal**: Xero Watcher detects new invoices, overdue invoices, payments, large transactions >$500 within 5 minutes

**Independent Test**: Create test invoice in Xero sandbox, verify watcher creates XERO_NEW_INVOICE_[timestamp].md in /Needs_Action within 5 minutes with invoice details (customer, amount, due date)

**Prerequisites**: Phase 2 complete (orchestrator running)

### Implementation

- [ ] T037 [P] [US2] Create watchers/xero_watcher.py with XeroWatcher class extending BaseWatcher
- [ ] T038 [P] [US2] Implement Xero OAuth 2.0 authentication in xero_watcher.py (authorization code flow, 30-min token refresh)
- [ ] T039 [P] [US2] Implement 5-minute check interval in xero_watcher.py (per orchestrator_config.json)
- [ ] T040 [US2] Implement new invoice detection in xero_watcher.py (query Xero API for invoices created since last check)
- [ ] T041 [US2] Implement overdue invoice detection in xero_watcher.py (query invoices where due_date < today - 7 days)
- [ ] T042 [US2] Implement large transaction detection in xero_watcher.py (query transactions where amount > $500)
- [ ] T043 [US2] Implement payment received detection in xero_watcher.py (query payments, update Dashboard.md cash flow)
- [ ] T044 [US2] Implement action file creation in xero_watcher.py with YAML frontmatter (type: xero, metadata: invoice_number, contact_name, amount, due_date, status)
- [ ] T045 [US2] Test xero_watcher detects invoices within 5 minutes (create test invoice in Xero, verify action file)
- [ ] T046 [US2] Test overdue invoice detection (create test invoice with due_date 8 days ago, verify urgent priority flag)

---

## Phase 5: User Story 5 - Ralph Wiggum Loop (P1) (10 tasks, T047-T056)

**Goal**: Ralph loop autonomously completes multi-step tasks without additional human prompts until completion criteria met

**Independent Test**: Place 3 task files in /Needs_Action, invoke Ralph loop with "all files moved to /Done" criteria, verify Claude completes all tasks without additional prompts, exits when all files in /Done

**Prerequisites**: Phase 2 complete (orchestrator running), Silver Tier approval workflow operational

### Implementation

- [ ] T047 [P] [US5] Install Ralph Wiggum Stop Hook from official repo (clone to .claude/plugins/ralph-wiggum)
- [ ] T048 [P] [US5] Build Ralph Wiggum Stop Hook (npm install, npm run build)
- [ ] T049 [US5] Create .claude/plugins/ralph-wiggum/config.json with max_iterations=10, max_duration_minutes=30
- [ ] T050 [US5] Configure completion_criteria="file_movement" in Ralph config (target folder: /Done)
- [ ] T051 [US5] Implement stuck detection in Ralph hook (same error 3x = escalate to human)
- [ ] T052 [US5] Create test Plan.md with 3 steps in /Plans/active/ (objective, steps with checkboxes)
- [ ] T053 [US5] Test Ralph loop completes 3 steps autonomously (invoke /ralph, verify no additional prompts needed)
- [ ] T054 [US5] Test max_iterations limit (create plan with 15 steps, verify stops at 10 iterations)
- [ ] T055 [US5] Test stuck detection (create plan that fails 3x on same step, verify escalation to human)
- [ ] T056 [US5] Test file movement completion (verify Ralph loop exits when target file moved to /Done)

---

## Phase 6: User Story 10 - Audit Logging (P1) (12 tasks, T057-T068)

**Goal**: Every action logged to /Logs/audit_YYYY-MM-DD.json with timestamp, action_type, actor, target, parameters, approval_status, result

**Independent Test**: Trigger test action (send email via approval workflow), verify /Logs/audit_YYYY-MM-DD.json created with entry containing all required fields (timestamp, action_type, actor, target, parameters, approval_status, result, file_created)

**Prerequisites**: Phase 2 complete (orchestrator running)

### Implementation

- [ ] T057 [P] [US10] Define audit log entry schema (JSON format with all required fields per spec.md)
- [ ] T058 [P] [US10] Implement audit logging in watchers/gmail_watcher.py (log watcher_activity events)
- [ ] T059 [P] [US10] Implement audit logging in watchers/xero_watcher.py (log watcher_activity events)
- [ ] T060 [P] [US10] Implement audit logging in watchers/whatsapp_watcher.py (log watcher_activity events)
- [ ] T061 [P] [US10] Implement audit logging in watchers/calendar_watcher.py (log watcher_activity events)
- [ ] T062 [P] [US10] Implement audit logging in watchers/slack_watcher.py (log watcher_activity events)
- [ ] T063 [P] [US10] Implement audit logging in watchers/filesystem_watcher.py (log watcher_activity events)
- [ ] T064 [P] [US10] Implement audit logging in watchers/orchestrator.py (log system_health events)
- [ ] T065 [US10] Implement daily log rotation (create new file /Logs/audit_YYYY-MM-DD.json at midnight)
- [ ] T066 [US10] Implement 90-day log cleanup task (delete logs older than 90 days, optional compression >30 days)
- [ ] T067 [US10] Test audit logging completeness (trigger 10 different actions, verify all logged with correct fields)
- [ ] T068 [US10] Test log rotation and cleanup (verify new file created at midnight, verify old files deleted after 90 days)

---

## Phase 7: User Story 3 - Social Media Posting (P2) (14 tasks, T069-T082)

**Goal**: Multi-platform social media posting (LinkedIn, Twitter/X, Facebook, Instagram) via unified approval workflow

**Independent Test**: Trigger social-media-manager skill, verify generates approval file with platform-specific sections in /Pending_Approval, move to /Approved, verify posts to all platforms within 5 minutes via respective MCP servers

**Prerequisites**: Phase 2 complete (orchestrator running), Phase 6 complete (audit logging), Gmail MCP server operational (from Silver Tier)

### Implementation

- [ ] T069 [P] [US3] Create mcp-servers/linkedin-mcp/package.json with dependencies
- [ ] T070 [P] [US3] Implement mcp-servers/linkedin-mcp/src/index.ts with MCP server initialization
- [ ] T071 [P] [US3] Implement post_linkedin tool in linkedin-mcp (LinkedIn Marketing Developer Platform API)
- [ ] T072 [P] [US3] Create mcp-servers/x-poster/package.json with dependencies
- [ ] T073 [P] [US3] Implement mcp-servers/x-poster/src/index.ts with MCP server initialization
- [ ] T074 [P] [US3] Implement post_tweet tool in x-poster using Playwright automation (Twitter/X no API)
- [ ] T075 [P] [US3] Create mcp-servers/facebook-mcp/package.json with dependencies
- [ ] T076 [P] [US3] Implement mcp-servers/facebook-mcp/src/index.ts with MCP server initialization
- [ ] T077 [P] [US3] Implement post_facebook tool in facebook-mcp (Facebook Graph API)
- [ ] T078 [P] [US3] Create mcp-servers/instagram-mcp/package.json with dependencies
- [ ] T079 [P] [US3] Implement mcp-servers/instagram-mcp/src/index.ts with MCP server initialization
- [ ] T080 [P] [US3] Implement post_instagram tool in instagram-mcp (Instagram Graph API, two-step workflow)
- [ ] T081 [US3] Implement social-media-manager skill with unified approval file (single approval, platform-specific sections)
- [ ] T082 [US3] Test multi-platform posting (generate approval file, approve, verify posts to all 4 platforms, verify audit log entries)

---

## Phase 8: User Story 4 - WhatsApp Urgent Messages (P2) (10 tasks, T083-T092)

**Goal**: WhatsApp Watcher detects urgent keywords (urgent, ASAP, invoice, payment, help, emergency) within 30 seconds

**Independent Test**: Send test WhatsApp message with urgent keyword to monitored account, verify watcher creates WHATSAPP_URGENT_[timestamp].md in /Needs_Action within 30 seconds with urgent priority flag

**Prerequisites**: Phase 2 complete (orchestrator running), Phase 6 complete (audit logging)

### Implementation

- [ ] T083 [P] [US4] Enhance watchers/whatsapp_watcher.py for Gold Tier (add urgent keyword detection)
- [ ] T084 [P] [US4] Implement 30-second check interval in whatsapp_watcher.py (per orchestrator_config.json)
- [ ] T085 [US4] Implement persistent browser profile in whatsapp_watcher.py (playwright chromium persistent_context with user_data_dir)
- [ ] T086 [US4] Implement urgent keyword matching in whatsapp_watcher.py (urgent, ASAP, invoice, payment, help, emergency)
- [ ] T087 [US4] Implement QR code scan detection in whatsapp_watcher.py (detect logout, create alert for re-auth)
- [ ] T088 [US4] Implement action file creation in whatsapp_watcher.py with YAML frontmatter (type: whatsapp, priority: urgent, metadata: sender_name, phone_number, message, keyword_matched)
- [ ] T089 [US4] Add health status reporting to whatsapp_watcher.py (report to orchestrator every check)
- [ ] T090 [US4] Test whatsapp_watcher detects urgent messages within 30 seconds (send test message, verify action file)
- [ ] T091 [US4] Test session persistence (restart watcher, verify no QR rescan needed, verify session persists)
- [ ] T092 [US4] Test logout detection (log out from phone, verify watcher detects QR code page, creates alert in /Needs_Action)

---

## Phase 9: User Story 6 - CEO Briefing (P2) (12 tasks, T093-T104)

**Goal**: Weekly Sunday 7 AM autonomous CEO briefing with revenue vs targets, completed tasks, bottlenecks, proactive suggestions

**Independent Test**: Manually trigger ceo-briefing-generator skill, verify reads Xero data, /Done folder, /Logs, Business_Goals.md, generates briefing in /Briefings with all required sections

**Prerequisites**: Phase 2 complete (orchestrator running), Phase 4 complete (Xero watcher operational), Phase 6 complete (audit logging)

### Implementation

- [ ] T093 [P] [US6] Create .claude/commands/ceo-briefing-generator.md skill with input parameters, output format, usage examples
- [ ] T094 [P] [US6] Implement Xero API query in ceo-briefing-generator (GET /Invoices?where=Date>=DateTime(-7days))
- [ ] T095 [P] [US6] Implement /Done folder scanning in ceo-briefing-generator (parse completed tasks, count by category)
- [ ] T096 [P] [US6] Implement /Logs scanning in ceo-briefing-generator (parse errors, warnings, summarize patterns)
- [ ] T097 [P] [US6] Implement Business_Goals.md parsing in ceo-briefing-generator (read targets, KPIs, active projects)
- [ ] T098 [US6] Generate briefing sections: Executive Summary (2-3 sentences), Weekly Revenue (total + MTD vs target + trend), Completed Tasks (count by category + major milestones), Bottlenecks (tasks taking longer than expected + recommended solutions), Proactive Suggestions (unused subscriptions, cost optimization, upcoming deadlines)
- [ ] T099 [US6] Implement subscription audit logic in ceo-briefing-generator (flag subscriptions with no usage 30+ days or cost increase >20%)
- [ ] T100 [US6] Implement briefing file creation in /Briefings folder (filename: YYYY-MM-DD_Monday_Briefing.md)
- [ ] T101 [US6] Implement Dashboard.md update with link to latest briefing and notification flag
- [ ] T102 [US6] Create scheduled task for Sunday 7 AM execution (cron: `0 7 * * 0` or Task Scheduler)
- [ ] T103 [US6] Test CEO briefing generation (manually trigger skill, verify all sections populated correctly)
- [ ] T104 [US6] Test scheduled execution (configure scheduled task, verify briefing generated Sunday 7 AM)

---

## Phase 10: User Story 7 - Calendar Events (P3) (8 tasks, T105-T112)

**Goal**: Calendar Watcher detects upcoming events 1-48 hours ahead within 10 minutes, creates action files with event details and preparation suggestions

**Independent Test**: Create test calendar event 24 hours from now, verify watcher creates CALENDAR_[event_id]_[timestamp].md in /Needs_Action within 10 minutes with event details (title, time, location, attendees) and preparation suggestions

**Prerequisites**: Phase 2 complete (orchestrator running), Phase 6 complete (audit logging)

### Implementation

- [ ] T105 [P] [US7] Create watchers/calendar_watcher.py with CalendarWatcher class extending BaseWatcher
- [ ] T106 [P] [US7] Implement Google Calendar API authentication in calendar_watcher.py (OAuth 2.0)
- [ ] T107 [P] [US7] Implement 10-minute check interval in calendar_watcher.py (per orchestrator_config.json)
- [ ] T108 [US7] Implement event detection in calendar_watcher.py (query events 1-48 hours ahead: events.list?timeMin=now&timeMax=now+48h)
- [ ] T109 [US7] Implement event modification/cancellation detection in calendar_watcher.py (detect changes, update or remove action files)
- [ ] T110 [US7] Implement action file creation in calendar_watcher.py with YAML frontmatter (type: calendar, metadata: event_id, title, start_time, end_time, location, attendees)
- [ ] T111 [US7] Implement preparation suggestions generation in calendar_watcher.py (context-aware suggestions based on event type and attendees)
- [ ] T112 [US7] Test calendar_watcher detects events within 10 minutes (create test event 24 hours ahead, verify action file with details and suggestions)

---

## Phase 11: User Story 8 - Slack Monitoring (P3) (8 tasks, T113-T120)

**Goal**: Slack Watcher monitors channels for keywords (urgent, important, help, issue, problem) within 1 minute, creates action files with message context

**Independent Test**: Post test message with monitored keyword to Slack channel, verify watcher creates slack_keyword_match_[timestamp].md in /Needs_Action within 1 minute with message content and channel context

**Prerequisites**: Phase 2 complete (orchestrator running), Phase 6 complete (audit logging)

### Implementation

- [ ] T113 [P] [US8] Create watchers/slack_watcher.py with SlackWatcher class extending BaseWatcher
- [ ] T114 [P] [US8] Implement Slack Web API authentication in slack_watcher.py (bot token)
- [ ] T115 [P] [US8] Implement 1-minute check interval in slack_watcher.py (per orchestrator_config.json)
- [ ] T116 [US8] Implement keyword matching in slack_watcher.py (monitor: urgent, important, help, issue, problem)
- [ ] T117 [US8] Implement thread consolidation in slack_watcher.py (same keyword mentioned multiple times → single action file with thread context)
- [ ] T118 [US8] Implement action file creation in slack_watcher.py with YAML frontmatter (type: slack, metadata: channel, sender, message, timestamp, thread_id)
- [ ] T119 [US8] Add health status reporting to slack_watcher.py (report to orchestrator every check)
- [ ] T120 [US8] Test slack_watcher detects keyword matches within 1 minute (post test message, verify action file with context)

---

## Phase 12: User Story 9 - File System Drop Zone (P3) (8 tasks, T121-T128)

**Goal**: Filesystem Watcher monitors /Inbox folder in real-time (<5 seconds), creates action files for detected files with metadata (name, size, type)

**Independent Test**: Copy test file (PDF, DOCX, image) to /Inbox folder, verify watcher immediately creates FILE_[timestamp]_[filename].md in /Needs_Action with file metadata

**Prerequisites**: Phase 2 complete (orchestrator running), Phase 6 complete (audit logging)

### Implementation

- [ ] T121 [P] [US9] Create watchers/filesystem_watcher.py with FilesystemWatcher class extending BaseWatcher
- [ ] T122 [P] [US9] Implement real-time file system monitoring in filesystem_watcher.py (use watchdog library, on_created event)
- [ ] T123 [P] [US9] Implement file metadata extraction in filesystem_watcher.py (filename, file_size, file_type, file_path)
- [ ] T124 [US9] Implement file type detection in filesystem_watcher.py (PDF, DOCX, image → suggest appropriate actions)
- [ ] T125 [US9] Implement action file creation in filesystem_watcher.py with YAML frontmatter (type: file, metadata: filename, file_size, file_type, file_path)
- [ ] T126 [US9] Implement processed file cleanup in filesystem_watcher.py (move processed files to /Inbox/Archive to prevent re-detection)
- [ ] T127 [US9] Add health status reporting to filesystem_watcher.py (report to orchestrator)
- [ ] T128 [US9] Test filesystem_watcher detects files in real-time (copy test file, verify action file created <5 seconds)

---

## Phase 13: Cross-Domain Integration & Correlation (6 tasks, T129-T134)

**Goal**: Claude Code correlates related events across watchers (e.g., Gmail invoice email + Xero invoice creation) into unified plans

**Independent Test**: Trigger related events from 2 watchers (send invoice email to self, create invoice in Xero), verify Claude consolidates into single Plan.md with deduplication logged

**Prerequisites**: All watcher phases complete (Phases 3-4, 8-12)

### Implementation

- [ ] T129 [P] Implement cross-domain event detection in task-processor skill (read all /Needs_Action files, correlate by context)
- [ ] T130 [P] Implement deduplication logic in task-processor skill (same invoice ID, same customer, similar timestamp → consolidate)
- [ ] T131 [P] Implement Plan.md creation for correlated events (consolidate multiple action files into single Plan.md)
- [ ] T132 [P] Implement deduplication logging in task-processor skill (log "consolidated EMAIL_123 and XERO_456 into PLAN_678")
- [ ] T133 [P] Test cross-domain correlation (trigger related events from Gmail + Xero, verify consolidation)
- [ ] T134 Test deduplication (trigger same event from 2 watchers, verify single plan created, deduplication logged)

---

## Phase 14: Polish, Documentation & Testing (10 tasks, T135-T144)

**Goal**: Complete documentation, end-to-end testing, demo video, upgrade guide

**Independent Test**: Run end-to-end integration test tests/integration/test_gold_end_to_end.py, verify all 28 success criteria from spec.md pass

**Prerequisites**: All previous phases complete

### Implementation

- [ ] T135 [P] Create UPGRADE_GUIDE.md with Silver → Gold migration instructions
- [ ] T136 [P] Update README.md with Gold Tier content (6 watchers, 6 MCP servers, orchestrator, Ralph loop, CEO briefing, audit logging)
- [ ] T137 [P] Update Company_Handbook.md with Gold Tier sections (orchestrator management, Ralph loop usage, CEO briefing interpretation)
- [ ] T138 [P] Update Dashboard.md template with Gold Tier sections (orchestrator status, Ralph loop status, CEO briefing link, audit log summary)
- [ ] T139 [P] Create end-to-end integration test in tests/integration/test_gold_end_to_end.py
- [ ] T140 [P] Verify all 28 success criteria from spec.md (SC-001 through SC-028)
- [ ] T141 [P] Record demo video (10-15 minutes) showing full Gold Tier workflow (orchestrator launch, all 6 watchers detecting events, Ralph loop, CEO briefing, audit logs)
- [ ] T142 Test orchestrator auto-start on boot (reboot computer, verify all 6 watchers running after boot)
- [ ] T143 Test 99%+ uptime over 7-day period (run orchestrator for 7 days, verify auto-restart works, calculate uptime)
- [ ] T144 Test peak load handling (simulate 100+ events per day, verify system handles without performance degradation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (Silver Tier must be complete first)
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T010) AND Silver Tier complete - **BLOCKS ALL USER STORIES**
- **User Stories (Phases 3-13)**: All depend on Foundational phase completion (T011-T028)
  - **US1 (Email)**: Can start after Foundational - No dependencies on other stories
  - **US2 (Financial)**: Can start after Foundational - Independent (but recommended before US6 for CEO briefing)
  - **US5 (Ralph Loop)**: Can start after Foundational - Independent (requires Silver Tier approval workflow)
  - **US10 (Audit Logging)**: Can start after Foundational - Independent (recommended early, blocks nothing)
  - **US3 (Social Media)**: Can start after Foundational - Independent (requires Gmail MCP from Silver Tier)
  - **US4 (WhatsApp)**: Can start after Foundational - Independent
  - **US6 (CEO Briefing)**: Requires US2 (Xero watcher) and US10 (audit logging) complete
  - **US7 (Calendar)**: Can start after Foundational - Independent
  - **US8 (Slack)**: Can start after Foundational - Independent
  - **US9 (File System)**: Can start after Foundational - Independent
- **Cross-Domain Integration (Phase 13)**: Requires all watcher phases complete (Phases 3-4, 8-12)
- **Polish (Phase 14)**: Requires all previous phases complete

### Critical Path for MVP (P1 Stories - Functional Gold Tier Minimum)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T028) - **BLOCKS ALL STORIES**
3. Complete Phase 3: User Story 1 (T029-T036) - Email monitoring working
4. Complete Phase 4: User Story 2 (T037-T046) - Financial event detection working
5. Complete Phase 5: User Story 5 (T047-T056) - Ralph loop working
6. Complete Phase 6: User Story 10 (T057-T068) - Audit logging working
7. **STOP and VALIDATE**: Test P1 stories independently (no social media, no WhatsApp, no CEO briefing, no calendar, no Slack, no filesystem yet)
8. Deploy/demo if ready - **MVP DELIVERABLE** (Email + Financial + Ralph + Audit = Core Gold Tier)

### Recommended Full Gold Tier (All P1 + P2 Stories)

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Email) → Test independently → Email monitoring working
3. Add US2 (Financial) → Test independently → Financial event detection working
4. Add US5 (Ralph Loop) → Test independently → Autonomous multi-step working
5. Add US10 (Audit Logging) → Test independently → Complete audit trail working
6. Add US3 (Social Media) → Test independently → Multi-platform posting working
7. Add US4 (WhatsApp) → Test independently → Urgent message detection working
8. Add US6 (CEO Briefing) → Test independently → Weekly business audit working
9. Add US7 (Calendar) → Test independently → Calendar reminders working
10. Add US8 (Slack) → Test independently → Team communication monitoring working
11. Add US9 (File System) → Test independently → Drop zone processing working
12. Add Cross-Domain Integration → Test correlation
13. Complete Polish → End-to-end Gold Tier autonomous employee ready

### MVP First (P1 Only) - Functional Gold Tier Minimum

**Scope**: Email monitoring + Financial detection + Ralph loop + Audit logging (4 P1 stories)
**Time Estimate**: 20-25 hours (Setup + Foundational + US1 + US2 + US5 + US10)
**Deliverable**: Autonomous email and financial monitoring with Ralph loop and complete audit trail

**Implementation Order**:
1. Setup → Foundational → US1 (Email) → US2 (Financial) → US5 (Ralph) → US10 (Audit) → Polish MVP

### Standard Gold Tier (P1 + P2 Stories) - Recommended

**Scope**: All P1 stories (US1, US2, US5, US10) + P2 stories (US3, US4, US6)
**Time Estimate**: 35-45 hours (aligns with Gold Tier estimate)

**Implementation Order**:
1. Setup → Foundational → US1 → US2 → US5 → US10 → US3 → US4 → US6 → Cross-Domain Integration → Polish

### Full Gold Tier (All Stories)

**Scope**: All 10 user stories (US1-US10) with comprehensive documentation and testing
**Time Estimate**: 40-50 hours

---

## Parallel Examples

### Phase 2 - Foundational (Parallel Opportunities)

```bash
# Launch orchestrator, watchdog, and CLI tools in parallel:
Task: "T012 Create watchers/orchestrator.py with MultiWatcherManager class"
Task: "T018 Create watchers/watchdog.py to monitor orchestrator.py process"
Task: "T022 Create watchers/orchestrator_cli.py with status, stop, restart commands"
Task: "T026 Create watchers/orchestrator_config.json with settings for all 6 watchers"
```

### Phase 7 - Social Media MCP Servers (Parallel Opportunities)

```bash
# Launch all 4 social MCP servers in parallel:
Task: "T069 Create mcp-servers/linkedin-mcp/package.json with dependencies"
Task: "T072 Create mcp-servers/x-poster/package.json with dependencies"
Task: "T075 Create mcp-servers/facebook-mcp/package.json with dependencies"
Task: "T078 Create mcp-servers/instagram-mcp/package.json with dependencies"
Task: "T071 Implement post_linkedin tool in linkedin-mcp"
Task: "T074 Implement post_tweet tool in x-poster using Playwright"
Task: "T077 Implement post_facebook tool in facebook-mcp"
Task: "T080 Implement post_instagram tool in instagram-mcp"
```

### Phase 14 - Polish (Parallel Opportunities)

```bash
# Launch documentation updates in parallel:
Task: "T135 Create UPGRADE_GUIDE.md with Silver → Gold migration"
Task: "T136 Update README.md with Gold Tier content"
Task: "T137 Update Company_Handbook.md with Gold Tier sections"
Task: "T138 Update Dashboard.md template with Gold Tier sections"
```

---

## Task Summary

- **Total Tasks**: 138 tasks organized across 14 phases
- **Setup**: 10 tasks
- **Foundational**: 18 tasks (BLOCKS all user stories until complete)
- **User Story 1 (P1)**: 8 tasks - Email monitoring
- **User Story 2 (P1)**: 10 tasks - Financial event detection
- **User Story 5 (P1)**: 10 tasks - Ralph Wiggum loop
- **User Story 10 (P1)**: 12 tasks - Audit logging
- **User Story 3 (P2)**: 14 tasks - Social media posting
- **User Story 4 (P2)**: 10 tasks - WhatsApp urgent messages
- **User Story 6 (P2)**: 12 tasks - CEO briefing
- **User Story 7 (P3)**: 8 tasks - Calendar events
- **User Story 8 (P3)**: 8 tasks - Slack monitoring
- **User Story 9 (P3)**: 8 tasks - File system drop zone
- **Cross-Domain Integration**: 6 tasks
- **Polish**: 10 tasks

**Parallel Opportunities**: 60+ tasks marked [P] can run in parallel

**Format Validation**: ✅ All 138 tasks follow checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T138 (sequential)
- [P] marker: For parallelizable tasks
- [Story] label: [US1], [US2], [US3], [US4], [US5], [US6], [US7], [US8], [US9], [US10] for user story phases

**Prerequisite**: Silver Tier (feature 001) must be complete before starting Gold Tier implementation

---

**Tasks Complete**: Gold Tier task breakdown with complete dependency graph, parallel opportunities, and implementation strategies. Ready for execution following recommended phase order: Setup → Foundational → User Stories (US1 → US2 → US5 → US10 → US3 → US4 → US6 → US7 → US8 → US9) → Cross-Domain Integration → Polish.

**Tier Progression**: Bronze (000) → Silver (001) → **Gold (002)** → Platinum (003) validated. Gold tier builds incrementally on Silver foundation with orchestrator + watchdog, 6 coordinated watchers, 6 MCP servers, Ralph Wiggum autonomous loop, CEO briefing, and comprehensive audit logging before Platinum Tier's cloud deployment.

---

**Next Steps**:
1. Review Gold Tier tasks.md file for approval
2. Verify Silver Tier (feature 001) is complete
3. Implement tasks following MVP (US1+US2+US5+US10) or Standard (all P1+P2 stories) path
4. Validate Gold Tier success criteria before proceeding to Platinum Tier
5. Run /sp.plan for Platinum Tier (feature 003) after Gold Tier validated
