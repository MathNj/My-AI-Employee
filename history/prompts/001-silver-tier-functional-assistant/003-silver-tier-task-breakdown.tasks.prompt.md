---
id: 003
title: Silver Tier Task Breakdown
stage: tasks
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: 001-silver-tier-functional-assistant
branch: 001-silver-tier-functional-assistant
user: Najma-LP
command: /sp.tasks
labels: ["silver-tier", "tasks", "implementation", "breakdown", "multi-watcher"]
links:
  spec: specs/001-silver-tier-functional-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-silver-tier-functional-assistant/tasks.md
tests:
  - Manual integration testing focus per plan.md (Phase 0 research complete, Phase 1 design complete)
  - End-to-end test in tests/integration/test_silver_end_to_end.py (Phase 9)
---

## Prompt

for Silver Tire

## Response snapshot

Created comprehensive Silver Tier task breakdown with 104 tasks organized across 9 phases following user story structure from spec.md:

**Tasks File**: specs/001-silver-tier-functional-assistant/tasks.md

**Task Organization**: 104 tasks across 9 phases following Bronze Tier (feature 000) prerequisite

**Phase Breakdown**:

**Phase 1: Setup** (10 tasks, T001-T010)
- Verify Bronze Tier completion, upgrade RAM to 16GB if needed
- Install Node.js v24+, install Python dependencies (psutil, schedule), install Playwright
- Create MCP directory, create /Scheduled, /Pending_Approval, /Approved, /Rejected, /Plans folders
- Create watchers_state.json for deduplication tracking

**Phase 2: Foundational** (18 tasks, T011-T028) - BLOCKS all Silver user stories
- Multi-watcher orchestrator (5 tasks): launch, stop, monitor, health check basics
- Deduplication system (4 tasks): check_duplicate, register_event, rotate_state, logging
- Health monitoring (4 tasks): PID check, log freshness, CPU usage check, health logging
- Extended configuration (4 tasks): multi-watcher config, health_monitor config, scheduled config template

**Phase 3: User Story 1 - Multi-Watcher Orchestration** (8 tasks, T029-T036) - P1
- Add WhatsApp watcher or second File System watcher
- Test deduplication: trigger same event across watchers, verify single action file
- Update Dashboard for multi-watcher status table
- Test concurrent execution: run 1 hour, verify CPU <30%, no crashes

**Phase 4: User Story 5 - Approval Workflow** (9 tasks, T037-T045) - P1
- **CRITICAL**: Approval workflow prerequisite for LinkedIn posting (US2) and MCP email actions (US4)
- Extend task-processor to check /Pending_Approval before executing sensitive actions
- Define sensitive actions: email send, LinkedIn post, financial >$100, data deletion
- Create approval_request.md template with risk_level, deadline, potential_impact
- Implement /Approved → /Rejected → /Done file movement
- Add deadline monitoring and overdue notifications
- Test approval workflow with email requiring approval

**Phase 5: User Story 4 - MCP Server Integration** (11 tasks, T046-T056) - P1
- Create Gmail send MCP server (recommended - builds on Bronze Gmail API)
- Implement MCP server with TypeScript/Node.js, @modelcontextprotocol/sdk-python
- Define send_email tool: to, subject, body, attachments → success, message_id, error
- Add Gmail API integration, error handling, logging to /Logs/mcp_actions_*.json
- Test MCP server: invoke send_email, verify email sent, check log
- Extend task-processor to invoke MCP actions, add action queue with retry logic

**Phase 6: User Story 2 - LinkedIn Social Media Posting** (11 tasks, T057-T067) - P1
- Create linkedin-poster skill with Playwright browser automation (LinkedIn API restricted)
- Implement LinkedIn authentication, post creation, post validation, engagement tracking
- Integrate with approval workflow (all posts require approval)
- Log LinkedIn posts to Company_Handbook social media inventory
- Implement rate limiting handling: exponential backoff, respect 429, queue posts for retry
- Test: Create test post, approve, publish, verify on LinkedIn, check metrics

