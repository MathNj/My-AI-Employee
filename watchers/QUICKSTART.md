# Watcher System - Quick Start Guide

Get your watchers running in 10 minutes.

## Prerequisites Check

```bash
# Check Python version (need 3.10+)
python --version

# Check pip
pip --version
```

---

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)

```bash
cd watchers
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Configure Environment (1 min)

```bash
# Copy config template
copy .env.example .env

# Edit with your vault path
notepad .env
```

Set `VAULT_PATH` to your actual vault location:

```
VAULT_PATH=C:\Users\YourName\Desktop\My Vault
```

### Step 3: Test Filesystem Watcher (2 min)

```bash
# Start the watcher
python filesystem_watcher.py
```

In another terminal:

```bash
# Test it
echo "Test" > ..\Inbox\test.txt

# Check output
dir ..\Needs_Action
```

You should see a new task file! Press `Ctrl+C` to stop.

✅ **Filesystem watcher is working!**

---

## Gmail Setup (5 min)

### Step 1: Get Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API
3. Create OAuth credentials (Desktop app)
4. Download `credentials.json`

### Step 2: Place Credentials

```bash
mkdir credentials
move C:\Downloads\credentials.json credentials\credentials.json
```

### Step 3: Authenticate

```bash
python gmail_watcher.py
```

- Browser opens
- Grant permissions
- Done! Token saved for future runs

✅ **Gmail watcher is working!**

---

## WhatsApp Setup (Optional - 5 min)

### Step 1: Install

```bash
pip install playwright
playwright install chromium
```

### Step 2: Authenticate

```bash
python whatsapp_watcher.py --visible
```

- Browser opens to WhatsApp Web
- Scan QR code with phone
- Session saved

### Step 3: Switch to Headless

```bash
# Edit .env
WHATSAPP_HEADLESS=true

# Run headless
python whatsapp_watcher.py
```

✅ **WhatsApp watcher is working!**

---

## Running as Daemons (PM2)

### Install PM2

```bash
npm install -g pm2
```

### Start All Watchers

```bash
pm2 start ecosystem.config.js
```

### Check Status

```bash
pm2 status
```

### View Logs

```bash
pm2 logs
```

### Start on Boot

```bash
pm2 save
pm2 startup
```

✅ **All watchers running 24/7!**

---

## Verification

Check that everything is working:

```bash
# 1. Check PM2 status
pm2 status

# 2. Check logs for errors
pm2 logs --lines 20

# 3. Test file detection
echo "Test" > ..\Inbox\test2.txt

# 4. Check task was created
dir ..\Needs_Action

# 5. View action logs
type ..\Logs\actions_*.json
```

---

## Common Issues

### Python not found

```bash
# Windows: Add Python to PATH
# Or use full path
C:\Python310\python.exe gmail_watcher.py
```

### PM2 not found

```bash
# Install Node.js first
# Then: npm install -g pm2
```

### Gmail 403 error

```bash
# Enable Gmail API in Google Cloud Console
```

### WhatsApp QR timeout

```bash
# Run in visible mode and scan quickly
python whatsapp_watcher.py --visible
```

---

## Next Steps

1. ✅ Watchers running
2. → Process tasks with Claude Code
3. → Set up approval workflow
4. → Configure dashboard updates

See `COMPREHENSIVE_README.md` for detailed documentation.

---

## Quick Reference

```bash
# Start all
pm2 start ecosystem.config.js

# Stop all
pm2 stop all

# Restart all
pm2 restart all

# View logs
pm2 logs

# Monitor
pm2 monit

# Status
pm2 status
```

---

**Need Help?**

- Check `COMPREHENSIVE_README.md` for detailed docs
- Check `GMAIL_SETUP.md` for Gmail API setup
- Check `Logs/` folder for error details

---

*Part of Personal AI Employee Project*
*Setup time: ~10 minutes*
