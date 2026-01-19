---
id: 002
title: Gold Tier Task Breakdown
stage: tasks
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: 002-gold-tier-ai-employee
branch: 002-gold-tier-ai-employee
user: Najma-LP
command: /sp.tasks
labels: ["gold-tier", "tasks", "implementation", "breakdown", "orchestrator", "ralph-loop"]
links:
  spec: specs/002-gold-tier-ai-employee/spec.md
  plan: specs/002-gold-tier-ai-employee/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-gold-tier-ai-employee/tasks.md (138 tasks across 14 phases organized by user story)
tests:
  - Manual integration testing focus per plan.md (Phase 0 research complete, Phase 1 design complete)
  - End-to-end test in tests/integration/test_gold_end_to_end.py (Phase 14)
  - All 28 success criteria from spec.md validated (Phase 14)
---

## Prompt

for Gold Tier

## Response snapshot

Created comprehensive Gold Tier task breakdown with 138 tasks organized across 14 phases following user story structure from spec.md:

**Tasks File**: specs/002-gold-tier-ai-employee/tasks.md

**Task Organization**: 138 tasks across 14 phases following Silver Tier (feature 001) prerequisite

**Phase Breakdown**:

**Phase 1: Setup** (10 tasks, T001-T010)
- Verify Silver Tier completion, upgrade RAM to 16GB if needed
- Install Python 3.13+, install Node.js v24+ LTS, install Python dependencies, install Playwright
- Create Orchestrator and MCP servers directory structures
- Create vault folder structure: /Briefings, /Plans/active, /Plans/archive, /In_Progress

**Phase 2: Foundational** (18 tasks, T011-T028) - BLOCKS all user stories
- Orchestrator (7 tasks): MultiWatcherManager class, launch logic, health check loop, PID tracking, restart logic
- Watchdog (3 tasks): Monitor orchestrator PID, restart if crashed
- CLI tools (4 tasks): orchestrator_cli.py with status, stop, restart commands
- Configuration (2 tasks): orchestrator_config.json, orchestrator_state.json
- Testing (2 tasks): Test orchestrator and watchdog

**Phase 3: User Story 1 - Email Monitoring** (8 tasks, T029-T036) - P1
- Enhance gmail_watcher.py for Gold Tier (filter "unread important" emails)
- 2-minute check interval, action file creation with YAML frontmatter
- Deduplication (track processed message_ids), health status reporting
- Test gmail_watcher detects emails within 2 minutes

**Phase 4: User Story 2 - Financial Event Detection** (10 tasks, T037-T046) - P1
- Create xero_watcher.py with XeroWatcher class extending BaseWatcher
- Xero OAuth 2.0 authentication (30-min token refresh)
- Detect new invoices, overdue invoices (7+ days), large transactions (>$500), payments received
- 5-minute check interval, action file creation with YAML frontmatter
- Test xero_watcher detects invoices within 5 minutes

**Phase 5: User Story 5 - Ralph Wiggum Loop** (10 tasks, T047-T056) - P1
- Install Ralph Wiggum Stop Hook from official repo
- Configure max_iterations=10, max_duration_minutes=30, completion_criteria="file_movement"
- Implement stuck detection (same error 3x = escalate)
- Test Ralph loop completes 3 steps autonomously
- Test max_iterations limit, test stuck detection, test file movement completion

**Phase 6: User Story 10 - Audit Logging** (12 tasks, T057-T068) - P1
- Define audit log entry schema (JSON format with all required fields)
- Implement audit logging in all 6 watchers (gmail, xero, whatsapp, calendar, slack, filesystem)
- Implement audit logging in orchestrator (system_health events)
- Daily log rotation, 90-day log cleanup task
- Test audit logging completeness, test log rotation and cleanup

**Phase 7: User Story 3 - Social Media Posting** (14 tasks, T069-T082) - P2
- Create 4 MCP servers: linkedin-mcp, x-poster (Twitter/X), facebook-mcp, instagram-mcp
- Implement post_linkedin, post_tweet (Playwright), post_facebook, post_instagram tools
- Implement social-media-manager skill with unified approval file
- Test multi-platform posting (approve, verify posts to all 4 platforms)

**Phase 8: User Story 4 - WhatsApp Urgent Messages** (10 tasks, T083-T092) - P2
- Enhance whatsapp_watcher.py with urgent keyword detection (urgent, ASAP, invoice, payment, help, emergency)
- 30-second check interval, persistent browser profile (Playwright)
- QR code scan detection (logout detection, create alert)
- Action file creation with YAML frontmatter (priority: urgent)
- Test whatsapp_watcher detects urgent messages within 30 seconds

