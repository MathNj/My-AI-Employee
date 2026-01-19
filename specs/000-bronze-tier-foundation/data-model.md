# Data Model: Bronze Tier Foundation

**Feature**: Bronze Tier Foundation - Personal AI Employee
**Date**: 2026-01-17
**Status**: Phase 1 Design Complete

This document defines the data entities, relationships, and validation rules for Bronze Tier implementation.

---

## Overview

Bronze Tier uses **file-based data storage** with no database. All entities are represented as files (markdown, YAML, logs) in the Obsidian vault or watchers/ directory.

**Storage Strategy**:
- **Action Files**: Markdown with YAML frontmatter in /Needs_Action → /Done
- **Dashboard**: Single markdown file with append-only activity log
- **Company Handbook**: Single markdown file with business rules
- **Watcher State**: In-memory (process state) + file-based logs
- **Configuration**: YAML files (watcher_config.yaml)

---

## Entity Definitions

### 1. Action File

**Description**: Markdown file representing a detected event that requires processing by Claude Code.

**Storage Location**:
- Created in: `/Needs_Action/`
- Archived in: `/Done/` (after processing)
- Errors moved to: `/Errors/` (if malformed)

**File Naming Convention**:
```
{SOURCE}_{TIMESTAMP}_{IDENTIFIER}.md

Examples:
- FILE_20260117_143000_invoice-pdf.md
- EMAIL_20260117_090030_abc123xyz.md
- MANUAL_20260117_120000_client-followup.md
```

**File Structure**:
```markdown
---
type: email | file | scheduled
source: Gmail | FileSystem | Manual
timestamp: 2026-01-17T14:30:00Z
status: pending | processing | complete | error
payload:
  # Event-specific fields (see below)
processing_metadata:
  started_at: null
  completed_at: null
  processing_time_sec: null
  claude_model: null
  outcome: null
---

# Event Body

[Event-specific content - email text, file summary, task description]
```

**Payload Schemas by Type**:

**Email Event**:
```yaml
payload:
  sender: sender@example.com
  subject: "Invoice #1234"
  message_id: "abc123xyz"
  snippet: "First 100 chars of email body..."
  labels: ["INBOX", "IMPORTANT"]
  has_attachments: true
```

**File Event**:
```yaml
payload:
  filename: "invoice_jan_2026.pdf"
  path: "/vault/Inbox/invoice_jan_2026.pdf"
  size_bytes: 245678
  mime_type: "application/pdf"
  created_at: "2026-01-17T14:25:00Z"
```

**Manual Event**:
```yaml
payload:
  task_description: "Follow up with Client A on proposal"
  priority: high | medium | low
  due_date: "2026-01-20"
  context: "Proposal sent on Jan 10, no response yet"
```

**State Transitions**:
```
pending → processing → complete (move to /Done)
pending → processing → error (move to /Errors, log reason)
```

**Validation Rules**:
1. **type** MUST be one of: email, file, scheduled
2. **source** MUST be one of: Gmail, FileSystem, Manual
3. **timestamp** MUST be ISO 8601 format with timezone
4. **status** MUST be one of: pending, processing, complete, error
5. Payload MUST contain required fields for event type
6. File name MUST match naming convention

**Processing Metadata** (added by task-processor skill):
```yaml
processing_metadata:
  started_at: "2026-01-17T14:31:00Z"
  completed_at: "2026-01-17T14:32:30Z"
  processing_time_sec: 90
  claude_model: "claude-sonnet-4-5"
  outcome: "Invoice categorized, email reply drafted in /Pending_Approval"
```

---

### 2. Dashboard Entry

**Description**: Single line in Dashboard.md activity log showing task completion summary.

**Storage Location**: `/Dashboard.md` (activity log section)

