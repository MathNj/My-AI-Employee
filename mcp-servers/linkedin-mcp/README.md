# LinkedIn MCP Server

Production-ready Model Context Protocol (MCP) server for LinkedIn integration with OAuth 2.0 authentication, business automation, and Human-in-the-Loop approval workflows.

## Features

### Core Capabilities
- **Create Posts**: Publish text and media posts to LinkedIn
- **Post Templates**: Pre-built templates for common business posts
- **Generate Posts**: AI-assisted post generation from templates
- **Post Analytics**: Track likes, comments, shares, impressions
- **Profile Info**: Get LinkedIn profile information

### Security & Safety
- **OAuth 2.0 Authentication**: Secure LinkedIn authentication
- **Human-in-the-Loop (HITL)**: Approval workflow for all posts
- **Rate Limiting**: Prevents API quota exhaustion (100/hour, 500/day)
- **Audit Logging**: Comprehensive logging with content redaction
- **Retry Logic**: Exponential backoff for transient failures

### Business Automation
- **Service Announcements**: Template for new service/product launches
- **Achievement Posts**: Celebrate milestones and achievements
- **Thought Leadership**: Share insights and perspectives
- **Behind the Scenes**: Company culture and team stories
- **Customer Success**: Showcase customer results and testimonials

### Integration
- **Obsidian Vault Integration**: Creates approval files in `/Pending_Approval`
- **Audit Trail**: JSON logs in `/Logs` folder with timestamps
- **MCP Standard**: Compatible with Claude Code and other MCP clients

## Installation

### Prerequisites
- Node.js 20.0.0 or higher
- LinkedIn Developer account
- OAuth 2.0 app credentials from LinkedIn

### Setup Steps

#### 1. Install Dependencies
```bash
cd mcp-servers/linkedin-mcp
npm install
```

#### 2. Build TypeScript
```bash
npm run build
```

#### 3. Create LinkedIn Developer App

**A. Register as LinkedIn Developer**
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Sign in with your LinkedIn account
3. Accept Developer Program Terms

**B. Create App**
1. Click "Create app"
2. Fill in app details:
   - **App name**: Personal AI Employee
   - **LinkedIn Page**: Your company page or personal profile
   - **Privacy policy URL**: Required (can be placeholder for development)
   - **App logo**: Optional
3. Click "Create app"

**C. Configure OAuth**
1. Go to "Auth" tab
2. Add **Redirect URLs**:
   ```
   http://localhost:3000/auth/linkedin/callback
   ```
3. Note your **Client ID** and **Client Secret**
4. Request access to **Product**: "Sign In with LinkedIn using OpenID Connect"
5. Add **OAuth 2.0 scopes**:
   - `openid`
   - `profile`
   - `email`
   - `w_member_social` (for posting)

**D. Verification** (for production)
- LinkedIn requires app verification for production use
- During development, use your own account for testing
- For verification, provide:
  - App description
  - Use case explanation
  - Privacy policy
  - Terms of service

#### 4. Set Up Environment Variables

Create `.env` file:
```bash
# LinkedIn MCP Server Configuration

# LinkedIn OAuth Credentials
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:3000/auth/linkedin/callback

# Paths
VAULT_PATH=C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault
LINKEDIN_TOKEN_PATH=./linkedin_token.json
TEMPLATES_PATH=./templates
LOG_PATH=./logs

# Auto-Approval (CAUTION: Posts are public)
AUTO_APPROVE=false

# Logging
LOG_LEVEL=info
```

#### 5. Authenticate with LinkedIn

Run the authentication script:
```bash
node dist/auth.js
```

This will:
1. Start local server on port 3000
2. Open browser to LinkedIn OAuth
3. Ask you to authorize the application
4. Save access token to `linkedin_token.json`

**First-Time Setup:**
1. Browser opens to LinkedIn authorization page
2. Click "Allow" to grant permissions
3. Browser redirects to localhost
4. Token saved automatically
5. Server displays success message

#### 6. Test the Server

```bash
npm test
```

This verifies:
- OAuth token is valid
- LinkedIn API connection works
- Profile information retrieved
- Templates loaded