**Phase 9: User Story 6 - CEO Briefing** (12 tasks, T093-T104) - P2
- Create .claude/commands/ceo-briefing-generator.md skill
- Query Xero API (weekly revenue, invoices, payments)
- Scan /Done folder (completed tasks), /Logs (errors, warnings)
- Parse Business_Goals.md (targets, KPIs, projects)
- Generate briefing sections: Executive Summary, Weekly Revenue, Completed Tasks, Bottlenecks, Proactive Suggestions
- Subscription audit (flag unused subscriptions, cost increases)
- Scheduled task for Sunday 7 AM execution (cron/Task Scheduler)
- Test CEO briefing generation, test scheduled execution

**Phase 10: User Story 7 - Calendar Events** (8 tasks, T105-T112) - P3
- Create calendar_watcher.py with CalendarWatcher class extending BaseWatcher
- Google Calendar API authentication (OAuth 2.0)
- 10-minute check interval, detect events 1-48 hours ahead
- Event modification/cancellation detection
- Action file creation with YAML frontmatter (event_id, title, start_time, end_time, location, attendees)
- Preparation suggestions generation
- Test calendar_watcher detects events within 10 minutes

**Phase 11: User Story 8 - Slack Monitoring** (8 tasks, T113-T120) - P3
- Create slack_watcher.py with SlackWatcher class extending BaseWatcher
- Slack Web API authentication (bot token)
- 1-minute check interval, keyword matching (urgent, important, help, issue, problem)
- Thread consolidation (same keyword → single action file with thread context)
- Action file creation with YAML frontmatter (channel, sender, message, timestamp, thread_id)
- Test slack_watcher detects keyword matches within 1 minute

**Phase 12: User Story 9 - File System Drop Zone** (8 tasks, T121-T128) - P3
- Create filesystem_watcher.py with FilesystemWatcher class extending BaseWatcher
- Real-time file system monitoring (watchdog library, on_created event)
- File metadata extraction (filename, file_size, file_type, file_path)
- File type detection (PDF, DOCX, image → suggest appropriate actions)
- Action file creation with YAML frontmatter
- Processed file cleanup (move to /Inbox/Archive)
- Test filesystem_watcher detects files in real-time (<5 seconds)

**Phase 13: Cross-Domain Integration & Correlation** (6 tasks, T129-T134)
- Implement cross-domain event detection in task-processor skill
- Deduplication logic (same invoice ID, customer, timestamp → consolidate)
- Plan.md creation for correlated events
- Deduplication logging
- Test cross-domain correlation, test deduplication

**Phase 14: Polish & Cross-Cutting** (10 tasks, T135-T144)
- Create UPGRADE_GUIDE.md: Silver → Gold migration instructions
- Update README.md, Company_Handbook.md, Dashboard.md templates
- Create end-to-end integration test: tests/integration/test_gold_end_to_end.py
- Verify all 28 success criteria from spec.md (SC-001 to SC-028)
- Record demo video (10-15 minutes) showing full Gold Tier workflow
- Test orchestrator auto-start on boot
- Test 99%+ uptime over 7-day period
- Test peak load handling (100+ events per day)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (Bronze Tier must be complete first)
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T010) AND Silver Tier complete - BLOCKS all user stories
- **User Stories (Phases 3-13)**: All depend on Foundational phase completion (T011-T028)
  - US1 (Email): Can start after Foundational - No dependencies on other stories
  - US2 (Financial): Can start after Foundational - Independent (but recommended before US6)
  - US5 (Ralph Loop): Can start after Foundational - Independent (requires Silver approval workflow)
  - US10 (Audit Logging): Can start after Foundational - Independent (recommended early)
  - US3 (Social Media): Can start after Foundational - Independent (requires Gmail MCP from Silver)
  - US4 (WhatsApp): Can start after Foundational - Independent
  - US6 (CEO Briefing): Requires US2 (Xero) and US10 (audit logging) complete
  - US7 (Calendar): Can start after Foundational - Independent
  - US8 (Slack): Can start after Foundational - Independent
  - US9 (File System): Can start after Foundational - Independent

### Critical Path for MVP (P1 Stories - Functional Gold Tier Minimum)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T028) - BLOCKS ALL STORIES
3. Complete Phase 3: User Story 1 (T029-T036) - Email monitoring
4. Complete Phase 4: User Story 2 (T037-T046) - Financial detection
5. Complete Phase 5: User Story 5 (T047-T056) - Ralph loop
6. Complete Phase 6: User Story 10 (T057-T068) - Audit logging
7. STOP and VALIDATE: Test P1 stories independently
8. Deploy/demo - MVP DELIVERABLE (Email + Financial + Ralph + Audit)

