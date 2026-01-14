---
name: approval-processor
description: Process approval workflow from /Pending_Approval to execution. Use this skill when you need to (1) Process approved action requests, (2) Execute approved emails or LinkedIn posts, (3) Handle rejected requests, (4) Monitor approval queue continuously, or (5) Automate the human-in-the-loop workflow. Integrates with email-sender and linkedin-poster skills for action execution.
---

# Approval Processor

## Overview

This skill automates the human-in-the-loop approval workflow by monitoring approval folders, routing approved actions to the correct executors, and maintaining a complete audit trail. It's the orchestration layer that enables fully automated operation while maintaining human oversight.

## Quick Start

### Process Current Approvals

```bash
# One-time processing
python scripts/process_approvals.py
```

### Continuous Monitoring

```bash
# Run continuously (checks every 30 seconds)
python scripts/approval_watcher.py
```

### Check Status

```bash
# View approval queue status
python scripts/check_status.py
```

## Core Workflows

### Workflow 1: One-Time Processing

1. **Scan folders** (/Approved, /Rejected, /Pending_Approval)
2. **Process approved actions**
   - Parse metadata
   - Route to executor
   - Execute action
   - Move to /Done
3. **Process rejections**
   - Log rejection reason
   - Move to /Rejected archive
4. **Check expirations**
   - Identify expired approvals (>24 hours)
   - Move to /Expired folder
   - Log expiration

### Workflow 2: Continuous Monitoring

1. **Start watcher** (runs indefinitely)
2. **Monitor /Approved folder** (every 30 seconds)
3. **On new file detected:**
   - Parse action metadata
   - Route to executor
   - Execute immediately
   - Log result
4. **Continue monitoring**
5. **Handle errors gracefully**

### Workflow 3: Scheduled Processing

1. **Scheduler triggers** (e.g., every 5 minutes)
2. **Run process_approvals.py**
3. **Process all pending**
4. **Exit until next trigger**

## Approval Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/        # Awaiting human review
│   ├── EMAIL_*.md
│   └── LINKEDIN_POST_*.md
│
├── Approved/                # Human approved, ready to execute
│   └── (files moved here by human)
│
├── Rejected/                # Human rejected
│   └── (files moved here by human)
│
├── Done/                    # Executed successfully
│   ├── EMAIL_*.md
│   └── LINKEDIN_POST_*.md
│
└── Expired/                 # Expired before approval (>24 hours)
    └── (automatically moved here)
```

## Action Types

### Email Actions

**Frontmatter:**
```yaml
type: email
action: send_email
to: "recipient@example.com"
subject: "Subject"
body_full: |
  Email content...
attachments: ["/path/to/file.pdf"]
```

**Executor:** `email-sender` skill
**Script:** `.claude/skills/email-sender/scripts/send_email.py --execute-approved`

### LinkedIn Post Actions

**Frontmatter:**
```yaml
type: linkedin_post
action: post_to_linkedin
message: "Post content..."
hashtags: ["Automation", "AI"]
```

**Executor:** `linkedin-poster` skill
**Script:** `.claude/skills/linkedin-poster/scripts/linkedin_post.py --execute-approved`

### Future Action Types

- `type: payment` - Payment execution (Gold tier)
- `type: file_operation` - File management
- `type: api_call` - External API calls

## Usage

### Process All Pending Approvals

```bash
python scripts/process_approvals.py
```

**What it does:**
- Scans /Approved for new files
- Executes each approved action
- Moves to /Done on success
- Logs all activity

**Output:**
```
🔄 Processing approval queue...

Found 2 approved action(s)

Processing: EMAIL_2026-01-12T10-30-00.md
  Type: email
  To: client@example.com
  ✅ Email sent successfully
  ✅ Moved to Done

Processing: LINKEDIN_POST_2026-01-12T11-00-00.md
  Type: linkedin_post
  ✅ Post published successfully
  ✅ Moved to Done

📊 Summary:
  Processed: 2
  Successful: 2
  Failed: 0
```

### Start Continuous Monitoring

```bash
python scripts/approval_watcher.py
```

**What it does:**
- Runs indefinitely
- Checks /Approved every 30 seconds
- Executes immediately when file detected
- Logs all activity

**Output:**
```
👁️ Approval Watcher Started
   Monitoring: C:\...\AI_Employee_Vault\Approved
   Check interval: 30 seconds
   Press Ctrl+C to stop

[10:30:15] Checking for approved actions...
[10:30:15] No new approvals

[10:30:45] Checking for approved actions...
[10:30:45] Found 1 new approval(s)
[10:30:45] Processing EMAIL_2026-01-12T10-30-00.md...
[10:30:47] ✅ Email sent successfully

[10:31:15] Checking for approved actions...
[10:31:15] No new approvals
```

### Check Approval Status

```bash
python scripts/check_status.py
```

**Output:**
```
📋 Approval Queue Status

