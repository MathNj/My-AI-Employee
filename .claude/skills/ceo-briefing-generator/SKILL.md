---
name: ceo-briefing-generator
description: Generate comprehensive Monday Morning CEO Briefings with weekly business audit, financial analysis, and proactive recommendations. Use when the user needs to (1) Generate weekly business summary, (2) Audit accounting and subscriptions, (3) Track revenue vs goals, (4) Identify bottlenecks, (5) Get proactive business recommendations, or (6) Create executive reports. Triggers include "generate CEO briefing", "weekly business audit", "Monday briefing", "business summary", "audit subscriptions", "revenue report".
---

# CEO Briefing Generator

Automated weekly business audit and executive briefing system that analyzes financial data, project progress, and operational metrics to deliver actionable insights every Monday morning.

## Quick Start

### Generate Weekly Briefing

```bash
# Full weekly briefing
python scripts/generate_briefing.py --period week

# Custom date range
python scripts/generate_briefing.py --start 2026-01-01 --end 2026-01-07

# Specific sections only
python scripts/generate_briefing.py --sections revenue,tasks,subscriptions
```

### Audit Subscriptions

```bash
# Full subscription audit
python scripts/audit_subscriptions.py

# Check for unused (>30 days)
python scripts/audit_subscriptions.py --unused-days 30

# Generate recommendations
python scripts/audit_subscriptions.py --recommend
```

---

## Core Workflow

### Weekly Briefing Generation

**Triggered:** Every Sunday 11:00 PM (via scheduler-manager)

```
Sunday 11:00 PM
    ↓
ceo-briefing-generator activates
    ↓
Data Collection:
  - xero-integrator: Revenue & expenses
  - financial-analyst: Trend analysis
  - social-media-manager: Engagement metrics
  - Task files: Completed work
  - Business_Goals.md: Targets
    ↓
Analysis:
  - Revenue vs target
  - Expense trends
  - Task bottlenecks
  - Subscription audit
  - Social media ROI
    ↓
Generate CEO Briefing
    ↓
Save to /Briefings/Monday_Briefing_YYYY-MM-DD.md
    ↓
Update Dashboard with summary
    ↓
Ready for Monday morning review
```

---

## Data Sources

### Financial Data (xero-integrator)

**Required Files:**
- `/Accounting/Transactions_YYYY-MM.md` - Recent transactions
- `/Accounting/Reports/YYYY-MM_ProfitLoss.md` - P&L statement

**Data Points:**
- Revenue this week
- Expenses by category
- Cash flow
- Unpaid invoices
- Subscription charges

### Business Goals

**Required File:**
- `/Business_Goals.md`

**Structure:**
```markdown
---
last_updated: 2026-01-07
review_frequency: weekly
---

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |

### Active Projects
1. Project Alpha - Due Jan 15 - Budget $2,000
2. Project Beta - Due Jan 30 - Budget $3,500

### Subscription Audit Rules
Flag for review if:
- No login in 30 days
- Cost increased > 20%
- Duplicate functionality with another tool
```

### Task Progress

**Required Folder:**
- `/Tasks/Done/` - Completed tasks this week

**Analysis:**
- Tasks completed vs planned
- Average completion time
- Blocked or delayed tasks
- Team velocity

### Social Media Performance

**Required:**
- Integration with social-media-manager skill

**Metrics:**
- Posts published
- Total engagement
- Follower growth
- Best performing content

---

## Briefing Sections

### 1. Executive Summary

**3-sentence overview:**
- Revenue status (on/off track)
- Key wins this week
- Critical alerts

**Example:**
```markdown
## Executive Summary

Strong week with revenue ahead of target. Major milestone: launched new product with 50+ early adopters. One bottleneck identified in client onboarding process.
```

### 2. Financial Performance

**Revenue Analysis:**
- This week revenue: $2,450
- Month-to-date: $4,500 (45% of $10,000 target)
- Trend: On track / Behind / Ahead
- Comparison to last week: +15%

**Expense Analysis:**
- Total expenses this week
- Breakdown by category
- Unusual charges flagged
- Budget variance

**Cash Flow:**
- Current balance
- Projected end-of-month
- Outstanding invoices
- Upcoming payments

