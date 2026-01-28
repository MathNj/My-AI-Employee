---
name: email-sender
description: Send emails via Gmail MCP server after approval workflow. Uses OAuth 2.0 authentication (no app passwords needed). Integrates with auto-approver skill for intelligent approval decisions. Supports attachments, HTML, CC/BCC, and complete audit trail.
---

# Email Sender (via Gmail MCP)

## Overview

This skill sends emails through the **Gmail MCP server** using OAuth 2.0 authentication. It integrates with the approval workflow and auto-approver system for intelligent, automated email sending while maintaining human oversight for important communications.

## Architecture

```
┌─────────────────────────────────────────┐
│  Auto-Approver Skill                   │
│  - Evaluates pending requests          │
│  - Auto-approves known contacts        │
│  - Holds important emails for review   │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  /Approved Folder                       │
│  - Human-approved emails               │
│  - Auto-approved emails                │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  Email Sender Skill                     │
│  - Reads approved email files          │
│  - Extracts metadata & content         │
│  - Calls Gmail MCP server              │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  Gmail MCP Server                       │
│  - OAuth 2.0 authentication            │
│  - Sends via Gmail API                 │
│  - Handles attachments                 │
└─────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Gmail MCP Server Running:**
   ```bash
   # Should already be running
   cd mcp-servers/gmail-mcp
   node dist/index.js
   ```

2. **OAuth Configured:**
   - `mcp-servers/gmail-mcp/credentials.json` ✅
   - `mcp-servers/gmail-mcp/token.json` ✅

### Execute Approved Email

```bash
# Send an approved email
cd .claude/skills/email-sender
python scripts/send_email.py \
  --execute-approved /path/to/Approved/EMAIL_*.md
```

### Direct Email Send (Advanced)

```bash
# Send email directly (bypasses approval)
python scripts/send_email.py \
  --to "client@example.com" \
  --subject "Invoice Attached" \
  --body "Please find your invoice attached."
```

## How It Works

### 1. Email Created by AI

When Claude needs to send an email, it creates a file in `/Pending_Approval`:

```yaml
---
type: email
to: client@example.com
subject: Invoice for January
format: text
---

Hi Client,

Please find attached your January invoice for $2,500.

Total due: January 31, 2026

Best regards,
AI Employee
```

### 2. Approval Workflow

**Option A: Auto-Approver** (if known contact)
- Auto-approver checks: Known contact? Safe content?
- If yes: Moves to `/Approved` automatically
- If no: Keeps in `/Pending_Approval` for human review

**Option B: Human Approval**
- You review the email in Obsidian
- Move to `/Approved` (send) or `/Rejected` (cancel)

### 3. Email Sent via Gmail MCP

Email sender skill detects file in `/Approved`:

```bash
python scripts/send_email.py --execute-approved Approved/EMAIL_*.md
```

**What happens:**
1. ✅ Parses email metadata (to, subject, body)
2. ✅ Calls Gmail MCP server with OAuth token
3. ✅ Gmail API sends the email
4. ✅ Moves file to `/Done`
5. ✅ Logs action to `/Logs/emails_YYYY-MM-DD.json`

## Supported Features

### ✅ Recipients

- **To**: Primary recipient(s)
- **CC**: Carbon copy recipients
- **BCC**: Blind carbon copy
- **Multiple recipients**: `["email1@example.com", "email2@example.com"]`

### ✅ Attachments

```yaml
---
attachments: /path/to/invoice.pdf,/path/to/receipt.pdf
---
```

### ✅ HTML vs Plain Text

```yaml
---
format: html
---
<h1>Hello!</h1>
<p>This is <strong>HTML</strong> email.</p>
```

### ✅ Templates (Future)

```bash
# Use email template
python scripts/compose_email.py \
  --template invoice_notification \
  --to "client@example.com" \
  --amount "$2,500" \
  --due-date "2026-01-31"
