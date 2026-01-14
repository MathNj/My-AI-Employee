---
name: linkedin-poster
description: Automatically create and post business updates to LinkedIn to generate sales leads and brand awareness. Use this skill when you need to (1) Post business achievements or updates to LinkedIn, (2) Share thought leadership content, (3) Announce new services or products, (4) Create scheduled LinkedIn posts, or (5) Generate engagement through professional social media content. Integrates with approval workflow for human oversight before posting.
---

# LinkedIn Poster

## Overview

This skill enables automated LinkedIn posting for business development and brand building. It handles OAuth authentication, post creation from templates, approval workflows, and tracking engagement metrics. Designed for autonomous operation while maintaining human oversight through the approval system.

## Quick Start

### Basic LinkedIn Post

```python
# Simple post creation
python scripts/linkedin_post.py \
  --message "Excited to announce our new AI automation service!" \
  --create-approval
```

This creates an approval request in `/Pending_Approval` for human review before posting.

### Using Templates

```python
# Generate post from template
python scripts/generate_post.py \
  --template achievement \
  --data '{"achievement": "Completed Bronze Tier AI Employee", "impact": "24/7 automation"}'
```

## Core Workflows

### Workflow 1: Create and Post

1. **Generate content** from template or custom message
2. **Create approval request** in `/Pending_Approval` folder
3. **Human reviews** and moves to `/Approved` folder
4. **Approval processor** detects approval and calls this skill
5. **Post to LinkedIn** via API
6. **Log activity** to Dashboard and audit logs

### Workflow 2: Scheduled Posts

1. **Create scheduled post** with future timestamp
2. **Scheduler-manager** triggers at specified time
3. **Follows standard approval workflow**
4. **Posts automatically** after approval

### Workflow 3: Template-Based Posts

1. **Select template** (achievement, service, thought-leadership, etc.)
2. **Fill template data** (variables specific to post type)
3. **Generate formatted post** with hashtags and formatting
4. **Submit for approval** and post

## LinkedIn API Setup

### Prerequisites

1. **LinkedIn Developer Account:**
   - Visit: https://www.linkedin.com/developers/
   - Create new app
   - Set redirect URL: `http://localhost:8080/callback`

2. **Required Scopes:**
   - `w_member_social` (create posts)
   - `r_liteprofile` (get profile info)

3. **Get Credentials:**
   - Client ID from app settings
   - Client Secret from app settings
   - Store in `watchers/credentials/linkedin_credentials.json`

### Initial Setup

```bash
# Store credentials
python scripts/validate_credentials.py --setup

# Test connection
python scripts/test_connection.py

# First OAuth flow (opens browser)
python scripts/linkedin_post.py --authenticate
```

See `references/oauth_setup.md` for detailed setup instructions.

## Post Creation

### Method 1: Direct Message

```python
python scripts/linkedin_post.py \
  --message "Your post content here" \
  --hashtags "AIAutomation,BusinessGrowth" \
  --create-approval
```

### Method 2: Template-Based

```python
# Achievement post
python scripts/generate_post.py \
  --template achievement \
  --achievement "Reached 1000 followers" \
  --impact "Growing community"

# Service announcement
python scripts/generate_post.py \
  --template service \
  --service "AI Employee Automation" \
  --benefit "Save 20 hours/week"

# Thought leadership
python scripts/generate_post.py \
  --template thought-leadership \
  --topic "Future of AI Automation" \
  --insight "Personal AI employees will transform 2026"
```

### Method 3: Via Claude Code

Simply ask:
- "Post to LinkedIn about our new service"
- "Create a LinkedIn post celebrating this achievement"
- "Share this on LinkedIn with appropriate hashtags"

Claude will automatically use this skill and create an approval request.

## Post Templates

Available templates in `references/post_templates.md`:

### 1. Achievement Template
Celebrate business milestones and wins
- Project completions
- Client successes
- Team achievements
- Business growth

### 2. Service Announcement Template
Promote new offerings and capabilities
- New services
- Feature launches
- Product updates
- Special offers

### 3. Thought Leadership Template
Share expertise and insights
- Industry trends
- Best practices
- Case studies
- Lessons learned

### 4. Behind-the-Scenes Template
Humanize your brand
- Team culture
- Work process
- Day-in-the-life
- Company values

### 5. Engagement Template
Drive interaction and discussion
- Questions to audience
- Polls and surveys
- Request feedback
- Share experiences

See `references/post_templates.md` for complete templates with examples.

## Approval Workflow Integration

### Creating Approval Requests

When posting, always create an approval request:

```python
python scripts/linkedin_post.py \
  --message "Your content" \
  --create-approval  # Creates approval file
```

This creates a file in `/Pending_Approval/LINKEDIN_POST_[timestamp].md`:

```markdown
---
type: linkedin_post
action: post_to_linkedin
message: "Your post content..."
hashtags: ["AIAutomation", "BusinessGrowth"]
created: 2026-01-11T15:30:00Z
expires: 2026-01-12T15:30:00Z
status: pending
---

## LinkedIn Post Preview

Your post content...

#AIAutomation #BusinessGrowth

## To Approve
Move this file to /Approved folder

## To Reject
Move this file to /Rejected folder
```

### Processing Approved Posts

The `approval-processor` skill detects approved LinkedIn posts and executes:

```python
# Approval processor automatically calls:
python scripts/linkedin_post.py --execute-approved /path/to/approved/file.md
```

## Best Practices

### Posting Frequency
- **Optimal:** 3-5 posts per week
- **Minimum:** 2 posts per week
- **Maximum:** 2 posts per day
- **Best times:** Tuesday-Thursday, 9 AM - 12 PM

