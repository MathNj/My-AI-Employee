# Xero Integration Setup Guide

Complete guide for setting up Xero accounting integration with the Personal AI Employee.

## Prerequisites

- Xero account (free trial available at xero.com)
- Node.js 20+ installed
- Python 3.10+ installed
- Claude Code configured

## Step 1: Create Xero Developer Account

1. **Visit Xero Developer Portal**
   - Go to: https://developer.xero.com/
   - Click "Sign in" (use your Xero credentials)
   - Accept developer terms

2. **Create New App**
   - Click "New app"
   - App name: "Personal AI Employee"
   - Company/App URL: http://localhost:8080
   - Redirect URI: http://localhost:8080/callback
   - Click "Create app"

3. **Get Credentials**
   - Copy Client ID
   - Copy Client Secret
   - Save for next step

## Step 2: Install Xero MCP Server

```bash
# Install globally
npm install -g @xeroapi/xero-mcp-server

# Or install locally in project
cd ~/ai-employee
npm install @xeroapi/xero-mcp-server
```

## Step 3: Configure Environment Variables

Create or edit `.env` file in vault root:

```bash
# Xero API Credentials
XERO_CLIENT_ID=your_client_id_here
XERO_CLIENT_SECRET=your_client_secret_here
XERO_REDIRECT_URI=http://localhost:8080/callback

# Vault Configuration
VAULT_PATH=C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault
```

**Important:** Never commit `.env` to git!

## Step 4: Configure Claude Code MCP

Edit Claude Code MCP configuration:

**Windows:** `%USERPROFILE%\.config\claude-code\mcp.json`
**Mac/Linux:** `~/.config/claude-code/mcp.json`

Add Xero MCP server:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["gmail-mcp"],
      "env": {
        "GMAIL_CREDENTIALS": "credentials/credentials.json"
      }
    },
    "linkedin": {
      "command": "npx",
      "args": ["linkedin-mcp"],
      "env": {
        "LINKEDIN_CLIENT_ID": "your_linkedin_client_id"
      }
    },
    "xero": {
      "command": "npx",
      "args": ["@xeroapi/xero-mcp-server"],
      "env": {
        "XERO_CLIENT_ID": "${XERO_CLIENT_ID}",
        "XERO_CLIENT_SECRET": "${XERO_CLIENT_SECRET}",
        "XERO_REDIRECT_URI": "http://localhost:8080/callback"
      }
    }
  }
}
```

## Step 5: Authenticate with Xero

Run the authentication script:

```bash
cd .claude/skills/xero-integrator
python scripts/xero_auth.py
```

This will:
1. Open browser for Xero login
2. Request permissions
3. Save OAuth token to `credentials/xero_token.json`
4. Display "Authentication successful!"

## Step 6: Test Connection

```bash
python scripts/test_xero_connection.py
```

Expected output:
```
✓ Connected to Xero
✓ Organization: Your Company Name
✓ Permissions: accounting.transactions, accounting.reports
✓ Connection test successful!
```

## Step 7: Initial Sync

Sync your first transactions:

```bash
python scripts/sync_transactions.py --start 2026-01-01
```

This creates: `/Accounting/Transactions_2026-01.md`

## Xero Permissions Required

The app needs these scopes:

- `accounting.transactions` - Read and categorize transactions
- `accounting.reports.read` - Generate financial reports
- `accounting.contacts` - Manage customers/suppliers
- `accounting.settings` - Read chart of accounts

Grant these during OAuth flow.

## Folder Structure

After setup, you'll have:

```
AI_Employee_Vault/
├── Accounting/
│   ├── Transactions_2026-01.md
│   ├── Transactions_2026-02.md
│   └── Reports/
│       ├── 2026-01_ProfitLoss.md
│       └── 2026-01_BalanceSheet.md
└── credentials/
    └── xero_token.json (OAuth token)
```

## Troubleshooting

### "Client ID not found"
- Check `.env` file exists and has correct credentials
- Verify no extra spaces in credentials
- Restart Claude Code after editing mcp.json

### "Redirect URI mismatch"
- Ensure redirect URI in Xero app matches exactly: `http://localhost:8080/callback`
- Check for trailing slashes

### "Permission denied"
- Re-run OAuth flow: `python scripts/xero_auth.py`
- Ensure all required scopes granted in Xero

### "Token expired"
- Tokens expire after 30 minutes
- Run: `python scripts/refresh_xero_token.py`
- Or automatic refresh will happen on next sync

## Security Best Practices

1. **Never share credentials**
   - Add `.env` to `.gitignore`
   - Don't screenshot or email credentials

2. **Rotate credentials quarterly**
   - Generate new Client Secret in Xero Developer Portal
   - Update `.env` file

3. **Review app permissions**
   - Visit https://developer.xero.com/myapps
   - Ensure only necessary scopes enabled

4. **Monitor API usage**
   - Xero has rate limits (60 calls/minute)
   - Check usage in developer portal

## Next Steps

1. ✅ Set up daily transaction sync
   - Use scheduler-manager: "Schedule daily Xero sync at 6 AM"

2. ✅ Configure expense categories
   - Edit `references/category_rules.md`
   - Add your common vendors

3. ✅ Generate first report
   - Run: `python scripts/generate_report.py --type profit-loss --month 2026-01`

4. ✅ Integrate with CEO briefing
   - ceo-briefing-generator will automatically use Xero data

## Support Resources

- Xero API Docs: https://developer.xero.com/documentation/
- Xero MCP Server: https://github.com/XeroAPI/xero-mcp-server
- Xero Support: https://central.xero.com/s/
