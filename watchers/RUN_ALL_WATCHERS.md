# Running All Watchers - Complete Guide

Complete guide to run all 5 watchers for your Personal AI Employee system.

---

## Overview

Your AI Employee has **5 watchers** that monitor different input sources:

| Watcher | Source | Frequency | Protocol |
|---------|--------|-----------|----------|
| **Filesystem** | Local file drops | Real-time | Watchdog |
| **Gmail** | Email inbox | 2 minutes | OAuth 2.0 |
| **WhatsApp** | WhatsApp messages | 5 minutes | Playwright |
| **Xero** | Accounting system | 5 minutes | OAuth 2.0 |
| **Slack** | Team communication | 1 minute | Bot Token |

---

## Quick Start (Development Mode)

Run all watchers in separate terminal windows for testing:

### Terminal 1: Filesystem Watcher
```bash
cd watchers
python filesystem_watcher.py
```

### Terminal 2: Gmail Watcher
```bash
cd watchers
python gmail_watcher.py
```

### Terminal 3: WhatsApp Watcher
```bash
cd watchers
python whatsapp_watcher.py
```

### Terminal 4: Xero Watcher
```bash
cd watchers
python xero_watcher.py
```

### Terminal 5: Slack Watcher
```bash
cd watchers
python slack_watcher.py
```

---

## Production Deployment

### Option 1: Windows Task Scheduler (Recommended)

Schedule watchers to run automatically:

```powershell
# Navigate to project directory
cd C:\Users\YourName\Desktop\My Vault

# Create scheduled tasks
schtasks /create /tn "AI_Employee_Gmail" /tr "python %CD%\watchers\gmail_watcher.py" /sc minute /mo 2
schtasks /create /tn "AI_Employee_WhatsApp" /tr "python %CD%\watchers\whatsapp_watcher.py" /sc minute /mo 5
schtasks /create /tn "AI_Employee_Xero" /tr "python %CD%\watchers\xero_watcher.py" /sc minute /mo 5
schtasks /create /tn "AI_Employee_Slack" /tr "python %CD%\watchers\slack_watcher.py" /sc minute /mo 1

# Filesystem watcher as startup task (runs continuously)
schtasks /create /tn "AI_Employee_Filesystem" /tr "python %CD%\watchers\filesystem_watcher.py" /sc onstart
```

**Verify tasks created:**
```powershell
schtasks /query /tn "AI_Employee_Gmail"
schtasks /query /tn "AI_Employee_WhatsApp"
schtasks /query /tn "AI_Employee_Xero"
schtasks /query /tn "AI_Employee_Slack"
schtasks /query /tn "AI_Employee_Filesystem"
```

**Start tasks manually:**
```powershell
schtasks /run /tn "AI_Employee_Gmail"
schtasks /run /tn "AI_Employee_WhatsApp"
schtasks /run /tn "AI_Employee_Xero"
schtasks /run /tn "AI_Employee_Slack"
schtasks /run /tn "AI_Employee_Filesystem"
```

**Stop tasks:**
```powershell
schtasks /end /tn "AI_Employee_Gmail"
schtasks /end /tn "AI_Employee_WhatsApp"
schtasks /end /tn "AI_Employee_Xero"
schtasks /end /tn "AI_Employee_Slack"
schtasks /end /tn "AI_Employee_Filesystem"
```

**Delete tasks (cleanup):**
```powershell
schtasks /delete /tn "AI_Employee_Gmail" /f
schtasks /delete /tn "AI_Employee_WhatsApp" /f
schtasks /delete /tn "AI_Employee_Xero" /f
schtasks /delete /tn "AI_Employee_Slack" /f
schtasks /delete /tn "AI_Employee_Filesystem" /f
```

### Option 2: Linux/Mac Cron Jobs

Add to crontab:

```bash
# Edit crontab
crontab -e

# Add these lines:
*/2 * * * * cd /path/to/My\ Vault/watchers && python gmail_watcher.py >> /tmp/gmail_watcher.log 2>&1
*/5 * * * * cd /path/to/My\ Vault/watchers && python whatsapp_watcher.py >> /tmp/whatsapp_watcher.log 2>&1
*/5 * * * * cd /path/to/My\ Vault/watchers && python xero_watcher.py >> /tmp/xero_watcher.log 2>&1
* * * * * cd /path/to/My\ Vault/watchers && python slack_watcher.py >> /tmp/slack_watcher.log 2>&1

# Filesystem watcher via systemd or run manually in screen/tmux
```

**Using systemd (better for long-running processes):**

Create `/etc/systemd/system/ai-employee-filesystem.service`:

```ini
[Unit]
Description=AI Employee Filesystem Watcher
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/My Vault/watchers
ExecStart=/usr/bin/python3 filesystem_watcher.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ai-employee-filesystem
sudo systemctl start ai-employee-filesystem
sudo systemctl status ai-employee-filesystem
```

