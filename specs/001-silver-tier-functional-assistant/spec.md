# Feature Specification: Silver Tier Functional Assistant - Personal AI Employee

**Feature Branch**: `001-silver-tier-functional-assistant`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "for Silver Tier and keep it after Bronze Tier"
**Tier**: Silver (Functional Assistant - Multi-Watcher Automation)
**Estimated Time**: 20-30 hours
**Prerequisite**: Bronze Tier Foundation (feature 000) must be complete

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Watcher Orchestration (Priority: P1)

As a user, I want two or more Watcher scripts running simultaneously (Gmail + File System, or add WhatsApp) so that my AI Employee can detect and process events from multiple sources without manual switching.

**Why this priority**: Core enhancement over Bronze tier's single watcher - demonstrates scalable perception layer that can monitor multiple domains (personal + business) simultaneously.

**Independent Test**: Can be fully tested by running two watcher scripts in parallel, triggering events in both sources, and verifying action files created for each with correct source metadata.

**Acceptance Scenarios**:
1. **Given** File System Watcher and Gmail Watcher are both running, **When** I drop a file in /Inbox AND receive a new email, **Then** both action files should be created in /Needs_Action with correct source labels (FileSystem vs Gmail)
2. **Given** multiple watchers are running, **When** I check each watcher's log file, **Then** I should see independent check cycles and detection events for each watcher
3. **Given** watchers are running concurrently, **When** I monitor system resources, **Then** CPU usage should remain <30% and watchers should not interfere with each other

---

### User Story 2 - LinkedIn Social Media Posting (Priority: P1)

As a business owner, I want my AI Employee to automatically post business updates to LinkedIn so that I can generate sales leads and build brand awareness without manual social media management.

**Why this priority**: Business value generator - transforms AI Employee from reactive task processor to proactive marketing assistant that drives revenue.

**Independent Test**: Can be fully tested by invoking LinkedIn posting skill with test content, verifying post is published to LinkedIn profile, and confirming action file tracking in /Done.

**Acceptance Scenarios**:
1. **Given** I have an approved business update in /Pending_Approval, **When** I invoke the LinkedIn poster skill, **Then** the post should be published to my LinkedIn profile with correct formatting (hashtags, mentions, media attachments)
2. **Given** the LinkedIn poster skill is invoked, **When** posting completes, **Then** an action file should be created in /Done with metadata: post_url, engagement_metrics (likes, comments), posting_timestamp
3. **Given** a post fails (network error, API rate limit), **When** the error occurs, **Then** the action file should be moved to /Errors with retry information and human should be notified

---

### User Story 3 - Plan.md Reasoning Loop (Priority: P1)

As a user, I want Claude Code to create Plan.md files that show the reasoning and step-by-step approach for complex tasks so that I can understand the AI's decision-making process and intervene if needed.

**Why this priority**: Transparency and control - transforms AI from black-box executor to transparent reasoning engine that documents its thought process, enabling human oversight and learning.

**Independent Test**: Can be fully tested by processing a complex action file (e.g., "organize client files by project"), verifying Plan.md is created with task breakdown, and confirming execution follows the plan.

**Acceptance Scenarios**:
1. **Given** a complex task arrives in /Needs_Action, **When** Claude Code processes it, **Then** a Plan.md file should be created in /Plans folder with: objective, step-by-step approach, estimated time, dependencies
2. **Given** Plan.md exists, **When** I review it, **Then** I should see clear reasoning for each step with alternatives considered and rationale for chosen approach
3. **Given** Plan.md is approved (file moved to /Approved), **When** execution proceeds, **Then** each completed step should be checked off in Plan.md with actual time vs estimated time

---

### User Story 4 - MCP Server Integration (Priority: P1)

As a user, I want one working MCP server for external actions (e.g., sending emails, posting to LinkedIn) so that my AI Employee can execute actions beyond file manipulation and integrate with external services.

**Why this priority**: Action layer expansion - enables AI Employee to interact with external systems (email, social media, APIs) instead of just managing local files, dramatically expanding useful automation scope.

**Independent Test**: Can be fully tested by invoking MCP server action (e.g., send email via Gmail MCP), verifying external action completes successfully, and confirming response is logged in action file.

**Acceptance Scenarios**:
1. **Given** Gmail MCP server is running, **When** task-processor skill invokes send_email action, **Then** email should be sent successfully with correct recipient, subject, body, and attachments
2. **Given** MCP server executes an action, **When** action completes, **Then** response should include: success status, external_id (message_id, post_id), timestamp, any returned data
3. **Given** MCP server encounters an error, **When** error occurs, **Then** error should be logged with: error_type, error_message, retry_possible (boolean), suggested_action

---

### User Story 5 - Human-in-the-Loop Approval Workflow (Priority: P1)

