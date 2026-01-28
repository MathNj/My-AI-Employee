---
name: approval-processor
description: File-based human-in-the-loop orchestration for safe execution of high-risk AI actions (email, social posts, payments). Enforces explicit approval, prevents double execution via claim-by-move, updates Dashboard.md memory, and handles failures gracefully. Use when you need to (1) Process approved actions from Action_Queue, (2) Execute emails, LinkedIn posts, or payments, (3) Handle rejected requests, (4) Monitor queue continuously, or (5) Automate HITL workflow with Gold-tier safety.
---

# Approval Processor

A file-based, human-in-the-loop orchestration skill that safely executes high-risk AI actions (email, social posts, payments) by enforcing explicit human approval, preventing double execution, updating the AI's Obsidian memory, and recovering gracefully from failures.

## Overview

The approval-processor skill is the **execution engine** for autonomous AI actions. It implements a **claim-by-move** pattern where:
1. AI creates action requests in `Action_Queue/0_Pending`
2. Human reviews and moves to `Action_Queue/1_Approved`
3. Processor atomically claims files (moves to `2_Processing`)
4. Executes action via appropriate executor
5. Moves to `3_Done` on success or `9_Failed` on failure
6. Updates Dashboard.md (AI-visible memory)

### Core Guarantees

- ✅ **No approval → no action**: Human must explicitly approve
- ✅ **Single execution**: Claim-by-move prevents duplicate processing
- ✅ **AI memory**: Every result written to Dashboard.md
- ✅ **Failure visibility**: Errors create alerts in Needs_Attention
- ✅ **Gold-tier safe**: Payment actions require explicit approval

### Key Capabilities

- **Atomic Execution**: Global lock + processing folder prevents race conditions
- **Multi-Executor Support**: Routes to email-sender, linkedin-poster, MCP servers
- **Payment Support**: Gold-tier Odoo integration via MCP
- **Automatic Retries**: Exponential backoff (3 attempts max)
- **Audit Trail**: Complete log of all actions and outcomes
- **Dashboard Integration**: Results visible to Claude for context

---

## Quick Start

### One-Time Processing

```bash
# Process all approved actions once
python .claude/skills/approval-processor/scripts/process_approvals.py
```

**Output:**
```
🔄 Processing approval queue...

Found 2 approved action(s)

Processing: EMAIL_client_a_2026-01-23T10-30-00.md
  Type: email
  To: client@example.com
  ⏳ Claimed (moved to 2_Processing)
  ✅ Email sent successfully
  ✅ Moved to Done
  📝 Updated Dashboard.md

Processing: LINKEDIN_POST_2026-01-23T11-00-00.md
  Type: linkedin_post
  ⏳ Claimed (moved to 2_Processing)
  ✅ Post published successfully
  ✅ Moved to Done
  📝 Updated Dashboard.md

📊 Summary:
  Processed: 2
  Successful: 2
  Failed: 0
```

### Continuous Monitoring

```bash
# Run indefinitely (checks every 30 seconds)
python .claude/skills/approval-processor/scripts/approval_watcher.py
```

### Check Queue Status

```bash
# View current queue state
python .claude/skills/approval-processor/scripts/check_status.py
```

---

## Folder Contract (Authoritative)

```
AI_Employee_Vault/
├── Dashboard.md                      # ← AI-readable system memory
│
├── Action_Queue/                     # ← Main approval queue
│   ├── 0_Pending/                    # Awaiting human review
│   │   ├── EMAIL_*.md
│   │   ├── LINKEDIN_POST_*.md
│   │   └── PAYMENT_*.md
│   │
│   ├── 1_Approved/                   # Human approved, ready to execute
│   │   └── (files moved here by human)
│   │
│   ├── 2_Processing/                 # ← Execution lock (atomic claim)
│   │   └── (files moved here during execution)
│   │
│   ├── 3_Done/                       # Executed successfully
│   │   ├── EMAIL_*.md
│   │   └── LINKEDIN_POST_*.md
│   │
│   ├── 4_Rejected/                   # Human rejected
│   │   └── (files moved here by human)
│   │
│   └── 9_Failed/                     # Execution failed (after retries)
│       └── (auto-moved here)
│
└── Needs_Attention/                  # ← Error alerts visible to Claude
    └── ERROR_ALERT_*.md
```

