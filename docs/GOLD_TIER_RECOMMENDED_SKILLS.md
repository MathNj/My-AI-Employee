# Gold Tier: Recommended Skills List
**Based on:** Requirements.md Gold Tier specifications
**Generated:** 2026-01-12

---

## Gold Tier Requirements (From Requirements.md)

1. ✅ All Silver requirements plus:
2. ✅ Full cross-domain integration (Personal + Business)
3. ❌ **Create accounting system in Xero and integrate MCP Server**
4. ❌ **Integrate Facebook and Instagram - post messages and generate summary**
5. ❌ **Integrate Twitter (X) - post messages and generate summary**
6. ✅ Multiple MCP servers for different action types
7. ❌ **Weekly Business and Accounting Audit with CEO Briefing generation**
8. ✅ Error recovery and graceful degradation
9. ✅ Comprehensive audit logging
10. ✅ Documentation of architecture and lessons learned
11. ✅ All AI functionality as Agent Skills

**Status:** 7/11 complete (64%)
**Remaining:** 4 requirements → 3-4 new skills needed

---

## RECOMMENDED SKILLS FOR GOLD TIER

### ✅ Already Have (From Silver Tier)

These skills already satisfy some Gold Tier requirements:

| Skill | Gold Requirement Satisfied |
|-------|---------------------------|
| vault-setup | Infrastructure |
| task-processor | Cross-domain integration |
| plan-generator | Business workflow |
| approval-processor | HITL for sensitive actions |
| email-sender | Personal domain integration |
| linkedin-poster | Business domain integration |
| scheduler-manager | Automation scheduling |
| dashboard-updater | Status monitoring |
| watcher-manager | Input monitoring |
| financial-analyst | Financial analysis (partial #7) |
| web-researcher | External knowledge |

**Total Existing:** 11 skills ✅

---

## 🆕 NEW SKILLS NEEDED (3-4 Skills)

### 1. xero-integrator ⭐ REQUIRED

**Gold Requirement:** #3 - Create accounting system in Xero and integrate MCP Server

**Purpose:**
Integrate with Xero accounting platform to automate bookkeeping, transaction categorization, and financial reporting.

**Key Features:**
- Sync transactions from Xero to /Accounting folder
- Automatic expense categorization using AI
- Invoice management (create, send, track)
- Financial report generation
- Bank reconciliation
- Integration with financial-analyst skill for deeper analysis
- Real-time transaction monitoring

**Triggers:**
- "Sync with Xero"
- "Import transactions"
- "Categorize expenses"
- "Generate financial report"
- "Check Xero balance"

**Implementation Details:**

**Scripts:**
```
scripts/
├── sync_transactions.py      # Import from Xero API
├── categorize_expenses.py    # AI-powered categorization
├── generate_invoice.py        # Create and send invoices
├── reconcile_accounts.py      # Bank reconciliation
└── financial_report.py        # Generate reports
```

**References:**
```
references/
├── xero_api.md               # Xero API documentation
├── category_rules.md         # Expense categorization rules
├── tax_categories.md         # Tax classification rules
└── report_templates.md       # Financial report formats
```

**MCP Server:** ✅ Exists at https://github.com/XeroAPI/xero-mcp-server

**Workflow:**
```
Xero API → xero-integrator → /Accounting folder
                           → financial-analyst (analysis)
                           → Dashboard update
```

**Time Estimate:** 6-8 hours
- MCP server setup: 1 hour
- Skill creation: 4-5 hours
- Testing: 1-2 hours

---

### 2. social-media-manager ⭐ REQUIRED

**Gold Requirements:** #4 & #5 - Integrate Facebook/Instagram and Twitter/X

**Purpose:**
Unified social media management across LinkedIn, Facebook, Instagram, and Twitter/X for business development and sales lead generation.

**Key Features:**
- **Multi-platform posting:** LinkedIn, Facebook, Instagram, Twitter/X
- **Platform selection:** Post to one, some, or all platforms simultaneously
- **Approval workflow:** HITL approval for all posts across all platforms
- **Templates:** Platform-specific post templates
- **Scheduling:** Schedule posts for optimal engagement times
- **Analytics:** Unified dashboard showing engagement across all platforms
- **Summary generation:** Weekly/monthly engagement summaries
- **Hashtag optimization:** Platform-specific hashtag recommendations

**Triggers:**
- "Post to social media"
- "Share on Facebook and Instagram"
- "Tweet this"
- "Post to all platforms"
- "Schedule LinkedIn post"
- "Generate social media summary"

**Platform-Specific Features:**

**LinkedIn:**
- ✅ Already implemented (reuse linkedin-poster)
- Service announcements
- Thought leadership
- Achievement posts

**Facebook:**
- Business page posts
- Event promotions
- Customer stories
- Photo/video posts
- Link sharing with preview

**Instagram:**
- Photo/video posts
- Stories
- Carousel posts
- Product showcases
- Behind-the-scenes content

**Twitter/X:**
- Tweets (280 characters)
- Threads (multi-tweet stories)
- Retweets with comments
- Quick announcements
- Engagement with mentions

**Implementation Details:**

**Scripts:**
```
scripts/
├── post_to_platform.py       # Universal posting (all platforms)
├── schedule_post.py           # Cross-platform scheduling
├── generate_summary.py        # Engagement analytics
├── optimize_hashtags.py       # Platform-specific hashtags
└── analytics_dashboard.py     # Unified analytics view
```

**References:**
```
references/
├── platform_apis.md          # API docs for all platforms
├── best_practices.md         # Platform-specific guidelines
├── templates.md              # Templates for each platform
├── optimal_times.md          # Best posting times by platform
└── hashtag_strategy.md       # Hashtag optimization guide
```

**Assets:**
```
assets/
└── templates/
    ├── linkedin/             # LinkedIn post templates
    ├── facebook/             # Facebook post templates
    ├── instagram/            # Instagram post templates
    └── twitter/              # Twitter/X post templates
```

**MCP Servers Needed:**
- ✅ LinkedIn MCP (already exists)
- ❌ Meta MCP (Facebook + Instagram) - **needs to be built**
- ❌ X MCP (Twitter/X) - **needs to be built**

**Workflow:**
```
User request → social-media-manager
                ↓
            Select platforms
                ↓
            Apply templates
                ↓
            /Pending_Approval (platform-specific files)
                ↓
            Human approves
                ↓
            approval-processor routes to MCP
                ↓
            Posts to selected platforms
                ↓
            Analytics tracking
                ↓
            Dashboard update
```

**Approval File Format:**
```yaml
---
type: social_post
platforms: ["linkedin", "facebook", "instagram"]
message: "Excited to announce our new AI automation service!"
hashtags: ["AIAutomation", "BusinessGrowth", "Innovation"]
image: "/path/to/image.jpg"
schedule: "2026-01-15T09:00:00Z"
status: pending
---
```

**Time Estimate:** 11-14 hours
- Meta MCP server: 4-5 hours
- X MCP server: 3-4 hours
- Skill creation: 3-4 hours
- Testing: 1 hour

---

### 3. ceo-briefing-generator ⭐ REQUIRED

**Gold Requirement:** #7 - Weekly Business and Accounting Audit with CEO Briefing generation

**Purpose:**
Automated weekly business audit that analyzes performance, identifies bottlenecks, and generates proactive suggestions - creating a comprehensive "Monday Morning CEO Briefing."

**Key Features:**
- **Scheduled execution:** Runs every Sunday at 11 PM automatically
- **Revenue analysis:** Weekly and monthly revenue tracking vs goals
- **Task completion audit:** Analyze tasks completed from /Done folder
- **Bottleneck detection:** Identify tasks that took longer than expected
- **Financial review:** Integration with financial-analyst and xero-integrator
- **Subscription audit:** Detect unused subscriptions (Requirements.md spec)
- **Proactive suggestions:** Cost optimization, deadline alerts, process improvements
- **Goal tracking:** Compare actual vs Business_Goals.md targets

**Triggers:**
- "Generate CEO briefing"
- "Weekly business audit"
- "Analyze business performance"
- "Check against goals"
- (Automatically on Sunday nights)

**Briefing Sections (from Requirements.md):**

1. **Executive Summary:** One-paragraph overview
2. **Revenue Performance:**
   - This week's revenue
   - Month-to-date vs target
   - Trend analysis (on track / ahead / behind)
3. **Completed Tasks:**
   - All tasks moved to /Done this week
   - Major milestones achieved
4. **Bottlenecks:**
   - Tasks that exceeded expected duration
   - Delayed deliverables
   - Resource constraints
5. **Proactive Suggestions:**
   - **Subscription audit:** "Notion: No activity in 45 days. Cost: $15/month. [ACTION] Cancel?"
   - Cost optimization opportunities
   - Process improvements
6. **Upcoming Deadlines:**
   - Next 7 days
   - Next 30 days
7. **Key Metrics Dashboard:**
   - Client response time
   - Invoice payment rate
   - Software costs
   - Project budgets vs actuals

**Implementation Details:**

**Scripts:**
```
scripts/
├── generate_briefing.py       # Main briefing generator
├── analyze_revenue.py         # Revenue tracking and analysis
├── analyze_tasks.py           # Task completion and bottlenecks
├── subscription_audit.py      # Detect unused subscriptions (Requirements.md)
├── deadline_checker.py        # Upcoming deadline alerts
└── goal_comparison.py         # Actual vs Business_Goals.md
```

**References:**
```
references/
├── briefing_template.md       # CEO briefing format (from Requirements.md)
├── business_goals_schema.md   # Business_Goals.md structure
├── audit_logic.md             # Business audit rules
├── subscription_patterns.md   # Subscription detection patterns
└── metric_thresholds.md       # Alert thresholds for metrics
```

**Input Files:**
- `/Business_Goals.md` - Targets and thresholds
- `/Done/*.md` - Completed tasks
- `/Accounting/Current_Month.md` - Financial transactions
- `/Logs/*.json` - Activity logs

**Output:**
```
/Briefings/2026-01-13_Monday_Briefing.md
```

**Subscription Audit Pattern (from Requirements.md):**
```python
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    # User-customizable
}
```

**Workflow:**
```
Sunday 11 PM → Scheduler triggers
                    ↓
              ceo-briefing-generator
                    ↓
            Read Business_Goals.md
                    ↓
            Analyze /Done tasks
                    ↓
            Query financial-analyst
                    ↓
            Query xero-integrator
                    ↓
            Run subscription audit
                    ↓
            Check upcoming deadlines
                    ↓
            Generate briefing markdown
                    ↓
            Save to /Briefings/
                    ↓
            Update Dashboard
                    ↓
            (Optional) Email briefing to user
```

**Dependencies:**
- financial-analyst skill (financial data)
- xero-integrator skill (Xero transactions)
- task-processor skill (task metadata)
- scheduler-manager skill (weekly scheduling)

**Time Estimate:** 3-4 hours
- Skill creation: 2-3 hours
- Integration with scheduler: 30 min
- Testing: 30 min

---

### 4. business-goals-manager (OPTIONAL - Quality of Life)

**Not Required by Gold Tier, but highly recommended**

**Purpose:**
Manage Business_Goals.md file with structured updates, goal tracking, and automated alerts when metrics exceed thresholds.

**Key Features:**
- Create and update Business_Goals.md
- Track progress against goals
- Alert when metrics exceed thresholds
- Suggest goal adjustments based on trends
- Integration with ceo-briefing-generator

**Triggers:**
- "Update business goals"
- "Set revenue target"
- "Add new project"
- "Check goal progress"

**Time Estimate:** 2-3 hours

**Priority:** 🟡 Low (Nice to have, not required)

---

## SKILL DEPENDENCIES & INTEGRATION

### Skill Interaction Map

```
                    vault-setup
                         ↓
              Creates folder structure
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Watchers    →  task-processor  ←  dashboard-updater
        ↓                ↓                ↑
   /Needs_Action   plan-generator        ↑
                         ↓                ↑
                  approval-processor     ↑
                    ↓         ↓          ↑
          email-sender   linkedin-poster ↑
                    ↓         ↓          ↑
              social-media-manager       ↑
                         ↓               ↑
                    All post to         ↑
                    platforms           ↑
                         ↓               ↑
              financial-analyst ←────────┤
                         ↓               ↑
              xero-integrator ───────────┤
                         ↓               ↑
            ceo-briefing-generator ──────┤
                         ↓               ↑
                 scheduler-manager ──────┘
```

### Cross-Skill Dependencies

**ceo-briefing-generator depends on:**
- financial-analyst (financial data analysis)
- xero-integrator (Xero transaction data)
- task-processor (task metadata)
- scheduler-manager (weekly scheduling)

**social-media-manager depends on:**
- approval-processor (HITL workflow)
- LinkedIn MCP (existing)
- Meta MCP (new)
- X MCP (new)

**xero-integrator depends on:**
- Xero MCP server (install)
- financial-analyst (analysis integration)

---

## MCP SERVERS REQUIRED

### ✅ Already Have

1. **Gmail MCP** - Email sending/reading
2. **LinkedIn MCP** - LinkedIn posting

### ❌ Need to Build (2 New MCPs)

3. **Meta MCP** (Facebook + Instagram)
   - **API:** Meta Graph API
   - **Auth:** OAuth 2.0
   - **Scopes:** pages_manage_posts, instagram_basic, instagram_content_publish
   - **Time:** 4-5 hours

4. **X MCP** (Twitter/X)
   - **API:** X API v2
   - **Auth:** OAuth 2.0
   - **Scopes:** tweet.read, tweet.write, users.read
   - **Time:** 3-4 hours

### ✅ Can Use Existing

5. **Xero MCP** - Already built by Xero
   - **Source:** https://github.com/XeroAPI/xero-mcp-server
   - **Setup:** 1 hour (install + configure)

**Total MCP Work:** 8-10 hours

---

## IMPLEMENTATION PRIORITY

### 🔴 CRITICAL (Required for Gold Tier)

**Priority 1: CEO Briefing (Fastest ROI)**
- ✅ Create: ceo-briefing-generator
- ⏱️ Time: 3-4 hours
- 💡 Why first: No new MCP needed, immediate business value

**Priority 2: Accounting (Infrastructure)**
- ✅ Setup: Xero MCP server
- ✅ Create: xero-integrator
- ⏱️ Time: 6-8 hours
- 💡 Why second: Feeds data to CEO briefing, MCP exists

**Priority 3: Social Media (Complex but High Value)**
- ✅ Build: Meta MCP
- ✅ Build: X MCP
- ✅ Create: social-media-manager
- ⏱️ Time: 11-14 hours
- 💡 Why last: Most complex, requires 2 new MCPs

### 🟡 OPTIONAL (Quality of Life)

**Priority 4: Business Goals Management**
- ✅ Create: business-goals-manager
- ⏱️ Time: 2-3 hours
- 💡 Why optional: Not required by Gold Tier

---

## TOTAL TIME INVESTMENT

| Component | Time Required |
|-----------|---------------|
| **NEW SKILLS** |
| ceo-briefing-generator | 3-4 hours |
| xero-integrator | 5-7 hours |
| social-media-manager | 3-4 hours |
| business-goals-manager (optional) | 2-3 hours |
| **SUBTOTAL SKILLS** | **13-18 hours** |
| | |
| **NEW MCP SERVERS** |
| Xero MCP setup | 1 hour |
| Meta MCP build | 4-5 hours |
| X MCP build | 3-4 hours |
| **SUBTOTAL MCPs** | **8-10 hours** |
| | |
| **TESTING & INTEGRATION** |
| End-to-end testing | 2-3 hours |
| Documentation | 1-2 hours |
| **SUBTOTAL TESTING** | **3-5 hours** |
| | |
| **GRAND TOTAL** | **24-33 hours** |

**Current Investment:** ~32 hours (Silver Tier complete)
**After Gold Tier:** ~56-65 hours total
**Requirements Estimate:** 40+ hours ✅ On track

---

## FINAL RECOMMENDED SKILLS LIST

### ✅ REQUIRED FOR GOLD TIER (3 skills)

1. **xero-integrator** - Xero accounting integration
2. **social-media-manager** - Multi-platform social media (LinkedIn/Facebook/Instagram/X)
3. **ceo-briefing-generator** - Weekly business audit and CEO briefing

### 🟡 OPTIONAL BUT RECOMMENDED (1 skill)

4. **business-goals-manager** - Manage Business_Goals.md and goal tracking

### 📊 FINAL SKILL COUNT

- **Silver Tier Skills:** 11
- **Gold Tier New Skills:** 3-4
- **Total Skills After Gold:** 14-15

---

## SUCCESS CRITERIA

### Gold Tier COMPLETE When:

✅ All Silver requirements met (DONE)
✅ Xero transactions syncing automatically
✅ Facebook posts with approval workflow
✅ Instagram posts with approval workflow
✅ Twitter/X posts with approval workflow
✅ Weekly CEO briefing generated every Sunday night
✅ Monday morning inbox has comprehensive business audit
✅ Proactive subscription audit working (Requirements.md spec)
✅ Multiple MCP servers operational (2+ required, will have 5)
✅ Error recovery implemented (DONE)
✅ Comprehensive audit logging (DONE)
✅ Architecture documented (DONE)
✅ All functionality as Agent Skills (DONE + 3 new)

**Result:** 12/12 Gold Tier requirements → 100% COMPLETE

---

## NEXT ACTIONS

### To Start Gold Tier:

**Option 1: Quick Win Approach**
1. Create ceo-briefing-generator (3-4 hours)
2. Test with current data
3. See immediate business value
4. Build momentum for remaining work

**Option 2: Foundation First Approach**
1. Setup Xero MCP (1 hour)
2. Create xero-integrator (5-7 hours)
3. Get accounting data flowing
4. Then tackle CEO briefing and social media

**Option 3: Parallel Development**
1. Create ceo-briefing-generator (3-4 hours)
2. While testing, setup Xero in parallel
3. Then tackle social media last

**Recommended:** Option 1 (Quick Win) for motivation and early business value

---

**Document Created:** 2026-01-12
**Based On:** Requirements.md Gold Tier specifications
**Status:** Ready for implementation