## Usage

### Starting the Server

```bash
npm start
```

Or use with Claude Code (see Configuration section below).

### Available Tools

#### 1. linkedin_create_post

Create and publish a LinkedIn post (requires approval).

**Example:**
```json
{
  "text": "🚀 Excited to announce our new AI automation service! \n\nWe're helping businesses save 85% on operational costs by implementing AI employees. \n\nInterested? Let's connect! \n\n#AI #Automation #Business",
  "visibility": "PUBLIC",
  "media": [
    {
      "url": "https://example.com/image.jpg",
      "title": "AI Automation Dashboard",
      "description": "Our new service dashboard"
    }
  ]
}
```

**Response (Pending Approval):**
```json
{
  "status": "pending_approval",
  "message": "LinkedIn post requires approval. Approval request created.",
  "approvalFile": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault\\Pending_Approval\\LINKEDIN_linkedin_post_2026-01-12T10-30-00-000Z.md",
  "instructions": "Move the approval file to /Approved folder to publish the post.",
  "preview": "🚀 Excited to announce our new AI automation service! \n\nWe're helping businesses save 85% on operational costs..."
}
```

**Response (Published):**
```json
{
  "status": "success",
  "message": "LinkedIn post published successfully",
  "postId": "urn:li:share:7154321098765432",
  "postUrl": "https://www.linkedin.com/feed/update/urn:li:share:7154321098765432"
}
```

#### 2. linkedin_generate_post

Generate a post from a template.

**Example (Service Announcement):**
```json
{
  "template": "service_announcement",
  "data": {
    "service": "AI-Powered Email Automation",
    "description": "Our new service automatically processes emails, drafts responses, and manages your inbox - saving you 10+ hours per week.",
    "benefits": "✅ 90% faster email response time\n✅ Zero inbox anxiety\n✅ 24/7 email monitoring",
    "callToAction": "DM me to learn more!",
    "hashtags": "#AI #Productivity #EmailAutomation"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "template": "service_announcement",
  "generatedText": "🚀 Exciting News!\n\nWe're thrilled to announce AI-Powered Email Automation!\n\nOur new service automatically processes emails, drafts responses, and manages your inbox - saving you 10+ hours per week.\n\n✅ 90% faster email response time\n✅ Zero inbox anxiety\n✅ 24/7 email monitoring\n\nDM me to learn more!\n\n#AI #Productivity #EmailAutomation",
  "nextStep": "Use linkedin_create_post to publish this content"
}
```

**Example (Achievement):**
```json
{
  "template": "achievement",
  "data": {
    "achievement": "we've reached 1,000 users on our AI Employee platform",
    "details": "In just 3 months, businesses using our platform have saved over 50,000 hours of manual work. This is just the beginning!",
    "gratitude": "Huge thanks to our amazing early adopters who trusted us and provided invaluable feedback!",
    "hashtags": "#Startup #Milestone #AI"
  }
}
```

**Example (Thought Leadership):**
```json
{
  "template": "thought_leadership",
  "data": {
    "title": "The Future of Work: AI Employees",
    "insight": "In 2026, businesses aren't asking 'Should we use AI?' but 'How many AI employees should we hire?' \n\nThe shift from AI as a tool to AI as a workforce is happening faster than most predicted. Companies that adapt now will have a 5-year advantage.",
    "perspective": "The key isn't replacing humans - it's augmenting them. AI handles repetitive tasks, humans focus on creativity and strategy.",
    "hashtags": "#FutureOfWork #AI #Leadership"
  }
}
```

#### 3. linkedin_list_templates

List all available post templates.

**Example:**
```json
{}
```

**Response:**
```json
{
  "status": "success",
  "templates": [
    {
      "name": "service_announcement",
      "title": "Service Announcement",
      "description": "Template for service announcement"
    },
    {
      "name": "achievement",
      "title": "Achievement/Milestone",
      "description": "Template for achievement/milestone"
    },
    {
      "name": "thought_leadership",
      "title": "Thought Leadership",
      "description": "Template for thought leadership"
    },
    {
      "name": "behind_the_scenes",
      "title": "Behind the Scenes",
      "description": "Template for behind the scenes"
    },
    {
      "name": "customer_success",
      "title": "Customer Success Story",
      "description": "Template for customer success story"
    }
  ]
}
```