```

## Configuration

### Gmail MCP Server

**Location:** `mcp-servers/gmail-mcp/`

**Files:**
- `credentials.json` - OAuth client credentials
- `token.json` - OAuth access token
- `config/.env` - Environment variables

**Status:** ✅ Running and authenticated

### Email Sender Skill

**Location:** `.claude/skills/email-sender/`

**Config:** None required (uses Gmail MCP)

## Integration with Auto-Approver

The auto-approver skill makes intelligent decisions about emails:

### ✅ Auto-Approves When:

- Recipient is **known contact** (5+ interactions)
- Content is **safe** (no urgent/payment keywords)
- It's a **reply** (not new conversation)
- **Routine business communication**

### ⏸️ Holds for Review When:

- **New contact** (first interaction)
- **Financial content** (payment, invoice, transfer)
- **Urgent keywords** (URGENT, ASAP, emergency)
- **Unknown patterns**
- **Attachments** (unless verified safe)

## Examples

### Example 1: Routine Email (Auto-Approved)

```yaml
---
type: email
to: boss@company.com
subject: Weekly Report Attached
---
Hi Boss,

Please find attached the weekly status report.
All metrics are on track.

Best,
AI Employee
```

**Auto-Approver Decision:** ✅ APPROVE
- Known contact: boss@company.com (45 interactions)
- Safe content: Weekly report
- Confidence: 96%

**Result:** Email sent automatically via Gmail MCP ✅

### Example 2: Payment Request (Held for Review)

```yaml
---
type: email
to: new-vendor@unknown.com
subject: URGENT: Invoice Payment
---
Please approve payment of $5,000 to new vendor.
```

**Auto-Approver Decision:** ⏸️ HOLD
- Unknown contact: new-vendor@unknown.com (0 interactions)
- Financial content: $5,000 payment
- Urgent keyword: URGENT

**Result:** Held for your review in `/Pending_Approval` ⏸️

## Troubleshooting

### Email Not Sending

**Check Gmail MCP Server:**
```bash
# Is Gmail MCP running?
ps aux | grep "gmail-mcp"

# Check logs
tail -f mcp-servers/gmail-mcp/logs/gmail-mcp.log
```

**Check OAuth Token:**
```bash
# Token exists and valid?
cat mcp-servers/gmail-mcp/token.json | jq
```

**Test Direct Send:**
```bash
cd .claude/skills/email-sender
python scripts/send_email.py \
  --to "test@example.com" \
  --subject "Test" \
  --body "Test email"
```

### "MCP Server Not Found" Error

**Build the MCP Server:**
```bash
cd mcp-servers/gmail-mcp
npm install
npm run build
```

## Audit Trail

All email actions logged to: `/Logs/emails_YYYY-MM-DD.json`

```json
{
  "timestamp": "2026-01-19T22:50:00Z",
  "action": "email_sent",
  "to": "client@example.com",
  "subject": "Invoice Attached",
  "method": "gmail_mcp",
  "file": "EMAIL_20260119_invoice.md"
}
```

## Benefits of MCP vs SMTP

| Feature | Old (SMTP) | New (Gmail MCP) |
|---------|------------|-----------------|
| Authentication | App password ❌ | OAuth 2.0 ✅ |
| Security | Less secure | More secure |
| Attachments | Manual | Automatic |
| Rate limiting | Manual | Built-in |
| Token refresh | Manual | Automatic |
| Audit logging | Basic | Comprehensive |

## Version History

**v3.0.0** (2026-01-26) - Ultimate Edition
- ✅ Email template system with Jinja2 rendering
- ✅ Batch sending with rate limiting (token bucket algorithm)
- ✅ Bounce and complaint handling with classification
- ✅ Retry logic with exponential backoff
- ✅ Email scheduling and queue management
- ✅ Structured JSON logging
- ✅ Delivery tracking and analytics
- ✅ Email suppression list for bounces

**v2.0.0** (2026-01-19)
- ✅ Migrated from SMTP to Gmail MCP
- ✅ OAuth 2.0 authentication
- ✅ Integrated with auto-approver
- ✅ Removed dependency on app passwords

**v1.0.0** (2025-12-01)
- Initial SMTP-based implementation

---

## Ultimate Edition Features

### New Script: email_sender_ultimate.py

**Advanced Email Sending with:**

1. **Template System**
   - Jinja2-based email templates
   - Variable substitution
   - HTML and plain text support
   - Template inheritance

2. **Batch Processing**
   - Send multiple emails efficiently
   - Rate limiting (configurable emails/minute)
   - Parallel sending with thread pool
   - Progress tracking

3. **Bounce Handling**
   - Automatic bounce classification (hard/soft)
   - Suppression list management
   - Bounce analytics
   - SMTP code interpretation

4. **Queue Management**
   - Schedule emails for later
   - Persistent queue storage
   - Automatic retry on failure
   - Delivery status tracking

**Usage:**
```bash
# Send from template
python .claude/skills/email-sender/scripts/email_sender_ultimate.py \
  --template invoice_notification \
  --to "client@example.com" \
  --data '{"amount": "$2,500", "due_date": "2026-01-31"}'

