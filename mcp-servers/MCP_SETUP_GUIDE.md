# MCP Servers Setup Guide

Complete guide for setting up Gmail and LinkedIn MCP servers for your Personal AI Employee.

## Overview

This guide covers:
1. Gmail MCP Server setup (OAuth 2.0 + HITL approval)
2. LinkedIn MCP Server setup (OAuth 2.0 + business automation)
3. Claude Code integration
4. Testing and verification

**Estimated Time**: 60-90 minutes

---

## Prerequisites

### Software Requirements
- [x] Node.js 20.0.0+ installed
- [x] TypeScript knowledge (basic)
- [x] Git installed
- [x] Claude Code subscription

### Account Requirements
- [ ] Google Cloud Platform account
- [ ] LinkedIn Developer account
- [ ] Gmail account (for testing)
- [ ] LinkedIn account (for posting)

---

## Part 1: Gmail MCP Server Setup

### Step 1: Google Cloud Configuration (15 min)

#### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" dropdown (top navigation)
3. Click "New Project"
4. Enter project name: `ai-employee-gmail`
5. Click "Create"

#### B. Enable Gmail API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click "Gmail API" in results
4. Click "Enable" button
5. Wait for API to enable (10-30 seconds)

#### C. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" (unless you have Google Workspace)
3. Click "Create"

**Fill in required fields:**
- **App name**: Personal AI Employee
- **User support email**: Your email
- **Developer contact**: Your email

**Add scopes** (click "Add or Remove Scopes"):
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.compose`

**Add test users**:
- Click "Add Users"
- Enter your Gmail address
- Click "Add"

**Save and continue through remaining screens** (leave defaults)

#### D. Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as application type
4. Name: `ai-employee-desktop`
5. Click "Create"
6. **Download JSON** - Click "Download JSON" button
7. Save as `credentials.json` in `mcp-servers/gmail-mcp/`

### Step 2: Gmail MCP Installation (10 min)

```bash
# Navigate to Gmail MCP directory
cd "C:\Users\Najma-LP\Desktop\My Vault\mcp-servers\gmail-mcp"

# Install dependencies
npm install

# Build TypeScript
npm run build
```

### Step 3: Environment Configuration (5 min)

Create `.env` file in `mcp-servers/gmail-mcp/`:

```bash
# Gmail MCP Server Configuration

# Google OAuth Credentials (from credentials.json)
GMAIL_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret-here
GMAIL_REDIRECT_URI=urn:ietf:wg:oauth:2.0:oob

# Paths (adjust if needed)
VAULT_PATH=C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
LOG_PATH=./logs

# Auto-Approval (keep false for safety)
AUTO_APPROVE=false

# Logging
LOG_LEVEL=info
```

**How to get CLIENT_ID and CLIENT_SECRET:**
1. Open downloaded `credentials.json`
2. Find `client_id` field
3. Find `client_secret` field
4. Copy values to `.env`

### Step 4: Authentication (10 min)

Create `src/auth.ts`:

```typescript
import { google } from 'googleapis';
import fs from 'fs/promises';
import readline from 'readline';
import dotenv from 'dotenv';

dotenv.config();

const SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.compose',
];

async function authenticate() {
  const oauth2Client = new google.auth.OAuth2(
    process.env.GMAIL_CLIENT_ID,
    process.env.GMAIL_CLIENT_SECRET,
    process.env.GMAIL_REDIRECT_URI
  );

  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });

  console.log('Authorize this app by visiting this url:', authUrl);

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const code = await new Promise<string>((resolve) => {
    rl.question('Enter the code from that page here: ', (answer) => {
      rl.close();
      resolve(answer);
    });
  });

  const { tokens } = await oauth2Client.getToken(code);
  await fs.writeFile('./token.json', JSON.stringify(tokens, null, 2));

  console.log('Token stored successfully!');
  console.log('You can now start the Gmail MCP server with: npm start');
}

authenticate().catch(console.error);
```

**Build and run authentication:**

```bash
# Build TypeScript
npm run build

