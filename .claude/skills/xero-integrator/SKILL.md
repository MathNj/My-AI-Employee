---
name: xero-integrator
description: Integrate with Xero accounting system for automated bookkeeping and financial reporting. Use when the user needs to (1) Sync transactions from Xero, (2) Categorize expenses automatically, (3) Generate financial reports, (4) Manage invoices, (5) Reconcile bank accounts, or (6) Import accounting data. Triggers include "sync with Xero", "import transactions", "categorize expenses", "generate financial report", "check Xero balance".
---

# Xero Integrator

Automate accounting workflows by integrating with Xero accounting platform via MCP server.

## Quick Start

### Sync Transactions

```bash
# Import all recent transactions
python scripts/sync_transactions.py

# Import transactions for specific period
python scripts/sync_transactions.py --start 2026-01-01 --end 2026-01-31

# Sync and auto-categorize
python scripts/sync_transactions.py --auto-categorize
```

### Categorize Expenses

```bash
# Categorize all uncategorized transactions
python scripts/categorize_expenses.py

# Review and approve categorizations
python scripts/categorize_expenses.py --review
```

### Generate Report

```bash
# Generate monthly financial report
python scripts/generate_report.py --month 2026-01

# Generate custom report
python scripts/generate_report.py --start 2026-01-01 --end 2026-01-31 --type profit-loss
```

## Core Workflows

### Workflow 1: Daily Transaction Sync

**Trigger:** Scheduled daily (via scheduler-manager)

1. Connect to Xero via MCP server
2. Fetch new transactions since last sync
3. Auto-categorize using AI rules
4. Save to `/Accounting/Transactions_YYYY-MM.md`
5. Flag uncertain categorizations for review
6. Update Dashboard with sync status

**Output:**
```markdown
# Transactions - January 2026

## 2026-01-12
- **Office Supplies** - $45.00 - Staples Inc. (Auto-categorized)
- **Software Subscription** - $29.00 - Adobe Inc. (Auto-categorized)
- **Client Payment** - $1,500.00 - Client A (Income)
- **Uncategorized** - $200.00 - Unknown Vendor (Needs Review)
```

### Workflow 2: Monthly Financial Reporting

**Trigger:** End of month (via scheduler-manager or manual)

1. Sync all transactions for the month
2. Generate Profit & Loss statement
3. Generate Balance Sheet
4. Identify top expenses by category
5. Calculate tax estimates
6. Save to `/Accounting/Reports/YYYY-MM_Report.md`
7. Integration with ceo-briefing-generator

**Report Sections:**
- Revenue Summary
- Expense Breakdown by Category
- Net Profit/Loss
- Cash Flow Analysis
- Tax Estimates
- Notable Transactions

### Workflow 3: Expense Categorization Review

**Trigger:** Weekly review or when uncertain categories detected

1. List all uncategorized transactions
2. Apply category rules from `references/category_rules.md`
3. Use AI to suggest categories
4. Create approval file in `/Pending_Approval` for uncertain items
5. Human reviews and approves
6. Update Xero with approved categories

## Xero MCP Integration

This skill requires the Xero MCP server to be installed and configured.

### MCP Server Setup

**Install Xero MCP:**
```bash
npm install -g @xeroapi/xero-mcp-server
```

**Configure Claude Code** (`~/.config/claude-code/mcp.json`):
```json
{
  "mcpServers": {
    "xero": {
      "command": "npx",
      "args": ["@xeroapi/xero-mcp-server"],
      "env": {
        "XERO_CLIENT_ID": "your-client-id",
        "XERO_CLIENT_SECRET": "your-client-secret",
        "XERO_REDIRECT_URI": "http://localhost:8080/callback"
      }
    }
  }
}
```

**Authenticate:**
1. Visit https://developer.xero.com/
2. Create new app
3. Copy Client ID and Secret to `.env`
4. Run OAuth flow: `python scripts/xero_auth.py`

See `references/xero_setup.md` for detailed setup instructions.

### MCP Tools Available

The Xero MCP server exposes these tools:

- `xero_get_transactions` - Fetch transactions
- `xero_get_invoices` - Retrieve invoices
- `xero_create_invoice` - Create new invoice
- `xero_get_contacts` - Get customer/supplier list
- `xero_get_accounts` - Get chart of accounts
- `xero_update_transaction` - Update transaction category

## Transaction Categorization

### Auto-Categorization Rules

The skill uses AI-powered categorization with learned patterns:

**Category Rules** (see `references/category_rules.md`):
- **Office Supplies:** Staples, Office Depot, Amazon Business
- **Software:** Adobe, Microsoft, Slack, Notion
- **Marketing:** Google Ads, Facebook Ads, LinkedIn
- **Travel:** Airlines, Hotels, Uber, Lyft
- **Utilities:** Internet, Phone, Electricity
- **Professional Services:** Legal, Accounting, Consulting

**Confidence Levels:**
- **High (90%+):** Auto-apply category
- **Medium (70-89%):** Suggest category, require review
- **Low (<70%):** Mark as uncategorized

### Learning from Corrections

When humans correct categorizations:
1. Pattern is saved to category rules
2. Future similar transactions auto-categorize
3. Rules file updates automatically

## Financial Reports

### Report Types

**Profit & Loss (P&L):**
```bash
python scripts/generate_report.py --type profit-loss --month 2026-01
```

Generates:
- Revenue by category
- Expenses by category
- Gross profit
- Net profit/loss
- Comparison to previous month

**Balance Sheet:**
```bash
python scripts/generate_report.py --type balance-sheet --date 2026-01-31
```

Generates:
- Assets (current, fixed)
- Liabilities (current, long-term)
- Equity
- Financial ratios

**Cash Flow:**
```bash
python scripts/generate_report.py --type cash-flow --month 2026-01
```

Generates:
- Operating activities
- Investing activities
- Financing activities
- Net cash change

**Tax Estimate:**
```bash
python scripts/generate_report.py --type tax-estimate --quarter Q1-2026
```

Generates:
- Quarterly income
- Deductible expenses
- Estimated tax liability
- Payment recommendations

### Report Output Location

All reports saved to: `/Accounting/Reports/YYYY-MM_ReportType.md`

## Integration with Other Skills

### financial-analyst

```
xero-integrator syncs transactions
    ↓
Saves to /Accounting folder
    ↓
financial-analyst reads data
    ↓
Performs trend analysis
    ↓
Identifies anomalies
```

### ceo-briefing-generator

```
xero-integrator provides financial data
    ↓
ceo-briefing-generator uses for weekly audit
    ↓
Includes revenue, expenses, cash flow
    ↓
Monday Morning CEO Briefing
```

### approval-processor

For uncertain categorizations:
```
xero-integrator detects low-confidence category
    ↓
Creates approval file in /Pending_Approval
    ↓
Human reviews and moves to /Approved
    ↓
approval-processor triggers xero-integrator
    ↓
Category updated in Xero
```

## Expense Categorization

### Category Hierarchy

```
Revenue
├── Product Sales
├── Service Revenue
└── Other Income

Cost of Goods Sold
├── Materials
├── Labor
└── Shipping

Operating Expenses
├── Office Supplies
├── Software & Subscriptions
├── Marketing & Advertising
├── Travel & Entertainment
├── Utilities
├── Professional Services
└── Insurance

Other Expenses
├── Bank Fees
├── Interest
└── Depreciation
```

### Custom Category Rules

Add custom rules in `references/category_rules.md`:

```yaml
- pattern: "amazon.com"
  keywords: ["office", "supplies", "paper"]
  category: "Office Supplies"
  confidence: 85

- pattern: "google.com/ads"
  category: "Marketing & Advertising"
  confidence: 95
```

## Invoice Management

### Create Invoice

```bash
# Create invoice from template
python scripts/create_invoice.py --client "Client A" --amount 1500 --items "Consulting Services"

# Create from approval file
python scripts/create_invoice.py --from-approval /Pending_Approval/INVOICE_ClientA.md
```

### Track Invoice Status

```bash
# Check unpaid invoices
python scripts/track_invoices.py --status unpaid

# Check overdue invoices
python scripts/track_invoices.py --status overdue --days 30
```

### Send Invoice

Invoices integrate with email-sender skill:
```
Create invoice in Xero
    ↓
Generate PDF
    ↓
Create email with email-sender
    ↓
Attach invoice PDF
    ↓
Send with approval
```

## Bank Reconciliation

### Auto-Reconciliation

```bash
# Reconcile bank account
python scripts/reconcile_bank.py --account "Business Checking"

# Review unreconciled items
python scripts/reconcile_bank.py --account "Business Checking" --show-unmatched
```

**Matching Rules:**
- Amount matches within $0.01
- Date within 3 days
- Description similarity > 70%

### Manual Reconciliation

