---
name: dashboard-updater
description: Update Dashboard.md with current system status for Personal AI Employee. Use when the user needs to refresh the dashboard, show current status, update activity logs, or generate status reports. Triggers include "update dashboard", "refresh dashboard", "show status", "what's the current state", "generate report", or "update activity log".
---

# Dashboard Updater

## Overview

This skill updates the Dashboard.md file with current system status, task counts, recent activity, and alerts. It provides a real-time view of the AI Employee's operations.

## Core Workflow

### 1. Collect System Statistics

Gather data from various folders:
- Count files in `/Needs_Action` (pending tasks)
- Count files in `/Plans` (active plans)
- Count files in `/Pending_Approval` (awaiting approval)
- Count files in `/Done` (completed today/this week)
- Read latest log entries

### 2. Update Dashboard Sections

Update these sections in Dashboard.md:

**System Status:**
- Vault location
- Active watchers count
- Pending/completed task counts

**Quick Stats Table:**
- Tasks in each folder
- Plans generated
- Completions (today/week)

**Recent Activity:**
- Latest 10 actions from logs
- Formatted as table or list

**Alerts & Notifications:**
- Any high-priority tasks
- Failed operations
- System warnings

### 3. Add Timestamp

Update the "Last refreshed" timestamp at the bottom of Dashboard.

## Usage

**Manual update:**
```bash
python scripts/update_dashboard.py
```

**From Claude:**
Simply ask "update dashboard" and Claude will use this skill to refresh Dashboard.md.

**Automated:**
Call after task processing or at scheduled intervals.

## Dashboard Sections

### Quick Stats
Shows current counts for monitoring health:
- Pending tasks (should trend to zero)
- Completed tasks (should increase)
- Approval queue (highlights attention needed)

### Recent Activity
Last 10 actions logged:
- Timestamp
- Action type
- Status (success/failed)
- Brief details

### Alerts
Highlights items needing attention:
- High-priority pending tasks
- Stale approval requests (>24 hours)
- Failed watcher scripts
- System errors

### System Health
Visual indicators:
- ✅ Green: Working normally
- ⚠️ Yellow: Attention needed
- ❌ Red: Error/failure

## Integration Points

The dashboard-updater integrates with:
- **task-processor:** After processing tasks
- **watcher-manager:** Watcher status updates
- **Log files:** Reading recent activity

## Data Sources

### /Logs/actions_[date].json
Action log format:
```json
{
  "timestamp": "2026-01-11T10:30:00Z",
  "action": "task_processed",
  "details": { }
}
```

### Folder Counts
- `/Needs_Action/*.md`
- `/Plans/*.md`
- `/Pending_Approval/*.md`
- `/Done/*.md` (filtered by date)

### Watcher Status
Check `/watchers/*.log` for last update time.

## Output Format

Dashboard.md follows this structure:
```markdown
# AI Employee Dashboard

## System Status
[Current counts and status]

## Quick Stats
[Table of key metrics]

## Recent Activity
[Latest actions]

## Alerts & Notifications
[Items needing attention]

## System Health
[Visual health indicators]

---
*Last refreshed: [timestamp]*
```

## Resources

### scripts/update_dashboard.py
Main script to refresh dashboard with latest data.

### references/dashboard_sections.md
Detailed specification for each dashboard section.