**Example:**
```markdown
## Financial Performance

### Revenue
- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track
- **vs Last Week**: +15% growth

### Expenses
- **Total**: $1,890
- **Software & Subscriptions**: $490
- **Marketing**: $1,200
- **Office Supplies**: $200

### Cash Flow
- **Current Balance**: $15,250
- **Projected EOM**: $18,500
- **Outstanding Invoices**: $3,200 (2 clients)
```

### 3. Project & Task Analysis

**Completed Tasks:**
- List of major tasks completed
- Time spent vs estimated
- Blockers encountered

**Bottlenecks:**
- Tasks taking longer than expected
- Blocked tasks
- Resource constraints

**Upcoming Deadlines:**
- This week
- Next 2 weeks
- Overdue items

**Example:**
```markdown
## Project & Task Progress

### Completed This Week
- ✅ Client A proposal delivered (Est: 2 days, Actual: 2 days)
- ✅ Product launch preparation (Est: 3 days, Actual: 5 days) ⚠️
- ✅ Q4 financial review completed

### Bottlenecks
| Task | Expected | Actual | Delay | Impact |
|------|----------|--------|-------|--------|
| Client B proposal | 2 days | 5 days | +3 days | High - Delayed revenue |

### Upcoming Deadlines
- **This Week**: Project Alpha final delivery (Jan 15)
- **Next 2 Weeks**: Quarterly tax prep (Jan 31)
```

### 4. Subscription Audit

**Automated Detection:**
- Active subscriptions identified
- Usage patterns analyzed
- Cost optimization opportunities
- Duplicate services flagged

**Subscription Patterns (from Requirements.md):**
```python
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Entertainment',
    'spotify.com': 'Entertainment',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    'github.com': 'GitHub',
    'zoom.us': 'Zoom',
    'dropbox.com': 'Dropbox',
    'google.com/workspace': 'Google Workspace',
    'microsoft.com/microsoft-365': 'Microsoft 365',
}
```

**Audit Criteria:**
- No activity in 30+ days
- Cost increase > 20%
- Duplicate functionality
- Unused seats/licenses

**Example:**
```markdown
## Subscription Audit

### Active Subscriptions (12 total, $847/month)

✅ **Recommended to Keep:**
- **Xero** - $35/month - Daily usage, essential
- **GitHub** - $21/month - Daily usage, essential
- **Google Workspace** - $72/month - Daily usage, essential

⚠️ **Review Recommended:**
- **Notion** - $15/month - No activity in 45 days
  - **Action**: Cancel? Team not using, duplicate with Google Docs
  - **Annual Savings**: $180

- **Adobe Creative Cloud** - $54.99/month - Limited usage (2 times/month)
  - **Action**: Consider downgrading to Photography plan ($19.99/month)
  - **Annual Savings**: $420

- **Slack** - $8/user/month (5 users = $40) - Low team engagement
  - **Action**: Consolidate to free tier or use Teams
  - **Annual Savings**: $480

### Potential Annual Savings: $1,080
```

### 5. Social Media Summary

**Integration:** social-media-manager skill

**Metrics:**
- Posts published this week
- Total reach/impressions
- Engagement rate
- Follower growth
- Best performing post

**Example:**
```markdown
## Social Media Performance

### This Week
- **Posts Published**: 12 (3 per platform)
- **Total Impressions**: 15,000
- **Total Engagement**: 450 (3.0% rate)
- **Follower Growth**: +25 followers

### Top Performing Post
**Platform**: Instagram
**Content**: "Behind the scenes at our new office..."
**Impressions**: 5,000
**Engagement**: 280 likes, 45 comments

### Recommendation
Instagram continues to outperform. Consider increasing Instagram content to 5 posts/week.
```

### 6. Proactive Recommendations

**AI-Generated Insights:**
- Cost optimization opportunities
- Revenue growth suggestions
- Process improvements
- Risk alerts

**Categories:**
1. **Financial** - Cost savings, revenue opportunities
2. **Operational** - Process bottlenecks, efficiency gains
3. **Strategic** - Growth opportunities, competitive threats
4. **Risk** - Cash flow concerns, client dependencies

