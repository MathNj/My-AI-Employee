# Feature Specification: Gold Tier Personal AI Employee

**Feature Branch**: `002-gold-tier-ai-employee`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "Gold Tier Personal AI Employee - Autonomous Digital FTE with full cross-domain integration, Xero accounting, multi-platform social media, Ralph Wiggum loop, comprehensive audit logging, and 24/7 orchestrated watchers"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autonomous Email Monitoring and Response Drafting (Priority: P1)

As a busy business owner, I need my AI Employee to continuously monitor my Gmail inbox for important emails and automatically create draft responses, so that I can quickly review and approve them without spending hours in my inbox.

**Why this priority**: Email is the primary communication channel for most businesses. Unread important emails can lead to lost opportunities, delayed responses to clients, and missed deadlines. This is the foundation of the Digital FTE value proposition.

**Independent Test**: Can be fully tested by sending test emails to the monitored Gmail account, verifying that the Gmail Watcher detects them within 2 minutes, creates action files in /Needs_Action with proper YAML frontmatter, and that these files contain accurate email metadata (sender, subject, snippet).

**Acceptance Scenarios**:

1. **Given** I have configured Gmail OAuth credentials and the Gmail Watcher is running, **When** an unread important email arrives in my inbox, **Then** the watcher creates an `EMAIL_[id].md` file in /Needs_Action within 2 minutes with complete email metadata
2. **Given** an email action file exists in /Needs_Action, **When** I invoke Claude Code to process it, **Then** Claude reads the email, consults Company_Handbook.md for tone/style rules, and creates a draft response in /Pending_Approval
3. **Given** a draft email response in /Pending_Approval, **When** I review and move it to /Approved, **Then** the approval processor sends the email via Gmail MCP and moves all related files to /Done with a complete audit log entry

---

### User Story 2 - Financial Event Detection and Invoice Management (Priority: P1)

As a business owner using Xero for accounting, I need my AI Employee to automatically detect new invoices, overdue invoices, payments, and large transactions, creating actionable tasks and draft communications, so that I never miss a financial deadline or opportunity.

**Why this priority**: Financial management is critical for business survival. Late invoice follow-ups lead to cash flow problems, and missed payments damage vendor relationships. This directly contributes to the "Monday Morning CEO Briefing" value proposition.

**Independent Test**: Can be fully tested by creating test invoices/bills in Xero (or using the Xero sandbox API), verifying that the Xero Watcher detects them within 5 minutes, and creates properly formatted action files with financial data and suggested actions.

**Acceptance Scenarios**:

1. **Given** the Xero Watcher is running with valid OAuth credentials, **When** a new invoice is created in Xero, **Then** the watcher creates `xero_new_invoice_[timestamp].md` in /Needs_Action within 5 minutes with invoice details (customer, amount, due date)
2. **Given** an invoice becomes overdue (7+ days past due date), **When** the Xero Watcher runs its next check, **Then** it creates an urgent priority action file with "overdue" flag and suggested follow-up email text
3. **Given** a transaction over $500 is detected, **When** the Xero Watcher processes it, **Then** it creates a high-priority alert file flagged for human review before any action is taken
4. **Given** a payment is received, **When** the Xero Watcher detects it, **Then** it logs the transaction, updates cash flow tracking in Dashboard.md, and moves the related invoice file to /Done

---

### User Story 3 - Multi-Platform Social Media Posting with Approval Workflow (Priority: P2)

As a business owner, I need my AI Employee to generate social media posts for LinkedIn, Facebook, Instagram, and Twitter/X based on business achievements or scheduled campaigns, present them for approval, and post them automatically once approved, so that I maintain consistent online presence without manual posting.

**Why this priority**: Social media presence drives lead generation and brand awareness, but manual posting is time-consuming. This is a key differentiator for Silver → Gold tier progression.

**Independent Test**: Can be fully tested by triggering the social-media-manager skill, verifying it generates posts in the correct format for each platform, creates approval files with preview content, and successfully posts to test accounts once files are moved to /Approved.

**Acceptance Scenarios**:

1. **Given** I have a business achievement to announce, **When** I provide the achievement details to the AI Employee, **Then** it generates platform-specific posts (LinkedIn professional tone, Instagram visual-focused, Twitter concise, Facebook community-oriented) in /Pending_Approval
2. **Given** social media post drafts exist in /Pending_Approval, **When** I review and edit them (if needed) and move to /Approved, **Then** the approval processor posts each to the correct platform via respective MCP servers within 5 minutes
3. **Given** posts have been published, **When** the approval processor completes, **Then** it logs all post IDs, timestamps, and platform confirmation in /Logs and moves approval files to /Done
4. **Given** a post fails to publish (API error, rate limit, auth issue), **When** the error occurs, **Then** the system moves the file to /Failed with error details and alerts the user via Dashboard.md update

---

### User Story 4 - WhatsApp Urgent Message Detection (Priority: P2)

As a business owner who uses WhatsApp for client communication, I need my AI Employee to monitor WhatsApp Web for messages containing urgent keywords (urgent, ASAP, invoice, payment, help, emergency) and create high-priority action files, so that I respond to time-sensitive client requests quickly.

**Why this priority**: WhatsApp is a critical communication channel for many businesses, especially for urgent client matters. Missing an urgent WhatsApp message can damage client relationships or lose sales opportunities.

**Independent Test**: Can be fully tested by sending test WhatsApp messages containing urgent keywords to the monitored account, verifying that the WhatsApp Watcher detects them within 30 seconds and creates action files with "urgent" priority flag.

**Acceptance Scenarios**:

1. **Given** the WhatsApp Watcher is running with an authenticated session, **When** a message arrives containing any urgent keyword (urgent, ASAP, invoice, payment, help, emergency), **Then** the watcher creates `whatsapp_urgent_[timestamp].md` in /Needs_Action within 30 seconds
2. **Given** a WhatsApp urgent message file exists, **When** Claude Code processes it, **Then** it recognizes the urgency, creates a high-priority response plan, and flags it in Dashboard.md for immediate human attention
3. **Given** the WhatsApp session expires or browser connection fails, **When** the Watchdog detects the failure, **Then** it logs the error, attempts to restart the watcher, and alerts the user if restart fails after 3 attempts

---

### User Story 5 - Autonomous Multi-Step Task Completion with Ralph Wiggum Loop (Priority: P1)

