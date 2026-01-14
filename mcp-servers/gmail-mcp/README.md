# Gmail MCP Server

Production-ready Model Context Protocol (MCP) server for Gmail integration with OAuth 2.0 authentication and Human-in-the-Loop approval workflows.

## Features

### Core Capabilities
- **Send Emails**: Send emails with attachments, CC/BCC support, HTML/plain text
- **Read Emails**: Retrieve and filter emails with Gmail search syntax
- **Search Emails**: Advanced search with full Gmail query support
- **Draft Emails**: Create drafts for later sending
- **Profile Info**: Get Gmail account information

### Security & Safety
- **OAuth 2.0 Authentication**: Secure Google authentication with automatic token refresh
- **Human-in-the-Loop (HITL)**: Approval workflow for sensitive actions
- **Rate Limiting**: Prevents API quota exhaustion (60/min, 10000/day)
- **Audit Logging**: Comprehensive logging with PII redaction
- **Retry Logic**: Exponential backoff for transient failures
- **Auto-Approval**: Optional auto-approve for single-recipient emails

### Integration
- **Obsidian Vault Integration**: Creates approval files in `/Pending_Approval`
- **Audit Trail**: JSON logs in `/Logs` folder with timestamps
- **MCP Standard**: Compatible with Claude Code and other MCP clients

## Installation

### Prerequisites
- Node.js 20.0.0 or higher
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials from Google Cloud Console

### Setup Steps

#### 1. Install Dependencies
```bash
cd mcp-servers/gmail-mcp
npm install
```

#### 2. Build TypeScript
```bash
npm run build
```

#### 3. Configure Google Cloud Project

**A. Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

**B. Create OAuth 2.0 Credentials**
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as application type
4. Download credentials as `credentials.json`
5. Place in `mcp-servers/gmail-mcp/credentials.json`

**C. Configure OAuth Consent Screen**
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" (unless you have Google Workspace)
3. Fill in application name and contact information
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.compose`
5. Add your email as test user

#### 4. Set Up Environment Variables

Create `.env` file:
```bash
# Gmail MCP Server Configuration

# Google OAuth Credentials
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=urn:ietf:wg:oauth:2.0:oob

# Paths
VAULT_PATH=C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
LOG_PATH=./logs

# Auto-Approval (use with caution)
AUTO_APPROVE=false

# Logging
LOG_LEVEL=info
```

#### 5. Authenticate with Google

Run the authentication script:
```bash
node dist/auth.js
```

This will:
1. Open a browser for Google OAuth
2. Ask you to authorize the application
3. Save the token to `token.json`

**First-Time Setup:**
1. Browser opens to Google login
2. Select your Gmail account
3. Click "Allow" to grant permissions
4. Copy the authorization code
5. Paste into terminal
6. Token saved automatically

#### 6. Test the Server

```bash
npm test
```

This verifies:
- OAuth token is valid
- Gmail API connection works
- Profile information retrieved
- Logging functional

## Usage

### Starting the Server

```bash
npm start
```

Or use with Claude Code (see Configuration section below).

### Available Tools

#### 1. gmail_send_email

Send an email with optional attachments, CC/BCC.

**Example:**
```json
{
  "to": "client@example.com",
  "subject": "Invoice #12345",
  "body": "Please find attached your invoice for January 2026.",
  "cc": ["manager@example.com"],
  "attachments": [
    {
      "filename": "invoice-12345.pdf",
      "path": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault\\Invoices\\invoice-12345.pdf",
      "mimeType": "application/pdf"
    }
  ],
  "isHtml": false,
  "requireApproval": true
}
```

**Response (Pending Approval):**
```json
{
  "status": "pending_approval",
  "message": "Email requires approval. Approval request created.",
  "approvalFile": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault\\Pending_Approval\\EMAIL_email_send_2026-01-12T10-30-00-000Z.md",
  "instructions": "Move the approval file to /Approved folder to send the email."
}
```

**Response (Sent):**
```json
{
  "status": "success",
  "message": "Email sent successfully",
  "messageId": "18d1a2b3c4d5e6f7",
  "threadId": "18d1a2b3c4d5e6f7"
}
```

#### 2. gmail_read_emails

Read emails from inbox with filtering.

**Example:**
```json
{
  "query": "is:unread from:client@example.com",
  "maxResults": 10,
  "labelIds": ["INBOX", "IMPORTANT"]
}
```

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "emails": [
    {
      "id": "18d1a2b3c4d5e6f7",
      "threadId": "18d1a2b3c4d5e6f7",
      "from": "client@example.com",
      "to": "you@example.com",
      "subject": "Project Update",
      "snippet": "Hi, here's the latest update on the project...",
      "date": "Fri, 12 Jan 2026 10:30:00 GMT",
      "labels": ["INBOX", "IMPORTANT", "UNREAD"],
      "isUnread": true
    }
  ]
}
```

