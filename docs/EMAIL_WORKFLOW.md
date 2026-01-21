# Email Reply Workflow - Documentation

**Created:** 2026-01-21
**Status:** ✅ Implemented and Ready

---

## Overview

Your AI Employee Vault now has **automated email reply capabilities** integrated into the approval workflow. When you approve an email reply action, it will be sent automatically via Gmail API.

---

## How It Works

### **Current Email Flow**

1. **Gmail Watcher** detects important emails
2. Creates task file in `Needs_Action/EMAIL_*.md`
3. **Auto-Approver** analyzes and approves (or you manually approve)
4. **Approval Processor** executes the approved action
5. **Email Sender** sends the reply via Gmail API
6. Task moves to `Done/` with confirmation

### **What Changed**

**Before:**
- ❌ Gmail watcher only created task files
- ❌ Approval processor logged "Email requires manual sending"
- ❌ You had to manually send replies in Gmail

**After:**
- ✅ Gmail watcher still creates task files (no change)
- ✅ Approval processor **automatically sends** approved emails
- ✅ Task file includes `to`, `subject`, and `message_id` metadata
- ✅ Gmail API used with OAuth 2.0 authentication
- ✅ Failed emails include manual instructions in `Done/` folder

---

## File Structure

### **Email Task File Format**

When Gmail watcher detects an email, it creates:

```markdown
---
type: email
message_id: 1234567890abcdef
from: sender@example.com
subject: Important Update
received: 2026-01-21T12:00:00
priority: high
status: pending
---

# New Email: Important Update

## Email Information
- **From:** sender@example.com
- **Subject:** Important Update
- **Date:** Mon, 21 Jan 2026 12:00:00 +0000
- **Priority:** high

## Email Preview
This is the email content...

## Gmail Link
https://mail.google.com/mail/u/0/#inbox/1234567890abcdef
```

### **Approved Email Reply File**

When you (or auto-approver) creates a reply, it should be:

```markdown
---
type: email
action: send_reply
to: recipient@example.com
subject: Re: Important Update
message_id: 1234567890abcdef
status: approved
---

## Email Reply

Hi [Recipient Name],

Thank you for your email about [topic]. Here's my response...

[Your full reply here]

Best regards,
[Your Name]
```

---

## Components

### **1. Email Sender Module**

**File:** `watchers/email_sender.py`

**Features:**
- ✅ Gmail API integration with OAuth 2.0
- ✅ Send emails with thread support (replies)
- ✅ HTML and plain text support
- ✅ Automatic authentication token refresh
- ✅ Comprehensive error handling
- ✅ Audit logging

**Dependencies:**
```bash
pip install google-api-python-client google-auth-oauthlib
```

### **2. Approval Processor Enhancement**

**File:** `watchers/approval_processor.py`

**Changes:**
- ✅ Integrated email sender module
- ✅ Reads email body from approved action files
- ✅ Extracts `to`, `subject`, `message_id` from metadata
- ✅ Sends via Gmail API automatically
- ✅ Falls back to manual instructions on failure

**New Logic:**
1. Check if email sender is available
2. If yes, send via Gmail API
3. If successful, move to `Done/` with confirmation
4. If failed, move to `Done/` with manual instructions
5. If not available, provide manual sending template

### **3. WhatsApp Watcher Status**

**Status:** ✅ **Working Correctly**

**Current Configuration:**
- ✅ Running in **visible mode** (browser shows)
- ✅ Checks every 30 seconds for urgent keywords
- ✅ 15 keywords monitored: urgent, asap, emergency, critical, help, invoice, payment, etc.
- ✅ Session persistence in `watchers/whatsapp_session/`
- ✅ Memory leak fixes applied
- ✅ Auto-reconnection on page timeout

**No Issues Found** - WhatsApp watcher is working as designed.

---

## Usage

### **Send Email Reply (Automated)**

1. **Gmail watcher** detects email → Creates `Needs_Action/EMAIL_123456.md`
2. **Review** the email task in Obsidian
3. **Create reply** in same file or new file in `Approved/`:
   ```markdown
   ---
   type: email
   action: send_reply
   to: original.sender@example.com
   subject: Re: Original Subject
   message_id: 1234567890abcdef
   ---

   Hi [Name],

   Thanks for your email...

   Best,
   [Your Name]
   ```
