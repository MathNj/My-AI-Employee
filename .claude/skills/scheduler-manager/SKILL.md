---
name: scheduler-manager
description: Cross-platform task scheduling for AI Employee automation. Creates, lists, and removes scheduled tasks using Windows Task Scheduler or Unix cron. Supports hourly, daily, weekly patterns and custom schedules. Includes recommended schedules for dashboard updates, approval processing, and financial analysis.
---

# scheduler-manager

## Overview

The **scheduler-manager** skill enables automated task scheduling for your Personal AI Employee using native OS schedulers (Windows Task Scheduler or Unix cron).

**Cross-Platform:** Works on Windows, Linux, and macOS.

---

## Quick Start

```bash
# Set up all recommended schedules (easiest!)
python .claude/skills/scheduler-manager/scripts/schedule_task.py --setup-recommended

# List current schedules
python .claude/skills/scheduler-manager/scripts/schedule_task.py --list

# Create custom schedule
python .claude/skills/scheduler-manager/scripts/schedule_task.py \
  --name "My_Task" \
  --command "python script.py" \
  --schedule hourly

# Remove schedule
python .claude/skills/scheduler-manager/scripts/schedule_task.py --remove "My_Task"
```

---

## When to Use This Skill

### ✅ Use when:
- Setting up AI Employee automation
- Need regular dashboard updates
- Want automatic approval processing
- Require scheduled financial analysis
- Need any recurring task execution

### ❌ Do NOT use when:
- One-time task execution needed
- Immediate execution required
- Testing/debugging (use direct script calls)

---

## Recommended Schedules

The skill includes pre-configured schedules optimized for AI Employee:

| Task | Name | Schedule | Purpose |
|------|------|----------|---------|
| Dashboard Update | AI_Employee_Dashboard_Update | Every hour | Keep dashboard current |
| Approval Processor | AI_Employee_Approval_Processor | Every 5 minutes | Process approved actions quickly |
| Financial Analysis | AI_Employee_Financial_Analysis | Daily at 9 AM | Daily financial health check |
| Task Processor | AI_Employee_Task_Processor | Every hour | Process new tasks |

**Set up all at once:**
```bash
python scripts/schedule_task.py --setup-recommended
```

---

## Core Capabilities

### 1. Create Schedules

**Named patterns:**
- `hourly` - Every hour at :00
- `daily` - Daily at 9 AM
- `weekly` - Monday at 9 AM
- `monthly` - 1st of month at 9 AM
- `every_5_min` - Every 5 minutes
- `every_15_min` - Every 15 minutes
- `every_30_min` - Every 30 minutes

**Custom cron format:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sun=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

**Examples:**
```bash
# Every hour
--schedule hourly
# or
--schedule "0 * * * *"

# Every day at 3 PM
--schedule "0 15 * * *"

# Every Monday at 8 AM
--schedule "0 8 * * 1"

# Every 10 minutes
--schedule "*/10 * * * *"
```

### 2. List Schedules

View all AI Employee scheduled tasks:

```bash
python scripts/schedule_task.py --list
```

**Output (Windows):**
```
**AI_Employee_Dashboard_Update**
  Status: Ready
  Next Run: 1/12/2026 3:00:00 PM
  Command: python "C:\...\dashboard_updater.py"
```

**Output (Unix):**
```
**AI_Employee_Dashboard_Update**
  Schedule: 0 * * * *
  Command: python "/path/to/dashboard_updater.py"
```

### 3. Remove Schedules

Remove specific scheduled task:

```bash
python scripts/schedule_task.py --remove "AI_Employee_Dashboard_Update"
```

---

## Platform Support

### Windows (Task Scheduler)

**Requirements:**
- Windows 7 or later
- Administrator privileges (for some operations)

**Backend:** Uses `schtasks` command

**Features:**
- GUI viewing (Task Scheduler app)
- Event log integration
- Power-aware scheduling
- Multiple triggers per task

### Linux (cron)

**Requirements:**
- cron daemon installed and running
- User permissions for crontab

**Backend:** Uses `crontab` command

**Features:**
- Standard cron syntax
- User-specific schedules
- System-wide schedules (with sudo)
- Email notifications (if configured)