#### 3. gmail_search_emails

Search emails using Gmail query syntax.

**Example:**
```json
{
  "query": "subject:invoice after:2026/01/01",
  "maxResults": 20
}
```

Gmail Query Syntax:
- `from:user@example.com` - From specific sender
- `to:user@example.com` - To specific recipient
- `subject:invoice` - Subject contains "invoice"
- `has:attachment` - Has attachments
- `is:unread` - Unread emails
- `is:important` - Important emails
- `after:2026/01/01` - After date
- `before:2026/12/31` - Before date
- `newer_than:7d` - Last 7 days
- `older_than:30d` - Older than 30 days

#### 4. gmail_draft_email

Create an email draft.

**Example:**
```json
{
  "to": "client@example.com",
  "subject": "Follow-up on Meeting",
  "body": "Thank you for meeting with us today...",
  "isHtml": false
}
```

#### 5. gmail_get_profile

Get Gmail account information.

**Example:**
```json
{}
```

**Response:**
```json
{
  "status": "success",
  "profile": {
    "emailAddress": "you@example.com",
    "messagesTotal": 1523,
    "threadsTotal": 892
  }
}
```

## Human-in-the-Loop Workflow

### Approval Process

1. **Action Requested**: MCP tool called (e.g., `gmail_send_email`)
2. **Approval File Created**: Server creates markdown file in `/Pending_Approval`
3. **Human Review**: You review the approval request
4. **Approval Decision**:
   - **Approve**: Move file to `/Approved` folder
   - **Reject**: Move file to `/Rejected` folder
5. **Execution**: Approval processor detects approved file and executes action
6. **Logging**: Action logged to `/Logs` with full audit trail

### Approval File Format

```markdown
---
type: approval_request
action: Send Email
category: email_send
created: 2026-01-12T10:30:00Z
expires: 2026-01-13T10:30:00Z
status: pending
priority: high
---

# Email Approval Request

## Action
Send Email

## Details
**To:** client@example.com
**Subject:** Invoice #12345

## Email Body
```
Please find attached your invoice for January 2026.
```

## Attachments
- invoice-12345.pdf

## Reason
Email requires human approval before sending

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with a reason comment.

---
*Created by Gmail MCP Server*
*Request ID: 2026-01-12T10-30-00-000Z*
```

### Auto-Approval

Set `AUTO_APPROVE=true` in `.env` to enable auto-approval for:
- Single recipient emails
- Emails to known contacts (optional)

**Security Note**: Use auto-approval with caution. Always review important emails manually.

## Rate Limiting

The server implements rate limiting to prevent quota exhaustion:

- **Per Minute**: 60 requests
- **Per Day**: 10,000 requests

If limits are exceeded, the server returns an error:
```json
{
  "status": "error",
  "error": "Rate limit exceeded: too many requests per minute"
}
```

Rate limits reset automatically.

## Error Handling

### Retry Logic

The server automatically retries failed requests with exponential backoff:
- **Attempt 1**: Immediate
- **Attempt 2**: 1 second delay
- **Attempt 3**: 2 second delay
- **Max Attempts**: 3

### Error Types

1. **Authentication Error (401)**: Token expired or invalid
   - **Solution**: Re-run `node dist/auth.js`

2. **Permission Error (403)**: Insufficient permissions
   - **Solution**: Check OAuth scopes in Google Cloud Console

3. **Rate Limit Error (429)**: Too many requests
   - **Solution**: Wait and retry, or adjust rate limits

4. **Network Error**: Connection failed
   - **Solution**: Check internet connection, server retries automatically

## Logging

### Log Files

- **Error Log**: `logs/gmail-mcp-error.log` (errors only)
- **General Log**: `logs/gmail-mcp.log` (all events)
- **Audit Log**: `AI_Employee_Vault/Logs/actions_YYYY-MM-DD.json`

### Log Format

**Server Logs:**
```
2026-01-12T10:30:00.000Z [INFO] Email sent successfully {"messageId":"18d1a2b3c4d5e6f7","to":["client@example.com"],"subject":"Invoice #12345"}
```

**Audit Logs (JSON):**
```json
{
  "timestamp": "2026-01-12T10:30:00.000Z",
  "action": "gmail_send_email",
  "type": "email_send",
  "result": "success",
  "actor": "gmail-mcp-server",
  "data": {
    "to": "client@example.com",
    "subject": "Invoice #12345",
    "messageId": "18d1a2b3c4d5e6f7",
    "body": "[REDACTED]"
  }
}
```

**PII Redaction**: Sensitive data (tokens, passwords, email bodies) is automatically redacted in logs.

## Configuration

### Claude Code Integration

