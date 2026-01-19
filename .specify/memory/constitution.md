# Personal AI Employee Hackathon 0 Constitution

**Project Name**: Personal AI Employee - Digital FTE (Full-Time Equivalent)

**Version**: 1.0.0
**Ratified**: 2026-01-17
**Last Amended**: 2026-01-17

---

## Core Principles

### I. Local-First & Data Sovereignty

**Description**: All data, state, and processing MUST reside on local storage (Obsidian vault on user's machine). No cloud dependencies except for API calls (Gmail, social media, Claude Code). User maintains full data sovereignty and control.

**Rationale**:
- Privacy: Personal and business data never leaves local machine without explicit consent
- Reliability: System functions without internet connectivity (cached content, queued actions)
- Security: No cloud vendor lock-in, user can change any component at any time
- Compliance: GDPR-friendly data residency, full audit trail in local logs
- Trust: User can see, modify, and understand every action the AI Employee takes

**Implementation**:
- Obsidian vault at user-specified absolute path (not cloud-based)
- All action files, logs, plans, and configuration stored locally
- Claude Code and MCP servers run locally with local authentication
- Watcher scripts maintain local state (PIDs, last check timestamps, detected events)
- No cloud databases, no cloud synchronization (Gold Tier Platinum tier may add cloud + local split)

**Validation**:
- System functions completely offline (except API calls) with degraded but functional state
- User can backup entire vault to any storage location (USB drive, cloud storage for backup)
- No cloud credentials stored in code - all credentials in .env file (documented as non-production for hackathon)

---

### II. Agent Skills Architecture (MCP Integration)

**Description**: All AI functionality MUST be implemented as Agent Skills (SKILL.md files in `.claude/commands/` directory). Each skill provides reusable, documented capabilities that Claude Code can invoke consistently.

**Rationale**:
- **Reusability**: Skills can be invoked across tiers (Bronze, Silver, Gold, Platinum) without reimplementation
- **Documentation**: Every skill MUST include: skill name, description, input parameters, output format, usage examples, error handling
- **Testability**: Each skill can be independently tested with test inputs to verify expected outputs
- **Composition**: Complex capabilities built by composing simple skills (e.g., "process-email" = "read-email" + "draft-reply" + "send-email-via-MCP")
- **Hackathon Rule**: Per hackathon requirements, all AI functionality must use Agent Skills architecture

**Implementation**:
- Each SKILL.md file follows standard format: name, description, input parameters (with types), output format, usage examples
- Skills organized in `.claude/commands/` by category: /vault-setup, /task-processor, /dashboard-updater, /linkedin-poster, /plan-generator, etc.
- Claude Code invokes skills by skill name (file basename without .md extension) or via full file path
- Skills can call other skills recursively (composition without depth limit)
- All Bronze, Silver, Gold, Platinum functionality MUST be implemented as skills

**Validation**:
- Every AI capability has corresponding SKILL.md file
- Skills can be independently tested with mock inputs
- Skills maintain backward compatibility across tiers (Bronze skills work in Gold, Platinum)
- New skills follow naming convention: {action}-{object} (e.g., "process-email", "post-linkedin", "audit-odoo")

---

### III. Multi-Tier Incremental Architecture

**Description**: System MUST follow tiered progression (Bronze → Silver → Gold → Platinum) where each tier validates core principles before adding complexity. Each tier builds incrementally on previous tier's foundation.

**Rationale**:
- **Risk Mitigation**: Validates architecture principles at each tier before scaling (Bronze: file-based approach, Silver: multi-watcher + MCP, Gold: orchestrator + audit, Platinum: cloud+local split)
- **Learning Curve**: Hackathon participants can start with Bronze tier (8-12 hours), progress to Silver (20-30 hours) or Gold (40+ hours) based on time and skill level
- **Testing Validation**: Each tier independently testable with clear success criteria
- **Scope Control**: Prevents over-engineering by breaking complex requirements into achievable milestones

**Tier Definitions** (from Requirements2.md):
- **🥉 Bronze Tier (8-12 hours)**: Single watcher, Obsidian vault, Dashboard.md, Company_Handbook.md, basic folder structure
- **🥈 Silver Tier (20-30 hours)**: Two+ watchers, MCP server, approval workflow, Plan.md reasoning, scheduled automation
- **🏆 Gold Tier (40+ hours)**: All Silver plus cross-domain integration, 6+ watchers, 6+ MCP servers, orchestrator + watchdog, Ralph Wiggum loop, CEO briefing, audit logging, **Odoo Community accounting system (self-hosted, local) with MCP server integration via Odoo 19+ External JSON-2 API**
- **💎 Platinum Tier (60+ hours)**: Gold plus cloud + local split, vault synchronization, advanced analytics

**Implementation**:
- Each tier MUST be independently testable with clear success criteria
- Features MUST be organized by tier: Bronze foundation, Silver functional, Gold autonomous, platinum cloud-local
- Specified in specs/{tier}-tier-name}/spec.md for each tier
- Tasks MUST reference prerequisite tier (Bronze tier is prerequisite for Silver, Silver is prerequisite for Gold, etc.)
- No tier can be skipped (Bronze → Silver → Gold → Platinum in order)

