# Error Recovery Guide

Comprehensive guide for handling errors, failures, and recovery scenarios in the approval workflow system.

## Error Categories

### 1. Transient Errors

**Definition:** Temporary failures that may succeed on retry.

**Examples:**
- Network timeouts
- API rate limits
- Temporary service unavailability
- SMTP connection failures

**Recovery Strategy:** Automatic retry with exponential backoff

**Implementation:**
```python
# In process_approvals.py
MAX_RETRIES = 3
RETRY_DELAYS = [0, 30, 60]  # seconds

for attempt in range(MAX_RETRIES):
    try:
        result = execute_action()
        return True
    except TransientError:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAYS[attempt])
            continue
        raise
```

### 2. Authentication Errors

**Definition:** Credential or permission failures.

**Examples:**
- Expired OAuth tokens
- Invalid SMTP passwords
- Revoked API access
- Missing permissions

**Recovery Strategy:** Alert human, pause operations

**Indicators:**
- HTTP 401 Unauthorized
- HTTP 403 Forbidden
- SMTP 535 Authentication failed
- OAuth token expired

**Actions:**
1. Move affected file to /Failed
2. Log detailed error
3. Alert human via Dashboard
4. Pause further attempts for this action type
5. Wait for credential refresh

**Example Error Log:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "approval_failed",
  "error_type": "authentication",
  "details": {
    "file": "EMAIL_2026-01-12T10-00-00.md",
    "error": "SMTP Authentication failed: Invalid credentials",
    "service": "Gmail SMTP",
    "resolution": "Check SMTP password in credentials file"
  }
}
```

### 3. Validation Errors

**Definition:** Invalid data or configuration.

**Examples:**
- Invalid email addresses
- Missing required fields
- File not found (attachments)
- Malformed frontmatter

**Recovery Strategy:** Move to /Failed, alert human

**No retry:** These errors won't fix themselves

**Example:**
```python
def validate_email_action(metadata):
    """Validate email action metadata."""
    errors = []

    # Check required fields
    if 'to' not in metadata:
        errors.append("Missing 'to' field")

    # Validate email format
    if not is_valid_email(metadata.get('to')):
        errors.append(f"Invalid email: {metadata.get('to')}")

    # Check attachments exist
    for attachment in metadata.get('attachments', []):
        if not Path(attachment).exists():
            errors.append(f"Attachment not found: {attachment}")

    if errors:
        raise ValidationError(errors)
```

### 4. Logic Errors

**Definition:** Claude misinterpreted requirements.

**Examples:**
- Wrong recipient
- Incorrect email subject
- Inappropriate post content
- Mismatched amounts

**Recovery Strategy:** Human review queue

**Prevention:**
- Clear approval request formatting
- Preview of actual action
- Checkboxes for verification

### 5. System Errors

**Definition:** Infrastructure or process failures.

**Examples:**
- approval-processor crashed
- Disk full
- Permission denied
- Out of memory

**Recovery Strategy:** Watchdog + auto-restart

---

## Retry Logic

### Exponential Backoff

```python
def execute_with_retry(func, max_attempts=3, base_delay=1, max_delay=60):
    """Execute function with exponential backoff retry."""
    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise  # Last attempt, give up

            # Calculate delay: 1s, 2s, 4s, 8s, etc.
            delay = min(base_delay * (2 ** attempt), max_delay)

            print(f"Attempt {attempt + 1} failed: {e}")
            print(f"Retrying in {delay}s...")
            time.sleep(delay)

    raise MaxRetriesExceeded(f"Failed after {max_attempts} attempts")
```

### Retry Configuration

**Per-action type settings:**

```python
RETRY_CONFIG = {
    'email': {
        'max_attempts': 3,
        'base_delay': 30,
        'max_delay': 300,
        'retryable_errors': [
            'NetworkTimeout',
            'ConnectionRefused',
            'SMTPServerDisconnected'
        ]
    },
    'linkedin_post': {
        'max_attempts': 2,  # Fewer retries for social posts
        'base_delay': 60,
        'max_delay': 600,
        'retryable_errors': [
            'NetworkTimeout',
            'RateLimitExceeded'
        ]
    },
    'payment': {
        'max_attempts': 1,  # NO automatic retry for payments
        'base_delay': 0,
        'max_delay': 0,
        'retryable_errors': []  # Empty - no retries
    }
}
```

### When NOT to Retry

**Never retry automatically:**
1. **Payments:** Risk of duplicate transactions
2. **Delete operations:** Risk of data loss
3. **Authentication errors:** Won't fix themselves
4. **Validation errors:** Data is still invalid

---

## Failed Action Recovery

### Manual Retry Process

**Step 1: Identify failure**
```bash
# Check failed folder
ls Failed/

# View failure details in logs
cat Logs/approval_activity_2026-01-12.json | grep "approval_failed"
```

**Step 2: Diagnose issue**
```bash
# Read the failed file
cat Failed/EMAIL_2026-01-12T10-00-00.md