#### 4. linkedin_get_profile

Get LinkedIn profile information.

**Example:**
```json
{}
```

**Response:**
```json
{
  "status": "success",
  "profile": {
    "id": "AbCdEfGhIj",
    "firstName": "John",
    "lastName": "Doe",
    "profileUrl": "https://www.linkedin.com/in/johndoe"
  }
}
```

#### 5. linkedin_get_post_analytics

Get analytics for a published post.

**Example:**
```json
{
  "postId": "urn:li:share:7154321098765432"
}
```

**Response:**
```json
{
  "status": "success",
  "postId": "urn:li:share:7154321098765432",
  "analytics": {
    "likes": 127,
    "comments": 23,
    "shares": 15,
    "impressions": 3542
  }
}
```

## Post Templates

### Available Templates

#### 1. Service Announcement
Use for: New product/service launches, feature announcements

**Data Fields:**
- `service` (required): Service/product name
- `description` (required): What it does
- `benefits` (optional): Key benefits/features
- `callToAction` (optional): What should people do?
- `hashtags` (optional): Relevant hashtags

#### 2. Achievement/Milestone
Use for: Company milestones, awards, growth metrics

**Data Fields:**
- `achievement` (required): What was achieved
- `details` (required): Context and significance
- `gratitude` (optional): Thank you message
- `hashtags` (optional): Relevant hashtags

#### 3. Thought Leadership
Use for: Industry insights, trends, predictions

**Data Fields:**
- `title` (required): Post title/hook
- `insight` (required): Main insight or perspective
- `perspective` (optional): Additional context
- `hashtags` (optional): Relevant hashtags

#### 4. Behind the Scenes
Use for: Company culture, team stories, day-in-the-life

**Data Fields:**
- `company` (required): Company name
- `story` (required): The story/experience
- `details` (optional): Additional details
- `hashtags` (optional): Relevant hashtags

#### 5. Customer Success Story
Use for: Case studies, testimonials, results

**Data Fields:**
- `customerName` (required): Customer/client name
- `result` (required): Result achieved
- `solution` (required): Your solution used
- `testimonial` (optional): Customer quote
- `callToAction` (optional): Next step for readers
- `hashtags` (optional): Relevant hashtags

### Creating Custom Templates

Edit `src/index.ts` and add to `POST_TEMPLATES`:

```typescript
my_custom_template: {
  title: 'My Custom Template',
  template: (data: any) => `
${data.customField1}

${data.customField2}

${data.hashtags || '#Default'}
  `.trim(),
},
```

## Human-in-the-Loop Workflow

### Why HITL for LinkedIn?

LinkedIn posts are **public and permanent**. They represent your professional brand. HITL ensures:
- No accidental posts
- Content quality control
- Brand voice consistency
- Legal/compliance review

### Approval Process

1. **Post Generated**: Template or custom content created
2. **Approval File Created**: Server creates markdown file in `/Pending_Approval`
3. **Human Review**: You review content, tone, timing
4. **Approval Decision**:
   - **Approve**: Move file to `/Approved` folder
   - **Reject**: Move file to `/Rejected` folder (with reason comment)
5. **Publishing**: Approval processor detects approved file and publishes
6. **Logging**: Post logged to `/Logs` with analytics tracking

### Approval File Format

```markdown
---
type: approval_request
action: Create LinkedIn Post
category: linkedin_post
created: 2026-01-12T10:30:00Z
expires: 2026-01-13T10:30:00Z
status: pending
priority: high
---

# LinkedIn Post Approval Request

## Action
Create LinkedIn Post

## Post Content
```
🚀 Exciting News!

We're thrilled to announce AI-Powered Email Automation!

Our new service automatically processes emails, drafts responses, and manages your inbox - saving you 10+ hours per week.

✅ 90% faster email response time
✅ Zero inbox anxiety
✅ 24/7 email monitoring

DM me to learn more!

