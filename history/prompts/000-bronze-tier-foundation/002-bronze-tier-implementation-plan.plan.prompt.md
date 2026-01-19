---
id: 002
title: Bronze Tier Implementation Plan
stage: plan
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: 000-bronze-tier-foundation
branch: 000-bronze-tier-foundation
user: Najma-LP
command: /sp.plan
labels: ["bronze-tier", "plan", "architecture", "implementation", "hackathon"]
links:
  spec: specs/000-bronze-tier-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/000-bronze-tier-foundation/plan.md
  - specs/000-bronze-tier-foundation/research.md
  - specs/000-bronze-tier-foundation/data-model.md
  - specs/000-bronze-tier-foundation/quickstart.md
  - specs/000-bronze-tier-foundation/contracts/action-file-schema.yaml
  - specs/000-bronze-tier-foundation/contracts/dashboard-format.yaml
  - specs/000-bronze-tier-foundation/contracts/watcher-config-schema.yaml
tests:
  - Phase 0: Research decisions documented for all unknowns
  - Phase 1: Data model defined with validation rules
  - Phase 1: Contracts created for action files, Dashboard, watcher config
  - Phase 1: Quickstart guide written with setup and troubleshooting
---

## Prompt

for Bronze Teir

## Response snapshot

Created comprehensive Bronze Tier implementation plan with Phase 0 (research) and Phase 1 (design) artifacts complete:

**Implementation Plan**: specs/000-bronze-tier-foundation/plan.md

**Key Architectural Decisions**:

1. **File-Based State Management**: No database - all state in file system (action files, logs, Dashboard.md). Validates Bronze tier assumption that file-based approach scales to 50 files/day.

2. **Pull-Based Processing**: Watcher creates action files, user invokes Claude Code to process (manual for Bronze). Push-based orchestrator deferred to Gold tier.

3. **Agent Skills Architecture**: All Claude Code functionality as SKILL.md files (vault-setup, task-processor, dashboard-updater). Provides structure, documentation, reusability per hackathon rules.

4. **Local-First Philosophy**: Obsidian vault on local disk, watchers run locally. Only external dependencies: Gmail API (optional), Claude API (required). User maintains data sovereignty.

5. **Manual Scaling**: No auto-rotation/archiving/restart. User manually manages system health. Appropriate for Bronze tier learning phase.

**Technology Stack**:
- **Watcher Scripts**: Python 3.13+ (gmail API, watchdog library)
- **Memory/GUI**: Obsidian (local-first, markdown-native)
- **Reasoning Engine**: Claude Code (Agent Skills architecture)
- **Action File Format**: Markdown + YAML frontmatter (human-readable, git-friendly)
- **Configuration**: YAML (watcher_config.yaml)

**Phase 0: Research** (research.md):
- **8 research decisions** documented with rationale, alternatives, implementation guidance
- Gmail vs File System: Recommend File System for beginners (zero setup friction), Gmail for users comfortable with OAuth
- Action file format: Markdown + YAML frontmatter (human-readable, Obsidian-native, supports rich content)
- Dashboard update: Append-only (simpler, faster, preserves history)
- Error recovery: Log and continue for transient errors, crash on critical failures
- Claude invocation: Manual for Bronze (no orchestrator), automated in Gold tier
- Dependencies: Standard venv + requirements.txt (universal compatibility)
- Vault structure: Flat folders at root (simple navigation, easy file movement)
- Check intervals: Conservative - File System 30 sec, Gmail 2-5 min (quota-safe)

**Phase 1: Design Artifacts**:

1. **data-model.md**: Complete entity definitions
   - Action File (markdown with YAML frontmatter)
   - Dashboard Entry (activity log line format)
   - Watcher Process (in-memory state + logs)
   - Skill Definition (SKILL.md format)
   - Company Handbook (business rules document)
   - Validation rules for each entity
   - Storage estimates: 25 MB/month for 50 files/day

2. **contracts/action-file-schema.yaml**: YAML frontmatter structure
   - Type: email | file | scheduled
   - Source: Gmail | FileSystem | Manual
   - Payload schemas for each event type
   - Processing metadata added by task-processor
   - File naming convention: {SOURCE}_{TIMESTAMP}_{IDENTIFIER}.md
   - Validation rules

3. **contracts/dashboard-format.yaml**: Dashboard.md structure
   - YAML frontmatter (last_updated, vault_version)
   - Current Status section (watcher status, pending tasks, completed today, error rate)
   - Activity Log section (chronological entries, newest first)
   - Task Summary table (last 24 hours by type)
   - Update protocol (append-only for activity log)
   - Archiving protocol (manual at 1000 entries)

4. **contracts/watcher-config-schema.yaml**: Configuration format
   - Gmail watcher config (check_interval, labels, credentials, scopes)
   - File system watcher config (watched_path, file_filters, settle_time)
   - Logging config (log_level, log_path, format)
   - Validation rules (exactly ONE watcher enabled)
   - Gmail quota analysis (recommended intervals)
   - Bronze tier recommendations

5. **quickstart.md**: Setup and testing guide
   - Prerequisites (Obsidian, Python 3.13+, Claude Code)
   - Phase 1: Environment setup (10 min)
   - Phase 2: Obsidian vault setup (5 min)
   - Phase 3: Watcher selection & setup (15-20 min)
   - Phase 4: Install dependencies (5 min)
   - Phase 5: Initial testing (10 min)
   - Phase 6: Claude Code integration (5 min)
   - Daily operation workflow
   - Troubleshooting guide (5 common issues)
   - Bronze tier completion checklist

