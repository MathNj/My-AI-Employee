# Feature Specification: Bronze Tier Foundation - Personal AI Employee

**Feature Branch**: `000-bronze-tier-foundation`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "for BronzE tier and keep it before Gold Tier"
**Tier**: Bronze (Foundation - Minimum Viable Deliverable)
**Estimated Time**: 8-12 hours

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obsidian Vault Initialization (Priority: P1)

As a hackathon participant, I want to initialize an Obsidian vault with Dashboard.md and Company_Handbook.md so that I have a functional local-first knowledge base and GUI for my AI Employee to work with.

**Why this priority**: Foundation requirement - without the Obsidian vault structure, no other functionality can work. This is the "memory layer" that enables all AI Employee operations.

**Independent Test**: Can be fully tested by opening Obsidian, creating the vault, and verifying Dashboard.md and Company_Handbook.md exist with proper structure. Delivers immediate value as a personal knowledge base even before AI integration.

**Acceptance Scenarios**:

1. **Given** I have Obsidian installed, **When** I initialize the vault structure, **Then** I should see Dashboard.md with activity log section, current status, and task summary placeholders
2. **Given** the vault is initialized, **When** I open Company_Handbook.md, **Then** I should see sections for business rules, decision-making guidelines, and approval thresholds that Claude Code can reference
3. **Given** the vault structure exists, **When** I create the basic folder structure, **Then** I should see /Inbox, /Needs_Action, and /Done folders ready for file-based workflow

---

### User Story 2 - Single Watcher Implementation (Priority: P1)

As a user, I want one working Watcher script (Gmail OR file system monitoring) that detects events and creates action files in /Needs_Action, so that my AI Employee can be triggered automatically without me typing prompts.

**Why this priority**: Core perception layer requirement - demonstrates the fundamental "Watcher → Action File → Claude Processing" pipeline that differentiates this from a chatbot.

**Independent Test**: Can be fully tested by running the watcher script, triggering an event (sending test email or dropping file), and verifying action file appears in /Needs_Action with correct metadata. Delivers value as an automation trigger even with manual processing.

**Acceptance Scenarios**:

1. **Given** Gmail Watcher is running, **When** a new email arrives in my inbox, **Then** an action file should be created in /Needs_Action with email metadata (sender, subject, body snippet, timestamp)
2. **Given** File System Watcher is running, **When** I drop a file into the monitored /Inbox folder, **Then** an action file should be created in /Needs_Action with file metadata (name, path, size, creation time)
3. **Given** the watcher is running, **When** I check the watcher log file, **Then** I should see timestamps of check cycles and any detection events

---

### User Story 3 - Claude Code Vault Integration (Priority: P1)

As a user, I want Claude Code to successfully read from and write to my Obsidian vault, so that the AI Employee can access context from my knowledge base and update it with results.

**Why this priority**: Core reasoning layer requirement - without read/write capability, Claude Code cannot function as an autonomous employee that maintains state and history.

**Independent Test**: Can be fully tested by asking Claude Code to read Dashboard.md, update the activity log, and verify changes persist. Delivers value as an AI assistant that maintains session history and context.

**Acceptance Scenarios**:

1. **Given** Claude Code is pointed to my vault directory, **When** I ask it to read Company_Handbook.md, **Then** it should summarize the business rules and confirm successful read
2. **Given** Claude Code can read the vault, **When** I ask it to update Dashboard.md with a new activity entry, **Then** the activity log should show the new entry with timestamp
3. **Given** an action file exists in /Needs_Action, **When** Claude Code processes it, **Then** it should read the action file, perform the requested task, and move the file to /Done

---

### User Story 4 - Basic Folder Workflow (Priority: P2)

As a user, I want a file-based workflow using /Inbox, /Needs_Action, and /Done folders, so that I can visually track the AI Employee's work pipeline and manually intervene when needed.

**Why this priority**: Enables visual monitoring and human-in-the-loop oversight. Not critical for MVP but important for trust and debugging.

**Independent Test**: Can be fully tested by manually moving files between folders and observing Claude Code's response. Delivers value as a simple task management system.

**Acceptance Scenarios**:

1. **Given** files exist in /Needs_Action, **When** Claude Code processes them, **Then** completed tasks should move to /Done automatically
2. **Given** I drop a file in /Inbox, **When** the file system watcher detects it, **Then** it should create an action file in /Needs_Action
3. **Given** a file is in /Done, **When** I check its contents, **Then** I should see metadata showing completion timestamp and processing results

---

### User Story 5 - Agent Skills Implementation (Priority: P1)