### Recommended Full Gold Tier (All P1 + P2 Stories)

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Email) → Test independently
3. Add US2 (Financial) → Test independently
4. Add US5 (Ralph Loop) → Test independently
5. Add US10 (Audit Logging) → Test independently
6. Add US3 (Social Media) → Test independently
7. Add US4 (WhatsApp) → Test independently
8. Add US6 (CEO Briefing) → Test independently
9. Add US7 (Calendar) → Test independently
10. Add US8 (Slack) → Test independently
11. Add US9 (File System) → Test independently
12. Add Cross-Domain Integration → Test correlation
13. Complete Polish → End-to-end Gold Tier ready

---

## Parallel Examples

### Phase 2 - Foundational (Parallel Opportunities)

```bash
# Launch orchestrator and watchdog in parallel:
Task: "T012 Create watchers/orchestrator.py with MultiWatcherManager class"
Task: "T018 Create watchers/watchdog.py to monitor orchestrator.py process"
Task: "T022 Create watchers/orchestrator_cli.py with status, stop, restart commands"
Task: "T026 Create watchers/orchestrator_config.json with settings for all 6 watchers"
```

### Phase 7 - Social Media MCP Servers (Parallel Opportunities)

```bash
# Launch MCP server setup in parallel:
Task: "T069 Create mcp-servers/linkedin-mcp/package.json"
Task: "T072 Create mcp-servers/x-poster/package.json"
Task: "T075 Create mcp-servers/facebook-mcp/package.json"
Task: "T078 Create mcp-servers/instagram-mcp/package.json"
```

---

## Implementation Strategy

### MVP First (P1 Stories) - Functional Gold Tier Minimum

**Scope**: Email monitoring + Financial detection + Ralph loop + Audit logging (4 P1 stories)
**Time Estimate**: 20-25 hours
**Deliverable**: Autonomous email and financial monitoring with Ralph loop and complete audit trail

**Implementation Order**:
1. Setup → Foundational → US1 → US2 → US5 → US10 → Polish MVP

### Standard Gold Tier (P1 + P2 Stories) - Recommended

**Scope**: All P1 stories (US1, US2, US5, US10) + P2 stories (US3, US4, US6)
**Time Estimate**: 35-45 hours (aligns with Gold Tier estimate)

**Implementation Order**:
1. Setup → Foundational → US1 → US2 → US5 → US10 → US3 → US4 → US6 → Cross-Domain Integration → Polish

### Full Gold Tier (All Stories)

**Scope**: All 10 user stories (US1-US10) with comprehensive documentation and testing
**Time Estimate**: 40-50 hours

---

## Task Summary

- **Total Tasks**: 138 tasks organized across 14 phases
- **Setup**: 10 tasks
- **Foundational**: 18 tasks (BLOCKS all stories until complete)
- **User Story 1**: 8 tasks - Email monitoring
- **User Story 2**: 10 tasks - Financial event detection
- **User Story 5**: 10 tasks - Ralph Wiggum loop
- **User Story 10**: 12 tasks - Audit logging
- **User Story 3**: 14 tasks - Social media posting
- **User Story 4**: 10 tasks - WhatsApp urgent messages
- **User Story 6**: 12 tasks - CEO briefing
- **User Story 7**: 8 tasks - Calendar events
- **User Story 8**: 8 tasks - Slack monitoring
- **User Story 9**: 8 tasks - File system drop zone
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

**Tier Progression**: Bronze (000) → Silver (001) → **Gold (002)** → Platinum (003) validated. Gold tier builds incrementally on Silver and Bronze foundations with orchestrator + watchdog, 6 coordinated watchers, 6 MCP servers, Ralph Wiggum autonomous loop, CEO briefing, and comprehensive audit logging before Platinum Tier's cloud deployment.

---

**Next Steps**:
1. Review Gold Tier tasks.md file for approval
2. Verify Silver Tier (feature 001) is complete
3. Implement tasks following MVP (US1+US2+US5+US10) or Standard (all P1+P2 stories) path
4. Validate Gold Tier success criteria before proceeding to Platinum Tier
5. Run /sp.plan for Platinum Tier (feature 003) after Gold Tier validated

---

**File Created**: specs/002-gold-tier-ai-employee/tasks.md

**PHR**: To be created after reporting completion
