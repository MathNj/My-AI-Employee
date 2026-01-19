# Gmail Send MCP Server

Model Context Protocol (MCP) server for sending emails via Gmail API.

## Overview

This MCP server provides an AI Employee with the ability to send emails through Gmail. It implements the `send_email` tool which supports:
- Plain text and HTML email bodies
- CC and BCC recipients
- File attachments (base64-encoded)
- Full error handling and logging

## Setup

### 1. Gmail API Project Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

### 2. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Desktop app" or "Web application"
4. Add authorized redirect URI: `http://localhost:3000`
5. Save and copy your Client ID and Client Secret

### 3. Environment Variables

Create a `.env` file in the project root:

```bash
# Gmail OAuth2 Credentials
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:3000

# Optional: Custom paths
GMAIL_TOKEN_PATH=tokens/gmail-token.json
MCP_LOG_PATH=Logs/mcp_server.log
```

### 4. Install Dependencies

```bash
cd mcp/gmail-send-server
npm install
```

### 5. Authenticate (First Time Only)

The server will automatically authenticate on first startup. You'll need to:

1. Run the server (it will print an auth URL)
2. Visit the auth URL in your browser
3. Grant Gmail permissions
4. Copy the authorization code
5. Paste it back into the server

Tokens are saved automatically and refreshed when expired.

## Usage

### Starting the Server

```bash
# Production
npm start

# Development (with auto-reload)
npm run dev
```

### Tool Schema: `send_email`

```json
{
  "name": "send_email",
  "description": "Send an email via Gmail API. Supports plain text, HTML, CC, BCC, and file attachments.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "description": "Recipient email address (required)"
      },
      "subject": {
        "type": "string",
        "description": "Email subject line (required)"
      },
      "body": {
        "type": "string",
        "description": "Plain text email body (optional if html is provided)"
      },
      "html": {
        "type": "string",
        "description": "HTML email body (optional if body is provided)"
      },
      "cc": {
        "type": "string",
        "description": "CC recipient email address (optional)"
      },
      "bcc": {
        "type": "string",
        "description": "BCC recipient email address (optional)"
      },
      "attachments": {
        "type": "array",
        "description": "Array of file attachments (optional)",
        "items": {
          "type": "object",
          "properties": {
            "filename": { "type": "string" },
            "content": { "type": "string", "description": "Base64-encoded" },
            "contentType": { "type": "string" }
          },
          "required": ["filename", "content"]
        }
      }
    },
    "required": ["to", "subject"]
  }
}
```

### Example Usage

**Simple text email:**
```json
{
  "to": "recipient@example.com",
  "subject": "Hello from AI Employee",
  "body": "This is a plain text email sent via MCP server."
}
```

**HTML email with CC:**
```json
{
  "to": "recipient@example.com",
  "subject": "HTML Email",
  "html": "<h1>Hello!</h1><p>This is an <strong>HTML</strong> email.</p>",
  "cc": "manager@example.com"
}
```

**Email with attachment:**
```json
{
  "to": "recipient@example.com",
  "subject": "Invoice Attached",
  "body": "Please find the invoice attached.",
  "attachments": [
    {
      "filename": "invoice.pdf",
      "content": "JVBERi0xLjQKJeLjz9MK...",
      "contentType": "application/pdf"
    }
  ]
}
```

## Integration with AI Employee

This MCP server is integrated with the AI Employee system through:

1. **Claude Desktop Config** (`~/.claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "gmail-send": {
      "command": "node",
      "args": ["C:/Users/Najma-LP/Desktop/AI_Employee_Vault/mcp/gmail-send-server/src/index.js"],
      "env": {
        "GMAIL_CLIENT_ID": "your-client-id",
        "GMAIL_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

2. **task-processor skill** (T054):
   - Invokes `send_email` tool via MCP for approved actions
   - Reads recipient, subject, body from approval request metadata

3. **MCP Action Queue** (T055):
   - Queues email actions for batch processing
   - Tracks action status in `/Logs/mcp_actions.json`

## Response Format

### Success Response:
```json
{
  "success": true,
  "messageId": "18f45abc123def456",
  "threadId": "18f45abc123def456",
  "labelIds": ["SENT"]
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Authentication failed. Please re-authenticate with Gmail."
}
```

## Logging

All MCP operations are logged to `Logs/mcp_server.log`:

```
[2025-01-17T10:30:45.123Z] [INFO] Gmail Send MCP Server starting...
[2025-01-17T10:30:46.456Z] [INFO] Loaded existing Gmail tokens
[2025-01-17T10:30:50.789Z] [INFO] Executing send_email tool {"to":"user@example.com","subject":"Test"}
[2025-01-17T10:30:51.234Z] [INFO] Email sent successfully {"id":"18f45abc123","to":"user@example.com"}
```

## Troubleshooting

### Authentication Failed
- Verify GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET are correct
- Check that Gmail API is enabled in Google Cloud Console
- Ensure redirect URI matches: `http://localhost:3000`

### 403 Permission Denied
- Verify Gmail API scopes include `https://www.googleapis.com/auth/gmail.send`
- Re-authenticate to get fresh tokens

### Invalid Request
- Check that all required parameters are provided: `to`, `subject`
- Ensure at least one of `body` or `html` is provided
- Verify attachments are base64-encoded

## Testing

Run the integration test:
```bash
npm test
```

This will verify:
- MCP server startup (T053)
- Tool listing
- Email sending with mock data

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│ AI Employee     │────▶│ task-processor   │────▶│ Gmail Send  │
│ (Claude Code)   │     │ skill (T054)     │     │ MCP Server  │
└─────────────────┘     └──────────────────┘     └─────────────┘
                               │                         │
                               ▼                         ▼
                        /Pending_Approval/      Gmail API
                              │
                              ▼ (approved)
                         /Approved/
                              │
                              ▼
                         /Done/
```

## Silver Tier Tasks

This MCP server implements the following Silver Tier tasks:
- **T046**: Create mcp/gmail-send-server/package.json
- **T047**: Implement mcp/gmail-send-server/src/index.ts
- **T048**: Define send_email tool
- **T049**: Implement Gmail API integration
- **T050**: Add error handling
- **T051**: Implement MCP logging
- **T052**: Create MCP README.md
- **T053**: Test MCP server startup
- **T054**: Extend task-processor to invoke MCP
- **T055**: Add MCP action queue
- **T056**: Test end-to-end MCP workflow

## License

MIT License - Part of the Personal AI Employee System