# Run authentication
node dist/auth.js
```

**Follow the prompts:**
1. Browser opens to Google OAuth page
2. Select your Gmail account
3. Click "Allow" to grant permissions
4. Copy authorization code from browser
5. Paste code into terminal
6. Press Enter
7. Token saved to `token.json`

### Step 5: Test Gmail MCP (5 min)

```bash
npm test
```

**Expected output:**
```
Gmail MCP Server - Test Suite
------------------------------
✓ OAuth token valid
✓ Gmail API connection successful
✓ Profile retrieved: you@example.com
✓ Inbox access confirmed
✓ Logging functional

All tests passed!
```

---

## Part 2: LinkedIn MCP Server Setup

### Step 1: LinkedIn Developer Setup (20 min)

#### A. Register as Developer

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Sign in with your LinkedIn account
3. Click "Create app"

#### B. Create LinkedIn App

**App Information:**
- **App name**: Personal AI Employee
- **LinkedIn Page**: Select your company page or personal profile
  - If no page, create one: [Create Company Page](https://www.linkedin.com/company/setup/new/)
- **Privacy policy URL**:
  - For dev: Use `https://example.com/privacy` (placeholder)
  - For prod: Must be real URL
- **App logo**: Upload logo (optional but recommended)
- **Legal agreement**: Check box and accept

Click "Create app"

#### C. Configure App Settings

**Auth Tab:**
1. Click "Auth" tab
2. Add **Redirect URLs**:
   ```
   http://localhost:3000/auth/linkedin/callback
   ```
3. Click "Update"

**Note your credentials:**
- **Client ID**: Displayed at top of Auth tab
- **Client Secret**: Click "Show" to reveal, then copy

**Products Tab:**
1. Click "Products" tab
2. Request access to "Sign In with LinkedIn using OpenID Connect"
3. Click "Request access"
4. Fill out use case (if prompted):
   - **Use case**: Personal productivity automation
   - **Description**: AI employee for business automation

**Settings Tab:**
1. Verify app details
2. Add app description (recommended)

### Step 2: LinkedIn MCP Installation (10 min)

```bash
# Navigate to LinkedIn MCP directory
cd "C:\Users\Najma-LP\Desktop\My Vault\mcp-servers\linkedin-mcp"

# Install dependencies
npm install

# Build TypeScript
npm run build
```

### Step 3: Environment Configuration (5 min)

Create `.env` file in `mcp-servers/linkedin-mcp/`:

```bash
# LinkedIn MCP Server Configuration

# LinkedIn OAuth Credentials
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:3000/auth/linkedin/callback

# Paths
VAULT_PATH=C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault
LINKEDIN_TOKEN_PATH=./linkedin_token.json
TEMPLATES_PATH=./templates
LOG_PATH=./logs

# Auto-Approval (NEVER enable for production)
AUTO_APPROVE=false

# Logging
LOG_LEVEL=info
```

### Step 4: Authentication (10 min)

Create `src/auth.ts`:

```typescript
import express from 'express';
import axios from 'axios';
import fs from 'fs/promises';
import dotenv from 'dotenv';
import open from 'open';

dotenv.config();

const app = express();
const PORT = 3000;

const LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization';
const LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken';

const clientId = process.env.LINKEDIN_CLIENT_ID!;
const clientSecret = process.env.LINKEDIN_CLIENT_SECRET!;
const redirectUri = process.env.LINKEDIN_REDIRECT_URI!;

app.get('/auth/linkedin/callback', async (req, res) => {
  const { code } = req.query;

  if (!code) {
    res.send('Error: No authorization code received');
    return;
  }

  try {
    // Exchange code for access token
    const response = await axios.post(LINKEDIN_TOKEN_URL, null, {
      params: {
        grant_type: 'authorization_code',
        code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token, expires_in } = response.data;

    // Get user profile to get person URN
    const profileResponse = await axios.get('https://api.linkedin.com/v2/me', {
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    });

    const personUrn = `urn:li:person:${profileResponse.data.id}`;

    // Save token
    const tokenData = {
      access_token,
      expires_in,
      person_urn: personUrn,
      created_at: new Date().toISOString(),
    };

    await fs.writeFile('./linkedin_token.json', JSON.stringify(tokenData, null, 2));

    res.send(`
      <h1>Authentication Successful!</h1>
      <p>Your LinkedIn account is now connected.</p>
      <p>You can close this window and return to the terminal.</p>
    `);

    console.log('\n✓ Authentication successful!');
    console.log('Token saved to linkedin_token.json');
    console.log('You can now start the LinkedIn MCP server with: npm start');

    setTimeout(() => process.exit(0), 2000);
  } catch (error: any) {
    console.error('Authentication failed:', error.message);
    res.send(`<h1>Authentication Failed</h1><p>${error.message}</p>`);
  }
});

async function startAuth() {
  const authUrl = `${LINKEDIN_AUTH_URL}?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=openid%20profile%20email%20w_member_social`;

  app.listen(PORT, () => {
    console.log(`Auth server running on http://localhost:${PORT}`);
    console.log('\nOpening browser for LinkedIn authentication...');
    console.log('If browser does not open, visit this URL:');
    console.log(authUrl);

    open(authUrl);
  });
}

