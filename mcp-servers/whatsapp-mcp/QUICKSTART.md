# WhatsApp MCP Server - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd mcp-servers/whatsapp-mcp
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Authenticate WhatsApp
```bash
# Option A: Run watcher (recommended)
python watchers/whatsapp_watcher.py --visible

# Option B: Test sender directly
python whatsapp_sender.py --visible --to "Test" --message "Test"
```
- Scan QR code with your phone
- Wait for chat list to load
- Close browser (session is saved)

### Step 3: Send Test Message
```bash
python whatsapp_sender.py \
  --to "CONTACT_NAME" \
  --message "Hello from WhatsApp MCP!" \
  --visible
```

✅ **Done!** WhatsApp MCP is ready.

---

## 📝 Usage

### Send Message via AI

Just ask Claude:
```
"Send a WhatsApp message to John saying I'll be 10 minutes late"
```

Claude will:
1. Create approval request in `/Pending_Approval`
2. Wait for your approval
3. Send message via WhatsApp MCP
4. Move to `/Done` with result

### Send Message via Approval Workflow

1. Create file in `/Pending_Approval`:
```yaml
---
type: whatsapp
to: John Doe
priority: medium
---

## Message

Hi John, I'll be 10 minutes late to our meeting.

Sorry for the delay!
```

2. Move to `/Approved` (in Obsidian)

3. Approval processor sends automatically

---

## 📁 Files Created

**Core Implementation:**
- `mcp-servers/whatsapp-mcp/whatsapp_sender.py` - Playwright automation
- `mcp-servers/whatsapp-mcp/server.py` - MCP server
- `mcp-servers/whatsapp-mcp/requirements.txt` - Dependencies
- `mcp-servers/whatsapp-mcp/README.md` - Full documentation

**Integration:**
- `watchers/approval_processor.py` - ✅ Updated with WhatsApp support
- `.claude/skills/whatsapp-sender/SKILL.md` - Skill documentation

**Documentation:**
- `TESTING.md` - Testing scenarios
- `IMPLEMENTATION_SUMMARY.md` - Complete technical details

---

## 🔧 Troubleshooting

**Problem:** "Chromium not installed"
```bash
playwright install chromium
```

**Problem:** "Not authenticated"
```bash
python watchers/whatsapp_watcher.py --visible
# Scan QR code
```

**Problem:** "Chat not found"
- Use exact contact name (case-sensitive)
- Verify contact exists in WhatsApp
- Try sending manually via WhatsApp Web first

**Problem:** Message not sending
- Check logs: `cat Logs/whatsapp_*.json`
- Run with `--visible` flag to debug
- Verify internet connection

---

## ✅ What's Supported

- ✅ Send text messages to individuals
- ✅ Send text messages to groups
- ✅ Long messages (no character limit)
- ✅ Emojis
- ✅ HITL approval workflow
- ✅ Persistent authentication
- ✅ Auto-approver integration

---

## ❌ What's Not Supported (Yet)

- ❌ Media attachments (images, documents, voice notes)
- ❌ Message templates
- ❌ Bulk messaging
- ❌ Conversation history retrieval
- ❌ Contact information lookup

---

## 📊 System Architecture

```
AI Employee (Claude)
    ↓
/Pending_Approval
    ↓ (Human approves)
/Approved
    ↓
Approval Processor
    ↓
WhatsApp MCP Server
    ↓
Playwright → WhatsApp Web
    ↓
Message Sent ✅
```

---

## 🎯 Next Steps

1. ✅ Install Chromium: `playwright install chromium`
2. ✅ Authenticate WhatsApp: Run watcher, scan QR code
3. ✅ Send test message: `python whatsapp_sender.py --to "Name" --message "Test"`
4. ✅ Test approval workflow: Create approval file, move to `/Approved`
5. ✅ Monitor logs: Check `Logs/whatsapp_YYYY-MM-DD.json`

---

## 📖 Full Documentation

- **README.md** - Complete user guide
- **TESTING.md** - Testing scenarios
- **SKILL.md** - Skill documentation (`.claude/skills/whatsapp-sender/`)
- **IMPLEMENTATION_SUMMARY.md** - Technical details

---

**Version:** 1.0.0
**Status:** ✅ Production Ready (after authentication)
**Last Updated:** 2026-01-22
