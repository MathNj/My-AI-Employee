# Source Verification Guide

How to verify sources, score confidence levels, and ensure research quality.

---

## Overview

The web-researcher skill automatically scores confidence levels, but understanding the verification process helps you:
1. Interpret confidence scores correctly
2. Know when to escalate to human review
3. Validate critical information independently

**Core Principle:** Trust, but verify. Always cross-reference critical information.

---

## Confidence Scoring System

### High Confidence (⭐⭐⭐)

**Criteria:**
- Official documentation or government sites (.gov, .edu, docs.*)
- Reputable technical sources (GitHub, Stack Overflow, MDN)
- Multiple independent sources agree
- High keyword relevance to query
- Recent publication date (for time-sensitive topics)

**Examples:**
```
✅ Python Documentation: https://docs.python.org/3/library/asyncio.html
✅ W3C Web Standards: https://www.w3.org/TR/...
✅ GitHub Official Repo: https://github.com/python/cpython
✅ Government Data: https://data.gov/...
```

**When to trust:**
- Technical documentation lookups
- API usage examples
- Standard definitions
- Official policy statements

**Still verify if:**
- Financial decision depends on it
- Legal/compliance implications
- Medical/safety considerations

### Medium Confidence (⭐⭐)

**Criteria:**
- Established blogs and news sites (.org, medium.com, news.*)
- Industry publications
- Moderate keyword relevance
- Single source but reputable
- Some authority signals

**Examples:**
```
⚠️  TechCrunch article: https://techcrunch.com/...
⚠️  Medium blog post: https://medium.com/@expert/...
⚠️  Industry site: https://machinelearningmastery.com/...
```

**When to trust:**
- Background research
- Industry trends
- Non-critical information
- Supported by high-confidence sources

**Requires verification for:**
- Critical business decisions
- Financial matters
- Specific claims or numbers

### Low Confidence (⭐)

**Criteria:**
- Unknown or low-authority domains
- Poor keyword relevance
- No publication date
- Potential conflicts with other sources
- Thin content or aggregator sites

**Examples:**
```
❌ Random blog: https://unknown-blog.com/...
❌ Forum post: https://random-forum.net/...
❌ Aggregator: https://news-aggregator.co/...
❌ No HTTPS: http://old-site.com/...
```

**When to trust:**
- Never for critical decisions
- Only as starting point for further research
- With explicit human review

**Always escalate:**
- Low confidence results for critical queries
- All low confidence results (>50% of total)
- Conflicting low confidence sources

---

## Domain Authority Assessment

### Tier 1: Official/Authoritative

**Highest trust** - Primary sources

- `.gov` - Government websites
- `.edu` - Educational institutions
- `docs.*` - Official documentation
- `developer.*` - Official developer docs
- `github.com/<official-org>` - Official repositories

**Examples:**
- https://www.irs.gov/
- https://docs.python.org/
- https://developer.mozilla.org/
- https://github.com/microsoft/vscode

### Tier 2: Reputable Technical

**High trust** - Established technical resources

- `stackoverflow.com` - Technical Q&A
- `wikipedia.org` - General knowledge (verify critical facts)
- Major news sites (NYTimes, Reuters, BBC)
- `arxiv.org` - Academic preprints

**Verify:**
- Wikipedia citations
- Stack Overflow answer votes and date
- News article sources

### Tier 3: Industry/Professional

**Medium trust** - Industry sources

- `.org` - Organizations
- Industry publications (TechCrunch, Ars Technica)
- Professional blogs (Medium verified authors)
- Company blogs (company.com/blog)

**Check:**
- Author credentials
- Publication date
- Supporting evidence

### Tier 4: General/Unknown

**Low trust** - Unverified sources

- Unknown domains
- Personal blogs
- Forums without moderation
- Aggregator sites
- Sites without HTTPS

**Use only for:**
- Initial research
- Lead generation
- Must verify independently

---

## Content Verification Checklist

### For All Sources

- [ ] Domain matches topic authority (medical = .gov/.edu)
- [ ] HTTPS enabled (security)
- [ ] Recent publication date (if time-sensitive)
- [ ] Author credentials listed
- [ ] Citations or sources provided
- [ ] No obvious bias or agenda
- [ ] Consistent with other sources