### macOS (cron)

**Requirements:**
- macOS 10.10 or later
- Full Disk Access permission (System Preferences)

**Backend:** Uses `crontab` command

**Note:** macOS has deprecation warnings for cron. Future versions may require `launchd` instead (not yet implemented).

---

## Usage Examples

### Example 1: Set Up All Recommended Schedules

```bash
# One command to set up everything
python scripts/schedule_task.py --setup-recommended
```

This creates:
- Hourly dashboard updates
- 5-minute approval processing
- Daily financial analysis
- Hourly task processing

### Example 2: Custom Schedule for LinkedIn Posting

```bash
# Post check daily at 9 AM
python scripts/schedule_task.py \
  --name "AI_Employee_LinkedIn_Check" \
  --command "python .claude/skills/linkedin-poster/scripts/check_scheduled.py" \
  --schedule daily \
  --description "Check for scheduled LinkedIn posts"
```

### Example 3: Frequent Approval Processing

```bash
# Every 2 minutes
python scripts/schedule_task.py \
  --name "AI_Employee_Approval_Fast" \
  --command "python .claude/skills/approval-processor/scripts/process_approvals.py" \
  --schedule "*/2 * * * *"
```

### Example 4: Weekly CEO Briefing

```bash
# Monday 8 AM
python scripts/schedule_task.py \
  --name "AI_Employee_Weekly_Briefing" \
  --command "python .claude/skills/financial-analyst/scripts/weekly_report.py" \
  --schedule "0 8 * * 1" \
  --description "Weekly business briefing for CEO"
```

---

## Integration with Other Skills

### With approval-processor

```
schedule_task creates "every 5 min" schedule
    ↓
OS runs approval-processor automatically
    ↓
Approved actions executed promptly
    ↓
Human approves, AI acts fast
```

### With dashboard-updater

```
schedule_task creates "hourly" schedule
    ↓
Dashboard refreshed automatically
    ↓
Always up-to-date status
```

### With financial-analyst

```
schedule_task creates "daily at 9 AM" schedule
    ↓
Financial analysis runs every morning
    ↓
Reports ready for review
```

---

## Best Practices

### Frequency Guidelines

**Every 5 minutes:**
- Approval processing (responsive to human decisions)
- High-priority monitoring

**Every hour:**
- Dashboard updates
- Task processing
- Status checks

**Daily:**
- Financial analysis
- Report generation
- Email summaries

**Weekly:**
- Business reviews
- Subscription audits
- Cleanup tasks

**Monthly:**
- Archiving
- Long-term analysis
- Budget reviews

### Resource Considerations

1. **Don't over-schedule**
   - Avoid < 5 minute intervals for heavy tasks
   - Consider system load

2. **Stagger schedules**
   - Don't run everything at :00
   - Spread across the hour

3. **Test first**
   - Run script manually before scheduling
   - Verify paths and permissions

4. **Monitor logs**
   - Check `/Logs` for execution history
   - Review failures and adjust

---

## Via Claude Code

When using Claude Code, simply ask:

- "Set up scheduling for AI Employee"
- "Schedule dashboard updates"
- "Create hourly approval processing"
- "Show me current schedules"

Claude will:
1. Use scheduler-manager skill
2. Create appropriate schedules
3. Verify setup
4. Report status

---

## Troubleshooting

### Windows: "Access Denied"

**Cause:** Insufficient permissions

**Solutions:**
1. Run Command Prompt as Administrator
2. Or create task for current user only

### Windows: Task Doesn't Run

**Causes:**
- Task Scheduler service stopped
- Wrong path to Python/script
- User not logged in (if "Run only when user is logged on")

**Solutions:**
1. Check Task Scheduler service: `services.msc`
2. Verify paths are absolute
3. Set task to "Run whether user is logged on or not"

### Unix: Cron Job Not Running

**Causes:**
- cron daemon not running
- Wrong path to Python/script
- Environment variables not set
- Permission issues

**Solutions:**
1. Check cron service: `sudo service cron status`
2. Use absolute paths
3. Set PATH in crontab: `PATH=/usr/bin:/usr/local/bin`
4. Test with simple command first

### macOS: Permission Denied

