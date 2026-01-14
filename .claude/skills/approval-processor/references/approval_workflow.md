# Approval Workflow Complete Guide

This document provides a comprehensive guide to the approval workflow system, including folder structure, file formats, and integration patterns.

## Overview

The approval workflow provides human-in-the-loop oversight for all external actions performed by the AI Employee. This ensures that no emails are sent, posts are published, or payments are made without explicit human approval.

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/     # Created by skills, awaiting human review
│   ├── EMAIL_*.md
│   ├── LINKEDIN_POST_*.md
│   └── PAYMENT_*.md (future)
│
├── Approved/             # Human moved here to approve
│   └── (files moved by human)
│
├── Rejected/             # Human moved here to reject
│   └── (files with rejection reasons)
│
├── Done/                 # Successfully executed actions
│   ├── EMAIL_*.md
│   └── LINKEDIN_POST_*.md
│
├── Expired/              # Expired before approval (>24 hours)
│   └── (auto-moved by check_expirations.py)
│
└── Failed/               # Failed execution attempts
    └── (moved after 3 retry attempts)
```

## Approval File Format

All approval request files use Markdown with YAML frontmatter:

```markdown
---
type: <action_type>
action: <specific_action>
created: <ISO 8601 timestamp>
expires: <ISO 8601 timestamp>
status: pending
<action-specific fields>
---

# Human-readable description

Details about what will happen when approved.

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

## Action Types

### Email Actions

**File naming:** `EMAIL_YYYY-MM-DDTHH-MM-SS.md`

**Required frontmatter:**
```yaml
type: email
action: send_email
to: "recipient@example.com"
subject: "Email subject"
body_full: |
  Complete email body content...
created: "2026-01-12T10:00:00Z"
expires: "2026-01-13T10:00:00Z"
status: pending
```

**Optional frontmatter:**
```yaml
cc: ["cc1@example.com", "cc2@example.com"]
bcc: ["bcc@example.com"]
attachments: ["/path/to/file.pdf", "/path/to/doc.docx"]
html: true
reply_to: "reply@example.com"
```

### LinkedIn Post Actions

**File naming:** `LINKEDIN_POST_YYYY-MM-DDTHH-MM-SS.md`

**Required frontmatter:**
```yaml
type: linkedin_post
action: post_to_linkedin
message: "Post content goes here..."
created: "2026-01-12T10:00:00Z"
expires: "2026-01-13T10:00:00Z"
status: pending
```

**Optional frontmatter:**
```yaml
hashtags: ["BusinessGrowth", "AI", "Automation"]
link_url: "https://example.com"
link_title: "Read more"
```

### Payment Actions (Future)

**File naming:** `PAYMENT_YYYY-MM-DDTHH-MM-SS.md`

**Required frontmatter:**
```yaml
type: payment
action: send_payment
recipient: "Client Name"
amount: 500.00
currency: "USD"
reference: "Invoice #1234"
created: "2026-01-12T10:00:00Z"
expires: "2026-01-13T10:00:00Z"
status: pending
```

## Workflow States

### 1. Creation (by Skills)

Skills create approval requests when they need to perform external actions:

```python
# Example: email-sender creates approval request
def create_approval_request(to, subject, body):
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    filename = f"EMAIL_{timestamp}.md"

    frontmatter = f"""---
type: email
action: send_email
to: "{to}"
subject: "{subject}"
body_full: |
  {body}
created: "{datetime.now().isoformat()}Z"
expires: "{(datetime.now() + timedelta(hours=24)).isoformat()}Z"
status: pending
---

# Email Approval Request

**To:** {to}
**Subject:** {subject}

## Email Content

{body}

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with reason.
"""

    filepath = PENDING_APPROVAL / filename
    filepath.write_text(frontmatter, encoding='utf-8')
    return filepath
```

### 2. Human Review

**Human reviews the file in /Pending_Approval and either:**

1. **Approves:** Moves file to /Approved
2. **Rejects:** Moves file to /Rejected and adds rejection reason
3. **Ignores:** Leaves in /Pending_Approval (will expire after 24 hours)

**Adding rejection reason:**

Edit the file and add to frontmatter:
```yaml
rejection_reason: "Content not appropriate"
rejected_by: "Your Name"
rejected_at: "2026-01-12T14:30:00Z"
```

### 3. Execution (by approval-processor)

The approval-processor monitors /Approved folder:

**One-time processing:**
```bash
python scripts/process_approvals.py
```

**Continuous monitoring:**
```bash
python scripts/approval_watcher.py
```

**What happens:**
1. Detects new file in /Approved
2. Parses action type from frontmatter
3. Routes to appropriate executor:
   - `type: email` → calls email-sender
   - `type: linkedin_post` → calls linkedin-poster
4. Executor performs the action
5. On success: moves file to /Done
6. On failure: retries up to 3 times, then moves to /Failed

### 4. Completion

**Success:** File moved to /Done with execution log
**Failure:** File moved to /Failed with error details

## Expiration Handling

### Automatic Expiration

Approval requests expire 24 hours after creation by default.

**Check for expirations:**
```bash
python scripts/check_expirations.py
```

**Move expired to /Expired:**
```bash
python scripts/check_expirations.py --move
```

**Custom expiration time:**
```bash
python scripts/check_expirations.py --hours 48 --move
```

### Manual Extension

To extend expiration, edit the file and update the `expires` field:

```yaml
expires: "2026-01-14T10:00:00Z"  # Extended by 1 day
```

## Integration Patterns

