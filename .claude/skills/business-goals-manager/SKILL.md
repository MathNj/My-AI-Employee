---
name: business-goals-manager
description: Manage business goals, targets, and key metrics for the AI Employee system. Use when the user needs to (1) Initialize or update business goals, (2) Set revenue targets, (3) Define key performance indicators, (4) Track progress against goals, (5) Adjust alert thresholds, or (6) Generate goal achievement reports. Triggers include "set business goals", "update revenue target", "track goal progress", "adjust metrics", "create Business_Goals.md".
---

# Business Goals Manager

Centralized management of business goals, targets, and key performance indicators (KPIs) for the Personal AI Employee system.

## Quick Start

### Initialize Business Goals

```bash
# Create default Business_Goals.md
python scripts/initialize_goals.py

# Create with custom revenue target
python scripts/initialize_goals.py --monthly-target 15000

# Interactive setup
python scripts/initialize_goals.py --interactive
```

### Update Goals

```bash
# Update revenue target
python scripts/update_goals.py --type revenue --monthly 12000 --quarterly 36000

# Add new metric
python scripts/update_goals.py --add-metric "Customer retention rate" --target 95 --alert 85 --unit percent

# Adjust alert threshold
python scripts/update_goals.py --metric "Client response time" --alert 36
```

### Track Progress

```bash
# Current progress against all goals
python scripts/track_progress.py

# Specific goal progress
python scripts/track_progress.py --goal revenue

# Export progress report
python scripts/track_progress.py --export md --output progress_report.md
```

---

## Core Purpose

The business-goals-manager skill:

1. **Creates and maintains** Business_Goals.md file
2. **Provides templates** for different business types
3. **Validates goals** for completeness and consistency
4. **Tracks progress** against defined targets
5. **Adjusts thresholds** based on actual performance
6. **Integrates** with ceo-briefing-generator for automated tracking

---

## Business_Goals.md Structure

### Standard Template

```markdown
---
last_updated: 2026-01-12
review_frequency: weekly
created: 2026-01-12
version: 1.0
---

# Business Goals & Targets

## Revenue Targets

### Monthly
- **Target**: $10,000
- **Stretch Goal**: $12,000
- **Minimum Acceptable**: $8,000

### Quarterly
- **Q1 2026**: $30,000
- **Q2 2026**: $35,000
- **Q3 2026**: $40,000
- **Q4 2026**: $45,000

### Annual
- **2026 Target**: $150,000
- **2026 Stretch**: $180,000

## Key Metrics to Track

| Metric | Target | Alert Threshold | Unit | Priority |
|--------|--------|-----------------|------|----------|
| Client response time | < 24 hours | > 48 hours | hours | High |
| Invoice payment rate | > 90% | < 80% | percent | High |
| Software costs | < $500/month | > $600/month | dollars | Medium |
| Project margin | > 40% | < 30% | percent | High |
| Customer satisfaction | > 4.5/5 | < 4.0/5 | rating | High |
| Lead conversion rate | > 25% | < 15% | percent | Medium |

## Active Projects

### Project Alpha
- **Due Date**: 2026-01-15
- **Budget**: $2,000
- **Status**: On track
- **Completion**: 75%
- **Owner**: Team Lead A

### Project Beta
- **Due Date**: 2026-01-30
- **Budget**: $3,500
- **Status**: At risk
- **Completion**: 45%
- **Owner**: Team Lead B
- **Blockers**: Waiting on client feedback

## Strategic Initiatives

### Q1 2026
1. **Launch new service offering**
   - Target date: January 31
   - Expected revenue impact: +$2,000/month
   - Status: In progress

2. **Optimize subscription costs**
   - Target savings: $1,000/year
   - Status: Ongoing via ceo-briefing-generator

3. **Expand social media presence**
   - Target: 500 new followers across platforms
   - Status: In progress via social-media-manager

## Subscription Audit Rules

Flag subscriptions for review if:
- No login activity in 30+ days
- Cost increased by > 20%
- Duplicate functionality with another tool
- Usage below 30% of purchased capacity
- Annual renewal approaching with low usage

## Alert Thresholds

### Revenue Alerts
- 🟢 **On Track**: ≥ 90% of target
- 🟡 **Attention Needed**: 70-89% of target
- 🔴 **Urgent**: < 70% of target

### Expense Alerts
- 🟢 **Healthy**: < 70% of revenue
- 🟡 **Watch**: 70-85% of revenue
- 🔴 **Critical**: > 85% of revenue

### Cash Flow Alerts
- 🟢 **Healthy**: > 60 days runway
- 🟡 **Monitor**: 30-60 days runway
- 🔴 **Urgent**: < 30 days runway

## Review Schedule

- **Daily**: Dashboard review (5 minutes)
- **Weekly**: CEO Briefing review (15 minutes)
- **Monthly**: Deep dive and goal adjustment (1 hour)
- **Quarterly**: Strategic review and planning (4 hours)

---

*Managed by business-goals-manager skill*
*Last updated: 2026-01-12*
```

