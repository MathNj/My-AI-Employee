# Web Researcher Use Cases

Common scenarios and examples for using the web-researcher skill effectively.

---

## Overview

This document provides practical examples of when and how to use web research in your AI Employee workflows.

---

## Category 1: Vendor & Company Verification

### Use Case 1.1: Verify New Vendor Legitimacy

**Scenario:** Customer wants to work with a new supplier you've never heard of.

**Query:**
```bash
python web_search.py "Acme Industrial Supplies official website contact"
```

**What to verify:**
- Official website exists and is professional
- Company registration/legal entity
- Physical address (not just PO Box)
- Contact information (phone, email)
- Years in business
- BBB rating or reviews

**Decision criteria:**
- ✅ High confidence + verified address → Proceed
- ⚠️  Medium confidence → Manual research
- ❌ Low confidence/no results → Reject or escalate

### Use Case 1.2: Find Company Contact Information

**Scenario:** Need to contact a partner company's support team.

**Query:**
```bash
python web_search.py "XYZ Corp customer support email phone"
```

**Expected results:**
- Official support page
- Contact form
- Direct email addresses
- Phone numbers
- Business hours

### Use Case 1.3: Competitor Analysis

**Scenario:** Client asks about competitors in their industry.

**Query:**
```bash
python web_search.py "companies similar to Salesforce CRM" --max-results 10
```

**Use results for:**
- Competitive landscape analysis
- Feature comparison research
- Pricing research (combine with manual verification)
- Market positioning

---

## Category 2: Technical Documentation

### Use Case 2.1: API Usage Lookup

**Scenario:** Getting error using Python library, need correct syntax.

**Query:**
```bash
python web_search.py "Python requests library timeout parameter example"
```

**Expected results:**
- Official documentation (docs.python-requests.org)
- Stack Overflow examples
- Tutorial sites

**Confidence needed:** High (official docs + community validation)

### Use Case 2.2: Debugging Error Messages

**Scenario:** Encountering unfamiliar error code.

**Query:**
```bash
python web_search.py "PostgreSQL error 42P01 relation does not exist"
```

**Look for:**
- Official documentation
- Stack Overflow solutions
- GitHub issues

**Use with caution:**
- Verify solution applies to your version
- Test in dev environment first
- Understand the fix, don't blindly apply

### Use Case 2.3: Best Practices Research

**Scenario:** Need to implement feature with security best practices.

**Query:**
```bash
python web_search.py "OAuth 2.0 implementation best practices 2026"
```

**Prioritize:**
- Official OAuth docs
- Security organizations (OWASP)
- Major framework docs
- Recent publication (last 1-2 years)

---

## Category 3: Market Intelligence

### Use Case 3.1: Industry Trends

**Scenario:** Client asks about AI trends for business planning.

**Query:**
```bash
python web_search.py "artificial intelligence business trends 2026" \
  --max-results 10 \
  --output reports/ai_trends_2026.md
```

**Use for:**
- Executive summaries
- Strategic planning input
- Newsletter content
- Client presentations

**Important:** Note publication dates, multiple sources, and confidence levels in report.

### Use Case 3.2: Technology Adoption

**Scenario:** Evaluating whether to adopt new technology.

**Query:**
```bash
python web_search.py "Kubernetes adoption rate enterprise 2026"
```

**Look for:**
- Industry surveys
- Analyst reports (Gartner, Forrester)
- Case studies
- Recent statistics

### Use Case 3.3: Pricing Research

**Scenario:** Need market rate for services.

**Query:**
```bash
python web_search.py "average freelance developer hourly rate 2026"
```

**Verify with:**
- Multiple sources
- Geographic specificity
- Skill level breakdown
- Official surveys/reports

**Never:**
- Use for competitor pricing (check their site)
- Make pricing decisions solely on research
- Share client pricing publicly

---

## Category 4: Fact Verification

### Use Case 4.1: Verify Statistics

**Scenario:** Client cites a statistic, need to verify.

**Claim:** "80% of businesses use AI"

**Query:**
```bash
python web_search.py "business AI adoption rate statistics 2026 source"
```

**Check for:**
- Original source (study, survey)
- Sample size and methodology
- Publication date
- Geographic scope
- Definition of "AI"

### Use Case 4.2: Verify News/Events

**Scenario:** Customer mentions news event affecting project.