# Batch send from file
python .claude/skills/email-sender/scripts/email_sender_ultimate.py \
  --batch emails_batch.json

# Process queued emails
python .claude/skills/email-sender/scripts/email_sender_ultimate.py \
  --process-queue

# Check bounces
python .claude/skills/email-sender/scripts/email_sender_ultimate.py \
  --bounces

# Show statistics
python .claude/skills/email-sender/scripts/email_sender_ultimate.py \
  --stats
```

**Configuration (email_sender_config.yaml):**
```yaml
smtp_host: smtp.gmail.com
smtp_port: 587
smtp_user: your-email@gmail.com
smtp_password: your-app-password
from_addr: noreply@example.com
from_name: "AI Employee"
rate_per_minute: 60
max_retries: 3
```

---

**Status:** Production Ready ✅
**Method:** Gmail MCP (OAuth 2.0) or SMTP
**Integration:** Auto-approver enabled


## Core Workflows

### Workflow 1: Send Email with Approval

1. **Compose email** (manual or template)
2. **Create approval request** in `/Pending_Approval`
3. **Human reviews** email content
4. **Move to `/Approved`** if acceptable
5. **approval-processor** detects and triggers email-sender
6. **Email sent** via MCP or SMTP
7. **Activity logged** to Dashboard

### Workflow 2: Reply to Inquiry

1. **Gmail watcher** detects important email
2. **Task processor** creates plan to reply
3. **email-sender** composes response
4. **Create approval request**
5. **After approval** → Send reply
6. **Thread maintained** (Reply-To preserved)

### Workflow 3: Scheduled Report

1. **Scheduler triggers** weekly report generation
2. **Generate report** content
3. **Compose email** with report attached
4. **Create approval request**
5. **After approval** → Send to recipients
6. **Log activity**

## Setup

### Option 1: MCP Server (Recommended)

MCP provides better integration with Claude Code and the approval system.

**Install MCP Email Server:**
```bash
npm install -g @modelcontextprotocol/server-email
```

**Configure Claude Code:**

Edit `~/.config/claude-code/mcp.json`:
```json
{
  "mcpServers": {
    "email": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-email"],
      "env": {
        "EMAIL_PROVIDER": "gmail",
        "EMAIL_ADDRESS": "your-email@gmail.com",
        "EMAIL_PASSWORD": "your-app-password"
      }
    }
  }
}
```

**Test MCP Connection:**
```bash
python scripts/test_email.py --mcp
```

See `references/mcp_setup.md` for complete setup guide.

### Option 2: Direct SMTP

For systems without MCP or as fallback.

**Configure SMTP:**

Create `watchers/credentials/smtp_config.json`:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "email_address": "your-email@gmail.com",
  "email_password": "your-app-password",
  "use_tls": true
}
```

**Gmail App Password:**
1. Enable 2-factor authentication
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use app password (not regular password)

**Test SMTP Connection:**
```bash
python scripts/test_email.py --smtp
```

See `references/smtp_guide.md` for detailed SMTP setup.

## Email Composition

### Method 1: Direct Parameters

```bash
python scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Your Subject" \
  --body "Email body content" \
  --create-approval
```

### Method 2: Template-Based

Available templates in `references/email_templates.md`:

**Invoice Email:**
```bash
python scripts/compose_email.py \
  --template invoice \
  --to "client@example.com" \
  --invoice-number "INV-001" \
  --amount "$1,500" \
  --due-date "2026-01-31"
```