---

## Goal Templates

### Startup Template

**For:** Early-stage businesses focused on growth

**Key Metrics:**
- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (LTV)
- Burn rate
- Runway
- User growth rate

**Usage:**
```bash
python scripts/initialize_goals.py --template startup --monthly-target 5000
```

### Consulting Template

**For:** Service-based businesses

**Key Metrics:**
- Billable hours percentage
- Average project margin
- Client retention rate
- Pipeline value
- Proposal win rate
- Revenue per consultant

**Usage:**
```bash
python scripts/initialize_goals.py --template consulting --monthly-target 20000
```

### E-commerce Template

**For:** Product-based businesses

**Key Metrics:**
- Average order value
- Conversion rate
- Cart abandonment rate
- Customer acquisition cost
- Return on ad spend (ROAS)
- Inventory turnover

**Usage:**
```bash
python scripts/initialize_goals.py --template ecommerce --monthly-target 50000
```

### SaaS Template

**For:** Software-as-a-Service businesses

**Key Metrics:**
- Monthly Recurring Revenue (MRR)
- Churn rate
- Net Revenue Retention (NRR)
- Customer Acquisition Cost (CAC)
- LTV:CAC ratio
- Activation rate

**Usage:**
```bash
python scripts/initialize_goals.py --template saas --monthly-target 15000
```

---

## Scripts Overview

### initialize_goals.py

**Purpose:** Create Business_Goals.md with appropriate template

**Features:**
- Multiple business templates
- Interactive wizard
- Custom revenue targets
- Metric recommendations
- Validation checks

**Usage:**
```bash
# Default template
python scripts/initialize_goals.py

# Specific template
python scripts/initialize_goals.py --template saas --monthly-target 15000

# Interactive mode
python scripts/initialize_goals.py --interactive

# Custom metrics file
python scripts/initialize_goals.py --custom-metrics metrics.json
```

---

### update_goals.py

**Purpose:** Update existing goals and targets

**Features:**
- Revenue target updates
- Add/remove metrics
- Adjust thresholds
- Update project status
- Version tracking

**Usage:**
```bash
# Update revenue target
python scripts/update_goals.py --type revenue --monthly 12000

# Add new metric
python scripts/update_goals.py --add-metric "Net Promoter Score" --target 50 --alert 30 --unit score

# Remove metric
python scripts/update_goals.py --remove-metric "Old metric name"

# Update project status
python scripts/update_goals.py --project "Project Alpha" --status "completed"

# Adjust alert threshold
python scripts/update_goals.py --metric "Client response time" --alert 36 --unit hours
```

---

### track_progress.py

**Purpose:** Track progress against defined goals

**Features:**
- Real-time progress calculation
- Goal achievement percentage
- Trend analysis
- Forecasting
- Visual progress indicators

**Usage:**
```bash
# All goals progress
python scripts/track_progress.py

# Specific goal
python scripts/track_progress.py --goal revenue

# With forecasting
python scripts/track_progress.py --forecast

# Export report
python scripts/track_progress.py --export md --output progress.md
```