**Query:**
```bash
python web_search.py "Python 3.13 release date official announcement"
```

**Verify with:**
- Official sources (python.org)
- Multiple news outlets
- Direct announcement

### Use Case 4.3: Verify Person Information

**Scenario:** Vetting potential business partner.

**Query:**
```bash
python web_search.py "John Smith CEO TechCorp LinkedIn"
```

**Find:**
- LinkedIn profile
- Company bio
- Professional history
- News mentions

**Privacy note:** Only search public professional information.

---

## Category 5: Real-Time Information

### Use Case 5.1: Current Exchange Rates

**Scenario:** International client payment calculation.

**Query:**
```bash
python web_search.py "USD to EUR exchange rate today"
```

**Use:**
- Estimate only
- Verify with bank/payment processor
- Note rate fluctuates

### Use Case 5.2: Event Schedules

**Scenario:** Client asks about conference dates.

**Query:**
```bash
python web_search.py "AWS re:Invent 2026 dates location"
```

**Verify:**
- Official event website
- Registration page
- Multiple sources confirm

### Use Case 5.3: Service Status

**Scenario:** API seems down, check if it's just you.

**Query:**
```bash
python web_search.py "GitHub status outage today"
```

**Check:**
- Official status page
- Social media (Twitter/X)
- Third-party status monitors

---

## Category 6: Compliance & Legal

### Use Case 6.1: Regulation Lookup

**Scenario:** Need to verify GDPR requirements.

**Query:**
```bash
python web_search.py "GDPR data retention requirements official"
```

**Critical:**
- **Always use official government sources**
- Verify with .gov or .eu sites
- Check publication date
- **Consult legal professional** for official interpretation

**Never:**
- Rely solely on blogs
- Use outdated information
- Make legal decisions without lawyer review

### Use Case 6.2: License Verification

**Scenario:** Using open source library, check license.

**Query:**
```bash
python web_search.py "MIT License requirements commercial use"
```

**Look for:**
- Official license text
- OSI (Open Source Initiative) definition
- Authoritative legal resources

---

## Category 7: Learning & Education

### Use Case 7.1: Concept Explanation

**Scenario:** Customer uses unfamiliar term.

**Query:**
```bash
python web_search.py "What is edge computing simple explanation"
```

**Use:**
- Wikipedia (overview)
- Official definitions
- Reputable tech sites

**For learning:**
- Save high-quality sources
- Build knowledge base
- Update Company_Handbook.md with new concepts

### Use Case 7.2: Tutorial Discovery

**Scenario:** Need to learn new technology.

**Query:**
```bash
python web_search.py "Docker beginner tutorial 2026"
```

**Look for:**
- Official getting started guides
- Highly-rated tutorials
- Recent publication
- Hands-on examples

---

## Anti-Patterns (DON'T Do These)

### ❌ Anti-Pattern 1: Using for Decisions Without Verification

**Wrong:**
```
Search: "Should I invest in cryptocurrency"
Action: Make investment based on first result
```

**Why wrong:** Opinion-based, high-risk decision

**Right approach:**
- Research multiple perspectives
- Consult financial advisor
- Use only for background information

### ❌ Anti-Pattern 2: Ignoring Confidence Levels

**Wrong:**
```
All results are low confidence
→ Use anyway because "it's something"
```

**Why wrong:** Low confidence = unreliable

**Right approach:**
- Escalate to human research
- Try different queries
- Use alternative sources

### ❌ Anti-Pattern 3: Not Checking Dates

**Wrong:**
```
Search: "Python best practices"
Result: Article from 2015
→ Use outdated practices
```

**Why wrong:** Technology evolves rapidly

**Right approach:**
- Filter for recent results
- Check if still applicable
- Look for version-specific info

### ❌ Anti-Pattern 4: Single Source for Critical Info

**Wrong:**
```
Search: "Company ABC headquarters"
Result: One random business directory
→ Use address for contract
```

**Why wrong:** Could be outdated or wrong

**Right approach:**
- Check official company website
- Verify with multiple sources
- Contact company directly if critical

### ❌ Anti-Pattern 5: Searching for Existing Internal Info

**Wrong:**
```
Search web for: "What did I tell client about project timeline"
```

**Why wrong:** This is in your vault/memory