Pending Approval: 3 items
  - EMAIL_2026-01-12T09-00-00.md (Created 2 hours ago)
  - LINKEDIN_POST_2026-01-12T10-00-00.md (Created 1 hour ago)
  - EMAIL_2026-01-12T11-00-00.md (Created 15 minutes ago)

Awaiting Review: 3 items
Approved (Ready): 0 items
Rejected: 1 item
Done (Today): 5 items
Expired: 0 items

⚠️ Expiring Soon:
  - EMAIL_2026-01-12T09-00-00.md (expires in 2 hours)
```

### Via Claude Code

Simply ask:
- "Process pending approvals"
- "Check approval queue"
- "Execute approved actions"

Claude will automatically use this skill.

## Action Routing

### Router Logic

```python
def route_action(action_file):
    """Route action to correct executor based on type."""

    metadata = parse_frontmatter(action_file)
    action_type = metadata.get('type')

    if action_type == 'email':
        return execute_email(action_file)
    elif action_type == 'linkedin_post':
        return execute_linkedin_post(action_file)
    elif action_type == 'payment':
        return execute_payment(action_file)  # Future
    else:
        raise UnknownActionType(action_type)
```

### Executor Mapping

| Action Type | Executor | Script Path |
|-------------|----------|-------------|
| `email` | email-sender | `skills/email-sender/scripts/send_email.py` |
| `linkedin_post` | linkedin-poster | `skills/linkedin-poster/scripts/linkedin_post.py` |
| `payment` | (future) | TBD |
| `file_operation` | (future) | TBD |

## Expiration Handling

### Automatic Expiration

Approval requests expire after 24 hours by default.

**Check expiration:**
```bash
python scripts/check_expirations.py
```

**What happens:**
1. Scans /Pending_Approval
2. Checks `expires` field in frontmatter
3. If expired (> 24 hours old):
   - Moves to /Expired folder
   - Logs expiration
   - No action taken

**Manual expiration override:**
Edit frontmatter and extend `expires` timestamp.

## Rejection Handling

### Process Rejections

When human moves file to /Rejected:

```bash
python scripts/process_approvals.py
```

**What happens:**
1. Detects file in /Rejected
2. Logs rejection with reason (if provided)
3. Moves to /Rejected archive
4. Updates Dashboard stats
5. No action executed

**Adding rejection reason:**

Edit rejection file and add:
```yaml
rejection_reason: "Content not appropriate for current audience"
rejected_by: "Your Name"
rejected_at: "2026-01-12T14:30:00Z"
```

## Error Handling

### Retry Logic

Failed actions are retried with exponential backoff:

- **Attempt 1:** Immediate
- **Attempt 2:** After 30 seconds
- **Attempt 3:** After 60 seconds
- **Max attempts:** 3

After 3 failures:
- Move to /Failed folder
- Log detailed error
- Alert human (Dashboard notification)

### Failed Action Recovery

```bash
# Retry failed action manually
python scripts/retry_failed.py /path/to/failed/action.md

# Or move back to /Approved for automatic retry
mv Done/EMAIL_*.md Approved/
```

### Common Errors

**"Executor not found"**
- Ensure skill scripts exist
- Check file paths in router configuration

**"Invalid action file format"**
- Verify frontmatter YAML is valid
- Check required fields present

**"Action timed out"**
- Increase timeout in configuration
- Check executor script for hangs

## Integration with Skills

### With email-sender

```
email-sender creates approval request
    ↓
File in /Pending_Approval
    ↓
Human reviews and moves to /Approved
    ↓
approval-processor detects
    ↓
Calls email-sender to execute
    ↓
Email sent, file moved to /Done
```

### With linkedin-poster

```
linkedin-poster creates approval request
    ↓
File in /Pending_Approval
    ↓
Human reviews and moves to /Approved
    ↓
approval-processor detects
    ↓
Calls linkedin-poster to execute
    ↓
Post published, file moved to /Done
```

### With scheduler-manager

```
Scheduled task triggers
    ↓
Generate content (report, post, etc.)
    ↓
Create approval request
    ↓
Human approves (async)
    ↓
approval-processor (runs every 5 min)
    ↓
Detects approval and executes
    ↓
Scheduled action complete
```

### With dashboard-updater

Dashboard displays:
- Pending approvals count
- Approved awaiting execution
- Executed today
- Failed actions
- Rejection rate

## Configuration

### Approval Settings

Edit `scripts/process_approvals.py` configuration:

```python
# Check interval for watcher (seconds)
CHECK_INTERVAL = 30

# Expiration time (hours)
EXPIRATION_HOURS = 24

# Retry attempts
MAX_RETRIES = 3

# Retry delays (seconds)
RETRY_DELAYS = [0, 30, 60]