# Check error log entry
# Look for error_type and resolution steps
```

**Step 3: Fix root cause**

Common fixes:
- **Authentication:** Update credentials
- **Network:** Wait for connectivity
- **Validation:** Edit file, fix invalid data
- **Missing files:** Add attachments

**Step 4: Retry**

```bash
# Move back to Approved for automatic retry
mv Failed/EMAIL_2026-01-12T10-00-00.md Approved/

# Or retry manually with executor
python .claude/skills/email-sender/scripts/send_email.py \
  --execute-approved Failed/EMAIL_2026-01-12T10-00-00.md
```

### Bulk Recovery

**Retry all failed emails:**
```bash
# Create retry script
cat > retry_failed_emails.sh << 'EOF'
#!/bin/bash
for file in Failed/EMAIL_*.md; do
  echo "Retrying: $file"
  mv "$file" Approved/
  sleep 5  # Wait for processing
done
EOF

chmod +x retry_failed_emails.sh
./retry_failed_emails.sh
```

---

## Graceful Degradation

### Service Outage Handling

**When Gmail API is down:**
```python
def send_email_with_fallback(to, subject, body):
    """Send email with fallback to SMTP if API fails."""
    try:
        # Try MCP/API first
        send_via_api(to, subject, body)
    except APIError:
        print("API unavailable, falling back to SMTP...")
        send_via_smtp(to, subject, body)
```

**When LinkedIn API is down:**
```python
def post_with_queue(message):
    """Queue post if API unavailable."""
    try:
        post_to_linkedin(message)
    except APIError:
        # Queue for later
        queue_path = Path("Queued_Posts")
        queue_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        queued_file = queue_path / f"QUEUED_POST_{timestamp}.md"
        queued_file.write_text(message)

        print("LinkedIn unavailable - post queued for later")
```

### Partial Failure Handling

**Sending email with multiple attachments:**
```python
def send_email_with_attachments(to, subject, body, attachments):
    """Handle partial attachment failures gracefully."""
    successful_attachments = []
    failed_attachments = []

    # Try to attach each file
    for attachment in attachments:
        try:
            attach_file(attachment)
            successful_attachments.append(attachment)
        except FileNotFoundError:
            failed_attachments.append(attachment)

    # Send with available attachments
    if successful_attachments or not attachments:
        send_email(to, subject, body, successful_attachments)

        # Report partial failure
        if failed_attachments:
            log_warning(f"Email sent but {len(failed_attachments)} attachments failed")
            return 'partial_success'

        return 'success'
    else:
        # No attachments succeeded
        raise AllAttachmentsFailed(failed_attachments)
```

---

## Monitoring and Alerts

### Failure Rate Monitoring

```python
def calculate_failure_rate(period_hours=24):
    """Calculate failure rate for last N hours."""
    cutoff = datetime.now() - timedelta(hours=period_hours)

    # Count attempts and failures
    total_attempts = 0
    failures = 0

    for log_file in sorted(Path("Logs").glob("approval_activity_*.json")):
        with open(log_file) as f:
            logs = json.load(f)

        for entry in logs:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            if timestamp < cutoff:
                continue

            if entry['action'] in ['approval_executed', 'approval_failed']:
                total_attempts += 1

            if entry['action'] == 'approval_failed':
                failures += 1

    if total_attempts == 0:
        return 0.0

    return (failures / total_attempts) * 100
```

### Alert Thresholds

**Configure in Company_Handbook.md:**

```markdown
## Error Alert Thresholds

Alert human when:
- Failure rate > 20% (over 24 hours)
- 3+ consecutive failures (same action type)
- Any authentication error
- Any payment failure
- Disk usage > 90%
```

### Alert Implementation

```python
def check_and_alert():
    """Check for alert conditions."""
    failure_rate = calculate_failure_rate()

    if failure_rate > 20:
        create_alert(
            title="High Failure Rate",
            message=f"Approval execution failure rate: {failure_rate:.1f}%",
            severity="warning",
            action="Review logs and check service status"
        )

def create_alert(title, message, severity, action):
    """Create alert file for human review."""
    alert_file = Path("Alerts") / f"ALERT_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.md"
    alert_file.parent.mkdir(exist_ok=True)

    content = f"""---
title: {title}
severity: {severity}
created: {datetime.now().isoformat()}
status: new
---

# {title}

**Severity:** {severity}

## Message
{message}

## Recommended Action
{action}

## To Acknowledge
Move to Alerts/Acknowledged/
"""

    alert_file.write_text(content)
    print(f"⚠️  Alert created: {title}")
```

---

## Process Management

### Watchdog Implementation

```python
#!/usr/bin/env python3
"""
Watchdog - Monitor and restart critical processes.
"""

import subprocess
import time
from pathlib import Path

PROCESSES = {
    'approval_watcher': {
        'command': 'python .claude/skills/approval-processor/scripts/approval_watcher.py',
        'pid_file': '/tmp/approval_watcher.pid',
        'critical': True
    }
}

