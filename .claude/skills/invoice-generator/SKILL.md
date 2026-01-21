# Invoice Generator Skill

**Skill Name:** invoice-generator
**Category:** Business Operations
**Version:** 1.0.0

## Overview

Automatically generates professional PDF invoices when triggered by business emails containing payment requests, billing inquiries, or invoice requests. Integrates with the cross-domain bridge to classify invoice requests and routes them through the approval workflow.

## When to Use

Use this skill when the AI Employee detects:
- Emails requesting invoices: "Please send invoice for Project X"
- Payment reminders: "Invoice #1234 is due"
- Billing inquiries: "What's the status of my invoice?"
- New business emails requiring invoicing: "Work completed, please bill"
- Client requests for billing statements

## Capabilities

### 1. Email Analysis
- Detects invoice-related keywords in emails
- Extracts client information from email signatures
- Identifies project/service details from email context
- Determines invoice amount from payment requests or project data

### 2. Invoice Data Extraction
- **From Email:**
  - Client name and email address
  - Project/service description
  - Requested billing amount (if specified)
  - Due date hints (ASAP, net 30, etc.)
  - Purchase order numbers

- **From Business Context:**
  - Company information from Company_Handbook.md
  - Standard rates from Business_Goals.md
  - Previous invoice history from Done/ folder
  - Client data from CRM or project files

### 3. Invoice Generation
- Creates professional PDF invoices
- Uses customizable templates
- Includes:
  - Company logo and branding
  - Invoice number (auto-incremented)
  - Date and due date
  - Client details
  - Line items (services/products)
  - Subtotal, tax, total
  - Payment terms
  - Payment instructions

### 4. Approval Workflow Integration
- Creates task file in `Pending_Approval/INVOICE_*.md`
- Includes all invoice metadata in frontmatter
- Attaches generated PDF for review
- Routes through auto-approver if amount < threshold
- Awaits manual approval for large invoices

### 5. Cross-Domain Bridge Integration
- Classifies invoice requests as BUSINESS domain
- Enriches with business context:
  - Company_Handbook: Business info, banking details
  - Business_Goals: Revenue tracking against targets
  - Previous invoices: Client billing history
- Distinguishes business invoices from personal receipts

## Triggers

### Email Triggers (Gmail Watcher)
```yaml
keywords:
  - "invoice"
  - "bill"
  - "payment"
  - "receipt"
  - "statement"
  - "purchase order"
  - "PO#"
  - "send invoice"
  - "please bill"
  - "charge for"
```

### Business Rule Triggers
- New project completion detected in Calendar
- Contract milestones reached
- Recurring billing dates (monthly/quarterly)
- Retainer replenishment alerts

## Input Data

The skill requires:

1. **Email Metadata** (from Gmail Watcher)
   ```yaml
   from: client@company.com
   subject: Project Completion - Please Send Invoice
   message_id: 1234567890abcdef
   received: 2026-01-21T12:00:00
   ```

2. **Email Content** (from Gmail Watcher task file)
   ```markdown
   ## Email Preview
   Hi [Your Name],

   The project deliverables have been completed. Please send us an invoice for the agreed amount of $5,000.

   Purchase Order: PO-2026-001
   Due Date: Within 30 days

   Best,
   Client Name
   ```

3. **Business Context** (from Cross-Domain Bridge)
   - Company name, address, contact info
   - Banking details for payment
   - Tax ID/VAT number
   - Standard payment terms
   - Previous invoice history

## Output

### 1. Invoice Task File
```markdown
---
type: invoice
action: generate_pdf
client: "Acme Corporation"
client_email: "billing@acme.com"
amount: 5000.00
currency: USD
invoice_number: INV-2026-001
po_number: PO-2026-001
due_date: 2026-02-20
status: pending_approval
---

# Invoice Request: INV-2026-001

## Client Information
- **Name:** Acme Corporation
- **Email:** billing@acme.com
- **PO Number:** PO-2026-001

## Invoice Details
- **Amount:** $5,000.00 USD
- **Due Date:** 2026-02-20 (Net 30)
- **Payment Terms:** Due within 30 days

## Line Items
1. **Project Development Services** - $5,000.00
   - Project completion as per contract
   - All deliverables submitted

## Source Email
From: client@acme.com
Subject: Project Completion - Please Send Invoice
Date: 2026-01-21

## Generated Invoice
[PDF will be attached after approval]
```

### 2. PDF Invoice
- Professional layout with company branding
- Itemized services/products
- Tax calculations
- Payment instructions
- QR code for online payment (optional)

### 3. Approval Routing
- **Low Amount (< $500):** Auto-approved by auto-approver
- **Medium Amount ($500-$5,000):** Auto-approved with review flag
- **High Amount (>$5,000):** Requires manual approval

## Usage Examples

### Example 1: Simple Invoice Request
```
User receives: "Please send invoice for $2,000 for Website Design"

→ Invoice generator:
  1. Extracts: Client name, amount, service description
  2. Creates invoice: INV-2026-042 for $2,000
  3. Generates PDF
  4. Creates approval task in Pending_Approval/
  5. Auto-approver approves (< $5,000 threshold)
  6. Approval processor sends invoice via email
```

