# Personal AI Employee - Watcher System

Complete documentation for the watcher system that monitors external sources and creates actionable task files for your AI Employee.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Watcher Types](#watcher-types)
  - [Gmail Watcher](#gmail-watcher)
  - [Filesystem Watcher](#filesystem-watcher)
  - [WhatsApp Watcher](#whatsapp-watcher)
- [Configuration](#configuration)
- [Running Watchers](#running-watchers)
- [Running as Daemons (PM2)](#running-as-daemons-pm2)
- [Task File Format](#task-file-format)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## Overview

Watchers are Python sentinel scripts that continuously monitor external sources (Gmail, WhatsApp, File System) and create task files in the `Needs_Action` folder for Claude Code to process.

### Key Features

✅ **Automatic Detection** - Real-time monitoring of external sources
✅ **Smart Filtering** - Keyword-based priority detection
✅ **Persistent Tracking** - Avoids duplicate processing
✅ **Comprehensive Logging** - Full audit trail of all detections
✅ **Error Recovery** - Automatic retry with exponential backoff
✅ **Production Ready** - PM2 daemon support for 24/7 operation

### How It Works

```
External Source → Watcher Script → Task File → Claude Code → Action
    (Gmail)          (Python)      (Markdown)     (AI)        (Result)
```

---

## Architecture

All watchers inherit from the `BaseWatcher` abstract class:

```python
BaseWatcher (base_watcher.py)
├── GmailWatcher (gmail_watcher.py)
├── FilesystemWatcher (filesystem_watcher.py)
└── WhatsAppWatcher (whatsapp_watcher.py)
```

### BaseWatcher Features

- Abstract methods: `check_for_updates()`, `create_action_file()`
- Common functionality: logging, folder creation, run loop
- Configurable check intervals
- Exception handling with graceful recovery
- Processed items tracking
- Statistics and monitoring

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (for version control)

### Step 1: Install Python Dependencies

```bash
# Navigate to watchers directory
cd "C:\Users\YourName\Desktop\My Vault\watchers"

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Install Playwright Browsers (for WhatsApp)

```bash
# Install Playwright browsers (required for WhatsApp watcher)
playwright install chromium
```

### Step 3: Configure Environment

```bash
# Copy the example configuration
copy .env.example .env

# Edit .env with your settings (use notepad or any text editor)
notepad .env
```

### Step 4: Verify Installation

```bash
# Test Python imports
python -c "import watchdog, playwright; print('✓ All dependencies installed')"
```

---

## Watcher Types

### Gmail Watcher

Monitors Gmail for important unread emails using the Gmail API.

#### Features

- OAuth 2.0 authentication (secure, no password storage)
- Monitors: `is:unread is:important`
- Automatic priority detection based on keywords
- Full email metadata extraction
- Direct Gmail link generation

#### Setup Instructions

1. **Enable Gmail API**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json`

2. **Place Credentials**

   ```bash
   # Create credentials directory
   mkdir credentials

   # Place your credentials.json file here
   move C:\Downloads\credentials.json watchers\credentials\credentials.json
   ```

3. **First Run Authentication**

   ```bash
   python gmail_watcher.py
   ```

   - Browser will open for OAuth consent
   - Grant permissions
   - Token will be saved for future runs

4. **Verify Setup**
   ```bash
   # Check for token file
   dir credentials\token.pickle
   ```

#### Configuration

Edit `.env`:

```bash
GMAIL_CREDENTIALS_PATH=C:\Users\YourName\Desktop\My Vault\watchers\credentials\credentials.json
GMAIL_CHECK_INTERVAL=120  # Check every 2 minutes
GMAIL_QUERY=is:unread is:important
```

#### Output Example

Task files created: `EMAIL_{message_id}.md`

```yaml
---
type: email
from: client@example.com
subject: Urgent: Invoice Payment Due
priority: high
status: pending
---

# New Email: Urgent: Invoice Payment Due

## Email Information
- **From:** client@example.com
- **Subject:** Urgent: Invoice Payment Due
- **Date:** 2026-01-12T10:30:00

## Suggested Actions
- [ ] Reply to sender
- [ ] Process payment
```

---

### Filesystem Watcher

Monitors the `Inbox` folder for new files using the watchdog library.

#### Features

- Real-time file detection (event-driven, not polling)
- Instant task creation
- Automatic file size formatting
- File type detection
- Priority based on filename keywords

#### Setup Instructions

1. **Ensure Inbox Folder Exists**

   ```bash
   # The watcher creates it automatically, but you can verify
   cd "C:\Users\YourName\Desktop\My Vault"
   mkdir Inbox
   ```

2. **Start the Watcher**

   ```bash
   python filesystem_watcher.py
   ```

3. **Test It**
   ```bash
   # In another terminal/window
   echo "Test file" > Inbox\test.txt
   # Check Needs_Action for new task file
   ```

#### Configuration

No special configuration needed. Edit check behavior in `filesystem_watcher.py` if needed.

#### Output Example

Task files created: `FILE_{timestamp}_{filename}.md`

```yaml
---
type: file_drop
source_file: invoice.pdf
size_bytes: 102400
priority: medium
status: pending
---

# New File Detected: invoice.pdf

## File Information
- **Size:** 100.0 KB
- **Type:** .pdf
```

---

### WhatsApp Watcher

Monitors WhatsApp Web for messages containing urgent keywords using Playwright.

#### Features

- Browser automation (Playwright)
- Persistent login session
- Keyword-based filtering
- Screenshot capture
- Group and individual chat support
- Unread message detection

#### Setup Instructions

1. **Install Playwright**

   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Configure Keywords**

   Edit `.env`:

   ```bash
   WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,emergency
   WHATSAPP_HEADLESS=false  # Set to false for first run
   ```

3. **First Run - Authenticate**

   ```bash
   python whatsapp_watcher.py --visible
   ```

   - Browser opens to WhatsApp Web
   - Scan QR code with your phone
   - Session is saved for future runs

4. **Switch to Headless Mode**

   After authentication:

   ```bash
   # Edit .env
   WHATSAPP_HEADLESS=true

   # Or run with flag
   python whatsapp_watcher.py  # Headless by default
   ```

#### Configuration

Edit `.env`:

```bash
WHATSAPP_SESSION_PATH=C:\Users\YourName\Desktop\My Vault\watchers\whatsapp_session
WHATSAPP_CHECK_INTERVAL=30  # Check every 30 seconds
WHATSAPP_KEYWORDS=urgent,asap,emergency,invoice,payment
```

#### Output Example

Task files created: `WHATSAPP_{chat_name}_{timestamp}.md`

```yaml
---
type: whatsapp
chat_name: Client A
priority: high
matched_keywords: urgent, invoice
---

# WhatsApp Message: Client A

## Message Preview
Need invoice URGENT for payment today

## Screenshots
![Screenshot](screenshot_2026-01-12.png)
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Vault path (absolute)
VAULT_PATH=C:\Users\YourName\Desktop\My Vault

# Gmail settings
GMAIL_CREDENTIALS_PATH=C:\Path\To\credentials.json
GMAIL_CHECK_INTERVAL=120

# WhatsApp settings
WHATSAPP_KEYWORDS=urgent,asap,invoice
WHATSAPP_HEADLESS=true

# Logging
LOG_LEVEL=INFO
```

### Per-Watcher Configuration

Each watcher can be configured with:

- **Check Interval** - How often to check for updates
- **Keywords** - Terms to trigger high priority
- **Credentials** - API keys and OAuth tokens
- **Session Data** - Persistent login state

---

## Running Watchers

### Option 1: Run in Terminal (Foreground)

```bash
# Start individual watchers
python gmail_watcher.py
python filesystem_watcher.py
python whatsapp_watcher.py
```

**Pros:** Easy to debug, see logs in real-time
**Cons:** Stops when terminal closes

### Option 2: Run in Background (Windows)

```bash
# Start in background
start pythonw gmail_watcher.py
start pythonw filesystem_watcher.py
start pythonw whatsapp_watcher.py

# Stop (find PID and kill)
tasklist | findstr python
taskkill /PID <pid> /F
```

### Option 3: Run in Background (Linux/Mac)

```bash
# Start in background
nohup python gmail_watcher.py &
nohup python filesystem_watcher.py &
nohup python whatsapp_watcher.py &

# Stop
ps aux | grep watcher
kill <pid>
```

### Option 4: Use PM2 (Recommended for Production)

See [Running as Daemons](#running-as-daemons-pm2) below.

---

## Running as Daemons (PM2)

**PM2** is a production-ready process manager that keeps watchers running 24/7.

### Why PM2?

✅ Auto-restart on crash
✅ Startup on system boot
✅ Log management with rotation
✅ Process monitoring (CPU, memory)
✅ Easy start/stop/restart
✅ Works with Python (not just Node.js)

### Installation

```bash
# Install Node.js first (if not installed)
# Download from: https://nodejs.org/

# Install PM2 globally
npm install -g pm2
```

### Starting Watchers

```bash
# Navigate to watchers directory
cd "C:\Users\YourName\Desktop\My Vault\watchers"

# Start all watchers
pm2 start ecosystem.config.js

# Start specific watcher
pm2 start ecosystem.config.js --only gmail-watcher
pm2 start ecosystem.config.js --only filesystem-watcher
pm2 start ecosystem.config.js --only whatsapp-watcher
```

### Managing Processes

```bash
# Check status
pm2 status

# View logs (live)
pm2 logs

# View specific watcher logs
pm2 logs gmail-watcher

# Stop all
pm2 stop all

# Stop specific
pm2 stop gmail-watcher

# Restart all
pm2 restart all

# Delete from PM2 (remove completely)
pm2 delete all
```

### Monitor Performance

```bash
# Real-time monitoring dashboard
pm2 monit

# Detailed info on specific watcher
pm2 info gmail-watcher

# Show all processes
pm2 list
```

### Configure Startup on Boot

```bash
# Generate startup script (run once)
pm2 startup

# Save current process list
pm2 save

# Now watchers will auto-start when system boots!
```

### Logs

PM2 logs are stored in:

```
../Logs/pm2-gmail-out.log
../Logs/pm2-gmail-error.log
../Logs/pm2-filesystem-out.log
../Logs/pm2-filesystem-error.log
../Logs/pm2-whatsapp-out.log
../Logs/pm2-whatsapp-error.log
```

View logs:

```bash
# All logs (live tail)
pm2 logs

# Last 100 lines
pm2 logs --lines 100

# Specific watcher
pm2 logs gmail-watcher

# Flush old logs
pm2 flush
```

---

## Task File Format

All task files follow this YAML frontmatter format:

```yaml
---
type: email|whatsapp|file_drop
from: sender_info
subject: subject_line
received: 2026-01-12T10:30:00Z
priority: high|medium|low
status: pending
---

# Task Title

## Information Section
Details about the detected item

## Suggested Actions
- [ ] Action 1
- [ ] Action 2

## Processing Notes
Notes added by AI or human
```

### Priority Levels

- **high** - Contains urgent keywords (urgent, asap, critical, payment)
- **medium** - Standard business communication
- **low** - Informational only

---

## Troubleshooting

### Gmail Watcher Issues

**Problem:** `credentials.json not found`

```bash
# Solution: Place credentials in correct location
move C:\Downloads\credentials.json watchers\credentials\credentials.json
```

**Problem:** `403 Forbidden` from Gmail API

```bash
# Solution: Enable Gmail API in Google Cloud Console
# Go to: console.cloud.google.com → APIs & Services → Enable APIs
```

**Problem:** Token expired

```bash
# Solution: Delete token and re-authenticate
del credentials\token.pickle
python gmail_watcher.py
```

### Filesystem Watcher Issues

**Problem:** Not detecting files

```bash
# Check watchdog is installed
pip show watchdog

# Verify Inbox folder exists
dir "C:\Users\YourName\Desktop\My Vault\Inbox"

# Check watcher is running
# Look for "Watcher started successfully" in logs
```

**Problem:** Permission errors

```bash
# Run as administrator (Windows)
# Or check folder permissions
```

### WhatsApp Watcher Issues

**Problem:** Playwright not installed

```bash
# Solution: Install Playwright
pip install playwright
playwright install chromium
```

**Problem:** QR code timeout

```bash
# Solution: Run in visible mode and scan quickly
python whatsapp_watcher.py --visible

# Or increase timeout in code
```

**Problem:** Browser crashes

```bash
# Solution: Clear session and re-authenticate
rmdir /s whatsapp_session
python whatsapp_watcher.py --visible
```

### PM2 Issues

**Problem:** PM2 command not found

```bash
# Solution: Install PM2 globally
npm install -g pm2

# Or use full path
C:\Users\YourName\AppData\Roaming\npm\pm2 status
```

**Problem:** Watcher not starting

```bash
# Check PM2 logs
pm2 logs

# Check Python path
pm2 info gmail-watcher

# Try running manually first
python gmail_watcher.py
```

---

## Security Best Practices

### Credentials Management

✅ **DO:**

- Store credentials in `credentials/` folder
- Add `credentials/` to `.gitignore`
- Use OAuth 2.0 for Gmail (not passwords)
- Rotate credentials every 90 days

❌ **DON'T:**

- Commit credentials to git
- Share credentials in chat/email
- Store passwords in plain text
- Use root/admin accounts

### Environment Variables

```bash
# Always use .env for sensitive data
GMAIL_CREDENTIALS_PATH=...  # Never hardcode in Python

# Add to .gitignore
echo ".env" >> ../.gitignore
echo "credentials/" >> ../.gitignore
echo "whatsapp_session/" >> ../.gitignore
```

### Logging Security

```bash
# Never log sensitive data
logger.info(f"Email from: {sender}")  # ✓ OK
logger.info(f"Password: {pwd}")       # ✗ NEVER!

# Review logs before sharing
# Redact email addresses and personal info
```

### Rate Limiting

Configure reasonable check intervals:

- Gmail: 120 seconds (2 minutes) - respects API quotas
- WhatsApp: 30 seconds - avoids detection as bot
- Filesystem: Instant (event-driven) - no rate limit needed

---

## Advanced Usage

### Custom Keywords

Edit watcher scripts to add custom keyword detection:

```python
# In gmail_watcher.py
HIGH_PRIORITY_KEYWORDS = [
    'urgent', 'asap', 'critical',
    'invoice', 'payment',
    # Add your custom keywords
    'client_name', 'project_deadline'
]
```

### Custom Queries

Gmail watcher can use any Gmail search query:

```python
# In .env
GMAIL_QUERY=from:important@client.com OR subject:invoice

# Or in code
query = 'is:unread label:important after:2026/01/01'
```

### Webhook Integration

Add webhook notifications when tasks are created:

```python
# In create_action_file()
import requests

def notify_webhook(task_file):
    requests.post('https://your-webhook.com/notify', json={
        'task': task_file.name,
        'timestamp': datetime.now().isoformat()
    })
```

---

## Performance Metrics

### Resource Usage

| Watcher    | CPU (Idle) | RAM   | Disk I/O |
| ---------- | ---------- | ----- | -------- |
| Gmail      | <1%        | ~30MB | Minimal  |
| Filesystem | <1%        | ~20MB | Minimal  |
| WhatsApp   | ~2-5%      | ~80MB | Moderate |

### Check Intervals

| Watcher    | Default | Recommended | Max Frequency |
| ---------- | ------- | ----------- | ------------- |
| Gmail      | 120s    | 60-300s     | 30s           |
| Filesystem | Instant | Instant     | Event-driven  |
| WhatsApp   | 30s     | 30-60s      | 10s           |

---

## Next Steps

After setting up watchers:

1. ✅ Install dependencies
2. ✅ Configure environment (.env)
3. ✅ Set up credentials (Gmail OAuth)
4. ✅ Test each watcher individually
5. ✅ Start watchers with PM2
6. ⏳ Process tasks with `task-processor` skill
7. ⏳ Set up approval workflow
8. ⏳ Configure dashboard updates

---

## Support & Documentation

- **Requirements:** See `Requirements.md` in vault root
- **Gmail Setup:** See `GMAIL_SETUP.md` in watchers folder
- **Architecture:** See "Watcher Architecture" in Requirements.md
- **Issues:** Check `Logs/` folder for error details

---

## License & Attribution

Part of the Personal AI Employee project.
Created for Panaversity Hackathon 2026.

**Contributors:**

- Base architecture from Requirements.md
- Implementation by AI Employee Project Team

---

*Last Updated: 2026-01-12*
*Version: 1.0.0*
*Status: Production Ready*