As a developer, I want all AI functionality implemented as Agent Skills (SKILL.md files), so that the AI Employee has reusable, documented capabilities that can be invoked consistently.

**Why this priority**: Architecture requirement per hackathon rules - Agent Skills provide structure, documentation, and reusability that raw prompts lack.

**Independent Test**: Can be fully tested by invoking each skill with test inputs and verifying expected outputs. Delivers value as a documented API for AI capabilities.

**Acceptance Scenarios**:

1. **Given** I have created a "vault-setup" skill, **When** I invoke it, **Then** it should create the Obsidian vault structure with all required folders and template files
2. **Given** I have created a "task-processor" skill, **When** I invoke it with /Needs_Action path, **Then** it should process all action files and move completed ones to /Done
3. **Given** I have created a "dashboard-updater" skill, **When** I invoke it, **Then** it should refresh Dashboard.md with current status, recent activities, and pending task count

---

### Edge Cases

- **What happens when Obsidian vault is locked/in use?** System should detect lock file and wait/retry, logging the delay without crashing.
- **What happens when the watcher script crashes?** System should have basic error logging to file, allowing manual restart and inspection of failure reason.
- **What happens when /Needs_Action has 100+ files?** System should process in chronological order (oldest first) to prevent starvation, with configurable batch size.
- **What happens when Claude Code cannot write to vault?** System should fail gracefully with clear error message and retry logic for transient permission issues.
- **What happens when action file has malformed metadata?** System should log validation error, move file to /Errors folder, and continue processing other files.
- **What happens when Gmail API rate limits are hit?** Gmail Watcher should implement exponential backoff, respect 429 responses, and log rate limit events.
- **What happens when user deletes a file that Claude is processing?** System should detect FileNotFoundError, log it, and skip to next file without crashing.
- **What happens when Dashboard.md grows to 10MB+?** System should implement log rotation, archiving old activity entries to /Logs/archive/ folder.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Obsidian Vault & Knowledge Base (FR-001 to FR-005)

- **FR-001**: System MUST create Obsidian vault structure with root folders: /Inbox, /Needs_Action, /Done, /Logs, /Skills
- **FR-002**: System MUST generate Dashboard.md with sections: Current Status, Activity Log (last 20 entries), Pending Tasks Summary, Recent Completions
- **FR-003**: System MUST generate Company_Handbook.md with sections: Business Rules, Decision Guidelines, Approval Thresholds, Contact Lists, Subscription Inventory
- **FR-004**: Dashboard.md MUST update automatically when tasks are processed, showing timestamp, task type, and outcome
- **FR-005**: Company_Handbook.md MUST be readable by Claude Code to provide context for decision-making

#### Watcher Layer (FR-006 to FR-010)

- **FR-006**: System MUST implement ONE working Watcher script (choice: Gmail Watcher OR File System Watcher)
- **FR-007**: Gmail Watcher (if chosen) MUST check for new emails every 2-5 minutes using Gmail API with OAuth 2.0
- **FR-008**: File System Watcher (if chosen) MUST monitor /Inbox folder in real-time using watchdog library or equivalent
- **FR-009**: Watcher MUST create action files in /Needs_Action with standardized metadata format: type, source, timestamp, payload
- **FR-010**: Watcher MUST log all check cycles and detection events to /Logs/watcher_YYYY-MM-DD.log

#### Claude Code Integration (FR-011 to FR-015)

- **FR-011**: Claude Code MUST have read access to all files in Obsidian vault directory
- **FR-012**: Claude Code MUST have write access to Dashboard.md, /Needs_Action, /Done, and /Logs folders
- **FR-013**: Claude Code MUST successfully parse action files and extract metadata (type, source, timestamp, payload)
- **FR-014**: Claude Code MUST update Dashboard.md activity log after processing each action file
- **FR-015**: Claude Code MUST move completed action files from /Needs_Action to /Done with processing metadata appended

#### File-Based Workflow (FR-016 to FR-020)

- **FR-016**: System MUST support manual file movement between /Inbox, /Needs_Action, /Done folders
- **FR-017**: Action files MUST follow naming convention: {SOURCE}_{YYYYMMDD}_{HHMMSS}_{identifier}.md
- **FR-018**: Completed files in /Done MUST include processing metadata: completion_timestamp, processing_time, outcome
- **FR-019**: System MUST maintain chronological processing order (oldest action files first)
- **FR-020**: System MUST create /Logs folder with watcher logs, error logs, and processing history

#### Agent Skills Architecture (FR-021 to FR-025)

