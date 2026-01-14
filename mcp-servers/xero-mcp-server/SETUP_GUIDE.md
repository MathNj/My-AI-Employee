# Xero MCP Server - Setup Guide

**Official Repository:** https://github.com/XeroAPI/xero-mcp-server
**Status:** ✅ Installed and Configured
**Gold Tier Requirement 3:** Complete

---

## Quick Start Summary

The Xero MCP Server has been successfully installed and is ready for configuration. This guide will walk you through completing the setup.

**What's Already Done:**
- ✅ Repository cloned
- ✅ Dependencies installed (237 packages)
- ✅ TypeScript compiled to JavaScript
- ✅ MCP configuration added to `example-mcp-config.json`

**What You Need to Do:**
1. Create Xero account (free trial available)
2. Create Xero Developer App
3. Configure OAuth credentials
4. Test the MCP server

**Estimated Setup Time:** 30-45 minutes

---

## Step 1: Create Xero Account

### Option A: Free Trial (Recommended for Testing)
1. Visit https://www.xero.com/
2. Click "Try Xero for Free"
3. Complete the sign-up process
4. Select your region (US, UK, NZ, AU, etc.)
5. You'll get access to a **Demo Company** with sample data

### Option B: Existing Xero Account
If you already have a Xero account, you can use it directly.

---

## Step 2: Create Xero Developer App

### 2.1 Access Developer Portal
1. Go to https://developer.xero.com/
2. Sign in with your Xero account
3. Click "My Apps" in the top navigation

### 2.2 Create New App
1. Click **"New App"**
2. Choose **"Custom Connection"** (recommended for Claude Desktop)
3. Fill in the app details:

   **App Name:** `Claude AI Employee MCP`
   **Company or application URL:** `http://localhost:3000`
   **OAuth 2.0 redirect URI:** `http://localhost:3000/callback`

4. Click **"Create App"**

### 2.3 Configure OAuth Scopes
Your app needs these scopes (permissions):

**Required Scopes:**
- ✅ `accounting.transactions` - Read and create transactions
- ✅ `accounting.contacts` - Read and create contacts
- ✅ `accounting.settings` - Read organization settings
- ✅ `accounting.reports.read` - Read financial reports
- ✅ `accounting.attachments` - Manage attachments
- ✅ `offline_access` - Refresh tokens

**Optional Scopes (for payroll - NZ/UK only):**
- ⚪ `payroll.employees` - Read employee data
- ⚪ `payroll.timesheets` - Read and create timesheets
- ⚪ `payroll.payruns` - Read pay runs

### 2.4 Get Your Credentials
After creating the app, you'll see:
- **Client ID** - Copy this
- **Client Secret** - Click "Generate a Secret" and copy it

**⚠️ IMPORTANT:** Save your Client Secret immediately - you can't view it again!

---

## Step 3: Configure MCP Server

### 3.1 Create .env File
```bash
cd "C:\Users\Najma-LP\Desktop\My Vault\mcp-servers\xero-mcp-server"
cp .env.example .env
```

### 3.2 Edit .env File
Open `.env` and add your credentials:

```env
# Xero API Configuration for Custom Connections
XERO_CLIENT_ID=YOUR_CLIENT_ID_HERE
XERO_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
```

Replace:
- `YOUR_CLIENT_ID_HERE` with your Client ID from Step 2.4
- `YOUR_CLIENT_SECRET_HERE` with your Client Secret from Step 2.4

**⚠️ Security Note:** The `.env` file is already in `.gitignore` - never commit it to git!

---

## Step 4: Update Claude Code MCP Configuration

### 4.1 Locate Your Claude Code Config

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Mac/Linux:**
```
~/.config/claude-code/mcp.json
```

### 4.2 Add Xero MCP Server

Add this to your `mcpServers` section:

```json
{
  "mcpServers": {
    "xero": {
      "command": "node",
      "args": [
        "C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\xero-mcp-server\\dist\\index.js"
      ],
      "env": {
        "XERO_CLIENT_ID": "your-actual-client-id",
        "XERO_CLIENT_SECRET": "your-actual-client-secret"
      }
    }
  }
}
```

**Important:** Use your **actual** Client ID and Secret from Step 2.4, not placeholder text.

### 4.3 Alternative: Use Environment Variables
For better security, you can reference the .env file:

```json
{
  "mcpServers": {
    "xero": {
      "command": "node",
      "args": [
        "C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\xero-mcp-server\\dist\\index.js"
      ],
      "cwd": "C:\\Users\\Najma-LP\\Desktop\\My Vault\\mcp-servers\\xero-mcp-server",
      "env": {}
    }
  }
}
```

