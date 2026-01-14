---
name: web-researcher
description: Safe external knowledge access with source citations and confidence scoring. Prevents hallucination by providing verifiable evidence from web searches. Supports Brave Search, Tavily, and other search APIs. Use for fact verification, vendor research, technical documentation lookup, and market intelligence gathering. Returns structured reports with confidence levels.
---

# web-researcher

## Overview

The **web-researcher** skill enables your Personal AI Employee to **safely access external knowledge** when required. It performs web searches, validates sources, scores confidence levels, and returns structured reports with citations.

This skill exists to **prevent hallucination**, not to make decisions.

**Key Principle:** This skill provides **sourced evidence**, not authoritative truth. Final decisions must be made by downstream planning or policy-enforcement skills.

---

## Quick Start

```bash
# 1. Set up API credentials (choose one)
# See Setup section for API key instructions

# 2. Perform a search
python .claude/skills/web-researcher/scripts/web_search.py "Python async programming best practices"

# 3. Use specific provider
python .claude/skills/web-researcher/scripts/web_search.py "Company XYZ address" --provider brave

# 4. Save report to file
python .claude/skills/web-researcher/scripts/web_search.py "Machine learning trends" --output research_report.md
```

---

## When to Use This Skill

### ✅ Use this skill when:

1. **Verification is required**
   - Example: "Verify whether this vendor exists"
   - Example: "Confirm this company's official website"

2. **Critical information is missing**
   - Example: "Find the official address of [Company Name]"
   - Example: "What is the current CEO of [Company]?"

3. **Market or industry research is requested**
   - Example: "Summarize recent news about [Topic]"
   - Example: "Find competitors in [Industry]"

4. **Technical debugging or documentation lookup is needed**
   - Example: "Look up the correct API usage for this error"
   - Example: "Find Python documentation for asyncio.gather"

5. **Real-time or recent information is required**
   - Example: "What are today's exchange rates?"
   - Example: "Recent news about [Event]"

### ❌ Do NOT use this skill when:

1. **Information already exists in:**
   - `Company_Handbook.md`
   - Long-term memory (`02_Memory`)
   - Recent conversation history

2. **The task involves purely internal data**
   - Example: "What did I work on yesterday?" (use vault search)
   - Example: "What's in my Business_Goals.md?" (read file directly)

3. **The request is opinion-based**
   - Example: "What's the best programming language?" (subjective)
   - Use this skill only for factual, verifiable information

4. **Real-time API access is available**
   - If you have direct API access (weather, stock prices), use that instead

---

## Core Workflows

### Workflow 1: Basic Web Search

```bash
# Search for information
python scripts/web_search.py "search query here"
```

**What happens:**
1. Query sent to available search provider (Brave → Tavily → fallback)
2. Results retrieved and validated
3. Confidence scored for each source
4. Formatted report generated
5. Activity logged

### Workflow 2: Provider-Specific Search

```bash
# Use specific search provider
python scripts/web_search.py "query" --provider brave

# Try Tavily for academic/technical queries
python scripts/web_search.py "machine learning research" --provider tavily
```

### Workflow 3: Research Report Generation

```bash
# Generate report file
python scripts/web_search.py "artificial intelligence ethics" \
  --max-results 5 \
  --output reports/ai_ethics_research.md
```

---

## Setup

### Prerequisites

Choose **one or more** search providers:
1. **Brave Search** (Recommended for general web search)
2. **Tavily** (Best for AI/technical queries)
3. **Claude WebSearch** (If available via MCP)

### Option 1: Brave Search API

**Cost:** Free tier available (2,500 queries/month), paid plans from $5/month

**Setup:**

1. Get API key:
   - Visit https://brave.com/search/api/
   - Sign up and get your API key

2. Create credentials file:
   ```bash
   mkdir -p watchers/credentials
   cat > watchers/credentials/brave_api.json << 'EOF'
   {
     "api_key": "your-brave-api-key-here"
   }
   EOF
   ```

3. Test:
   ```bash
   python scripts/brave_search.py "test search"
   ```

**Pros:**
- Free tier available
- Fast responses
- Good general web coverage
- Privacy-focused

**Cons:**
- Requires API key
- Rate limits on free tier

### Option 2: Tavily Search API

**Cost:** Free tier (1,000 searches/month), paid plans from $20/month

**Setup:**

1. Get API key:
   - Visit https://tavily.com/
   - Sign up and get your API key (starts with `tvly-`)

2. Create credentials file:
   ```bash
   cat > watchers/credentials/tavily_api.json << 'EOF'
   {
     "api_key": "tvly-your-api-key-here"
   }
   EOF
   ```

3. Test:
   ```bash
   python scripts/tavily_search.py "test search"
   ```