**Customer Inquiry Response:**
```bash
python scripts/compose_email.py \
  --template inquiry-response \
  --to "customer@example.com" \
  --inquiry "Question about pricing" \
  --response "Our pricing starts at..."
```

**Business Report:**
```bash
python scripts/compose_email.py \
  --template report \
  --to "team@company.com" \
  --report-type "Weekly Status" \
  --summary "Completed 10 tasks this week"
```

### Method 3: Interactive Composer

```bash
python scripts/compose_email.py --interactive
```

Prompts for:
- To (recipient email)
- Subject
- Body (opens editor)
- Attachments (optional)
- Template (optional)

### Method 4: Via Claude Code

Simply ask:
- "Send email to client about invoice"
- "Reply to customer inquiry email"
- "Send weekly report email"

Claude will automatically compose and create approval request.

## Attachments

### Single Attachment

```bash
python scripts/send_email.py \
  --to "client@example.com" \
  --subject "Invoice" \
  --body "Please find attached" \
  --attach "/path/to/invoice.pdf" \
  --create-approval
```

### Multiple Attachments

```bash
python scripts/send_email.py \
  --to "client@example.com" \
  --subject "Documents" \
  --body "Attached documents" \
  --attach "/path/to/doc1.pdf" \
  --attach "/path/to/doc2.xlsx" \
  --create-approval
```

### Attachment Limits

- **Maximum size:** 25 MB per email (Gmail limit)
- **Maximum attachments:** 10 files recommended
- **Supported types:** PDF, DOCX, XLSX, PNG, JPG, TXT, CSV

Large files? Use cloud storage and send link instead.

## Email Templates

### Available Templates

See `references/email_templates.md` for complete library:

1. **Invoice Email** - Send invoices to clients
2. **Inquiry Response** - Reply to customer questions
3. **Meeting Follow-up** - Send meeting notes and action items
4. **Business Report** - Weekly/monthly status reports
5. **Welcome Email** - Onboard new clients/subscribers
6. **Reminder Email** - Payment reminders, deadline alerts
7. **Thank You Email** - Express gratitude to clients
8. **General Business** - Professional business communication

Each template includes:
- Subject line template
- Body structure
- Variable placeholders
- Tone guidelines
- Example usage

### Template Variables

Common variables across templates:
- `{recipient_name}` - Recipient's name
- `{sender_name}` - Your name
- `{company_name}` - Your company
- `{date}` - Current date
- `{amount}` - Dollar amounts
- `{invoice_number}` - Invoice ID
- `{due_date}` - Deadline dates

## Approval Workflow Integration

### Creating Approval Requests

All emails create approval requests by default:

```bash
python scripts/send_email.py \
  --to "client@example.com" \
  --subject "Invoice" \
  --body "Content" \
  --create-approval  # Default behavior
```

Creates file in `/Pending_Approval/EMAIL_[timestamp].md`:

```markdown
---
type: email
action: send_email
to: client@example.com
subject: Invoice for January
body: "Please find attached..."
attachments: ["/path/to/invoice.pdf"]
created: 2026-01-11T15:30:00Z
expires: 2026-01-12T15:30:00Z
status: pending
---

## Email Preview

**To:** client@example.com
**Subject:** Invoice for January

Please find attached your January invoice.

**Attachments:**
- invoice.pdf (125 KB)

---

## To Approve
Move this file to /Approved folder

## To Reject
Move this file to /Rejected folder
```

### Processing Approved Emails

The `approval-processor` skill (to be created) will:
1. Detect approved email in `/Approved`
2. Call `email-sender` to execute
3. Move approval file to `/Done`
4. Log activity

Manual execution (for testing):
```bash
python scripts/send_email.py \
  --execute-approved /path/to/approved/EMAIL_*.md
```

## Sending Methods

### Via MCP (Recommended)

MCP provides better integration and error handling.

**Requirements:**
- MCP server installed and configured
- Claude Code MCP integration enabled

**Advantages:**
- Better error messages
- Automatic retry logic
- Integration with Claude Code
- Unified API across tools

**Test:**
```bash
python scripts/test_email.py --mcp
```

### Via SMTP (Fallback)

Direct SMTP when MCP unavailable.