### Content Guidelines
- **Length:** 150-300 characters (optimal engagement)
- **Hashtags:** 3-5 relevant hashtags
- **Call-to-action:** Include in 80% of posts
- **Visuals:** Add images/videos when possible (not implemented yet)
- **Authenticity:** Personal voice > corporate speak

### Engagement Tips
- Ask questions to drive comments
- Tag relevant people/companies
- Share genuine insights and lessons
- Respond to comments within 24 hours
- Mix content types (achievements, insights, questions)

See `references/best_practices.md` for comprehensive guidelines.

## Hashtag Strategy

### Industry Hashtags (Always relevant)
- #BusinessAutomation
- #AIEmployee
- #Productivity
- #DigitalTransformation
- #FutureOfWork

### Topic-Specific Hashtags
- Automation: #AIAutomation, #WorkAutomation
- Business: #SmallBusiness, #Entrepreneurship
- Tech: #ArtificialIntelligence, #MachineLearning
- Productivity: #ProductivityHacks, #TimeManagement

### Engagement Hashtags
- #MondayMotivation
- #TechTuesday
- #ThoughtLeadership
- #FridayFeeling

Limit to 5 hashtags per post for maximum effectiveness.

## Error Handling

### Common Issues

**OAuth token expired:**
```bash
python scripts/linkedin_post.py --authenticate
```

**Rate limit exceeded:**
- LinkedIn allows 100 posts per day
- Wait 24 hours or reduce posting frequency

**Post rejected by LinkedIn:**
- Check content guidelines
- Avoid spam-like content
- Remove prohibited links

**API connection failed:**
```bash
python scripts/test_connection.py
```

### Logs

All activity logged to:
- `/Logs/linkedin_activity_[date].json` - API calls and responses
- `/Logs/actions_[date].json` - System actions
- `Dashboard.md` - Recent activity section

## Integration with Other Skills

### With approval-processor
Automatically posts after approval:
```python
# approval-processor detects approved LinkedIn posts
# and calls this skill to execute
```

### With scheduler-manager
Schedule posts in advance:
```bash
# Schedule daily post at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "linkedin-daily-post" \
  --command "python scripts/generate_post.py --template daily-tip" \
  --schedule "0 9 * * *"
```

### With dashboard-updater
Track LinkedIn activity:
- Posts created
- Posts approved/rejected
- Engagement metrics (future)

## Tracking and Analytics

### Post Metrics (Future Feature)
Currently creates posts only. Future versions will track:
- Impressions
- Engagements (likes, comments, shares)
- Click-through rates
- Follower growth

### Current Tracking
- Number of posts created
- Number of posts approved/rejected
- Posting frequency
- Template usage

## Scripts Reference

### linkedin_post.py
Main posting script with full OAuth and API integration.

**Usage:**
```bash
# Authenticate
python scripts/linkedin_post.py --authenticate

# Create post with approval
python scripts/linkedin_post.py --message "Content" --create-approval

# Execute approved post
python scripts/linkedin_post.py --execute-approved /path/to/file.md

# Test mode (dry run)
python scripts/linkedin_post.py --message "Test" --dry-run
```

### generate_post.py
Generate posts from templates with variable substitution.

**Usage:**
```bash
# From template
python scripts/generate_post.py --template achievement --data '{...}'

# List templates
python scripts/generate_post.py --list-templates

# Custom template
python scripts/generate_post.py --custom-template /path/to/template.md
```

### test_connection.py
Verify LinkedIn API connectivity and credentials.

**Usage:**
```bash
# Test connection
python scripts/test_connection.py

# Verbose output
python scripts/test_connection.py --verbose
```

### validate_credentials.py
Validate and set up LinkedIn API credentials.

**Usage:**
```bash
# Setup wizard
python scripts/validate_credentials.py --setup

# Validate existing
python scripts/validate_credentials.py --validate

# Show current config
python scripts/validate_credentials.py --show
```

## Security Considerations

### Credential Storage
- **Never commit** credentials to Git
- Store in `watchers/credentials/linkedin_credentials.json`
- Protected by `.gitignore`
- Use environment variables in production

### OAuth Tokens
- Access tokens expire after 60 days
- Refresh tokens valid for 1 year
- Re-authenticate when expired
- Tokens encrypted at rest

### Approval Workflow
- **All posts require approval** by default
- Can configure auto-approve for specific templates (not recommended)
- Approval expires after 24 hours
- Rejected posts logged for audit

## Troubleshooting

### Posts not appearing on LinkedIn
1. Check account permissions
2. Verify company page vs. personal profile
3. Review LinkedIn posting guidelines
4. Check for shadowban (rare)

### Authentication issues
1. Verify client ID and secret
2. Check redirect URL matches app settings
3. Clear token cache and re-authenticate
4. Ensure app is not in limited mode

### Template not working
1. Verify template exists in `references/post_templates.md`
2. Check JSON data format
3. Ensure all required variables provided
4. Test with `--dry-run` flag

## References

- `references/linkedin_api_guide.md` - Complete API documentation
- `references/post_templates.md` - All post templates with examples
- `references/best_practices.md` - LinkedIn posting best practices
- `references/oauth_setup.md` - OAuth setup step-by-step

## Assets

- `assets/post_templates.json` - JSON template definitions
- `assets/brand_voice.md` - Your brand voice guidelines (customize this)

---

**Note:** This skill requires LinkedIn Developer account and API credentials. See `references/oauth_setup.md` for setup instructions.
