---
id: 001
title: Bronze Tier Foundation Specification
stage: spec
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: 000-bronze-tier-foundation
branch: 000-bronze-tier-foundation
user: Najma-LP
command: /sp.specify
labels: ["bronze-tier", "foundation", "mvp", "specification", "hackathon"]
links:
  spec: specs/000-bronze-tier-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/000-bronze-tier-foundation/spec.md
  - specs/000-bronze-tier-foundation/checklists/requirements.md
tests:
  - Specification quality checklist validation (PASSED)
---

## Prompt

for BronzE tier and keep it before Gold Tier

## Response snapshot

Created comprehensive Bronze Tier Foundation specification as feature 000 (before Gold Tier 001) following Spec-Driven Development workflow:

**Branch Created**: 000-bronze-tier-foundation (numbered to come before 001-gold-tier-ai-employee)

**Specification Generated**: specs/000-bronze-tier-foundation/spec.md (comprehensive foundation spec)

**Bronze Tier Scope - Minimum Viable Deliverable (8-12 hours)**:

**Key Components**:

1. **User Stories** (5 prioritized scenarios):
   - **P1**: Obsidian Vault Initialization (Dashboard.md + Company_Handbook.md)
   - **P1**: Single Watcher Implementation (Gmail OR File System - user choice)
   - **P1**: Claude Code Vault Integration (read/write capability)
   - **P2**: Basic Folder Workflow (/Inbox, /Needs_Action, /Done)
   - **P1**: Agent Skills Implementation (vault-setup, task-processor, dashboard-updater)

2. **Functional Requirements** (30 requirements):
   - FR-001 to FR-005: Obsidian Vault & Knowledge Base (Dashboard.md, Company_Handbook.md, folder structure)
   - FR-006 to FR-010: Watcher Layer (ONE watcher - Gmail OR File System, action file creation, logging)
   - FR-011 to FR-015: Claude Code Integration (read/write vault, parse action files, update Dashboard, move to /Done)
   - FR-016 to FR-020: File-Based Workflow (manual file movement, naming convention, processing metadata, chronological order)
   - FR-021 to FR-025: Agent Skills Architecture (SKILL.md files, vault-setup, task-processor, dashboard-updater skills)
   - FR-026 to FR-030: Error Handling & Logging (error logs, graceful degradation, rate limit handling, malformed file validation)

3. **Success Criteria** (20 measurable outcomes):
   - Core Functionality: Vault init <2 min, watcher runs 24 hours, 95% detection rate, 90% processing success, Dashboard updates <5 sec
   - User Experience: Verify watcher status, manual file drop processed <2 min, clear Dashboard summary, human-readable action files, setup <15 min
   - Quality: Handle 50 files/day, <5% error rate, comprehensive error logging, auto-recovery from transient failures, no data loss
   - Architecture: 100% functionality as Agent Skills, standardized action file format, timestamped watcher logs, sufficient Company_Handbook context, separation of concerns

4. **Key Entities**:
   - Action File (detected event payload)
   - Dashboard Entry (activity log line)
   - Skill Definition (reusable AI capability)
   - Watcher Process (background monitor)
   - Company Handbook (rules document)

5. **Additional Sections**:
   - 8 edge cases covering vault locks, crashes, rate limits, large file counts, malformed files, concurrent writes, large logs
   - Comprehensive assumptions across environment (Obsidian 1.10.6+, Python 3.13+, Claude Code subscription), accounts (Gmail API if chosen), data (small action files, manual archiving), operations (work hours testing, manual start), technical (atomic file moves, local disk, token budget), scope (single-user, no encryption, manual checks)
   - Dependencies on Gmail API (if chosen), Claude API, Obsidian, Python packages (google-auth, watchdog, pyyaml)
   - Out of scope: Multiple watchers, MCP servers, approval workflow, scheduling, Plan.md, cross-domain integration, accounting, social media, Ralph loop, orchestrator, audit logging, CEO briefing (all Silver/Gold tier)
   - 9 risks with severity ratings and mitigation strategies (Gmail quota, vault corruption, OAuth expiration, crashes, token exhaustion, naming collisions, unbounded logs, disk space, CPU usage)
   - Implementation notes with Bronze completion checklist, recommended 5-phase order (Vault Setup → Watcher → Claude Integration → Skills → Testing), key technical decisions, architecture validation principles

**Requirements Checklist**: specs/000-bronze-tier-foundation/checklists/requirements.md (PASSED)
- All quality criteria met
- No [NEEDS CLARIFICATION] markers
- Technology-agnostic success criteria
- Ready for /sp.plan phase

**Bronze Before Gold**: Feature numbered as 000 to ensure Bronze Tier comes before Gold Tier (001) in the implementation sequence, as Bronze validates the core architecture that Gold depends on.

## Outcome

- ✅ Impact: Comprehensive Bronze Tier Foundation specification created with 5 user stories, 30 functional requirements, 20 success criteria. Minimum viable deliverable (8-12 hours) focusing on proving core architecture: Obsidian vault setup, ONE watcher (Gmail OR File System), Claude Code integration, file-based workflow, Agent Skills. Numbered as 000 to come before Gold Tier 001.
- 🧪 Tests: Specification quality checklist validation passed - all content quality, requirement completeness, and feature readiness criteria met. No [NEEDS CLARIFICATION] markers. Architecture validation principles clearly stated: must prove Perception → Memory → Reasoning → Action pipeline works.
- 📁 Files: Created specs/000-bronze-tier-foundation/spec.md (comprehensive foundation spec), specs/000-bronze-tier-foundation/checklists/requirements.md. Branch 000-bronze-tier-foundation created and checked out.
- 🔁 Next prompts: `/sp.plan` (ready for Bronze Tier architectural planning), then implement and validate Bronze before proceeding to Silver, then Gold Tier (001)
- 🧠 Reflection: Bronze Tier specification successfully scoped as foundation/MVP that proves viability before adding complexity. Key decisions: ONE watcher (user choice), no MCP servers yet, no approval workflow yet, all deferred to Silver/Gold. Focus on proving file-based automation works. Implementation notes include recommended phase order and completion checklist. Critical insight: Bronze must validate core principles or Silver/Gold will compound problems.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification created successfully with proper numbering (000) to come before Gold Tier (001). Branch creation and directory structure worked correctly.
- Graders run and results (PASS/FAIL): Specification Quality Checklist - PASSED (14/14 validation items), Content Quality - PASSED (4/4), Requirement Completeness - PASSED (8/8), Feature Readiness - PASSED (4/4). Bronze scope properly differentiated from Silver/Gold.
- Prompt variant (if applicable): Standard /sp.specify workflow with user input: "for BronzE tier and keep it before Gold Tier". Successfully interpreted user intent to create Bronze Tier spec numbered before existing Gold Tier (001).
- Next experiment (smallest change to try): For future tier specifications (Silver), consider adding explicit "Upgrade Path" section showing how to incrementally add features on top of Bronze foundation. Current approach has clear out-of-scope items but could benefit from explicit "adds X on top of Bronze" language to emphasize incremental approach.