**Entry Format**:
```markdown
- 2026-01-17 14:32 | EMAIL | Invoice #1234 processed → reply drafted | ✅ Complete
- 2026-01-17 13:15 | FILE  | invoice_jan_2026.pdf categorized as expense | ✅ Complete
- 2026-01-17 10:05 | EMAIL | Meeting request from Client A | ❌ Error: No calendar access
```

**Structure**:
```
- {timestamp} | {task_type} | {summary} | {status_icon} {outcome}
```

**Fields**:
- **timestamp**: YYYY-MM-DD HH:MM (local time, 24-hour format)
- **task_type**: EMAIL | FILE | MANUAL | SCHEDULED (uppercase, fixed width for alignment)
- **summary**: Human-readable description of task (50-100 chars)
- **status_icon**: ✅ (complete), ❌ (error), ⏸️ (pending approval)
- **outcome**: Brief result description

**Dashboard.md Full Structure**:
```markdown
---
last_updated: 2026-01-17T14:32:00Z
vault_version: bronze_tier_v1
---

# AI Employee Dashboard

## Current Status

**Watcher**: Running (last check: 2026-01-17 14:30)
**Pending Tasks**: 3 files in /Needs_Action
**Completed Today**: 12 tasks
**Error Rate**: 1/13 (7.7%)

## Activity Log

Most recent entries (newest first):

- 2026-01-17 14:32 | EMAIL | Invoice #1234 processed → reply drafted | ✅ Complete
- 2026-01-17 13:15 | FILE  | invoice_jan_2026.pdf categorized as expense | ✅ Complete
...

## Task Summary (Last 24 Hours)

| Type | Count | Success Rate |
|------|-------|--------------|
| EMAIL | 8 | 100% |
| FILE | 4 | 75% |
| MANUAL | 1 | 100% |

---
*Dashboard managed by dashboard-updater skill. Archive entries when log exceeds 1000 lines.*
```

**Update Strategy**:
- **Append-only**: New entries prepended to activity log section (newest first)
- **No parsing**: Find "## Activity Log" marker, insert after first blank line
- **Atomic write**: Read entire file, modify in memory, write atomically
- **Manual archiving**: User cuts old entries when >1000 lines

---

### 3. Watcher Process

**Description**: Python script running in background that monitors for events and creates action files.

**Storage Location**:
- Source code: `/watchers/gmail_watcher.py` or `/watchers/filesystem_watcher.py`
- Configuration: `/watchers/watcher_config.yaml`
- Process state: In-memory (PID, last check time, event count)
- Logs: `/vault/Logs/watcher_YYYY-MM-DD.log`

**Watcher State** (in-memory):
```python
@dataclass
class WatcherState:
    watcher_type: str  # "Gmail" | "FileSystem"
    pid: int
    started_at: datetime
    last_check_at: datetime
    check_count: int
    events_detected: int
    errors_count: int
    status: str  # "running" | "stopped" | "error"
```

**Configuration Schema** (watcher_config.yaml):
```yaml
gmail_watcher:
  enabled: false
  check_interval_sec: 120  # 2 minutes
  max_results: 10
  labels: ["INBOX"]
  credentials_path: .env
  vault_path: /absolute/path/to/vault

filesystem_watcher:
  enabled: true
  check_interval_sec: 30
  watched_path: /absolute/path/to/vault/Inbox
  recursive: false
  vault_path: /absolute/path/to/vault
  file_filters:
    - "*.pdf"
    - "*.docx"
    - "*.txt"
    - "*.md"
```

**Log Entry Format**:
```
2026-01-17 14:30:00 | INFO | FileSystem watcher started (PID: 12345)
2026-01-17 14:30:30 | INFO | Check cycle #1 complete - 0 new files detected
2026-01-17 14:31:00 | INFO | Check cycle #2 complete - 1 new file detected: invoice_jan.pdf
2026-01-17 14:31:05 | INFO | Action file created: FILE_20260117_143100_invoice-jan.md
2026-01-17 14:31:30 | ERROR | Failed to create action file for test.tmp: Permission denied
```