def is_running(pid_file):
    """Check if process is running."""
    if not Path(pid_file).exists():
        return False

    try:
        pid = int(Path(pid_file).read_text().strip())
        os.kill(pid, 0)  # Check if process exists
        return True
    except (ValueError, OSError):
        return False

def start_process(name, config):
    """Start a process."""
    print(f"Starting {name}...")

    proc = subprocess.Popen(
        config['command'].split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    Path(config['pid_file']).write_text(str(proc.pid))
    print(f"✅ Started {name} (PID: {proc.pid})")

    return proc

def monitor():
    """Monitor and restart processes."""
    print("👁️  Watchdog started")

    while True:
        for name, config in PROCESSES.items():
            if not is_running(config['pid_file']):
                print(f"⚠️  {name} not running!")

                if config['critical']:
                    start_process(name, config)
                    create_alert(
                        f"Process Restarted: {name}",
                        f"{name} crashed and was automatically restarted",
                        "info",
                        "Review logs for cause of crash"
                    )

        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    monitor()
```

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start approval watcher
pm2 start .claude/skills/approval-processor/scripts/approval_watcher.py \
  --interpreter python3 \
  --name approval-processor

# Start watchdog
pm2 start watchdog.py \
  --interpreter python3 \
  --name watchdog

# Auto-start on system boot
pm2 startup
pm2 save

# Monitor
pm2 status
pm2 logs approval-processor

# Restart on crash (automatic with PM2)
# PM2 handles this by default
```

---

## Common Error Scenarios

### Scenario 1: SMTP Authentication Failed

**Symptoms:**
- Emails in /Failed
- Log shows: "SMTP Authentication failed"

**Diagnosis:**
```bash
# Test SMTP directly
python .claude/skills/email-sender/scripts/test_email.py
```

**Resolution:**
1. Check SMTP credentials in `watchers/credentials/smtp_config.json`
2. Verify app password (not account password)
3. Check 2FA is enabled
4. Regenerate app password if needed
5. Update config file
6. Retry failed emails

### Scenario 2: LinkedIn Token Expired

**Symptoms:**
- Posts in /Failed
- Log shows: "OAuth token expired"

**Diagnosis:**
```bash
# Check token expiration
cat watchers/credentials/linkedin_token.json | jq '.expires_at'
```

**Resolution:**
1. Re-authenticate: `python .claude/skills/linkedin-poster/scripts/linkedin_post.py --auth`
2. Complete OAuth flow
3. Retry failed posts

### Scenario 3: Approval Watcher Stopped

**Symptoms:**
- Files in /Approved not being processed
- No recent activity in logs

**Diagnosis:**
```bash
# Check if running
ps aux | grep approval_watcher

# Check logs
tail Logs/approval_activity_*.json
```

**Resolution:**
```bash
# Restart watcher
python .claude/skills/approval-processor/scripts/approval_watcher.py &

# Or with PM2
pm2 restart approval-processor
```

### Scenario 4: Disk Full

**Symptoms:**
- All operations failing
- Log errors: "No space left on device"

**Diagnosis:**
```bash
df -h  # Check disk usage
du -sh */  # Find large directories
```

**Resolution:**
1. Archive old /Done files:
```bash
python scripts/archive_old.py --days 30
```

2. Clear old logs:
```bash
find Logs -name "*.json" -mtime +90 -delete
```

3. Compress archives:
```bash
tar -czf archive_2025.tar.gz Done_2025/
rm -rf Done_2025/
```

---

## Prevention Best Practices

### 1. Regular Maintenance

**Daily:**
- Check failure rate: `python scripts/check_status.py`
- Review alerts: `ls Alerts/`

**Weekly:**
- Archive completed actions older than 7 days
- Review failure patterns in logs
- Test credential validity

**Monthly:**
- Rotate credentials
- Full system test
- Update dependencies

### 2. Defensive Coding

**Always validate inputs:**
```python
def execute_email_action(metadata):
    """Execute email with validation."""
    # Validate before attempting
    validate_email_metadata(metadata)

    # Use try-except for external calls
    try:
        send_email(
            metadata['to'],
            metadata['subject'],
            metadata['body_full']
        )
    except Exception as e:
        # Log detailed error
        log_error('email_send_failed', str(e), metadata)
        raise
```

**Implement timeouts:**
```python
# Prevent hanging forever
result = execute_action(timeout=300)  # 5 minute max
```

### 3. Comprehensive Logging

**Log everything:**
- All approval attempts
- All execution results
- All errors with stack traces
- Retry attempts
- Configuration changes

**Log format:**
```json
{
  "timestamp": "ISO 8601",
  "level": "INFO|WARNING|ERROR",
  "action": "action_name",
  "details": {},
  "error": "error message (if any)",
  "stack_trace": "full trace (if error)"
}
```

---

**Related Documentation:**
- See `approval_workflow.md` for workflow details
- See `action_types.md` for action specifications
- See main `SKILL.md` for usage examples