**Pros:**
- AI-optimized results
- Includes relevance scores
- Can provide AI-generated answers
- Good for technical/academic queries

**Cons:**
- Higher cost than Brave
- Smaller free tier

### Option 3: Claude WebSearch (Future)

If using Claude Code with WebSearch MCP server:
- No additional setup required
- Built-in citation and sourcing
- See references/search_apis.md for details

---

## Output Format

All research outputs follow this **required structure**:

```markdown
### 🔍 Research Report

**Query:** "search query used"
**Status:** ✅ Success | ❌ Failed

| Key Finding | Source URL | Confidence |
|------------|------------|------------|
| Finding title/summary | https://source.com | High |
| Another finding | https://other-source.com | Medium |

**Summary:**
2-3 sentences summarizing the findings.
If confidence is low or sources conflict, this is stated explicitly.
```

### Example Output

```markdown
### 🔍 Research Report

**Query:** "Python asyncio best practices 2026"
**Status:** ✅ Success

| Key Finding | Source URL | Confidence |
|------------|------------|------------|
| Real Python: Python AsyncIO Tutorial | https://realpython.com/async-io-python/ | High |
| Official Python Docs: asyncio | https://docs.python.org/3/library/asyncio.html | High |
| Stack Overflow: asyncio patterns | https://stackoverflow.com/questions/... | Medium |

**Summary:**
Found 3 relevant sources. 2 high-confidence sources identified from official documentation and established technical sites. Consensus on using asyncio.gather() for concurrent operations and proper exception handling patterns.
```

---

## Confidence Scoring

Each search result is automatically scored as **High**, **Medium**, or **Low** confidence based on:

### High Confidence
- Official documentation sites (.gov, .edu, docs.*)
- Reputable technical sources (GitHub, Stack Overflow)
- High query relevance (keywords match well)
- Recent publication date

### Medium Confidence
- Established blogs and news sites (.org, medium.com)
- Moderate query relevance
- Some authority signals present