**Example:**
```markdown
## Proactive Recommendations

### Cost Optimization 🎯
1. **Subscription Cleanup**: Cancel Notion ($15/mo), downgrade Adobe ($35/mo savings)
   - **Impact**: $600/year savings
   - **Action**: Review with team, implement next week

2. **Payment Terms**: 2 invoices unpaid >30 days ($3,200)
   - **Impact**: Cash flow risk
   - **Action**: Follow up with clients this week

### Revenue Growth 💰
3. **Client A Expansion**: Usage increased 150% this quarter
   - **Impact**: Upsell opportunity ($500-1,000/month)
   - **Action**: Schedule expansion discussion

4. **Social Media ROI**: Instagram engagement 5%, well above 3% average
   - **Impact**: Lead generation opportunity
   - **Action**: Increase Instagram posting frequency

### Process Improvements ⚙️
5. **Client Onboarding**: Average 5 days vs 2 days target
   - **Impact**: Delayed revenue, poor experience
   - **Action**: Review onboarding checklist, automate steps
```

### 7. Key Metrics Dashboard

**Weekly Snapshot:**
- Revenue vs target: Progress bar
- Expense ratio: This week vs average
- Task completion rate: % of planned tasks
- Cash flow health: Days of runway
- Client satisfaction: Response time

**Example:**
```markdown
## Key Metrics Dashboard

| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Revenue | $2,450 | $2,500/wk | 🟡 98% |
| Expense Ratio | 77% | <80% | 🟢 Good |
| Task Completion | 85% | >80% | 🟢 Good |
| Cash Flow | 45 days | >30 days | 🟢 Healthy |
| Client Response | 18 hrs | <24 hrs | 🟢 Excellent |

### Legend
🟢 On Track | 🟡 Attention Needed | 🔴 Urgent
```

---

## Integration Points

### xero-integrator Skill

**Data Retrieved:**
- Weekly transactions
- Revenue by category
- Expenses by category
- Subscription charges
- Invoice status

**API Calls:**
```python
# Get week's transactions
transactions = xero_integrator.get_transactions(
    start_date='2026-01-05',
    end_date='2026-01-12'
)

# Get P&L statement
profit_loss = xero_integrator.generate_report(
    type='profit-loss',
    month='2026-01'
)
```

### financial-analyst Skill

**Analysis Requested:**
- Trend analysis (revenue, expenses)
- Anomaly detection (unusual charges)
- Cash flow projection
- Expense categorization confidence

**API Calls:**
```python
# Analyze revenue trends
trends = financial_analyst.analyze_trends(
    data=transactions,
    period='week',
    focus='revenue'
)

# Detect anomalies
anomalies = financial_analyst.detect_anomalies(
    transactions=transactions,
    threshold=2.0  # 2 std deviations
)
```

### social-media-manager Skill

**Metrics Retrieved:**
- Posts published count
- Engagement metrics
- Platform comparison
- Top performing content

**API Calls:**
```python
# Get weekly summary
social_summary = social_media_manager.generate_summary(
    period='week',
    platforms=['linkedin', 'facebook', 'instagram', 'twitter']
)
```

### scheduler-manager Integration

**Scheduling:**
- Weekly briefing: Every Sunday 11:00 PM
- Monthly deep dive: Last Sunday of month
- Quarterly review: End of quarter

**Configuration:**
```bash
# Set up weekly briefing
scheduler-manager schedule \
  --task "Generate CEO Briefing" \
  --command "python scripts/generate_briefing.py --period week" \
  --schedule "weekly" \
  --day "sunday" \
  --time "23:00"
```

---

## Subscription Audit Logic

### Pattern Detection

**Subscription Identification:**
```python
# From Requirements.md
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    'github.com': 'GitHub',
    'zoom.us': 'Zoom',
    'dropbox.com': 'Dropbox',
    'gsuite.google.com': 'Google Workspace',
    'office365.microsoft.com': 'Microsoft 365',
}

def identify_subscription(transaction):
    """Identify if transaction is subscription"""
    description = transaction['description'].lower()

    for pattern, name in SUBSCRIPTION_PATTERNS.items():
        if pattern in description:
            return {
                'name': name,
                'amount': transaction['amount'],
                'date': transaction['date'],
                'frequency': 'monthly',  # detect from history
            }
    return None
```