**Output:**
```markdown
# Goal Progress Report
**Period:** 2026-01-01 to 2026-01-12

## Revenue Progress
- **Target**: $10,000/month
- **Actual**: $4,500 (45% of target)
- **Status**: 🟢 On track (12 days into month)
- **Forecast**: $11,200 (projected end-of-month)
- **Trend**: +15% vs last month

## Key Metrics Status
| Metric | Target | Current | Status | Trend |
|--------|--------|---------|--------|-------|
| Client response time | < 24h | 18h | 🟢 | ↓ Improving |
| Invoice payment rate | > 90% | 92% | 🟢 | ↑ Improving |
| Project margin | > 40% | 38% | 🟡 | → Stable |
```

---

## Integration with CEO Briefing

### Automatic Goal Tracking

```
ceo-briefing-generator runs
    ↓
Reads Business_Goals.md
    ↓
Retrieves actual performance data
    ↓
Calculates progress:
  - Revenue vs target
  - Metrics vs thresholds
  - Project completion
    ↓
Determines status (🟢🟡🔴)
    ↓
Includes in briefing
    ↓
Flags goals at risk
```

### Goal-Based Recommendations

```python
# ceo-briefing-generator calls business-goals-manager

goals = business_goals_manager.get_goals()
progress = business_goals_manager.track_progress()

# Analyze each goal
for goal in goals['revenue_targets']:
    actual = get_actual_revenue()
    progress_pct = (actual / goal['target']) * 100

    if progress_pct < 70:
        recommendations.append({
            'type': 'urgent',
            'goal': goal['name'],
            'status': 'behind_target',
            'action': 'Review revenue pipeline and acceleration strategies'
        })
```

---

## Goal Validation

### Completeness Checks

**Required Fields:**
- ✅ Revenue targets (monthly minimum)
- ✅ At least 3 key metrics
- ✅ Alert thresholds for each metric
- ✅ Review schedule defined
- ✅ Last updated date

**Validation:**
```bash
python scripts/validate_goals.py

# Output
✅ Revenue targets complete
✅ 6 metrics defined (minimum 3)
✅ All metrics have alert thresholds
⚠️ Warning: No quarterly targets defined
✅ Review schedule defined
✅ Last updated: 2026-01-12
```

### Consistency Checks

**Validation Rules:**
- Alert thresholds are less favorable than targets
- Quarterly targets align with monthly targets
- Annual targets align with quarterly targets
- Metrics have appropriate units
- Dates are in valid format

**Example:**
```python
# Invalid: Alert threshold more favorable than target
Metric: "Project margin"
Target: > 40%
Alert: > 50%  # ❌ Should be < 40%

# Valid
Metric: "Project margin"
Target: > 40%
Alert: < 30%  # ✅ Correct
```

---

## Goal Adjustment Strategies

### Performance-Based Adjustment

**When to Adjust:**
- Consistently exceeding targets (3+ months)
- Consistently missing targets (3+ months)
- Market conditions changed
- Business model pivot
- Seasonal variations identified

**Adjustment Examples:**

**Scenario 1: Exceeding Targets**
```
Current: $10,000/month target
Actual: $12,500/month (125% for 3 months)

Recommendation: Increase target to $12,000/month
New stretch goal: $15,000/month
```

**Scenario 2: Missing Targets**
```
Current: $10,000/month target
Actual: $7,000/month (70% for 3 months)

Options:
1. Reduce target to $8,000/month (realistic)
2. Identify and address root causes (recommended)
3. Extend timeline for goal achievement
```

**Script Usage:**
```bash
# Suggest adjustments based on performance
python scripts/suggest_adjustments.py

# Apply recommended adjustments
python scripts/suggest_adjustments.py --apply

# Preview adjustments without applying
python scripts/suggest_adjustments.py --dry-run
```

---

## Metric Categories

### Financial Metrics

**Revenue:**
- Total revenue
- Monthly Recurring Revenue (MRR)
- Average Revenue Per User (ARPU)
- Revenue growth rate

**Profitability:**
- Gross margin
- Net profit margin
- EBITDA
- Burn rate