### Folder Numbering Convention

Prefixes ensure **correct processing order**:
- `0_*` = Pending (creation)
- `1_*` = Approved (ready)
- `2_*` = Processing (locked)
- `3_*` = Done (success)
- `4_*` = Rejected (cancelled)
- `9_*` = Failed (error)

This prevents accidental processing of wrong files.

---

## Execution Logic

### Core Algorithm (Simplified)

```python
def process_approved_actions():
    """Main execution loop with atomic claims."""

    acquire_global_lock()

    for file in list_files("Action_Queue/1_Approved"):
        try:
            # 1. Atomic claim (prevents double execution)
            working = atomic_move(file, "Action_Queue/2_Processing")

            # 2. Parse and validate
            meta = parse_and_validate_yaml(working)

            # 3. Route to executor
            result = route_and_execute(meta)

            # 4. Success → Done
            move(working, "Action_Queue/3_Done")
            append_dashboard(f"✅ Executed {meta.type}: {meta.summary}")

        except Exception as e:
            # 5. Failure → Failed + Alert
            move(working, "Action_Queue/9_Failed")
            write_alert(f"❌ Action failed: {e}")
            append_dashboard(f"❌ Failed {meta.type}: {e}")

    release_global_lock()
```

### Atomic Execution

The `2_Processing` folder is the **execution lock**:
- Move from `1_Approved` to `2_Processing` is atomic
- If script crashes during execution, file stays in `2_Processing`
- Recovery script can detect and retry stale processing files
- Prevents duplicate execution (file no longer in `1_Approved`)

**Global Lock:**
- File-based lock (`.approval_processor.lock`) prevents concurrent runs
- Single processor instance even if multiple watchers running
- Auto-releases after processing completes

---

## Supported Action Types

### Type: `email`

**Executor:** email-sender skill
**Risk Level:** Medium
**Auto-Approve:** Known contacts only

**Frontmatter Schema:**
```yaml
---
type: email
action: send_email
to: recipient@example.com
subject: "Invoice #1234 - January 2026"
body_full: |
  Dear Client,

  Please find attached your invoice for January 2026.

  Best regards,
  Your Name
attachments:
  - /path/to/invoice.pdf
created: 2026-01-23T10:30:00Z
expires: 2026-01-24T10:30:00Z
priority: normal
---
```

**Execution:**
```python
def execute_email(meta):
    return call_skill(
        'email-sender',
        script='send_email.py',
        args=['--execute-approved', meta.filepath]
    )
```

**Result in Dashboard.md:**
```markdown
## Recent Actions
- ✅ 10:30 Sent email to client@example.com (Invoice #1234)
```

---

### Type: `linkedin_post`

**Executor:** linkedin-poster skill
**Risk Level:** Medium
**Auto-Approve:** Never (always requires human review)

**Frontmatter Schema:**
```yaml
---
type: linkedin_post
action: post_to_linkedin
message: |
  Excited to announce our new AI automation service!

  We're helping businesses save 20+ hours per week with intelligent automation.

  #Automation #AI #BusinessEfficiency
hashtags: ["Automation", "AI", "BusinessEfficiency"]
media: []
created: 2026-01-23T11:00:00Z
expires: 2026-01-24T11:00:00Z
priority: normal
---
```

**Execution:**
```python
def execute_linkedin_post(meta):
    return call_skill(
        'linkedin-poster',
        script='linkedin_post.py',
        args=['--execute-approved', meta.filepath]
    )
```

**Result in Dashboard.md:**
```markdown
## Recent Actions
- ✅ 11:00 Posted on LinkedIn (AI automation announcement)
```

---

### Type: `payment` (Gold Tier)

**Executor:** MCP-Odoo server
**Risk Level:** Critical
**Auto-Approve:** Never (always requires human approval)

