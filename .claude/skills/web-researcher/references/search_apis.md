### Search API Setup Guide

Complete setup instructions for all supported search providers.

---

## Brave Search API

### Overview

**Provider:** Brave Software
**URL:** https://brave.com/search/api/
**Best for:** General web search, privacy-focused research
**Pricing:** Free tier (2,500 queries/month), Paid from $5/month

### Features

- Web search with filtering
- News search
- Image search (optional)
- Location-based results
- No tracking or profiling
- GDPR compliant

### Setup Instructions

#### Step 1: Create Account

1. Visit https://brave.com/search/api/
2. Click "Get Started" or "Sign Up"
3. Create account with email
4. Verify email address

#### Step 2: Get API Key

1. Log in to Brave Search API dashboard
2. Navigate to "API Keys"
3. Click "Create New Key"
4. Copy your API key (format: starts with `BSA...`)
5. **Save securely** - you won't see it again

#### Step 3: Configure Credentials

Create credentials file:

```bash
# Create credentials directory
mkdir -p watchers/credentials

# Create Brave API credentials file
cat > watchers/credentials/brave_api.json << 'EOF'
{
  "api_key": "BSAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
EOF

# Verify file created
cat watchers/credentials/brave_api.json
```

**Security:** Ensure `.gitignore` includes `watchers/credentials/`

#### Step 4: Test Connection

```bash
# Test Brave Search integration
python .claude/skills/web-researcher/scripts/brave_search.py "test query"
```

**Expected output:**
```
Searching Brave for: test query

Found 5 results:

1. Test Result Title
   URL: https://example.com
   Description here...
```

### API Limits

**Free Tier:**
- 2,500 queries per month
- Rate limit: ~1 query per second
- No credit card required

**Paid Tiers:**
- **Developer:** $5/month - 15,000 queries
- **Pro:** $10/month - 30,000 queries
- **Enterprise:** Custom pricing

### Troubleshooting

**Error: "Invalid API key"**
- Verify key copied correctly (no spaces)
- Check key is active in dashboard
- Regenerate key if needed

**Error: "Rate limit exceeded"**
- Wait for rate limit reset (resets monthly)
- Upgrade to paid tier
- Implement query throttling

---

## Tavily Search API

### Overview

**Provider:** Tavily AI
**URL:** https://tavily.com/
**Best for:** AI-optimized search, technical/academic queries
**Pricing:** Free tier (1,000 searches/month), Paid from $20/month

### Features

- AI-optimized search results
- Relevance scoring
- AI-generated answers (optional)
- Deep search mode
- Academic/technical focus
- JSON-first API

### Setup Instructions

#### Step 1: Create Account

1. Visit https://tavily.com/
2. Click "Get Started" or "Sign Up"
3. Sign up with email or GitHub
4. Complete email verification

#### Step 2: Get API Key

1. Log in to Tavily dashboard
2. Go to "API Keys" section
3. Your API key is displayed (format: `tvly-...`)
4. Copy API key

**Note:** Tavily shows your key in dashboard, but generate new one if compromised

#### Step 3: Configure Credentials

Create credentials file:

```bash
# Create Tavily API credentials file
cat > watchers/credentials/tavily_api.json << 'EOF'
{
  "api_key": "tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
EOF

# Verify
cat watchers/credentials/tavily_api.json
```

#### Step 4: Test Connection

```bash
# Test Tavily Search integration
python .claude/skills/web-researcher/scripts/tavily_search.py "artificial intelligence"
```

**Expected output:**
```
Searching Tavily for: artificial intelligence

Found 5 results:

1. AI-Generated Answer
   URL: https://tavily.com
   ANSWER: Artificial intelligence (AI) is...

2. Wikipedia: Artificial Intelligence
   URL: https://en.wikipedia.org/wiki/...
   Score: 0.95
   Description...
```

### Search Modes

**Basic Search (default):**
- Fast results
- Lower credit usage
- Good for most queries

**Advanced Search:**
```python
from tavily_search import search_tavily
results = search_tavily("query", search_depth='advanced')
```
- More comprehensive
- Higher credit usage (2-3x)
- Best for research tasks

**With AI Answer:**
```python
results = search_tavily("query", include_answer=True)
```
- Includes AI-generated answer
- Extra credit cost
- Good for direct questions

### API Limits

**Free Tier:**
- 1,000 searches per month
- Basic search only
- 10 results max per query

**Paid Tiers:**
- **Starter:** $20/month - 10,000 searches
- **Pro:** $100/month - 100,000 searches
- **Enterprise:** Custom

### Troubleshooting

**Error: "Invalid API key"**
- Verify key starts with `tvly-`
- Check for extra spaces or newlines
- Regenerate in dashboard if needed

**Error: "Insufficient credits"**
- Check usage in dashboard
- Wait for monthly reset
- Upgrade plan if needed

**No results returned:**
- Tavily is selective - try broader query
- Use basic search instead of advanced
- Check query spelling

---

## Google Custom Search (Alternative)

### Overview

**Provider:** Google
**URL:** https://developers.google.com/custom-search
**Best for:** General web search, large scale
**Pricing:** 100 queries/day free, Paid from $5/1000 queries

### Setup Instructions

#### Step 1: Create Search Engine