**Phase 7: User Story 3 - Plan.md Reasoning Loop** (12 tasks, T068-T079) - P1
- Create plan-generator skill with Plan.md template (objective, steps, reasoning, alternatives, rationale)
- Implement complex task detection: 3+ steps OR >15 min threshold
- Create /Plans/active/ and /Plans/archive/ folder structure
- Implement plan approval workflow (file movement to /Approved)
- Add execution tracking: mark steps complete, log actual_time vs estimated_time
- Add deviation detection: if >20% deviation, create addendum Plan.md, notify human
- Test: Process complex task, verify plan created, approve, verify execution tracked

**Phase 8: User Story 6 - Scheduled Automation** (13 tasks, T080-T092) - P2
- Create scheduled-runner skill and /Scheduled/config.yaml configuration schema
- Define scheduled task schema: task_name, schedule (cron or Task Scheduler), skill_to_invoke, parameters
- Implement daily briefing task (8 AM daily): invoke /dashboard-updater skill
- Implement weekly audit task (Sunday 10 AM weekly): invoke audit skill or task-processor
- Implement monthly cleanup task (1st of month 2 AM): invoke cleanup skill
- Configure cron (Linux/macOS) or Task Scheduler (Windows) to run scheduled tasks
- Add scheduled task logging to /Logs/scheduled_tasks_YYYY-MM-DD.log
- Test: Schedule test task 1 minute in future, verify execution, check logs

**Phase 9: Polish & Cross-Cutting** (12 tasks, T093-T104)
- Create UPGRADE_GUIDE.md: Bronze → Silver migration instructions
- Update README.md, SETUP.md, TROUBLESHOOTING.md, ARCHITECTURE.md with Silver Tier content
- Extend Dashboard.md and Company_Handbook.md templates with Silver sections
- Update watchers/requirements.txt with Silver dependencies
- Create end-to-end integration test: tests/integration/test_silver_end_to_end.py
- Verify all 28 success criteria from spec.md (SC-001 to SC-028)
- Record demo video (5-10 minutes) showing full Silver Tier workflow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (Bronze Tier must be complete first)
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T010) AND Bronze Tier complete - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion (T011-T028)
  - US1 (Multi-Watcher): Can start after Foundational - No dependencies on other stories
  - US5 (Approval): Can start after Foundational - Independent (but required for US2, US4)
  - US4 (MCP Server): Can start after Foundational - Independent (recommended before US2 for Gmail send)
  - US2 (LinkedIn): Depends on US5 (approval workflow) and US4 (MCP for LinkedIn if using MCP)
  - US3 (Plan.md): Can start after Foundational - Independent of all other stories
  - US6 (Scheduled): Can start after Foundational - Independent of all other stories

### Critical Path for MVP (Multi-Watcher + Approval - Functional Silver Tier Minimum)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T028) - **BLOCKS ALL STORIES**
3. Complete Phase 3: User Story 1 (T029-T036) - 2+ watchers coordinated
4. Complete Phase 4: User Story 5 (T037-T045) - approval workflow working
5. **STOP and VALIDATE**: Test multi-watcher + approval independently (no MCP, no LinkedIn, no Plan.md, no scheduling yet)
6. Deploy/demo if ready - **MVP DELIVERABLE** (2+ watchers with safe automation)

### Recommended Full Silver Tier (All P1 Stories)

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Multi-Watcher) → Test independently → 2+ watchers coordinated
3. Add US5 (Approval) → Test independently → Safe automation established
4. Add US4 (MCP Server) → Test independently → External actions enabled
5. Add US2 (LinkedIn) → Test independently → Social media automated
6. Add US3 (Plan.md) → Test independently → Transparent planning for complex tasks
7. Add US6 (Scheduled) → Test independently → Scheduled automation active
8. Complete Polish → End-to-end Silver Tier functional assistant ready

---

## Parallel Examples

### Phase 2 - Foundational (Parallel Opportunities)