**Right approach:**
- Search Obsidian vault
- Check Plans/ and Done/ folders
- Review conversation history

---

## Workflow Integration Examples

### Integration 1: Customer Inquiry Response

```
Customer email: "Do you support integration with Slack?"
    ↓
Read email via email-sender
    ↓
Check Company_Handbook.md (current capabilities)
    ↓
web-researcher: "Slack API integration best practices"
    ↓
Draft response with research citations
    ↓
Approval workflow
    ↓
Send reply
```

### Integration 2: Vendor Onboarding

```
New vendor proposed: "TechSupply Co"
    ↓
web-researcher: "TechSupply Co official website reviews"
    ↓
High confidence results found
    ↓
Extract: website, address, contact
    ↓
Store in Company_Handbook.md: Approved Vendors
    ↓
Proceed with onboarding
```

### Integration 3: Technical Support

```
Customer reports error: "Connection timeout"
    ↓
web-researcher: "API connection timeout causes solutions"
    ↓
Find official documentation
    ↓
Draft solution email with citations
    ↓
Approval workflow
    ↓
Send solution with source links
```

### Integration 4: Market Report

```
Scheduled task: "Weekly AI news summary"
    ↓
web-researcher: "AI industry news this week"
    ↓
Collect 10 high-confidence sources
    ↓
Generate summary report
    ↓
Save to reports/weekly_ai_YYYY-MM-DD.md
    ↓
Email to team (with approval)
```

---

## Query Formulation Tips

### Good Query Patterns

**For facts:**
```
"Python 3.12 release date"
"GDPR maximum fine amount"
"GitHub Actions pricing"
```

**For how-to:**
```
"How to implement OAuth 2.0 in Python"
"Docker container networking tutorial"
"Set up PostgreSQL replication"
```

**For verification:**
```
"Company XYZ official website"
"Is [Product] legitimate"
"[Person] CEO [Company] LinkedIn"
```

**For comparison:**
```
"React vs Vue 2026 comparison"
"AWS vs Azure pricing comparison"
"Best CRM for small business"
```

### Query Refinement

**Too broad:**
```
❌ "programming"
✅ "Python async programming best practices"
```

**Too narrow:**
```
❌ "asyncio.gather() with timeout of exactly 5.2 seconds"
✅ "asyncio.gather() timeout handling"
```

**Multiple questions:**
```
❌ "Python vs JavaScript and which is better for web development"
✅ "Python web development frameworks 2026"
✅ "JavaScript frameworks comparison 2026"
```

**Opinion-based:**
```
❌ "Best programming language"
✅ "Most popular programming languages 2026 statistics"
```

---

## Measuring Research Quality

### Quality Metrics

**High-quality research:**
- ✅ 60%+ high confidence sources
- ✅ Multiple independent sources agree
- ✅ Recent publication (< 1 year for tech, < 6 months for news)
- ✅ Official sources included
- ✅ Clear citations and attributions

**Poor-quality research:**
- ❌ All low confidence sources
- ❌ Single source
- ❌ Outdated information
- ❌ Conflicting information
- ❌ No official sources

### When to Re-Research

**Triggers:**
- Information > 6 months old (for time-sensitive topics)
- Low confidence on first attempt
- Conflicting results
- Stakeholder questions research quality
- Using for high-stakes decision

---

## Cost Management

### Free Tier Optimization

**Brave (2,500/month):**
- ~80 searches per day
- Good for general business use
- Cache results to reduce duplicates

**Tavily (1,000/month):**
- ~30 searches per day
- Reserve for technical/complex queries
- Use basic search mode to conserve credits

### Query Batching

Instead of:
```bash
python web_search.py "Python asyncio"
python web_search.py "Python async await"
python web_search.py "Python asyncio tutorial"
```

Do:
```bash
python web_search.py "Python asyncio async await tutorial" --max-results 10
```

### Result Caching

Save research reports for reuse:
```bash
python web_search.py "query" --output cache/query_2026-01-12.md
```

Check cache before new search:
```bash
find cache/ -name "*query*" -mtime -7  # Results < 7 days old
```

---

## Related Documentation

- See main `SKILL.md` for setup and usage
- See `search_apis.md` for provider details
- See `verification_guide.md` for validation process

---

**Remember:** Research provides evidence, not decisions. Always apply domain expertise and critical thinking to search results.