### Example 2: Complex Invoice with Line Items
```
User receives: "Work completed on Phase 1 ($10,000) and Phase 2 ($15,000). Please invoice separately."

→ Invoice generator:
  1. Detects request for 2 separate invoices
  2. Creates INV-2026-043 ($10,000) and INV-2026-044 ($15,000)
  3. Both require manual approval (>$5,000 threshold)
  4. User reviews and approves in Pending_Approval/
  5. Sent to client separately
```

### Example 3: Recurring Invoice
```
Calendar event: "Monthly Retainer Invoice - Client ABC"

→ Invoice generator:
  1. Detects retainer billing trigger
  2. Retrieves standard retainer amount from Business_Goals
  3. Creates invoice for $5,000 (monthly retainer)
  4. Auto-approved (recurring/known amount)
  5. Sent automatically on 1st of month
```

## Integration Points

### 1. Gmail Watcher (Incoming)
- Provides email data when invoice keywords detected
- Creates initial task file in Needs_Action/

### 2. Cross-Domain Bridge (Context)
- Classifies as BUSINESS domain task
- Provides company information
- Enriches with business goals context

### 3. Auto-Approver (Approval)
- Uses amount-based approval rules
- Checks against spending limits
- Verifies client information

### 4. Approval Processor (Execution)
- Sends approved invoices via email_sender.py
- Moves completed tasks to Done/
- Logs invoice numbers for tracking

### 5. Business Goals Manager (Tracking)
- Records invoice against revenue targets
- Updates cash-flow projections
- Alerts on revenue shortfalls

## Configuration

### Environment Variables
```bash
# Invoice settings
INVOICE_TEMPLATE_PATH=./.claude/skills/invoice-generator/templates
INVOICE_OUTPUT_PATH=./Invoices
INVOICE_AUTO_APPROVE_THRESHOLD=5000
INVOICE_CURRENCY=USD
INVOICE_PAYMENT_TERMS="Net 30"
INVOICE_TAX_RATE=0

# Company info (from Company_Handbook.md)
INVOICE_COMPANY_NAME=""
INVOICE_COMPANY_ADDRESS=""
INVOICE_COMPANY_EMAIL=""
INVOICE_COMPANY_PHONE=""
INVOICE_BANK_NAME=""
INVOICE_BANK_ACCOUNT=""
```

### Invoice Numbering
- Format: `INV-YYYY-NNN`
- Auto-incremented per year
- Resets to 001 on January 1st
- Stored in `Invoices/last_invoice_number.txt`

## Error Handling

### Missing Client Information
```
[WARNING] Client address not found in email
[INFO] Using default billing address from Company_Handbook.md
[INFO] Flagging for manual review
```

### Ambiguous Amount
```
[WARNING] Multiple amounts found in email: $500, $1,000, $1,500
[INFO] Flagging for manual review
[TODO] Create task: "Clarify invoice amount for Client ABC"
```

### Duplicate Invoice Detection
```
[INFO] Checking for duplicate invoices...
[INFO] Found existing invoice INV-2026-042 for this client/project
[WARNING] Possible duplicate - flagging for manual review
```

## Templates

The skill includes these invoice templates:
1. **Standard Invoice** - General purpose, clean design
2. **Service Invoice** - Time-based billing, hourly rates
3. **Product Invoice** - Itemized products with quantities
4. **Recurring Invoice** - Retainer/maintenance billing
5. **Pro Forma Invoice** - Pre-payment estimate

## Dependencies

```python
# PDF generation
pip install reportlab

# Email integration (already installed)
pip install google-api-python-client

# Template rendering
pip install jinja2

# Data validation
pip install pydantic
```

## Testing

```bash
# Test invoice generation
cd .claude/skills/invoice-generator
python scripts/generate_invoice.py \
  --client "Acme Corp" \
  --amount 5000 \
  --service "Web Development" \
  --test

# Test email trigger detection
python scripts/test_email_detection.py \
  --email-file sample_invoice_request.eml
```

## Future Enhancements

1. **Online Payment Integration** - Add Stripe/PayPal links to invoices
2. **Invoice Reminders** - Automatic payment reminders before due date
3. **Multi-Currency** - Support for international clients
4. **Invoice Analytics** - Dashboard showing invoices, aging, trends
5. **QuickBooks Integration** - Sync with accounting software
6. **Recurring Invoice Schedules** - Automated billing for retainers
7. **Expense Tracking** - Link invoice to project costs

## Troubleshooting

### PDF Generation Fails
```bash
# Check reportlab installation
pip list | grep reportlab

# Test template rendering
python scripts/test_template.py
```

### Invoice Number Conflicts
```bash
# Check last invoice number
cat Invoices/last_invoice_number.txt

# Manually reset if needed
echo "INV-2026-001" > Invoices/last_invoice_number.txt
```

### Company Info Missing
```bash
# Verify Company_Handbook.md exists and has required fields
cat Company_Handbook.md | grep -A 10 "Company Information"
```

## Related Files

- `watchers/email_sender.py` - Sends approved invoices
- `watchers/approval_processor.py` - Processes invoice approvals
- `.claude/skills/cross-domain-bridge/` - Provides business context
- `.claude/skills/business-goals-manager/` - Tracks revenue
- `Company_Handbook.md` - Company information and banking details
- `Business_Goals.md` - Revenue targets and billing policies

---

**Skill Status:** ✅ Active
**Last Updated:** 2026-01-21
**Maintained By:** AI Employee Vault System