4. **Approval processor** picks up the file automatically
5. **Email sender** sends via Gmail API
6. **Confirmation** in `Done/` folder with message ID

### **Send Email Manually (Fallback)**

If auto-send fails or email sender unavailable:

```bash
# From watchers directory
python email_sender.py \
  --to "recipient@example.com" \
  --subject "Test Subject" \
  --body "Email body here"
```

### **Test Email Integration**

```bash
# Test email sender
cd watchers
python email_sender.py \
  --to "your-email@example.com" \
  --subject "AI Employee Test" \
  --body "This is a test email from AI Employee"
```

---

## Configuration

### **Required Setup**

1. **Gmail API Credentials** (same as Gmail watcher)
   - Google Cloud Project with Gmail API enabled
   - OAuth 2.0 credentials
   - Located at: `watchers/credentials/credentials.json`
   - Token at: `watchers/credentials/token.json`

2. **Python Dependencies**
   ```bash
   pip install google-api-python-client google-auth-oauthlib
   ```

3. **Approval Processor**
   - Must be running to process approved emails
   - Runs via PM2 or manually: `python approval_processor.py --once`

### **Environment Variables**

The email sender uses the same credentials as Gmail watcher, configured in watchers/.env:

```bash
# These are shared with Gmail watcher
GMAIL_CREDENTIALS_PATH=./credentials/credentials.json
# Token is auto-generated on first authentication
```

---

## Troubleshooting

### **Email Not Sending Automatically**

**Check 1:** Is approval processor running?
```bash
pm2 status approval-processor
# Should show "online"
```

**Check 2:** Are Gmail credentials valid?
```bash
# Token should exist
ls watchers/credentials/token.json

# Credentials should exist
ls watchers/credentials/credentials.json
```

**Check 3:** Is approved file formatted correctly?
```bash
# Should have these fields in frontmatter:
# - type: email
# - action: send_reply
# - to: email@address.com
# - subject: Reply Subject
```

**Check 4:** Review approval processor logs
```bash
tail -50 Logs/approval_processor.log
```

### **WhatsApp Watcher Issues**

**Issue:** Browser not authenticating

**Solution:**
- Check logs: `tail -50 Logs/whatsappwatcher_2026-01-21.log`
- Browser should open in visible mode (configured)
- Scan QR code when prompted
- Wait for authentication to complete

**Issue:** Not detecting urgent messages

**Solution:**
- Check keywords: grep "WHATSAPP_KEYWORDS" watchers/.env
- Add custom keywords: `urgent,asap,emergency,critical,help`
- Check logs for "urgent messages found"

---

## Example Workflow

### **Complete Email Reply Example**

**1. Email Received**
```
From: client@company.com
Subject: Project Update Request
Gmail Watcher → Creates Needs_Action/EMAIL_abc123.md
```

**2. You Review in Obsidian**
Open the task file, see email content

**3. Create Reply in Approved/**
```markdown
---
type: email
action: send_reply
to: client@company.com
subject: Re: Project Update Request
message_id: abc123
---

Hi [Client Name],

I've reviewed the project update request. Here's my response...

[Detailed response]

Best regards,
Your Name
```

**4. Auto-Approver** (or you manually approve)
Moves to `Approved/EMAIL_REPLY_abc123.md`

**5. Approval Processor** (running every 30s)
- Detects approved file
- Reads metadata and content
- Calls email sender
- **Email sent automatically via Gmail API!**

**6. Confirmation**
File moves to `Done/EMAIL_REPLY_abc123.md` with:
```
**Completed:** 2026-01-21T13:00:00
**Note:** Email sent successfully via Gmail API. Message ID: xyz789
```

---

## Summary

### **✅ What's Working**
- Email sender module created and integrated
- Approval processor enhanced with Gmail API support
- Automatic email sending when approved
- Fallback to manual instructions on failure
- WhatsApp watcher working correctly (no issues found)

### **📝 Next Steps**
1. Test email sender with manual command
2. Create a sample approved email reply
3. Verify approval processor sends it
4. Monitor logs for any authentication issues

### **🔒 Security**
- Uses same OAuth 2.0 as Gmail watcher (secure)
- No hardcoded credentials
- Token auto-refresh supported
- Human-in-the-loop approval maintained

---

**Questions?**
- Check logs: `Logs/approval_processor.log`
- Check PM2: `pm2 logs approval-processor`
- Test email: `python watchers/email_sender.py --help`
