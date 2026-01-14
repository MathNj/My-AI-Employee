# Watcher System - Troubleshooting Guide

Complete troubleshooting reference for all watcher issues.

## Table of Contents

- [General Issues](#general-issues)
- [Gmail Watcher](#gmail-watcher-issues)
- [Filesystem Watcher](#filesystem-watcher-issues)
- [WhatsApp Watcher](#whatsapp-watcher-issues)
- [PM2 Daemon Issues](#pm2-daemon-issues)
- [Performance Problems](#performance-problems)
- [Error Messages](#common-error-messages)

---

## General Issues

### Python Not Found

**Symptom:** `'python' is not recognized as an internal or external command`

**Solutions:**

```bash
# Solution 1: Add Python to PATH
# Windows: System Properties → Environment Variables → Add Python path

# Solution 2: Use full path
C:\Python310\python.exe gmail_watcher.py

# Solution 3: Use py launcher (Windows)
py gmail_watcher.py

# Solution 4: Reinstall Python with "Add to PATH" checked
```

### Pip Not Working

**Symptom:** `'pip' is not recognized`

**Solutions:**

```bash
# Solution 1: Use python -m pip
python -m pip install -r requirements.txt

# Solution 2: Upgrade pip
python -m pip install --upgrade pip

# Solution 3: Check Python installation
python -c "import sys; print(sys.executable)"
```

### Module Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'watchdog'`

**Solutions:**

```bash
# Solution 1: Install dependencies
pip install -r requirements.txt

# Solution 2: Check which Python is running
where python
pip show watchdog

# Solution 3: Use virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Path Issues

**Symptom:** `Vault path does not exist: ...`

**Solutions:**

```bash
# Solution 1: Use absolute paths
VAULT_PATH=C:\Users\YourName\Desktop\My Vault

# Solution 2: Check path exists
dir "C:\Users\YourName\Desktop\My Vault"

# Solution 3: Escape spaces in paths
cd "C:\Users\YourName\Desktop\My Vault\watchers"
```

---

## Gmail Watcher Issues

### Credentials Not Found

**Symptom:** `Credentials file not found: credentials.json`

**Solutions:**

```bash
# Solution 1: Check file exists
dir watchers\credentials\credentials.json

# Solution 2: Download from Google Cloud Console
# - Go to console.cloud.google.com
# - APIs & Services → Credentials
# - Download OAuth 2.0 credentials

# Solution 3: Check .env path
notepad .env
# Verify GMAIL_CREDENTIALS_PATH is correct
```

### OAuth Flow Fails

**Symptom:** `OAuth2 flow failed: Connection refused`

**Solutions:**

```bash
# Solution 1: Check firewall isn't blocking port
# Allow Python in Windows Firewall

# Solution 2: Use different port
# Edit gmail_watcher.py: flow.run_local_server(port=8080)

# Solution 3: Run as administrator
```

### Gmail API 403 Forbidden

**Symptom:** `HttpError 403: Gmail API has not been enabled`

**Solutions:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. APIs & Services → Library
4. Search "Gmail API"
5. Click Enable

### Token Expired

**Symptom:** `Error refreshing credentials: Token expired`

**Solutions:**

```bash
# Solution 1: Delete token and re-authenticate
del credentials\token.pickle
python gmail_watcher.py

# Solution 2: Generate new credentials
# Re-download credentials.json from Google Cloud Console

# Solution 3: Check OAuth consent screen is published (not testing)
```

### No Emails Detected

**Symptom:** Watcher running but no task files created

**Debug Steps:**

```bash
# 1. Check Gmail query
# Open Gmail and test query manually: is:unread is:important

# 2. Check processed IDs cache
type ..\Logs\gmailwatcher_processed.json

# 3. Clear cache to reprocess
del ..\Logs\gmailwatcher_processed.json

# 4. Check watcher logs
type ..\Logs\gmail_watcher_*.log
```

### Rate Limiting

**Symptom:** `HttpError 429: Rate limit exceeded`

**Solutions:**

```bash
# Solution 1: Increase check interval
# Edit .env: GMAIL_CHECK_INTERVAL=300  # 5 minutes

# Solution 2: Check quota in Google Cloud Console
# APIs & Services → Dashboard → Gmail API

# Solution 3: Wait and retry
# Rate limits reset after 100 seconds
```

---

## Filesystem Watcher Issues

### Watchdog Not Installed

**Symptom:** `ModuleNotFoundError: No module named 'watchdog'`

**Solutions:**

```bash
# Solution 1: Install watchdog
pip install watchdog

# Solution 2: Install all requirements
pip install -r requirements.txt

# Solution 3: Check installation
pip show watchdog
python -c "import watchdog; print(watchdog.__version__)"
```

### Not Detecting Files

**Symptom:** Files added to Inbox but no tasks created

**Debug Steps:**

```bash
# 1. Verify watcher is running
# Look for "Watcher started successfully" message

# 2. Check Inbox path
dir ..\Inbox

# 3. Test with visible file
echo "Test content" > ..\Inbox\visible_test.txt

# 4. Check logs for errors
type ..\Logs\watcher_*.log

# 5. Verify Needs_Action folder exists
dir ..\Needs_Action
```

**Solutions:**

```bash
# Solution 1: Restart watcher
# Press Ctrl+C and restart

# Solution 2: Check file isn't hidden/temporary
# Watcher skips files starting with . or ~

# Solution 3: Wait for file to finish writing
# Watcher waits 0.5s before processing

# Solution 4: Check permissions
# Ensure Python can read Inbox folder
```

### Permission Errors

**Symptom:** `PermissionError: [Errno 13] Permission denied`

**Solutions:**

```bash
# Solution 1: Run as administrator (Windows)
# Right-click → Run as administrator

# Solution 2: Check folder permissions
# Properties → Security → Ensure user has Full Control

# Solution 3: Move vault to user directory
# Avoid C:\Program Files or system folders
```

### Duplicate Tasks Created

**Symptom:** Same file creates multiple tasks

**Solutions:**

```bash
# Solution 1: Check for file moves/copies
# Watcher detects both operations

# Solution 2: Clear processed cache if needed
del ..\Logs\filesystemwatcher_processed.json

# Solution 3: Don't modify files in Inbox after detection
```

---

## WhatsApp Watcher Issues

### Playwright Not Installed

**Symptom:** `ModuleNotFoundError: No module named 'playwright'`

**Solutions:**

```bash
# Solution 1: Install Playwright
pip install playwright

# Solution 2: Install browser binaries
playwright install chromium

# Solution 3: Verify installation
playwright --version
```

### Browser Install Failed

**Symptom:** `Failed to install browsers`

**Solutions:**

```bash
# Solution 1: Install with specific browser
playwright install chromium

# Solution 2: Check disk space
# Browsers need ~300MB

# Solution 3: Use different download location
set PLAYWRIGHT_BROWSERS_PATH=C:\playwright_browsers
playwright install chromium

# Solution 4: Manual download
# Check https://playwright.dev/python/docs/browsers
```

### QR Code Timeout

**Symptom:** `TimeoutError: waiting for selector failed`

**Solutions:**

```bash
# Solution 1: Run in visible mode
python whatsapp_watcher.py --visible

# Solution 2: Increase timeout in code
# Edit whatsapp_watcher.py:
# page.wait_for_selector('[data-testid="chat-list"]', timeout=180000)

# Solution 3: Scan QR code faster
# Have phone ready before starting watcher
```

### Session Lost

**Symptom:** Asks for QR code every time

**Solutions:**

```bash
# Solution 1: Check session path
dir whatsapp_session

# Solution 2: Don't delete session folder
# Keep whatsapp_session/ folder intact

# Solution 3: Run in non-headless mode first
python whatsapp_watcher.py --visible
# Then switch to headless after authenticated
```

### No Messages Detected

**Symptom:** Watcher running but no tasks created

**Debug Steps:**

```bash
# 1. Check keywords match
# Edit .env: WHATSAPP_KEYWORDS=urgent,test

# 2. Send test message with keyword
# Send "urgent test" to yourself on WhatsApp

# 3. Check logs
type ..\Logs\whatsappwatcher_*.log

# 4. Verify WhatsApp Web is loaded
# Run in visible mode to see browser
python whatsapp_watcher.py --visible

# 5. Check processed cache
type ..\Logs\whatsappwatcher_processed.json
```

**Solutions:**

```bash
# Solution 1: Add more keywords
# Edit .env: WHATSAPP_KEYWORDS=urgent,asap,invoice,test

# Solution 2: Clear processed cache
del ..\Logs\whatsappwatcher_processed.json

# Solution 3: Check message is unread
# Watcher only detects unread messages
```

### Browser Crashes

**Symptom:** Browser closes unexpectedly

**Solutions:**

```bash
# Solution 1: Increase memory limit
# Edit ecosystem.config.js: max_memory_restart: '1G'

# Solution 2: Clear session and restart
rmdir /s whatsapp_session
python whatsapp_watcher.py --visible

# Solution 3: Disable headless mode
# Edit .env: WHATSAPP_HEADLESS=false

# Solution 4: Update Playwright
pip install --upgrade playwright
playwright install chromium
```

---

## PM2 Daemon Issues

### PM2 Not Found

**Symptom:** `'pm2' is not recognized`

**Solutions:**

```bash
# Solution 1: Install PM2
npm install -g pm2

# Solution 2: Check Node.js is installed
node --version
npm --version

# Solution 3: Use full path
C:\Users\YourName\AppData\Roaming\npm\pm2 status

# Solution 4: Add npm to PATH
# System Properties → Environment Variables → Add npm path
```

### Watcher Won't Start

**Symptom:** `pm2 start` fails or shows error

**Debug Steps:**

```bash
# 1. Check PM2 logs
pm2 logs

# 2. Try running manually first
python gmail_watcher.py

# 3. Check ecosystem.config.js syntax
# Ensure valid JavaScript

# 4. Verify Python interpreter path
pm2 info gmail-watcher
```

**Solutions:**

```bash
# Solution 1: Update interpreter path
# Edit ecosystem.config.js:
# interpreter: 'C:\\Python310\\python.exe'

# Solution 2: Delete and recreate
pm2 delete all
pm2 start ecosystem.config.js

# Solution 3: Check working directory
# Ensure cwd in ecosystem.config.js is correct
```

### Logs Not Appearing

**Symptom:** `pm2 logs` shows nothing

**Solutions:**

```bash
# Solution 1: Check log file paths
pm2 info gmail-watcher
# Look at out_file and error_file paths

# Solution 2: Manually check log files
type ..\Logs\pm2-gmail-out.log

# Solution 3: Flush and restart
pm2 flush
pm2 restart all

# Solution 4: Enable console output
# Add to ecosystem.config.js: log_type: 'json'
```

### Auto-restart Loop

**Symptom:** Process keeps restarting repeatedly

**Debug Steps:**

```bash
# 1. Check error logs
pm2 logs gmail-watcher --err

# 2. Check restart count
pm2 info gmail-watcher

# 3. Disable auto-restart temporarily
pm2 stop gmail-watcher
python gmail_watcher.py  # Run manually to see error
```

**Solutions:**

```bash
# Solution 1: Fix underlying error
# Check logs for the root cause

# Solution 2: Increase min_uptime
# Edit ecosystem.config.js: min_uptime: '30s'

# Solution 3: Increase restart delay
# Edit ecosystem.config.js: restart_delay: 10000

# Solution 4: Stop and debug
pm2 stop gmail-watcher
python gmail_watcher.py  # Debug manually
```

### Startup Script Not Working

**Symptom:** Watchers don't start on boot

**Solutions:**

```bash
# Solution 1: Run startup command with correct platform
pm2 startup

# Solution 2: Save process list
pm2 save

# Solution 3: Test startup script
# Restart computer and check

# Solution 4: Manual startup (Windows Task Scheduler)
# Create task to run: pm2 resurrect
```

---

## Performance Problems

### High CPU Usage

**Symptom:** Python process using lots of CPU

**Debug Steps:**

```bash
# 1. Check which watcher is causing it
pm2 monit

# 2. Check logs for errors/loops
pm2 logs

# 3. Monitor system resources
# Task Manager → Performance
```

**Solutions:**

```bash
# Solution 1: Increase check intervals
# Edit .env:
# GMAIL_CHECK_INTERVAL=300
# WHATSAPP_CHECK_INTERVAL=60

# Solution 2: Restart watcher
pm2 restart all

# Solution 3: Check for infinite loops in logs
# Look for rapid repeated messages

# Solution 4: Reduce browser instances (WhatsApp)
# Stop WhatsApp watcher if not needed
pm2 stop whatsapp-watcher
```

### High Memory Usage

**Symptom:** Process using excessive RAM

**Solutions:**

```bash
# Solution 1: Set memory limits in PM2
# Edit ecosystem.config.js:
# max_memory_restart: '200M'

# Solution 2: Clear processed items cache
# Limits grow over time
del ..\Logs\*_processed.json

# Solution 3: Restart watchers daily
pm2 restart all

# Solution 4: Close browser when not needed (WhatsApp)
# WhatsApp watcher uses most memory due to browser
```

### Slow Response

**Symptom:** Tasks take long time to appear

**Solutions:**

```bash
# Solution 1: Decrease check intervals
# Edit .env:
# GMAIL_CHECK_INTERVAL=60  # Check every 1 minute

# Solution 2: Check system load
# Ensure system isn't overloaded

# Solution 3: Use SSD for vault
# Faster disk I/O

# Solution 4: Check network latency
# API calls depend on internet speed
```

---

## Common Error Messages

### `Vault path does not exist`

**Cause:** Incorrect VAULT_PATH in .env

**Fix:**

```bash
# Edit .env with correct absolute path
notepad .env
# VAULT_PATH=C:\Users\YourName\Desktop\My Vault
```

### `credentials.json not found`

**Cause:** Gmail credentials missing

**Fix:**

```bash
# Download from Google Cloud Console
# Place in: watchers\credentials\credentials.json
```

### `Token expired or invalid`

**Cause:** Gmail OAuth token expired

**Fix:**

```bash
del credentials\token.pickle
python gmail_watcher.py
```

### `Rate limit exceeded`

**Cause:** Too many API requests

**Fix:**

```bash
# Increase check interval
# Edit .env: GMAIL_CHECK_INTERVAL=300
```

### `Permission denied`

**Cause:** Insufficient file permissions

**Fix:**

```bash
# Run as administrator (Windows)
# Or check folder permissions
```

### `Port already in use`

**Cause:** OAuth server port conflict

**Fix:**

```bash
# Change port in gmail_watcher.py
# flow.run_local_server(port=8080)
```

### `Playwright browser not found`

**Cause:** Browser binaries not installed

**Fix:**

```bash
playwright install chromium
```

### `TimeoutError: waiting for selector`

**Cause:** WhatsApp Web not loading or QR code timeout

**Fix:**

```bash
# Increase timeout or run in visible mode
python whatsapp_watcher.py --visible
```

---

## Getting Help

If you're still stuck after trying these solutions:

### 1. Check Logs

```bash
# Watcher logs
type ..\Logs\gmail_watcher_*.log
type ..\Logs\watcher_*.log
type ..\Logs\whatsappwatcher_*.log

# PM2 logs
pm2 logs --lines 50

# Action logs
type ..\Logs\actions_*.json
```

### 2. Run in Debug Mode

```bash
# Edit watcher code to enable DEBUG logging
# Change: logging.INFO to logging.DEBUG
```

### 3. Test Components

```bash
# Test Python
python --version

# Test imports
python -c "import watchdog, playwright; print('OK')"

# Test Gmail API
python -c "from googleapiclient.discovery import build; print('OK')"

# Test Playwright
playwright --version
```

### 4. Check System

```bash
# Disk space
dir C:\

# Memory
# Task Manager → Performance

# Python path
where python

# Environment variables
echo %PATH%
```

---

## Prevention Tips

### Keep Dependencies Updated

```bash
# Update packages monthly
pip install --upgrade -r requirements.txt
playwright install chromium
npm update -g pm2
```

### Monitor Logs Regularly

```bash
# Check logs weekly
pm2 logs --lines 100

# Clear old logs
pm2 flush
```

### Backup Configuration

```bash
# Backup credentials (excluding sensitive files)
copy ecosystem.config.js ecosystem.config.js.backup
copy .env .env.backup  # DO NOT commit this

# Backup to version control (exclude sensitive files)
git add .gitignore
git commit -m "Update watcher config"
```

### Test After Changes

```bash
# Always test manually before running as daemon
python gmail_watcher.py  # Test for 1-2 minutes
# Press Ctrl+C if working

# Then start with PM2
pm2 start ecosystem.config.js
```

---

## Emergency Recovery

If everything is broken:

### Nuclear Option - Fresh Start

```bash
# 1. Stop all processes
pm2 delete all

# 2. Backup important files
copy credentials\credentials.json credentials.json.backup
copy .env .env.backup

# 3. Clear cache
del ..\Logs\*_processed.json

# 4. Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
playwright install chromium

# 5. Test each watcher individually
python gmail_watcher.py  # Press Ctrl+C after testing
python filesystem_watcher.py
python whatsapp_watcher.py

# 6. Restart with PM2
pm2 start ecosystem.config.js
```

---

## Still Need Help?

- Check `COMPREHENSIVE_README.md` for detailed documentation
- Check `Requirements.md` for architecture overview
- Check GitHub issues or community forums
- Review code comments in watcher scripts

---

*Last Updated: 2026-01-12*
*Part of Personal AI Employee Project*