**Requirements:**
- SMTP credentials configured
- Gmail app password (for Gmail)

**Advantages:**
- No additional dependencies
- Works anywhere
- Direct control

**Test:**
```bash
python scripts/test_email.py --smtp
```

### Automatic Fallback

Scripts automatically try MCP first, fall back to SMTP:

```python
# Automatic fallback logic
try:
    send_via_mcp(email_data)
except MCPError:
    logger.warning("MCP failed, trying SMTP...")
    send_via_smtp(email_data)
```

## HTML vs Plain Text

### Plain Text (Default)

Simple, universal compatibility:

```bash
python scripts/send_email.py \
  --to "client@example.com" \
  --subject "Hello" \
  --body "Plain text message"
```

### HTML Email

Rich formatting, images, links:

```bash
python scripts/send_email.py \
  --to "client@example.com" \
  --subject "Newsletter" \
  --body-html "<h1>Hello</h1><p>Rich content</p>"
```

### HTML Template

Use pre-designed HTML template:

```bash
python scripts/compose_email.py \
  --template newsletter \
  --html \
  --title "January Update" \
  --content "..."
```

HTML templates in `assets/templates/`:
- `invoice.html` - Professional invoice email
- `report.html` - Business report format
- `newsletter.html` - Marketing/update format
- `basic.html` - Simple responsive layout

## Reply and Threading

### Reply to Email

Maintain email thread:

```bash
python scripts/send_email.py \
  --to "client@example.com" \
  --subject "Re: Your inquiry" \
  --body "Response content" \
  --in-reply-to "<original-message-id>" \
  --references "<original-message-id>" \
  --create-approval
```

### Gmail Watcher Integration

When Gmail watcher detects important email:
1. Extracts message-id from headers
2. Stores in task file metadata
3. email-sender uses for proper threading

## Error Handling

### Common Issues

**"SMTP Authentication Failed"**
- Use Gmail app password, not regular password
- Enable "Less secure app access" (if needed)
- Check email/password in config

**"MCP Server Not Found"**
```bash
npm install -g @modelcontextprotocol/server-email
```

**"Attachment Too Large"**
- Gmail limit: 25 MB
- Split into multiple emails
- Or use cloud storage link

**"Email Rejected by Server"**
- Check recipient email is valid
- Verify sender email is verified
- Review email content for spam triggers

### Logs

All activity logged to:
- `/Logs/email_activity_[date].json` - Send attempts
- `/Logs/actions_[date].json` - System actions
- Console output - Real-time status

### Dry Run Mode

Test without actually sending:

```bash
python scripts/send_email.py \
  --to "test@example.com" \
  --subject "Test" \
  --body "Test email" \
  --dry-run
```

Shows email preview without sending.

## Integration with Other Skills

### With Gmail Watcher (Bronze Tier)

```
Gmail receives important email
    ↓
Gmail watcher creates task in /Needs_Action
    ↓
Task processor creates reply plan
    ↓
email-sender composes response
    ↓
Approval request created
    ↓
Human approves
    ↓
email-sender sends reply
```

### With approval-processor (Silver Tier)

```
Any skill creates email approval request
    ↓
Placed in /Pending_Approval
    ↓
Human moves to /Approved
    ↓
approval-processor detects
    ↓
Calls email-sender to execute
    ↓
Email sent and logged
```

### With scheduler-manager (Silver Tier)

```
Scheduled task triggers (e.g., Monday 8 AM)
    ↓
Generate weekly report
    ↓
email-sender composes report email
    ↓
Approval request created
    ↓
After approval → Send to team
```

### With dashboard-updater (Bronze Tier)

Dashboard shows:
- Emails sent today/this week
- Pending email approvals
- Failed send attempts
- Recent email activity

## Best Practices

### Email Writing

**Subject Lines:**
- Clear and specific
- Max 50 characters
- Action-oriented when needed
- Example: "Invoice INV-001 Due Jan 31"

**Body Content:**
- Start with recipient name
- Clear purpose in first sentence
- Break into short paragraphs
- End with clear call-to-action
- Include signature

**Professional Tone:**
- Use "please" and "thank you"
- Be concise and clear
- Proofread before approving
- Avoid all caps or excessive punctuation