**Frontmatter Schema:**
```yaml
---
type: payment
action: execute_payment
amount: 1500.00
currency: USD
recipient: "Vendor ABC Inc."
recipient_account: "XXXX-1234"
reference: "Invoice #5678 - Q1 Services"
payment_method: "ACH"
created: 2026-01-23T14:00:00Z
expires: 2026-01-23T16:00:00Z  # 2-hour expiration for payments
priority: critical
---
```

**Execution:**
```python
def execute_payment(meta):
    # Gold-tier: Always double-check with human
    if not confirm_payment_safe(meta):
        raise PaymentVerificationError("Manual verification required")

    # Call Odoo MCP server
    return call_mcp_server(
        'odoo',
        method='execute_payment',
        params=meta.to_dict()
    )
```

**Safety Checks:**
- First-time recipient → Always prompt human
- Amount > $1000 → Always prompt human
- Recurring payment → Check if previous payment exists
- Account changed → Always prompt human

**Result in Dashboard.md:**
```markdown
## Recent Actions
- ✅ 14:05 Payment of $1,500.00 to Vendor ABC Inc. (Invoice #5678)

## Financial Summary
- Today's Payments: $1,500.00
- Month-to-Date: $4,500.00
```

---

### Type: `api_call`

**Executor:** Direct MCP server call
**Risk Level:** Variable (based on endpoint)
**Auto-Approve:** GET requests only

**Frontmatter Schema:**
```yaml
---
type: api_call
action: call_api
method: POST
url: "https://api.example.com/v1/create"
headers:
  Authorization: "Bearer ${API_TOKEN}"
  Content-Type: "application/json"
body:
  name: "Project Alpha"
  value: 1500
created: 2026-01-23T15:00:00Z
expires: 2026-01-23T17:00:00Z
priority: normal
---
```

**Execution:**
```python
def execute_api_call(meta):
    return call_mcp_server(
        'http',
        method=meta.method,
        url=meta.url,
        headers=meta.headers,
        body=meta.body
    )
```

---

### Type: `file_operation`

**Executor:** Local filesystem
**Risk Level:** Low to Medium
**Auto-Approve:** Create/update only (no delete)

**Frontmatter Schema:**
```yaml
---
type: file_operation
action: move_files
source: "/Inbox/Invoices/*.pdf"
destination: "/Accounting/2026-01/Processed/"
pattern: "*.pdf"
created: 2026-01-23T16:00:00Z
expires: 2026-01-24T16:00:00Z
priority: low
---
```

**Execution:**
```python
def execute_file_operation(meta):
    if meta.action == 'move_files':
        for file in glob(meta.source):
            shutil.move(file, meta.destination)
        return {"moved": len(files)}
```

---

## Dashboard.md Integration (Mandatory)

Every execution result **must** be written to Dashboard.md for AI visibility.

### Update Format

```python
def append_dashboard(message):
    """Append to Dashboard.md Recent Actions section."""

    dashboard = Path("Dashboard.md")

    # Read existing content
    content = dashboard.read_text()

    # Find or create ## Recent Actions section
    if "## Recent Actions" not in content:
        content += "\n## Recent Actions\n"

    # Append with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = f"- [{timestamp}] {message}\n"

    # Update (keep last 50 entries)
    lines = content.split('\n')
    recent_actions_idx = next(i for i, line in enumerate(lines)
                             if "## Recent Actions" in line)

    # Insert after Recent Actions header
    lines.insert(recent_actions_idx + 1, new_entry)

    # Write back
    dashboard.write_text('\n'.join(lines))
```

### Example Dashboard Updates

**After email execution:**
```markdown
## Recent Actions
- [2026-01-23 10:30] ✅ Sent email to client@example.com (Invoice #1234)
- [2026-01-23 11:00] ✅ Posted on LinkedIn (AI automation announcement)
- [2026-01-23 14:05] ✅ Payment of $1,500.00 to Vendor ABC Inc.
```

**After failure:**
```markdown
## Recent Actions
- [2026-01-23 15:30] ❌ Failed to send email (SMTP connection error)
```

**AI Visibility:**
- Claude reads Dashboard.md for context
- Understands what actions were taken
- Sees failures and can troubleshoot
- Maintains situational awareness