**Health Indicators**:
- Last check timestamp (should update every check_interval_sec)
- Error rate (<5% acceptable)
- Process uptime (24 hours continuous for Bronze tier validation)

---

### 4. Skill Definition

**Description**: SKILL.md file defining a reusable Claude Code capability.

**Storage Location**: `/.claude/commands/{skill-name}.md`

**File Structure** (following Agent Skills format):
```markdown
# Skill: {skill-name}

## Description

[1-2 sentences describing what this skill does]

## Input Parameters

- **parameter_name** (type): Description [required/optional]
- **another_param** (type): Description [required/optional, default: value]

## Output

[Description of what this skill produces - files created, updates made, return values]

## Usage Examples

### Example 1: [Scenario]
\`\`\`
/skill-name --param1 value1 --param2 value2
\`\`\`

Expected output:
- File created at /path/to/output
- Dashboard updated with entry

### Example 2: [Another scenario]
\`\`\`
/skill-name --param1 different_value
\`\`\`

## Implementation Notes

[Technical details, edge cases, assumptions]

## Error Handling

[Common errors and how skill handles them]
```

**Bronze Tier Skills**:

**1. vault-setup**:
```markdown
# Skill: vault-setup

## Description
Initialize Obsidian vault structure with folders, Dashboard.md, and Company_Handbook.md templates.

## Input Parameters
- **vault_path** (string): Absolute path to Obsidian vault directory [required]

## Output
Creates:
- Folders: /Inbox, /Needs_Action, /Done, /Errors, /Logs
- Dashboard.md with template structure
- Company_Handbook.md with business rules template

## Usage Example
\`\`\`
/vault-setup --vault_path "/Users/name/Documents/AI_Employee_Vault"
\`\`\`

## Error Handling
- If vault_path doesn't exist: Create directory structure
- If files already exist: Prompt user to overwrite or skip
- If permissions denied: Exit with clear error message
```

**2. task-processor**:
```markdown
# Skill: task-processor

## Description
Process all action files in /Needs_Action, execute tasks, move completed files to /Done.

## Input Parameters
- **vault_path** (string): Absolute path to Obsidian vault directory [required]
- **max_files** (integer): Maximum files to process in one run [optional, default: 50]

## Output
- Processes action files sequentially (oldest first)
- Updates Dashboard.md activity log
- Moves completed files to /Done with processing metadata
- Moves malformed files to /Errors with validation errors

## Usage Example
\`\`\`
/task-processor --vault_path "/path/to/vault" --max_files 10
\`\`\`

## Error Handling
- Malformed YAML frontmatter: Move to /Errors, log validation error
- Missing required fields: Move to /Errors, document missing fields
- Processing failure: Keep in /Needs_Action with error status, log details
- Vault locked: Wait and retry up to 3 times
```

**3. dashboard-updater**:
```markdown
# Skill: dashboard-updater

## Description
Refresh Dashboard.md current status section with live system metrics.

## Input Parameters
- **vault_path** (string): Absolute path to Obsidian vault directory [required]

## Output
Updates Dashboard.md:
- Watcher status (running/stopped, last check time)
- Pending tasks count (/Needs_Action file count)
- Completed today count (activity log entries with today's date)
- Error rate calculation

## Usage Example
\`\`\`
/dashboard-updater --vault_path "/path/to/vault"
\`\`\`

## Error Handling
- Watcher log missing: Report "Unknown" status
- Dashboard.md missing: Recreate from template
- Cannot parse activity log: Report "Parse error, manual inspection needed"
```

---

### 5. Company Handbook

**Description**: Central markdown document containing business rules, decision guidelines, and context for Claude Code.

**Storage Location**: `/Company_Handbook.md`

