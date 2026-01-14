# MCP Servers for Personal AI Employee

Production-ready Model Context Protocol (MCP) servers for Gmail, LinkedIn, and Xero integration with OAuth 2.0, Human-in-the-Loop approval workflows, and comprehensive automation capabilities.

## Project Overview

This project provides three enterprise-grade MCP servers designed for the Personal AI Employee hackathon:

### 1. Gmail MCP Server
- **Purpose**: Email automation with human oversight
- **Features**: Send, read, search, draft emails with attachments
- **Security**: OAuth 2.0, rate limiting, HITL approval, audit logging
- **Integration**: Seamless Obsidian vault integration

### 2. LinkedIn MCP Server
- **Purpose**: Business automation and lead generation
- **Features**: Create posts, generate from templates, track analytics
- **Security**: OAuth 2.0, mandatory approval for all posts, content logging
- **Templates**: 5 pre-built templates for common business posts

### 3. Xero MCP Server (Official)
- **Purpose**: Accounting automation and financial management
- **Features**: 40+ tools for invoices, reports, contacts, payments, payroll
- **Security**: OAuth 2.0, official Xero API integration, audit logging
- **Integration**: Full Xero accounting system automation
- **Repository**: https://github.com/XeroAPI/xero-mcp-server

All servers are production-ready with:
- Comprehensive error handling and retry logic
- Rate limiting to prevent quota exhaustion
- Detailed audit logging with PII redaction
- Full integration with Obsidian vault workflow
- MCP standard compliance for Claude Code

---

## Quick Start

### Prerequisites
- Node.js 20.0.0+
- Google Cloud account (for Gmail)
- LinkedIn Developer account
- Claude Code subscription

### Installation

```bash
# Clone or navigate to mcp-servers directory
cd "C:\Users\Najma-LP\Desktop\My Vault\mcp-servers"

# Install Gmail MCP
cd gmail-mcp
npm install
npm run build

# Install LinkedIn MCP
cd ../linkedin-mcp
npm install
npm run build
```

### Configuration

Follow the comprehensive setup guide:
```bash
# Read the setup guide
cat MCP_SETUP_GUIDE.md
```

**Estimated setup time**: 60-90 minutes

---

## Project Structure

```
mcp-servers/
├── gmail-mcp/
│   ├── src/
│   │   ├── index.ts           # Main MCP server implementation
│   │   ├── auth.ts            # OAuth authentication flow
│   │   └── test.ts            # Integration tests
│   ├── dist/                  # Compiled JavaScript (generated)
│   ├── logs/                  # Server logs (generated)
│   ├── credentials.json       # Google OAuth credentials (gitignored)
│   ├── token.json            # OAuth access token (gitignored)
│   ├── .env                  # Environment variables (gitignored)
│   ├── .env.example          # Environment template
│   ├── package.json          # Dependencies and scripts
│   ├── tsconfig.json         # TypeScript configuration
│   └── README.md             # Comprehensive documentation
│
├── linkedin-mcp/
│   ├── src/
│   │   ├── index.ts           # Main MCP server implementation
│   │   ├── auth.ts            # OAuth authentication flow
│   │   └── test.ts            # Integration tests
│   ├── dist/                  # Compiled JavaScript (generated)
│   ├── logs/                  # Server logs (generated)
│   ├── templates/             # Custom post templates (optional)
│   ├── linkedin_token.json    # OAuth access token (gitignored)
│   ├── .env                  # Environment variables (gitignored)
│   ├── .env.example          # Environment template
│   ├── package.json          # Dependencies and scripts
│   ├── tsconfig.json         # TypeScript configuration
│   └── README.md             # Comprehensive documentation
│
├── MCP_SETUP_GUIDE.md         # Complete setup instructions
├── example-mcp-config.json    # Claude Code MCP configuration
├── .gitignore                 # Security: never commit credentials
└── README.md                  # This file
```

---

## Features

### Gmail MCP Server

#### Core Operations
- **Send Emails**: Full support for HTML/plain text, CC/BCC, attachments
- **Read Emails**: Filter by labels, search queries, date ranges
- **Search Emails**: Full Gmail search syntax support
- **Draft Emails**: Create drafts for review before sending
- **Profile Info**: Account information and statistics