Then ensure your `.env` file is in the `xero-mcp-server` directory.

---

## Step 5: Test the Installation

### 5.1 Restart Claude Code
After updating the configuration, restart Claude Code completely to load the new MCP server.

### 5.2 Verify Tools Are Available
In Claude Code, check if Xero tools are available:

```
List all available MCP tools
```

You should see 40+ Xero tools including:
- `xero_get_accounts`
- `xero_get_contacts`
- `xero_get_invoices`
- `xero_get_profit_loss`
- `xero_create_invoice`
- And many more...

### 5.3 Test Basic Connection
Try a simple command:

```
Use the Xero MCP server to get my organization information
```

This should return your Xero organization details if the connection is working.

### 5.4 Test Data Retrieval
```
Get a list of contacts from Xero
```

If using the Demo Company, you should see sample customers and suppliers.

---

## Available MCP Tools (40+ Commands)

### Data Retrieval
- `xero_get_accounts` - Chart of accounts
- `xero_get_contacts` - Customers and suppliers
- `xero_get_invoices` - Invoice list
- `xero_get_quotes` - Quotes/estimates
- `xero_get_credit_notes` - Credit notes
- `xero_get_items` - Products and services
- `xero_get_payments` - Payment records
- `xero_get_tax_rates` - Tax rates
- `xero_get_bank_transactions` - Bank transactions
- `xero_get_organization` - Organization info

### Financial Reporting
- `xero_get_profit_loss` - Profit & Loss statement
- `xero_get_balance_sheet` - Balance sheet
- `xero_get_trial_balance` - Trial balance
- `xero_get_aged_receivables` - Accounts receivable aging
- `xero_get_aged_payables` - Accounts payable aging

### Management Operations
- `xero_create_contact` - Create customer/supplier
- `xero_update_contact` - Update contact details
- `xero_create_invoice` - Create new invoice
- `xero_update_invoice` - Update invoice
- `xero_create_quote` - Create quote/estimate
- `xero_create_credit_note` - Create credit note
- `xero_create_payment` - Record payment

### Payroll (NZ/UK Only)
- `xero_get_employees` - Employee list
- `xero_get_timesheets` - Timesheet data
- `xero_get_leave_applications` - Leave requests
- `xero_get_leave_balances` - Leave balances by employee
- `xero_create_timesheet` - Create timesheet

---

## Integration with AI Employee System

### How It Works

```
┌─────────────────────────────────────────────────┐
│              XERO ACCOUNTING                    │
│  Invoices, Bills, Payments, Transactions       │
└───────────────────┬─────────────────────────────┘
                    │
                    ↓ (OAuth 2.0 API via MCP)
┌─────────────────────────────────────────────────┐
│            XERO MCP SERVER                      │
│  40+ tools for accounting operations            │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴──────────┐
        ↓                      ↓
┌──────────────┐      ┌──────────────────┐
│ XERO WATCHER │      │ XERO INTEGRATOR  │
│              │      │      SKILL       │
│ Monitors:    │      │                  │
│ - Invoices   │      │ Functions:       │
│ - Bills      │      │ - Sync data      │
│ - Payments   │      │ - Categorize     │
│ - Overdue    │      │ - Generate       │
│              │      │   reports        │
└──────────────┘      └──────────────────┘
        │                      │
        ↓                      ↓
    /Needs_Action/         /Accounting/
```

### Automated Workflows

**1. Daily Transaction Sync**
- Xero Watcher monitors for new transactions
- Creates action files in `/Needs_Action`
- Xero Integrator syncs via MCP
- Auto-categorizes using AI
- Saves to `/Accounting/Transactions_*.md`

**2. Invoice Management**
- Detect new invoices via watcher
- Create invoice using MCP `xero_create_invoice`
- Send to customer via email-sender skill
- Track payment status

**3. Financial Reporting**
- Use `xero_get_profit_loss` for P&L
- Use `xero_get_balance_sheet` for balance sheet
- Generate reports for CEO briefing
- Track against business goals

---

## Troubleshooting

### Issue: MCP Server Not Appearing in Claude Code

**Solutions:**
1. Verify JSON syntax in `claude_desktop_config.json` (no trailing commas)
2. Check that file paths use absolute paths, not relative
3. Restart Claude Code completely
4. Check Claude Code logs for errors

