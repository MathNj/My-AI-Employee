# AI Employee Orchestration System

## Overview

This orchestration system manages all your AI Employee watchers and posters automatically. You no longer need to manually start each watcher - the orchestrator handles everything.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      WATCHDOG                               │
│  (Monitors orchestrator, restarts if crashed)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                              │
│  (Manages all watcher/poster processes)                     │
├─────────────────────────────────────────────────────────────┤
│  - Starts all enabled watchers                              │
│  - Monitors health every 60 seconds                         │
│  - Auto-restarts failed processes                           │
│  - Handles graceful shutdown                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │Calendar │   │ Slack   │   │ Gmail   │   │WhatsApp │
   │ Watcher │   │ Watcher │   │ Watcher │   │ Watcher │
   └─────────┘   └─────────┘   └─────────┘   └─────────┘

   ┌─────────┐   ┌─────────┐
   │FileSys  │   │  Xero   │
   │ Watcher │   │ Watcher │
   └─────────┘   └─────────┘
```

## Components

### 1. **orchestrator.py**
The master process manager that:
- Starts all enabled watchers
- Monitors their health every 60 seconds
- Auto-restarts crashed processes
- Handles graceful shutdown

### 2. **watchdog.py**
The watchdog for the watchdog:
- Monitors the orchestrator itself
- Restarts it if it crashes
- Ensures 24/7 operation

### 3. **orchestrator_cli.py**
Command-line interface for management:
- `python orchestrator_cli.py start` - Start orchestrator
- `python orchestrator_cli.py stop` - Stop all processes
- `python orchestrator_cli.py status` - Check status
- `python orchestrator_cli.py restart` - Restart everything

### 4. **orchestrator_config.json**
Configuration file for customizing:
- Check intervals for each watcher
- Enable/disable specific watchers
- Auto-restart settings
- Logging levels

## Quick Start

### Option 1: Manual Start (for testing)

1. **Start the orchestrator:**
   ```bash
   python orchestrator.py
   ```

2. **Check status:**
   ```bash
   python orchestrator_cli.py status
   ```

3. **Stop all watchers:**
   ```bash
   python orchestrator_cli.py stop
   ```

### Option 2: Auto-Start on Boot (recommended)

1. **Run setup script:**
   ```bash
   setup_auto_start.bat
   ```
   (Right-click → Run as Administrator)

2. **The watchdog will now start automatically on Windows login**

3. **To disable auto-start:**
   ```bash
   schtasks /Delete /TN "AI Employee Watchdog" /F
   ```

### Option 3: Using Batch Files (easiest)

1. **Start all:**
   Double-click `start_ai_employee.bat`

2. **Stop all:**
   Double-click `stop_ai_employee.bat`

## Configuration

Edit `orchestrator_config.json` to customize:

```json
{
  "check_interval": 60,
  "processes": {
    "calendar": {
      "enabled": true,
      "priority": "high"
    },
    "slack": {
      "enabled": true,
      "priority": "high"
    },
    "gmail": {
      "enabled": true,
      "priority": "high"
    },
    "whatsapp": {
      "enabled": true,
      "requires_visible_browser": true
    },
    "filesystem": {
      "enabled": true
    },
    "xero": {
      "enabled": true
    }
  }
}
```

### Enable/Disable Watchers

Set `"enabled": false` for any watcher you don't want to run:

```json
"xero": {
  "enabled": false
}
```

## Managed Watchers

The orchestrator manages these watchers:

1. **Calendar Watcher** - Google Calendar events (1-48 hours ahead)
2. **Slack Watcher** - Slack messages with keywords
3. **Gmail Watcher** - Unread important emails
4. **WhatsApp Watcher** - WhatsApp messages with keywords (visible mode)
5. **Filesystem Watcher** - Files dropped in Inbox folder
6. **Xero Watcher** - Financial events (invoices, bills, payments)

## Monitoring & Health Checks

### Automatic Health Checks

The orchestrator runs health checks every 60 seconds:
- Detects crashed processes
- Auto-restarts failed watchers
- Logs all restart events

### Check Status Manually

```bash
python orchestrator_cli.py status
```

Output:
```
======================================================================
AI Employee Status
======================================================================
Orchestrator PID: 12345
Memory: 45.3 MB

