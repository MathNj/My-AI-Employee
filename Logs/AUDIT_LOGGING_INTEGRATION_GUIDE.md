# Audit Logging Integration Guide

**Gold Tier Requirement 9: Comprehensive Audit Logging**

This guide shows how to integrate the centralized audit logger into any AI Employee skill or script.

## Quick Integration

### 1. Import the Audit Logger

```python
import sys
from pathlib import Path

# Add Logs directory to path
VAULT_PATH = Path(__file__).parent.parent.parent.parent / "AI_Employee_Vault"
sys.path.insert(0, str(VAULT_PATH / "Logs"))

try:
    from audit_logger import get_audit_logger
    HAS_AUDIT_LOGGER = True
except ImportError:
    HAS_AUDIT_LOGGER = False
```

### 2. Log Actions

```python
if HAS_AUDIT_LOGGER:
    audit_logger = get_audit_logger(VAULT_PATH.parent)

    audit_logger.log_action(
        action_type="email_send",         # Type of action
        actor="email_sender",             # Which skill performed it
        target="client@example.com",      # Who/what was affected
        parameters={                      # Action details
            "subject": "Invoice #123",
            "body_length": 500
        },
        approval_status="approved",       # "approved", "not_required", "rejected"
        approved_by="human",              # "human", "system", "auto"
        result="success",                 # "success", "failure", "error"
        error_message=None                # Error details if failed
    )
```

## Integration Examples

### Example 1: X/Twitter Poster

```python
# File: .claude/skills/x-poster/scripts/x_post.py

# Add at top of file after imports
import sys
from pathlib import Path

VAULT_PATH = Path(__file__).parent.parent.parent.parent / "AI_Employee_Vault"
sys.path.insert(0, str(VAULT_PATH / "Logs"))

try:
    from audit_logger import get_audit_logger
    HAS_AUDIT_LOGGER = True
except ImportError:
    HAS_AUDIT_LOGGER = False

# In execute_approved_post function, after successful post:
if HAS_AUDIT_LOGGER:
    try:
        audit_logger = get_audit_logger(VAULT_PATH.parent)
        audit_logger.log_action(
            action_type="x_post",
            actor="x_poster",
            target="X/Twitter",
            parameters={"message": tweet_text[:200], "char_count": len(tweet_text)},
            approval_status="approved",
            approved_by="human",
            result="success",
            metadata={"approval_file": approval_file.name}
        )
    except Exception as e:
        print(f"[WARNING] Audit logging failed: {e}", file=sys.stderr)

# On failure:
if HAS_AUDIT_LOGGER:
    try:
        audit_logger = get_audit_logger(VAULT_PATH.parent)
        audit_logger.log_action(
            action_type="x_post",
            actor="x_poster",
            target="X/Twitter",
            parameters={"message": tweet_text[:200], "char_count": len(tweet_text)},
            approval_status="approved",
            approved_by="human",
            result="failure",
            error_message=error_message,
            metadata={"approval_file": approval_file.name}
        )
    except Exception as e:
        print(f"[WARNING] Audit logging failed: {e}", file=sys.stderr)
```

### Example 2: Email Sender

```python
# File: .claude/skills/email-sender/scripts/send_email.py

# After successful email send:
if HAS_AUDIT_LOGGER:
    audit_logger = get_audit_logger(VAULT_PATH.parent)
    audit_logger.log_action(
        action_type="email_send",
        actor="email_sender",
        target=recipient_email,
        parameters={
            "subject": email_subject,
            "has_attachments": len(attachments) > 0,
            "attachment_count": len(attachments)
        },
        approval_status="approved",
        approved_by="human",
        result="success",
        metadata={"approval_file": approval_file.name}
    )
```

### Example 3: Watcher (Auto-Action, No Approval)

```python
# For automatic actions that don't require approval (e.g., task detection)

if HAS_AUDIT_LOGGER:
    audit_logger = get_audit_logger(VAULT_PATH.parent)
    audit_logger.log_auto_action(
        action_type="task_created",
        actor="gmail_watcher",
        target=f"Email from {sender}",
        parameters={
            "subject": email_subject,
            "priority": priority,
            "task_file": task_filename
        },
        result="success"
    )
```

## Action Types Reference

Use consistent action type names across the system:

| Action Type | Description | Actor Examples |
|-------------|-------------|----------------|
| `email_send` | Sending an email | `email_sender`, `approval_processor` |
| `linkedin_post` | Posting to LinkedIn | `linkedin_poster`, `social_media_manager` |
| `x_post` | Posting to X/Twitter | `x_poster`, `social_media_manager` |
| `instagram_post` | Posting to Instagram | `instagram_poster`, `social_media_manager` |
| `facebook_post` | Posting to Facebook | `facebook_poster`, `social_media_manager` |
| `task_created` | Creating a task file | `*_watcher` |
| `file_process` | Processing a file | `filesystem_watcher`, `task_processor` |
| `approval_requested` | Creating approval request | Any skill |
| `approval_granted` | Approval given | `approval_processor` |
| `approval_rejected` | Approval rejected | `approval_processor` |