As a user, I want sensitive actions (emails, social media posts, financial decisions) to require my approval before execution so that I maintain control over business-critical communications and avoid AI mistakes.

**Why this priority**: Trust and safety - essential for business deployment where mistakes can damage reputation or incur financial liability. Approval workflow enables AI autonomy while maintaining human oversight.

**Independent Test**: Can be fully tested by processing an action requiring approval (email to client), verifying it moves to /Pending_Approval, manually approving, and confirming execution proceeds.

**Acceptance Scenarios**:
1. **Given** task-processor encounters an action requiring approval (email send, LinkedIn post), **When** action is processed, **Then** action file should be moved to /Pending_Approval folder with approval_request.md containing: action_summary, risk_level, approval_deadline
3. **Given** file is in /Pending_Approval, **When** I move it to /Approved, **Then** task-processor should execute the action immediately
4. **Given** file is in /Pending_Approval, **When** I move it to /Rejected, **Then** action file should be moved to /Done with rejection_reason and no action taken
5. **Given** approval deadline expires (default 24 hours), **When** deadline passes, **Then** system should notify human and mark as overdue

---

### User Story 6 - Scheduled Automation (Priority: P2)

As a user, I want my AI Employee to run scheduled tasks (e.g., daily briefing, weekly reports) via cron or Task Scheduler so that I get regular updates without manual triggering.

**Why this priority**: Convenience and regularity - transforms AI from on-demand tool to proactive assistant that delivers value on a schedule, reducing manual oversight.

**Independent Test**: Can be fully tested by scheduling a test task (e.g., create daily summary file), waiting for scheduled time, and verifying task executes and creates expected output.

**Acceptance Scenarios**:
1. **Given** I schedule a daily briefing task for 8:00 AM, **When** 8:00 AM arrives, **Then** task-processor should automatically run and create briefing file in /Done with: date, pending_tasks, recent_activity, recommendations
2. **Given** scheduled task is configured, **When** I check schedule configuration, **Then** I should see: task_name, schedule (cron expression or Task Scheduler trigger), last_run, next_run, status (enabled/disabled)
3. **Given** scheduled task fails, **When** failure occurs, **Then** error should be logged in /Logs/scheduled_tasks.log with: task_name, scheduled_time, failure_reason, retry_scheduled (boolean)

---

### Edge Cases

- **What happens when two watchers detect the same event simultaneously?** System should deduplicate based on event ID (message_id, file_hash) to prevent duplicate action files
- **What happens when MCP server is unreachable?** System should queue the action, retry with exponential backoff (3 attempts), then move to /Errors for manual intervention
- **What happens when approval workflow has 100+ pending files?** System should sort by priority (high/medium/low) and deadline (oldest first), show summary count in Dashboard
- **What happens when Plan.md execution diverges from plan?** System should log deviation in Plan.md, create new action file for unexpected steps, notify human if deviation >20% of estimated time
- **What happens when scheduled task overlaps with manual task processing?** System should queue scheduled task, process after current manual batch completes, log delay in scheduled_tasks.log
- **What happens when LinkedIn API rate limits are hit?** LinkedIn poster should implement exponential backoff, respect 429 responses, queue posts for retry, notify human of delay
- **What happens when approval request expires without human action?** System should send reminder notification, escalate priority, mark as overdue in Dashboard, auto-reject after 7 days (configurable)
- **What happens when MCP server returns partial success?** System should log partial results, create follow-up action file for incomplete portion, notify human of partial completion

---

## Requirements *(mandatory)*

### Functional Requirements

#### Multi-Watcher Orchestration (FR-001 to FR-010)

- **FR-001**: System MUST run 2 or more Watcher scripts concurrently (e.g., Gmail + File System + WhatsApp from Bronze tier options)
- **FR-002**: Each watcher MUST maintain independent check cycles and logging (watcher_name_YYYY-MM-DD.log)
- **FR-003**: Watchers MUST coordinate to prevent duplicate action files for the same event (deduplication by event_id)
- **FR-004**: System MUST support adding/removing watchers dynamically without restarting other watchers
- **FR-005**: Watchers MUST report health status to Dashboard: watcher_name, status (running/stopped/error), last_check_time, events_detected_today
- **FR-006**: System MUST handle watcher crashes gracefully: auto-restart by watchdog process, log crash reason, notify human
- **FR-007**: Gmail Watcher MUST continue using 2-5 minute check interval from Bronze tier
- **FR-008**: File System Watcher MUST continue using 30 second check interval from Bronze tier
- **FR-009**: WhatsApp Watcher (if chosen) MUST check for new messages every 30 seconds using WhatsApp Web API
- **FR-010**: System MUST scale to 6 watchers for Gold tier without architecture changes (Silver tier proves 2+ watcher capability)

#### LinkedIn Social Media Posting (FR-011 to FR-020)