**Cash Flow:**
- Operating cash flow
- Days of runway
- Accounts receivable days
- Accounts payable days

### Customer Metrics

**Acquisition:**
- Customer Acquisition Cost (CAC)
- Lead conversion rate
- Sales cycle length
- Pipeline value

**Retention:**
- Customer retention rate
- Churn rate
- Net Revenue Retention (NRR)
- Customer Lifetime Value (LTV)

**Satisfaction:**
- Net Promoter Score (NPS)
- Customer Satisfaction Score (CSAT)
- Customer Effort Score (CES)
- Support ticket resolution time

### Operational Metrics

**Efficiency:**
- Billable hours percentage
- Project delivery time
- Resource utilization
- Cost per transaction

**Quality:**
- Error rate
- On-time delivery rate
- Rework percentage
- Quality score

### Growth Metrics

**Market:**
- Market share
- Brand awareness
- Website traffic
- Lead generation rate

**Product:**
- Feature adoption rate
- Active users
- Engagement rate
- Product-market fit score

---

## Best Practices

### 1. SMART Goals

Goals should be:
- **Specific**: Clearly defined
- **Measurable**: Quantifiable with numbers
- **Achievable**: Realistic given resources
- **Relevant**: Aligned with business strategy
- **Time-bound**: Has a deadline

**Example:**
```markdown
❌ Bad: "Increase revenue"
✅ Good: "Increase monthly revenue to $15,000 by Q2 2026"

❌ Bad: "Improve customer satisfaction"
✅ Good: "Achieve NPS score of 50+ by end of Q1 2026"
```

### 2. Balanced Scorecard

Track goals across multiple dimensions:
- **Financial**: Revenue, profit, costs
- **Customer**: Satisfaction, retention, acquisition
- **Internal**: Efficiency, quality, innovation
- **Learning**: Skills, culture, systems

### 3. Leading vs Lagging Indicators

**Lagging Indicators** (outcomes):
- Revenue achieved
- Profit earned
- Customers churned

**Leading Indicators** (drivers):
- Sales pipeline value
- Customer satisfaction scores
- Product usage metrics

**Balance both:**
```markdown
## Key Metrics

### Lagging (Results)
- Monthly Revenue: $10,000 target
- Net Profit: $3,000 target

### Leading (Drivers)
- Sales Pipeline: $30,000+ (3x monthly target)
- Demo Completion Rate: > 60%
- Proposal Win Rate: > 30%
```

### 4. Regular Review Cadence

**Weekly:**
- Quick dashboard check
- Progress toward monthly targets
- Identify blockers

**Monthly:**
- Detailed goal review
- Adjust tactics if needed
- Celebrate wins

**Quarterly:**
- Strategic review
- Goal adjustment if needed
- Set next quarter objectives

### 5. Goal Hierarchy

```
Vision (3-5 years)
    ↓
Strategic Goals (1 year)
    ↓
Quarterly Objectives (3 months)
    ↓
Monthly Targets (1 month)
    ↓
Weekly Actions (1 week)
```

**Example:**
```markdown
## Goal Hierarchy

### Vision (3 years)
Become the leading AI automation consultancy in our region

### Strategic Goal (2026)
Reach $150,000 annual revenue with 50+ happy clients

### Q1 Objective
Launch new AI service offering, achieve $30,000 revenue

### January Target
Complete service package, sign 3 pilot clients, generate $10,000

### This Week
- Finalize pricing and proposal template
- Reach out to 20 warm leads
- Close 1 pilot deal
```

---

## Common Use Cases

### Use Case 1: New Business Setup

**Scenario:** Starting a new consulting business

**Steps:**
1. Initialize with consulting template
   ```bash
   python scripts/initialize_goals.py --template consulting --monthly-target 10000
   ```

2. Customize metrics for your business
   ```bash
   python scripts/update_goals.py --add-metric "Billable hours %" --target 70 --alert 50
   ```

3. Set up review schedule
   ```bash
   python scripts/update_goals.py --review-schedule weekly
   ```

4. Integrate with CEO briefing
   - CEO briefing will automatically track progress

