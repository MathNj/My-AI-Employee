---
name: social-media-manager
description: Unified social media management for LinkedIn, Facebook, Instagram, and Twitter/X to generate sales leads and brand awareness. Use when the user needs to (1) Post to any social media platform, (2) Schedule posts across platforms, (3) Share business updates or achievements, (4) Announce products or services, (5) Generate engagement summaries, or (6) Track social media analytics. Triggers include "post to LinkedIn", "share on Facebook", "post to Instagram", "tweet this", "post to all platforms", "schedule social post", "generate social media summary".
---

# Social Media Manager

Unified platform for posting business content to LinkedIn, Facebook, Instagram, and Twitter/X with approval workflow and analytics.

## Quick Start

### Post to Single Platform

```bash
# LinkedIn post
python scripts/post_to_platform.py --platform linkedin --message "Excited to announce our new AI service!"

# Facebook post
python scripts/post_to_platform.py --platform facebook --message "Check out our latest update"

# Instagram post
python scripts/post_to_platform.py --platform instagram --message "Behind the scenes" --image photo.jpg

# Twitter/X post
python scripts/post_to_platform.py --platform twitter --message "Quick update on our progress"
```

### Post to Multiple Platforms

```bash
# Post to all platforms
python scripts/post_to_platform.py --platforms all --message "Major announcement!" --create-approval

# Post to specific platforms
python scripts/post_to_platform.py --platforms linkedin,facebook,twitter --message "Business update"
```

### Use Template

```bash
# Achievement post
python scripts/generate_from_template.py --template achievement --data '{"achievement": "Reached 1000 customers", "impact": "10x growth"}'

# Service announcement
python scripts/generate_from_template.py --template service --platform all
```

## Core Workflows

### Workflow 1: Single Platform Post

1. User requests post or Claude generates content
2. Create draft with platform-specific formatting
3. Create approval file in `/Pending_Approval`
4. Human reviews and moves to `/Approved`
5. approval-processor triggers social-media-manager
6. Post to selected platform via MCP
7. Track engagement metrics
8. Update Dashboard

### Workflow 2: Multi-Platform Campaign

1. Generate content for announcement
2. Adapt message for each platform:
   - **LinkedIn:** Professional, detailed (up to 3,000 chars)
   - **Facebook:** Conversational, engaging (up to 63,206 chars)
   - **Instagram:** Visual-first, brief (up to 2,200 chars)
   - **Twitter/X:** Concise, impactful (280 chars)
3. Create single approval file with all platforms
4. Human approves
5. Post to all platforms simultaneously
6. Track cross-platform engagement

### Workflow 3: Scheduled Campaign

1. Create scheduled post with future timestamp
2. scheduler-manager triggers at specified time
3. Follows standard approval workflow
4. Posts automatically after approval
5. Logs all activity

## Platform Integration

### LinkedIn (Already Integrated)

**MCP:** ✅ linkedin-mcp (existing)
**Character Limit:** 3,000
**Best For:**
- Professional announcements
- Thought leadership
- B2B content
- Service updates

**Templates:**
- Service announcement
- Achievement post
- Thought leadership
- Customer success story
- Behind-the-scenes

### Facebook (Requires Meta MCP)

**MCP:** ❌ Needs to be built (meta-mcp)
**Character Limit:** 63,206
**Best For:**
- Community engagement
- Event promotion
- Customer stories
- Behind-the-scenes content

**Templates:**
- Business update
- Event promotion
- Customer testimonial
- Product showcase
- Community engagement

### Instagram (Requires Meta MCP)

**MCP:** ❌ Needs to be built (meta-mcp)
**Character Limit:** 2,200
**Best For:**
- Visual content
- Product photos
- Team culture
- Process demonstrations

**Templates:**
- Product showcase
- Behind-the-scenes
- Team spotlight
- Process visualization
- Customer success

**Requirements:**
- Image required
- Square or vertical format recommended
- Hashtags essential

### Twitter/X (Requires X MCP)

**MCP:** ❌ Needs to be built (x-mcp)
**Character Limit:** 280
**Best For:**
- Quick updates
- Announcements
- Engagement
- Trend participation

**Templates:**
- Quick announcement
- Achievement share
- Thread starter
- Industry insight
- Question to followers