- **FR-011**: System MUST integrate with LinkedIn API for posting business updates
- **FR-012**: LinkedIn poster MUST support post types: text-only, text with image, text with link, text with document
- **FR-013**: LinkedIn poster MUST validate post content before sending: character limits, hashtag format, mention syntax, media size limits
- **FR-014**: System MUST create action file for LinkedIn posts with metadata: post_type, content, media_attachments, scheduled_time (optional), target_audience (public/connections)
- **FR-015**: LinkedIn poster MUST require approval for all posts via /Pending_Approval workflow
- **FR-016**: LinkedIn poster MUST publish post and capture: post_url, post_id, publishing_timestamp
- **FR-017**: LinkedIn poster SHOULD track engagement metrics: likes, comments, shares (if API allows)
- **FR-018**: System MUST log LinkedIn posts in Company_Handbook.md for social media inventory tracking
- **FR-019**: LinkedIn poster MUST handle API errors: rate limits (429), authentication failures, media upload errors
- **FR-020**: System MUST support scheduled LinkedIn posts (queue for future posting at specified time)

#### Plan.md Reasoning Loop (FR-021 to FR-030)

- **FR-021**: System MUST create Plan.md files in /Plans folder for complex tasks (3+ steps or estimated time >15 minutes)
- **FR-022**: Plan.md MUST include: objective, task_description, step_numbered_list, estimated_time_per_step, total_estimated_time, dependencies, risks
- **FR-023**: Plan.md MUST document reasoning: why_this_approach, alternatives_considered, rationale_for_choice
- **FR-024**: Plan.md MUST be created BEFORE task execution begins (approval workflow for plan itself)
- **FR-025**: System MUST move Plan.md to /Approved when human approves (file movement)
- **FR-026**: During execution, system MUST update Plan.md: mark steps complete, log actual_time vs estimated_time, note deviations
- **FR-027**: If execution deviates >20% from plan, system MUST create new Plan.md addendum with: deviation_reason, revised_steps, human_notification
- **FR-028**: Completed plans MUST be archived to /Plans/archive/ with: completion_timestamp, success_criteria, lessons_learned
- **FR-029**: System SHOULD learn from past plans: extract patterns, suggest improvements for similar future tasks
- **FR-030**: Dashboard MUST show: active_plans (count), plans_completed_today, average_plan_accuracy (estimated vs actual time)

#### MCP Server Integration (FR-031 to FR-040)

- **FR-031**: System MUST implement at least one MCP server for external action (e.g., Gmail send MCP server)
- **FR-032**: MCP server MUST follow Model Context Protocol specification for tools, resources, prompts
- **FR-033**: MCP server MUST expose action methods: send_email, send_linkedin_post, read_calendar, etc.
- **FR-034**: MCP server MUST return structured responses: success (boolean), result_data, error_message (if failed), external_id
- **FR-035**: Task-processor skill MUST invoke MCP server actions instead of direct API calls
- **FR-036**: System MUST handle MCP server communication errors: timeout, connection refused, malformed response
- **FR-037**: MCP server MUST log all actions to /Logs/mcp_actions_YYYY-MM-DD.json with: action_type, input_params, output_result, timestamp
- **FR-038**: System MUST support MCP server restart without losing queued actions (persistent queue)
- **FR-039**: MCP server MUST validate input parameters before execution (e.g., email format, LinkedIn post length)
- **FR-040**: System architecture MUST support multiple MCP servers (Silver tier proves 1, Gold tier adds 6+)

#### Human-in-the-Loop Approval Workflow (FR-041 to FR-050)

- **FR-041**: System MUST create /Pending_Approval folder for human review before executing sensitive actions
- **FR-042**: Sensitive actions MUST include: sending emails, posting to social media, financial decisions >$100, data deletion, external API writes
- **FR-043**: System MUST create approval_request.md alongside action file with: action_summary, risk_level (high/medium/low), approval_deadline (default 24 hours), potential_impact
- **FR-044**: System MUST support three approval outcomes: /Approved (execute), /Rejected (cancel with reason), /Pending_Approval (still waiting)
- **FR-045**: When file moved to /Approved, task-processor MUST execute action immediately
- **FR-046**: When file moved to /Rejected, action file MUST move to /Done with: rejection_reason, rejected_by (human), rejection_timestamp
- **FR-047**: Dashboard MUST show: pending_approvals_count, approvals_today, rejections_today, oldest_pending_approval_age
- **FR-048**: System MUST send notification when approval deadline expires: email, Dashboard alert, or Obsidian notification
- **FR-049**: System MUST auto-reject approvals after 7 days overdue (configurable) with: auto_rejection_reason, overdue_duration
- **FR-050**: Company_Handbook.md MUST define approval_thresholds: which actions require approval, risk_levels, escalation_paths

#### Scheduled Automation (FR-051 to FR-058)

