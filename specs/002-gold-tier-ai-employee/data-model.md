# Gold Tier Data Model

**Feature**: 002-gold-tier-ai-employee
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document defines the core entities, relationships, and validation rules for Gold Tier Personal AI Employee. All data is stored as files in the Obsidian vault (file-based state management per constitution).

---

## Entity Definitions

### 1. Action File

Represents a detected event requiring processing. Created by Watchers when external events are detected.

**Attributes**:
- `type` (string, required): Event type - `email` | `xero` | `whatsapp` | `slack` | `calendar` | `file`
- `source` (string, required): Watcher that created the file - `gmail_watcher` | `xero_watcher` | `whatsapp_watcher` | `slack_watcher` | `calendar_watcher` | `filesystem_watcher`
- `priority` (string, required): Urgency level - `urgent` | `high` | `medium` | `low`
- `status` (string, required): Processing status - `pending` | `in_progress` | `completed`
- `timestamp` (string, required): ISO 8601 timestamp - `YYYY-MM-DDTHH:MM:SSZ`
- `content` (string, required): Human-readable description of the event
- `metadata` (object, required): Event-specific metadata (YAML frontmatter)

**Metadata by Type**:
- **email**: `from`, `subject`, `snippet`, `message_id`, `labels[]`
- **xero**: `type` (invoice/bill/payment), `invoice_number`, `contact_name`, `amount`, `due_date`, `status`
- **whatsapp**: `sender_name`, `phone_number`, `message`, `keyword_matched`
- **slack**: `channel`, `sender`, `message`, `timestamp`, `thread_id?`
- **calendar**: `event_id`, `title`, `start_time`, `end_time`, `location?`, `attendees[]`
- **file**: `filename`, `file_size`, `file_type`, `file_path`

**File Format**: Markdown with YAML frontmatter
```markdown
---
type: email
source: gmail_watcher
priority: high
status: pending
timestamp: 2026-01-17T12:34:56Z
metadata:
  from: "sender@example.com"
  subject: "Invoice #1234 overdue"
  snippet: "Your invoice #1234 is 7 days overdue..."
  message_id: "19abc123xyz456"
  labels: ["IMPORTANT", "INVOICES"]
---

# Invoice Overdue Alert

**From**: sender@example.com
**Subject**: Invoice #1234 overdue
**Date**: 2026-01-17T12:34:56Z

Your invoice #1234 is 7 days overdue. Please pay immediately to avoid late fees.
```

**Location**: `/Needs_Action/EMAIL_[message_id].md` (or `XERO_...`, `WHATSAPP_...`, etc.)

**Validation Rules**:
- `type` must be one of: `email`, `xero`, `whatsapp`, `slack`, `calendar`, `file`
- `source` must match watcher name (e.g., `gmail_watcher`)
- `priority` must be one of: `urgent`, `high`, `medium`, `low`
- `status` must be `pending` on creation, transitions to `in_progress` → `completed`
- `timestamp` must be valid ISO 8601 format
- `content` must be non-empty string
- `metadata` must include required fields for type (see above)

**Relationships**:
- One Action File → One Approval Request (if sensitive action)
- Many Action Files → One Plan (consolidated by Claude Code)
- One Watcher Process → Many Action Files

---

### 2. Approval Request

Represents a sensitive action awaiting human approval. Created by task-processor when Action File requires approval.

**Attributes**:
- `action_type` (string, required): Type of action - `send_email` | `post_linkedin` | `post_tweet` | `post_facebook` | `post_instagram` | `process_payment` | `delete_file`
- `target` (string, required): Action target - email address | social platform | payment recipient
- `context` (string, required): Why this action is needed (reasoning from Claude Code)
- `impact` (string, required): What happens if approved (business impact, risks)
- `risk_level` (string, required): Risk assessment - `low` | `medium` | `high` | `critical`
- `created_timestamp` (string, required): ISO 8601 timestamp when request created
- `deadline_timestamp` (string, optional): ISO 8601 timestamp for approval deadline (default 24 hours)
- `expiration_timestamp` (string, optional): ISO 8601 timestamp for auto-rejection (default 7 days)
- `instructions` (string, required): Clear approval instructions - "Move to /Approved to proceed, /Rejected to cancel"
- `approval_metadata` (object, required): Action-specific data (email draft, social post content, payment details)