### Option 3: Background Processes (Quick Testing)

**Windows PowerShell:**
```powershell
cd watchers

# Start all in background
Start-Process python -ArgumentList "filesystem_watcher.py" -WindowStyle Hidden
Start-Process python -ArgumentList "gmail_watcher.py" -WindowStyle Hidden
Start-Process python -ArgumentList "whatsapp_watcher.py" -WindowStyle Hidden
Start-Process python -ArgumentList "xero_watcher.py" -WindowStyle Hidden
Start-Process python -ArgumentList "slack_watcher.py" -WindowStyle Hidden
```

**Linux/Mac:**
```bash
cd watchers

# Start all in background with nohup
nohup python filesystem_watcher.py > /tmp/fs_watcher.log 2>&1 &
nohup python gmail_watcher.py > /tmp/gmail_watcher.log 2>&1 &
nohup python whatsapp_watcher.py > /tmp/whatsapp_watcher.log 2>&1 &
nohup python xero_watcher.py > /tmp/xero_watcher.log 2>&1 &
nohup python slack_watcher.py > /tmp/slack_watcher.log 2>&1 &

# View running processes
ps aux | grep watcher

# Stop all watchers
pkill -f "watcher.py"
```

---

## Master Control Script (Recommended)

Create a master script to control all watchers:

**File:** `watchers/run_all.py`

```python
#!/usr/bin/env python3
"""
Master control script for all AI Employee watchers.
Start, stop, and monitor all watchers from one place.
"""

import subprocess
import sys
import time
from pathlib import Path

WATCHERS = [
    {'name': 'Filesystem', 'script': 'filesystem_watcher.py', 'mode': 'continuous'},
    {'name': 'Gmail', 'script': 'gmail_watcher.py', 'mode': 'polling'},
    {'name': 'WhatsApp', 'script': 'whatsapp_watcher.py', 'mode': 'polling'},
    {'name': 'Xero', 'script': 'xero_watcher.py', 'mode': 'polling'},
    {'name': 'Slack', 'script': 'slack_watcher.py', 'mode': 'polling'},
]

def start_all():
    """Start all watchers."""
    print("=" * 70)
    print("Starting AI Employee Watchers")
    print("=" * 70)

    processes = []

    for watcher in WATCHERS:
        print(f"Starting {watcher['name']} Watcher...")
        try:
            proc = subprocess.Popen(
                [sys.executable, watcher['script']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append((watcher['name'], proc))
            print(f"  ✓ {watcher['name']} started (PID: {proc.pid})")
        except Exception as e:
            print(f"  ✗ Failed to start {watcher['name']}: {e}")

    print("\n" + "=" * 70)
    print(f"All watchers started. Press Ctrl+C to stop all.")
    print("=" * 70)

    try:
        # Keep script running and monitor processes
        while True:
            time.sleep(10)

            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} watcher stopped unexpectedly!")

    except KeyboardInterrupt:
        print("\n\nStopping all watchers...")

        for name, proc in processes:
            print(f"  Stopping {name}...")
            proc.terminate()
            proc.wait(timeout=5)

        print("✓ All watchers stopped")

if __name__ == "__main__":
    start_all()
```

**Usage:**
```bash
python watchers/run_all.py
```

---

## Monitoring Watchers

### Check Status

**Windows:**
```powershell
# Check if tasks are running
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI_Employee*"}

# View logs
Get-Content Logs\*watcher*.log -Tail 50
```

**Linux/Mac:**
```bash
# Check running processes
ps aux | grep watcher

# View logs
tail -f Logs/*watcher*.log
```

### View Recent Activity

```bash
# Today's logs
ls -lh Logs/*watcher*$(date +%Y-%m-%d).log

# Action logs (JSON)
cat Logs/actions_$(date +%Y-%m-%d).json | python -m json.tool

# Files created in Needs_Action
ls -lth Needs_Action/ | head -20
```

### Dashboard Check

```bash
# View dashboard status
cat AI_Employee_Vault/Dashboard.md

# Count pending tasks
ls Needs_Action/ | wc -l

# Count completed tasks
ls Done/ | wc -l
```

---

## Troubleshooting

### Watcher Not Starting

**Check Python:**
```bash
python --version  # Should be 3.8+
which python      # Verify correct Python
```

**Check Dependencies:**
```bash
pip install -r requirements.txt
pip list | grep -E "watchdog|google-auth|playwright|requests"
```

**Check Permissions:**
```bash
# Windows: Run as Administrator
# Linux/Mac:
chmod +x watchers/*.py
```

### No Files Created

1. **Check watcher logs:**
   ```bash
   tail -f Logs/*watcher*.log
   ```

2. **Verify source has new items:**
   - Gmail: Send test email
   - Filesystem: Drop test file
   - WhatsApp: Send test message
   - Xero: Create test invoice

3. **Check Needs_Action folder:**
   ```bash
   ls -lh Needs_Action/
   ```

