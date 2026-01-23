# WhatsApp MCP Server

Model Context Protocol (MCP) server for WhatsApp messaging functionality.

## Features

- **Send text messages** to individuals and groups
- **Persistent browser session** (shares authentication with WhatsApp Watcher)
- **Human-in-the-Loop approval workflow** integration
- **Comprehensive error handling** with retry logic
- **Detailed audit logging** (all actions logged)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Authenticate WhatsApp Web:
   - Run the WhatsApp Watcher first to authenticate
   - Or run in visible mode: `python whatsapp_sender.py --visible --to "Test" --message "Test"`

## Usage

### As MCP Server

Add to Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "python",
      "args": ["/path/to/mcp-servers/whatsapp-mcp/server.py"],
      "env": {
        "VAULT_PATH": "/path/to/AI_Employee_Vault"
      }
    }
  }
}
```

### Standalone Testing

```bash
python whatsapp_sender.py --to "Contact Name" --message "Hello from WhatsApp!"
```

## Available Tools

### `send_whatsapp_message`

Send a WhatsApp message to a contact or group.

**Parameters:**
- `to` (string, required): Contact name or group name
- `message` (string, required): Message content to send

**Example:**
```json
{
  "to": "John Doe",
  "message": "Hello! This is a test message from the AI Employee."
}
```

## HITL Approval Workflow

All WhatsApp messages require human approval:

1. AI creates message request in `/Pending_Approval`
2. Human reviews message in Obsidian
3. Human moves to `/Approved` if approved
4. Approval processor executes the send
5. Message file moved to `/Done` with result

## Session Management

- Uses same session as WhatsApp Watcher (located in `watchers/whatsapp_session/`)
- Browser stays authenticated for extended periods
- Session persists across restarts

## Error Handling

- **Chat not found**: Verify contact/group name matches exactly
- **Not authenticated**: Run WhatsApp Watcher first to authenticate
- **Browser errors**: Automatic retry with exponential backoff
- **Session timeout**: Re-authenticate via WhatsApp Watcher

## Logging

All actions logged to:
- `logs/whatsapp-mcp.log` - Server logs
- `Logs/mcp_actions_YYYY-MM-DD.json` - Action audit trail

## Security

- All messages require HITL approval
- No automatic sending (manual approval required)
- Session data stored locally (never shared)
- PII redacted from logs

## Troubleshooting

### "Chat not found" error
- Verify contact/group name is exact
- Check WhatsApp Web is loaded and authenticated
- Try sending manually via WhatsApp Web first

### "Not authenticated" error
- Run WhatsApp Watcher to authenticate
- Or run: `python whatsapp_sender.py --visible --to "Test" --message "Test"`
- Scan QR code when prompted

### Browser crashes
- Check Playwright is installed: `playwright install chromium`
- Check session directory permissions
- Try deleting `whatsapp_session` and re-authenticating

## Architecture

```
AI Employee (Claude)
    ↓
Creates approval request
    ↓
/Pending_Approval (HITL review)
    ↓
/Approved (by human)
    ↓
Approval Processor
    ↓
WhatsApp MCP Server
    ↓
Playwright → WhatsApp Web
    ↓
Message sent
```

## Integration with WhatsApp Watcher

- **Watcher**: Monitors incoming messages (read-only)
- **MCP Server**: Sends outgoing messages (write action)
- **Shared session**: Both use same authentication
- **Separate concerns**: Clean separation of monitoring vs. action

## Future Enhancements

- Media attachments (images, documents)
- Message templates
- Bulk messaging
- Conversation history retrieval
- Search messages by date/content
- Contact information retrieval