### For Technical Information

- [ ] Code examples are tested/working
- [ ] Version numbers specified
- [ ] Official documentation referenced
- [ ] Community validation (votes, stars)
- [ ] Active maintenance (recent updates)

### For Business Information

- [ ] Company official website matches
- [ ] Cross-reference with public records
- [ ] Multiple sources confirm
- [ ] Contact information verifiable
- [ ] Recent and accurate

### For News/Events

- [ ] Multiple news outlets report
- [ ] Primary source cited
- [ ] Date and location specified
- [ ] Author byline present
- [ ] Fact-checking available

---

## Cross-Referencing Strategy

### The 3-Source Rule

**For critical information**, verify with 3 independent sources:

1. **Official source** (Tier 1)
2. **Reputable technical** (Tier 2)
3. **Industry/professional** (Tier 3)

**Example: Verifying company information**
```
Query: "Acme Corp headquarters address"

Source 1: Company website (/contact) - Tier 1 ✅
Source 2: LinkedIn company page - Tier 2 ✅
Source 3: Business directory - Tier 3 ✅

All match? → High confidence
Any mismatch? → Investigate
```

### Detecting Conflicts

**When sources conflict:**

1. **Identify discrepancy:**
   - What specifically conflicts?
   - Is it substantial or minor?

2. **Check source quality:**
   - Which sources are more authoritative?
   - Which are more recent?

3. **Find tie-breaker:**
   - Look for additional source
   - Check official/primary source

4. **Document conflict:**
   - Flag in summary
   - Lower confidence
   - Recommend human review

**Example conflict resolution:**
```
Query: "Python 3.12 release date"

Source A: Blog says October 2023
Source B: Python.org says October 2023
Source C: News article says September 2023

Resolution:
- Python.org is official (Tier 1)
- Blog and Python.org agree
- News article likely error or different event
- Trust: October 2023 (High confidence)
```

---

## Red Flags

### Content Red Flags

❌ **No author or organization listed**
- Can't verify credentials
- No accountability

❌ **Extreme language or bias**
- "Amazing discovery!"
- "Everyone knows..."
- Strong political/commercial bias

❌ **No sources cited**
- Claims without evidence
- Opinions presented as facts

❌ **Outdated information**
- Old dates on time-sensitive topics
- Technology articles from >2 years ago
- Broken links or images

❌ **Poor quality writing**
- Grammatical errors
- Spelling mistakes
- Unprofessional formatting

### Technical Red Flags

❌ **Code doesn't work**
- Syntax errors
- Deprecated methods
- Missing imports

❌ **Conflicting technical details**
- Different version numbers
- Incompatible approaches

❌ **No version specified**
- "Just use Python" (which version?)
- "This works in React" (which React version?)

### Business Red Flags

❌ **Can't verify company exists**
- No official website
- No business registrations
- No social media presence

❌ **Suspicious contact info**
- Gmail/Yahoo email for business
- No phone number
- PO Box only

❌ **Too good to be true**
- Unrealistic claims
- Guaranteed results
- Urgency tactics

---

## Escalation Criteria

### Automatic Escalation

**Always escalate to human when:**

1. **All results are low confidence**
   - No authoritative sources found
   - Query may be too niche or specific

2. **Sources actively conflict**
   - Contradictory information
   - Can't determine which is correct

3. **Critical high-stakes decision**
   - Financial transactions
   - Legal/compliance matters
   - Medical/safety decisions
   - Personnel/hiring decisions

4. **No results found**
   - Query may need rephrasing
   - Manual research may be needed

### Manual Escalation

**Consider escalating when:**

1. **Confidence is marginal**
   - Mix of medium and low confidence
   - Unsure about source authority

2. **Time-sensitive information**
   - Need most recent data
   - Situation may have changed

3. **Unusual query**
   - First time searching this topic
   - Unfamiliar domain

4. **High visibility**
   - Client-facing information
   - Public communications
   - Board presentations

---

## Verification Workflows

### Workflow 1: Quick Verification (< 2 minutes)

**Use for:** Routine lookups, low-stakes information