### Email Security

**Sensitive Information:**
- Never send passwords via email
- Use secure file sharing for sensitive docs
- Encrypt attachments if needed
- Double-check recipient before approving

**Spam Prevention:**
- Avoid spam trigger words
- Include unsubscribe link (bulk emails)
- Valid sender address
- Proper SPF/DKIM/DMARC records

### Response Times

- **Urgent:** < 1 hour (after approval)
- **Important:** < 4 hours
- **Normal:** < 24 hours
- **Low priority:** < 48 hours

Set up scheduled checks for approved emails.

## Scripts Reference

### send_email.py

Main email sending script.

**Usage:**
```bash
# Create approval request
python scripts/send_email.py --to "..." --subject "..." --body "..." --create-approval

# Execute approved
python scripts/send_email.py --execute-approved /path/to/file.md

# Dry run
python scripts/send_email.py --to "..." --subject "..." --body "..." --dry-run

# Direct send (bypass approval - not recommended)
python scripts/send_email.py --to "..." --subject "..." --body "..." --send-now
```

### compose_email.py

Interactive email composer with templates.

**Usage:**
```bash
# Interactive mode
python scripts/compose_email.py --interactive

# From template
python scripts/compose_email.py --template invoice --to "..." --invoice-number "..."

# List templates
python scripts/compose_email.py --list-templates
```

### test_email.py

Test email configuration and connectivity.

**Usage:**
```bash
# Test all methods
python scripts/test_email.py

# Test MCP only
python scripts/test_email.py --mcp

# Test SMTP only
python scripts/test_email.py --smtp

# Verbose output
python scripts/test_email.py --verbose

# Send test email
python scripts/test_email.py --send-test --to "your-email@example.com"
```

### setup_mcp.py

Configure MCP server for Claude Code.

**Usage:**
```bash
# Interactive setup
python scripts/setup_mcp.py

# Show current config
python scripts/setup_mcp.py --show

# Validate config
python scripts/setup_mcp.py --validate
```

## Security Considerations

### Credential Storage

**SMTP credentials:**
```
watchers/credentials/smtp_config.json
```

**MCP configuration:**
```
~/.config/claude-code/mcp.json
```

Both protected by `.gitignore` - never committed.

### App Passwords

For Gmail:
- Use app passwords, not account password
- One app password per application
- Revoke if compromised
- Rotate every 6 months

### Email Content

- Review before approving
- No passwords or sensitive data
- Verify recipient address
- Check attachments

### Approval Required

**Always require approval for:**
- Emails to new recipients
- Bulk emails
- Emails with attachments
- Any financial communication

**Can auto-approve (with caution):**
- Automated reports to known team
- Standard responses to known contacts
- System notifications to yourself

*Note: Auto-approve not implemented by default for safety.*

## Troubleshooting

### SMTP Connection Fails

1. Verify credentials in `smtp_config.json`
2. Enable 2FA and create app password
3. Check SMTP server and port
4. Test with: `python scripts/test_email.py --smtp --verbose`

### MCP Server Not Working

1. Check installation: `npm list -g @modelcontextprotocol/server-email`
2. Verify `mcp.json` configuration
3. Restart Claude Code
4. Test with: `python scripts/test_email.py --mcp --verbose`

### Email Not Delivered

1. Check spam folder
2. Verify recipient address
3. Review email logs in `/Logs`
4. Check email content for spam triggers

### Attachments Fail

1. Verify file exists
2. Check file size (< 25 MB)
3. Verify file permissions
4. Use absolute paths

## References

- `references/mcp_setup.md` - Complete MCP setup guide
- `references/smtp_guide.md` - SMTP configuration guide
- `references/email_templates.md` - Template library with examples
- `references/gmail_setup.md` - Gmail-specific setup

## Assets

- `assets/email_signature.txt` - Your email signature (customize)
- `assets/templates/invoice.html` - HTML invoice template
- `assets/templates/report.html` - HTML report template
- `assets/templates/basic.html` - Basic HTML template

---

**Note:** This skill requires either MCP server setup or SMTP configuration. MCP is recommended for better Claude Code integration.