**Validation**:
- Each tier's specification includes tier-specific success criteria
- Each tier builds incrementally on previous tier without breaking changes
- Tier progression validated through end-to-end testing at each stage

---

### IV. Watcher Pattern: Perception → Action File → Reasoning → Action

**Description**: All system perception MUST follow the Watcher Pattern: Lightweight Python scripts monitor external sources (Gmail, Slack, WhatsApp, Calendar, File System, Odoo) for events, create action files in /Needs_Action with standardized metadata, and trigger Claude Code reasoning and action via MCP servers.

**Rationale**:
- **Autonomous Triggering**: System detects events without user typing prompts (vs reactive chatbot approach)
- **Scalability**: Independent watcher scripts can be added/removed without affecting other watchers
- **Reliability**: Watchers run continuously even if Claude Code is not processing (queue builds for later processing)
- **Simplicity**: Each watcher is a simple Python script with single responsibility (SRP: Single Responsibility Principle)
- **Observability**: Each watcher maintains independent log file with timestamps and detection events

**Implementation**:
- BaseWatcher class defines: check_for_updates(), create_action_file(metadata), run() main loop
- Each watcher (Gmail, Slack, WhatsApp, Calendar, File System, Odoo) extends BaseWatcher
- Watcher config in watchers/watcher_config.yaml enables/disables watchers and defines check intervals
- Watchers create action files with YAML frontmatter: type, source, timestamp, status, payload, processing_metadata
- Watchers log all detection events and errors to /Logs/watcher_{watcher_name}_YYYY-MM-DD.log
- Claude Code processes action files via task-processor Agent Skill

**Validation**:
- Each watcher can run independently without other watchers
- Watchers maintain independent log files
- Deduplication prevents duplicate action files for same event (event_id matching: Gmail message_id, file hash, etc.)
- System continues functioning if one watcher crashes (other watchers continue detecting events)
- All watchers report health status to Dashboard

---

### V. File-Based State Management

**Description**: All system state (except ephemeral process state) MUST be stored as files in the Obsidian vault. No database required for Bronze, Silver, or Gold tiers. This ensures transparency, debuggability, and observability.

**Rationale**:
- **Transparency**: All state is human-readable (markdown files in Obsidian GUI)
- **Debuggability**: User can inspect any state file to understand system behavior
- **Observability**: All changes logged with timestamps and context
- **Version Control**: Git tracks vault history (Dashboard.md, Company_Handbook.md, action files, logs)
- **Simplicity**: No database schema migrations, no query language to learn
- **Audit Trail**: Complete history of all actions stored in files (files in /Done, /Errors, /Logs)

**Implementation**:
- Action files: Markdown with YAML frontmatter in /Needs_Action, /Done, /Errors
- Configuration: YAML files in watchers/, /Scheduled/config.yaml
- State tracking: Watcher state in watchers_state.json (deduplication), Plan.md files (task reasoning)
- Logs: All text files with timestamps in /Logs/ folder
- Dashboard.md: Activity log, current status, task summary
- Company_Handbook.md: Business rules, decision guidelines, approval thresholds

**Validation**:
- All state can be inspected with text editor or Obsidian GUI
- Git diff shows all changes over time
- User can manually edit any state file if needed
- No state is locked or binary (except temporary process memory)
- System functions correctly if user manually moves or edits state files

---

### VI. Human-in-the-Loop Approval Workflow

**Description**: All sensitive actions (emails, social media posts, financial transactions >$100, data deletion) MUST route through human approval workflow before execution. File-based state machine (/Pending_Approval → /Approved or /Rejected) ensures human oversight and prevents autonomous mistakes.