---

## Failure Handling (Gold Requirement)

### Retry Logic

**Max Attempts:** 3
**Backoff Strategy:** Exponential

```python
RETRY_DELAYS = [0, 30, 60]  # seconds

def execute_with_retry(action_file):
    for attempt, delay in enumerate(RETRY_DELAYS):
        try:
            return route_and_execute(action_file)
        except TransientError as e:
            if attempt == len(RETRY_DELAYS) - 1:
                raise  # Final attempt failed
            time.sleep(delay)
```

### Failure Categories

**Transient Errors** (retry):
- Network timeout
- API rate limit
- Temporary service unavailable
- Lock contention

**Permanent Errors** (fail immediately):
- Invalid credentials
- Missing required fields
- Action not supported
- Account locked

**Human Errors** (manual intervention):
- Payment verification failed
- Recipient not found
- Content policy violation

### After Final Failure

1. **Move to `9_Failed`**
   ```python
   move(working_file, "Action_Queue/9_Failed")
   ```

2. **Create Error Alert**
   ```python
   alert_path = "Needs_Attention/ERROR_ALERT_{}.md".format(timestamp)
   alert_content = f"""
   ---
   type: error_alert
   severity: high
   action_type: {meta.type}
   file: {working_file}
   timestamp: {datetime.now().isoformat()}
   ---

   # Action Execution Failed

   **Type:** {meta.type}
   **Error:** {error_message}

   ## Details
   {format_error(error)}

   ## Recovery Options
   - [ ] Fix issue and move to `1_Approved` to retry
   - [ ] Move to `4_Rejected` to cancel
   - [ ] Manual intervention required

   ---
   *Created by approval-processor*
   """
   write_file(alert_path, alert_content)
   ```

3. **Update Dashboard**
   ```python
   append_dashboard(f"❌ Failed {meta.type}: {error}")
   ```

4. **Log for Audit**
   ```python
   log_entry = {
       "timestamp": datetime.now().isoformat(),
       "action": "execution_failed",
       "type": meta.type,
       "file": working_file,
       "error": str(error),
       "attempts": 3,
       "skill": "approval-processor"
   }
   append_to_log("action_failures_*.json", log_entry)
   ```

### Recovery Procedures

**Retry Failed Action:**
```bash
# Option 1: Move back to Approved
mv Action_Queue/9_Failed/EMAIL_*.md Action_Queue/1_Approved/

# Option 2: Manual retry script
python .claude/skills/approval-processor/scripts/retry_action.py \
    Action_Queue/9_Failed/EMAIL_*.md
```

**Cancel Failed Action:**
```bash
mv Action_Queue/9_Failed/EMAIL_*.md Action_Queue/4_Rejected/
```

**Investigate Failure:**
```bash
# View error details
cat Action_Queue/9_Failed/EMAIL_*.md

# Check logs
cat Logs/action_failures_*.json | grep "EMAIL_"
```

---

## Workflow Examples

### Example 1: Email Approval and Execution

**Step 1: AI Creates Request**
```bash
# AI writes to Action_Queue/0_Pending/EMAIL_client_a_2026-01-23T10-30-00.md
```

**Step 2: Human Reviews**
```markdown
# Human opens file in Obsidian
# Reviews content, recipient, attachments
# Moves to Action_Queue/1_Approved/
```

**Step 3: Processor Executes**
```bash
python .claude/skills/approval-processor/scripts/process_approvals.py

# Output:
# Processing: EMAIL_client_a_2026-01-23T10-30-00.md
#   ⏳ Claimed (moved to 2_Processing)
#   ✅ Email sent successfully
#   ✅ Moved to Done
#   📝 Updated Dashboard.md
```

**Step 4: Dashboard Updated**
```markdown
## Recent Actions
- ✅ Sent email to client@example.com (Invoice #1234)
```

---

### Example 2: Payment Failure and Recovery

**Step 1: Payment Request**
```yaml
---
type: payment
amount: 1500.00
recipient: "Vendor ABC"
priority: critical
---
```