#AI #Productivity #EmailAutomation
```

## Visibility
PUBLIC

## Reason
LinkedIn posts require human approval before publishing

## Preview
This post will be published to your LinkedIn profile and visible to the public.

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with a reason comment.

---
*Created by LinkedIn MCP Server*
*Request ID: 2026-01-12T10-30-00-000Z*
```

## Best Practices

### Posting Strategy

**Frequency:**
- 3-5 posts per week (optimal engagement)
- Don't post more than once per day
- Schedule posts for peak times (Tue-Thu, 8am-10am)

**Content Mix:**
- 40% Thought leadership
- 30% Company updates
- 20% Customer success
- 10% Personal/behind-the-scenes

**Engagement:**
- Respond to comments within 24 hours
- Ask questions to encourage discussion
- Tag relevant people/companies (sparingly)

### Writing Tips

**Hooks (First 2 Lines):**
- Start with emoji + bold statement
- Ask a provocative question
- Share a surprising statistic
- Make a bold prediction

**Structure:**
- Short paragraphs (1-2 sentences)
- Use line breaks liberally
- Bullet points for lists
- 3-4 hashtags maximum

**Call to Action:**
- "What's your experience? Comment below!"
- "DM me to learn more"
- "Link in comments"
- "Share if you agree"

**Hashtags:**
- Mix of broad (#AI) and specific (#EmailAutomation)
- 3-5 hashtags total
- Place at end of post
- Research trending hashtags in your industry

### Content Guidelines

**Do:**
- Share genuine insights
- Tell authentic stories
- Provide value (education, inspiration, entertainment)
- Be conversational
- Show personality

**Don't:**
- Over-promote (80/20 rule: 80% value, 20% promotion)
- Use corporate jargon
- Write long paragraphs
- Post political/controversial content (unless it's your niche)
- Use more than 2-3 emojis per post

## Rate Limiting

The server implements rate limiting to prevent quota exhaustion:

- **Per Hour**: 100 requests
- **Per Day**: 500 requests

LinkedIn API limits:
- **Posts per day**: ~50-100 (unofficial soft limit)
- **API calls per day**: Variable by app verification status

## Error Handling

### Retry Logic

The server automatically retries failed requests with exponential backoff:
- **Attempt 1**: Immediate
- **Attempt 2**: 1 second delay
- **Attempt 3**: 2 second delay
- **Max Attempts**: 3

### Common Errors

1. **Authentication Error (401)**: Token expired
   - **Solution**: Re-run `node dist/auth.js`

2. **Permission Error (403)**: Missing scopes
   - **Solution**: Add `w_member_social` scope in LinkedIn Developer Portal

3. **Rate Limit Error (429)**: Too many requests
   - **Solution**: Wait 1 hour and retry

4. **Invalid Post Content**: Post violates LinkedIn policies
   - **Solution**: Review content, ensure compliance with LinkedIn guidelines

## Logging

### Log Files

- **Error Log**: `logs/linkedin-mcp-error.log` (errors only)
- **General Log**: `logs/linkedin-mcp.log` (all events)
- **Audit Log**: `AI_Employee_Vault/Logs/actions_YYYY-MM-DD.json`

### Audit Log Format

```json
{
  "timestamp": "2026-01-12T10:30:00.000Z",
  "action": "linkedin_create_post",
  "type": "linkedin_post",
  "result": "success",
  "actor": "linkedin-mcp-server",
  "data": {
    "postId": "urn:li:share:7154321098765432",
    "postUrl": "https://www.linkedin.com/feed/update/urn:li:share:7154321098765432",
    "text": "[REDACTED]"
  }
}
```

**Content Redaction**: Post content is redacted in logs for privacy.

## Configuration

### Claude Code Integration

Add to `~/.config/claude-code/mcp.json` (Mac/Linux) or `%APPDATA%\Claude\mcp.json` (Windows):

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": ["C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\linkedin-mcp\\dist\\index.js"],
      "env": {
        "VAULT_PATH": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault",
        "LINKEDIN_CLIENT_ID": "your-client-id",
        "LINKEDIN_CLIENT_SECRET": "your-client-secret",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LINKEDIN_CLIENT_ID` | LinkedIn OAuth client ID | - | Yes |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn OAuth client secret | - | Yes |
| `LINKEDIN_REDIRECT_URI` | OAuth redirect URI | `http://localhost:3000/auth/linkedin/callback` | No |
| `VAULT_PATH` | Obsidian vault path | Current directory | Yes |
| `LINKEDIN_TOKEN_PATH` | Token JSON path | `./linkedin_token.json` | No |
| `TEMPLATES_PATH` | Templates directory | `./templates` | No |
| `LOG_PATH` | Log directory path | `./logs` | No |
| `AUTO_APPROVE` | Enable auto-approval (CAUTION) | `false` | No |
| `LOG_LEVEL` | Logging level | `info` | No |

## Troubleshooting

### "LinkedIn client not initialized"

**Problem**: OAuth token is missing or invalid.

**Solution**:
```bash
node dist/auth.js
```

### "Permission denied" / "Insufficient scope"

**Problem**: App doesn't have required permissions.

**Solution**:
1. Go to LinkedIn Developer Portal
2. Navigate to your app > "Products" tab
3. Request access to "Sign In with LinkedIn using OpenID Connect"
4. Add scope: `w_member_social`
5. Re-authenticate

### Post not appearing on LinkedIn

**Problem**: Post published but not visible.

**Solution**:
- LinkedIn has post moderation - posts may take 5-10 minutes to appear
- Check if account is restricted or flagged
- Verify post doesn't violate LinkedIn content policies
- Check `postUrl` in response - try accessing directly

### "App not verified"

**Problem**: LinkedIn requires app verification for production.

**Solution** (Development):
- Use your own account for testing
- Add account as test user in Developer Portal

**Solution** (Production):
- Submit app for verification in Developer Portal
- Provide: app description, use case, privacy policy, terms of service
- Verification typically takes 1-2 weeks

### Token expires frequently

**Problem**: Access token expires every 60 days.

**Solution**:
- Implement token refresh (advanced)
- Re-authenticate when needed
- Consider using refresh tokens (if available in your OAuth setup)

## Security Best Practices

### Credential Management

- **Never commit** `linkedin_token.json` or `.env` to version control
- **Add to .gitignore**:
  ```
  linkedin_token.json
  .env
  logs/
  ```

- **Rotate credentials** every 3-6 months
- **Use separate apps** for development and production

### Content Approval

- **Always review posts** before publishing
- **Never enable auto-approval** for public posts
- **Have multiple reviewers** for company accounts
- **Check for typos, errors, broken links**

### Compliance

- **Follow LinkedIn User Agreement** and **Professional Community Policies**
- **Disclose AI usage** if required by your industry
- **Respect copyright** - only use original content or properly licensed media
- **Avoid spam** - no excessive posting or automated engagement

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
linkedin-mcp/
├── src/
│   ├── index.ts           # Main MCP server
│   ├── auth.ts            # OAuth authentication
│   └── test.ts            # Integration tests
├── dist/                  # Compiled JavaScript
├── logs/                  # Server logs
├── templates/             # Custom post templates (optional)
├── linkedin_token.json    # OAuth token (gitignored)
├── .env                   # Environment variables (gitignored)
├── package.json
├── tsconfig.json
└── README.md
```

## LinkedIn API Reference

### Content Policies

Review [LinkedIn Content Policies](https://www.linkedin.com/help/linkedin/answer/137368):
- No spam or misleading content
- No hate speech or harassment
- No adult content
- No infringement of intellectual property
- No fake news or misinformation

### API Limits

- **Posts per day**: ~50-100 (soft limit, varies)
- **Characters per post**: 3,000 (recommended: 1,300)
- **Hashtags per post**: 3-5 (recommended)
- **Mentions per post**: ~10 (recommended: 2-3)

### Media Support

- **Images**: JPEG, PNG (recommended: 1200x627px)
- **Videos**: MP4 (max: 10 minutes, 5GB)
- **Documents**: PDF, PPT, DOC (max: 100MB)

## Support

### Resources
- [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [LinkedIn Developer Portal](https://www.linkedin.com/developers/)

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