As a business owner, I need my AI Employee to work autonomously on multi-step tasks (like "Process all invoices in /Needs_Action") without requiring me to prompt it after each step, so that tasks are completed end-to-end while I focus on high-value work.

**Why this priority**: This is the core differentiator between a "smart assistant" and a "Digital FTE". Without autonomous persistence, the AI requires constant human prompting, defeating the purpose of automation. This is a Gold Tier requirement.

**Independent Test**: Can be fully tested by placing multiple task files in /Needs_Action, invoking the Ralph Wiggum loop with a completion criteria (e.g., "all files moved to /Done"), and verifying that Claude continues working through all tasks without additional human prompts until the criteria is met or max iterations reached.

**Acceptance Scenarios**:

1. **Given** multiple task files exist in /Needs_Action and the Ralph loop is initiated, **When** Claude processes one task and attempts to exit, **Then** the Stop hook detects incomplete work, blocks the exit, re-injects the prompt with previous output visible, and Claude continues to the next task
2. **Given** the Ralph loop is running, **When** all tasks are moved to /Done (file movement completion strategy), **Then** the Stop hook allows Claude to exit gracefully and logs the completion with total iteration count and time elapsed
3. **Given** the Ralph loop encounters the same error 3 times consecutively, **When** the stuck detection triggers, **Then** it escalates to human review by creating an alert file, stops the loop, and logs the error pattern
4. **Given** the Ralph loop reaches max iterations (default 10) or max duration (default 30 minutes), **When** the safety limit is hit, **Then** it stops execution, logs remaining incomplete tasks, and reports status to Dashboard.md

---

### User Story 6 - Weekly CEO Briefing with Business Audit (Priority: P2)

As a business owner, I need my AI Employee to autonomously generate a comprehensive weekly CEO briefing every Sunday at 7:00 AM, analyzing revenue vs targets, completed tasks, bottlenecks, and proactive suggestions (like unused subscriptions to cancel), so that I start my Monday with complete business visibility.

**Why this priority**: This transforms the AI from reactive assistant to proactive business partner. The "Monday Morning CEO Briefing" is a standout feature that demonstrates true Digital FTE value. This is a Gold Tier requirement.

**Independent Test**: Can be fully tested by manually triggering the ceo-briefing-generator skill (or waiting for the scheduled Sunday 7 AM run), verifying it reads data from Xero, /Done folder, /Needs_Action, /Logs, and Business_Goals.md, generates a complete briefing in /Briefings folder with all required sections populated.

**Acceptance Scenarios**:

1. **Given** it's Sunday at 7:00 AM, **When** the scheduled task triggers, **Then** the ceo-briefing-generator skill runs automatically and generates `YYYY-MM-DD_Monday_Briefing.md` in /Briefings
2. **Given** the briefing is being generated, **When** the skill analyzes the past 7 days, **Then** it includes: Executive Summary (2-3 sentences), Weekly Revenue (total + MTD vs target + trend), Completed Tasks (count by category + major milestones), Bottlenecks (tasks taking longer than expected + recommended solutions), and Proactive Suggestions (unused subscriptions, cost optimization, upcoming deadlines)
3. **Given** the briefing includes subscription audit data, **When** a subscription has no usage in 30+ days or cost increased >20%, **Then** it's flagged with specific cancellation/downgrade recommendation and estimated annual savings
4. **Given** the briefing is complete, **When** saved to /Briefings, **Then** Dashboard.md is updated with a link to the latest briefing and a notification flag

---

### User Story 7 - Calendar Event Preparation and Reminders (Priority: P3)

As a business owner with a busy schedule, I need my AI Employee to monitor my Google Calendar for upcoming events (1-48 hours ahead) and create preparation reminders with context, so that I'm always prepared for meetings and never miss important appointments.

**Why this priority**: Calendar management is valuable but less critical than financial/communication monitoring. This provides quality-of-life improvement and demonstrates cross-domain integration.

**Independent Test**: Can be fully tested by creating test calendar events (1-48 hours from now) in Google Calendar, verifying that the Calendar Watcher detects them within 10 minutes and creates action files with event details and preparation suggestions.

**Acceptance Scenarios**:

1. **Given** the Calendar Watcher is running with authenticated Google Calendar access, **When** an event is scheduled 1-48 hours in the future, **Then** the watcher creates `CALENDAR_[event_id]_[timestamp].md` in /Needs_Action within 10 minutes
2. **Given** a calendar event action file exists, **When** Claude processes it, **Then** it includes event details (title, time, location, attendees) and generates context-aware preparation suggestions based on event type and attendees
3. **Given** an event is modified or cancelled, **When** the Calendar Watcher detects the change on its next check, **Then** it updates or removes the corresponding action file and logs the change

---

### User Story 8 - Slack Team Communication Monitoring (Priority: P3)

As a business owner managing a team, I need my AI Employee to monitor specific Slack channels for keyword matches (urgent, important, help, issue, problem) and create action files for messages requiring my attention, so that I don't miss critical team communications.

**Why this priority**: Valuable for team collaboration but less critical than client-facing communication. This demonstrates the system's flexibility to monitor multiple communication channels.

**Independent Test**: Can be fully tested by posting test messages with keywords to the monitored Slack channel, verifying that the Slack Watcher detects them within 1 minute and creates action files with message content and channel context.

**Acceptance Scenarios**:

1. **Given** the Slack Watcher is running with valid bot token and channel access, **When** a message containing a monitored keyword is posted, **Then** the watcher creates `slack_keyword_match_[timestamp].md` in /Needs_Action within 1 minute
2. **Given** a Slack action file includes message context (sender, channel, timestamp, thread), **When** Claude processes it, **Then** it analyzes whether the message requires immediate response, escalation, or just awareness
3. **Given** the same keyword is mentioned multiple times in a thread, **When** the Slack Watcher processes it, **Then** it consolidates into a single action file (not duplicate files) with thread context

---

### User Story 9 - File System Drop Zone Processing (Priority: P3)

As a business owner, I need to be able to drag-and-drop files (invoices, documents, contracts) into an Inbox folder and have my AI Employee automatically detect them in real-time and create action files for processing, so that I can easily add new tasks without using a complex interface.

**Why this priority**: Provides a simple, intuitive interface for adding tasks. Less critical than automated monitoring but enhances usability and demonstrates file handling capability.

**Independent Test**: Can be fully tested by copying various file types (PDF, DOCX, images) into the AI_Employee_Vault/Inbox folder and verifying that the Filesystem Watcher immediately detects them and creates action files with file metadata.

