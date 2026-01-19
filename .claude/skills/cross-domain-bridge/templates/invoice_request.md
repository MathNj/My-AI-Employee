# Invoice Request Template

**Trigger Keywords:** invoice, bill, payment, statement, send me the invoice

**Workflow Steps:**

1. **Verify Client** (Business_Goals.md)
   - Check if client is in active projects
   - Verify client is legitimate

2. **Check Unbilled Work** (Odoo/Accounting)
   - Query for unbilled hours/projects
   - Calculate total amount

3. **Generate Invoice Draft**
   - Create invoice with line items
   - Save to /Accounting/Drafts/

4. **Check Approval Requirements** (Company_Handbook.md)
   - Amount > $1,000 → Manual approval
   - New client → Manual approval
   - Standard client → Auto-approve if < threshold

5. **Create Approval Request** (if needed)
   - Move to /Pending_Approval/
   - Include invoice draft
   - Wait for human approval

6. **Send Invoice** (after approval)
   - Use email-sender skill
   - Attach PDF invoice
   - Log to /Logs/

**Example Enrichment:**

```yaml
---
type: invoice_request
domain: business
business_relevance_score: 0.95
entities_extracted:
  clients: ["Client A"]
  keywords: ["invoice", "payment"]
  amounts: ["2500"]
approval_required: true
approval_reason: "Amount $2,500 exceeds $1,000 threshold"
enriched_at: 2026-01-19T10:30:00Z
enriched_by: cross-domain-bridge
workflow_status: pending_approval
---

Can you send me the invoice for January work?

## Cross-Domain Analysis

**Context:**
- Client: Client A (25% of monthly revenue)
- Project: Project Alpha (80% complete, due 2026-01-30)
- Unbilled Amount: $2,500

**Action Required:**
1. Generate invoice for $2,500
2. Create approval request in /Pending_Approval/
3. Awaiting human approval

## Recommendation
This is a high-value client with standard invoice request.
Auto-approve if client is known and amount < $5,000.
```

**Success Criteria:**
- Invoice generated correctly
- Approval workflow followed
- Invoice sent successfully
- Transaction logged
