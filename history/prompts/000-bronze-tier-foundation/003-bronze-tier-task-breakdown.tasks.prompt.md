---
id: 003
title: Bronze Tier Task Breakdown
stage: tasks
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: 000-bronze-tier-foundation
branch: 000-bronze-tier-foundation
user: Najma-LP
command: /sp.tasks
labels: ["bronze-tier", "tasks", "implementation", "breakdown", "user-stories"]
links:
  spec: specs/000-bronze-tier-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/000-bronze-tier-foundation/tasks.md
tests:
  - Manual integration testing focus per quickstart.md
  - End-to-end validation test in tests/integration/test_end_to_end.py
---

## Prompt

for bronze tier

## Response snapshot

Created comprehensive Bronze Tier task breakdown organized by user stories for independent implementation and testing:

**Tasks File**: specs/000-bronze-tier-foundation/tasks.md

**Task Organization**: 94 tasks organized across 8 phases following user story structure from spec.md

**Phase Breakdown**:

**Phase 1: Setup** (10 tasks, T001-T010)
- Create directory structure: watchers/, .claude/commands/, tests/, docs/, vault/
- Create requirements.txt with common dependencies (pyyaml, python-frontmatter, watchdog)
- Create Gmail dependencies (google-auth, google-api-python-client) for Gmail watcher option
- Create .env.example template for Gmail credentials
- Create watcher_config.yaml template with both watchers disabled by default
- Create setup documentation structure

**Phase 2: Foundational** (11 tasks, T011-T021) - BLOCKS all user stories
- Logging infrastructure: watcher_logger.py with configure_logging(), file rotation support
- Action file format: action_file.py with create_action_file(), YAML frontmatter schema
- Configuration management: config.py with load_config(), validation for vault_path, check intervals, exactly-one-watcher rule

**Phase 3: User Story 1 - Obsidian Vault Initialization** (8 tasks, T022-T029) - P1, 🎯 MVP
- Create vault folder structure (/Inbox, /Needs_Action, /Done, /Errors, /Logs)
- Create Dashboard.md template with YAML frontmatter and sections
- Create Company_Handbook.md template with business rules sections
- Implement vault-setup Agent Skill (.claude/commands/vault-setup.md)
- Test vault-setup skill invocation
- **Independent Test**: Open Obsidian, verify folders exist, verify Dashboard/Handbook structure
- **MVP Scope**: Complete US1 for minimum Bronze Tier (vault structure only, ~4 hours)

**Phase 4: User Story 2 - Single Watcher Implementation** (24 tasks, T030-T053) - P1
- Base Watcher class (T030-T034): abstract class with check_interval loop, logging, error handling, action file creation
- File System Watcher option (T035-T043): watchdog library, file filtering, ignore patterns, file size validation, settle_time logic
- Gmail Watcher option (T044-T053): OAuth 2.0 authentication, token refresh, Gmail API calls, exponential backoff
- **Note**: Implement ONE watcher for Bronze Tier, not both
- **Independent Test**: Run watcher, trigger event, verify action file created with correct metadata

**Phase 5: User Story 3 - Claude Code Vault Integration** (15 tasks, T054-T068) - P1
- Action file parsing: read files, validate frontmatter, chronological sorting, batch processing
- Dashboard updates: append activity log entries, refresh Current Status section, calculate error rate
- File movement: move_to_done() with processing metadata, move_to_errors() for malformed files
- Task Processor skill: .claude/commands/task-processor.md with error handling and processing loop
- **Independent Test**: Claude Code reads vault, writes to Dashboard, parses action files, moves files to /Done

**Phase 6: User Story 4 - Basic Folder Workflow** (6 tasks, T069-T074) - P2
- Document folder workflow: /Inbox → Watcher → /Needs_Action → task-processor → /Done
- Add /Errors folder handling for malformed files
- Implement visual status indicators in Dashboard (✅, ❌, ⏸️)
- Document manual intervention options
- Add troubleshooting documentation
- **Independent Test**: Drop file in /Inbox, verify workflow through all folders

**Phase 7: User Story 5 - Agent Skills Implementation** (10 tasks, T075-T084) - P1
- Enhance vault-setup skill (created in US1)
- Enhance task-processor skill (created in US3)
- Create dashboard-updater skill: refresh status, calculate task summary, update table
- Add comprehensive documentation for each skill (name, description, inputs, outputs, examples)
- **Independent Test**: Invoke each skill, verify expected outputs

**Phase 8: Polish & Cross-Cutting Concerns** (10 tasks, T085-T094)
- Create comprehensive documentation: SETUP.md, TROUBLESHOOTING.md, ARCHITECTURE.md
- Update README.md with Bronze Tier status and setup instructions
- Add end-to-end integration test
- Implement graceful shutdown, file locking for Dashboard.md
- Add log rotation guidance
- Validate all Bronze tier success criteria from spec.md
- Record demo video (5-10 minutes)