**File Format**: Markdown with YAML frontmatter
```markdown
---
action_type: send_email
target: "client@example.com"
context: "Client sent inquiry via website form, requires response with pricing information"
impact: "If approved: Email sent with pricing PDF. If rejected: Client may not receive pricing, potential lost sale."
risk_level: medium
created_timestamp: 2026-01-17T12:34:56Z
deadline_timestamp: 2026-01-18T12:34:56Z
expiration_timestamp: 2026-01-24T12:34:56Z
instructions: "Move this file to /Approved to send email, or /Rejected to cancel."
approval_metadata:
  subject: "Pricing Information - Your Inquiry"
  body: "Dear Client, Thank you for your inquiry..."
  attachments: ["/path/to/pricing.pdf"]
---

# Approval Required: Send Email to client@example.com

## Action Details
**Type**: Send Email
**Target**: client@example.com
**Risk Level**: Medium

## Context
Client sent inquiry via website form, requires response with pricing information.

## Impact
If approved: Email sent with pricing PDF.
If rejected: Client may not receive pricing, potential lost sale.

## Draft Content
**Subject**: Pricing Information - Your Inquiry

**Body**:
Dear Client,

Thank you for your inquiry about our services. Attached is our pricing PDF...

## Instructions
Move this file to `/Approved` to send the email, or `/Rejected` to cancel.
```

**Location**: `/Pending_Approval/[action_type]_[timestamp].md`

**Validation Rules**:
- `action_type` must be one of: `send_email`, `post_linkedin`, `post_tweet`, `post_facebook`, `post_instagram`, `process_payment`, `delete_file`
- `target` must be non-empty string (valid email address, social platform handle, payment recipient)
- `context` must be non-empty string (explains why action is needed)
- `impact` must be non-empty string (explains consequences)
- `risk_level` must be one of: `low`, `medium`, `high`, `critical`
- `created_timestamp` must be valid ISO 8601 format
- `deadline_timestamp` must be > `created_timestamp` (default +24 hours)
- `expiration_timestamp` must be > `deadline_timestamp` (default +7 days)
- `instructions` must contain clear approval/rejection steps
- `approval_metadata` must include required fields for `action_type`

**Relationships**:
- One Approval Request → One Action File (original event)
- One Approval Request → Many Audit Log Entries (created, approved/rejected, executed)

---

### 3. Plan

Represents an execution strategy created by Claude for complex tasks (3+ steps or >15 minutes). Includes objective, step-by-step approach, tracking.

**Attributes**:
- `plan_id` (string, required): Unique plan identifier - `PLAN_YYYYMMDD_HHMMSS`
- `objective` (string, required): What needs to be accomplished
- `steps` (array, required): Ordered checklist with checkboxes
  - `step_number` (integer, required): Step order (1, 2, 3, ...)
  - `description` (string, required): Step description
  - `status` (string, required): Step status - `pending` | `in_progress` | `completed`
  - `estimated_time_minutes` (integer, optional): Estimated time for step
  - `actual_time_minutes` (integer, optional): Actual time taken
  - `notes` (string, optional): Additional notes for step
- `approval_required` (boolean, required): True if plan requires human approval before execution
- `dependencies` (array, optional): References to other files or entities - `["EMAIL_123.md", "XERO_456.md"]`
- `status` (string, required): Plan status - `pending_approval` | `in_progress` | `completed` | `failed` | `deviated`
- `created_timestamp` (string, required): ISO 8601 timestamp when plan created
- `started_timestamp` (string, optional): ISO 8601 timestamp when execution started
- `completed_timestamp` (string, optional): ISO 8601 timestamp when plan completed
- `total_estimated_time_minutes` (integer, optional): Total estimated time for all steps
- `total_actual_time_minutes` (integer, optional): Total actual time taken
- `deviation_percentage` (number, optional): Percentage deviation from estimate (e.g., 23.5 for +23.5%)
- `lessons_learned` (string, optional): Insights captured after completion