1. Run search: `web_search.py "query"`
2. Check confidence scores
3. If all high/medium: Use results
4. If any low: Verify or escalate

### Workflow 2: Standard Verification (2-5 minutes)

**Use for:** Important business decisions, client information

1. Run search with max results: `--max-results 5`
2. Check top 3 sources manually
3. Verify domain authority
4. Cross-reference if needed
5. Document sources in notes

### Workflow 3: Comprehensive Verification (10+ minutes)

**Use for:** Critical decisions, financial/legal matters

1. Run multiple searches (different providers)
2. Check all sources manually
3. Verify with official sources
4. Cross-reference 3+ independent sources
5. Document verification process
6. Get human review before use

---

## Examples

### Example 1: Technical Documentation Lookup

**Query:** "Python asyncio gather timeout"

**Results:**
```
1. Python Docs (docs.python.org) - High
2. Stack Overflow accepted answer - High
3. Real Python tutorial - Medium
```

**Verification:**
- ✅ Official docs present
- ✅ Community validation (SO votes)
- ✅ Recent publication
- ✅ Content consistent

**Decision:** High confidence, use results

### Example 2: Company Verification

**Query:** "ABC Widget Corp headquarters"

**Results:**
```
1. Unknown directory site - Low
2. LinkedIn company page - Medium
```

**Verification:**
- ❌ No official website result
- ⚠️  Only one medium confidence source
- ❌ No government business registry

**Decision:** Low confidence, escalate for manual research

### Example 3: News/Events

**Query:** "Latest AI regulations 2026"

**Results:**
```
1. Tech news site - Medium
2. Blog post - Low
3. Another tech news - Medium
```

**Verification:**
- ⚠️  No official government source
- ⚠️  All medium/low confidence
- ❌ May need official .gov source

**Decision:** Escalate to verify with official sources (FTC, EU, etc.)

---

## Best Practices

### Do's

✅ **Always check confidence scores**
- Don't ignore low confidence warnings

✅ **Verify critical information manually**
- Visit source directly
- Check publication date
- Verify author credentials

✅ **Use multiple search providers**
- Brave for general
- Tavily for technical
- Cross-check results

✅ **Document your verification**
- Note sources checked
- Record confidence assessment
- Save for audit trail

✅ **Update stale information**
- Re-search periodically
- Check for updates
- Note when information was verified

### Don'ts

❌ **Don't trust single sources**
- Especially for critical decisions
- Always cross-reference

❌ **Don't ignore conflicts**
- Never average conflicting data
- Investigate discrepancies

❌ **Don't skip verification for "obvious" facts**
- Verify business addresses
- Check current CEOs
- Confirm API endpoints

❌ **Don't use outdated information**
- Technology changes rapidly
- Regulations update
- Companies reorganize

❌ **Don't bypass human review**
- For high-stakes decisions
- When confidence is low
- When sources conflict

---

## Confidence Score Algorithm

**For reference**, here's how confidence is scored:

```python
def score_confidence(result, query):
    score = 0

    # Domain authority (max 3 points)
    if any(auth in domain for auth in ['.gov', '.edu', 'docs.']):
        score += 3
    elif any(auth in domain for auth in ['.org', 'medium.com']):
        score += 2
    else:
        score += 1

    # Keyword relevance (max 3 points)
    matching_words = count_matching_keywords(result, query)
    relevance_ratio = matching_words / total_query_words
    if relevance_ratio > 0.7:
        score += 3
    elif relevance_ratio > 0.4:
        score += 2
    else:
        score += 1

    # Recency (max 1 point)
    if has_recent_publication_date(result):
        score += 1

    # Score to confidence
    if score >= 6:
        return 'High'
    elif score >= 4:
        return 'Medium'
    else:
        return 'Low'
```

**Total range:** 2-7 points
- **High:** 6-7 points
- **Medium:** 4-5 points
- **Low:** 2-3 points

---

## Related Documentation

- See main `SKILL.md` for usage
- See `search_apis.md` for provider setup
- See `use_cases.md` for examples

---

**Remember:** The skill provides evidence, not truth. Always apply critical thinking and domain expertise to research results.