**Rationale**:
- **Trust & Safety**: Business-critical actions require human authorization to prevent reputation damage or financial liability
- **Control**: User maintains veto power over autonomous actions
- **Learning**: Approval requests include action summary, risk level, deadline, potential impact to help user learn system behavior
- **Liability**: Human approval provides audit trail of authorized vs unauthorized actions
- **Transparency**: Obsidian GUI makes approval state visible (file folder shows pending items)

**Implementation**:
- Task-processor skill checks action type against sensitive actions list before executing
- Sensitive actions list defined in Company_Handbook.md or Company_Handbook.md
- Task-processor moves action file from /Needs_Action to /Pending_Approval with approval_request.md metadata
- User reviews action summary in Obsidian, moves file to /Approved (execute) or /Rejected (cancel)
- Task-processor checks /Approved folder every 60 seconds, executes approved actions immediately
- Approval deadline: Default 24 hours (configurable in Company_Handbook.md),过期 = auto-reject after 7 days
- Dashboard shows: pending_approvals_count, approvals_today, rejections_today, oldest_pending_approval_age

**Validation**:
- 100% of sensitive actions route through /Pending_Approval (zero bypasses)
- Human can approve or reject actions in Obsidian GUI via file movement
- Approved actions execute within 1 hour of human approval
- Rejected actions move to /Done with rejection_reason
- System notifies human when approval deadline expires

---

### VII. Ralph Wiggum Autonomous Loop (Stop Hook Pattern)