**File Format**: Markdown with YAML frontmatter
```markdown
---
plan_id: PLAN_20260117_123456
objective: "Process all overdue invoices in /Needs_Action (5 invoices)"
approval_required: true
dependencies: ["XERO_OVERDUE_20260117_120000.md", "XERO_OVERDUE_20260117_120500.md", ...]
status: in_progress
created_timestamp: 2026-01-17T12:34:56Z
started_timestamp: 2026-01-17T12:35:00Z
total_estimated_time_minutes: 30
steps:
  - step_number: 1
    description: "Read all overdue invoice action files in /Needs_Action"
    status: completed
    estimated_time_minutes: 2
    actual_time_minutes: 1
  - step_number: 2
    description: "Query Xero API for each invoice to verify overdue status"
    status: completed
    estimated_time_minutes: 10
    actual_time_minutes: 12
  - step_number: 3
    description: "Create approval request for follow-up emails to 5 customers"
    status: in_progress
    estimated_time_minutes: 5
  - step_number: 4
    description: "Move approval requests to /Pending_Approval"
    status: pending
    estimated_time_minutes: 1
  - step_number: 5
    description: "Update Dashboard.md with overdue invoice summary"
    status: pending
    estimated_time_minutes: 2
---

# Plan: Process Overdue Invoices

## Objective
Process all overdue invoices in /Needs_Action (5 invoices)

## Status
**Status**: In Progress
**Started**: 2026-01-17 12:35:00 UTC
**Estimated Time**: 30 minutes

## Execution Steps

- [x] **Step 1**: Read all overdue invoice action files in /Needs_Action (1 min / 2 min est)
- [x] **Step 2**: Query Xero API for each invoice to verify overdue status (12 min / 10 min est)
- [ ] **Step 3**: Create approval request for follow-up emails to 5 customers (5 min est)
- [ ] **Step 4**: Move approval requests to /Pending_Approval (1 min est)
- [ ] **Step 5**: Update Dashboard.md with overdue invoice summary (2 min est)

## Dependencies
- XERO_OVERDUE_20260117_120000.md
- XERO_OVERDIVE_20260117_120500.md
- ... (3 more files)

## Notes
- Step 2 took longer than estimated due to Xero API rate limiting
- All 5 invoices confirmed as overdue (7-14 days overdue)
- Next: Create approval requests for follow-up emails
```

**Location**: `/Plans/active/PLAN_YYYYMMDD_HHMMSS.md` (active) or `/Plans/archive/PLAN_YYYYMMDD_HHMMSS.md` (completed)

**Validation Rules**:
- `plan_id` must be unique format: `PLAN_YYYYMMDD_HHMMSS`
- `objective` must be non-empty string
- `steps` must contain at least 3 steps (definition of complex task)
- Each step must have `step_number`, `description`, `status`
- `status` must be one of: `pending_approval`, `in_progress`, `completed`, `failed`, `deviated`
- If `status` = `completed`, then `completed_timestamp` is required
- If `deviation_percentage` > 20, then `status` = `deviated` and addendum plan required
- `approval_required` = true for plans with `risk_level` = high or critical

**Relationships**:
- One Plan → Many Action Files (consolidated from /Needs_Action)
- One Plan → Many Audit Log Entries (created, each step completed, final status)
- One Plan → One Addendum Plan (if deviation >20%)

---

### 4. Audit Log Entry

Represents a recorded action for accountability and compliance. Logged to daily JSON files.

**Attributes**:
- `timestamp` (string, required): ISO 8601 timestamp - `YYYY-MM-DDTHH:MM:SSZ`
- `action_type` (string, required): Type of action - `watcher_activity` | `file_operation` | `approval_request` | `external_action` | `error` | `system_health`
- `actor` (string, required): Component that performed action - `gmail_watcher` | `approval-processor` | `ceo-briefing-generator` | `orchestrator` | `user` (human)
- `target` (string, optional): What was acted upon - email address | file path | social platform
- `parameters` (object, optional): Action-specific parameters
- `approval_status` (string, optional): Approval workflow status - `not_required` | `pending` | `approved` | `rejected`
- `result` (string, required): Action outcome - `success` | `failure`
- `error` (string, optional): Error message (if result = failure)
- `file_created` (string, optional): Path to file created by action
- `retry_possible` (boolean, optional): True if error is transient and retry is possible
- `retry_count` (integer, optional): Number of retry attempts made

**File Format**: JSON (one entry per line, or JSON array)
```json
{
  "timestamp": "2026-01-17T12:34:56Z",
  "action_type": "external_action",
  "actor": "approval-processor",
  "target": "client@example.com",
  "parameters": {
    "subject": "Pricing Information",
    "body": "Dear Client...",
    "attachments": ["/path/to/pricing.pdf"]
  },
  "approval_status": "approved",
  "result": "success",
  "file_created": "/Done/EMAIL_approval_20260117_123456.md"
}
```

**Location**: `/Logs/audit_YYYY-MM-DD.json` (daily file, rotated at midnight)