### Usage Tracking

**Activity Detection:**
```python
def check_subscription_usage(subscription, period_days=30):
    """Check if subscription was used recently"""

    # Check login logs (if available)
    # Check API usage (if integrated)
    # Check file access (for storage services)

    last_activity = get_last_activity(subscription['name'])
    days_inactive = (datetime.now() - last_activity).days

    return {
        'subscription': subscription,
        'last_activity': last_activity,
        'days_inactive': days_inactive,
        'usage_status': 'active' if days_inactive < period_days else 'unused'
    }
```

### Cost Analysis

**Optimization Opportunities:**
```python
def analyze_subscription_value(subscription, usage):
    """Analyze if subscription provides value"""

    recommendations = []
    annual_cost = subscription['amount'] * 12

    # Unused for 30+ days
    if usage['days_inactive'] > 30:
        recommendations.append({
            'action': 'cancel',
            'reason': f"No activity in {usage['days_inactive']} days",
            'savings': annual_cost
        })

    # Check for duplicates
    duplicates = find_duplicate_functionality(subscription['name'])
    if duplicates:
        recommendations.append({
            'action': 'consolidate',
            'reason': f"Duplicate functionality with {duplicates[0]}",
            'savings': annual_cost
        })

    # Cost increase detection
    if check_price_increase(subscription, threshold=0.20):
        recommendations.append({
            'action': 'review',
            'reason': "Price increased >20%",
            'impact': 'high'
        })

    return recommendations
```

---

## Output Format

### Monday Morning CEO Briefing

**File Location:** `/Briefings/Monday_Briefing_YYYY-MM-DD.md`

**Structure:**
```markdown
# Monday Morning CEO Briefing
## Week of January 5-12, 2026

**Generated:** 2026-01-12 23:00:00

---

## 📊 Executive Summary
[3-sentence overview]

---

## 💰 Financial Performance
[Revenue, expenses, cash flow]

---

## ✅ Project & Task Progress
[Completed tasks, bottlenecks, upcoming deadlines]

---

## 💳 Subscription Audit
[Active subscriptions, recommendations, savings opportunities]

---

## 📱 Social Media Performance
[Posts, engagement, top content]

---

## 🎯 Proactive Recommendations
[AI-generated insights and actions]

---

## 📈 Key Metrics Dashboard
[Weekly snapshot with status indicators]

---

*Generated by ceo-briefing-generator skill*
*Next briefing: January 19, 2026*
```

### Dashboard Update

**Updates `/Dashboard.md` with:**
- Last briefing date
- Key metrics summary
- Critical alerts
- Action items requiring attention

**Example:**
```markdown
## Latest CEO Briefing

**Generated:** January 12, 2026

**Quick Status:**
- 🟢 Revenue: On track (98% of target)
- 🟡 Subscriptions: 3 opportunities for $1,080/year savings
- 🟢 Cash Flow: Healthy (45 days runway)
- 🔴 Urgent: 2 invoices overdue (follow up this week)

**[View Full Briefing →](/Briefings/Monday_Briefing_2026-01-12.md)**
```

---

## Briefing Templates

### Template: Standard Weekly

**Use For:** Regular weekly briefings

**Sections:**
1. Executive Summary
2. Financial Performance
3. Project Progress
4. Subscription Audit (monthly)
5. Social Media Summary
6. Recommendations
7. Key Metrics

### Template: Month-End Deep Dive

**Use For:** Last week of month

**Additional Sections:**
- Full month financial review
- Quarterly progress (if applicable)
- Comprehensive subscription audit
- Strategic recommendations
- Next month planning

### Template: Quarter-End Review

**Use For:** End of quarter

**Additional Sections:**
- Quarterly financial summary
- Goal achievement analysis
- Strategic initiatives review
- Competitive analysis
- Next quarter planning

---

## Customization

### Configure Business Goals

**Edit `/Business_Goals.md`:**

```markdown
### Revenue Target
- Monthly goal: $15,000  # Adjust to your target
- Quarterly goal: $45,000

### Key Metrics
| Metric | Target | Alert |
|--------|--------|-------|
| Client response | < 12 hours | > 24 hours |  # Adjust thresholds
| Project margin | > 40% | < 30% |
```