```bash
# Launch orchestrator and deduplication in parallel:
Task: "T011 Create watchers/orchestrator.py with MultiWatcherManager class"
Task: "T016 Implement check_duplicate() function in orchestrator.py"
Task: "T022 Implement log freshness check in health_monitor.py"
Task: "T025 Update watchers/watcher_config.yaml to support multiple watchers"
```

### Phase 5 - MCP Server Integration (Parallel Opportunities)

```bash
# Launch MCP server setup in parallel:
Task: "T046 Create mcp/gmail-send-server/package.json with dependencies"
Task: "T047 Implement mcp/gmail-send-server/src/index.ts with MCP server initialization"
Task: "T048 Define send_email tool in MCP server"
Task: "T049 Implement Gmail API integration in MCP server"
Task: "T050 Add error handling for MCP server"
```

---

## Implementation Strategy

### MVP First (Multi-Watcher + Approval) - Functional Silver Tier Minimum

**Scope**: Multi-watcher orchestration (2+ watchers) + Approval workflow + MCP server (Gmail send)
**Time Estimate**: 12-15 hours (Setup + Foundational + US1 + US5 + US4)
**Deliverable**: 2+ watchers coordinated, safe automation via approval, external email actions enabled

**Implementation Order**:
1. Setup → Foundational → US1 (Multi-Watcher) → US5 (Approval) → US4 (MCP Gmail) → Polish

### Standard Silver Tier (All P1 Stories) - Recommended

**Scope**: All P1 stories (US1, US2, US5, US4, US3) + US6 (P2)
**Time Estimate**: 20-30 hours (aligns with Silver Tier estimate)

**Implementation Order**:
1. Setup → Foundational → US1 → US5 → US4 → US2 → US3 → US6 → Polish

### Full Silver Tier (All Stories)

**Scope**: All 6 user stories (US1-US6) with comprehensive documentation and testing
**Time Estimate**: 20-30 hours

---

## Task Summary

- **Total Tasks**: 104 tasks organized across 9 phases
- **Setup**: 10 tasks
- **Foundational**: 18 tasks (BLOCKS all stories until complete)
- **User Story 1**: 8 tasks - Multi-watcher orchestration
- **User Story 5**: 9 tasks - Approval workflow
- **User Story 4**: 11 tasks - MCP server integration
- **User Story 2**: 11 tasks - LinkedIn posting
- **User Story 3**: 12 tasks - Plan.md reasoning
- **User Story 6**: 13 tasks - Scheduled automation
- **Polish**: 12 tasks

**Parallel Opportunities**: 35+ tasks marked [P] can run in parallel

**Format Validation**: ✅ All 104 tasks follow checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T104 (sequential)
- [P] marker: For parallelizable tasks
- [Story] label: [US1], [US2], [US3], [US4], [US5], [US6] for user story phases

**Prerequisite**: Bronze Tier (feature 000) must be complete before starting Silver Tier implementation

---

**Tasks Complete**: Silver Tier task breakdown with complete dependency graph, parallel opportunities, and implementation strategies. Ready for execution following recommended phase order: Setup → Foundational → User Stories (US1 → US5 → US4 → US2 → US3) → Polish.

**Tier Progression**: Bronze (000) → Silver (001) → Gold (002) validated. Silver tier builds incrementally on Bronze foundation with multi-watcher coordination, safe automation via approval, external actions via MCP, transparent planning, and scheduled reliability before Gold Tier's full autonomous employee.

---

**Next Steps**:
1. Review Silver Tier tasks.md file for approval
2. Verify Bronze Tier (feature 000) is complete
3. Implement tasks following MVP (US1+US5+US4) or Standard (all P1 stories) path
4. Validate Silver Tier success criteria before proceeding to Gold Tier
5. Run /sp.plan for Gold Tier (feature 002) after Silver Tier validated

---

**File Created**: specs/001-silver-tier-functional-assistant/tasks.md

**PHR**: To be created after reporting completion
