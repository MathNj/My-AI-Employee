# Cross-Domain Integration Guide

## Overview

Cross-domain integration is the **critical missing piece** that transforms your AI Employee from separate silos into a unified, intelligent system that can reason across Personal and Business contexts.

**Current State (Without Cross-Domain Integration):**
```
┌─────────────────┐         ┌─────────────────┐
│  Personal       │         │   Business      │
│  Domain         │         │   Domain        │
├─────────────────┤         ├─────────────────┤
│ Gmail Watcher   │         │ Calendar        │
│ WhatsApp Watcher│         │ Slack           │
│ Bank/Finance    │         │ Odoo Accounting │
│                 │         │                 |
│ Processes       │         │ Processes       │
│ independently   │         │ independently   │
└─────────────────┘         └─────────────────┘
```

**Target State (With Cross-Domain Integration):**
```
                    ┌──────────────────┐
                    │  Unified Reasoning│
                    │   (Claude Code)   │
                    └────────┬──────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Personal    │    │   Business   │    │   Context    │
│  Domain      │◄──►│   Domain     │◄──►│   Bridge     │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ Gmail        │    │ Odoo         │    │ Business_    │
│ WhatsApp     │    │ Calendar     │    │   Goals.md   │
│ Bank/Finance │    │ LinkedIn     │    │ Company_     │
│              │    │ Projects     │    │   Handbook.md│
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## What is Cross-Domain Integration?

Cross-domain integration means that **data from one domain informs decisions in another domain**. Your AI Employee shouldn't just react to inputs in isolation—it should understand the full context.

### Example Scenarios

#### **Scenario 1: Invoice Request (WhatsApp → Business → Accounting)**
**Without Integration:**
```
WhatsApp: "Can you send me the invoice?"
AI: "I'll notify you about this message."
```

**With Integration:**
```
WhatsApp: "Can you send me the invoice?"
AI Reasoning:
  1. Recognize: Client asking for invoice
  2. Check Business Context: Business_Goals.md shows "Client Project A" active
  3. Check Accounting: Odoo has unbilled hours for this client
  4. Cross-check: Company_Handbook.md approves sending invoices
  5. Action: Create invoice in Odoo → Draft email → Request approval
  6. Response: "I've prepared your invoice ($2,500) and moved it to /Pending_Approval"
```

#### **Scenario 2: Payment Received (Bank → Business → Goals)**
**Without Integration:**
```
Bank: "Received $3,000 from Client A"
AI: "Logged transaction"
```

**With Integration:**
```
Bank: "Received $3,000 from Client A"
AI Reasoning:
  1. Recognize: Payment received
  2. Check Business Goals: Monthly target $15,000, currently at $12,000
  3. Update Dashboard: Revenue now $15,000 (100% of target!)
  4. Update Business_Goals.md: Mark monthly target achieved
  5. Proactive Alert: "You've hit your monthly revenue target! Consider:
      - Sending client thank you note
      - Reinvesting excess into Business Development initiative"
```

#### **Scenario 3: Urgent Email During Personal Time (Gmail → Calendar → Business)**
**Without Integration:**
```
Gmail: "Urgent: Server down at Client B!"
AI: "New email marked urgent"
```

**With Integration:**
```
Gmail: "Urgent: Server down at Client B!"
AI Reasoning:
  1. Recognize: Urgent client issue
  2. Check Calendar: You're in "Personal Time - Family Dinner"
  3. Check Business Context: Client B is high-value client (15% of revenue)
  4. Check Company_Handbook: "Emergency response within 30 min for >10% revenue clients"
  5. Cross-Check: Is this actually an emergency? (analyze content)
  6. Decision: Notify with priority level
  7. Response: "High-priority client issue detected. You're in personal time.
       Client B represents 15% of monthly revenue.
       Mark as urgent (interrupt) or handle at 9 AM?"
```

---

## Architecture: How Cross-Domain Integration Works

### **Layer 1: Perception (Watchers) - Collect Context**

Each watcher enriches its data with domain tags:

```python
# whatsapp_watcher.py (enhanced)
def create_action_file(self, message):
    # Existing: Basic message capture
    content = f"""
    ---
    type: whatsapp_message
    from: {sender}
    domain: personal
    timestamp: {now}
    """

    # NEW: Cross-domain enrichment
    if self.is_business_related(message):
        content += f"""
    business_context: true
    potential_client: true
    detected_keywords: [invoice, payment, project]
    """