- **FR-051**: System MUST support scheduled tasks via cron (Linux/macOS) or Task Scheduler (Windows)
- **FR-052**: System MUST create /Scheduled/config.yaml with task definitions: task_name, schedule (cron/trigger), skill_to_invoke, parameters
- **FR-053**: Scheduled tasks MUST invoke Agent Skills with predefined parameters (e.g., /dashboard-updater --vault_path "/path/to/vault")
- **FR-054**: System MUST log scheduled task execution to /Logs/scheduled_tasks_YYYY-MM-DD.log with: task_name, scheduled_time, actual_time, status, output
- **FR-055**: Scheduled tasks MUST handle failures: log error, retry according to policy, notify human if critical failure
- **FR-056**: System MUST support schedule patterns: daily (specific time), weekly (specific day/time), hourly, on-demand (manual trigger)
- **FR-057**: Dashboard MUST show: scheduled_tasks_count, next_run_time, last_successful_run, failed_runs_today
- **FR-058**: Common scheduled tasks for Silver tier: daily status summary (8 AM), weekly inventory audit (Sunday 10 PM), monthly archive cleanup (1st of month)

#### Agent Skills Architecture (FR-059 to FR-065)

- **FR-059**: All new Silver tier functionality MUST be implemented as Agent Skills (SKILL.md files)
- **FR-060**: System MUST implement linkedin-poster skill for LinkedIn social media posting
- **FR-061**: System MUST implement plan-generator skill for creating Plan.md reasoning documents
- **FR-062**: System MUST implement approval-processor skill for managing /Pending_Approval workflow
- **FR-063**: System MUST extend task-processor skill to support MCP server actions
- **FR-064**: Each skill MUST include: skill name, description, input parameters, output format, usage examples, error handling
- **FR-065**: Skills MUST be reusable across Bronze → Silver → Gold tiers (backward compatibility maintained)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Core Functionality (SC-001 to SC-007)

- **SC-001**: Two or more watchers run concurrently for 24 hours without crashes or interference
- **SC-002**: 95% of events detected by watchers result in unique action files (successful deduplication)
- **SC-003**: LinkedIn posts publish successfully with 90% success rate (API failures handled gracefully)
- **SC-004**: Plan.md files are created for 100% of complex tasks (3+ steps or >15 minutes)
- **SC-005**: MCP server executes actions with 95% success rate and <5 second average response time
- **SC-006**: 100% of sensitive actions route through /Pending_Approval workflow (zero bypasses)
- **SC-007**: Scheduled tasks execute on time with <5 minute deviation from schedule

#### Business Value ROI (SC-008 to SC-013)

- **SC-008**: LinkedIn posting automation saves 2-3 hours per week on social media management
- **SC-009**: Multi-watcher coverage increases event detection rate by 200% compared to single watcher (Bronze tier)
- **SC-010**: Approval workflow prevents 100% of business-critical mistakes (zero unauthorized emails/posts)
- **SC-011**: Plan.md reasoning reduces task execution errors by 50% (transparent planning catches issues before execution)
- **SC-012**: Scheduled automation delivers daily briefings without manual triggering (zero effort daily updates)
- **SC-013**: MCP server integration expands automation scope by 500% (from file-only to external actions)

#### Quality & Reliability (SC-014 to SC-019)

- **SC-014**: System handles 100 action files per day across multiple watchers without performance degradation
- **SC-015**: Error rate remains below 5% (95% of tasks complete successfully)
- **SC-016**: All errors logged with sufficient detail for debugging and retry
- **SC-017**: System recovers automatically from transient failures (API timeout, network glitch) without human intervention
- **SC-018**: Approval workflow processes requests within 1 hour of human approval (instant execution)
- **SC-019**: Watcher health monitoring detects crashes within 60 seconds and triggers auto-restart

#### User Experience (SC-020 to SC-024)

- **SC-020**: Dashboard shows comprehensive status: all watchers, pending approvals, active plans, scheduled tasks
- **SC-021**: User can manually approve/reject actions in <30 seconds (file movement in Obsidian)
- **SC-022**: Plan.md documents are human-readable and understandable (non-technical stakeholders can follow reasoning)
- **SC-023**: Scheduled tasks provide clear output files (daily briefing, weekly audit) accessible in /Done
- **SC-024**: System configuration (watchers, schedules, MCP servers) is human-editable via YAML files

#### Scalability & Maintainability (SC-025 to SC-028)

- **SC-025**: System architecture supports adding 3rd, 4th, 5th watcher without code changes (configuration-only)
- **SC-026**: MCP server architecture supports adding 2nd, 3rd, 4th MCP server without refactoring
- **SC-027**: Plan.md templates are reusable for similar task types (email triage, file organization, report generation)
- **SC-028**: Approval workflow is extensible (new action types can require approval via Company_Handbook.md configuration)

---

## Key Entities *(include if feature involves data)*

