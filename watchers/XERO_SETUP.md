# Xero Watcher Setup Guide

Complete guide to set up the Xero watcher for your Personal AI Employee.

---

## Overview

The Xero watcher monitors your Xero accounting system for important financial events:

- **New Invoices** - Invoices created awaiting payment
- **New Bills** - Bills received that need to be paid
- **Payments Received** - Large payments from customers
- **Overdue Invoices** - Invoices requiring collection action
- **Large Transactions** - Significant transactions needing review

When events are detected, actionable files are created in `Needs_Action/` for the AI Employee to process.

---

## Prerequisites

- Xero account (any plan)
- Python 3.8+ installed
- Personal AI Employee vault set up

---

## Step 1: Install Python Dependencies

```bash
# Install Xero Python library
pip install pyxero

# Or add to your project requirements
pip install pyxero requests-oauthlib
```

---

## Step 2: Create Xero App

1. **Go to Xero Developer Portal:**
   - Visit: https://developer.xero.com/
   - Log in with your Xero account

2. **Create New App:**
   - Click "New App"
   - Choose "OAuth 2.0"
   - Fill in details:
     - **App Name:** Personal AI Employee
     - **Company/App URL:** http://localhost
     - **Redirect URI:** http://localhost:8080
     - **Description:** AI employee for business automation

3. **Save App Credentials:**
   - **Client ID** - Copy this
   - **Client Secret** - Copy this (keep secret!)

4. **Set App Scopes:**
   - Select these permissions:
     - `accounting.transactions` (read transactions)
     - `accounting.contacts` (read customers/vendors)
     - `accounting.reports.read` (read financial reports)

---

## Step 3: Configure Watcher

Create credentials file:

**File:** `watchers/credentials/xero_credentials.json`

```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "redirect_uri": "http://localhost:8080"
}
```

**Important:** Replace `YOUR_CLIENT_ID_HERE` and `YOUR_CLIENT_SECRET_HERE` with your actual credentials from Step 2.

---

## Step 4: Configure Watcher Settings

Create or edit configuration file:

**File:** `watchers/xero_config.json`

```json
{
  "large_transaction_threshold": 500.00,
  "overdue_alert_days": 7,
  "monitor_invoices": true,
  "monitor_bills": true,
  "monitor_payments": true,
  "monitor_bank_transactions": true,
  "monitor_overdue": true
}
```

**Configuration Options:**

| Setting | Default | Description |
|---------|---------|-------------|
| `large_transaction_threshold` | 500.00 | Alert for transactions above this amount |
| `overdue_alert_days` | 7 | Alert for invoices overdue by this many days |
| `monitor_invoices` | true | Monitor new customer invoices |
| `monitor_bills` | true | Monitor new bills to pay |
| `monitor_payments` | true | Monitor payment receipts |
| `monitor_bank_transactions` | true | Monitor bank transactions |
| `monitor_overdue` | true | Monitor overdue invoices |

---

## Step 5: First-Time OAuth Authorization

Run the watcher for the first time to complete OAuth flow:

```bash
cd watchers
python xero_watcher.py
```

**What Happens:**