```

### **Layer 2: Context Bridge - Unify Understanding**

Create a new skill: `cross-domain-bridge`

```yaml
# .claude/skills/cross-domain-bridge/SKILL.md
name: cross-domain-bridge
description: "Bridges Personal and Business domains for unified reasoning"
```

**Responsibilities:**
1. **Maintain Shared Context:**
   - Read Business_Goals.md
   - Read Company_Handbook.md
   - Read current Dashboard.md

2. **Enrich Incoming Messages:**
   ```python
   # When new item arrives in /Needs_Action
   def enrich_with_context(item):
       # Extract key entities
       entities = extract_entities(item)

       # Lookup in business context
       for entity in entities:
           if entity in Business_Goals.active_clients:
               item.metadata['client_value'] = get_client_revenue(entity)
               item.metadata['project_status'] = get_project_status(entity)

       # Lookup in personal context
       if item.domain == 'business' and is_after_hours():
           item.metadata['interrupt_check'] = True
       ```

3. **Provide Decision Support:**
   ```python
   def cross_domain_reasoning(item):
       context = {
           'business': get_business_context(),
           'personal': get_personal_context(),
           'rules': get_company_rules()
       }

       return analyze_cross_domain_impact(item, context)
   ```

### **Layer 3: Unified Reasoning (Claude Code)**

When processing /Needs_Action, Claude now has full context:

```
Task: Process EMAIL_client_project_update.md

Available Context:
  [x] Email content
  [x] Business_Goals: "Client Project A" = 35% of monthly revenue
  [x] Company_Handbook: "Check project status before responding"
  [x] Odoo: Project deadline in 3 days, 80% complete
  [x] Calendar: You have project meeting tomorrow 2 PM

Decision: This email affects a high-value project nearing deadline.
Action: Schedule review meeting, update project status, flag for attention.
```

---

## Implementation Steps

### **Step 1: Create Context Bridge Skill**

```bash
# Create the skill structure
mkdir -p .claude/skills/cross-domain-bridge/{scripts,references}
```

**Key files:**
- `SKILL.md` - Documentation
- `scripts/enrich_context.py` - Enrich items with cross-domain data
- `scripts/cross_domain_analysis.py` - Analyze impact across domains

### **Step 2: Enhance Watchers**

Modify existing watchers to add domain tags:

```python
# In all watchers
metadata = {
    'domain': classify_domain(message),  # 'personal', 'business', 'both'
    'business_relevance': score_business_importance(message),
    'entities': extract_business_entities(message)
}
```

### **Step 3: Auto-Approver Enhancement**

Update `auto_approver_watcher.py` to use cross-domain context:

```python
# Current: Rule-based analysis
# Enhanced: Include business context

def auto_approve_with_context(item):
    # Get cross-domain context
    context = cross_domain_bridge.get_context(item)

    # Check business impact
    if context.get('client_revenue_percent', 0) > 20:
        return {
            'decision': 'manual_review',
            'reason': f"High-value client ({context['client_revenue_percent']}% revenue)"
        }

    # Check personal boundaries
    if context.get('is_after_hours') and context.get('business_importance') == 'low':
        return {
            'decision': 'defer',
            'reason': 'Non-urgent business matter during personal time',
            'suggested_action': 'Handle at 9 AM next business day'
        }
```

### **Step 4: Create Cross-Domain Templates**

**Template: Invoice Request**
```yaml
# .claude/skills/cross-domain-bridge/templates/invoice_request.md
trigger_keywords: [invoice, bill, payment, statement]
required_context:
  - Business_Goals.active_clients
  - Odoo.invoices Outstanding
  - Company_Handbook.approval_limits
workflow:
  1. Verify client in Business_Goals
  2. Check Odoo for unbilled work
  3. Generate invoice draft
  4. Check Company_Handbook for approval requirements
  5. Create approval request if needed
```

**Template: Payment Received**
```yaml
# .claude/skills/cross-domain-bridge/templates/payment_received.md
trigger_keywords: [payment received, deposit, transfer]
required_context:
  - Business_Goals.revenue_targets
  - Odoo.invoices unpaid
  - Dashboard.current_revenue
workflow:
  1. Match payment to invoice in Odoo
  2. Update Dashboard revenue
  3. Check progress vs Business_Goals targets
  4. Generate proactive suggestions if milestone hit
  5. Update Business_Goals.md progress
