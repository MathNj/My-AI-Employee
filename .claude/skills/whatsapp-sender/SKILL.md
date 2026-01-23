---
name: whatsapp-sender
description: Send WhatsApp messages via WhatsApp MCP server after approval workflow. Uses Playwright browser automation (shares authentication with WhatsApp Watcher). Integrates with auto-approver skill for intelligent approval decisions. Supports individual and group messaging with complete audit trail.
---

# WhatsApp Sender (via WhatsApp MCP)

## Overview

This skill sends WhatsApp messages through the **WhatsApp MCP server** using Playwright browser automation. It integrates with the approval workflow and auto-approver system for intelligent, automated messaging while maintaining human oversight for important communications.

## Architecture

```
┌─────────────────────────────────────────┐
│  Auto-Approver Skill                   │
│  - Evaluates pending requests          │
│  - Auto-approves routine messages      │
│  - Holds important messages for review │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  /Approved Folder                       │
│  - Human-approved messages             │
│  - Auto-approved messages              │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  WhatsApp Sender Skill                  │
│  - Reads approved message files        │
│  - Extracts metadata & content         │
│  - Calls WhatsApp MCP server           │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  WhatsApp MCP Server                    │
│  - Playwright automation               │
│  - Sends via WhatsApp Web             │
│  - Shared session with watcher        │
└─────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **WhatsApp MCP Server Installed:**
   ```bash
   cd mcp-servers/whatsapp-mcp
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **WhatsApp Web Authenticated:**
   - Run WhatsApp Watcher first to authenticate
   - Or: `python mcp-servers/whatsapp-mcp/whatsapp_sender.py --visible --to "Test" --message "Test"`

### Execute Approved Message

```bash
# Send an approved WhatsApp message
cd watchers
python approval_processor.py --once
```

### Direct Message Send (Advanced - Bypasses Approval)

```bash
# Send message directly for testing
python mcp-servers/whatsapp-mcp/whatsapp_sender.py \
  --to "John Doe" \
  --message "Hello from the AI Employee!"
```

## How It Works

### 1. Message Created by AI

When Claude needs to send a WhatsApp message, it creates a file in `/Pending_Approval`:

```yaml
---
type: whatsapp
to: John Doe
message_id: whatsapp_1234567890
priority: medium
status: pending
---

## Message

Hi John,

This is a test message from the AI Employee system.

Let me know if you received this!

Best regards,
AI Employee
```

### 2. Approval Workflow

**Option A: Auto-Approver** (if routine message)
- Auto-approver checks: Known contact? Safe content?
- If yes: Moves to `/Approved` automatically
- If no: Keeps in `/Pending_Approval` for human review

**Option B: Human Approval**
- You review the message in Obsidian
- Move to `/Approved` (send) or `/Rejected` (cancel)

### 3. Message Sent via WhatsApp MCP

Approval processor detects file in `/Approved`:

```bash
python watchers/approval_processor.py --once
```

**What happens:**
1. ✅ Parses message metadata (to, message body)
2. ✅ Initializes Playwright browser with persistent session
3. ✅ Searches for chat by contact/group name
4. ✅ Types and sends message via WhatsApp Web
5. ✅ Moves file to `/Done`
6. ✅ Logs action to `/Logs/whatsapp_YYYY-MM-DD.json`

## Supported Features

### ✅ Recipients

- **Individual Contacts**: Search by name (must match exactly)
- **Groups**: Send to WhatsApp groups by group name
- **Multiple recipients**: Not supported by WhatsApp Web API (one at a time)

### ✅ Message Types

- **Text messages**: Plain text messages (markdown supported in content)
- **Long messages**: No character limit (splits automatically if needed)
- **Emojis**: ✅ Fully supported

### ❌ Not Yet Supported

- Media attachments (images, documents, voice notes)
- Message templates
- Bulk messaging
- Conversation history retrieval

## Usage Examples

### Example 1: Customer Follow-up

```yaml
---
type: whatsapp
to: Sarah Johnson
priority: medium
---

## Message

Hi Sarah! 👋

Just following up on your inquiry about our services. I'd be happy to schedule a call to discuss your requirements.

Would you be available tomorrow at 2 PM?

Best regards,
AI Employee
```

### Example 2: Team Notification

```yaml
---
type: whatsapp
to: Project Team
priority: low
---

## Message

Team update:

✅ Phase 1 completed
✅ Client approval received
📅 Starting Phase 2 on Monday

Please review the attached documents in the shared folder.

Thanks!
```

### Example 3: Urgent Alert

```yaml
---
type: whatsapp
to: John Smith
priority: high
---

## Message

🚨 URGENT: Server incident detected

The production server is experiencing high load. Current response time: 5.2s

Investigating now. Will update in 30 minutes.

- AI Employee
```

## Integration with WhatsApp Watcher

### Separate Concerns

- **WhatsApp Watcher** (Read-only):
  - Monitors incoming messages
  - Detects urgent keywords
  - Creates task files in `/Needs_Action`
  - No sending capability

- **WhatsApp Sender** (Write action):
  - Sends outgoing messages
  - Requires approval workflow
  - Uses same authentication session
  - No monitoring capability

### Shared Session

Both use the same browser session (`watchers/whatsapp_session/`):

```
whatsapp_session/
├── Default/
│   ├── Cookies  # Auth cookies (shared)
│   ├── Local Storage
│   └── Session Storage
```

Benefits:
- Authenticate once, use for both
- Session persists across restarts
- No need to re-scan QR code