### Low Confidence
- Unknown or low-authority domains
- Poor query relevance (keywords don't match well)
- No publication date
- Potential conflicts with other sources

**Important:** Low-confidence results should trigger human review before being used in decision-making.

---

## Failure Handling

### No Results Found

```markdown
### 🔍 Research Report

**Query:** "very specific obscure query"
**Status:** ❌ Failed

| Key Finding | Source URL | Confidence |
|------------|------------|------------|
| No results | N/A | N/A |

**Summary:**
Search failed or returned no reliable results. Consider rephrasing query or using alternative search methods.
```

**Actions:**
1. Rephrase query (more specific or more general)
2. Try different search provider
3. Break down into multiple simpler queries
4. Flag for human research

### Conflicting Sources

When sources conflict, the skill:
1. Lowers confidence levels for all conflicting sources
2. Flags the conflict explicitly in summary
3. Returns all conflicting sources for human review

**Example Summary:**
```
Found 4 sources. ⚠️ Sources present conflicting information about [topic].
Human review recommended before making decisions.
```

### Low Confidence Results

When >50% of results are low confidence:

```
Found 3 sources. ⚠️ Most sources have low confidence - human review recommended.
```

---

## Integration with Other Skills

### With task-processor

```
Task created: "Verify client ABC's official address"
    ↓
task-processor triggers web-researcher
    ↓
web-researcher performs search
    ↓
Returns structured report with sources
    ↓
task-processor includes in plan
```

### With approval-processor

For sensitive research requiring approval:

```
High-stakes decision requires external verification
    ↓
Create approval request in /Pending_Approval
    ↓
Include: Research query, intended use, decision impact
    ↓
Human approves research
    ↓
web-researcher executes search
    ↓
Results returned for decision-making
```

### With email-sender

```
Customer inquiry: "What are your company's competitors?"
    ↓
web-researcher searches for market competitors
    ↓
Generates research report
    ↓
email-sender drafts response citing sources
    ↓
Human approves email
    ↓
Response sent with researched information
```

---

## Best Practices

### Query Formulation

**Good queries:**
- Specific and focused: "Python asyncio timeout handling"
- Factual questions: "Current CEO of Microsoft"
- Technical lookups: "React useEffect cleanup function"

**Poor queries:**
- Too vague: "programming"
- Opinion-based: "best web framework"
- Multiple questions: "Python vs JavaScript and React vs Vue"

**Tips:**
1. Include relevant keywords
2. Be specific but not overly narrow
3. Use technical terms when appropriate
4. For companies: Include full legal name
5. For people: Include context (role, company)

### Source Validation

**Always check:**
1. Domain authority (.gov, .edu, official docs)
2. Publication date (recent for time-sensitive info)
3. Consistency across sources
4. Confidence score

**Red flags:**
- Single source for critical information
- All low-confidence results
- Conflicting information
- No official sources

### When to Escalate to Human

**Automatic escalation triggers:**
1. All results are low confidence
2. Sources present conflicts
3. No results found for critical query
4. High-stakes decision depends on results

**Manual escalation recommended:**
1. Financial decisions
2. Legal/compliance matters
3. Medical/safety information
4. Personnel decisions

---

## Usage Examples

### Example 1: Vendor Verification

```bash
python scripts/web_search.py "Acme Corp official website contact information" \
  --max-results 5
```

**Use case:** Verify vendor exists and get contact info before engaging

### Example 2: Technical Documentation

```bash
python scripts/web_search.py "Python requests library timeout parameter" \
  --provider brave
```

**Use case:** Look up correct API usage while debugging

### Example 3: Market Research

```bash
python scripts/web_search.py "artificial intelligence trends 2026" \
  --max-results 10 \
  --output reports/ai_trends.md
```

**Use case:** Generate market intelligence report for business planning

### Example 4: Competitor Analysis

```bash
python scripts/web_search.py "companies similar to Salesforce CRM" \
  --provider tavily
```

**Use case:** Research competitors in specific industry

---

## Via Claude Code

When using Claude Code, simply ask:

- "Research [topic] and provide sources"
- "Verify whether [company] is a legitimate business"
- "Find recent news about [event]"
- "Look up the documentation for [technical topic]"

Claude will automatically:
1. Use web-researcher skill
2. Perform search with appropriate provider
3. Return formatted report with citations
4. Include confidence levels

---

## Monitoring and Logging

All searches are logged to:
`/Logs/web_research_YYYY-MM-DD.json`

**Log format:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "query": "search query",
  "provider": "brave",
  "results_count": 3,
  "status": "success",
  "skill": "web-researcher"
}
```

**Use logs to:**
- Track search usage and costs
- Identify frequently researched topics
- Monitor API quota usage
- Audit external information access

---

## Security Considerations

### API Key Protection

**CRITICAL:** Never commit API keys to git

- Store in `watchers/credentials/*.json`
- Protected by `.gitignore`
- Rotate keys monthly
- Use read-only API keys when available

### Data Privacy

- Search queries may be logged by search providers
- Avoid searching for:
  - Personal identifying information (PII)
  - Passwords or credentials
  - Confidential business data
  - Private customer information

**For sensitive research:**
1. Use privacy-focused providers (Brave)
2. Review provider's privacy policy
3. Consider manual research for highly sensitive topics

### Result Validation

**Never trust search results blindly:**
1. Always check confidence scores
2. Verify critical information from multiple sources
3. Use official sources when available
4. Human review for high-stakes decisions

---

## Troubleshooting

### "API key not configured"

**Solution:**
1. Check credentials file exists: `watchers/credentials/brave_api.json`
2. Verify JSON format is correct
3. Confirm API key is valid (test on provider's website)

### "No results found"

**Possible causes:**
1. Query too specific or unusual
2. Spelling errors in query
3. Provider doesn't have relevant content

**Solutions:**
1. Rephrase query (broader or more specific)
2. Try different provider
3. Break into smaller queries

### "Rate limit exceeded"

**Solution:**
1. Wait for rate limit reset (usually hourly/daily)
2. Switch to different provider
3. Upgrade to paid tier if needed
4. Implement query throttling

### "All low confidence results"

**Solution:**
1. Query may be too vague - be more specific
2. Topic may not have authoritative sources
3. Try alternative search terms
4. Consider manual research or expert consultation

---

## Scripts Reference

### web_search.py

Main search interface.

**Usage:**
```bash
python web_search.py "query" [options]
```

**Options:**
- `--provider brave|tavily|websearch` - Specific provider
- `--max-results N` - Maximum results (default: 3)
- `--output FILE` - Save to file
- `--verbose` - Verbose output

### brave_search.py

Brave Search API integration.

**Direct usage:**
```bash
python brave_search.py "query"
```

**In code:**
```python
from brave_search import search_brave
results = search_brave("query", max_results=5)
```

### tavily_search.py

Tavily Search API integration.

**Direct usage:**
```bash
python tavily_search.py "query"
```

**In code:**
```python
from tavily_search import search_tavily
results = search_tavily("query", max_results=5)
```

---

## References

- See `references/search_apis.md` for detailed API setup guides
- See `references/verification_guide.md` for source validation best practices
- See `references/use_cases.md` for complete use case examples

---

**Note:** This skill requires at least one search provider API key to function. Brave Search is recommended for general use, Tavily for technical/academic queries.