1. Browser window opens automatically
2. Log in to Xero if needed
3. Authorize the app to access your Xero data
4. Browser redirects to localhost (you'll see a "can't connect" page - this is normal)
5. Copy the URL from the browser address bar
6. Paste it into the terminal when prompted
7. Watcher saves OAuth token and starts monitoring

**The token is saved to:** `watchers/credentials/xero_token.json`

---

## Step 6: Verify Watcher is Running

After OAuth authorization completes, you should see:

```
======================================================================
Personal AI Employee - Xero Watcher
======================================================================
Vault: C:\Users\YourName\Desktop\My Vault
Monitoring: Invoices, Bills, Payments, Transactions
Press Ctrl+C to stop
======================================================================

2026-01-13 10:30:00 - XeroWatcher - INFO - ✓ Connected to Xero API
2026-01-13 10:30:00 - XeroWatcher - INFO - XeroWatcher started
2026-01-13 10:30:00 - XeroWatcher - INFO - Check interval: 300 seconds
```

---

## Step 7: Test the Watcher

### Option 1: Create Test Invoice in Xero

1. Go to your Xero dashboard
2. Create a new invoice
3. Wait 5 minutes (default check interval)
4. Check `AI_Employee_Vault/Needs_Action/` for new file

### Option 2: Use Mock Mode

If you haven't set up OAuth yet, the watcher runs in mock mode with sample data:

```bash
# Run in mock mode (no OAuth needed)
python xero_watcher.py
```

Mock mode generates test events so you can see how the watcher works.

---

## Step 8: Schedule Watcher (Optional)

### Windows (Task Scheduler)

```powershell
# Run every 5 minutes
schtasks /create /tn "AI_Employee_Xero" /tr "python C:\path\to\watchers\xero_watcher.py" /sc minute /mo 5
```

### Linux/Mac (Cron)

```bash
# Add to crontab (runs every 5 minutes)
*/5 * * * * cd /path/to/watchers && python xero_watcher.py
```

---

## What Gets Created

When the watcher detects events, it creates markdown files in `Needs_Action/`:

### Example: New Invoice Detected

**File:** `Needs_Action/xero_new_invoice_20260113_103045.md`

```markdown
---
type: xero_event
event_type: new_invoice
source: xero_watcher
created: 2026-01-13T10:30:45Z
status: pending
priority: high
invoice_id: INV-2026-001
---

# New Invoice Created - INV-2026-001

## Invoice Details
- **Customer:** Acme Corp
- **Amount:** $2,500.00
- **Due Date:** 2026-02-13
- **Status:** AUTHORISED

## Action Required
A new invoice has been created and awaiting payment.

**Suggested Actions:**
1. Verify invoice details are correct
2. Send invoice to customer if not already sent
3. Add to accounts receivable tracking
...
```

The AI Employee can then:
- Process these files automatically
- Generate follow-up emails
- Update financial dashboards
- Create payment reminders
- Flag for approval if needed

---

## Troubleshooting

### "Xero library not available"

```bash
# Install the library
pip install pyxero
```

### "Xero credentials not found"

- Verify `watchers/credentials/xero_credentials.json` exists
- Check file path is correct
- Ensure JSON is valid

### "Failed to connect to Xero"

- Check your client_id and client_secret
- Verify app is created in Xero Developer Portal
- Ensure redirect_uri matches exactly
- Check scopes are set correctly

### OAuth Token Expired

- Delete `watchers/credentials/xero_token.json`
- Run watcher again to re-authorize
- Token is automatically refreshed normally

### No Events Detected

- Check `watchers/xero_config.json` settings
- Verify monitor flags are `true`
- Adjust `large_transaction_threshold` if needed
- Create a test invoice in Xero
- Check logs: `Logs/xerowatcher_YYYY-MM-DD.log`

---

## Configuration Examples

### High Alert Threshold (Only Major Events)

```json
{
  "large_transaction_threshold": 5000.00,
  "overdue_alert_days": 14,
  "monitor_invoices": true,
  "monitor_bills": true,
  "monitor_payments": true,
  "monitor_bank_transactions": false,
  "monitor_overdue": true
}
```

### Low Alert Threshold (All Activity)

```json
{
  "large_transaction_threshold": 100.00,
  "overdue_alert_days": 3,
  "monitor_invoices": true,
  "monitor_bills": true,
  "monitor_payments": true,
  "monitor_bank_transactions": true,
  "monitor_overdue": true
}
```

### Invoices Only

```json
{
  "large_transaction_threshold": 500.00,
  "overdue_alert_days": 7,
  "monitor_invoices": true,
  "monitor_bills": false,
  "monitor_payments": false,
  "monitor_bank_transactions": false,
  "monitor_overdue": true
}
```

---

## Security Best Practices

1. **Never commit credentials to git:**
   ```bash
   # Add to .gitignore
   watchers/credentials/xero_credentials.json
   watchers/credentials/xero_token.json
   ```

2. **Restrict file permissions:**
   ```bash
   # Linux/Mac
   chmod 600 watchers/credentials/xero_credentials.json
   ```

3. **Rotate credentials periodically:**
   - Generate new client_secret every 6 months
   - Update credentials file
   - Re-authorize watcher

4. **Use read-only scopes:**
   - Don't request write permissions unless needed
   - Limit scopes to minimum required

---

## Logs and Monitoring

### Log Files

- **Daily Log:** `Logs/xerowatcher_YYYY-MM-DD.log`
- **Action Log:** `Logs/actions_YYYY-MM-DD.json`
- **Processed Items:** `Logs/xerowatcher_processed.json`

### View Recent Activity

```bash
# View today's log
cat Logs/xerowatcher_$(date +%Y-%m-%d).log

# View action log (JSON)
cat Logs/actions_$(date +%Y-%m-%d).json | python -m json.tool
```

### Check Statistics

The watcher logs statistics on shutdown (Ctrl+C):

```
Runtime: 3600s
Total checks: 12
Items processed: 5
Errors: 0
Success rate: 100.0%
```

---

## Integration with AI Employee

The Xero watcher integrates seamlessly with your AI Employee workflow:

```
Xero API
    ↓
Xero Watcher (polls every 5 min)
    ↓
Needs_Action/ (creates .md files)
    ↓
Task Processor (AI reads and analyzes)
    ↓
Action Plans (creates execution plans)
    ↓
Approval Workflow (if needed)
    ↓
Execute Actions (email, post, record)
    ↓
Done/ (completed and logged)
```

---

## Advanced Usage

### Custom Check Interval

```python
# Check every 2 minutes (faster)
watcher = XeroWatcher(vault_path, check_interval=120)

# Check every 15 minutes (slower)
watcher = XeroWatcher(vault_path, check_interval=900)
```

### Multiple Xero Organizations

If you have multiple Xero organizations:

```bash
# Create separate credential files
watchers/credentials/xero_credentials_org1.json
watchers/credentials/xero_credentials_org2.json

# Run separate watcher instances
python xero_watcher.py --credentials org1
python xero_watcher.py --credentials org2
```

---

## Support and Resources

- **Xero API Docs:** https://developer.xero.com/documentation/api/accounting/overview
- **PyXero Library:** https://github.com/freakboy3742/pyxero
- **OAuth 2.0 Guide:** https://developer.xero.com/documentation/guides/oauth2/overview
- **Rate Limits:** https://developer.xero.com/documentation/guides/oauth2/limits

---

## Next Steps

1. ✅ Complete this setup
2. ✅ Test watcher with real Xero data
3. ✅ Schedule watcher to run continuously
4. Configure AI Employee to process Xero events
5. Set up approval workflow for financial actions
6. Integrate with email-sender for automated notifications
7. Connect to CEO briefing for financial reporting

---

**Xero Watcher Setup Complete!** 🎉

Your AI Employee is now monitoring your accounting system and will alert you to important financial events automatically.