For unmatched items:
1. List unreconciled transactions
2. Suggest possible matches
3. Create approval file for manual matching
4. Human confirms matches
5. Update Xero with reconciliations

## Usage Examples

### Daily Automation

Schedule with scheduler-manager:
```bash
# Every day at 6 AM
python scripts/sync_transactions.py --auto-categorize
```

### Weekly Review

```bash
# Check uncategorized items
python scripts/categorize_expenses.py --review

# View weekly summary
python scripts/generate_report.py --type weekly-summary
```

### Monthly Close

```bash
# End of month routine
python scripts/sync_transactions.py --full
python scripts/reconcile_bank.py --all-accounts
python scripts/generate_report.py --type profit-loss --month current
python scripts/generate_report.py --type balance-sheet --date today
```

### Quarterly Tax Prep

```bash
# Prepare tax estimates
python scripts/generate_report.py --type tax-estimate --quarter Q1-2026
python scripts/export_tax_data.py --quarter Q1-2026 --format csv
```

## Error Handling

### Common Issues

**Xero API Timeout:**
- Automatic retry with exponential backoff
- Maximum 3 attempts
- Log error to `/Logs/xero_errors.json`

**OAuth Token Expired:**
- Automatic token refresh
- If refresh fails, alert human
- Pause operations until re-authenticated

**Categorization Uncertainty:**
- Don't auto-apply if confidence < 70%
- Create approval file
- Continue with other transactions

**Duplicate Transactions:**
- Check transaction ID before importing
- Skip duplicates
- Log skipped transactions

## Security & Compliance

### Credential Storage

- Store credentials in `.env` file
- Never commit credentials to git
- Use OAuth 2.0 (no passwords)
- Automatic token refresh

### Data Privacy

- All data stays local in Obsidian vault
- Encrypted connection to Xero (HTTPS)
- Audit logs for all operations
- PII redacted in logs

### Audit Trail

Every operation logged to `/Logs/xero_activity.json`:

```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "sync_transactions",
  "details": {
    "transactions_imported": 15,
    "auto_categorized": 12,
    "requires_review": 3
  },
  "user": "claude_code",
  "status": "success"
}
```

## Troubleshooting

**Sync Not Working:**
1. Check Xero MCP server running: `ps aux | grep xero`
2. Verify OAuth credentials in `.env`
3. Test connection: `python scripts/test_xero_connection.py`
4. Check logs: `cat Logs/xero_errors.json`

**Categories Not Saving:**
1. Verify Xero account has permission to edit
2. Check category exists in Xero chart of accounts
3. Review category rules file syntax

**Reports Missing Data:**
1. Ensure transactions synced for date range
2. Check `/Accounting/Transactions_*.md` files exist
3. Verify Xero account has correct permissions

## Scripts Reference

### sync_transactions.py

**Usage:**
```bash
python scripts/sync_transactions.py [options]

Options:
  --start DATE          Start date (YYYY-MM-DD)
  --end DATE            End date (YYYY-MM-DD)
  --auto-categorize     Apply category rules automatically
  --full                Full sync (ignore last sync date)
```

### categorize_expenses.py

**Usage:**
```bash
python scripts/categorize_expenses.py [options]

Options:
  --review              Show categorizations for review
  --approve FILE        Approve categorization from file
  --learn               Update rules from corrections
```

### generate_report.py

**Usage:**
```bash
python scripts/generate_report.py [options]

Options:
  --type TYPE           Report type (profit-loss, balance-sheet, cash-flow, tax-estimate)
  --month YYYY-MM       Month for report
  --start DATE          Custom start date
  --end DATE            Custom end date
  --output PATH         Custom output location
```

### create_invoice.py

**Usage:**
```bash
python scripts/create_invoice.py [options]

Options:
  --client NAME         Client name
  --amount AMOUNT       Invoice amount
  --items TEXT          Invoice line items
  --from-approval FILE  Create from approval file
  --send                Send invoice via email
```

## References

- `references/xero_setup.md` - Detailed setup instructions
- `references/xero_api.md` - Xero API documentation
- `references/category_rules.md` - Expense categorization rules
- `references/tax_categories.md` - Tax classification guide

---

**Dependencies:**
- Xero MCP Server: https://github.com/XeroAPI/xero-mcp-server
- financial-analyst skill (for analysis)
- email-sender skill (for invoices)
- approval-processor skill (for uncertain items)
- scheduler-manager skill (for automation)