Running Watchers:
  - Calendar Watcher (PID: 12346)
  - Slack Watcher (PID: 12347)
  - Gmail Watcher (PID: 12348)
  - Whatsapp Watcher (PID: 12349)
  - Filesystem Watcher (PID: 12350)
  - Xero Watcher (PID: 12351)
======================================================================
```

## Logs

All activities are logged:

- `orchestrator.log` - Orchestrator activity and health checks
- `watchdog.log` - Watchdog monitoring and restarts
- Individual watcher logs in their own files

## Troubleshooting

### Orchestrator won't start

1. Check if it's already running:
   ```bash
   python orchestrator_cli.py status
   ```

2. Check the log:
   ```bash
   type orchestrator.log
   ```

3. Ensure all watcher scripts exist:
   ```bash
   dir *_watcher.py
   ```

### Watcher keeps crashing

1. Check orchestrator log:
   ```bash
   type orchestrator.log | findstr "ERROR"
   ```

2. Disable the problematic watcher in config:
   ```json
   "problematic_watcher": {
     "enabled": false
   }
   ```

3. Test the watcher manually:
   ```bash
   python calendar_watcher.py
   ```

### Auto-start not working

1. Verify the scheduled task exists:
   ```bash
   schtasks /Query /TN "AI Employee Watchdog"
   ```

2. Run the task manually:
   ```bash
   schtasks /Run /TN "AI Employee Watchdog"
   ```

3. Check Task Scheduler Event Viewer for errors

## Advanced Usage

### Running Specific Watchers Only

Edit `orchestrator_config.json` and disable unwanted watchers:

```json
{
  "processes": {
    "calendar": {"enabled": true},
    "slack": {"enabled": true},
    "gmail": {"enabled": false},
    "whatsapp": {"enabled": false},
    "filesystem": {"enabled": true},
    "xero": {"enabled": false}
  }
}
```

### Changing Check Intervals

Override individual watcher check intervals:

```json
{
  "processes": {
    "slack": {
      "enabled": true,
      "check_interval_override": 30
    }
  }
}
```

### Custom Notifications

The system supports notification hooks (future enhancement):

```json
{
  "notifications": {
    "email_on_failure": true,
    "slack_on_failure": true
  }
}
```

## Best Practices

1. **Always use the orchestrator** - Don't manually start individual watchers
2. **Enable auto-start** - Set up Windows Task Scheduler for 24/7 operation
3. **Monitor logs regularly** - Check `orchestrator.log` weekly
4. **Test before enabling** - Test each watcher individually before adding to orchestrator
5. **Keep config backed up** - Save `orchestrator_config.json` to version control

## Workflow

### Daily Operation

1. **Morning:** Check dashboard in Obsidian
2. **Automatic:** Orchestrator runs all watchers 24/7
3. **Automatic:** Failed processes auto-restart
4. **Evening:** Review any tasks in Needs_Action folder

### Weekly Maintenance

1. Review orchestrator logs
2. Check for repeated crashes
3. Update watcher configurations if needed
4. Verify all watchers are functioning

### Monthly Audit

1. Review all auto-restart events
2. Check system resource usage
3. Update credentials if expiring
4. Review and optimize check intervals

## Security Notes

- The orchestrator runs with your user permissions
- All credentials are stored in `watchers/credentials/` (gitignored)
- Logs may contain sensitive information - review before sharing
- Auto-start runs at user login (not system startup)

## Next Steps

After setting up orchestration:

1. ✓ Configure auto-start for 24/7 operation
2. ✓ Set up approval workflow for posters
3. ✓ Configure scheduled tasks (CEO Briefing, etc.)
4. ✓ Test failure scenarios and auto-restart
5. ✓ Set up monitoring and alerts

## Support

For issues or questions:
- Check logs: `orchestrator.log`, `watchdog.log`
- Review watcher-specific logs
- Test individual components manually
- Consult Requirements1.md for architecture details
