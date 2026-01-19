---
name: cross-domain-bridge
description: "Bridges Personal and Business domains for unified AI reasoning. Enriches incoming items with cross-domain context from Business_Goals, Company_Handbook, Odoo, and other sources."
---

# Cross-Domain Bridge

## Overview

The Cross-Domain Bridge skill unifies Personal and Business domains by enriching incoming items (emails, WhatsApp messages, etc.) with relevant context from business systems.

**Problem Solved:**
- Without cross-domain integration, Gmail/WhatsApp don't know about your business goals, projects, or client relationships
- The AI processes each domain in isolation
- No unified decision-making across personal and business contexts

**Solution:**
- Extract business entities (client names, project names, keywords)
- Enrich items with business context (revenue, deadlines, approval rules)
- Enable intelligent prioritization and auto-approval decisions

---

## When to Use

### ✅ Use this skill when:
- Processing items in /Needs_Action folder
- Auto-approver needs business context for decisions
- CEO Briefing requires cross-domain insights
- Personal boundary checking (urgent business during personal time)

### ❌ Do NOT use when:
- Purely personal tasks (no business relevance)
- Simple domain-specific actions
- Testing individual watchers in isolation

---

## Core Capabilities

### 1. Context Enrichment
Extracts business entities and enriches with:
- Business_Goals.md (revenue targets, active projects)
- Company_Handbook.md (approval rules, policies)
- Dashboard.md (current status, metrics)
- Odoo (client invoices, project status - when available)

### 2. Domain Classification
Classifies items as:
- **Personal:** No business relevance
- **Business:** Business-related only
- **Cross-Domain:** Affects both domains (urgent client issue, etc.)

### 3. Priority Scoring
Scores items based on:
- Client revenue contribution
- Project deadline proximity
- Rule requirements (approval limits, etc.)
- Personal boundary violations

---

## Quick Start

```bash
# Enrich a single file
python .claude/skills/cross-domain-bridge/scripts/enrich_context.py \
  --file Needs_Action/EMAIL_client_xyz.md

# Enrich all files in Needs_Action
python .claude/skills/cross-domain-bridge/scripts/enrich_context.py \
  --all

# Analyze cross-domain impact
python .claude/skills/cross-domain-bridge/scripts/analyze_cross_domain.py \
  --file Needs_Action/WHATSAPP_invoice_request.md
```

---

## Data Flow

```
Incoming Item (email, WhatsApp, etc.)
    ↓
Extract Entities (client names, projects, keywords)
    ↓
Lookup Business Context
    ├── Business_Goals.md (revenue, projects)
    ├── Company_Handbook.md (rules, policies)
    ├── Dashboard.md (current status)
    └── Odoo (invoices, projects) [optional]
    ↓
Enrich Item with Context
    ├── Add domain classification
    ├── Add business relevance score
    ├── Add client/project data
    └── Add approval requirements
    ↓
Output Enriched Item
    ├── Updated frontmatter
    ├── Context section
    └── Recommendations
```

---

## Integration Points

### Auto-Approver Integration
The auto-approver uses enriched context to make smarter decisions:

```python
# Auto-approver checks enriched context
if item.enriched_context.get('client_revenue_percent', 0) > 20:
    # High-value client - manual review required
    return 'manual_review'
```

### Watcher Integration
Watchers call enrich_context after creating items:

```python
# After creating action file
enrich_context(item_path)
```

### CEO Briefing Integration
Weekly briefing analyzes cross-domain patterns:

```python
# Get cross-domain insights
insights = get_cross_domain_insights(week_data)
```

---

## Templates

Common cross-domain scenarios:
- `invoice_request.md` - Invoice requests via WhatsApp/email
- `payment_received.md` - Payment notifications
- `urgent_client_issue.md` - Urgent client matters
- `project_deadline.md` - Project deadline reminders

See `/templates` folder for details.

---

## Configuration

**File:** `.claude/skills/cross-domain-bridge/config/config.json`

```json
{
  "business_keywords": ["invoice", "payment", "project", "deadline", "client"],
  "personal_boundary_hours": {"start": 18, "end": 9, "weekend": true},
  "high_value_client_threshold": 15,
  "approval_threshold": 1000
}
```

---

## Logging

All enrichment activities logged to:
- `/Logs/cross_domain_YYYY-MM-DD.json`

Format:
```json
{
  "timestamp": "2026-01-19T10:30:00Z",
  "action": "context_enrichment",
  "file": "EMAIL_client_xyz.md",
  "entities_extracted": ["Client A", "Project Alpha"],
  "domain_classification": "business",
  "business_relevance_score": 0.85
}
```

---

## Error Handling

- Missing Business_Goals.md: Warning logged, continues with basic enrichment
- Missing Company_Handbook.md: Warning logged, uses default rules
- Odoo connection failure: Gracefully degrades, continues with vault data only

---

## Future Enhancements

- [ ] Machine learning for entity extraction
- [ ] Historical context (past interactions with client)
- [ ] Sentiment analysis for urgency detection
- [ ] Cross-domain workflow orchestration
- [ ] Integration with calendar for meeting context