#### Security Features
- **OAuth 2.0**: Industry-standard authentication
- **Token Refresh**: Automatic token renewal
- **Rate Limiting**: 60 requests/minute, 10,000/day
- **Approval Workflow**: Human review before sending
- **Audit Logging**: Comprehensive JSON logs with PII redaction
- **Auto-Approval**: Optional, configurable for single-recipient emails

#### MCP Tools
- `gmail_send_email` - Send email (creates approval request)
- `gmail_read_emails` - Read inbox with filtering
- `gmail_search_emails` - Search using Gmail syntax
- `gmail_draft_email` - Create draft
- `gmail_get_profile` - Get account information

### LinkedIn MCP Server

#### Core Operations
- **Create Posts**: Text and media posts to LinkedIn
- **Generate Posts**: AI-assisted generation from templates
- **Post Analytics**: Track engagement (likes, comments, shares)
- **Profile Info**: LinkedIn account information
- **Template Library**: 5 pre-built business templates

#### Post Templates
1. **Service Announcement**: New products/services
2. **Achievement/Milestone**: Celebrate company wins
3. **Thought Leadership**: Share industry insights
4. **Behind the Scenes**: Company culture stories
5. **Customer Success**: Showcase results and testimonials

#### Security Features
- **OAuth 2.0**: Secure LinkedIn authentication
- **Mandatory Approval**: All posts require human review
- **Rate Limiting**: 100 requests/hour, 500/day
- **Content Logging**: Full audit trail (content redacted)
- **Public Safety**: Posts are permanent, extra caution enforced

#### MCP Tools
- `linkedin_create_post` - Create post (creates approval request)
- `linkedin_generate_post` - Generate from template
- `linkedin_list_templates` - List available templates
- `linkedin_get_profile` - Get profile information
- `linkedin_get_post_analytics` - Get post engagement stats

---

## Integration

