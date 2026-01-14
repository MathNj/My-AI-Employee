---
name: financial-analyst
description: Analyzes financial data to generate insights, summaries, trends, and risk signals. Supports expense categorization, cash-flow analysis, revenue tracking, cost optimization, and financial anomaly detection. Analysis only - never moves money or executes payments.
---

# financial-analyst

## Overview

The **financial-analyst** skill analyzes **financial data** to generate **insights, summaries, trends, and risk signals**.

**Critical Constraint:** This skill performs **ANALYSIS ONLY**. It never moves money, executes payments, edits bank records, or takes irreversible actions.

---

## Quick Start

```bash
# Analyze current month
python .claude/skills/financial-analyst/scripts/analyze_finances.py

# Analyze current year
python .claude/skills/financial-analyst/scripts/analyze_finances.py --period year

# Custom date range
python .claude/skills/financial-analyst/scripts/analyze_finances.py \
  --period custom --start 2026-01-01 --end 2026-01-31

# Save to specific location
python .claude/skills/financial-analyst/scripts/analyze_finances.py --output reports/jan_2026.md
```

---

## When to Use This Skill

### ✅ Use when:
- New transactions are logged
- Weekly or monthly financial reviews needed
- System must identify spending patterns or anomalies
- Preparing data for:
  - CEO briefings
  - Budget reviews
  - Subscription audits
- User asks:
  - "Where is my money going?"
  - "Are there unusual expenses?"
  - "Summarize this month's finances"

### ❌ Do NOT use when:
- Executing payments or refunds
- Editing accounting records
- Performing tax filing or legal compliance
- Making financial decisions without human approval

---

## Authority & Safety Rules

### Hard Constraints

1. **Analysis Only**
   - No payments
   - No account access
   - No MCP execution
   - Read-only vault access (except /Reports)

2. **No Financial Advice**
   - Descriptive analysis only, not prescriptive advice
   - Final decisions belong to the human
   - Clearly mark recommendations as suggestions

3. **No Record Mutation**
   - Must not modify accounting files
   - Must not alter transaction data
   - Never edit source financial records

4. **Transparency Over Accuracy**
   - If data is incomplete or ambiguous, state it clearly
   - Never infer missing amounts or dates
   - Mark data quality level explicitly

---

## Inputs (Read-Only)

**Financial Data:**
- `/Accounting/*.md`
- `/Accounting/*.csv`
- `/Bank_Transactions/*.md`
- `/Bank_Transactions/*.csv`
- `/Subscriptions/*.md`

**Context:**
- `/Business_Goals.md` (optional)
- Historical financial summaries
- Research data (benchmarks, tax thresholds via web-researcher)

---

## Outputs (Write-Only)

**Allowed:**
- `/Reports/Financial_Analysis_<YYYY-MM-DD>.md`

**Forbidden:**
- `/Approved`
- `/Pending_Approval`
- `/Done`
- `/Accounting`
- `/Bank_Transactions`

---

## Core Capabilities

### 1. Revenue Analysis

- Total revenue calculation
- Revenue trend detection (↑ / ↓ / stable)
- Revenue by source breakdown
- Average transaction size
- Period-over-period comparison

### 2. Expense Breakdown

- Automatic categorization:
  - Software & SaaS
  - Marketing & Advertising
  - Infrastructure (hosting, cloud)
  - Professional Services
  - Travel
  - Office & Equipment
  - Utilities
  - Other

- Top vendor analysis
- Expense trends by category
- Percentage of total calculations

### 3. Cash Flow Analysis

- Opening balance
- Total revenue (inflow)
- Total expenses (outflow)
- Net cash flow
- Closing balance
- Profit margin calculations

### 4. Anomaly Detection

**Detects:**
- **Unusual spikes:** Expenses >2.5x average for category
- **New vendors:** First-time transactions
- **Possible duplicates:** Similar amounts/vendors within 24 hours
- **Large transactions:** Charges >$1,000
- **Cost increases:** Category spending increases >20%