1. Visit https://programmablesearchengine.google.com/
2. Click "Add" or "Create Search Engine"
3. Configure:
   - Name: "AI Employee Search"
   - Search sites: "Search the entire web"
   - Language: English
4. Click "Create"

#### Step 2: Get API Credentials

1. Note your **Search Engine ID** (cx parameter)
2. Visit https://developers.google.com/custom-search/v1/introduction
3. Click "Get a Key"
4. Create or select project
5. Copy **API Key**

#### Step 3: Configure Credentials

```bash
cat > watchers/credentials/google_search.json << 'EOF'
{
  "api_key": "AIzaSy...",
  "search_engine_id": "your-cx-id"
}
EOF
```

#### Step 4: Implementation

**Note:** Google Custom Search not yet implemented in web-researcher skill.
Use Brave or Tavily for now. Google integration can be added if needed.

### API Limits

- **Free:** 100 queries/day
- **Paid:** $5 per 1,000 queries
- No monthly subscription option

---

## DuckDuckGo API (Alternative)

### Overview

**Provider:** DuckDuckGo
**URL:** https://duckduckgo.com/api
**Best for:** Privacy-focused, no API key required
**Pricing:** Free

### Limitations

- No official search API (only instant answers)
- Rate limiting without authentication
- Results quality varies
- Not recommended for production

**Alternative:** Use Brave Search for privacy-focused option

---

## Bing Search API (Alternative)

### Overview

**Provider:** Microsoft Azure
**URL:** https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/
**Best for:** Enterprise-scale search
**Pricing:** Free tier (3 calls/sec), Paid from $7/1000 queries

### Setup

Requires Azure account and Azure Cognitive Services setup.
More complex than Brave/Tavily.
Not currently implemented in web-researcher skill.

---

## Comparison Matrix

| Feature | Brave | Tavily | Google Custom | Bing |
|---------|-------|--------|---------------|------|
| Free Tier | 2,500/month | 1,000/month | 100/day | 3 calls/sec |
| Pricing | $5/month | $20/month | $5/1000 | $7/1000 |
| Setup Complexity | Easy | Easy | Medium | Hard |
| Privacy Focus | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ |
| AI Optimization | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| Result Quality | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Documentation | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

**Recommendation:**
- **General use:** Brave Search (best free tier)
- **Technical/AI queries:** Tavily (AI-optimized)
- **High volume:** Google or Bing (if >3K queries/month)

---

## Best Practices

### API Key Security

1. **Never commit keys to Git**
   - Always use `.gitignore` for credentials
   - Rotate keys monthly
   - Use read-only keys when available

2. **Environment variables (optional)**
   ```bash
   export BRAVE_API_KEY="your-key"
   export TAVILY_API_KEY="your-key"
   ```

3. **Key rotation schedule**
   - Rotate every 30-90 days
   - Rotate immediately if compromised
   - Keep old key active during transition

### Rate Limiting

Implement query throttling:

```python
import time

def throttled_search(queries, delay=1.0):
    """Search with rate limiting."""
    results = []
    for query in queries:
        result = web_search(query)
        results.append(result)
        time.sleep(delay)  # Respect rate limits
    return results
```

### Cost Management

1. **Cache results**
   - Save search results to avoid duplicate queries
   - Implement TTL (Time To Live) for cache

2. **Batch queries**
   - Combine related searches
   - Use broader queries instead of multiple specific ones

3. **Monitor usage**
   - Track API calls in logs
   - Set up alerts for high usage
   - Review monthly costs

### Error Handling

```python
def safe_search(query, max_retries=3):
    """Search with retry logic."""
    for attempt in range(max_retries):
        try:
            return web_search(query)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(60)  # Wait 1 minute
                continue
            raise
        except APIError as e:
            logging.error(f"Search failed: {e}")
            return None
```

---

## Troubleshooting Common Issues

### Authentication Failures

**Symptoms:**
- "Invalid API key"
- "Unauthorized"
- 401 errors

**Solutions:**
1. Verify API key in dashboard
2. Check credentials file format (valid JSON)
3. Ensure no extra whitespace in key
4. Regenerate key if needed
5. Verify account is active

### Rate Limiting

**Symptoms:**
- "Rate limit exceeded"
- 429 errors
- Throttled responses

**Solutions:**
1. Wait for limit reset
2. Implement exponential backoff
3. Cache search results
4. Upgrade API tier
5. Use multiple providers

### No Results

**Symptoms:**
- Empty results array
- "No results found"

**Solutions:**
1. Rephrase query (broader or more specific)
2. Check spelling
3. Try different provider
4. Verify query isn't too niche
5. Check API status page

### Slow Responses

**Symptoms:**
- Timeouts
- Long response times

**Solutions:**
1. Increase timeout setting
2. Use faster provider (Brave usually faster)
3. Check network connection
4. Try basic search instead of advanced

---

## Additional Resources

**Brave Search:**
- API Docs: https://brave.com/search/api/
- Support: https://community.brave.com/
- Status: https://status.brave.com/

**Tavily:**
- API Docs: https://docs.tavily.com/
- Dashboard: https://app.tavily.com/
- Support: support@tavily.com

**General:**
- Search Engine Comparison: https://searchengineland.com/
- API Best Practices: https://restfulapi.net/

---

**Related Documentation:**
- See main `SKILL.md` for usage examples
- See `verification_guide.md` for source validation
- See `use_cases.md` for common scenarios