**Step 2: Human Approves**
```bash
mv Action_Queue/0_Pending/PAYMENT_*.md \
   Action_Queue/1_Approved/
```

**Step 3: Execution Fails (Network Error)**
```bash
# Processor attempts retry 3 times
# All attempts fail
# File moved to Action_Queue/9_Failed/
```

**Step 4: Error Alert Created**
```markdown
# Needs_Attention/ERROR_ALERT_2026-01-23T14-30-00.md
---
severity: high
action_type: payment
---

# Action Execution Failed

**Type:** payment
**Error:** Connection timeout after 3 attempts

## Recovery Options
- [ ] Check network connection and retry
- [ ] Verify Odoo MCP server is running
- [ ] Manual intervention required
```

**Step 5: Human Investigates and Retries**
```bash
# Human checks network, confirms OK
# Moves back to Approved
mv Action_Queue/9_Failed/PAYMENT_*.md \
   Action_Queue/1_Approved/

# Processor retries
python .claude/skills/approval-processor/scripts/process_approvals.py

# ✅ Payment succeeds
```

---

## Configuration

### Processor Settings

Edit `scripts/process_approvals.py`:

```python
# Global lock timeout (seconds)
LOCK_TIMEOUT = 300

# Check interval for watcher (seconds)
WATCHER_INTERVAL = 30

# Retry settings
MAX_RETRIES = 3
RETRY_DELAYS = [0, 30, 60]  # seconds

# Expiration (hours)
DEFAULT_EXPIRATION = 24
PAYMENT_EXPIRATION = 2  # Payments expire faster

# Dashboard updates
DASHBOARD_MAX_ENTRIES = 50  # Keep last 50 actions

# Safety thresholds
PAYMENT_WARN_THRESHOLD = 1000  # Warn if > $1000
PAYMENT_BLOCK_THRESHOLD = 5000  # Block if > $5000 (require extra approval)
```

### Executor Mapping

Edit `scripts/action_router.py`:

```python
EXECUTORS = {
    'email': {
        'skill': 'email-sender',
        'script': 'send_email.py',
        'args': ['--execute-approved']
    },
    'linkedin_post': {
        'skill': 'linkedin-poster',
        'script': 'linkedin_post.py',
        'args': ['--execute-approved']
    },
    'payment': {
        'type': 'mcp',
        'server': 'odoo',
        'method': 'execute_payment',
        'verify': True  # Always verify before execution
    },
    'api_call': {
        'type': 'mcp',
        'server': 'http',
        'method': 'call_api'
    }
}
```

---

## Monitoring and Logging

### Activity Logs

All activity logged to:
- `Logs/approval_activity_YYYY-MM-DD.json` - All processing events
- `Logs/action_failures_YYYY-MM-DD.json` - Failed executions
- `Logs/execution_details_YYYY-MM-DD.json` - Detailed execution logs

**Log Entry Format:**
```json
{
  "timestamp": "2026-01-23T10:30:00Z",
  "action": "execution_success",
  "details": {
    "file": "EMAIL_client_a_2026-01-23T10-30-00.md",
    "type": "email",
    "executor": "email-sender",
    "duration_ms": 1250,
    "status": "success"
  },
  "skill": "approval-processor"
}
```

### Metrics Tracking

**Key Metrics:**
- Approval rate: Approved / (Approved + Rejected)
- Processing time: Time from approval to execution
- Success rate: Successful / Total processed
- Failure rate: Failed / Total processed
- Average retry count

**View Metrics:**
```bash
python .claude/skills/approval-processor/scripts/check_status.py --metrics
```

**Output:**
```
📊 Approval Queue Metrics (Last 7 Days)

Approval Rate: 85%
  - Approved: 17
  - Rejected: 3

Processing:
  - Average time: 45 seconds
  - Success rate: 94%
  - Failure rate: 6%

Failures:
  - Transient: 1 (recovered)
  - Permanent: 0
  - Human: 0

Actions by Type:
  - email: 12
  - linkedin_post: 5
  - payment: 3
```

---

## Best Practices

### Approval Workflow