**Acceptance Scenarios**:

1. **Given** the Filesystem Watcher is running, **When** a file is added to AI_Employee_Vault/Inbox, **Then** the watcher immediately creates `FILE_[timestamp]_[filename].md` in /Needs_Action with file metadata (name, size, type)
2. **Given** a file action file exists, **When** Claude processes it, **Then** it analyzes the file type and suggests appropriate actions (e.g., "Invoice detected: extract details and create Xero entry" or "Contract detected: flag for legal review")
3. **Given** the Inbox folder accumulates many processed files, **When** files have been successfully processed, **Then** the watcher (or a cleanup task) moves them to an Archive subfolder to prevent re-detection

---

### User Story 10 - Comprehensive Audit Logging for All Actions (Priority: P1)

As a business owner, I need every action my AI Employee takes (emails sent, social posts published, financial transactions logged, file operations) to be recorded in a structured audit log with timestamp, actor, target, parameters, and result, so that I have complete visibility and accountability for a 90-day retention period.

**Why this priority**: Audit logging is non-negotiable for any system with autonomous capabilities. This is essential for troubleshooting, security, compliance, and trust. This is a Gold Tier requirement.

**Independent Test**: Can be fully tested by triggering various actions (send email, post social media, create file) and verifying that each generates a corresponding JSON log entry in /Logs/YYYY-MM-DD.json with all required fields populated.

**Acceptance Scenarios**:

1. **Given** the audit logging system is active, **When** any MCP server executes an action (email sent, social post published), **Then** it logs a JSON entry in /Logs/[date].json with fields: timestamp (ISO 8601), action_type, actor, target, parameters (object), approval_status, result, file_created
2. **Given** a Watcher detects an external event, **When** it creates an action file, **Then** it logs a "watcher_activity" entry with detection timestamp, source (gmail/xero/whatsapp/etc), event_type, and file_path
3. **Given** logs accumulate over time, **When** logs reach 90 days old, **Then** an automated cleanup task archives logs older than 90 days to an Archive folder and optionally compresses them
4. **Given** any action fails (API error, auth failure, timeout), **When** the error occurs, **Then** it logs an "error" entry with error message, stack trace (if applicable), retry count, and recovery action taken

---

### Edge Cases

- **What happens when multiple watchers detect related events simultaneously?** (e.g., Gmail detects an invoice email and Xero detects the same invoice creation): The system creates both action files independently. Claude Code should recognize duplicates during processing and consolidate them into a single plan, logging the deduplication action.

- **What happens when Xero OAuth token expires mid-operation?** The Xero Watcher catches the 401 Unauthorized error, attempts to refresh the token using the refresh token (valid for 60 days), logs the refresh attempt, and retries the operation. If refresh fails, it logs an authentication error, pauses the watcher, and creates an alert in Dashboard.md for user to re-authenticate.

- **What happens when WhatsApp Web session is logged out remotely?** The WhatsApp Watcher detects the logout (QR code page appears), logs the session loss, and creates an alert file in /Needs_Action instructing the user to re-scan QR code. The Watchdog continues attempting restarts but cannot recover without human intervention.

- **What happens when the vault is locked or Obsidian is actively syncing?** Watchers catch file write errors, retry with exponential backoff (1s, 2s, 4s up to 60s), and if still failing after 3 attempts, write to a temporary buffer file in /Logs/temp/ and attempt to flush when vault becomes available.

- **What happens when the system is offline and misses scheduled tasks?** On startup, the Orchestrator checks for missed scheduled tasks (like Sunday CEO briefing) by comparing current time against schedule config. If a task was missed within the last 6 hours, it triggers immediately. If missed by more than 6 hours, it logs a "missed_schedule" event and waits for the next occurrence.

- **What happens when Claude Code reaches context window limits with many large files?** The task-processor skill implements intelligent file prioritization: high-priority files first, summarizes very long files (>5000 lines), and processes in batches of max 10 files per reasoning loop to stay within context limits.

- **What happens when the same approval file is moved to both /Approved and /Rejected?** The approval-processor uses file system watchers with atomic operations. The first directory change is detected and processed, the file is immediately moved to /Done or /Rejected, making the second operation fail with "file not found" which is logged as a race condition.

- **What happens when social media API rate limits are hit?** MCP servers catch rate limit errors (HTTP 429), extract the retry-after header, and queue the post for retry after the specified time. The system logs the rate limit event and updates the approval file status to "queued_retry" with expected retry time.

- **What happens when a large transaction is detected but the vendor is not in the approved vendor list?** The Xero Watcher flags the transaction with both "large_transaction" (>$500) and "unknown_vendor" alerts, creates a high-priority approval file requiring explicit vendor verification, and includes a checkbox in the approval file: "□ I confirm this vendor is legitimate and approved for payment."

- **What happens when Ralph Wiggum loop gets stuck on a file that cannot be processed?** After 3 consecutive failed attempts on the same file, the loop moves that file to /Failed with error details, logs the failure, continues processing remaining files, and includes the failed file count in the final summary.

## Requirements *(mandatory)*

### Functional Requirements

**Watcher Layer (Perception)**

- **FR-001**: System MUST run 6 independent Watcher scripts continuously: Gmail Watcher (check every 2 min), WhatsApp Watcher (30 sec), Xero Watcher (5 min), Calendar Watcher (10 min), Slack Watcher (1 min), Filesystem Watcher (real-time)
- **FR-002**: Each Watcher MUST use OAuth 2.0 authentication (where applicable: Gmail, Xero, Calendar, Slack) with automatic token refresh and secure credential storage outside the Obsidian vault
- **FR-003**: Watchers MUST create structured markdown files in /Needs_Action with YAML frontmatter including: type, source, priority (urgent/high/medium/low), status (pending), timestamp (ISO 8601), and human-readable content body
- **FR-004**: Watchers MUST persist processed item IDs to prevent duplicate detection (e.g., gmail_processed_ids.json, xero_processed_transactions.json)
- **FR-005**: WhatsApp Watcher MUST run in visible browser mode (not headless) and persist the authenticated session across restarts
- **FR-006**: Xero Watcher MUST detect and create action files for: new invoices, overdue invoices (7+ days), new bills, payments received, and transactions over $500
- **FR-007**: Gmail Watcher MUST filter for "unread important" emails only (not all unread) to reduce noise
- **FR-008**: Filesystem Watcher MUST monitor AI_Employee_Vault/Inbox folder using real-time file system events (not polling)