---

### Use Case 2: Goal Not Being Met

**Scenario:** Revenue target consistently missed for 2 months

**Steps:**
1. Review current progress
   ```bash
   python scripts/track_progress.py --goal revenue --detailed
   ```

2. Analyze trends
   ```bash
   python scripts/track_progress.py --goal revenue --trend-analysis
   ```

3. Get adjustment recommendations
   ```bash
   python scripts/suggest_adjustments.py --goal revenue
   ```

4. Either:
   - **Option A:** Reduce target to realistic level
   - **Option B:** Identify root causes and address (recommended)
   - **Option C:** Extend timeline

5. Update goals with decision
   ```bash
   python scripts/update_goals.py --type revenue --monthly 8000 --reason "Market conditions"
   ```

---

### Use Case 3: Adding New Metric

**Scenario:** Want to track customer satisfaction

**Steps:**
1. Add the metric
   ```bash
   python scripts/update_goals.py \
     --add-metric "Customer Satisfaction (CSAT)" \
     --target 4.5 \
     --alert 4.0 \
     --unit "rating" \
     --priority high
   ```

2. Verify it was added
   ```bash
   python scripts/validate_goals.py
   ```

3. Track progress
   ```bash
   python scripts/track_progress.py --metric "Customer Satisfaction"
   ```

---

### Use Case 4: Quarterly Review

**Scenario:** End of Q1, reviewing and setting Q2 goals

**Steps:**
1. Generate Q1 progress report
   ```bash
   python scripts/track_progress.py --period Q1 --export md --output Q1_review.md
   ```

2. Review achievement
   - Revenue: 102% of target ✅
   - New clients: 8 vs 10 target 🟡
   - Profit margin: 45% vs 40% target ✅

3. Adjust Q2 targets based on learnings
   ```bash
   python scripts/update_goals.py --quarterly Q2 --revenue 35000
   python scripts/update_goals.py --metric "New clients" --target 12
   ```

4. Add new strategic initiatives
   ```bash
   python scripts/update_goals.py --add-initiative "Launch referral program" --target-date "2026-05-15"
   ```

---

## Troubleshooting

**Business_Goals.md not found:**
```bash
python scripts/initialize_goals.py --interactive
```

**Goals seem unrealistic:**
```bash
python scripts/suggest_adjustments.py --analyze-feasibility
```

**Metrics not being tracked:**
- Check integration with ceo-briefing-generator
- Verify metric names match exactly
- Ensure data sources are connected

**Progress calculations incorrect:**
- Verify date ranges
- Check data source connections (xero-integrator, etc.)
- Run validation: `python scripts/validate_goals.py`

---

## Integration Points

### With ceo-briefing-generator

```python
# ceo-briefing-generator imports goals
from business_goals_manager import get_goals, track_progress

goals = get_goals()
progress = track_progress(period='week')

# Use in briefing
revenue_status = progress['revenue']['status']
metrics_at_risk = progress['metrics_at_risk']
```

### With financial-analyst

```python
# financial-analyst checks goals for context
goals = business_goals_manager.get_goals()
revenue_target = goals['revenue_targets']['monthly']

# Analyze if on track to meet target
forecast = financial_analyst.forecast_revenue()
if forecast < revenue_target:
    alert_user()
```

### With dashboard-updater

```python
# dashboard-updater shows goal progress
progress = business_goals_manager.track_progress()

dashboard.update_section('goals', {
    'revenue_progress': progress['revenue']['percentage'],
    'goals_at_risk': progress['at_risk_count'],
    'goals_on_track': progress['on_track_count']
})
```

---

## References

- `references/goal_templates.md` - Complete template library
- `references/metrics_catalog.md` - 100+ metric definitions
- `references/best_practices.md` - Goal-setting best practices

---

**Dependencies:**
- Obsidian vault (for Business_Goals.md storage)
- ceo-briefing-generator (for automated tracking)
- xero-integrator (for financial data)
- financial-analyst (for trend analysis)

**Integration:** Core skill that supports all Gold Tier business intelligence features.