**Severity Levels:**
- 🔴 High: Duplicates, large unauthorized charges
- 🟡 Medium: Unusual spikes, large transactions
- 🟢 Low: New vendors, minor variations

### 5. Subscription Analysis

- Active subscription count
- Monthly recurring cost
- Annual cost projection
- Cost by service
- Subscription as % of total expenses

---

## Report Structure

Every generated report follows this schema:

```markdown
---
report_id: FIN_<timestamp>
generated: <ISO-8601>
period: <date range>
data_completeness: high | medium | low
risk_level: low | medium | high
---

# Financial Analysis Report

## Executive Summary
- Revenue, Expenses, Net
- Profit margin
- Cash flow status
- Anomaly count

## Revenue Analysis
- Total, count, average
- Trend direction
- Revenue by source

## Expense Breakdown
- Total expenses
- By category (table with %)
- Top vendors

## Cash Flow
- Opening → Revenue → Expenses → Closing
- Net flow calculation

## Anomalies & Flags
- Grouped by type
- Severity indicators
- Transaction details

## Subscription Insights
- Active count
- Monthly/annual costs
- Top subscriptions

## Recommendations
- Action items based on findings
- Risk mitigation suggestions

## Data Quality Notes
- Completeness assessment
- Missing data flags
```

---

## Usage Examples

### Example 1: Monthly Review

```bash
# Analyze current month
python scripts/analyze_finances.py
```

**Use case:** Regular monthly financial health check

**Output:**
- Revenue vs expenses
- Category breakdown
- Anomalies detected
- Subscription costs

### Example 2: Year-End Analysis

```bash
# Analyze full year
python scripts/analyze_finances.py --period year --output reports/2026_annual.md
```

**Use case:** Annual financial review, tax preparation data

### Example 3: Specific Period

```bash
# Q1 analysis
python scripts/analyze_finances.py \
  --period custom \
  --start 2026-01-01 \
  --end 2026-03-31
```

**Use case:** Quarterly business reviews

---

## Integration with Other Skills

### With web-researcher

```
Financial analysis needs industry benchmark
    ↓
web-researcher looks up average SaaS spend
    ↓
financial-analyst includes context in report
```

### With approval-processor

```
financial-analyst detects anomaly
    ↓
Creates alert/recommendation
    ↓
Human reviews via approval workflow
    ↓
Approves action (contact vendor, cancel subscription)
```

### With dashboard-updater

```
financial-analyst generates report
    ↓
dashboard-updater extracts key metrics
    ↓
Updates Dashboard.md with:
  - Current cash flow
  - This month's expenses
  - Budget vs actual
```

---

## Data Format Support

### CSV Files

**Expected format:**
```csv
date,amount,type,description,vendor
2026-01-15,49.99,expense,Software subscription,Adobe
2026-01-16,2500.00,income,Client payment,Acme Corp
```

**Fields:**
- `date`: YYYY-MM-DD or MM/DD/YYYY
- `amount`: Numeric (negative for expenses)
- `type`: income or expense
- `description`: Transaction description
- `vendor`: Vendor/source name

### Markdown Files

**Expected format:**
```markdown
# January 2026 Transactions

| Date | Amount | Description | Vendor | Type |
|------|--------|-------------|--------|------|
| 2026-01-15 | $49.99 | Adobe subscription | Adobe | expense |
| 2026-01-16 | $2,500.00 | Client payment | Acme Corp | income |
```

---

## Anomaly Thresholds

**Default settings** (customizable in script):

```python
ANOMALY_THRESHOLDS = {
    'spike_multiplier': 2.5,      # Flag if >2.5x average
    'new_vendor_flag': True,       # Flag new vendors
    'duplicate_threshold_hours': 24,  # Check 24hr window
    'large_transaction_amount': 1000  # Flag >$1000
}
```