**For Humans:**
1. **Check `0_Pending` regularly** (2-3x daily)
2. **Review content carefully** before approving
3. **Move to `4_Rejected`** if not appropriate
4. **Add rejection reason** for AI learning

**For AI:**
1. **Create complete requests** with all required fields
2. **Set appropriate expiration** (shorter for urgent items)
3. **Monitor `9_Failed`** for recovery opportunities
4. **Read Dashboard.md** for execution context

### Security

**Never Auto-Approve:**
- First-time recipients
- Large amounts (> $1000)
- New payment destinations
- Bulk actions (multiple recipients)
- Sensitive content

**Always Verify:**
- Recipient email/domain
- Payment account details
- Attachment contents
- Social post content (hashtags, mentions)

### Folder Maintenance

**Weekly Cleanup:**
```bash
# Archive old Done items (>30 days)
python .claude/skills/approval-processor/scripts/archive_old.py --days 30

# Clear expired items
python .claude/skills/approval-processor/scripts/check_expirations.py --move

# Review Rejected patterns
ls Action_Queue/4_Rejected/
```

**Monthly Review:**
- Analyze rejection patterns
- Update auto-approval rules if needed
- Review failed actions for improvements
- Adjust expiration times based on actual approval time

---

## Integration with Skills

### With email-sender

```
email-sender creates approval request
    ↓
File in Action_Queue/0_Pending/EMAIL_*.md
    ↓
Human reviews and moves to Action_Queue/1_Approved/
    ↓
approval-processor detects and claims (moves to 2_Processing/)
    ↓
Calls email-sender to execute
    ↓
Email sent, file moved to Action_Queue/3_Done/
    ↓
Dashboard.md updated with result
```

### With linkedin-poster

```
linkedin-poster creates approval request
    ↓
File in Action_Queue/0_Pending/LINKEDIN_POST_*.md
    ↓
Human approves content
    ↓
approval-processor executes
    ↓
Post published, Dashboard updated
```

### With auto-approver

```
auto-approver scans Action_Queue/0_Pending/
    ↓
Uses Claude AI to analyze request
    ↓
Checks against Company_Handbook.md rules
    ↓
Auto-approves low-risk actions
    ↓
Moves to Action_Queue/1_Approved/
    ↓
approval-processor executes
```

### With scheduler-manager

```
Scheduled task triggers (e.g., Monday 9am)
    ↓
Generate content (CEO Briefing, social post)
    ↓
Create approval request
    ↓
Human approves (async, may take hours)
    ↓
approval-processor (runs every 5 min)
    ↓
Detects approval and executes
    ↓
Scheduled action complete
```

---

## Production Deployment

### Continuous Monitoring

**Option 1: Python Script**
```bash
# Run directly
python .claude/skills/approval-processor/scripts/approval_watcher.py

# Background (Windows)
start pythonw approval_watcher.py

# Background (Linux/Mac)
nohup python approval_watcher.py > /dev/null 2>&1 &
```

**Option 2: PM2 (Recommended)**
```bash
# Install PM2
npm install -g pm2

# Start watcher
pm2 start .claude/skills/approval-processor/scripts/approval_watcher.py \
    --interpreter python3 \
    --name approval-processor

# Auto-start on boot
pm2 startup
pm2 save

# Monitor
pm2 status
pm2 logs approval-processor

# Restart
pm2 restart approval-processor
```

**Option 3: Systemd (Linux)**
```ini
[Unit]
Description=Approval Processor Watcher
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/approval_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Option 4: Task Scheduler (Windows)**
```
Task: Approval Processor Watcher
Trigger: At system startup
Action: Start pythonw approval_watcher.py
```

### Scheduled Processing

**Cron (Linux/Mac):**
```bash
# Run every 5 minutes
*/5 * * * * cd /path/to/AI_Employee_Vault && \
    python .claude/skills/approval-processor/scripts/process_approvals.py