**Orchestration Layer (Process Management)**

- **FR-009**: System MUST provide an Orchestrator.py master process that launches and monitors all 6 Watchers as child processes
- **FR-010**: Orchestrator MUST perform health checks every 60 seconds on all child processes and automatically restart any crashed Watcher
- **FR-011**: System MUST provide a Watchdog.py process that monitors the Orchestrator itself and restarts it if it crashes
- **FR-012**: System MUST provide orchestrator_cli.py with commands: status (show all running processes), stop (gracefully terminate all), restart (stop + start)
- **FR-013**: Orchestrator MUST read configuration from orchestrator_config.json allowing individual Watchers to be enabled/disabled and check intervals to be overridden
- **FR-014**: System MUST support auto-start on Windows login via Task Scheduler (configured by setup_auto_start.bat)
- **FR-015**: All Watcher and Orchestrator processes MUST log to individual log files in watchers/ directory with daily rotation

**Reasoning Layer (Claude Code Integration)**

- **FR-016**: System MUST implement all AI functionality as Claude Code Agent Skills located in .claude/skills/ directory
- **FR-017**: System MUST provide task-processor skill that reads files from /Needs_Action, consults Company_Handbook.md for rules, and creates Plan.md files in /Plans
- **FR-018**: System MUST provide approval-processor skill that monitors /Approved folder and executes approved actions via appropriate MCP servers
- **FR-019**: System MUST provide dashboard-updater skill that refreshes Dashboard.md with current system status, recent activity, and pending tasks
- **FR-020**: System MUST provide ceo-briefing-generator skill that runs every Sunday 7:00 AM, analyzes data from Xero + /Done + /Logs + Business_Goals.md, and generates briefing in /Briefings folder
- **FR-021**: System MUST implement Ralph Wiggum loop pattern using a Stop hook that blocks Claude exit until completion criteria is met (file moved to /Done or promise tag detected)
- **FR-022**: Ralph loop MUST have safety limits: max iterations (configurable, default 10), max duration (default 30 min), stuck detection (same error 3x = escalate)
- **FR-023**: Claude Code MUST consult Company_Handbook.md v2.1 for all decision-making, including: response tone/style, approval thresholds, priority keywords, security rules

**Action Layer (MCP Servers)**

- **FR-024**: System MUST provide gmail-mcp server for sending emails with OAuth authentication
- **FR-025**: System MUST provide xero-mcp server for reading/writing Xero data with OAuth 2.0 and 30-minute token refresh
- **FR-026**: System MUST provide linkedin-mcp server for posting to LinkedIn with approval workflow
- **FR-027**: System MUST provide x-poster (Twitter/X) MCP using Playwright browser automation (not API) with persistent session
- **FR-028**: System MUST provide facebook-mcp and instagram-mcp for posting to respective platforms
- **FR-029**: System MUST provide social-media-manager skill that coordinates multi-platform posting with unified approval workflow
- **FR-030**: All MCP servers MUST never execute directly from Watchers - execution only via approval-processor after human approval

**Human-in-the-Loop Approval Workflow**

- **FR-031**: System MUST route all sensitive actions (emails, social posts, payments) through /Pending_Approval folder with structured markdown files
- **FR-032**: Approval files MUST include: action details, context/reason, impact if approved, clear instructions ("Move to /Approved to proceed, /Rejected to cancel")
- **FR-033**: System MUST monitor /Approved folder continuously (approval-processor checks every 5 minutes or real-time file watcher)
- **FR-034**: System MUST move executed actions to /Done with timestamp and success status, or to /Failed with error details
- **FR-035**: Gold Tier default: ALL emails and social posts require approval (even to known contacts) - zero auto-send threshold
- **FR-036**: System MUST never auto-approve payments, file deletions, or actions to new/unknown contacts regardless of amount

**Audit Logging & Monitoring**

- **FR-037**: System MUST log every action to /Logs/YYYY-MM-DD.json in structured format with: timestamp (ISO 8601), action_type, actor, target, parameters (object), approval_status, result, file_created
- **FR-038**: System MUST categorize logs: watcher_activity, file_operations, approval_requests, external_actions (MCP calls), errors, system_health
- **FR-039**: System MUST redact PII from logs: email content (log metadata only), payment account numbers (log amounts/references), phone numbers, passwords
- **FR-040**: System MUST retain logs for 90 days, then archive or delete per configured policy
- **FR-041**: Dashboard.md MUST be updated automatically: on system startup, hourly, and after any significant event (approval processed, error occurred)
- **FR-042**: Dashboard.md MUST show: system status (watchers running/stopped), recent activity (last 10 actions), pending approvals count, pending tasks count, errors/alerts

**Folder Structure & File Management**

- **FR-043**: System MUST maintain folder structure: /Inbox (drop zone), /Needs_Action (active tasks), /Plans (execution plans), /Pending_Approval, /Approved, /Rejected, /Done (completed), /Failed (errors), /Logs (audit trail), /Briefings (CEO reports)
- **FR-044**: System MUST move files atomically between folders to prevent race conditions or partial moves
- **FR-045**: System MUST timestamp all generated filenames using ISO 8601 format: YYYY-MM-DDTHH-MM-SS or YYYYMMDD_HHMMSS
- **FR-046**: System MUST clean up /Done folder: archive files older than 30 days to /Done/Archive/YYYY-MM to prevent folder bloat

**Cross-Domain Integration**

- **FR-047**: System MUST integrate Personal domain (Gmail, WhatsApp, Calendar) and Business domain (Xero accounting, Slack team, social media) in a unified workflow
- **FR-048**: System MUST correlate related events across domains: if Gmail detects invoice email AND Xero detects invoice creation, consolidate into single plan
- **FR-049**: Business_Goals.md MUST define: revenue targets, KPIs, active projects, alert thresholds, subscription audit rules
- **FR-050**: CEO briefing MUST cross-reference data: compare weekly revenue (Xero) against targets (Business_Goals.md), analyze completed tasks (/Done) vs project deadlines (Business_Goals.md)

**Error Handling & Recovery**

