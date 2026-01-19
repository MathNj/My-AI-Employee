# Urgent Client Issue Template

**Trigger Keywords:** urgent, emergency, asap, problem, issue, critical, server down

**Workflow Steps:**

1. **Assess Client Value** (Business_Goals.md)
   - Check client revenue contribution
   - Check if top client (>20% revenue)

2. **Check Personal Time** (Calendar/Time)
   - Is it currently personal time?
   - Is it weekend/evening?

3. **Assess Urgency Level**
   - Critical: System down, data loss, security breach
   - High: Feature broken, deadline at risk
   - Medium: Bug, question
   - Low: General inquiry

4. **Determine Response Strategy**
   - High-value client + critical urgency = IMMEDIATE INTERRUPT
   - High-value client + high urgency = Respond within 30 min
   - Low-value client + critical = Respond within 2 hours
   - Low-value client + non-critical = Next business day

5. **Notify Accordingly**
   - Immediate: Push notification + call
   - High: Email + SMS
   - Medium: Email marked urgent
   - Low: Normal queue

**Example Enrichment:**

```yaml
---
type: urgent_client_issue
domain: cross_domain
business_relevance_score: 0.9
entities_extracted:
  clients: ["Client B"]
  keywords: ["urgent", "server", "down"]
enriched_at: 2026-01-19T20:00:00Z
enriched_by: cross-domain-bridge
personal_boundary_violation: true
urgency_level: critical
---

URGENT: Server is down! Need immediate assistance.

## Cross-Domain Analysis

**Context:**
- Client: Client B (15% of monthly revenue)
- Issue: Server down (production impact)
- Time: 8:00 PM (personal time)
- Urgency: CRITICAL

**Decision: INTERRUPT RECOMMENDED**

**Reasoning:**
Although this is during personal time, Client B represents 15% of your monthly revenue, and the issue is critical (server down). This warrants immediate attention.

## Recommendations

**[IMMEDIATE ACTION REQUIRED]**

1. **Interrupt personal time** - This is justified
2. **Assess severity** - Is entire system down or single service?
3. **Client communication** - Acknowledge immediately, even if just "Looking into it"
4. **Resolution plan** - Estimate fix time and communicate
5. **Post-mortem** - Schedule review to prevent recurrence

## Response Template
```
Subject: RE: URGENT - Server Down

Hi [Client Name],

I've received your message and I'm looking into this immediately.

I understand this is critical and I'm prioritizing it now.

Will update you within 15 minutes with status.

Best,
[Your Name]
```

## Personal Boundary Note
Normally I would defer business matters to 9 AM next business day, but given:
- Client revenue impact (15% of monthly)
- Critical severity (server down)
- Potential business continuity impact

Immediate response is warranted and aligned with Company Handbook guidelines.
```

**Success Criteria:**
- Client value assessed correctly
- Urgency accurately determined
- Appropriate response strategy chosen
- Human notified correctly
- Issue resolved efficiently