### Add Custom Subscription Patterns

**Edit `scripts/audit_subscriptions.py`:**

```python
SUBSCRIPTION_PATTERNS.update({
    'yourservice.com': 'Your Service Name',
    'anotherapp.io': 'Another App',
})
```

### Customize Alert Thresholds

**Edit briefing configuration:**

```python
ALERT_THRESHOLDS = {
    'revenue_below_target': 0.90,  # Alert if <90% of target
    'expense_ratio_high': 0.85,     # Alert if expenses >85% of revenue
    'cash_flow_days_low': 30,       # Alert if <30 days runway
    'subscription_unused_days': 30,  # Flag if unused >30 days
    'invoice_overdue_days': 30,      # Alert if invoice >30 days overdue
}
```

---

## Error Handling

### Missing Data Sources

**If Business_Goals.md not found:**
- Use default targets ($10,000/month revenue)
- Create template Business_Goals.md
- Alert user to customize

**If Xero data unavailable:**
- Note in briefing: "Financial data unavailable"
- Use previous week's data with disclaimer
- Alert user to check Xero integration

**If task tracking incomplete:**
- Analyze available data
- Note limitations in briefing
- Recommend task tracking improvements

### Incomplete Integrations

**Graceful Degradation:**
```
If xero-integrator unavailable:
    ↓
Skip financial sections
    ↓
Generate briefing with available data
    ↓
Note missing sections

If social-media-manager unavailable:
    ↓
Skip social media section
    ↓
Continue with other sections
```

---

## Scheduling

### Weekly Briefing

**Schedule:**
```bash
# Every Sunday at 11:00 PM
scheduler-manager schedule \
  --task "Weekly CEO Briefing" \
  --command "python .claude/skills/ceo-briefing-generator/scripts/generate_briefing.py --period week" \
  --frequency "weekly" \
  --day "sunday" \
  --time "23:00"
```

### Monthly Deep Dive

**Schedule:**
```bash
# Last Sunday of month at 11:00 PM
scheduler-manager schedule \
  --task "Monthly Business Review" \
  --command "python .claude/skills/ceo-briefing-generator/scripts/generate_briefing.py --period month --template deep-dive" \
  --frequency "monthly" \
  --day-of-month "last-sunday" \
  --time "23:00"
```

---

## Analytics & Improvement

### Track Briefing Effectiveness

**Metrics to Monitor:**
- Action items completed vs suggested
- Revenue growth correlation
- Cost savings achieved from recommendations
- Time saved reviewing data

**Monthly Review:**
1. Review action item completion rate
2. Measure actual savings from recommendations
3. Adjust alert thresholds based on effectiveness
4. Refine subscription patterns

### Continuous Improvement

**Feedback Loop:**
```
Generate briefing
    ↓
Review with CEO/user
    ↓
Track which recommendations were acted on
    ↓
Measure outcomes
    ↓
Adjust algorithms and thresholds
    ↓
Improve future briefings
```

---

## Troubleshooting

**Briefing not generating:**
1. Check scheduler-manager is running
2. Verify all data sources accessible
3. Review error logs in `/Logs/`
4. Run manually to diagnose

**Subscription audit missing items:**
1. Check transaction descriptions match patterns
2. Add custom patterns in script
3. Review Xero categorization
4. Verify date range covers billing cycles

**Recommendations not relevant:**
1. Adjust alert thresholds in configuration
2. Update Business_Goals.md with accurate targets
3. Review and refine recommendation logic
4. Provide feedback for learning

---

## References

- `references/briefing_templates.md` - Briefing format templates
- `references/recommendation_engine.md` - AI recommendation logic
- `references/subscription_patterns.md` - Complete subscription database
- `references/metrics_definitions.md` - How metrics are calculated

---

**Dependencies:**
- xero-integrator skill (financial data)
- financial-analyst skill (trend analysis)
- social-media-manager skill (engagement metrics)
- scheduler-manager skill (automation)
- Business_Goals.md (targets and thresholds)

**Integration:** Fully integrated with Gold Tier skills for comprehensive business intelligence.