- **FR-051**: System MUST categorize errors: Transient (retry with exponential backoff), Authentication (alert human + pause), Logic (human review queue), Data (quarantine), System (watchdog restart)
- **FR-052**: System MUST retry transient errors (network timeout, API rate limit) max 3 attempts with exponential backoff (1s, 2s, 4s base delay, max 60s)
- **FR-053**: System MUST never retry automatically: payment operations, email sends (could duplicate), social posts, file deletions
- **FR-054**: System MUST gracefully degrade when services unavailable: Gmail API down → queue emails locally; Xero timeout → log event, retry next cycle; WhatsApp Web unavailable → pause watcher, alert human, retry hourly
- **FR-055**: System MUST verify Watcher processes running every 5 minutes; alert if: process crashed, no activity for 30 minutes, repeated errors (3x same error)

**Security & Privacy**

- **FR-056**: System MUST never store credentials in Obsidian vault - all credentials in watchers/credentials/ directory (gitignored) or OS credential managers
- **FR-057**: System MUST use OAuth 2.0 with automatic token refresh for: Gmail, Xero (30-min refresh), Calendar, Slack
- **FR-058**: System MUST rotate API keys monthly, passwords quarterly, and immediately if breach suspected
- **FR-059**: System MUST implement local-first architecture: all data in Obsidian vault (local), MCP servers run locally, only API calls leave machine (encrypted)
- **FR-060**: System MUST redact PII from all logs and minimize data collection (only capture what's necessary for operation)

### Key Entities *(data structures)*

- **Action File**: Represents a detected event requiring processing. Attributes: type (email/xero/whatsapp/slack/calendar/file), source (gmail_watcher/xero_watcher/etc), priority (urgent/high/medium/low), status (pending/in_progress/completed), timestamp (ISO 8601), content (human-readable description), metadata (YAML: from/subject for emails, amount/customer for invoices, keyword for WhatsApp, etc.)

- **Approval Request**: Represents a sensitive action awaiting human approval. Attributes: action_type (send_email/post_social/process_payment), target (email address/social platform/payment recipient), context (why this action is needed), impact (what happens if approved), instructions (move to /Approved or /Rejected), created timestamp, expiration timestamp (optional timeout)

- **Plan**: Represents an execution strategy created by Claude for a complex task. Attributes: objective (what needs to be accomplished), steps (ordered checklist with checkboxes), approval_required (boolean flag), dependencies (references to other files/entities), status (pending_approval/in_progress/completed)

- **Audit Log Entry**: Represents a recorded action for accountability. Attributes: timestamp (ISO 8601), action_type (watcher_activity/file_operation/approval_request/external_action/error/system_health), actor (which component performed the action), target (what was acted upon), parameters (object with action-specific details), approval_status (not_required/pending/approved/rejected), result (success/failure), file_created (path to any generated file)

- **Watcher Process**: Represents a monitoring script. Attributes: name (gmail_watcher/xero_watcher/etc), check_interval (seconds), enabled (boolean), pid (process ID when running), last_check_time, last_activity_time, status (running/stopped/crashed), error_count (consecutive errors)

- **Business Goal**: Represents a measurable business objective. Attributes: name (Q1 Revenue Target), metric_type (revenue/response_time/invoice_payment_rate), target_value (numeric), current_value (numeric), alert_threshold (when to flag), period (daily/weekly/monthly/quarterly), status (on_track/at_risk/behind)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Core Functionality (Must-Have)**

- **SC-001**: All 6 Watchers detect events within their specified intervals: Gmail (2 min), WhatsApp (30 sec), Xero (5 min), Calendar (10 min), Slack (1 min), Filesystem (real-time < 5 sec)
- **SC-002**: System achieves 99%+ uptime for Watcher processes over a 7-day period (Watchdog auto-restart prevents extended downtime)
- **SC-003**: Action files are created in correct format with valid YAML frontmatter and human-readable content 100% of the time
- **SC-004**: Approval workflow completes end-to-end (detection → action file → approval request → approval → execution → audit log → file moved to /Done) within 10 minutes of human approval
- **SC-005**: Ralph Wiggum loop successfully completes multi-step tasks (3+ steps) without requiring additional human prompts 95%+ of the time
- **SC-006**: All actions (100%) are logged to audit trail with complete metadata (no missing required fields)
- **SC-007**: OAuth tokens refresh automatically without human intervention 99%+ of the time (only re-auth needed if refresh token expires at 60 days)

**Business Value (ROI Metrics)**

- **SC-008**: User spends less than 30 minutes per day reviewing Dashboard.md and processing approvals (down from 2-3 hours of manual work)
- **SC-009**: Email response time improves by 50% (measured from email arrival to draft response created in /Pending_Approval)
- **SC-010**: Zero missed financial deadlines (overdue invoices are flagged within 5 minutes of becoming overdue)
- **SC-011**: CEO briefing is generated every Sunday at 7:00 AM with complete data (no missing sections) and includes at least 1 actionable proactive suggestion
- **SC-012**: Social media consistency improves to 3+ posts per week across all platforms (vs manual posting inconsistency)
- **SC-013**: System successfully identifies at least 1 cost optimization opportunity per month (unused subscription, duplicate tool, overage fee)

**Quality & Reliability**

- **SC-014**: Error recovery succeeds 90%+ of the time (transient errors are resolved via automatic retry without human intervention)
- **SC-015**: Zero duplicate action files created for the same event (duplicate detection works correctly)
- **SC-016**: Zero accidental executions of sensitive actions without approval (100% of emails/social posts/payments go through approval workflow)
- **SC-017**: Dashboard.md is updated within 5 minutes of any significant event (approval processed, error occurred, new urgent task)
- **SC-018**: Log files remain under 10 MB per day (efficient logging without bloat) and are successfully rotated/archived after 90 days
- **SC-019**: System handles peak load of 100+ detected events per day (busy business day scenario) without performance degradation

**User Experience**

- **SC-020**: User can start all watchers with a single command (python orchestrator.py or start_ai_employee.bat) and verify status in under 30 seconds
- **SC-021**: Approval requests are clear and actionable (user can approve/reject in under 1 minute per request without needing additional context)
- **SC-022**: 90%+ of generated social media posts require minimal or no editing before approval (content quality is high enough to post as-is)
- **SC-023**: Users successfully complete initial setup (credentials, authentication, auto-start configuration) in under 2 hours with provided documentation
- **SC-024**: System startup after reboot completes in under 2 minutes (all watchers running and ready to detect events)

**Scalability & Maintainability**

- **SC-025**: Adding a new Watcher requires under 200 lines of Python code following the BaseWatcher pattern (system is extensible)
- **SC-026**: Individual Watchers can be disabled via config file without requiring code changes or system restart
- **SC-027**: System architecture supports future Platinum tier upgrade (cloud deployment, agent-to-agent communication) without requiring major refactoring
- **SC-028**: Audit logs are queryable and filterable by: date range, action_type, actor, result (success/failure) for troubleshooting and compliance

## Assumptions

**Environment & Prerequisites**

- User has Windows 10/11 with PowerShell 5.1+ and Python 3.13+ installed
- User has Obsidian installed (v1.10.6+) with vault located at C:\Users\[User]\Desktop\AI_Employee_Vault
- User has Claude Code installed and configured with active subscription (or Gemini API with Claude Code Router)
- User has stable internet connection (10+ Mbps recommended) for API calls to Google, Xero, Slack, social media platforms
- User has admin rights to configure Windows Task Scheduler for auto-start functionality

**Account Access & Permissions**

- User has existing accounts for: Gmail (G Suite or personal), Xero (with Owner or Standard user role), Google Calendar, Slack (with bot creation permissions), LinkedIn, Facebook, Instagram, Twitter/X
- User can create OAuth applications in: Google Cloud Console (Gmail, Calendar), Xero Developer Portal, Slack App Directory
- User has 2FA configured for Xero and is willing to complete authentication flow (Gold Tier requirement per Xero API TOS)
- User's social media accounts have posting permissions (not restricted by organization policies)

**Data & Business Context**

- User has an existing Business_Goals.md file with defined revenue targets, KPIs, and active projects (or will create one using business-goals-manager skill during setup)
- User's Company_Handbook.md contains business-specific rules: email tone/style, approval thresholds, VIP contacts, blocked senders, financial alert amounts
- User's Xero account contains actual business data (invoices, bills, transactions) for meaningful CEO briefing generation
- User's Gmail inbox uses labels or importance markers (system filters for "unread important" emails)

**Operational Assumptions**

- User will review Dashboard.md at least once daily (morning recommended) to check pending approvals and system status
- User will process approval files within 24 hours (system does not auto-expire approvals, but some actions may have implicit deadlines)
- User's machine remains on and connected to internet for 24/7 operation, OR user accepts that detection happens only when machine is on (Platinum tier addresses this with cloud deployment)
- User will respond to authentication alerts (OAuth token expired, WhatsApp session logged out) within 24-48 hours to restore functionality

**Technical Assumptions**

- MCP servers are configured in ~/.config/claude-code/mcp.json with correct paths and environment variables
- Playwright browser automation is acceptable for WhatsApp and Twitter/X (user understands visible browser windows will appear)
- Ralph Wiggum loop Stop hook is correctly installed in Claude Code configuration (part of setup process)
- Python packages are installed via pip/uv: google-auth, google-api-python-client, playwright, watchdog, requests, pyyaml

**Scope Boundaries**

- System does NOT provide web UI or mobile app - Obsidian vault is the GUI
- System does NOT integrate with banking APIs directly - Xero is the interface for financial data (user must manually import bank transactions to Xero)
- System does NOT automatically execute payments - all payments require approval and manual execution (AI only drafts and logs)
- System does NOT provide AI-powered email/social content generation beyond drafting - user must review and edit for accuracy, tone, brand voice
- System does NOT support multi-user collaboration in Gold Tier - it's designed for a single business owner (team features are potential future enhancement)

**Gold Tier Specific Assumptions**

- User has completed Bronze tier (basic vault + 1 watcher) and Silver tier (multiple watchers + approval workflow) OR is comfortable with the increased complexity of Gold tier setup
- User understands that Gold tier requires ~40 hours of setup/configuration/testing time (per hackathon spec)
- User is willing to create and configure multiple OAuth applications across 6+ platforms
- User accepts that social media posting uses official MCP servers where available, or Playwright browser automation (Twitter/X) where APIs are restricted/expensive
- User's Xero subscription tier supports API access (Starter tier and above)

## Dependencies

**External Services**

- Google Workspace APIs: Gmail API, Google Calendar API (OAuth 2.0, free tier sufficient for personal use)
- Xero API: Accounting API (OAuth 2.0, requires paid Xero subscription Starter tier or above, API access included)
- Slack API: Web API, Events API (requires Slack workspace, free tier sufficient)
- LinkedIn API: Marketing Developer Platform (requires LinkedIn Page, OAuth 2.0)
- Facebook Graph API: Pages API (requires Facebook Page, Business account recommended)
- Instagram Graph API: Content Publishing API (requires Instagram Business account connected to Facebook Page)
- Twitter/X: No API used (Playwright browser automation due to API cost/restrictions)
- WhatsApp Web: No API used (Playwright browser automation, personal account sufficient)

**Software & Libraries**

- Obsidian (v1.10.6+): Markdown editor serving as GUI and vault storage
- Claude Code: AI reasoning engine with Agent Skills support (Pro subscription or Gemini API + Router)
- Python 3.13+: Watcher scripts, orchestration, utility scripts
- Node.js v24+ LTS: MCP servers (gmail-mcp, xero-mcp, linkedin-mcp, etc.)
- Playwright (Python package): Browser automation for WhatsApp, Twitter/X
- Google API Client (Python): google-auth, google-api-python-client for Gmail and Calendar
- Watchdog (Python): File system monitoring for Inbox folder
- PyYAML (Python): YAML frontmatter parsing
- Git (recommended): Version control for vault (not required but highly recommended)

**Internal Components**

- Company_Handbook.md v2.1: Rules engine containing all decision-making policies
- Business_Goals.md: Business context with targets, KPIs, projects, alert thresholds
- Dashboard.md: System status display and user interface
- Agent Skills: task-processor, approval-processor, dashboard-updater, ceo-briefing-generator, social-media-manager, financial-analyst, business-goals-manager
- MCP Servers: gmail-mcp, xero-mcp, linkedin-mcp, facebook-mcp, instagram-mcp, x-poster, browser-mcp
- Orchestrator + Watchdog: Process management and health monitoring
- Ralph Wiggum Loop: Stop hook for autonomous multi-step task completion

**Infrastructure**

- Windows Task Scheduler (or cron on Linux/Mac): Auto-start watchers on boot
- File system: Sufficient disk space for logs (estimate 10 MB/day × 90 days = ~1 GB), vault storage
- Network: Stable internet connection for API calls (10+ Mbps recommended)
- Compute: 8GB RAM minimum (16GB recommended), 4-core CPU minimum (8-core recommended)

**Documentation & Templates**

- Requirements2.md: Hackathon specification (Bronze → Platinum tiers)
- README.md: System overview and quickstart guide
- QUICKSTART.md: 5-minute setup guide
- Individual watcher README files: watchers/README.md, watchers/credentials/README.md
- MCP server README files: mcp-servers/*/README.md
- Agent Skill SKILL.md files: .claude/skills/*/SKILL.md

## Out of Scope

**Explicitly NOT Included in Gold Tier**

- Platinum Tier Features: 24/7 cloud deployment, Cloud + Local agent split architecture, vault synchronization via Git/Syncthing, Agent-to-Agent (A2A) direct communication, Odoo Community ERP cloud deployment
- Banking API Integration: Direct connection to banking APIs for transaction import (user must use Xero's bank feeds or manual CSV import)
- Payment Execution: Actual payment processing through banking systems (AI only creates approval requests; user executes payments manually in Xero or bank portal)
- Web UI / Mobile App: No browser-based dashboard or mobile application (Obsidian vault is the UI)
- Multi-User Collaboration: No role-based access control, no team member accounts, no shared approval queues (designed for single business owner)
- Real-Time Collaboration: No websocket connections, no live updates, no presence indicators (file-based async workflow)
- Advanced NLP: No sentiment analysis, no intent classification, no entity extraction (Claude Code handles reasoning, but not specialized NLP models)
- Computer Vision: No invoice OCR from images, no receipt scanning, no document parsing (file watcher detects files but doesn't extract data from PDFs/images)
- Voice Interface: No voice commands, no speech-to-text, no audio processing
- SMS / Text Message Monitoring: Only WhatsApp is supported for messaging; traditional SMS is out of scope
- Email Parsing for Complex Structures: System extracts basic metadata (from, subject, snippet) but does not parse HTML emails, attachments, or inline images
- CRM Integration: No Salesforce, HubSpot, Zoho, or other CRM connectors (Xero is the only business system integrated)
- Project Management Integration: No Asana, Trello, Jira, or other PM tool connectors
- Zapier / IFTTT Integration: No pre-built integrations with automation platforms
- AI Content Generation: System drafts responses and posts but does NOT generate long-form content (blog posts, articles, whitepapers)
- AI Image Generation: No DALL-E / Midjourney / Stable Diffusion integration for social media graphics
- Video Processing: No video editing, no YouTube upload automation, no video transcription

**Future Enhancements (Post-Gold Tier)**

- Odoo Community ERP Integration: As alternative to Xero (documented in Company_Handbook.md but not implemented in Gold)
- Instagram / Facebook Automated Engagement: Responding to comments, DMs, mentions (currently only posting is supported)
- LinkedIn Advanced Features: Scheduled publishing, LinkedIn newsletter, LinkedIn Live, poll creation
- Twitter/X Advanced Features: Thread creation, reply automation, mention tracking, DM monitoring
- Calendar Scheduling Automation: Automatically propose meeting times, send calendar invites, reschedule based on conflicts
- Email Auto-Categorization: ML-based priority scoring, auto-archive low-priority emails, intelligent inbox organization
- Subscription Cost Tracking: Automatically detect all subscription charges from bank transactions and track usage metrics
- Invoice Payment Prediction: Predict which invoices will be paid late based on historical customer payment patterns
- Business Intelligence Dashboards: Interactive charts/graphs for revenue trends, expense categories, task completion rates
- Custom Watcher Framework: UI or CLI tool to generate new Watchers without coding (template-based watcher creation)

**Known Limitations**

- WhatsApp Watcher Requires Visible Browser: Cannot run in headless mode due to WhatsApp Web restrictions; browser window must remain open
- Twitter/X No Official API: Uses Playwright browser automation instead of API due to Twitter API cost ($100+/month for write access)
- Xero OAuth Token 30-Minute Expiry: Requires automatic refresh every 30 minutes; if system is offline during refresh, manual re-auth required
- Context Window Limits: Claude Code has context limits; very large file backlogs (100+ files in /Needs_Action) may require batch processing
- No Offline Functionality: All features require internet connection; local-only mode is not supported
- Rate Limits: Social media platforms impose rate limits (e.g., LinkedIn 100 posts/day, Twitter 2400 tweets/day); system respects limits but doesn't have advanced quota management
- No Automated Testing: Gold tier includes manual testing procedures but no automated test suite (unit tests, integration tests, E2E tests)
- Windows-Centric Instructions: Setup guides assume Windows 10/11; Linux/Mac users must adapt scripts (orchestrator works cross-platform but auto-start setup is Windows-specific)

## Risks & Mitigation

**High-Severity Risks**

- **RISK-001: OAuth Token Expiration Leading to System Downtime**: If OAuth tokens expire and automatic refresh fails, watchers stop detecting events until user manually re-authenticates. **Mitigation**: Implement token refresh 5 minutes before expiry, log refresh attempts, create high-priority alert in Dashboard.md if refresh fails, send email notification (if Gmail MCP is still functional)

- **RISK-002: Accidental Posting of Sensitive Information to Social Media**: User approves a social post without noticing it contains confidential business data, customer PII, or embargoed information. **Mitigation**: Implement keyword scanning in social-media-manager skill for sensitive terms (configurable in Company_Handbook.md), add prominent warning in approval file if sensitive keywords detected, require explicit "I confirm this post contains no confidential information" checkbox

- **RISK-003: WhatsApp Session Logout Causing Missed Urgent Messages**: WhatsApp Web session expires remotely (user logged out from phone, session timeout), watcher stops working, urgent client messages are missed. **Mitigation**: Watcher detects logout within 30 seconds (QR code page appears), creates urgent alert in /Needs_Action with notification, Dashboard.md shows prominent "WhatsApp Disconnected" alert, consider SMS/email backup notification if available

- **RISK-004: Corrupted Vault Files Due to Concurrent Access**: Obsidian syncing conflicts or multiple processes writing to the same file cause data corruption or lost action files. **Mitigation**: Implement atomic file writes (write to temp file, then move), use file locking where possible, retry on write failures with exponential backoff, maintain file checksums for critical files (Company_Handbook.md, Business_Goals.md)

**Medium-Severity Risks**

- **RISK-005: Rate Limiting on Social Media Platforms Causing Posting Failures**: Posting too frequently hits API rate limits, posts fail to publish. **Mitigation**: Track API call counts per platform per hour/day in memory, implement exponential backoff when rate limited, queue posts for later retry with priority, log rate limit events

- **RISK-006: Large Backlog Overwhelming Claude Code Context Window**: If system is offline for days, /Needs_Action fills with hundreds of files, Claude Code cannot process them all in one session. **Mitigation**: Task-processor skill implements batch processing (max 10 files per session), prioritizes by urgency (urgent → high → medium → low), provides progress indicator in Dashboard.md, user can manually process batches

- **RISK-007: Xero Sandbox vs Production Confusion During Testing**: User accidentally connects to production Xero tenant during testing, test invoices/bills are created in live accounting system. **Mitigation**: Require explicit "PRODUCTION" or "SANDBOX" environment variable, display prominent warning in Dashboard.md showing which Xero tenant is connected, implement dry-run mode for testing, document testing procedures clearly

- **RISK-008: Watchdog Creating Restart Loop on Persistent Error**: Watcher crashes repeatedly due to persistent error (e.g., malformed credentials file), Watchdog keeps restarting it, log files fill up. **Mitigation**: Watchdog tracks restart count per watcher per hour, after 3 restarts in 1 hour, pause that watcher and create alert, log analysis to detect restart loops, manual intervention required to fix root cause

**Low-Severity Risks**

- **RISK-009: Duplicate Action Files from Race Conditions**: Two events happen simultaneously (email arrives, Xero invoice created for same customer), watchers create files concurrently, potential for duplicates. **Mitigation**: Each watcher maintains processed IDs locally, Claude Code implements duplicate detection during processing (checks for similar content in /Needs_Action), consolidates duplicates into single plan

- **RISK-010: Log Files Growing Too Large**: Busy system generates 10+ MB of logs per day, 90-day retention = 900 MB. **Mitigation**: Implement log rotation (compress daily logs older than 7 days), archive logs older than 30 days to separate Archive folder, document log retention policy in Company_Handbook.md, user can adjust retention period

- **RISK-011: Dashboard.md Sync Conflicts in Git**: If user has vault in Git repo and commits Dashboard.md, conflicts occur because dashboard is auto-updated frequently. **Mitigation**: Recommend adding Dashboard.md to .gitignore (or separate branch), document in setup guide, consider implementing "Dashboard.md is generated - do not manually edit" header

- **RISK-012: Social Media Post Preview Not Matching Final Output**: Approval file shows post preview, but actual posted content looks different due to platform formatting or character encoding. **Mitigation**: MCP servers generate exact preview that matches API payload, include character count and formatting warnings in approval file, test posting to each platform during setup

**Security Risks**

- **RISK-013: Credentials Accidentally Committed to Git**: User commits watchers/credentials/ directory with OAuth tokens to public GitHub repo. **Mitigation**: .gitignore includes watchers/credentials/ by default, setup script verifies .gitignore is configured, document security best practices prominently in README.md, recommend using git-secrets or similar tools

- **RISK-014: Malicious File Dropped in Inbox Folder**: Attacker with file system access drops malicious file in Inbox, filesystem watcher creates action file, Claude Code processes it. **Mitigation**: Filesystem watcher only copies file metadata (not executes), Claude Code does not execute files or run code from Inbox, user must manually review any file before taking action, document security warning in Company_Handbook.md

- **RISK-015: PII Leakage in Audit Logs**: Full email content or payment details accidentally logged in plain text. **Mitigation**: Implement PII redaction rules per FR-039, audit logs only capture metadata (email: from/to/subject, payment: amount/reference, NOT full content), log analysis to detect accidental PII leaks, encrypt logs at rest (optional)

## Notes

**Implementation Priorities**

This spec intentionally prioritizes user stories by P1 (critical for Gold tier) → P2 (important) → P3 (nice-to-have). Developers should implement in this order:

1. **Phase 1 (P1 Stories - Core MVP)**: Email monitoring (US-001), Financial management (US-002), Ralph loop (US-005), Audit logging (US-010) - these deliver the core "Digital FTE" value proposition
2. **Phase 2 (P2 Stories - High Value)**: Social media (US-003), WhatsApp (US-004), CEO briefing (US-006) - these complete the cross-domain integration
3. **Phase 3 (P3 Stories - Quality of Life)**: Calendar (US-007), Slack (US-008), Filesystem (US-009) - these add convenience but aren't critical

**Testing Recommendations**

- Create test accounts for all services (Gmail test account, Xero demo organization, LinkedIn test page, etc.) to avoid impacting production data
- Use Xero sandbox API during development (switch to production only after thorough testing)
- Implement a DRY_RUN environment variable that prevents all external actions (emails, posts, Xero writes) while logging what would have happened
- Test edge cases explicitly: token expiration, rate limiting, offline scenarios, large backlogs, concurrent access

**Gold Tier Completion Checklist**

Per Requirements2.md, Gold Tier requires:
- ✅ All Silver requirements plus
- ✅ Full cross-domain integration (Personal + Business) - covered by US-001, US-002, US-003, US-004, US-007, US-008, US-009
- ✅ Xero accounting integration via MCP - covered by US-002, FR-025, FR-006
- ✅ Facebook and Instagram posting - covered by US-003, FR-028
- ✅ Twitter/X posting - covered by US-003, FR-027
- ✅ Multiple MCP servers for different action types - covered by FR-024 through FR-029
- ✅ Weekly Business and Accounting Audit with CEO Briefing - covered by US-006, FR-020
- ✅ Error recovery and graceful degradation - covered by FR-051 through FR-055
- ✅ Comprehensive audit logging - covered by US-010, FR-037 through FR-042
- ✅ Ralph Wiggum loop for autonomous multi-step tasks - covered by US-005, FR-021, FR-022
- ✅ Complete architecture documentation - this spec + Company_Handbook.md + README.md
- ✅ All AI functionality as Agent Skills - covered by FR-016 through FR-023

**Known Specification Gaps (For Clarification Phase)**

This spec intentionally leaves some details for the clarification or planning phase:
- Specific social media post templates and tone (documented in Company_Handbook.md, not duplicated here)
- Exact Xero API endpoints and request/response formats (technical implementation details)
- MCP server internal architecture (out of scope for requirements spec)
- Ralph Wiggum loop Stop hook implementation details (defer to official GitHub repo)
- Detailed error message text and wording (defer to implementation)

These are appropriate to defer because they're either already documented elsewhere, are technical implementation details (not requirements), or are specific wording/UX polish that can be decided during development.
