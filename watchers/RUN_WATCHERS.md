# Running Multiple Watchers

Guide for running both Filesystem and Gmail watchers simultaneously.

## Overview

Your Personal AI Employee can monitor multiple sources at once:
- **Filesystem Watcher** - Monitors `/Inbox` folder for new files
- **Gmail Watcher** - Monitors Gmail for unread important emails

Both watchers run independently and create tasks in `/Needs_Action`.

## Quick Start

### Option 1: Run Each Watcher in Separate Terminals

**Terminal 1 - Filesystem Watcher:**
```bash
python watchers/filesystem_watcher.py
```

**Terminal 2 - Gmail Watcher:**
```bash
python watchers/gmail_watcher.py
```

Keep both terminals open and running.

### Option 2: Run in Background (Recommended)

**Windows:**
```bash
# Start filesystem watcher
start pythonw watchers\filesystem_watcher.py

# Start Gmail watcher
start pythonw watchers\gmail_watcher.py
```

**Linux/Mac:**
```bash
# Start filesystem watcher
nohup python watchers/filesystem_watcher.py > /dev/null 2>&1 &

# Start Gmail watcher
nohup python watchers/gmail_watcher.py > /dev/null 2>&1 &
```

### Option 3: Use Process Manager (Best for 24/7)

Install PM2 (if not already installed):
```bash
npm install -g pm2
```

Start both watchers:
```bash
# Start filesystem watcher
pm2 start watchers/filesystem_watcher.py --interpreter python3 --name fs-watcher

# Start Gmail watcher
pm2 start watchers/gmail_watcher.py --interpreter python3 --name gmail-watcher

# Save configuration
pm2 save

# Set up auto-start on boot
pm2 startup
```

View status:
```bash
pm2 status
```

View logs:
```bash
pm2 logs
```

Stop watchers:
```bash
pm2 stop all
```

## Master Watcher Script (Optional)

Create a master script to run all watchers:

### Create `watchers/run_all.py`

```python
#!/usr/bin/env python3
"""
Master script to run all watchers
"""
import subprocess
import sys
from pathlib import Path

VAULT_PATH = Path(__file__).parent.parent.resolve()
WATCHERS_PATH = VAULT_PATH / "watchers"

def main():
    print("=" * 60)
    print("Starting All Watchers")
    print("=" * 60)

    watchers = [
        ("Filesystem Watcher", "filesystem_watcher.py"),
        ("Gmail Watcher", "gmail_watcher.py"),
    ]

    processes = []

    for name, script in watchers:
        script_path = WATCHERS_PATH / script
        if script_path.exists():
            print(f"Starting {name}...")
            proc = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(VAULT_PATH)
            )
            processes.append((name, proc))
            print(f"  ✓ {name} started (PID: {proc.pid})")
        else:
            print(f"  ✗ {name} script not found: {script}")

    print("=" * 60)
    print(f"Running {len(processes)} watcher(s)")
    print("Press Ctrl+C to stop all watchers")
    print("=" * 60)

    try:
        # Wait for all processes
        for name, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Stopping all watchers...")
        for name, proc in processes:
            proc.terminate()
            print(f"  ✓ Stopped {name}")
        print("=" * 60)

if __name__ == "__main__":
    main()
```

Then run:
```bash
python watchers/run_all.py
```

## Monitoring Watcher Status

### Check Running Processes

**Windows:**
```bash
tasklist | findstr python
```

**Linux/Mac:**
```bash
ps aux | grep watcher
```

### Check Logs

Each watcher creates daily logs:

```bash
# Filesystem watcher logs
cat Logs/watcher_2026-01-11.log

# Gmail watcher logs
cat Logs/gmail_watcher_2026-01-11.log

# All watcher activity (combined)
cat Logs/actions_2026-01-11.json
```

### View Recent Activity

```bash
# Last 20 lines of filesystem watcher
tail -20 Logs/watcher_*.log

# Last 20 lines of Gmail watcher
tail -20 Logs/gmail_watcher_*.log

# Follow logs in real-time
tail -f Logs/watcher_*.log
```

## Dashboard Integration

Update Dashboard to see all watcher activity:

```bash
python .claude/skills/dashboard-updater/scripts/update_dashboard.py
cat Dashboard.md
```

The dashboard will show:
- Total tasks detected
- Recent watcher activity
- System health status

## Troubleshooting

### Only One Watcher Running

**Check which watchers are active:**
```bash
ps aux | grep -E "filesystem_watcher|gmail_watcher"
```