4. **Verify watchers are running:**
   ```bash
   ps aux | grep watcher  # Linux/Mac
   Get-Process | Where-Object {$_.Name -like "*python*"}  # Windows
   ```

### High CPU/Memory Usage

```bash
# Check resource usage
top -p $(pgrep -f watcher)  # Linux
Get-Process python  # Windows

# Increase check intervals in config files
# filesystem_watcher.py: POLL_INTERVAL
# gmail_watcher.py: CHECK_INTERVAL (default: 120s)
# whatsapp_watcher.py: CHECK_INTERVAL (default: 300s)
# xero_watcher.py: check_interval (default: 300s)
```

### OAuth Issues

**Gmail:**
```bash
# Delete token and re-authorize
rm watchers/credentials/token.pickle
python watchers/gmail_watcher.py
```

**Xero:**
```bash
# Delete token and re-authorize
rm watchers/credentials/xero_token.json
python watchers/xero_watcher.py
```

---

## Best Practices

### 1. Monitor Regularly

Set up daily check:
```bash
# Add to daily routine
echo "0 9 * * * cd /path/to/vault && ls Needs_Action/ | wc -l" | crontab -
```

### 2. Rotate Logs

```bash
# Weekly log cleanup (keep last 7 days)
find Logs/ -name "*watcher*.log" -mtime +7 -delete
```

### 3. Backup Configuration

```bash
# Backup credentials and config
tar -czf watcher_config_backup.tar.gz \
  watchers/credentials/ \
  watchers/*_config.json
```

### 4. Test After Updates

```bash
# After updating watcher code
python watchers/test_watchers.py
```

### 5. Monitor Disk Space

```bash
# Check vault size
du -sh AI_Employee_Vault/

# Clean old completed tasks (optional)
find Done/ -name "*.md" -mtime +30 -delete
```

---

## Integration Workflow

When all watchers are running:

```
[Filesystem] + [Gmail] + [WhatsApp] + [Xero]
                    ↓
        All create files in Needs_Action/
                    ↓
            Task Processor reads files
                    ↓
            Plans generated
                    ↓
        Approval workflow (if needed)
                    ↓
            Actions executed
                    ↓
        Files moved to Done/
                    ↓
        Dashboard updated
```

---

## Performance Tips

### Adjust Check Intervals

Balance responsiveness vs. resource usage:

**High Activity (Fast):**
- Gmail: 1 minute
- WhatsApp: 2 minutes
- Xero: 2 minutes

**Normal Activity (Default):**
- Gmail: 2 minutes
- WhatsApp: 5 minutes
- Xero: 5 minutes

**Low Activity (Slow):**
- Gmail: 5 minutes
- WhatsApp: 10 minutes
- Xero: 15 minutes

Edit check intervals in watcher files:
```python
# gmail_watcher.py
CHECK_INTERVAL = 120  # seconds

# whatsapp_watcher.py
CHECK_INTERVAL = 300  # seconds

# xero_watcher.py
check_interval = 300  # seconds
```

### Optimize Queries

**Gmail:** Use filters to reduce email volume
**WhatsApp:** Monitor specific chats only
**Xero:** Adjust thresholds in xero_config.json

---

## Security Checklist

- [ ] All OAuth credentials stored securely
- [ ] credentials/ directory in .gitignore
- [ ] File permissions restricted (600 on Linux/Mac)
- [ ] Logs directory not publicly accessible
- [ ] Regular credential rotation (every 6 months)
- [ ] Audit logs reviewed weekly
- [ ] No credentials in environment variables
- [ ] Scheduled tasks run under dedicated service account

---

## Quick Reference Card

```
START ALL:        python watchers/run_all.py
STOP ALL:         Ctrl+C (if running in terminal)
                  OR: pkill -f watcher.py (Linux/Mac)

CHECK LOGS:       tail -f Logs/*watcher*.log
VIEW PENDING:     ls Needs_Action/
VIEW COMPLETED:   ls Done/
VIEW DASHBOARD:   cat AI_Employee_Vault/Dashboard.md

TEST WATCHERS:    python watchers/test_watchers.py
RESTART WATCHER:  schtasks /run /tn "AI_Employee_Gmail"
```

---

## Support

If issues persist:

1. Check individual watcher documentation:
   - `GMAIL_SETUP.md`
   - `WHATSAPP_SETUP.md`
   - `XERO_SETUP.md`

2. Review logs for errors:
   ```bash
   grep -i error Logs/*watcher*.log
   ```

3. Test watchers individually before running together

4. Verify all prerequisites installed

---

**All Watchers Ready!** 🎉

Your AI Employee is now monitoring 5 input sources 24/7:
- 📁 Files (Real-time)
- 📧 Email (Every 2 min)
- 💬 WhatsApp (Every 5 min)
- 💰 Accounting (Every 5 min)
- 💼 Slack (Every 1 min)