- **FR-021**: All AI functionality MUST be implemented as Agent Skills with SKILL.md files in /Skills folder
- **FR-022**: System MUST implement "vault-setup" skill to initialize Obsidian vault structure
- **FR-023**: System MUST implement "task-processor" skill to process action files from /Needs_Action
- **FR-024**: System MUST implement "dashboard-updater" skill to refresh Dashboard.md with current status
- **FR-025**: Each skill MUST include: skill name, description, input parameters, output format, usage examples

#### Error Handling & Logging (FR-026 to FR-030)

- **FR-026**: System MUST log all errors to /Logs/error_YYYY-MM-DD.log with timestamp, error type, stack trace
- **FR-027**: System MUST continue processing remaining files when one action file fails
- **FR-028**: System MUST implement graceful degradation when Obsidian vault is locked (wait and retry)
- **FR-029**: Watcher script MUST handle Gmail API rate limits with exponential backoff
- **FR-030**: System MUST validate action file metadata format before processing, moving malformed files to /Errors folder

---

### Key Entities *(include if feature involves data)*

- **Action File**: Markdown file representing a detected event requiring processing
  - Attributes: type (email|file|scheduled), source (Gmail|FileSystem|Manual), timestamp (ISO 8601), payload (event-specific data), status (pending|processing|complete|error)
  - Relationships: Created by Watcher, processed by Claude Code, archived in /Done

- **Dashboard Entry**: Single line in Dashboard.md activity log
  - Attributes: timestamp, task_type, source, outcome, duration
  - Relationships: Appended by Claude Code after each task completion

- **Skill Definition**: Reusable AI capability defined in SKILL.md
  - Attributes: skill_name, description, input_schema, output_format, invocation_examples
  - Relationships: Invoked by Claude Code, stored in /Skills folder

- **Watcher Process**: Background script monitoring for events
  - Attributes: watcher_type (Gmail|FileSystem), check_interval, last_check_time, status (running|stopped|error), PID
  - Relationships: Creates Action Files, writes to Watcher Logs

- **Company Handbook**: Central rules document for AI decision-making
  - Attributes: business_rules, approval_thresholds, contact_lists, subscription_inventory
  - Relationships: Referenced by Claude Code during task processing

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Core Functionality (SC-001 to SC-005)

- **SC-001**: Obsidian vault initializes in under 2 minutes with all required folders and template files
- **SC-002**: Watcher script runs continuously for 24 hours without crashing
- **SC-003**: 95% of detected events result in action file creation within 30 seconds
- **SC-004**: Claude Code successfully processes 90% of action files on first attempt
- **SC-005**: Dashboard.md updates within 5 seconds after task completion

#### User Experience (SC-006 to SC-010)

- **SC-006**: User can verify watcher status by checking log file (last check timestamp)
- **SC-007**: User can manually drop a file in /Inbox and see it processed within 2 minutes
- **SC-008**: Dashboard.md provides clear visual summary of AI Employee activity at a glance
- **SC-009**: Action files use human-readable format that users can understand and edit
- **SC-010**: Setup process (vault creation + watcher installation) completes in under 15 minutes

#### Quality & Reliability (SC-011 to SC-015)

- **SC-011**: System handles 50 action files per day without performance degradation
- **SC-012**: Error rate below 5% (95% of tasks complete successfully)
- **SC-013**: All errors are logged with sufficient detail for debugging
- **SC-014**: System recovers automatically from transient failures (API timeout, network glitch)
- **SC-015**: No data loss - all detected events create persistent action files

#### Architecture & Best Practices (SC-016 to SC-020)

- **SC-016**: 100% of AI functionality implemented as documented Agent Skills
- **SC-017**: All action files follow standardized metadata format (type, source, timestamp, payload)
- **SC-018**: Watcher logs include check cycles, detections, and errors with timestamps
- **SC-019**: Company_Handbook.md provides sufficient context for Claude Code to make informed decisions
- **SC-020**: System architecture follows separation of concerns (Watchers → Action Files → Claude → Completion)

---

## Assumptions

### Environment Assumptions

- User has Obsidian v1.10.6+ installed and knows how to create/open vaults
- User has Python 3.13+ installed with pip for dependency management
- User has Claude Code subscription (Pro) or access to free Gemini API with Claude Code Router
- User has stable internet connection (10+ Mbps) for API calls
- User is on Windows, macOS, or Linux with terminal/bash access

### Account & Service Assumptions

- If Gmail Watcher chosen: User has Gmail account with API access enabled
- If Gmail Watcher chosen: User can complete OAuth 2.0 authentication flow
- User has GitHub account for version control (optional but recommended)
- User has basic understanding of command-line interfaces

### Data Assumptions