# Auto-expire enabled
AUTO_EXPIRE = True
```

### Executor Paths

Edit `scripts/action_router.py`:

```python
EXECUTORS = {
    'email': {
        'script': '.claude/skills/email-sender/scripts/send_email.py',
        'arg': '--execute-approved'
    },
    'linkedin_post': {
        'script': '.claude/skills/linkedin-poster/scripts/linkedin_post.py',
        'arg': '--execute-approved'
    }
}
```

## Monitoring and Logging

### Activity Logs

All activity logged to:
- `/Logs/approval_activity_[date].json` - All processing
- `/Logs/actions_[date].json` - System actions
- Console output - Real-time status

**Log entry format:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "approval_executed",
  "details": {
    "file": "EMAIL_2026-01-12T10-00-00.md",
    "type": "email",
    "executor": "email-sender",
    "status": "success"
  },
  "skill": "approval-processor"
}
```

### Metrics Tracking

Track key metrics:
- **Approval rate:** Approved / (Approved + Rejected)
- **Processing time:** Time from approval to execution
- **Success rate:** Successful / Total processed
- **Expiration rate:** Expired / Total created

**View metrics:**
```bash
python scripts/show_metrics.py --period 7d
```

## Best Practices

### Approval Turnaround

**Recommended:**
- Check approvals 2-3 times daily minimum
- Process urgent items within 1 hour
- Set up notifications for new approvals

**Automated:**
- Run approval_watcher.py continuously
- Or schedule process_approvals.py every 5 minutes

### Folder Organization

**Keep clean:**
- Archive /Done items older than 30 days
- Review /Rejected for patterns
- Clear /Expired regularly

**Script for archiving:**
```bash
python scripts/archive_old.py --days 30
```

### Security

**Review before approving:**
- Verify recipient/audience
- Check content accuracy
- Validate attachments
- Confirm timing is appropriate

**Never auto-approve:**
- First-time recipients
- Large distributions
- Financial transactions
- Sensitive content

## Troubleshooting

### Approvals Not Processing

1. Check watcher is running: `ps aux | grep approval_watcher`
2. Verify files in /Approved folder: `ls Approved/`
3. Check logs: `cat Logs/approval_activity_*.json`
4. Run manually: `python scripts/process_approvals.py --verbose`

### Executor Errors

1. Test executor directly:
   ```bash
   python .claude/skills/email-sender/scripts/send_email.py --execute-approved /path/to/file.md
   ```
2. Check executor logs
3. Verify credentials configured

### File Not Moving to Done

1. Check file permissions
2. Verify /Done folder exists
3. Check for file conflicts (duplicate names)
4. Review error logs

## Scripts Reference

### process_approvals.py

Main approval processor (one-time execution).

**Usage:**
```bash
# Process all pending
python scripts/process_approvals.py

# Verbose output
python scripts/process_approvals.py --verbose

# Dry run (preview only)
python scripts/process_approvals.py --dry-run

# Process specific folder
python scripts/process_approvals.py --folder /Approved
```

### approval_watcher.py

Continuous monitoring daemon.

**Usage:**
```bash
# Start watcher (foreground)
python scripts/approval_watcher.py

# Background (Windows)
start pythonw scripts\approval_watcher.py

# Background (Linux/Mac)
nohup python scripts/approval_watcher.py &

# Custom interval
python scripts/approval_watcher.py --interval 60
```

### check_status.py

View approval queue status.

**Usage:**
```bash
# Current status
python scripts/check_status.py

# Detailed view
python scripts/check_status.py --detailed

# JSON output
python scripts/check_status.py --json
```

### check_expirations.py

Check and process expired approvals.

**Usage:**
```bash
# Check expirations
python scripts/check_expirations.py

# Move expired to /Expired
python scripts/check_expirations.py --move

# Custom expiration time
python scripts/check_expirations.py --hours 48
```

## Production Deployment

### Running as Service

**Windows (Task Scheduler):**
```
Task: Approval Watcher
Trigger: At system startup
Action: python approval_watcher.py
```

**Linux (systemd):**
```ini
[Unit]
Description=Approval Processor Watcher

[Service]
ExecStart=/usr/bin/python3 /path/to/approval_watcher.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**macOS (launchd):**
```xml
<plist>
  <dict>
    <key>Label</key>
    <string>com.aiemployee.approval</string>
    <key>ProgramArguments</key>
    <array>
      <string>python3</string>
      <string>/path/to/approval_watcher.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
```

### Process Management

Use PM2 (recommended):
```bash
# Install PM2
npm install -g pm2

# Start watcher
pm2 start scripts/approval_watcher.py --interpreter python3 --name approval-processor

# Auto-start on boot
pm2 startup
pm2 save

# Monitor
pm2 status
pm2 logs approval-processor
```

## References

- `references/approval_workflow.md` - Complete workflow documentation
- `references/action_types.md` - All supported action types
- `references/error_recovery.md` - Error handling guide

---

**Note:** This skill requires email-sender and/or linkedin-poster skills to be installed for action execution.