**Dependencies**:
- Setup (Phase 1) → Foundational (Phase 2) → All User Stories can start
- US1 has no dependencies on other user stories (MVP candidate)
- US2 is independent (can implement File System OR Gmail watcher)
- US3 depends on US1 (needs vault structure)
- US4 depends on US2 and US3 (integration story)
- US5 depends on US1 and US3 (vault-setup and task-processor)

**Parallel Opportunities**: 30+ tasks marked [P] can run in parallel within phases

**Implementation Strategies**:

1. **MVP First (US1 only)**: 29 tasks, ~4 hours - Vault structure ready
2. **Standard Bronze Tier (US1, US2, US3, US5)**: 78 tasks, ~10-13 hours - Complete pipeline
3. **Full Bronze Tier (US1-5)**: 84 tasks, ~12-16 hours - All Bronze Tier features

**Task Format Compliance**: All 94 tasks follow strict checklist format:
- Checkbox: `- [ ]`
- Task ID: Sequential (T001-T094)
- [P] marker: For parallelizable tasks
- [Story] label: [US1], [US2], [US3], [US4], [US5] for user story phases
- Description: Clear action with exact file path

## Outcome

- ✅ Impact: Comprehensive Bronze Tier task breakdown created with 94 tasks organized by user story for independent implementation and testing. Clear MVP path (US1 only, 29 tasks, ~4 hours), standard Bronze Tier path (US1,2,3,5, 78 tasks, ~10-13 hours), and full Bronze Tier path (US1-5, 84 tasks, ~12-16 hours). Each user story independently testable with checkpoint validation. 30+ parallel opportunities identified. Task format validated: all tasks follow checklist format with checkbox, ID, [P] marker, [Story] label, file paths.
- 🧪 Tests: Manual integration testing focus per quickstart.md. End-to-end test task T089 in tests/integration/test_end_to_end.py. No automated unit tests required for Bronze tier (manual testing appropriate for MVP). Success criteria validation tasks T093: validate all Bronze tier success criteria from spec.md (vault init <2 min, watcher runs 24 hours, 95% detection, 90% processing, Dashboard <5 sec).
- 📁 Files: Created specs/000-bronze-tier-foundation/tasks.md with 8 phases, 94 tasks, dependency graph, parallel examples, implementation strategies (MVP, Standard, Full), task summary by phase.
- 🔁 Next prompts: Implement tasks following MVP (US1) or Standard Bronze (US1,2,3,5) or Full Bronze (US1-5) path. Start with Phase 1 Setup (T001-T010), then Phase 2 Foundational (T011-T021), then user stories in priority order (P1 → P2). Validate at each checkpoint. Record demo video after Polish phase.
- 🧠 Reflection: Task breakdown successfully maps all functional requirements (FR-001 to FR-030) to implementation tasks organized by user story. Each user story independently testable with clear checkpoint validation. Bronze Tier scope appropriate: 94 tasks is manageable for 8-12 hour hackathon (with focused effort). MVP path (US1 only, 29 tasks, 4 hours) enables quick vault structure demo. Standard path (US1,2,3,5, 78 tasks, 10-13 hours) delivers complete Bronze Tier with all P1 stories. US4 (P2) is nice-to-have workflow enhancement, not required for core functionality. Task format compliance ensures each task is immediately executable with clear file paths and acceptance criteria.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation successful. All design documents (plan.md, spec.md, research.md, data-model.md, contracts/) loaded and mapped to tasks. Task format validated against template requirements.
- Graders run and results (PASS/FAIL): Format Validation - PASSED (all 94 tasks follow checklist format with checkbox, ID, [P] marker, [Story] label, file paths). User Story Mapping - PASSED (all 5 user stories from spec.md have tasks, each story independently testable). Dependency Analysis - PASSED (clear phase dependencies, US1 has no dependencies, US3 depends on US1, US4 depends on US2+US3). Scope Validation - PASSED (94 tasks for 8-12 hour Bronze Tier is appropriate, MVP path clearly defined).
- Prompt variant (if applicable): Standard /sp.tasks workflow with user input: "for bronze tier". Successfully interpreted intent to generate task breakdown for Bronze Tier (feature 000) following task generation rules (organize by user story, checklist format, file paths, parallel opportunities).
- Next experiment (smallest change to try): For future task breakdowns, consider adding "Estimated Time per Task" field to help with timeboxing and sprint planning. Current approach has phase-level time estimates but not task-level estimates. Could add: "Est: 15 min" or "Est: 30 min" to each task. Alternative: Keep current approach (phase-level estimates) as task-level estimates are highly variable based on developer experience.