### Pattern 1: Direct Skill Integration

Skill creates approval request directly:

```python
# In skill script
from pathlib import Path
from datetime import datetime, timedelta

def request_approval(action_type, **params):
    """Create approval request."""
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    filename = f"{action_type.upper()}_{timestamp}.md"

    # Build frontmatter from params
    frontmatter = "---\n"
    frontmatter += f"type: {action_type}\n"
    for key, value in params.items():
        frontmatter += f"{key}: {value}\n"
    frontmatter += f"created: {datetime.now().isoformat()}Z\n"
    frontmatter += f"expires: {(datetime.now() + timedelta(hours=24)).isoformat()}Z\n"
    frontmatter += "status: pending\n"
    frontmatter += "---\n\n"

    # Add human-readable body
    frontmatter += f"# {action_type.title()} Approval Request\n\n"
    frontmatter += "Move to /Approved to execute.\n"

    filepath = Path("Pending_Approval") / filename
    filepath.write_text(frontmatter, encoding='utf-8')
    return filepath
```

### Pattern 2: Skill with Dual Mode

Skills support both approval and direct execution modes:

```python
# email-sender example
def send_email(to, subject, body, create_approval=True, execute_approved=None):
    """
    Send email with approval workflow support.

    Args:
        create_approval: Create approval request instead of sending
        execute_approved: Execute from approved file path
    """
    if execute_approved:
        # Execution mode (called by approval-processor)
        # Parse file, send email, log result
        pass
    elif create_approval:
        # Approval mode (default)
        # Create approval request file
        create_approval_request(to, subject, body)
    else:
        # Direct mode (manual override)
        # Send immediately without approval
        send_via_smtp(to, subject, body)
```

**CLI support:**
```bash
# Create approval request (default)
python send_email.py --to "user@example.com" --subject "Test"

# Execute approved file
python send_email.py --execute-approved /path/to/approved.md

# Direct send (bypass approval - use with caution)
python send_email.py --to "user@example.com" --direct
```

### Pattern 3: Dashboard Integration

Display approval queue status in Dashboard.md:

```bash
# Update dashboard with pending count
python scripts/check_status.py --json | jq '.pending_approval.count'
```

## Best Practices

### For Skill Developers

1. **Always use approval workflow by default**
   - Only allow direct execution with explicit `--force` or `--direct` flag
   - Log warning when bypassing approval

2. **Provide rich approval context**
   - Include preview of what will happen
   - Show full email body, post content, etc.
   - Add clear approve/reject instructions

3. **Set appropriate expiration**
   - Default 24 hours for most actions
   - Shorter (2-4 hours) for time-sensitive items
   - Longer (48-72 hours) for complex reviews

4. **Support `--execute-approved` mode**
   - All action skills must support execution from approved files
   - Parse frontmatter, perform action, return success/failure

### For Human Reviewers

1. **Review daily minimum**
   - Check /Pending_Approval 2-3 times per day
   - Prevents expirations and keeps AI responsive

2. **Add rejection reasons**
   - Always document why you rejected
   - Helps AI learn patterns over time

3. **Be wary of:**
   - New recipients (emails, payments)
   - Large amounts (payments)
   - Bulk operations (mass emails, social posts)
   - Unusual timing (middle of night)

4. **Archive regularly**
   - Move /Done items older than 30 days to archive
   - Keep /Rejected for pattern analysis

## Security Considerations

### Approval Thresholds

Configure auto-approve thresholds in Company_Handbook.md:

```markdown
## Approval Thresholds

### Email
- Auto-approve: Replies to known contacts (in address book)
- Require approval: New contacts, bulk sends (>5 recipients)

### LinkedIn Posts
- Auto-approve: Scheduled posts reviewed in advance
- Require approval: All real-time posts

### Payments
- Auto-approve: Recurring payments under $50 to verified payees
- Require approval: All new payees, amounts >$100
```

### Audit Trail

All approval actions are logged:

```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "approval_executed",
  "details": {
    "file": "EMAIL_2026-01-12T10-00-00.md",
    "type": "email",
    "executor": "email-sender",
    "status": "success",
    "approved_by": "human",
    "execution_time": "2.3s"
  }
}
```

### Preventing Approval Bypass

1. **File permissions:** Ensure only human can write to /Approved
2. **Code review:** Audit skills for `--force` flags
3. **Logging:** Log all direct executions as warnings
4. **Monitoring:** Alert on high direct execution rates

## Troubleshooting

### Files Not Being Processed

**Symptom:** File in /Approved but not executing

**Solutions:**
1. Check approval-processor is running: `ps aux | grep approval`
2. Verify frontmatter format (valid YAML)
3. Check executor script exists and is executable
4. Review logs: `cat Logs/approval_activity_*.json`

### Expirations Too Fast

**Symptom:** Files expiring before you can review

**Solutions:**
1. Increase expiration time: edit `EXPIRATION_HOURS` in config
2. Check more frequently (2-3x daily minimum)
3. Set up notifications for new approvals
4. Manually extend `expires` field for complex reviews

### Executor Errors

**Symptom:** Files moved to /Failed

**Solutions:**
1. Check error in activity log
2. Test executor directly: `python scripts/send_email.py --execute-approved file.md`
3. Verify credentials configured correctly
4. Check network connectivity
5. Move back to /Approved to retry

---

**Related Documentation:**
- See `action_types.md` for detailed action specifications
- See `error_recovery.md` for failure handling
- See main `SKILL.md` for overview and quick start