**Validation Rules**:
- `timestamp` must be valid ISO 8601 format
- `action_type` must be one of: `watcher_activity`, `file_operation`, `approval_request`, `external_action`, `error`, `system_health`
- `actor` must be valid component name or `user` (human)
- `result` must be either `success` or `failure`
- If `result` = `failure`, then `error` is required
- If `action_type` = `external_action`, then `approval_status` is required

**Relationships**:
- One Audit Log Entry → One Action File (if action created file)
- One Audit Log Entry → One Approval Request (if approval workflow)
- One Audit Log Entry → One Plan (if action was plan execution)

---

### 5. Watcher Process

Represents a monitoring script (Watcher) managed by Orchestrator. State tracked in memory by Orchestrator.

**Attributes**:
- `name` (string, required): Watcher name - `gmail_watcher` | `whatsapp_watcher` | `xero_watcher` | `calendar_watcher` | `slack_watcher` | `filesystem_watcher`
- `script_path` (string, required): Path to Python script - `watchers/gmail_watcher.py`
- `check_interval` (integer, required): Check interval in seconds - 120 (Gmail) | 30 (WhatsApp) | 300 (Xero) | 600 (Calendar) | 60 (Slack) | 0 (Filesystem, real-time)
- `enabled` (boolean, required): Whether watcher is enabled in config - `true` | `false`
- `pid` (integer, optional): Process ID when running (null if stopped)
- `last_check_time` (string, optional): ISO 8601 timestamp of last successful check
- `last_activity_time` (string, optional): ISO 8601 timestamp of last event detected
- `status` (string, required): Watcher status - `running` | `stopped` | `crashed` | `disabled`
- `error_count` (integer, required): Consecutive error count (resets to 0 on success)
- `restart_count` (integer, required): Total restart count since orchestrator started
- `last_error_message` (string, optional): Last error message (if error_count > 0)

**File Format**: JSON (managed by Orchestrator, persisted to `orchestrator_state.json`)
```json
{
  "name": "gmail_watcher",
  "script_path": "watchers/gmail_watcher.py",
  "check_interval": 120,
  "enabled": true,
  "pid": 12345,
  "last_check_time": "2026-01-17T12:34:56Z",
  "last_activity_time": "2026-01-17T12:34:50Z",
  "status": "running",
  "error_count": 0,
  "restart_count": 1,
  "last_error_message": null
}
```

**Location**: `watchers/orchestrator_state.json` (in-memory state persisted by Orchestrator)

**Validation Rules**:
- `name` must be one of the 6 watcher names
- `check_interval` must be positive integer (0 for real-time)
- If `status` = `running`, then `pid` is required and `pid` must be valid process ID
- If `error_count` >= 3, Orchestrator pauses watcher and creates alert
- `last_check_time` must be <= current time (no future timestamps)

**Relationships**:
- One Watcher Process → Many Action Files (creates action files when events detected)
- One Watcher Process → Many Audit Log Entries (logs all detection events)

---

### 6. Business Goal

Represents a measurable business objective defined in Business_Goals.md. Referenced by CEO Briefing.

**Attributes**:
- `name` (string, required): Goal name - "Q1 Revenue Target" | "Monthly Invoice Payment Rate" | "Weekly Task Completion"
- `metric_type` (string, required): Type of metric - `revenue` | `response_time` | `invoice_payment_rate` | `task_completion_rate` | `customer_satisfaction`
- `target_value` (number, required): Target value (numeric)
- `current_value` (number, required): Current actual value
- `unit` (string, optional): Unit of measurement - "$" | "%" | "hours" | "days" | "count"
- `period` (string, required): Goal period - `daily` | `weekly` | `monthly` | `quarterly` | `annual`
- `start_date` (string, required): ISO 8601 date when goal period starts
- `end_date` (string, required): ISO 8601 date when goal period ends
- `status` (string, required): Goal status - `on_track` | `at_risk` | `behind` | `achieved` | `not_achieved`
- `alert_threshold` (number, optional): Threshold for triggering alert (e.g., if current_value < alert_threshold)
- `last_updated_timestamp` (string, required): ISO 8601 timestamp when current_value last updated

**File Format**: Markdown in Business_Goals.md
```markdown
# Business Goals

## Q1 2026 Revenue Target
- **Metric Type**: Revenue
- **Target Value**: $100,000
- **Current Value**: $85,000
- **Unit**: $
- **Period**: Quarterly
- **Start Date**: 2026-01-01
- **End Date**: 2026-03-31
- **Status**: at_risk (85% of target, 6 weeks remaining)
- **Alert Threshold**: $90,000 (trigger alert if below this value)
- **Last Updated**: 2026-01-17T12:34:56Z
```