- **Approval Request**: Action file in /Pending_Approval awaiting human decision
  - Attributes: action_file_reference, action_type, risk_level, approval_deadline, potential_impact, created_at, status (pending/approved/rejected/expired)
  - Relationships: References Action File from /Needs_Action, becomes Approved Action or Rejected Action

- **Plan**: Reasoning document for complex multi-step tasks
  - Attributes: plan_id, objective, task_description, steps (array), estimated_time, dependencies, risks, status (draft/approved/in_progress/completed/archived), actual_time, accuracy_metric
  - Relationships: Created by plan-generator skill, references Action File, updated during execution, archived to /Plans/archive/

- **MCP Server Action**: External action executed via Model Context Protocol server
  - Attributes: action_type, input_params, output_result, external_id, success (boolean), error_message, timestamp, retry_count
  - Relationships: Invoked by task-processor skill, logged in /Logs/mcp_actions_, creates/update Action Files

- **Scheduled Task**: Automated task execution on schedule (cron or Task Scheduler)
  - Attributes: task_name, schedule (cron expression or trigger), skill_to_invoke, parameters, last_run, next_run, status (enabled/disabled/failed), last_failure_reason
  - Relationships: Defined in /Scheduled/config.yaml, invokes Agent Skills, logs to /Logs/scheduled_tasks_

- **Watcher Health**: Status monitoring for concurrent watcher processes
  - Attributes: watcher_name, watcher_type (Gmail/FileSystem/WhatsApp), pid, status (running/stopped/error), last_check_time, events_detected_today, errors_today, uptime_seconds
  - Relationships: Monitored by orchestrator/watchdog, reported in Dashboard, logged to /Logs/watcher_

- **LinkedIn Post**: Social media content published to LinkedIn
  - Attributes: post_id, post_type (text/image/link/document), content, media_attachments, scheduled_time, published_time, post_url, engagement_metrics (likes/comments/shares), approval_status
  - Relationships: Created by linkedin-poster skill, requires approval via /Pending_Approval, tracked in Company_Handbook social media inventory

---

## Assumptions

### Environment Assumptions

- Bronze Tier (feature 000) is complete with: Obsidian vault structure, one working watcher, task-processor skill, Dashboard.md/Company_Handbook.md
- User has LinkedIn account with API access or LinkedIn automation tool (e.g., Playwright browser automation if API unavailable)
- User has cron (Linux/macOS) or Task Scheduler (Windows) available for scheduled automation
- System has sufficient resources for multiple concurrent watchers: 16GB RAM recommended (upgraded from Bronze 8GB), 4-core CPU

### Account & Service Assumptions

- LinkedIn account: Business account or personal profile with posting permissions
- If LinkedIn API unavailable: Use Playwright browser automation (manual login, cookie persistence)
- Gmail account: Continue using Bronze tier OAuth credentials
- WhatsApp: If WhatsApp Watcher chosen, WhatsApp Web with QR code authentication (manual initial setup)
- MCP server runtime: Node.js v24+ LTS or Python runtime for server process

### Data Assumptions

- Plan.md files are markdown with structured YAML frontmatter for metadata
- Approval requests expire after 24 hours default (configurable via Company_Handbook.md)
- Scheduled task logs rotate monthly (archive after 30 days)
- MCP server action logs persist for 180 days (audit trail for external actions)
- LinkedIn posts tracked indefinitely in Company_Handbook social media inventory

### Operational Assumptions

- Silver tier targets semi-autonomous operation: scheduled tasks run automatically, but approval workflow still requires human oversight
- Multi-watcher orchestrator manages watcher lifecycle: start, stop, restart, health monitoring
- Approval workflow expected response time: <24 hours for standard actions, <4 hours for urgent actions
- Scheduled tasks: daily briefing, weekly audit recommended but configurable by user

### Technical Assumptions

- Watchers run as independent processes (not threads) for isolation and crash resilience
- MCP server runs as separate process (external to watchers and Claude Code)
- Approval workflow uses file-based state machine (file movement = state transition)
- Plan.md generation uses Claude Code reasoning capabilities (no external planning service)
- Scheduled tasks use OS-native scheduling (cron/Task Scheduler) rather than custom scheduler

### Scope Boundaries

- Silver tier is single-user system (no multi-tenancy)
- No distributed system support (all watchers run on same machine)
- No cloud deployment (local-only as per Bronze tier local-first philosophy)
- No real-time push notifications (email/Dashboard alerts only)
- No machine learning or AI training (all reasoning is prompt-based, no model fine-tuning)
- No web-based dashboard (Obsidian GUI only)

---

## Dependencies

### External Services

- **LinkedIn API**: OAuth 2.0 access or Playwright browser automation
- **Gmail API**: Continue using Bronze tier credentials
- **WhatsApp Web API** (if WhatsApp Watcher chosen): WhatsApp Web automation
- **Claude API**: Continue using Bronze tier Claude Code access