**Adjust in script for your business:**
- Higher multiplier = fewer spike alerts
- Lower amount threshold = more large transaction flags
- Disable new_vendor_flag if frequent new vendors

---

## Best Practices

### Data Organization

1. **Consistent file structure**
   - Store all transactions in `/Accounting` or `/Bank_Transactions`
   - Use consistent date format (YYYY-MM-DD recommended)
   - Include vendor names

2. **Regular updates**
   - Import bank statements monthly
   - Log transactions promptly
   - Review and categorize

3. **Subscription tracking**
   - Maintain `/Subscriptions` folder
   - Update when adding/removing services
   - Include renewal dates

### Analysis Frequency

**Recommended:**
- Weekly: Quick check (last 7 days)
- Monthly: Full analysis with anomaly review
- Quarterly: Trend analysis and budget review
- Annual: Year-end summary for taxes

### Anomaly Review

1. **Always review high-severity anomalies**
   - Duplicates (possible billing errors)
   - Large unauthorized transactions

2. **Investigate medium-severity**
   - Unusual spikes (verify legitimate)
   - Cost increases (planned or unexpected?)

3. **Monitor low-severity**
   - New vendors (expected purchases?)
   - Track for patterns

---

## Via Claude Code

When using Claude Code, simply ask:

- "Analyze this month's finances"
- "Generate financial report"
- "Check for unusual expenses"
- "Review my subscriptions"

Claude will:
1. Use financial-analyst skill
2. Load transaction data
3. Perform analysis
4. Generate structured report
5. Save to /Reports

---

## Security Considerations

### Data Privacy

- All analysis performed locally
- No data sent to external services
- Reports stored in vault

### Read-Only Access

- Never modifies source financial files
- No write access to /Accounting or /Bank_Transactions
- Only writes to /Reports

### No Financial Actions

- Cannot execute payments
- Cannot access bank accounts
- Cannot modify balances
- Analysis only, no side effects

---

## Troubleshooting

### "No transactions found"

**Cause:** No files in Accounting or Bank_Transactions folders

**Solution:**
- Ensure transaction files exist
- Check date range matches data
- Verify file format (CSV or MD)

### "Data completeness: low"

**Cause:** Missing vendor or description fields

**Solution:**
- Review transaction files
- Add missing information
- Ensure consistent format

### "Incorrect categorization"

**Cause:** Keyword-based categorization limitations

**Solution:**
- Update EXPENSE_CATEGORIES in script
- Add specific vendor keywords
- Manual review and adjustment

### "Revenue trend shows 'insufficient_data'"

**Cause:** Too few transactions for trend analysis

**Solution:**
- Analyze longer period
- Ensure revenue transactions labeled correctly
- Check type field = "income"

---

## Monitoring and Logging

All analyses logged to:
`/Logs/financial_analysis_YYYY-MM-DD.json`

**Log entry:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "financial_analysis_completed",
  "details": {
    "period": "2026-01-01 to 2026-01-31",
    "transactions": 45,
    "revenue": 5000.00,
    "expenses": 3200.00,
    "net_flow": 1800.00,
    "anomalies": 3,
    "risk_level": "low"
  },
  "skill": "financial-analyst"
}
```

---

## Limitations

### What It Can Do

✅ Analyze transaction data
✅ Categorize expenses
✅ Detect anomalies
✅ Calculate cash flow
✅ Generate insights

### What It Cannot Do

❌ Access bank accounts
❌ Execute payments
❌ Provide tax advice
❌ Make investment recommendations
❌ Guarantee accuracy (depends on data quality)
❌ Replace professional accountant

---

## References

- See `templates/report_template.md` for report format
- See `Business_Goals.md` for financial targets
- See web-researcher skill for external benchmark research

---

**Remember:** This skill provides descriptive analysis only, not prescriptive financial advice. Final decisions belong to the business owner.