```

**Task Scheduler (Windows):**
```
Trigger: Daily at 12:00 AM
Repeat every 5 minutes for 24 hours
Action: python process_approvals.py
```

---

## Troubleshooting

### Files Not Processing

**Symptom:** Files in `1_Approved` but not executing

**Checks:**
1. Is watcher/processor running?
   ```bash
   ps aux | grep approval_watcher
   pm2 status
   ```

2. Is global lock stuck?
   ```bash
   ls -la .approval_processor.lock
   # If old (>10 min), delete it
   rm .approval_processor.lock
   ```

3. Are files in `2_Processing` (stale)?
   ```bash
   ls Action_Queue/2_Processing/
   # If files exist, move back to 1_Approved to retry
   mv Action_Queue/2_Processing/* Action_Queue/1_Approved/
   ```

4. Check logs
   ```bash
   cat Logs/approval_activity_*.json | tail -20
   ```

### Executor Not Found

**Symptom:** "Executor not found for type: X"

**Solution:**
1. Check executor mapping in `action_router.py`
2. Verify skill scripts exist
3. Test executor directly:
   ```bash
   python .claude/skills/email-sender/scripts/send_email.py --test
   ```

### Dashboard Not Updating

**Symptom:** Actions execute but Dashboard.md not updated

**Checks:**
1. Verify Dashboard.md exists
2. Check file permissions (writable?)
3. Look for "## Recent Actions" section
4. Manual update:
   ```bash
   python .claude/skills/approval-processor/scripts/update_dashboard.py
   ```

### Persistent Failures

**Symptom:** Same action fails repeatedly

**Investigation:**
1. Check error type in `9_Failed` file
2. Review logs: `Logs/action_failures_*.json`
3. Test executor manually
4. Check credentials/configuration
5. Verify external service is available

---

## Scripts Reference

### process_approvals.py

**Purpose:** Main approval processor (one-time execution)

**Usage:**
```bash
# Process all approved
python .claude/skills/approval-processor/scripts/process_approvals.py

# Verbose output
python .claude/skills/approval-processor/scripts/process_approvals.py --verbose

# Dry run (preview only)
python .claude/skills/approval-processor/scripts/process_approvals.py --dry-run

# Process specific folder
python .claude/skills/approval-processor/scripts/process_approvals.py \
    --folder Action_Queue/1_Approved
```

**Returns:** 0 (success), 1 (errors occurred)

---

### approval_watcher.py

**Purpose:** Continuous monitoring daemon

**Usage:**
```bash
# Start watcher (foreground)
python .claude/skills/approval-processor/scripts/approval_watcher.py

# Custom interval
python .claude/skills/approval-processor/scripts/approval_watcher.py --interval 60

# Verbose logging
python .claude/skills/approval-processor/scripts/approval_watcher.py --verbose
```

**Output:**
```
👁️ Approval Watcher Started
   Monitoring: Action_Queue/1_Approved
   Check interval: 30 seconds
   Press Ctrl+C to stop

[10:30:15] Checking for approved actions...
[10:30:15] No new approvals

[10:30:45] Checking for approved actions...
[10:30:45] Found 1 new approval(s)
[10:30:45] Processing EMAIL_client_a_2026-01-23T10-30-00.md...
[10:30:47] ✅ Email sent successfully
```

---

### check_status.py

**Purpose:** View approval queue status

**Usage:**
```bash
# Current status
python .claude/skills/approval-processor/scripts/check_status.py

# Detailed view
python .claude/skills/approval-processor/scripts/check_status.py --detailed

# JSON output
python .claude/skills/approval-processor/scripts/check_status.py --json

# Show metrics
python .claude/skills/approval-processor/scripts/check_status.py --metrics
```

**Output:**
```
📋 Approval Queue Status

Pending Review (0_Pending): 3 items
  - EMAIL_client_a_2026-01-23T09-00-00.md (2 hours old)
  - LINKEDIN_POST_2026-01-23T10-00-00.md (1 hour old)
  - PAYMENT_vendor_x_2026-01-23T11-00-00.md (15 min old)

Approved (1_Approved): 0 items
Processing (2_Processing): 0 items
Done (3_Done): 5 items
Rejected (4_Rejected): 1 item
Failed (9_Failed): 0 items

⚠️ Expiring Soon:
  - EMAIL_client_a_2026-01-23T09-00-00.md (expires in 2 hours)
```

---

### check_expirations.py

**Purpose:** Check and process expired approvals

**Usage:**
```bash
# Check only (no action)
python .claude/skills/approval-processor/scripts/check_expirations.py

# Move expired to special folder
python .claude/skills/approval-processor/scripts/check_expirations.py --move

# Custom expiration time
python .claude/skills/approval-processor/scripts/check_expirations.py --hours 48
```

---

## References

### Dependencies

**Required Skills:**
- `email-sender` - For email execution
- `linkedin-poster` - For LinkedIn posting
- `auto-approver` - For intelligent auto-approval (optional)

**Required Infrastructure:**
- Obsidian vault (for Dashboard.md and queue)
- MCP Odoo server (for payments, Gold tier)
- PM2 or systemd (for process management)

### File Structure

```
.claude/skills/approval-processor/
├── SKILL.md                              # This file
├── scripts/
│   ├── process_approvals.py              # Main processor
│   ├── approval_watcher.py               # Continuous monitor
│   ├── check_status.py                   # Status viewer
│   └── check_expirations.py              # Expiration handler
└── references/
    ├── approval_workflow.md              # Workflow documentation
    ├── action_types.md                   # All action types
    └── error_recovery.md                 # Error handling guide
```

---

## Version History

- **v1.0** (2026-01-12): Initial release with email and LinkedIn support
- **v2.0** (2026-01-23):
  - Redesigned with Action_Queue numbered folder structure
  - Added atomic execution with 2_Processing lock
  - Integrated Dashboard.md updates (mandatory)
  - Added payment support (Gold tier)
  - Implemented exponential retry logic
  - Enhanced error handling with Needs_Attention alerts
  - Added MCP server integration for API calls and payments
- **v3.0.0** (2026-01-26) - Ultimate Edition:
  - ✅ Multi-stage approval workflows with sequential/parallel chains
  - ✅ Escalation management with configurable chains
  - ✅ SLA tracking and auto-escalation
  - ✅ Auto-approval rules engine with condition matching
  - ✅ Structured JSON logging
  - ✅ Approval analytics and reporting
  - ✅ Delegation and substitution support
  - ✅ Batch approval operations
  - ✅ Health check and monitoring

---

## Ultimate Edition Features

### New Script: approval_processor_ultimate.py

**Advanced Approval Processing with:**

1. **Multi-Stage Workflows**
   - Sequential approval chains
   - Parallel approval steps
   - Optional vs mandatory approvers
   - Step timeout handling

2. **Escalation Management**
   - Configurable escalation chains
   - Auto-escalation on SLA breach
   - Escalation level tracking
   - Supervisor → Manager → Director → Executive

3. **Auto-Approval Rules**
   - Condition-based auto-approval
   - Field matching (amount, recipient, etc.)
   - Safe contact whitelisting
   - Risk-based approval thresholds

4. **SLA Tracking**
   - Per-request SLA monitoring
   - Overdue detection and alerts
   - Approval time analytics
   - Performance metrics

**Usage:**
```bash
# Process with enhanced features
python .claude/skills/approval-processor/scripts/approval_processor_ultimate.py

# Check and escalate overdue approvals
python .claude/skills/approval-processor/scripts/approval_processor_ultimate.py --escalate

# Show analytics dashboard
python .claude/skills/approval-processor/scripts/approval_processor_ultimate.py --analytics

# Health check
python .claude/skills/approval-processor/scripts/approval_processor_ultimate.py --health
```

**Configuration (approval_processor_config.yaml):**
```yaml
sla_default_minutes: 1440  # 24 hours
auto_approve_enabled: true
escalation_enabled: true
escalation_threshold_percent: 80  # Escalate at 80% of SLA
max_workers: 4
batch_size: 20

auto_approval_rules:
  - name: low_value_expense
    type: expense
    conditions:
      - field: amount
        operator: lt
        value: 50
    action: approve
```

---

**Last Updated:** 2026-01-26
**Skill Version:** 3.0
**Maintained By:** approval-processor skill