**Project Structure**:
```
watchers/
  ├── base_watcher.py
  ├── gmail_watcher.py (option 1)
  ├── filesystem_watcher.py (option 2)
  ├── watcher_config.yaml
  └── requirements.txt

.claude/commands/
  ├── vault-setup.md
  ├── task-processor.md
  └── dashboard-updater.md

[Vault Root]/
  ├── Dashboard.md
  ├── Company_Handbook.md
  ├── Inbox/ (file system watcher monitored directory)
  ├── Needs_Action/ (action file queue)
  ├── Done/ (archive)
  ├── Errors/ (malformed files)
  └── Logs/ (watcher logs, error logs)

tests/
  ├── test_action_file_format.py
  ├── test_watcher_gmail.py
  ├── test_watcher_filesystem.py
  └── integration/test_end_to_end.py
```

**Implementation Sequence** (8-12 hours):
1. Phase 1 - Vault Setup (2 hours): vault-setup skill, Dashboard/Handbook templates, folder structure
2. Phase 2 - Watcher Script (3-4 hours): base_watcher.py, chosen implementation, action file creation, logging
3. Phase 3 - Claude Integration (2-3 hours): task-processor skill, Dashboard update, file movement
4. Phase 4 - Additional Skills (2 hours): dashboard-updater skill, documentation
5. Phase 5 - Testing & Documentation (1-2 hours): end-to-end test, validate success criteria, demo video

**Architecture Validation Principles**:
1. Perception → Memory → Reasoning → Action pipeline works end-to-end
2. File-based state management viable for AI automation (50 files/day)
3. Claude Code reliably parses and updates Obsidian markdown (90% success)
4. Watcher pattern enables autonomous triggering (not reactive chat)
5. Agent Skills provide reusable structure

**Risk Mitigation** (from spec.md):
- High severity: OAuth token expiration (auto-refresh), Gmail quota (conservative interval), vault corruption (file locking)
- Medium severity: Watcher crashes (comprehensive logging), token budget (cost monitoring)
- Low severity: Unbounded Dashboard growth (manual archiving at 1000 entries)

**Success Criteria Mapping**:
- SC-001: Vault init <2 min → vault-setup skill uses templates
- SC-002: Watcher runs 24 hours → robust error handling, retry logic
- SC-003: 95% detection accuracy → test with 20 events, verify 19+ action files
- SC-004: 90% processing success → test with 20 action files, verify 18+ moved to /Done
- SC-016: 100% functionality as Agent Skills → vault-setup, task-processor, dashboard-updater implemented

## Outcome

- ✅ Impact: Comprehensive Bronze Tier implementation plan created with Phase 0 (research) and Phase 1 (design) artifacts complete. 8 research decisions documented with rationale, data model defined for 5 key entities, 3 contract schemas created (action-file, dashboard, watcher-config), quickstart guide with 6 setup phases and troubleshooting. Ready for /sp.tasks command to generate detailed task breakdown.
- 🧪 Tests: Constitution check PASSED (simplicity, local-first, testability, observability, human-in-the-loop principles validated). Data model validation rules defined. Contract schemas include validation rules. Architecture validation principles clearly stated (5 principles to prove in Bronze tier).
- 📁 Files: Created plan.md (comprehensive architecture), research.md (8 technology decisions), data-model.md (5 entities with validation), quickstart.md (setup guide), contracts/action-file-schema.yaml, contracts/dashboard-format.yaml, contracts/watcher-config-schema.yaml
- 🔁 Next prompts: `/sp.tasks` (generate detailed task breakdown from plan), then implement following 5-phase sequence, validate Bronze tier success criteria, record demo video
- 🧠 Reflection: Bronze Tier plan successfully balances simplicity (ONE watcher, no MCP, no approval, manual processing) with completeness (all Agent Skills, file-based workflow, comprehensive logging). Key insight: Bronze must prove file-based architecture viability before adding Silver/Gold complexity. Research phase identified critical trade-offs (Gmail vs FileSystem, append vs replace, manual vs automated) with clear recommendations. Quickstart guide provides fast path to working system (45 min setup, 8-12 hour implementation). Architecture continuity: Bronze validates core pipeline → Silver adds watchers/MCP → Gold adds orchestration/audit.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan creation successful. Phase 0 and Phase 1 artifacts generated without issues. Constitution template was empty but applied general best practices for Bronze tier foundation.
- Graders run and results (PASS/FAIL): Constitution Check - PASSED (simplicity, local-first, testability, observability, human-in-the-loop principles). Research decisions - COMPLETE (8/8 questions resolved with rationale). Data model - COMPLETE (5 entities defined with validation rules). Contracts - COMPLETE (3 schemas with validation rules). Quickstart - COMPLETE (6 phases with troubleshooting).
- Prompt variant (if applicable): Standard /sp.plan workflow with user input: "for Bronze Teir" (typo preserved from user). Successfully interpreted intent to create implementation plan for Bronze Tier (feature 000) following Phase 0 research + Phase 1 design workflow.
- Next experiment (smallest change to try): For future plans, consider adding "Implementation Example" section showing code snippets for critical components (e.g., action file creation in watcher, Dashboard update in task-processor). Current approach has comprehensive schemas but concrete code examples could accelerate implementation. Alternative: Create "reference-implementations/" directory in specs/ with minimal working examples for each component.