### Claude Code Configuration

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
    },
    "linkedin": {
      "command": "node",
      "args": ["C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\linkedin-mcp\\dist\\index.js"],
      "env": {
        "VAULT_PATH": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault",
        "LINKEDIN_CLIENT_ID": "your-linkedin-client-id",
        "LINKEDIN_CLIENT_SECRET": "your-linkedin-client-secret",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Obsidian Vault Integration

Both servers integrate seamlessly with the Obsidian vault structure:

```
AI_Employee_Vault/
├── Pending_Approval/          # Approval requests created here
│   ├── EMAIL_email_send_*.md
│   └── LINKEDIN_linkedin_post_*.md
│
├── Approved/                  # Move files here to approve
│
├── Rejected/                  # Move files here to reject
│
└── Logs/                      # Audit logs written here
    └── actions_YYYY-MM-DD.json
```

**Workflow:**
1. AI Employee creates approval request → `/Pending_Approval`
2. Human reviews request
3. Move to `/Approved` (approve) or `/Rejected` (reject)
4. Approval processor executes approved actions
5. All actions logged to `/Logs`

---

## Human-in-the-Loop (HITL) Workflow

### Why HITL?

Both Gmail and LinkedIn involve **public communication** representing you or your business. HITL provides:
- **Safety**: Catch errors before they go public
- **Quality Control**: Ensure content meets standards
- **Compliance**: Legal/regulatory review when needed
- **Brand Protection**: Maintain consistent voice and messaging

### Approval Process

#### 1. Action Requested
```javascript
// In Claude Code
"Send an email to client@example.com about the invoice"
```

#### 2. Approval File Created
```markdown
---
type: approval_request
action: Send Email
status: pending
priority: medium
---

# Email Approval Request

**To:** client@example.com
**Subject:** Invoice #12345

## Email Body
```
Please find attached your invoice for January 2026.
```

## To Approve
Move this file to /Approved folder.
```

#### 3. Human Review
- Read email content
- Check recipients
- Verify attachments
- Review tone and accuracy

#### 4. Approval Decision
- **Approve**: `move file to /Approved/`
- **Reject**: `move file to /Rejected/` (add reason comment)

#### 5. Execution
- Approval processor detects approved file
- Executes action via MCP
- Logs result to `/Logs`

#### 6. Audit Trail
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "gmail_send_email",
  "result": "success",
  "approved_by": "human",
  "messageId": "abc123"
}
```

---

## Security Best Practices

### Credential Management

**NEVER commit these files to git:**
- `credentials.json`
- `token.json`
- `linkedin_token.json`
- `.env`

**Always:**
- Use `.gitignore` (provided)
- Rotate credentials every 3-6 months
- Use separate credentials for dev/production
- Store backups securely (password manager)

### Approval Guidelines

**Always require approval for:**
- Emails to new contacts
- Emails with attachments
- Bulk emails (multiple recipients)
- All LinkedIn posts (no exceptions)
- Financial or legal content

**Optional auto-approval (Gmail only):**
- Single recipient
- Known contacts
- Non-sensitive content
- Set `AUTO_APPROVE=true` cautiously

### Monitoring

- Review logs daily: `AI_Employee_Vault/Logs/`
- Check approval queue regularly: `Pending_Approval/`
- Monitor error logs: `mcp-servers/*/logs/`
- Set up alerts for failures (optional)

---

## Usage Examples

### Example 1: Send Invoice Email

**Claude Code:**
```
Send an email to john@client.com with the subject "January Invoice"
and attach the file C:\Users\...\invoice-jan-2026.pdf
```

**Result:**
1. Approval request created in `/Pending_Approval`
2. You review and approve
3. Email sent via Gmail
4. Action logged

### Example 2: Read Important Emails

**Claude Code:**
```
Check my Gmail for any important unread emails from clients
```

**Result:**
1. MCP server queries Gmail
2. Returns list of unread, important emails
3. No approval needed (read-only)

### Example 3: Create LinkedIn Post

**Claude Code:**
```
Create a LinkedIn post announcing our new AI automation service.
Use the service announcement template.
```

**Result:**
1. Post generated from template
2. Approval request created
3. You review post content
4. Approve or reject
5. If approved, post published to LinkedIn
6. Analytics tracked

### Example 4: Customer Success Story

**Claude Code:**
```
Generate a LinkedIn customer success post:
- Customer: Acme Corp
- Result: Saved 50 hours per week
- Solution: Our AI Employee
- Include testimonial: "Game-changer for our business"
```

**Result:**
1. Post generated using customer_success template
2. Formatted with emojis and hashtags
3. Approval request created
4. You review and approve
5. Published to LinkedIn

---

## Troubleshooting

### Common Issues

#### Gmail: "Gmail client not initialized"
**Solution**: Re-authenticate
```bash
cd mcp-servers/gmail-mcp
node dist/auth.js
```

#### LinkedIn: "Insufficient scope"
**Solution**: Add `w_member_social` scope in LinkedIn Developer Portal, then re-authenticate

#### MCP: Servers not appearing in Claude Code
**Solution**:
1. Check `mcp.json` syntax (no trailing commas)
2. Verify paths are absolute
3. Restart Claude Code
4. Check Claude Code logs

#### Rate Limit Exceeded
**Solution**: Wait (1 minute for Gmail, 1 hour for LinkedIn), then retry

### Getting Help

1. **Check logs**: `mcp-servers/*/logs/`
2. **Read READMEs**: Each server has detailed troubleshooting section
3. **Review setup guide**: `MCP_SETUP_GUIDE.md`
4. **Check audit logs**: `AI_Employee_Vault/Logs/`

---

## Development

### Building

```bash
# Gmail MCP
cd gmail-mcp
npm run build

# LinkedIn MCP
cd linkedin-mcp
npm run build
```

### Testing

```bash
# Gmail MCP
cd gmail-mcp
npm test

# LinkedIn MCP
cd linkedin-mcp
npm test
```

### Development Mode (Watch)

```bash
# Auto-rebuild on changes
npm run dev
```

---

## Architecture

### Technology Stack
- **Language**: TypeScript 5.3+
- **Runtime**: Node.js 20.0+
- **MCP SDK**: @modelcontextprotocol/sdk 0.5+
- **Gmail API**: googleapis 133+
- **HTTP Client**: axios 1.6+
- **Logging**: winston 3.11+

### Design Patterns
- **Singleton**: Single client instance per server
- **Retry with Backoff**: Exponential backoff for failures
- **Rate Limiting**: Token bucket algorithm
- **Approval Workflow**: File-based state machine
- **Audit Logging**: Structured JSON logging

### MCP Protocol
Both servers fully implement MCP specification:
- Server initialization
- Tool discovery (`ListToolsRequest`)
- Tool execution (`CallToolRequest`)
- Structured responses
- Error handling
- Stdio transport

---

## Hackathon Requirements

### Silver Tier Requirements Met

✅ **One working MCP server** - TWO servers provided (Gmail + LinkedIn)
✅ **OAuth 2.0 authentication** - Both servers implemented
✅ **HITL approval workflow** - Fully integrated with Obsidian vault
✅ **Attachment support** - Gmail supports attachments (invoices, reports)
✅ **Rate limiting** - Both servers implement rate limiting
✅ **Error handling** - Comprehensive retry logic
✅ **Audit logging** - JSON logs with PII redaction
✅ **Documentation** - Extensive READMEs and setup guide

### Beyond Requirements

🚀 **Template System** - LinkedIn has 5 business post templates
🚀 **Auto-Approval** - Optional configurable auto-approval
🚀 **Analytics** - LinkedIn post engagement tracking
🚀 **Search** - Gmail advanced search with full query syntax
🚀 **Drafts** - Gmail draft creation
🚀 **Profile Info** - Account information for both services

---

## Next Steps for Silver Tier

These MCP servers are the foundation. Now create the Silver Tier agent skills:

1. **email-sender skill** (3-4 hours)
   - High-level skill that uses Gmail MCP
   - Template support for common emails
   - Integration with task-processor

2. **linkedin-poster skill** (4-6 hours)
   - High-level skill that uses LinkedIn MCP
   - Content generation and template selection
   - Scheduling support

3. **approval-processor skill** (3-4 hours)
   - Automates HITL workflow
   - Watches `/Pending_Approval` folder
   - Executes approved actions via MCP
   - Handles rejections

4. **scheduler-manager skill** (2-3 hours)
   - Schedules approval processor (every 5 minutes)
   - Schedules dashboard updates (hourly)
   - Cross-platform (Windows Task Scheduler / cron)

**Total**: 12-17 hours to complete Silver Tier

---

## Resources

### Documentation
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [LinkedIn API Docs](https://docs.microsoft.com/en-us/linkedin/)
- [MCP Specification](https://modelcontextprotocol.io)
- [OAuth 2.0 Guide](https://oauth.net/2/)

### Project Files
- `gmail-mcp/README.md` - Gmail server documentation
- `linkedin-mcp/README.md` - LinkedIn server documentation
- `MCP_SETUP_GUIDE.md` - Complete setup instructions
- `example-mcp-config.json` - Claude Code configuration

### Support
- GitHub Issues (if hosted on GitHub)
- Hackathon Discord/Slack
- Wednesday research meetings (10 PM, Zoom)

---

## License

MIT License - Free to use, modify, and distribute.

## Contributors

Personal AI Employee Team - Hackathon 0 (January 2026)

---

## Acknowledgments

Built for the Personal AI Employee Hackathon using:
- Claude Code by Anthropic
- Model Context Protocol (MCP)
- Google Gmail API
- LinkedIn API
- Obsidian knowledge management

Special thanks to the Panaversity community for the hackathon opportunity!

---

**Status**: Production Ready ✅
**Version**: 1.0.0
**Last Updated**: 2026-01-12

---

## Quick Reference

### Start Servers
```bash
# Gmail MCP
cd gmail-mcp && npm start

# LinkedIn MCP
cd linkedin-mcp && npm start
```

### Authenticate
```bash
# Gmail
cd gmail-mcp && node dist/auth.js

# LinkedIn
cd linkedin-mcp && node dist/auth.js
```

### Test
```bash
# Gmail
cd gmail-mcp && npm test

# LinkedIn
cd linkedin-mcp && npm test
```

### Logs
- Server logs: `mcp-servers/*/logs/`
- Audit logs: `AI_Employee_Vault/Logs/`
- Approval queue: `AI_Employee_Vault/Pending_Approval/`

---

**Ready to automate your business with AI employees!** 🚀