## Platform-Specific Formatting

### Auto-Formatting Rules

**LinkedIn:**
- Professional tone
- Include relevant hashtags (3-5)
- Add emojis sparingly
- Break into paragraphs for readability
- Call-to-action at end

**Facebook:**
- Conversational tone
- Ask questions for engagement
- Use line breaks for readability
- Include relevant hashtags
- Add emoji for personality

**Instagram:**
- Brief, punchy text
- Heavy emoji usage
- Hashtag list at end (10-30 hashtags)
- Line breaks for readability
- Strong call-to-action

**Twitter/X:**
- Concise, impactful
- Use thread if >280 chars
- Relevant hashtags (2-3)
- @ mentions for engagement
- Emojis for personality

## Approval Workflow

### Creating Approval Request

When posting with approval:

**File:** `/Pending_Approval/SOCIAL_POST_<timestamp>.md`

```yaml
---
type: social_post
platforms: ["linkedin", "facebook", "instagram", "twitter"]
created: 2026-01-12T10:30:00Z
schedule: null  # or future timestamp
status: pending
---

## Post Content

### LinkedIn (3000 char limit)
Excited to announce that we've reached 1,000 customers! 🎉

This milestone represents months of hard work from our amazing team and the trust of our incredible customers. Thank you for being part of our journey.

What started as a vision to revolutionize business automation has grown into a platform serving companies worldwide. We're just getting started!

#BusinessGrowth #Milestone #CustomerSuccess #AIAutomation

### Facebook (engaging version)
We just hit 1,000 customers! 🎊

Big shoutout to our team and every single customer who believed in us. You've helped us build something special.

Can't wait to show you what's next! 🚀

### Instagram (visual + brief)
1,000 customers and counting! 🎉🎉🎉

Your trust means everything. Thank you for growing with us! 💙

[Image: Team celebration photo]

#Milestone #Startup #BusinessGrowth #ThankYou #CustomerLove #AI #Automation #SmallBusiness #Entrepreneur #Success

### Twitter/X (280 char max)
🎉 1,000 customers milestone!

Huge thanks to our amazing team and every customer who believed in our vision. This is just the beginning! 🚀

#Startup #Milestone #Growth
```

**To Approve:** Move to `/Approved` folder
**To Reject:** Move to `/Rejected` folder

### Approval Processing

```
approval-processor detects file in /Approved
    ↓
Parses platform list
    ↓
For each platform:
    - Format content appropriately
    - Call platform MCP
    - Post content
    - Log result
    ↓
Track engagement metrics
    ↓
Move to /Done
    ↓
Update Dashboard
```

## Templates

### Template: Achievement Post

**Use When:** Celebrating milestones, goals reached, awards won

**Variables:**
- `achievement`: What was accomplished
- `impact`: Business impact/numbers
- `team_shoutout`: Optional team recognition

**Example:**
```bash
python scripts/generate_from_template.py \
  --template achievement \
  --data '{
    "achievement": "Reached $100K MRR",
    "impact": "300% growth in 6 months",
    "team_shoutout": "Amazing engineering team"
  }'
```

**Output:**
- LinkedIn: Professional announcement with metrics
- Facebook: Celebratory with team recognition
- Instagram: Visual celebration with emojis
- Twitter: Concise milestone share

### Template: Service Announcement

**Use When:** Launching new features, products, or services

**Variables:**
- `service_name`: Name of service/product
- `key_benefit`: Main value proposition
- `cta_link`: Call-to-action link

### Template: Customer Success Story

**Use When:** Sharing customer testimonials or case studies

**Variables:**
- `customer_name`: Client name (or anonymous)
- `problem`: Challenge they faced
- `solution`: How you helped
- `result`: Measurable outcome

### Template: Thought Leadership

**Use When:** Sharing industry insights or expertise

**Variables:**
- `topic`: Industry trend or insight
- `perspective`: Your unique take
- `cta`: Engagement question

### Template: Behind-the-Scenes

**Use When:** Showing company culture or process

**Variables:**
- `activity`: What's happening
- `team_member`: Optional team spotlight
- `insight`: What makes it interesting

See `references/templates.md` for full template library and customization guide.

## Analytics & Reporting

### Track Engagement