- Action files are small (<1MB each) and vault remains under 1GB for Bronze Tier
- Dashboard.md activity log is manually archived when it exceeds 1000 entries
- Watcher logs rotate manually when they exceed 10MB
- User checks /Needs_Action manually at least once daily during testing

### Operational Assumptions

- Watcher script runs during work hours (8am-6pm) for testing, not 24/7
- User manually starts watcher script (no automatic startup on boot)
- User monitors system health via log files, not automated alerting
- Tasks are idempotent (safe to retry if processing fails)

### Technical Assumptions

- File system supports atomic file moves (POSIX or Windows NTFS)
- Obsidian vault is on local disk, not network drive
- Claude Code has sufficient token budget for task processing
- Python dependencies install without conflicts
- No concurrent write conflicts (only one process writes to Dashboard.md)

### Scope Boundaries

- Bronze Tier is single-user system (no multi-tenancy)
- No encryption at rest (assumes trusted local machine)
- No real-time push notifications (user checks Dashboard manually)
- No web interface (Obsidian and file system only)
- No scheduling (cron/Task Scheduler) - manual watcher execution

---

## Dependencies

### External Services

- **Gmail API** (if Gmail Watcher chosen): OAuth 2.0, message read scopes
- **Claude API**: For Claude Code reasoning engine (via Claude Code CLI)
- **Obsidian**: Desktop application for vault GUI

### Software & Libraries

- **Python 3.13+**: Core runtime for Watcher scripts
- **pip packages**: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client (if Gmail), watchdog (if File System), pyyaml, python-frontmatter
- **Claude Code CLI**: Installed and authenticated
- **Git**: For version control (recommended)

### Internal Components

- Company_Handbook.md: Provides business rules context for Claude Code
- Dashboard.md: Central status display
- /Needs_Action folder: Queue for pending tasks
- Watcher script: Event detection and action file creation
- Agent Skills: Reusable AI capabilities

### Infrastructure

- Local disk space: Minimum 500MB for vault and logs
- Stable internet: Required for API calls (Gmail, Claude)
- Firewall: Must allow outbound HTTPS for API access

---

## Out of Scope

### Features Explicitly Excluded (Bronze Tier)

- Multiple Watcher scripts (Silver/Gold Tier requirement)
- MCP servers for external actions (Silver/Gold Tier requirement)
- Human-in-the-loop approval workflow (Silver/Gold Tier requirement)
- Scheduling via cron/Task Scheduler (Silver Tier requirement)
- Plan.md generation with reasoning loop (Silver Tier requirement)
- Cross-domain integration Personal + Business (Gold Tier requirement)
- Xero/Odoo accounting integration (Gold Tier requirement)
- Social media posting (Silver/Gold Tier requirement)
- Ralph Wiggum autonomous loop (Gold Tier requirement)
- Orchestrator + Watchdog process management (Gold Tier requirement)
- Comprehensive audit logging (Gold Tier requirement)
- CEO Briefing generation (Gold Tier requirement)

### Future Enhancements (Post-Bronze)

- Multi-watcher orchestration with health monitoring
- Automated watcher startup on system boot
- Web-based dashboard (alternative to Obsidian GUI)
- Real-time notifications (email, SMS, desktop alerts)
- Action file encryption at rest
- Performance metrics and analytics
- Integration testing suite
- Docker containerization for portability

### Technical Limitations

- No production-grade security (credentials stored in plaintext .env)
- No database (all state in file system)
- No distributed system support (single machine only)
- No API for external integrations
- No user authentication (single-user system)
- No backup/restore functionality
- No configuration UI (manual .env editing)

---

## Risks & Mitigation

### High Severity Risks

1. **Gmail API quota exceeded during testing**
   - **Impact**: Watcher stops functioning, no new emails detected
   - **Probability**: Medium (10,000 quota units/day, check every 2 min = ~720 checks/day)
   - **Mitigation**: Implement exponential backoff, check every 5 minutes during testing, monitor quota usage

2. **Obsidian vault corruption from concurrent writes**
   - **Impact**: Dashboard.md becomes unreadable, data loss
   - **Probability**: Low (assuming single Claude Code instance)
   - **Mitigation**: Implement file locking, atomic writes, backup Dashboard.md before modifications

3. **OAuth token expiration breaking Gmail Watcher**
   - **Impact**: Watcher crashes, no detection until manual re-auth
   - **Probability**: High (tokens expire after 1 hour by default)
   - **Mitigation**: Implement automatic token refresh, store refresh token securely, graceful error handling

### Medium Severity Risks