**Structure**:
```markdown
---
version: bronze_tier_v1
last_updated: 2026-01-17
business_type: [consulting|product|service|freelance]
---

# Company Handbook

## Business Overview

**Name**: [Your Business Name]
**Type**: Consulting / Product / Service / Freelance
**Primary Services**:
- Service 1
- Service 2

## Decision-Making Guidelines

### Email Triage Rules

- **Urgent**: Client emails with "urgent" or "ASAP" → flag for immediate attention
- **Invoice**: Emails with "invoice" or "payment" → categorize as finance
- **Meeting**: Calendar invites or meeting requests → extract date/time, check availability
- **General**: Everything else → standard processing

### Approval Thresholds

- **Requires Human Approval**:
  - Financial transactions over $100
  - Contract commitments
  - Client-facing communications (emails, proposals)
  - Data deletion or modification

- **Auto-Approve**:
  - Categorizing documents
  - Creating summaries
  - Logging activities
  - Updating internal notes

## Key Contacts

| Name | Role | Email | Priority |
|------|------|-------|----------|
| John Doe | Primary Client | john@client.com | High |
| Jane Smith | Vendor | jane@vendor.com | Medium |

## Business Rules

### Work Hours
- Standard hours: 9 AM - 5 PM EST
- After-hours emails: Auto-categorize, process next business day
- Urgent exceptions: Client A, Client B (always process immediately)

### Financial Rules
- Invoice payment terms: Net 30
- Late payment follow-up: 3 days after due date
- Expense categorization: Use categories from accounting system

### Communication Style
- Professional but friendly
- Response time target: <24 hours for clients, <48 hours for general
- Always include "Best regards," signature

## Subscription Inventory

Track active subscriptions for weekly audit:

| Service | Cost/Month | Renewal Date | Login Last Used | Status |
|---------|------------|--------------|-----------------|--------|
| Adobe Creative Cloud | $54.99 | 15th | 2026-01-10 | Active |
| Notion | $10.00 | 1st | 2026-01-16 | Active |

## Project Context

### Active Projects

**Project Alpha**:
- Client: Client A
- Due Date: 2026-02-15
- Budget: $5,000
- Status: In progress - 60% complete
- Key Deliverables: Report, presentation

## Notes for AI Employee

- When in doubt about client communication, draft but mark for approval
- Always log financial decisions in activity log
- Check Company_Handbook.md for latest business rules before processing
- Update subscription inventory when detecting new recurring charges
```

**Usage by Claude Code**:
- Read at start of each task-processor invocation
- Reference decision guidelines for email triage, approval thresholds
- Use contact list for prioritization
- Update subscription inventory when processing financial data

---

## Entity Relationships

```
Watcher Process
  ├── monitors → Events (emails, files)
  ├── creates → Action Files (in /Needs_Action)
  └── writes → Watcher Logs (in /Logs)

Action File
  ├── created by → Watcher Process
  ├── processed by → task-processor skill
  ├── references → Company Handbook (for business rules)
  └── generates → Dashboard Entry

Dashboard Entry
  ├── written by → task-processor skill
  └── summarized by → dashboard-updater skill

Skill Definition
  ├── invoked by → User (manual) or future orchestrator
  ├── reads → Action Files, Company Handbook
  └── writes → Action Files (status updates), Dashboard

Company Handbook
  ├── read by → task-processor skill
  ├── updated by → User (manual)
  └── provides context for → All skills
```

---

## Validation Rules

### Action File Validation

Implemented in task-processor skill:

```python
def validate_action_file(file_path):
    """Validate action file format and required fields."""
    try:
        # Parse frontmatter
        with open(file_path) as f:
            post = frontmatter.load(f)

        # Required fields
        required = ['type', 'source', 'timestamp', 'status', 'payload']
        for field in required:
            if field not in post.metadata:
                raise ValidationError(f"Missing required field: {field}")

        # Type validation
        if post['type'] not in ['email', 'file', 'scheduled']:
            raise ValidationError(f"Invalid type: {post['type']}")

        if post['source'] not in ['Gmail', 'FileSystem', 'Manual']:
            raise ValidationError(f"Invalid source: {post['source']}")

        if post['status'] not in ['pending', 'processing', 'complete', 'error']:
            raise ValidationError(f"Invalid status: {post['status']}")

        # Timestamp format (ISO 8601)
        datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))

        # Payload validation by type
        if post['type'] == 'email':
            email_required = ['sender', 'subject', 'message_id']
            for field in email_required:
                if field not in post['payload']:
                    raise ValidationError(f"Missing email payload field: {field}")

        return True, None

    except Exception as e:
        return False, str(e)
```