### Software & Libraries

- **Python 3.13+**: Continue using Bronze tier runtime for watchers
- **Node.js v24+ LTS**: For MCP server implementation (if using official MCP SDK)
- **Playwright** (if LinkedIn API unavailable): Browser automation for LinkedIn posting
- **Python packages from Bronze tier**: pyyaml, python-frontmatter, watchdog, google-api-python-client
- **Additional Python packages**: schedule (cron-like scheduling in Python), psutil (process monitoring for watcher health)

### Internal Components

- **Bronze Tier Components** (Prerequisite): vault structure (Dashboard.md, Company_Handbook.md), task-processor skill, one working watcher, action file format
- **New Silver Tier Components**: approval-processor skill, linkedin-poster skill, plan-generator skill, MCP server, orchestrator for multi-watcher management

### Infrastructure

- **Local disk space**: Minimum 2GB (upgraded from Bronze 500MB) for Plan.md files, MCP action logs, approval history
- **RAM**: 16GB recommended (upgraded from Bronze 8GB) for multiple concurrent watchers + MCP server
- **Stable internet**: Required for LinkedIn posting, MCP server communication, WhatsApp Web (if chosen)

---

## Out of Scope

### Features Explicitly Excluded (Silver Tier)

- Full cross-domain integration (Personal + Business) → Gold Tier requirement
- Accounting system integration (Odoo/Xero) → Gold Tier requirement
- Facebook/Instagram posting → Gold Tier requirement
- Twitter/X posting → Gold Tier requirement
- Multiple MCP servers (6+) → Gold Tier requirement
- CEO Briefing generation → Gold Tier requirement
- Ralph Wiggum autonomous loop (stop hook pattern) → Gold Tier requirement
- Comprehensive audit logging (180-day retention) → Gold Tier requirement
- Orchestrator + Watchdog process management → Silver tier has basic health monitoring only, full orchestrator in Gold Tier
- 24/7 continuous operation → Silver tier targets work hours + scheduled tasks, not 24/7 monitoring

### Future Enhancements (Post-Silver)

- Multi-watcher load balancing (distribute events across multiple Claude Code instances)
- Approval workflow mobile app (currently file-based in Obsidian only)
- Plan.md template library (pre-built plans for common task types)
- Scheduled task web UI (currently YAML configuration only)
- MCP server marketplace (discover and install 3rd party MCP servers)
- Real-time collaboration (multi-user access to same vault)

### Technical Limitations

- No production-grade security (credentials still in plaintext .env, document as non-production)
- No database for Plan.md/Approval storage (all file-based)
- No distributed watcher support (all on same machine)
- No automatic failover for watcher crashes (manual restart or basic watchdog only)
- No version control for Plan.md revisions (no git integration)
- No backup/restore functionality (manual vault backup only)

---

## Risks & Mitigation

### High Severity Risks

1. **LinkedIn API rate limiting or account suspension**
   - **Impact**: LinkedIn posting blocked, social media automation fails
   - **Probability**: Medium (LinkedIn has strict API limits and automation policies)
   - **Mitigation**: Implement exponential backoff, respect 429 responses, use Playwright browser automation as fallback, post during off-peak hours, space posts >1 hour apart

2. **Multi-watcher resource exhaustion**
   - **Impact**: Watchers crash or become unresponsive, system degrades
   - **Probability**: Medium (2+ watchers + MCP server + Claude Code may exceed Bronze tier 8GB RAM)
   - **Mitigation**: Upgrade to 16GB RAM, implement watcher health monitoring with auto-restart, add resource usage limits per watcher, gracefully degrade if resources low

3. **Approval workflow bottleneck (100+ pending files)**
   - **Impact**: Human cannot keep up with approval volume, tasks stall
   - **Probability**: Low (Silver tier scale is 100 files/day, approval rate estimated 20-30%)
   - **Mitigation**: Prioritize by risk_level and deadline, Dashboard shows oldest pending first, auto-reject after 7 days, implement approval batching (approve all low-risk marketing emails at once)

### Medium Severity Risks

4. **MCP server communication failure**
   - **Impact**: External actions (email send, LinkedIn post) fail
   - **Probability**: Medium (network issues, server crashes, malformed requests)
   - **Mitigation**: Persistent action queue (survives MCP restart), retry with exponential backoff (3 attempts), move to /Errors for manual intervention after retries exhausted

5. **Plan.md execution divergence**
   - **Impact**: Task does not complete as planned, human expectations not met
   - **Probability**: Medium (unforeseen complications, dependencies not available)
   - **Mitigation**: Log deviations in real-time, create addendum Plan.md if deviation >20%, notify human if plan is no longer viable, archive lessons learned for future planning