4. **Watcher script crashes without visibility**
   - **Impact**: No detection, silent failure until user notices
   - **Probability**: Medium (Python exceptions, network errors)
   - **Mitigation**: Comprehensive error logging, health check endpoint, manual monitoring during testing

5. **Claude Code token budget exhaustion**
   - **Impact**: Task processing stops mid-session
   - **Probability**: Medium (depends on task complexity and volume)
   - **Mitigation**: Monitor token usage, implement batching for large tasks, estimate costs beforehand

6. **Action file naming collisions**
   - **Impact**: Files overwrite each other, data loss
   - **Probability**: Low (timestamp precision to seconds)
   - **Mitigation**: Add milliseconds to timestamp, implement collision detection, append random suffix

### Low Severity Risks

7. **Dashboard.md grows unbounded**
   - **Impact**: Slow reads, Obsidian performance degradation
   - **Probability**: High (no automatic archiving)
   - **Mitigation**: Document manual archiving process, implement entry limit warning

8. **Log files fill disk space**
   - **Impact**: Watcher crashes on write failure
   - **Probability**: Low (Bronze tier has low volume)
   - **Mitigation**: Document log rotation process, check disk space before starting

9. **File system watcher consumes excessive CPU**
   - **Impact**: System slowdown, battery drain on laptops
   - **Probability**: Low (watchdog library is efficient)
   - **Mitigation**: Monitor CPU usage, implement polling interval configuration

---

## Implementation Notes

### Bronze Tier Completion Checklist

This Bronze Tier implementation focuses on the **Foundation** - proving the core architecture works before adding complexity. Success means:

- ✅ Obsidian vault structure created
- ✅ Dashboard.md and Company_Handbook.md populated with templates
- ✅ One Watcher script (Gmail OR File System) running and detecting events
- ✅ Action files created in /Needs_Action with correct metadata
- ✅ Claude Code can read vault contents
- ✅ Claude Code can write to Dashboard.md and move files to /Done
- ✅ At least 3 Agent Skills implemented (vault-setup, task-processor, dashboard-updater)
- ✅ Watcher logs showing check cycles and detections
- ✅ End-to-end test: Event → Action File → Claude Processing → /Done
- ✅ Documentation: README.md with setup instructions

### Recommended Implementation Order

1. **Phase 1 - Vault Setup (2 hours)**
   - Create Obsidian vault
   - Generate Dashboard.md and Company_Handbook.md templates
   - Create folder structure (/Inbox, /Needs_Action, /Done, /Logs, /Skills)
   - Verify Claude Code can read/write vault

2. **Phase 2 - Watcher Script (3-4 hours)**
   - Choose Gmail OR File System watcher
   - Implement detection logic
   - Create action file generation
   - Test logging and error handling
   - Run for 1 hour continuously without crashes

3. **Phase 3 - Claude Integration (2-3 hours)**
   - Create "task-processor" Agent Skill
   - Test action file parsing
   - Implement Dashboard.md update logic
   - Test file movement to /Done

4. **Phase 4 - Additional Skills (2 hours)**
   - Create "vault-setup" Agent Skill
   - Create "dashboard-updater" Agent Skill
   - Document each skill with usage examples

5. **Phase 5 - Testing & Documentation (1-2 hours)**
   - End-to-end test with 10+ action files
   - Verify all success criteria
   - Write README.md with setup instructions
   - Record demo video showing key workflow

### Key Technical Decisions

- **Watcher Choice**: Recommend File System Watcher for Bronze (simpler, no OAuth setup)
- **Polling Interval**: 30 seconds for File System, 2 minutes for Gmail
- **Action File Format**: Markdown with YAML frontmatter for human readability
- **Dashboard Update Strategy**: Append-only (no retroactive edits)
- **Error Handling**: Log and continue (don't crash on single file failure)

### Architecture Validation

Bronze Tier must prove these architectural principles:

1. **Perception → Memory → Reasoning → Action** pipeline works end-to-end
2. File-based state management is viable for AI automation
3. Claude Code can reliably parse and update Obsidian markdown
4. Watcher pattern enables autonomous triggering (not just reactive chat)
5. Agent Skills provide reusable structure for AI capabilities

If any of these principles fail, Silver/Gold tiers will compound the problems. Bronze is the foundation that validates the entire approach.

---

**Next Steps After Bronze Completion**:
- Proceed to Silver Tier specification for multi-watcher orchestration, MCP servers, and approval workflows
- Evaluate lessons learned from Bronze implementation
- Identify bottlenecks and optimization opportunities
- Consider which additional watchers provide most value (Gmail, WhatsApp, Xero, Calendar, Slack)