startAuth().catch(console.error);
```

**Install additional dependency:**

```bash
npm install express open
npm install --save-dev @types/express
```

**Build and run authentication:**

```bash
# Build TypeScript
npm run build

# Run authentication
node dist/auth.js
```

**Follow the prompts:**
1. Browser opens to LinkedIn authorization page
2. Click "Allow" to grant permissions
3. Browser redirects to success page
4. Token saved automatically
5. Terminal displays success message

### Step 5: Test LinkedIn MCP (5 min)

```bash
npm test
```

**Expected output:**
```
LinkedIn MCP Server - Test Suite
---------------------------------
✓ OAuth token valid
✓ LinkedIn API connection successful
✓ Profile retrieved: John Doe
✓ Templates loaded (5 templates)
✓ Logging functional

All tests passed!
```

---

## Part 3: Claude Code Integration

### Step 1: Configure MCP Settings

**Location:**
- **Windows**: `%APPDATA%\Claude\mcp.json`
- **Mac**: `~/.config/claude-code/mcp.json`
- **Linux**: `~/.config/claude-code/mcp.json`

**Create or edit `mcp.json`:**

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": [
        "C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\gmail-mcp\\dist\\index.js"
      ],
      "env": {
        "VAULT_PATH": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault",
        "GMAIL_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GMAIL_CLIENT_SECRET": "your-client-secret",
        "LOG_LEVEL": "info"
      }
    },
    "linkedin": {
      "command": "node",
      "args": [
        "C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\linkedin-mcp\\dist\\index.js"
      ],
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

**Important: Use absolute paths for:**
- `args`: Full path to compiled `index.js`
- `VAULT_PATH`: Full path to Obsidian vault

### Step 2: Restart Claude Code

```bash
# Close Claude Code completely
# Then restart

