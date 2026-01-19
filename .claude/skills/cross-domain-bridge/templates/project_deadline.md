# Project Deadline Template

**Trigger Keywords:** deadline, due date, milestone, delivery, submission

**Workflow Steps:**

1. **Identify Project** (Business_Goals.md / Odoo)
   - Lookup project details
   - Check current status
   - Verify deadline

2. **Calculate Deadline Proximity**
   - Critical: Due today or overdue
   - High: Due within 2 days
   - Medium: Due within 7 days
   - Low: Due > 7 days out

3. **Assess Completion Status**
   - What % complete?
   - What's remaining?
   - Any blockers?

4. **Generate Risk Assessment**
   - High risk: Deadline close + low completion + blockers
   - Medium risk: Deadline close or low completion
   - Low risk: On track

5. **Suggest Actions**
   - Reschedule if needed
   - Reprioritize tasks
   - Allocate resources
   - Communicate with client

**Example Enrichment:**

```yaml
---
type: project_deadline
domain: business
business_relevance_score: 0.85
entities_extracted:
  projects: ["Project Alpha"]
  keywords: ["deadline", "milestone"]
enriched_at: 2026-01-19T10:30:00Z
enriched_by: cross-domain-bridge
deadline_proximity: 2_days
completion_percent: 65
risk_level: high
---

Project Alpha deadline reminder: Due in 2 days

## Cross-Domain Analysis

**Project Details:**
- Project: Project Alpha
- Client: Client A (25% of monthly revenue)
- Deadline: 2026-01-21 (2 days)
- Current Status: 65% complete
- Remaining: User testing, documentation, bug fixes

**Risk Assessment: HIGH**

**Risk Factors:**
- Only 65% complete with 2 days remaining
- 35% remaining work is significant
- Client is high-value (25% of revenue)
- Missing deadline could damage relationship

## Recommendations

**[IMMEDIATE ACTION REQUIRED]**

**Priority Plan:**
1. **Today (Day 1):**
   - Focus: Complete user testing (4 hours)
   - Focus: Fix critical bugs (4 hours)

2. **Tomorrow (Day 2):**
   - Morning: Write documentation (3 hours)
   - Afternoon: Final testing and polish (3 hours)
   - Evening: Deliver to client (2 hours)

**Total Work:** ~16 hours over 2 days
**Feasible:** Yes, but requires focused effort

**Client Communication:**
Send update today:
```
Subject: Project Alpha Status Update

Hi [Client Name],

Quick update on Project Alpha: We're 65% complete and on track
for our January 21st deadline.

Remaining work: User testing, documentation, and final polish.

I'll send another update tomorrow as we approach completion.

Best,
[Your Name]
```

**Contingency Plan:**
If unable to complete:
1. Communicate early (don't wait until deadline)
2. Propose realistic new deadline
3. Explain what's causing delay
4. Offer partial delivery if possible

## Resource Allocation
Consider:
- Blocking other work for next 2 days
- Declining new meetings
- Focusing purely on Project Alpha

## Calendar Check
[ ] Clear calendar for next 2 days
[ ] Reschedule non-essential meetings
[ ] Set focused work blocks
[ ] Enable do-not-disturb

## Success Criteria
- [ ] User testing completed
- [ ] Critical bugs fixed
- [ ] Documentation written
- [ ] Client delivery made on time
- [ ] Client satisfaction confirmed
```

**Success Criteria:**
- Deadline proximity calculated correctly
- Risk assessed accurately
- Action plan generated
- Client communication suggested
- Contingency planning done