```

### **Step 5: Update CEO Briefing**

Add cross-domain insights:

```markdown
## Monday Morning CEO Briefing - Cross-Domain Insights

### Personal → Business Overlap
- [ ] 3 client WhatsApp messages during personal time (1 urgent)
- [ ] 5 after-hours emails (2 required response)

### Business → Personal Impact
- [ ] Project deadline week -> High meeting load expected
- [ ] Client visit scheduled -> Block personal time Friday

### Recommendations
- Consider setting "office hours" for client WhatsApp
- Delegate Project X to reduce meeting load
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    INCOMING DATA                             │
└──────┬──────────────┬──────────────┬──────────────┬─────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
   Gmail        WhatsApp      Bank API      File Drop
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Context Bridge        │
         │  (cross-domain-bridge)  │
         └────────┬───────────────┘
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Enrich with  │      │ Classify by  │
│ Business     │      │ Domain &     │
│ Context      │      │ Priority     │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Needs_Action/  │
         │  (enriched)    │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Claude Code    │
         │ (reasoning)    │
         └────────┬───────┘
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Personal     │      │ Business     │
│ Response     │      │ Action       │
└──────────────┘      └──────────────┘
```

---

## Testing Cross-Domain Integration

### **Test Case 1: Invoice Request**
```bash
# Simulate WhatsApp message
echo "Can you send me the invoice for January?" > \
  Needs_Action/WHATSAPP_client_invoice_request.md

# Run cross-domain bridge
python .claude/skills/cross-domain-bridge/scripts/enrich_context.py \
  --file Needs_Action/WHATSAPP_client_invoice_request.md

# Expected: File enriched with:
# - Client lookup from Business_Goals
# - Odoo project status
# - Approval requirements from Company_Handbook
```

### **Test Case 2: After-Hours Urgent Email**
```bash
# Simulate urgent email
# Run during personal time (evening/weekend)

# Expected: Cross-domain bridge flags for manual review
# due to high business importance vs personal boundary
```

### **Test Case 3: Payment Milestone**
```bash
# Simulate payment reaching monthly target

# Expected:
# - Dashboard updated
# - Business_Goals.md marked as achieved
# - Proactive suggestions generated
# - Celebration notification
```

---

## Priority Matrix for Implementation

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| Context Bridge Skill | HIGH | Medium | **DO FIRST** |
| Business Entity Extraction | HIGH | Medium | **DO FIRST** |
| Auto-Approver Enhancement | HIGH | Low | **SECOND** |
| Watcher Domain Tagging | MEDIUM | Low | **SECOND** |
| CEO Briefing Cross-Domain | MEDIUM | Low | **THIRD** |
| Personal Time Boundary | MEDIUM | Medium | **FOURTH** |
| Advanced Templates | LOW | High | **LATER** |

---

## Quick Start Implementation

**Minimum Viable Cross-Domain Integration (2-4 hours):**

1. **Create Context Bridge Skill** (1 hour)
   - Build `enrich_context.py`
   - Read Business_Goals.md and Company_Handbook.md
   - Simple entity extraction (client names, project names)

2. **Enhance Auto-Approver** (30 min)
   - Add cross-domain checks
   - Use business context for approval decisions

3. **Update Watchers** (1 hour)
   - Add domain classification
   - Tag business-related messages

4. **Test & Iterate** (1 hour)
   - Create test scenarios
   - Verify end-to-end flow

---

## Key Benefits

**With Cross-Domain Integration:**

1. **Intelligent Prioritization**
   - Knows which clients matter most
   - Understands deadlines and commitments
   - Respects personal time boundaries

2. **Proactive Insights**
   - "You're 80% to monthly revenue goal"
   - "Client meeting tomorrow - prep materials attached"
   - "Invoice overdue - follow up recommended"

3. **Reduced Cognitive Load**
   - AI surfaces what's important
   - Filters noise during personal time
   - Provides context, not just notifications

4. **Better Business Decisions**
   - Sees full picture (personal + business)
   - Identifies conflicts before they happen
   - Optimizes schedule across domains

---

## Next Steps

**To implement cross-domain integration, run:**

```bash
# I can create the cross-domain-bridge skill
# Would you like me to build it now?
```

**Estimated time:** 2-4 hours for MVP
**Impact:** Transforms AI from reactive to proactive, unified intelligence

---

**Status:** DOCUMENTATION COMPLETE
**Action Required:** Build cross-domain-bridge skill