**Location**: `/Business_Goals.md` (all goals in single file, managed by business-goals-manager skill)

**Validation Rules**:
- `metric_type` must be one of: `revenue`, `response_time`, `invoice_payment_rate`, `task_completion_rate`, `customer_satisfaction`
- `period` must be one of: `daily`, `weekly`, `monthly`, `quarterly`, `annual`
- `status` must be one of: `on_track`, `at_risk`, `behind`, `achieved`, `not_achieved`
- `start_date` must be < `end_date`
- `current_value` must be numeric (can be 0 or negative)
- `target_value` must be > 0

**Relationships**:
- Many Business Goals → One CEO Briefing (referenced in briefing generation)

---

## Entity Relationships

```
Action File (1) -----> (1) Approval Request
    |
    | (consolidated by Claude Code)
    v
Plan (1) <----- (many) Action Files
    |
    | (generates)
    v
Audit Log Entry (many)

Watcher Process (1) -----> (many) Action Files
    |
    | (logs)
    v
Audit Log Entry (many)

Business Goal (many) -----> (1) CEO Briefing (references goals)
```

---

## File Organization

All entities stored as files in Obsidian vault:

```
AI_Employee_Vault/
├── Needs_Action/              # Action Files (pending)
├── Plans/
│   ├── active/                # Plans (currently executing)
│   └── archive/               # Plans (completed)
├── Pending_Approval/          # Approval Requests (awaiting review)
├── Approved/                  # Approval Requests (ready to execute)
├── Rejected/                  # Approval Requests (cancelled)
├── Done/                      # Action Files + Approval Requests (completed)
├── Failed/                    # Action Files + Approval Requests (errors)
├── Logs/
│   ├── audit_YYYY-MM-DD.json  # Audit Log Entries (daily rotation)
│   └── mcp_actions_YYYY-MM-DD.json
├── Briefings/                 # CEO Briefings
│   └── YYYY-MM-DD_Monday_Briefing.md
├── Business_Goals.md          # Business Goals
├── Company_Handbook.md        # Business rules
└── Dashboard.md               # System status
```

---

## Data Validation

**Validation Approach**:
1. **Schema Validation**: All entities validated against schema definitions (see Validation Rules above)
2. **Format Validation**: ISO 8601 timestamps, required fields, enum values
3. **Business Logic Validation**: Status transitions, dependency checks, threshold checks
4. **Cross-Entity Validation**: Referential integrity (e.g., Plan references existing Action Files)

**Validation Tools**:
- Watcher scripts validate action file format before creation
- Agent Skills validate approval request format before creation
- Orchestrator validates watcher state before health checks
- Audit logging validates entry format before write

**Error Handling**:
- Malformed files moved to `/Failed/` with validation error details
- Invalid entities logged to error log with schema violation details
- Human alerted via Dashboard.md if validation error rate > 10%

---

## Data Lifecycle

**Creation**:
- Action Files created by Watchers (external events)
- Approval Requests created by task-processor (sensitive actions)
- Plans created by Claude Code (complex tasks)
- Audit Log Entries created by all components (every action)
- Business Goals created/updated by business-goals-manager (human input)

**Updates**:
- Action Files: status transitions (pending → in_progress → completed)
- Approval Requests: moved between folders (/Pending_Approval → /Approved → /Done)
- Plans: step status updates, status transitions
- Audit Log Entries: immutable (never updated, new entries created for changes)
- Watcher Processes: in-memory state updated by Orchestrator
- Business Goals: current_value updated by CEO briefing skill

**Deletion**:
- Action Files: moved to /Done/Archive after 30 days
- Approval Requests: moved to /Done or /Rejected (no deletion)
- Plans: moved to /Plans/archive after completion
- Audit Log Entries: daily files deleted after 90 days
- Business Goals: never deleted (historical tracking)

**Archive**:
- /Done/Archive/YYYY-MM/ (monthly subfolders)
- /Logs/Archive/YYYY-MM.tar.gz (compressed logs >30 days)
- /Plans/archive/ (all completed plans)

---

## Next Steps

- Use this data model as reference for implementation
- Generate validation functions for each entity type
- Create unit tests for entity validation
- Document entity lifecycle state transitions
- Create entity relationship diagram (visual)