6. **Scheduled task overlap**
   - **Impact**: Two tasks run simultaneously, resource conflict, inconsistent state
   - **Probability**: Low (scheduled tasks spaced out: daily briefing at 8 AM, weekly audit Sunday 10 PM)
   - **Mitigation**: Implement task queue for scheduled tasks, execute sequentially if overlap, log delay in scheduled_tasks.log, Dashboard shows task queue status

### Low Severity Risks

7. **Watcher deduplication misses duplicate events**
   - **Impact**: Duplicate action files created, wasted processing time
   - **Probability**: Low (event_id deduplication is reliable: message_id for emails, file_hash for files)
   - **Mitigation**: Deduplication by event_id (message_id, file_hash), log deduplication events, manual cleanup if duplicates slip through

8. **Plan.md files grow unbounded**
   - **Impact**: /Plans folder becomes cluttered, hard to find active plans
   - **Probability**: Medium (complex tasks generate Plans, completed plans archived)
   - **Mitigation**: Auto-archive completed plans to /Plans/archive/ monthly, implement Plan.md search via Dashboard, manual cleanup of draft/abandoned plans

9. **Approval deadline expires without human action**
   - **Impact**: Time-sensitive actions missed (e.g., urgent email not sent)
   - **Probability**: Low (approval workflow is lightweight: file movement in Obsidian)
   - **Mitigation**: Send reminder notifications (email, Dashboard alert), escalate priority as deadline approaches, auto-reject after 7 days (configurable), Dashboard shows overdue approvals prominently

---

## Implementation Notes

### Silver Tier Completion Checklist

This Silver Tier implementation builds on Bronze Tier foundation and adds functional assistant capabilities. Success means:

- ✅ Bronze Tier (feature 000) complete: vault structure, one watcher, task-processor skill
- ✅ Two or more watchers running concurrently (e.g., Gmail + File System)
- ✅ Multi-watcher orchestration: deduplication, health monitoring, coordinated logging
- ✅ LinkedIn posting skill with approval workflow: create post, approve, publish, track engagement
- ✅ Plan.md generation for complex tasks: objective, steps, reasoning, approval, execution tracking
- ✅ MCP server integration: one working MCP server (Gmail send or LinkedIn post), error handling, action logging
- ✅ Approval workflow: /Pending_Approval folder, approval_request.md, three outcomes (approved/rejected/expired)
- ✅ Scheduled automation: cron or Task Scheduler setup, daily briefing, weekly audit
- ✅ Dashboard enhancements: watcher status, pending approvals, active plans, scheduled tasks
- ✅ End-to-end test: multi-watcher event detection → action file → plan generation (if complex) → approval (if sensitive) → execution → done
- ✅ Documentation: Silver Tier README.md, architecture updates, lessons learned

### Recommended Implementation Order

1. **Phase 1 - Multi-Watcher Setup** (4-5 hours)
   - Add second watcher (e.g., WhatsApp or second File System location)
   - Implement watcher orchestrator for health monitoring
   - Add deduplication logic (event_id matching)
   - Update Dashboard to show all watcher statuses
   - Test: Run both watchers 1 hour, verify no crashes, check logs

2. **Phase 2 - Approval Workflow** (3-4 hours)
   - Create /Pending_Approval folder structure
   - Implement approval-processor skill
   - Add approval_request.md generation
   - Extend task-processor skill to check /Pending_Approval before executing sensitive actions
   - Update Dashboard with pending approvals count
   - Test: Process action requiring approval, verify routing to /Pending_Approval, approve manually, verify execution

3. **Phase 3 - MCP Server Integration** (5-6 hours)
   - Choose first MCP server (Gmail send recommended - builds on Bronze Gmail API)
   - Implement MCP server following Model Context Protocol spec
   - Extend task-processor skill to invoke MCP actions instead of direct API calls
   - Add MCP action logging (/Logs/mcp_actions_YYYY-MM-DD.json)
   - Test: Invoke MCP send_email action, verify email sent, check logs

4. **Phase 4 - LinkedIn Posting** (4-5 hours)
   - Implement LinkedIn API integration or Playwright browser automation
   - Create linkedin-poster skill with post validation
   - Integrate with approval workflow (all posts require approval)
   - Add LinkedIn post tracking to Company_Handbook.md
   - Test: Create test post, approve, publish, verify post on LinkedIn, check engagement metrics

5. **Phase 5 - Plan.md Generation** (3-4 hours)
   - Create plan-generator skill
   - Add Plan.md template with: objective, steps, reasoning, estimates
   - Integrate with task-processor: create plan for complex tasks (3+ steps or >15 min)
   - Add plan approval workflow (move to /Approved to execute)
   - Test: Process complex task (e.g., "organize client files"), verify Plan.md created, approve, verify execution follows plan