# Verify MCP servers loaded
# Look for messages like:
# "MCP server 'gmail' connected"
# "MCP server 'linkedin' connected"
```

### Step 3: Test Integration

**In Claude Code, try:**

```
Can you check my Gmail inbox for unread emails?
```

**Expected behavior:**
1. Claude Code invokes `gmail_read_emails` tool
2. Returns list of unread emails
3. No errors

**Test LinkedIn:**

```
Create a LinkedIn post announcing our new AI automation service.
```

**Expected behavior:**
1. Claude Code invokes `linkedin_generate_post` or `linkedin_create_post`
2. Creates approval file in `/Pending_Approval`
3. Returns approval instructions

---

## Part 4: Verification & Testing

### End-to-End Test: Email Workflow

**Test sending an email:**

1. **Request email send** (in Claude Code):
   ```
   Send an email to test@example.com with subject "Test Email"
   and body "This is a test from the AI Employee."
   ```

2. **Check approval file created**:
   ```bash
   ls "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Pending_Approval"
   ```

3. **Review approval file**:
   ```bash
   cat "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Pending_Approval\EMAIL_email_send_*.md"
   ```

4. **Approve by moving file**:
   ```bash
   move "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Pending_Approval\EMAIL_*.md" ^
        "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Approved\"
   ```

5. **Run approval processor** (manual for now):
   ```bash
   # Will be automated in approval-processor skill
   # For now, manually verify approval workflow
   ```

6. **Check logs**:
   ```bash
   cat "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Logs\actions_*.json"
   ```

### End-to-End Test: LinkedIn Workflow

**Test LinkedIn post:**

1. **Request post creation** (in Claude Code):
   ```
   Create a LinkedIn post using the achievement template.
   We just reached 100 users!
   ```

2. **Claude generates post** using `linkedin_generate_post`

3. **Claude creates approval** using `linkedin_create_post`

4. **Check approval file**:
   ```bash
   ls "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Pending_Approval"
   ```

5. **Review content** in approval file

6. **Approve if satisfied**:
   ```bash
   move "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Pending_Approval\LINKEDIN_*.md" ^
        "C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault\Approved\"
   ```

7. **Verify post on LinkedIn** (after approval processor runs)

---

## Troubleshooting

### Gmail Issues

**"Gmail client not initialized"**
```bash
# Re-authenticate
cd mcp-servers/gmail-mcp
node dist/auth.js
```

**"Token expired"**
- Server should auto-refresh
- If fails, re-authenticate

**"Permission denied"**
- Check OAuth scopes in Google Cloud Console
- Verify test user added

### LinkedIn Issues

**"LinkedIn client not initialized"**
```bash
# Re-authenticate
cd mcp-servers/linkedin-mcp
node dist/auth.js
```

**"Insufficient scope"**
- Verify `w_member_social` scope requested
- Re-authenticate after adding scope

**"App not verified"**
- Use your own account for testing
- Submit for verification for production

### MCP Connection Issues

**MCP servers not appearing in Claude Code**
- Check `mcp.json` path is correct
- Verify JSON syntax (no trailing commas)
- Restart Claude Code completely
- Check Claude Code logs

**"Command not found" in mcp.json**
- Use absolute paths, not relative
- Verify `dist/index.js` exists
- Check file permissions

---

## Security Checklist

- [ ] `credentials.json` NOT committed to git
- [ ] `token.json` NOT committed to git
- [ ] `linkedin_token.json` NOT committed to git
- [ ] `.env` files NOT committed to git
- [ ] `.gitignore` includes all credential files
- [ ] `AUTO_APPROVE=false` in both servers
- [ ] OAuth redirect URIs match exactly
- [ ] Test users added in OAuth consent screens
- [ ] Client secrets stored securely

---

## Next Steps

After completing this setup:

1. **Create approval-processor skill** (Silver Tier requirement)
   - Automates processing of `/Pending_Approval` files
   - Executes approved actions via MCP

2. **Create email-sender skill** (Silver Tier requirement)
   - High-level skill that uses Gmail MCP
   - Integrates with task-processor

3. **Create linkedin-poster skill** (Silver Tier requirement)
   - High-level skill that uses LinkedIn MCP
   - Template selection and content generation

4. **Create scheduler-manager skill** (Silver Tier requirement)
   - Schedules approval processor to run every 5 minutes
   - Automates dashboard updates

---

## Quick Reference

### Gmail MCP Tools
- `gmail_send_email` - Send email (with approval)
- `gmail_read_emails` - Read inbox
- `gmail_search_emails` - Search emails
- `gmail_draft_email` - Create draft
- `gmail_get_profile` - Get account info

### LinkedIn MCP Tools
- `linkedin_create_post` - Create post (with approval)
- `linkedin_generate_post` - Generate from template
- `linkedin_list_templates` - List templates
- `linkedin_get_profile` - Get profile
- `linkedin_get_post_analytics` - Get post stats

### File Paths
- Gmail MCP: `C:\Users\Najma-LP\Desktop\My Vault\mcp-servers\gmail-mcp`
- LinkedIn MCP: `C:\Users\Najma-LP\Desktop\My Vault\mcp-servers\linkedin-mcp`
- Vault: `C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault`
- MCP Config: `%APPDATA%\Claude\mcp.json`

---

**Setup Complete!**

You now have:
- Gmail MCP server with OAuth 2.0 and HITL
- LinkedIn MCP server with business automation
- Claude Code integration
- Full approval workflow infrastructure

Ready to proceed to Silver Tier skill creation! 🚀