**Restart missing watcher:**
```bash
python watchers/filesystem_watcher.py
# OR
python watchers/gmail_watcher.py
```

### High CPU Usage

If watchers are using too much CPU:

1. **Increase check intervals:**
   - Gmail watcher: Edit `CHECK_INTERVAL` in `gmail_watcher.py`
   - Filesystem watcher: Uses events (already efficient)

2. **Use PM2 with limits:**
   ```bash
   pm2 start watchers/gmail_watcher.py --max-memory-restart 100M
   ```

### Watchers Stopping Unexpectedly

**Check error logs:**
```bash
cat Logs/watcher_*.log
cat Logs/gmail_watcher_*.log
```

**Common issues:**
- Gmail token expired - Delete `token.pickle` and re-authenticate
- Network connection lost - Watchers will retry automatically
- Permission errors - Check folder permissions

### Duplicate Tasks Created

This shouldn't happen because watchers track processed items:
- Filesystem watcher: Only triggers on new files
- Gmail watcher: Tracks processed message IDs

If it does happen:
```bash
# Check for duplicate tracking
cat Logs/gmail_processed_ids.json
```

## Performance Tuning

### Filesystem Watcher
- **Detection:** Instant (event-driven)
- **CPU usage:** Near zero when idle
- **Memory:** ~10-20 MB
- **Tuning:** No configuration needed

### Gmail Watcher
- **Check interval:** 120 seconds (2 minutes) default
- **CPU usage:** Minimal between checks
- **Memory:** ~30-50 MB
- **Tuning:** Adjust `CHECK_INTERVAL`

**For high-volume email:**
```python
CHECK_INTERVAL = 60  # Check every minute
```

**For low-volume email:**
```python
CHECK_INTERVAL = 300  # Check every 5 minutes
```

## Watcher Comparison

| Feature | Filesystem | Gmail |
|---------|-----------|-------|
| Detection | Real-time (events) | Polling (2 min) |
| CPU Usage | Very Low | Low |
| Setup | None | OAuth2 required |
| Reliability | Very High | High |
| Offline Mode | Yes | No (needs internet) |

## Advanced: Systemd Service (Linux)

For Linux servers, create systemd services:

### `/etc/systemd/system/ai-employee-filesystem.service`
```ini
[Unit]
Description=AI Employee Filesystem Watcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/AI_Employee_Vault
ExecStart=/usr/bin/python3 watchers/filesystem_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/ai-employee-gmail.service`
```ini
[Unit]
Description=AI Employee Gmail Watcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/AI_Employee_Vault
ExecStart=/usr/bin/python3 watchers/gmail_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ai-employee-filesystem
sudo systemctl enable ai-employee-gmail
sudo systemctl start ai-employee-filesystem
sudo systemctl start ai-employee-gmail
```

## Testing Both Watchers

### Test 1: Filesystem Watcher
```bash
echo "Test file" > Inbox/test.txt
ls Needs_Action/
```

### Test 2: Gmail Watcher
1. Send yourself an important email
2. Wait 2 minutes
3. Check: `ls Needs_Action/EMAIL_*.md`

### Test 3: Both Together
1. Drop file in Inbox
2. Send yourself an email
3. Wait 2 minutes
4. Check: `ls Needs_Action/`
5. Should see both FILE_* and EMAIL_* tasks

### Test 4: Process All Tasks
```bash
python .claude/skills/task-processor/scripts/process_tasks.py
ls Plans/
```

### Test 5: Update Dashboard
```bash
python .claude/skills/dashboard-updater/scripts/update_dashboard.py
cat Dashboard.md
```

## Best Practices

### For Development/Testing
- Run watchers in foreground (separate terminals)
- Monitor logs in real-time
- Easy to stop with Ctrl+C

### For Production/Daily Use
- Use PM2 or systemd
- Set up auto-restart on failure
- Configure log rotation
- Monitor via dashboard

### For 24/7 Operation
- Dedicated mini-PC or cloud VM
- PM2 with auto-startup
- Regular health checks
- Backup processed IDs database

## Next Steps

After setting up watchers:
1. ✅ Both watchers running
2. ⏳ Process tasks automatically with scheduling
3. ⏳ Set up MCP servers for actions (email replies)
4. ⏳ Configure approval workflows
5. ⏳ Add more watchers (WhatsApp, LinkedIn)

---

**Your AI Employee is now monitoring multiple channels 24/7!**

*Filesystem and Gmail integration complete*
*Ready for Silver tier features*