## Approval Status Values

- `approved` - Human approved via approval workflow
- `not_required` - Action doesn't need approval
- `rejected` - Human rejected the request
- `pending` - Waiting for approval

## Approved By Values

- `human` - Manually approved by user (file moved to /Approved)
- `system` - Auto-approved by system logic
- `auto` - Auto-approved based on rules
- `user@example.com` - Specific user (if multi-user system)

## Result Values

- `success` - Action completed successfully
- `failure` - Action failed (expected failure, can retry)
- `error` - Unexpected error occurred
- `partial` - Partially completed

## Integration Checklist

When adding audit logging to a skill:

- [ ] Import audit logger at top of file
- [ ] Handle import failure gracefully (HAS_AUDIT_LOGGER flag)
- [ ] Log on successful execution
- [ ] Log on failure/error with error_message
- [ ] Use consistent action_type naming
- [ ] Include relevant parameters (but not sensitive data like passwords)
- [ ] Set correct approval_status
- [ ] Catch and handle audit logging exceptions (don't crash main execution)
- [ ] Test that audit logs are created in `Logs/audit_YYYY-MM-DD.json`

## Skills That Need Integration

### ✅ Completed
- `audit_logger.py` - Core utility (done)
- `approval-processor` - Logs all executed approvals (done)
- `linkedin-poster` - Logs LinkedIn posts (done)

### ⚠️ Pending Integration
- `x-poster/scripts/x_post.py` - Add audit logging for tweets
- `email-sender/scripts/send_email.py` - Add audit logging for emails
- `instagram-poster/scripts/instagram_post.py` - Add audit logging
- `facebook-poster/scripts/facebook_post.py` - Add audit logging
- `social-media-manager/scripts/*.py` - Add audit logging for all platforms

### 💡 Optional (Low Priority)
- `task-processor` - Log task processing
- `dashboard-updater` - Log dashboard updates
- `financial-analyst` - Log financial analysis runs

## Viewing Audit Logs

### CLI Query Tool

```bash
# View today's audit logs
python AI_Employee_Vault/Logs/audit_logger.py

# Or use Python:
from audit_logger import get_audit_logger

logger = get_audit_logger()

# Get all logs from last 7 days
logs = logger.get_audit_trail(
    start_date=datetime.now() - timedelta(days=7)
)

# Filter by action type
linkedin_posts = logger.get_audit_trail(action_type="linkedin_post")

# Generate report
report = logger.generate_audit_report()
print(f"Total actions: {report['total_actions']}")
print(f"Success rate: {report['success_rate']}")
```

### Direct File Access

Audit logs are stored in:
```
AI_Employee_Vault/Logs/audit_YYYY-MM-DD.json
```

Format:
```json
[
  {
    "timestamp": "2026-01-14T13:41:20.220375",
    "action_type": "email_send",
    "actor": "email_sender",
    "target": "client@example.com",
    "parameters": {
      "subject": "Invoice #123",
      "body_length": 500
    },
    "approval_status": "approved",
    "approved_by": "human",
    "result": "success"
  }
]
```

## Testing Audit Logging

```bash
# Test the audit logger
cd AI_Employee_Vault/Logs
python audit_logger.py

# Check logs were created
type audit_2026-01-14.json
```

## Maintenance

### Log Retention

Logs are retained for 90 days minimum (as per Requirements1.md).

To manually clean old logs:
```python
from audit_logger import get_audit_logger

logger = get_audit_logger()
deleted_count = logger.cleanup_old_logs(retention_days=90)
print(f"Deleted {deleted_count} old log files")
```

### Monitoring

Set up scheduled task to generate weekly audit reports:
```bash
# Weekly audit report (Sunday midnight)
python -c "from audit_logger import get_audit_logger; print(get_audit_logger().generate_audit_report())"
```

## Security Considerations

**DO log:**
- Action types and targets
- Timestamps
- Success/failure results
- Error messages
- Approval status

**DO NOT log:**
- Passwords or API keys
- Full email/message content (truncate to 200 chars)
- Personal identifying information (PII) unless necessary
- Credit card numbers or payment details

**Example - Good:**
```python
parameters={"subject": email_subject, "recipient": recipient_email}
```

**Example - Bad (DO NOT DO):**
```python
parameters={"subject": email_subject, "password": user_password, "full_body": entire_email_content}
```

## Support

For issues with audit logging:
1. Check `audit_YYYY-MM-DD.json` file exists in `Logs/`
2. Verify import is working: `HAS_AUDIT_LOGGER` should be `True`
3. Check for exceptions in skill output (warnings printed to stderr)
4. Test audit logger directly: `python AI_Employee_Vault/Logs/audit_logger.py`

---

**Status:** Gold Tier Requirement 9 - Partially Complete

**Next Steps:** Integrate audit logging into remaining skills (X poster, email sender, social media manager)
