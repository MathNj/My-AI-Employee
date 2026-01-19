# Payment Received Template

**Trigger Keywords:** payment received, deposit, transfer, payment confirmation

**Workflow Steps:**

1. **Match Payment to Invoice** (Odoo/Accounting)
   - Query for outstanding invoices
   - Match by amount and client
   - Mark invoice as paid

2. **Update Dashboard** (Dashboard.md)
   - Add payment to revenue
   - Update month-to-date total
   - Refresh metrics

3. **Check Progress vs Goals** (Business_Goals.md)
   - Calculate % of monthly target achieved
   - Check if milestone reached
   - Generate insights

4. **Generate Proactive Suggestions**
   - If milestone hit: Celebrate, suggest reinvestment
   - If ahead of target: Suggest bonus or investment
   - If behind target: Suggest acceleration activities

5. **Update Business_Goals.md**
   - Mark progress if milestone hit
   - Update progress tracking section

**Example Enrichment:**

```yaml
---
type: payment_received
domain: business
business_relevance_score: 1.0
entities_extracted:
  clients: ["Client A"]
  keywords: ["payment", "received"]
  amounts: ["3000"]
enriched_at: 2026-01-19T10:30:00Z
enriched_by: cross-domain-bridge
workflow_status: processed
---

Payment received from Client A: $3,000

## Cross-Domain Analysis

**Payment Details:**
- Amount: $3,000
- Client: Client A (25% of monthly revenue)
- Invoice: INV-2026-001 (now marked paid)

**Goal Progress:**
- Monthly Target: $15,000
- Before Payment: $12,000 (80%)
- After Payment: $15,000 (100%)
- Status: TARGET ACHIEVED!

## Proactive Suggestions

**[CELEBRATION] Monthly Revenue Target Achieved!**
Congratulations! You've hit your $15,000 monthly target.

**Recommended Actions:**
1. Send thank you note to Client A
2. Consider reinvesting excess into Business Development initiative
3. Update Business_Goals.md to mark monthly target complete
4. Treat yourself (you've earned it!)

## Next Steps
- [ ] Update Business_Goals.md progress
- [ ] Send client thank you email
- [ ] Log transaction to Accounting
- [ ] Update Dashboard metrics
```

**Success Criteria:**
- Payment matched to invoice
- Dashboard updated
- Progress calculated correctly
- Proactive suggestions generated
- Business goals updated
