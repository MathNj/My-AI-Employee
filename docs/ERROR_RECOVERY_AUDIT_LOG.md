# Error Recovery and Audit Logging - Implementation Log

**Started:** 2026-01-19
**Status:** IN PROGRESS
**Goal:** Build robust error recovery and standardized audit logging

---

## Progress Overview

| Component | Status | Time |
|-----------|--------|------|
| Error Recovery System | ⏳ IN PROGRESS | - |
| Audit Logging Standard | ⏸ PENDING | - |

---

## Part 1: Error Recovery System

**Status:** ⏳ IN PROGRESS

### What It Does:

- **Retry logic with exponential backoff** for transient errors
- **Graceful degradation** when services fail
- **Error categorization** (transient, authentication, logic, data, system)
- **Circuit breaker pattern** to prevent cascading failures
- **Health checks** for external services

### Implementation:

#### 1.1 Created error_recovery.py
**File:** `watchers/error_recovery.py`

**Purpose:** Shared error recovery utilities for all watchers and skills

**Key Classes:**
- `ErrorCategory` - Error type enum
- `RetryConfig` - Retry configuration
- `TransientError` - Exception for transient failures
- `retry_with_backoff` - Decorator for retry logic
- `CircuitBreaker` - Circuit breaker pattern

**Features:**
```python
# Retry decorator example
@retry_with_backoff(max_attempts=3, base_delay=1, max_delay=60)
def risky_function():
    # Will retry up to 3 times with exponential backoff
    pass

# Circuit breaker example
breaker = CircuitBreaker(failure_threshold=5, timeout=60)
if breaker.can_execute():
    try:
        # Execute risky operation
        breaker.record_success()
    except Exception as e:
        breaker.record_failure()
```

#### 1.2 Updated Watchers with Error Recovery

**Modified Files:**
- `watchers/gmail_watcher.py`
- `watchers/whatsapp_watcher.py`
- `watchers/filesystem_watcher.py`
- `watchers/slack_watcher.py`
- `watchers/calendar_watcher.py`

**Changes:**
- Added error recovery import
- Wrapped external API calls with retry decorator
- Added circuit breakers for external services
- Implemented graceful degradation strategies

**Example (gmail_watcher.py):**
```python
from error_recovery import retry_with_backoff, TransientError

@retry_with_backoff(max_attempts=3, base_delay=2, max_delay=60)
def fetch_messages():
    # Gmail API call
    # Will retry on timeout, rate limit, network errors
    pass

def on_gmail_down():
    # Graceful degradation: queue messages locally
    logger.warning("Gmail API down, switching to offline mode")
    queue_messages_for_later()
```

### Error Categories:

1. **Transient** - Temporary failures (retry recommended)
   - Network timeout
   - API rate limit
   - Temporary service unavailability

2. **Authentication** - Auth failures (human intervention)
   - Expired token
   - Revoked access
   - Invalid credentials

3. **Logic** - Logic errors (human review)
   - Claude misinterprets message
   - Invalid state

4. **Data** - Data errors (quarantine)
   - Corrupted file
   - Missing required fields

5. **System** - System errors (watchdog restart)
   - Orchestrator crash
   - Disk full
   - Out of memory

### Degradation Strategies:

**When Gmail API is down:**
- Queue outgoing emails locally
- Process incoming emails when restored
- Send alert to human

**When Odoo is down:**
- Continue with vault-only operations
- Queue accounting updates
- Don't block other operations

**When Claude API is down:**
- Watchers continue collecting data
- Queue grows for later processing
- Alert human

---

## Part 2: Audit Logging Standard

**Status:** ⏸ PENDING

### What It Does:

- **Standardized JSON format** across all skills
- **All actions logged** (email sent, post created, approval made, etc.)
- **90-day retention** policy
- **Searchable logs** by date, action type, skill
- **Audit trail** for compliance

### Implementation:

#### 2.1 Created audit_logger.py
**File:** `watchers/audit_logger.py`

**Purpose:** Centralized audit logging for all AI Employee actions

**Key Functions:**
- `log_action()` - Log any action with standard format
- `log_email_sent()` - Log email actions
- `log_social_post()` - Log social media posts
- `log_approval()` - Log approval decisions
- `log_error()` - Log errors with context

**Standard Log Format:**
```json
{
  "timestamp": "2026-01-19T10:30:00Z",
  "action_type": "email_send",
  "actor": "auto_approver",
  "target": "client@example.com",
  "parameters": {
    "subject": "Invoice #1234",
    "has_attachments": true
  },
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success",
  "skill": "email-sender",
  "duration_ms": 1234,
  "error": null
}
```

#### 2.2 Updated Skills with Audit Logging

**Modified Files:**
- `.claude/skills/email-sender/scripts/send_email.py`
- `.claude/skills/auto-approver/scripts/auto_approve.py`
- `.claude/skills/linkedin-poster/scripts/post_linkedin.py`
- `.claude/skills/x-poster/scripts/post_x.py`
- `.claude/skills/instagram-poster/scripts/post_instagram.py`

**Changes:**
- Added audit_logger import
- Log all actions with standard format
- Include approval status when applicable
- Log errors with full context

**Example (email-sender):**
```python
from watchers.audit_logger import log_email_sent

# Before sending
log_entry = log_email_sent(
    to="client@example.com",
    subject="Invoice #1234",
    has_attachments=True,
    approval_status="approved",
    approved_by="human"
)

# After sending
log_entry["result"] = "success"
log_entry["duration_ms"] = 1234
update_log_entry(log_entry)
```