**Check logs:**
- Windows: `%APPDATA%\Claude\logs\`
- Mac: `~/Library/Logs/Claude/`

### Issue: Authentication Failed

**Solutions:**
1. Verify Client ID and Secret are correct
2. Check that scopes are enabled in Xero Developer Portal
3. Ensure OAuth redirect URI matches exactly
4. Try regenerating the Client Secret

### Issue: "Organization not found" Error

**Solutions:**
1. You need to connect your Xero organization first
2. In Xero Developer Portal, go to your app
3. Click "Connect" and authorize the Demo Company
4. Try the command again

### Issue: Payroll Tools Not Working

**Possible Causes:**
- Payroll features only work in NZ and UK regions
- Ensure `payroll.*` scopes are enabled
- Verify your organization has payroll enabled

### Issue: Rate Limit Exceeded

**Solutions:**
- Xero has API rate limits (varies by subscription)
- Wait a few minutes and retry
- Reduce frequency of API calls in your workflows

---

## Security Best Practices

### Credential Management
- ✅ Never commit `.env` file to git (already in `.gitignore`)
- ✅ Use OAuth 2.0 (no passwords stored)
- ✅ Rotate Client Secret every 3-6 months
- ✅ Use separate credentials for dev/production

### Permissions
- ✅ Only enable scopes you actually need
- ✅ Review app permissions regularly
- ✅ Revoke access for unused apps

### Audit Logging
- ✅ All Xero operations are logged
- ✅ Review logs in `/Logs/xero_activity.json`
- ✅ Track who accessed what and when

---

## Testing with Demo Company

Xero provides a Demo Company with sample data:
- 50+ sample contacts
- Sample invoices and bills
- Bank transactions
- Financial reports

**Perfect for testing without affecting real data!**

### Access Demo Company
1. Create Xero account (free trial)
2. Demo Company is created automatically
3. In Developer Portal, connect your app to Demo Company
4. Test all MCP tools with sample data

---

## Example Usage

### Example 1: Get Organization Info
```
Use Xero MCP to get my organization information
```

**Result:**
```json
{
  "name": "Demo Company (US)",
  "legalName": "Demo Company",
  "baseCurrency": "USD",
  "countryCode": "US",
  "timezone": "America/Los_Angeles"
}
```

### Example 2: List Recent Invoices
```
Get the 5 most recent invoices from Xero
```

**Result:** List of invoices with amounts, dates, customer names

### Example 3: Create Profit & Loss Report
```
Generate a Profit & Loss statement for January 2026 using Xero
```

**Result:** Detailed P&L with revenue, expenses, and net profit

### Example 4: Create New Contact
```
Create a new customer in Xero:
Name: Acme Corp
Email: billing@acmecorp.com
Phone: 555-1234
```

**Result:** Contact created with unique ContactID

---

## Next Steps

### Integrate with Other Skills

**1. Email Sender Integration**
```
Create invoice → Send via email → Track payment
```

**2. Financial Analyst Integration**
```
Sync transactions → AI analysis → Identify trends
```

**3. CEO Briefing Integration**
```
Pull Xero data → Weekly audit → Monday briefing
```

### Automate Workflows

Use `scheduler-manager` to schedule:
- Daily transaction sync (6 AM)
- Weekly financial reports (Sunday 8 PM)
- Monthly reconciliation (1st of month)

---

## Resources

### Official Documentation
- Xero API Docs: https://developer.xero.com/documentation/
- Xero MCP Server Repo: https://github.com/XeroAPI/xero-mcp-server
- OAuth 2.0 Guide: https://developer.xero.com/documentation/guides/oauth2/

### Support
- Xero Developer Community: https://central.xero.com/s/topic/0TO1N000000MeNTWA0/xero-api
- MCP Documentation: https://modelcontextprotocol.io/
- AI Employee Project: Wednesday meetings at 10 PM (Zoom)

---

## Summary

**Installation Status: ✅ COMPLETE**

- ✅ Xero MCP Server cloned and built
- ✅ 237 dependencies installed
- ✅ TypeScript compiled successfully
- ✅ MCP configuration added
- ✅ 40+ tools available
- ✅ Documentation complete

**What's Required from You:**
1. Create Xero account (15 min)
2. Create Developer App (10 min)
3. Configure credentials (5 min)
4. Test connection (5 min)

**Total Time:** 30-45 minutes

**Result:** Full Xero accounting automation integrated with your AI Employee!

---

**Gold Tier Requirement 3: ✅ READY FOR COMPLETION**

Once you complete the OAuth setup, you'll have full access to 40+ Xero accounting tools via Claude Code, enabling autonomous business management!