```bash
# Daily analytics check
python scripts/analytics_dashboard.py --period today

# Weekly summary
python scripts/analytics_dashboard.py --period week

# Platform comparison
python scripts/analytics_dashboard.py --compare-platforms
```

### Metrics Tracked

**Per Platform:**
- Impressions/Reach
- Engagement (likes, comments, shares)
- Click-through rate
- Follower growth
- Best performing posts

**Cross-Platform:**
- Total reach
- Engagement rate
- Platform performance comparison
- Optimal posting times
- Content type performance

### Weekly Summary

**Generated:** Every Monday morning (via ceo-briefing-generator integration)

**Location:** `/Logs/Social_Media_Summary_YYYY-MM-DD.md`

**Includes:**
- Posts published (by platform)
- Total engagement
- Top performing post
- Follower growth
- Recommendations for next week

## Hashtag Optimization

### Auto-Generated Hashtags

The skill suggests hashtags based on:
- Content analysis
- Platform best practices
- Trending topics
- Historical performance

**LinkedIn (3-5 hashtags):**
```python
analyze_content(post)
    ↓
Extract key topics
    ↓
Match to professional hashtags
    ↓
Suggest: #BusinessGrowth #AIAutomation #Innovation
```

**Instagram (10-30 hashtags):**
```python
analyze_content(post)
    ↓
Generate tiered hashtag strategy:
    - High competition: #Business #Success
    - Medium competition: #SmallBusiness #Entrepreneur
    - Niche: #AIforBusiness #AutomationTools
```

**Twitter/X (2-3 hashtags):**
```python
analyze_content(post)
    ↓
Identify trending hashtags
    ↓
Suggest: #Startup #TechNews
```

See `references/hashtag_strategy.md` for hashtag optimization guide.

## Scheduling

### Schedule Post

```bash
# Schedule for specific time
python scripts/post_to_platform.py \
  --platforms linkedin,facebook \
  --message "New blog post!" \
  --schedule "2026-01-15T09:00:00Z" \
  --create-approval
```

**Process:**
1. Create approval request with schedule timestamp
2. Human approves
3. approval-processor moves to `/Scheduled` folder
4. scheduler-manager triggers at specified time
5. Post executes automatically
6. Result logged

### Optimal Posting Times

**Default recommendations (customizable):**

**LinkedIn:**
- Tuesday-Thursday, 9-11 AM
- Best: Tuesday 10 AM

**Facebook:**
- Monday, Wednesday, Friday 1-3 PM
- Best: Wednesday 2 PM

**Instagram:**
- Monday, Wednesday 11 AM - 1 PM
- Best: Wednesday 12 PM

**Twitter/X:**
- Weekdays 9-11 AM, 5-6 PM
- Best: Wednesday 9 AM

See `references/optimal_times.md` for detailed timing guide.

## Content Guidelines

### LinkedIn Best Practices

✅ **Do:**
- Share professional insights
- Include metrics and data
- Tag relevant people/companies
- Use hashtags strategically
- Ask thought-provoking questions

❌ **Don't:**
- Over-promote
- Use excessive emojis
- Post too frequently (max 1-2/day)
- Share overly casual content

### Facebook Best Practices

✅ **Do:**
- Engage with community
- Share behind-the-scenes
- Ask questions
- Use visual content
- Respond to comments quickly

❌ **Don't:**
- Post identical content to other platforms
- Over-use hashtags
- Ignore negative comments

### Instagram Best Practices

✅ **Do:**
- Prioritize high-quality visuals
- Use all 30 hashtags
- Post consistently
- Use Stories for engagement
- Include clear CTAs

❌ **Don't:**
- Post low-quality images
- Use irrelevant hashtags
- Ignore aesthetics
- Forget alt text

### Twitter/X Best Practices

✅ **Do:**
- Be concise and impactful
- Use threads for longer content
- Engage with mentions
- Participate in trends
- Tweet regularly

❌ **Don't:**
- Exceed 280 characters in single tweet
- Overuse hashtags (max 2-3)
- Auto-post from other platforms
- Ignore conversations

See `references/platform_guidelines.md` for complete best practices.

## Integration with Other Skills

### approval-processor

```
social-media-manager creates post
    ↓
Saves to /Pending_Approval
    ↓
Human reviews and approves
    ↓
approval-processor detects
    ↓
Routes back to social-media-manager
    ↓
Posts to platforms
```