### Configuration Validation

Implemented in base_watcher.py:

```python
def validate_config(config):
    """Validate watcher configuration."""
    errors = []

    # Required fields
    if 'check_interval_sec' not in config:
        errors.append("Missing check_interval_sec")
    elif config['check_interval_sec'] < 10:
        errors.append("check_interval_sec must be >= 10 seconds")

    if 'vault_path' not in config:
        errors.append("Missing vault_path")
    elif not Path(config['vault_path']).exists():
        errors.append(f"vault_path does not exist: {config['vault_path']}")

    return len(errors) == 0, errors
```

---

## File Format Examples

### Complete Action File Example

**Filename**: `EMAIL_20260117_143000_abc123.md`

```markdown
---
type: email
source: Gmail
timestamp: 2026-01-17T14:30:00Z
status: pending
payload:
  sender: client@example.com
  subject: "Invoice #1234 for January Services"
  message_id: "abc123xyz"
  snippet: "Hi, attached is the invoice for January consulting services..."
  labels: ["INBOX", "IMPORTANT"]
  has_attachments: true
processing_metadata:
  started_at: null
  completed_at: null
  processing_time_sec: null
  claude_model: null
  outcome: null
---

# Email from client@example.com

**Subject**: Invoice #1234 for January Services

**Received**: 2026-01-17 14:30 UTC

**Body**:
Hi,

Attached is the invoice for January consulting services. Please process payment at your earliest convenience.

Invoice #1234
Amount: $5,000.00
Due Date: 2026-02-16

Let me know if you have any questions.

Best regards,
Client Name

**Attachments**:
- invoice_1234.pdf (124KB)
```

---

## Data Flow Diagram

```
[Event Source] → [Watcher] → [Action File] → [Task Processor] → [Dashboard]
                                                                      ↓
                                                                [Done Archive]

Detailed flow:
1. Event occurs (email arrives, file dropped in Inbox)
2. Watcher detects event during check cycle
3. Watcher creates action file in /Needs_Action with metadata
4. User invokes task-processor skill
5. Task processor:
   a. Reads Company Handbook for business rules
   b. Parses action file frontmatter
   c. Executes task based on type
   d. Updates processing_metadata
   e. Appends entry to Dashboard activity log
   f. Moves file to /Done
6. dashboard-updater skill refreshes Dashboard status section
```

---

## Storage Estimates

**Bronze Tier Scale** (50 action files/day):

| Entity | Storage Per Item | Daily Volume | Monthly Storage |
|--------|-----------------|--------------|-----------------|
| Action File | ~5 KB | 50 files | 7.5 MB |
| Dashboard Entry | ~150 bytes | 50 entries | 7.5 KB/day → 225 KB/month |
| Watcher Log | ~200 bytes/check | 2,880 checks | ~576 KB/day → 17 MB/month |
| Error Log | ~500 bytes/error | 2-3 errors | ~1.5 KB/day → 45 KB/month |

**Total Monthly Storage**: ~25 MB (well within Bronze tier <1GB vault size limit)

**Manual Archiving Triggers**:
- Action files in /Done: Archive monthly to /Done/archive_YYYY-MM/
- Dashboard activity log: Archive when >1000 entries (~20 days at 50/day)
- Watcher logs: Archive weekly to /Logs/archive/watcher_YYYY-MM-DD.log

---

**Data Model Complete**: All entities defined with validation rules, storage formats, and relationships. Ready for contract specifications in Phase 1.