Add to `~/.config/claude-code/mcp.json` (Mac/Linux) or `%APPDATA%\Claude\mcp.json` (Windows):

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": ["C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\gmail-mcp\\dist\\index.js"],
      "env": {
        "VAULT_PATH": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault",
        "GMAIL_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GMAIL_CLIENT_SECRET": "your-client-secret",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GMAIL_CLIENT_ID` | Google OAuth client ID | - | Yes |
| `GMAIL_CLIENT_SECRET` | Google OAuth client secret | - | Yes |
| `GMAIL_REDIRECT_URI` | OAuth redirect URI | `urn:ietf:wg:oauth:2.0:oob` | No |
| `VAULT_PATH` | Obsidian vault path | Current directory | Yes |
| `GMAIL_CREDENTIALS_PATH` | Credentials JSON path | `./credentials.json` | No |
| `GMAIL_TOKEN_PATH` | Token JSON path | `./token.json` | No |
| `LOG_PATH` | Log directory path | `./logs` | No |
| `AUTO_APPROVE` | Enable auto-approval | `false` | No |
| `LOG_LEVEL` | Logging level | `info` | No |

## Troubleshooting

### "Gmail client not initialized"

**Problem**: OAuth token is missing or invalid.

**Solution**:
```bash
node dist/auth.js
```

### "Rate limit exceeded"

**Problem**: Too many requests in short time.

**Solution**: Wait 1 minute and retry. Consider reducing request frequency.

### "Token expired"

**Problem**: OAuth token expired (typically after 1 hour).

**Solution**: Server automatically refreshes tokens. If it fails, re-authenticate:
```bash
node dist/auth.js
```

### "Permission denied"

**Problem**: OAuth scopes missing or consent screen not configured.

**Solution**:
1. Check OAuth scopes in Google Cloud Console
2. Re-run OAuth consent screen configuration
3. Re-authenticate

### Attachments not sending

**Problem**: File path incorrect or file doesn't exist.

**Solution**:
- Use absolute paths (e.g., `C:\\Users\\...`)
- Verify file exists: `ls "C:\path\to\file.pdf"`
- Check file permissions

## Security Best Practices

### Credential Management

- **Never commit** `credentials.json`, `token.json`, or `.env` to version control
- **Add to .gitignore**:
  ```
  credentials.json
  token.json
  .env
  logs/
  ```

- **Rotate credentials** monthly
- **Use separate accounts** for development and production

### Approval Workflow

- **Always require approval** for:
  - Emails to new contacts
  - Emails with attachments
  - Bulk emails (multiple recipients)
  - Emails with financial information

- **Auto-approve only** for:
  - Single recipient
  - Known contacts
  - Non-sensitive content

### Monitoring

- **Review logs daily** for unexpected activity
- **Check approval queue** regularly
- **Set up alerts** for errors (optional)

## Development

### Building

```bash
npm run build
```

### Development Mode (Watch)

```bash
npm run dev
```

### Testing

```bash
npm test
```

### Project Structure

```
gmail-mcp/
├── src/
│   ├── index.ts           # Main MCP server
│   ├── auth.ts            # OAuth authentication
│   └── test.ts            # Integration tests
├── dist/                  # Compiled JavaScript
├── logs/                  # Server logs
├── credentials.json       # Google OAuth credentials (gitignored)
├── token.json            # OAuth token (gitignored)
├── .env                  # Environment variables (gitignored)
├── package.json
├── tsconfig.json
└── README.md
```

## API Reference

### Gmail Search Query Syntax

Full Gmail search syntax is supported:

- **From/To**: `from:user@example.com`, `to:user@example.com`
- **Subject**: `subject:"exact phrase"`, `subject:keyword`
- **Date**: `after:2026/01/01`, `before:2026/12/31`, `newer_than:7d`, `older_than:30d`
- **Attachments**: `has:attachment`, `filename:pdf`
- **Labels**: `label:inbox`, `label:important`
- **Status**: `is:unread`, `is:read`, `is:starred`
- **Boolean**: `OR`, `-` (NOT), `AND` (implicit)

**Examples**:
```
from:client@example.com subject:invoice after:2026/01/01
has:attachment is:unread
subject:(urgent OR important) -label:spam
```

### Rate Limit Details

**Gmail API Quotas** (Google default):
- Per-user per-second: 250
- Per-project per-second: 250
- Per-project per-day: 1,000,000,000

**MCP Server Limits** (configurable):
- Per-minute: 60
- Per-day: 10,000

## Support

### Resources
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)

### Common Issues
- Check logs in `logs/` directory
- Review audit trail in `AI_Employee_Vault/Logs/`
- Verify OAuth token: `node dist/auth.js --verify`

## License

MIT

## Author

Personal AI Employee Team

---

**Version**: 1.0.0
**Last Updated**: 2026-01-12