**Description**: For complex multi-step tasks, Claude Code MUST iterate autonomously (without human input) until task is complete using the Ralph Wiggum Stop hook pattern (stop hook intercepts Claude's exit, checks if task is complete, re-injects prompt if not complete, loops until task completion or max iterations reached).

**Rationale**:
- **Autonomous Multi-Step Execution**: Enables AI Employee to complete complex workflows (e.g., "organize client files by month, then by project, then by client") without human intervention
- **Transparency**: Plan.md files document the reasoning and steps, human can review before approving task execution
- **Control**: Human can approve/reject Plan.md before Ralph loop execution, maintaining oversight
- **Reliability**: System continues working until task is complete, not stuck waiting for next user prompt
- **Progress Visibility**: Dashboard shows active plans with step-by-step execution tracking

**Implementation**:
- Plan.md includes: objective, step-by-step approach, estimated_time, dependencies, risks
- Ralph Wiggum stop hook: /claude/plugins/ralph-wiggum/stop_hook.py (see Gold Tier reference implementation)
- Stop hook checks: Is task file in /Done? (complete) OR max_iterations reached? (stop) OR task_still_pending? (continue)
- Stop hook blocks Claude exit, re-injects prompt with task context and partial results
- Plan.md updated in real-time: mark steps complete, log actual_time vs estimated_time, note deviations
- Execution tracked in Plan.md: step_number, status (pending/in_progress/complete), actual_time, notes

**Validation**:
- Complex tasks (3+ steps OR >15 minutes) always have Plan.md before execution
- Ralph loop continues autonomously until task complete or max_iterations (default 10)
- Human can approve Plan.md before Ralph loop execution
- Dashboard shows: active_plans_count, plans_completed_today, average_plan_accuracy
- System notifies human if plan execution deviates >20% from estimated time

---

### VIII. MCP Server External Action Layer

**Description**: All external actions (send email, post to social media, query accounting, etc.) MUST execute via Model Context Protocol (MCP) servers. Claude Code Agent Skills invoke MCP servers as tools. This abstraction enables external action integration without tight coupling to specific APIs.

**Gold Tier - Odoo Community Accounting Integration:**

**Description**: Gold tier MUST include a self-hosted Odoo Community accounting system (local installation) integrated via an MCP server using Odoo 19+ External JSON-2 API. This provides complete business accounting functionality while maintaining local-first data sovereignty.

**Rationale**:
- **Local-First Accounting**: Odoo Community installed locally ensures all financial data remains on user's machine (aligns with Principle I: Local-First & Data Sovereignty)
- **No Cloud Dependencies**: Self-hosted Odoo eliminates third-party accounting service subscriptions and data residency concerns
- **Complete ERP Features**: Odoo Community provides invoicing, bills, payments, bank reconciliation, financial reporting, and accounting management
- **MCP Integration**: Odoo MCP server exposes accounting operations as tools (create_invoice, record_payment, reconcile_bank, generate_financial_report)
- **External JSON-2 API**: Odoo 19+ External API uses HTTP REST-like protocol for seamless integration

**Implementation**:
- **Odoo Installation**: Install Odoo Community 19+ locally (Docker or direct installation) on user's machine
- **Database**: PostgreSQL database co-located with Odoo installation (local, not cloud)
- **Authentication**: Odoo user credentials stored securely in .env file
- **Odoo MCP Server**: MCP server (Node.js or Python) implements Odoo 19+ External JSON-2 API calls
  - Tools: create_invoice, create_bill, record_payment, reconcile_bank, generate_report, query_accounts
  - Input schema: invoice data (customer, items, amounts), bill data (vendor, items, amounts), payment data
  - Output schema: success status, invoice/bill IDs, payment confirmation, report data
- **Odoo Watcher**: Python watcher monitors Odoo for new invoices, bills, payments, creates action files in /Needs_Action
- **Financial Events**: Large transactions, overdue invoices, unusual account activity trigger alerts
- **Audit Logging**: All Odoo operations logged to /Logs/odoo_actions_YYYY-MM-DD.json with full context

**Validation**:
- Odoo Community 19+ installed locally and accessible
- MCP server successfully connects to Odoo via External JSON-2 API
- Create invoice, create bill, record payment operations work end-to-end
- Odoo watcher detects new financial events and creates action files
- All Odoo data remains local (no cloud sync or external dependencies)
- Financial reports (profit/loss, balance sheet, aged receivables) generated correctly

**General MCP Rationale**:
- **Abstraction**: MCP protocol standardizes tool definitions, input/output schemas, error handling
- **Modularity**: Each external service has dedicated MCP server (Gmail MCP, LinkedIn MCP, Odoo MCP, Calendar MCP, Slack MCP, Facebook MCP, etc.)
- **Extensibility**: Adding new external service = add new MCP server without changing core architecture
- **Testability**: MCP servers can be tested independently with MCP Client (mcp-client) before integration
- **Language Independence**: MCP servers can be implemented in any language (Node.js, Python, Rust, Go) - not tied to Claude Code Python runtime
- **Scalability**: Multiple MCP servers can run concurrently without interference

**General MCP Implementation**:
- Each MCP server exposes one or more tools: tool_name (string), description, input_schema, output_schema
- Claude Code Agent Skills invoke MCP tools via subprocess or HTTP if MCP server exposes HTTP endpoint
- MCP servers communicate via stdio (Model Context Protocol) or HTTP (for external accessibility)
- Each MCP server handles authentication (OAuth 2.0, API keys, session tokens, JSON-RPC) independently
- MCP servers log all actions to /Logs/mcp_actions_YYYY-MM-DD.json with: action_type, input_params, output_result, timestamp
- Error handling: MCP servers return structured errors with error_type, error_message, retry_possible, suggested_action

**Validation**:
- Each MCP server can be tested independently with MCP Client tool or simple curl/push commands
- Claude Code can invoke MCP tools successfully with correct inputs and get expected outputs
- MCP servers handle authentication failures gracefully (OAuth refresh, token expiration, invalid credentials)
- MCP servers return structured responses (success boolean, result data, error handling)
- Multiple MCP servers can run concurrently (Gmail MCP, LinkedIn MCP, Odoo MCP, etc.)

---

## Additional Constraints

### Security & Privacy

- **OAuth 2.0** MUST be used for all external API integrations (Gmail, LinkedIn, Calendar, Slack, WhatsApp)
- **Token Management**: Refresh tokens MUST be stored securely in .env file (documented as non-production for hackathon), automatic refresh before expiration
- **Credential Storage**: No credentials hardcoded in code. All credentials in .env file (user fills in manually)
- **Data Encryption**: Sensitive data (passwords, tokens) MUST be encrypted at rest if stored in files
- **Audit Trail**: All actions MUST be logged with: action_type, input_params, output_result, timestamp, responsible_agent (Claude Code or human)
- **Data Minimization**: System MUST only collect data necessary for task execution (no data collection for unspecified purposes)

### Performance & Scalability

- **Watcher Check Intervals**:
  - Gmail: every 2-5 minutes
  - Slack: every 1 minute
  - WhatsApp: every 30 seconds
  - Calendar: every 5 minutes (1-48 hours ahead)
  - File System: real-time (watchdog library)
  - Odoo: every 5 minutes
- **Action File Throughput**: System MUST support 100 action files per day (Silver tier) or 1000 files per day (Gold tier)
- **Dashboard Updates**: Dashboard.md MUST update within 5 seconds after task completion
- **MCP Response Time**: MCP servers MUST respond within 5 seconds for external actions (email send, social post)
- **Approval Timeout**: System MUST execute approved actions within 1 hour of human approval
- **Scheduled Task Deviation**: Scheduled tasks MUST execute within 5 minutes of scheduled time

### Error Handling & Recovery

- **Watcher Crashes**: Watcher scripts MUST log errors to /Logs/watcher_{watcher_name}_YYYY-MM-DD.log and exit gracefully (no crash)
- **MCP Server Unreachable**: Task-processor MUST queue actions, retry with exponential backoff (3 attempts), move to /Errors if retries exhausted
- **Plan.md Execution Deviation**: If task execution deviates >20% from Plan.md estimated time, system MUST create addendum Plan.md, notify human, archive lessons_learned
- **Approval Deadline Expired**: If approval deadline expires (default 24 hours), system MUST notify human, escalate priority, auto-reject after 7 days (configurable)
- **Deduplication Failures**: If deduplication misses duplicate event, system MUST log deduplication_error to /Logs/error_YYYY-MM-DD.json, human can manually clean up duplicates
- **Action File Format Errors**: If action file has malformed YAML frontmatter, move to /Errors with validation error details, continue processing other files

### Platform & Compatibility

- **Cross-Platform**: System MUST work on Windows 10/11+, macOS 12+, Linux (Ubuntu 20.04+, Debian 11+) without breaking functionality
- **Python Version**: 3.13+ (Bronze tier minimum) for watchers and orchestration
- **Node.js Version**: v24+ LTS for MCP servers (official MCP SDK support)
- **Obsidian Version**: 1.10.6+ for vault GUI (local markdown knowledge base)
- **Claude Code**: Active subscription (Pro) or Free Gemini API with Claude Code Router (alternative to Pro subscription)
- **Browsers**: Chrome, Firefox, Safari (latest versions) for MCP Playwright LinkedIn automation (if API unavailable)

### File Organization

- **Vault Root**: User-specified absolute path to Obsidian vault directory (e.g., `/Users/name/Documents/AI_Employee_Vault`)
- **Folder Structure**: /Inbox (drop zone), /Needs_Action (queue), /Done (archive), /Logs (logging), /Errors (errors), /Plans (plans), /Pending_Approval (approvals), /Approved (ready to execute), /Rejected (cancelled), /Scheduled (scheduled), /Skills (Agent Skills), /Ralph (autonomous loop), /Orchestrator (orchestration), /MCP (MCP servers)

---

## Governance

### Amendment Procedure

1. **Propose Amendment**: Identify need for constitutional change (e.g., new principle, existing principle update, section addition)
2. **Document Amendment**: Create amendment document: old_text → new_text with rationale
3. **Review & Discuss**: Present amendment to user with: impact analysis, alternatives considered, recommended approach
4. **User Approval**: Get user consent (user can request clarification or modification)
5. **Implement Changes**: Make changes to constitution.md, propagate to dependent artifacts
6 **Update Version**: Bump version according to semantic versioning: MAJOR (breaking changes), MINOR (additions), PATCH (clarifications)
7. **Validate Artifacts**: Ensure plan.md, spec.md, tasks.md, template files align with updated constitution

### Versioning Policy

- **Format**: MAJOR.MINOR.PATCH (e.g., 1.0.0, 1.1.0, 2.0.0)
- **MAJOR**: Breaking changes - removes or redefines core principles, backward incompatible changes
- **MINOR**: Adds new principle or materially expands existing principle
- **PATCH**: Clarifications, wording improvements, typo fixes, non-semantic refinements
- **Incremental Versioning**: Start at 1.0.0 (initial adoption), increment based on changes

### Compliance Review

- **Constitution Check**: All PRs and code reviews MUST verify compliance with constitutional principles before merge
- **Scope Creep**: All code reviews MUST verify changes are within defined tier scope (Bronze, Silver, Gold, Platinum)
- **Architecture Validation**: All architectural decisions MUST align with tier progression (Bronze → Silver → Gold → Platinum)
- **Component Reuse**: Code reviews MUST verify Bronze/Silver components are reused in Gold tier without breaking changes
- **File-Based State**: Code reviews MUST verify no database is introduced (file-based state management maintained across all tiers)
- **Agent Skills**: Code reviews MUST verify all AI functionality uses Agent Skills architecture (hackathon rule)

### Review Process

- **Pre-Merge Checklist**:
  - [ ] All constitutional principles satisfied
  - [ ] Tier-appropriate complexity (Bronze/Silver/Gold/Platinum only include features for that tier)
  - [ ] No implementation details in spec.md (WHAT and WHY, not HOW)
  - [ ] All success criteria measurable and technology-agnostic (no specific tools mentioned)
  - [ ] Edge cases identified and assumptions documented
  - [ ] Dependencies and risks identified

- **Post-Merge Verification**:
  - [ ] Version correctly incremented (MAJOR/MINOR/PATCH)
  - All template placeholders replaced or intentionally retained (no unexplained brackets)
  - Governance section updated if governance model changes
  - Template alignment verified: plan.md, spec.md, tasks.md, README.md, docs/

---

**Sync Impact Report**:

- **Version Change**: 1.0.0 → 1.1.0 (MINOR: Added Odoo Community accounting system requirement for Gold tier, removed Xero references)

- **Modified Principles**: 8 core principles defined (7 original + Gold Tier Odoo requirement)
  - I. Local-First & Data Sovereignty (updated: removed Xero from API exceptions)
  - II. Agent Skills Architecture (MCP Integration)
  - III. Multi-Tier Incremental Architecture (updated: added Odoo Community to Gold tier)
  - IV. Watcher Pattern: Perception → Action File → Reasoning → Action (updated: replaced Xero with Odoo)
  - V. File-Based State Management
  - VI. Human-in-the-Loop Approval Workflow
  - VII. Ralph Wiggum Autonomous Loop (Stop Hook Pattern)
  - VIII. MCP Server External Action Layer (updated: added Odoo Community integration section)

- **Changes in v1.1.0**:
  - **Removed**: All references to Xero accounting system (replaced with Odoo Community)
  - **Added**: Gold Tier - Odoo Community Accounting Integration section with:
    - Local-first Odoo installation requirement (Docker or direct installation)
    - Odoo 19+ External JSON-2 API integration
    - MCP server for accounting operations (create_invoice, create_bill, record_payment, reconcile_bank, generate_report)
    - Odoo Watcher for financial event monitoring
    - Complete validation criteria for Odoo integration

- **Added Sections**:
  - Additional Constraints: Security & Privacy, Performance & Scalability (updated: Odoo check interval), Error Handling & Recovery, Platform & Compatibility
  - Enhanced Governance: Amendment Procedure, Versioning Policy, Compliance Review, Review Process

- **Templates Requiring Updates**:
  - ⚠️ plan.md: Constitution Check section must align with 8 core principles above (including Odoo Community integration)
  - ⚠️ spec.md: Section requirements must align with tier-specific constraints (Bronze/Silver/Gold/Platinum only, Gold tier includes Odoo Community)
  - ⚠️ tasks.md: Task categorization must align with incremental complexity principle (MVP first, then incremental delivery)
  - ⚠️ README.md: Must reflect tier progression (Bronze → Silver → Gold → Platinum) and current status, including Odoo Community requirement for Gold tier
  - ⚠️ Requirements2.md: Verify Odoo Community integration is properly specified for Gold tier
  - ⚠️ .specify/templates/commands/*.md: Verify no outdated references remain (CLAUDE only for generic agent-specific guidance)
  - ⚠️ watchers-tester.md: Ensure Odoo Watcher and Odoo MCP server development patterns are documented

---

**Version**: 1.1.0 | **Ratified**: 2026-01-17 | **Last Amended**: 2026-01-17

**Purpose**: Define constitutional principles for Personal AI Employee Hackathon 0 project. Ensures all code, specs, and documentation align with core architectural principles: local-first data sovereignty, Agent Skills (MCP) architecture, incremental tier progression, Watcher pattern, file-based state, human-in-the-loop approvals, Ralph Wiggum autonomous loop, MCP external action layer, and Gold tier Odoo Community accounting integration (local-first, self-hosted, JSON-RPC API).