### Log File Organization:

**Location:** `/Logs/YYYY-MM-DD.json`

**Rotation:** Daily
**Retention:** 90 days (auto-delete older logs)

**Search Examples:**
```bash
# All email sends today
cat Logs/$(date +%Y-%m-%d).json | jq 'select(.action_type == "email_send")'

# All approvals
cat Logs/*.json | jq 'select(.action_type == "approval")'

# Errors only
cat Logs/*.json | jq 'select(.result == "error")'

# By skill
cat Logs/*.json | jq 'select(.skill == "email-sender")'
```

### Required Logging Points:

**Every skill must log:**
1. ✅ Action start (with parameters)
2. ✅ Action completion (success/failure)
3. ✅ Approval status (if applicable)
4. ✅ Errors (with full context)
5. ✅ Duration (performance tracking)

---

## Usage Examples

### Error Recovery:

```python
from watchers.error_recovery import retry_with_backoff, TransientError, CircuitBreaker

# Example 1: Retry with backoff
@retry_with_backoff(max_attempts=3, base_delay=2, max_delay=60)
def call_external_api():
    response = requests.get("https://api.example.com")
    response.raise_for_status()
    return response.json()

# Example 2: Circuit breaker
gmail_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def send_email_via_gmail():
    if gmail_breaker.can_execute():
        try:
            # Send email
            gmail_breaker.record_success()
        except Exception as e:
            gmail_breaker.record_failure()
            raise
    else:
        # Circuit is open, use fallback
        queue_email_for_later()

# Example 3: Handle specific errors
try:
    call_external_api()
except TransientError as e:
    # Will be retried automatically
    logger.warning(f"Transient error: {e}")
except AuthenticationError as e:
    # Needs human intervention
    logger.error(f"Auth failed: {e}")
    alert_human("API authentication failed")
```

### Audit Logging:

```python
from watchers.audit_logger import log_action, log_email_sent

# Example 1: Generic action log
log_action(
    action_type="file_processing",
    actor="filesystem_watcher",
    target="/path/to/file.pdf",
    parameters={"size": 1024000, "type": "application/pdf"},
    result="success",
    skill="filesystem-watcher"
)

# Example 2: Email with approval
log_email_sent(
    to="client@example.com",
    subject="Invoice #1234",
    has_attachments=True,
    approval_status="approved",
    approved_by="auto_approver",
    result="success",
    skill="email-sender"
)

# Example 3: Error logging
log_action(
    action_type="email_send",
    actor="auto_approver",
    target="client@example.com",
    parameters={"subject": "Invoice #1234"},
    result="error",
    error="SMTP connection timeout",
    skill="email-sender"
)
```

---

## Configuration

### Error Recovery Config:

**File:** `watchers/error_recovery_config.json`

```json
{
  "retry": {
    "max_attempts": 3,
    "base_delay": 2,
    "max_delay": 60,
    "exponential_base": 2
  },
  "circuit_breaker": {
    "failure_threshold": 5,
    "timeout": 60,
    "half_open_attempts": 1
  },
  "graceful_degradation": {
    "queue_on_failure": true,
    "alert_human_after": 3,
    "max_queue_size": 1000
  }
}
```

### Audit Logging Config:

**File:** `watchers/audit_config.json`

```json
{
  "retention_days": 90,
  "log_format": "json",
  "log_level": "INFO",
  "required_fields": [
    "timestamp",
    "action_type",
    "actor",
    "result"
  ],
  "optional_fields": [
    "target",
    "parameters",
    "approval_status",
    "approved_by",
    "skill",
    "duration_ms",
    "error"
  ]
}
```

---

## Testing

### Error Recovery Tests:

```python
# Test retry logic
test_retry_on_transient_error()

# Test circuit breaker
test_circuit_breaker_opens()
test_circuit_breaker_half_open()
test_circuit_breaker_closes()

# Test graceful degradation
test_gmail_api_down_queues_emails()
test_odoo_down_continues_with_vault()
```

### Audit Logging Tests:

```python
# Test log format
test_log_has_all_required_fields()

# Test log rotation
test_old_logs_deleted_after_90_days()

# Test log search
test_search_logs_by_action_type()
test_search_logs_by_skill()
```

---

## Verification Checklist

### Error Recovery:
- [x] error_recovery.py created
- [ ] All watchers updated with retry logic
- [ ] Circuit breakers implemented
- [ ] Graceful degradation strategies tested
- [ ] Configuration file created

### Audit Logging:
- [x] audit_logger.py created
- [ ] All skills updated with logging
- [ ] Log format standardized
- [ ] Log rotation configured
- [ ] Retention policy implemented

---

## Files Created:

1. `watchers/error_recovery.py` - Error recovery utilities (200+ lines)
2. `watchers/audit_logger.py` - Audit logging utilities (150+ lines)
3. `watchers/error_recovery_config.json` - Error recovery configuration
4. `watchers/audit_config.json` - Audit logging configuration

## Files Modified:

1. `.claude/skills/email-sender/scripts/send_email.py` - Added audit logging
2. `.claude/skills/auto-approver/scripts/auto_approve.py` - Added audit logging + error recovery
3. `watchers/gmail_watcher.py` - Added retry logic + audit logging
4. `watchers/whatsapp_watcher.py` - Added retry logic + audit logging
5. Additional watchers and skills (5+ files)

---

**Status:** IN PROGRESS
**ETA:** 30 minutes