6. **Phase 6 - Scheduled Automation** (2-3 hours)
   - Set up cron (Linux/macOS) or Task Scheduler (Windows)
   - Create /Scheduled/config.yaml with task definitions
   - Implement daily briefing scheduled task
   - Implement weekly audit scheduled task
   - Add scheduled task logging (/Logs/scheduled_tasks_YYYY-MM-DD.log)
   - Test: Schedule test task for 1 minute in future, verify execution, check logs

7. **Phase 7 - Testing & Documentation** (2-3 hours)
   - End-to-end integration test: all Silver Tier features working together
   - Verify all success criteria from spec.md
   - Update README.md with Silver Tier setup instructions
   - Document architecture and lessons learned
   - Record demo video showing multi-watcher → approval → LinkedIn posting → scheduled task

**Total Estimated Time**: 20-30 hours (aligns with Silver Tier estimate)

### Key Technical Decisions

1. **Two Watchers Minimum**: Silver tier requires 2+ watchers (Bronze had 1). Recommended: Gmail + File System (Bronze foundation) + add WhatsApp or LinkedIn. Proves multi-watcher orchestration before Gold tier's 6 watchers.

2. **LinkedIn as First Social Platform**: Silver tier adds LinkedIn posting. Gold tier adds Facebook/Instagram/Twitter. LinkedIn chosen first: business-oriented, B2B lead generation, better API access than Facebook/Instagram.

3. **MCP Server for External Actions**: Silver tier proves MCP architecture with 1 server. Gold tier scales to 6+ servers. Gmail send MCP server recommended (builds on Bronze Gmail API, low risk). Alternative: LinkedIn post MCP server.

4. **Approval Workflow File-Based**: Continue using file movement (/Pending_Approval → /Approved → /Rejected) instead of database. Maintains Bronze tier simplicity, works in Obsidian GUI, human-friendly.

5. **Plan.md for Complex Tasks Only**: Not every task needs a plan. Threshold: 3+ steps OR estimated time >15 minutes. Simple tasks (read email, categorize file) execute directly without plan. Prevents plan bloat.

6. **Scheduled Tasks via OS-Native Tools**: Use cron (Linux/macOS) or Task Scheduler (Windows) instead of custom Python scheduler. More reliable, survives restarts, OS-managed. Silver tier proves concept, Gold tier may add custom scheduler for orchestrator.

7. **Watcher Health Monitoring**: Basic health checks in Silver tier (status in Dashboard, auto-restart on crash). Full orchestrator + watchdog in Gold tier. Silver tier: Manual or simple script to check watcher processes and restart if needed.

### Architecture Validation

Silver Tier must prove these principles (beyond Bronze tier):

1. ✅ **Multi-watcher coordination works**: 2+ watchers run concurrently without interference, deduplication prevents duplicate action files
2. ✅ **Approval workflow enables safe automation**: 100% of sensitive actions route through /Pending_Approval, zero bypasses, human maintains control
3. ✅ **MCP server architecture scales**: 1 MCP server works reliably, adding 2nd/3rd server in Gold tier is straightforward (no architectural changes needed)
4. ✅ **Plan.md improves task execution**: Complex tasks with plans have 50% fewer errors than tasks without plans, plans are human-readable and auditable
5. ✅ **Scheduled automation delivers value**: Daily briefings arrive without manual triggering, scheduled tasks reduce manual oversight by 80%

**Failure Criteria**: If any principle fails validation during Silver Tier implementation, Gold tier will compound the problems. Silver is the functional bridge between Bronze (MVP) and Gold (fully autonomous).

---

## Upgrade Path to Gold Tier

Silver tier intentionally excludes features deferred to Gold tier. Clear upgrade path:

**Gold Tier Additions** (on top of Silver):
- Add 4 more watchers (total 6): WhatsApp, Xero, Calendar, Slack → full cross-domain integration
- Implement orchestrator + watchdog for comprehensive health monitoring and auto-restart
- Add Ralph Wiggum autonomous loop (stop hook pattern) for multi-step task completion without human intervention
- Add 5 more MCP servers (total 6): Xero accounting, Facebook posting, Instagram posting, Twitter posting, Calendar integration
- Implement comprehensive audit logging (180-day retention for all actions)
- Add CEO Briefing generation skill (weekly business audit + financial summary)
- Integrate accounting system (Odoo Community or Xero) via MCP server
- Implement error recovery and graceful degradation (continue processing when one component fails)

**Architecture Continuity**: Bronze validates core pipeline (single watcher, manual processing). Silver adds multi-watcher + MCP servers + approval workflow + planning. Gold adds orchestration + audit + business intelligence. Each tier builds incrementally on proven foundation.

---

**Next Steps After Silver Tier**:
- Proceed to Gold Tier specification for full autonomous employee (6 watchers, orchestrator, audit logging, CEO briefing)
- Evaluate lessons learned from Silver tier implementation
- Identify bottlenecks and optimization opportunities
- Consider which additional watchers provide most value for business use case