## Error Handling

### Chat Not Found

**Problem**: Contact/group name doesn't match exactly

**Solution**:
1. Verify name in WhatsApp Web
2. Use exact spelling (case-sensitive)
3. For groups, use full group name

### Not Authenticated

**Problem**: WhatsApp Web not logged in

**Solution**:
```bash
# Run watcher first to authenticate
python watchers/whatsapp_watcher.py --visible

# Or test sender directly
python mcp-servers/whatsapp-mcp/whatsapp_sender.py --visible --to "Test" --message "Test"
```

Scan QR code when prompted.

### Browser Crashes

**Problem**: Playwright browser process died

**Solution**:
1. Check if Chromium installed: `playwright install chromium`
2. Clear session: Delete `whatsapp_session/` folder
3. Re-authenticate and retry

## Logging and Audit Trail

### Action Logs

All WhatsApp sends logged to:
```
Logs/whatsapp_YYYY-MM-DD.json
```

Format:
```json
{
  "timestamp": "2026-01-22T10:30:00",
  "action": "send_whatsapp_message",
  "recipient": "John Doe",
  "message_length": 156,
  "success": true,
  "message_id": "whatsapp_1234567890"
}
```

### Done Folder

Completed messages moved to `/Done` with result note:
```markdown
**Completed:** 2026-01-22T10:30:00
**Note:** WhatsApp message sent successfully via Playwright automation.
Recipient: John Doe
Timestamp: 2026-01-22T10:30:15
```

## Troubleshooting

### "Contact not found"

**Checklist:**
- [ ] Contact exists in your WhatsApp
- [ ] Name matches exactly (case-sensitive)
- [ ] Try sending manually via WhatsApp Web first
- [ ] For groups, use full group name (not abbreviations)

### "Browser not authenticated"

**Checklist:**
- [ ] Run WhatsApp Watcher first
- [ ] Scan QR code when prompted
- [ ] Check WhatsApp Web loaded in browser
- [ ] Verify session folder exists

### "Message not sending"

**Checklist:**
- [ ] Internet connection working
- [ ] WhatsApp Web accessible (https://web.whatsapp.com)
- [ ] Message input box found
- [ ] Send button clickable
- [ ] Check logs for detailed error

## Security and Privacy

### HITL Required

All WhatsApp messages **require human approval**:

- ❌ No automatic sending
- ✅ Human reviews every message
- ✅ Can reject inappropriate messages
- ✅ Complete audit trail

### Data Privacy

- Messages stored locally (markdown files)
- No cloud API usage
- Session data on local machine only
- PII redacted from logs

## Testing

### Test Message Send

```bash
# Visible mode (see what happens)
python mcp-servers/whatsapp-mcp/whatsapp_sender.py \
  --visible \
  --to "Test Contact" \
  --message "Test message from WhatsApp MCP"

# Headless mode (production)
python mcp-servers/whatsapp-mcp/whatsapp_sender.py \
  --to "Test Contact" \
  --message "Test message from WhatsApp MCP"
```

### Test Approval Workflow

1. Create test message in `/Pending_Approval`
2. Move to `/Approved`
3. Run: `python watchers/approval_processor.py --once`
4. Check message sent in WhatsApp Web
5. Verify file moved to `/Done`

## MCP Server Details

### Server Location

```
mcp-servers/whatsapp-mcp/
├── server.py              # MCP server (JSON-RPC)
├── whatsapp_sender.py     # Playwright automation
├── requirements.txt       # Python dependencies
├── package.json           # Metadata
├── README.md              # Documentation
└── logs/                  # Server logs
```

### MCP Tool: `send_whatsapp_message`

**Parameters:**
- `to` (string, required): Contact name or group name
- `message` (string, required): Message content

**Returns:**
```json
{
  "success": true,
  "recipient": "John Doe",
  "message": "Hi John, just checking in...",
  "timestamp": "2026-01-22T10:30:15"
}
```

## Best Practices

### ✅ DO

- Use exact contact/group names
- Keep messages concise and clear
- Include context in message body
- Use appropriate priority levels
- Test with visible mode first

### ❌ DON'T

- Don't send spam or bulk messages
- Don't use for urgent/time-sensitive communications (may have delays)
- Don't send very long messages (>1000 chars)
- Don't assume auto-approval for all messages
- Don't share session files (security risk)

## Future Enhancements

Planned features for future versions:

1. **Media attachments**: Send images, documents, voice notes
2. **Message templates**: Pre-defined templates for common messages
3. **Bulk messaging**: Send same message to multiple contacts
4. **Conversation history**: Retrieve past conversations
5. **Search messages**: Find messages by date/content
6. **Contact info**: Get contact details and profile picture
7. **Message status**: Track delivered/read receipts
8. **Scheduled messages**: Queue messages for later delivery

## Related Skills

- **whatsapp-watcher**: Monitor incoming WhatsApp messages
- **auto-approver**: Intelligent approval decisions
- **approval-processor**: Execute approved actions
- **email-sender**: Send emails via Gmail MCP

## Support

For issues or questions:

1. Check logs: `Logs/whatsapp_YYYY-MM-DD.json`
2. Check server logs: `mcp-servers/whatsapp-mcp/logs/whatsapp-mcp.log`
3. Test with visible mode: `--visible` flag
4. Verify WhatsApp Web authentication
5. Check Playwright installation: `playwright install chromium`

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-01-22
**Status:** Production Ready ✅