**Cause:** Full Disk Access not granted

**Solution:**
1. System Preferences → Security & Privacy → Privacy
2. Full Disk Access
3. Add Terminal/Python to allowed apps

### Task Runs But Fails

**Causes:**
- Working directory different
- Missing dependencies
- Wrong Python environment

**Solutions:**
1. Use absolute paths everywhere
2. `cd` to correct directory in command
3. Use full Python path: `/usr/bin/python3`

---

## Monitoring and Logging

All scheduling operations logged to:
`/Logs/scheduler_YYYY-MM-DD.json`

**Log entry:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "task_created",
  "details": {
    "name": "AI_Employee_Dashboard_Update",
    "command": "python dashboard_updater.py",
    "schedule": "hourly",
    "platform": "windows"
  },
  "skill": "scheduler-manager"
}
```

**Scheduled task execution** logged by individual skills (dashboard-updater, approval-processor, etc.)

---

## Security Considerations

### Command Injection Prevention

- Uses subprocess with list arguments (not shell=True)
- Validates schedule format
- No user input passed to shell directly

### Permission Model

**Windows:**
- Tasks run under creating user
- Can specify different user (requires password)
- Recommend running as current user

**Unix:**
- User-specific crontab (no root needed)
- System crontab requires sudo
- Recommend user crontab for AI Employee

### Audit Trail

- All operations logged
- Task creation/removal tracked
- Review logs regularly

---

## Limitations

### What It Can Do

✅ Create scheduled tasks
✅ List current schedules
✅ Remove schedules
✅ Cross-platform (Windows/Linux/Mac)
✅ Named patterns and custom cron
✅ Recommended AI Employee schedules

### What It Cannot Do

❌ Modify existing schedules (remove and recreate)
❌ Conditional scheduling (run if X condition)
❌ Task dependencies (run B after A)
❌ Remote task scheduling
❌ GUI task management

### Platform-Specific Limitations

**Windows:**
- No sub-minute scheduling (<1 minute)
- Requires Task Scheduler service

**Unix:**
- Minimum 1-minute intervals
- No GUI (Task Scheduler apps available separately)

**macOS:**
- cron deprecated (still works but may require launchd in future)
- Requires Full Disk Access permission

---

## Advanced Usage

### Running Tasks in Background

**Windows:**
```bash
# Use pythonw.exe to run without console window
--command "pythonw C:\path\to\script.py"
```

**Unix:**
```bash
# Redirect output to log file
--command "python /path/to/script.py >> /path/to/log.txt 2>&1"
```

### Multiple Schedules for Same Script

```bash
# Hourly during work hours
python schedule_task.py \
  --name "Task_Work_Hours" \
  --command "python script.py" \
  --schedule "0 9-17 * * 1-5"

# Different schedule for weekends
python schedule_task.py \
  --name "Task_Weekends" \
  --command "python script.py" \
  --schedule "0 10 * * 0,6"
```

### Environment Variables

**Unix crontab:**
```bash
# Add to crontab before scheduled commands
PATH=/usr/local/bin:/usr/bin:/bin
VAULT_PATH=/path/to/vault

0 * * * * python $VAULT_PATH/.claude/skills/...
```

---

## Migration Guide

### From Manual Execution

**Before:**
```bash
# Running manually
python dashboard_updater.py
```

**After:**
```bash
# Set up schedule once
python schedule_task.py \
  --name "Dashboard_Update" \
  --command "python /full/path/to/dashboard_updater.py" \
  --schedule hourly

# Runs automatically every hour
```

### From Other Schedulers

**If using external scheduler:**
1. List current tasks
2. Note schedules and commands
3. Remove from old scheduler
4. Set up with scheduler-manager
5. Verify execution

---

## Silver Tier Completion

**This skill completes Silver Tier Requirement #8:**
"Basic scheduling via cron/Task Scheduler" ✅

With scheduler-manager, your AI Employee can now:
- Run tasks automatically
- Process approvals continuously
- Update dashboard regularly
- Generate reports on schedule

**Silver Tier: 100% COMPLETE!** 🎉

---

**Remember:** Always test scheduled tasks manually before setting up automation. Verify paths, permissions, and execution.