### linkedin-poster

```
social-media-manager for LinkedIn
    ↓
Uses existing linkedin-poster functionality
    ↓
Leverages templates and MCP
    ↓
Unified workflow
```

### ceo-briefing-generator

```
Weekly briefing generated
    ↓
Includes social media summary
    ↓
Shows engagement metrics
    ↓
Recommends content strategy
```

### scheduler-manager

```
Schedule future post
    ↓
scheduler-manager triggers at time
    ↓
Executes post workflow
    ↓
Logs activity
```

## Error Handling

### Common Issues

**Rate Limiting:**
- LinkedIn: 100 posts/day
- Facebook: Varies by page
- Instagram: 25 posts/day (recommended)
- Twitter: 2,400 tweets/day

**Action:** Queue posts, retry with backoff

**Authentication Expired:**
- Automatic token refresh
- If refresh fails, alert human
- Pause operations until re-authenticated

**Content Rejected:**
- Platform policy violation
- Log error with reason
- Move to /Rejected folder
- Alert human for review

**Image Format Issues:**
- Auto-resize if too large
- Convert to supported format
- Compress if needed
- Maintain aspect ratio

## Security & Compliance

### Content Safety

Before posting:
- Check for sensitive information
- Verify no confidential data
- Ensure compliance with platform policies
- Validate links are safe

### Platform Policies

**LinkedIn:**
- No misleading content
- No spam or automation abuse
- Professional standards

**Facebook:**
- Community standards
- No false information
- Authentic engagement only

**Instagram:**
- No fake engagement
- Authentic content only
- Follow copyright rules

**Twitter/X:**
- No hate speech
- No manipulation
- Authentic behavior

### Audit Trail

Every post logged to `/Logs/social_media_activity_YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "post_published",
  "platforms": ["linkedin", "facebook"],
  "content": "Achievement announcement...",
  "engagement": {
    "linkedin": {"likes": 45, "comments": 12, "shares": 8},
    "facebook": {"likes": 32, "comments": 5, "shares": 3}
  },
  "skill": "social-media-manager"
}
```

## Troubleshooting

**Posts Not Publishing:**
1. Check MCP servers running
2. Verify OAuth tokens valid
3. Test connection: `python scripts/test_connections.py`
4. Review error logs

**Low Engagement:**
1. Review analytics: `python scripts/analytics_dashboard.py`
2. Check posting times
3. Analyze content type performance
4. Adjust hashtag strategy

**Image Upload Fails:**
1. Check file size (< 5MB)
2. Verify format (JPG, PNG)
3. Ensure aspect ratio correct
4. Try compressing image

## Scripts Reference

### post_to_platform.py

**Usage:**
```bash
python scripts/post_to_platform.py [options]

Options:
  --platform PLATFORM       Single platform (linkedin/facebook/instagram/twitter)
  --platforms PLATFORMS     Multiple platforms (comma-separated or 'all')
  --message TEXT           Post content
  --image PATH             Image file path
  --schedule TIMESTAMP     Future posting time
  --create-approval        Create approval request
```

### generate_from_template.py

**Usage:**
```bash
python scripts/generate_from_template.py [options]

Options:
  --template NAME          Template name
  --data JSON              Template variables
  --platforms PLATFORMS    Target platforms
  --create-approval        Create approval request
```

### analytics_dashboard.py

**Usage:**
```bash
python scripts/analytics_dashboard.py [options]

Options:
  --period PERIOD          Period (today/week/month)
  --platform PLATFORM      Specific platform
  --compare-platforms      Compare all platforms
  --export FORMAT          Export format (json/csv/md)
```

## References

- `references/platform_setup.md` - Setup guides for each platform
- `references/templates.md` - Complete template library
- `references/hashtag_strategy.md` - Hashtag optimization
- `references/optimal_times.md` - Best posting times
- `references/platform_guidelines.md` - Content best practices
- `references/mcp_setup.md` - MCP server setup

---

**Dependencies:**
- LinkedIn MCP (existing)
- Meta MCP (Facebook + Instagram) - **needs to be built**
- X MCP (Twitter/X) - **needs to be built**
- approval-processor skill
- scheduler-manager skill
