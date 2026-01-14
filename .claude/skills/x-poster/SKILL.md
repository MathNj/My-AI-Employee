---
name: x-poster
description: Automatically create and post tweets to X/Twitter using Playwright browser automation. Supports persistent login sessions, approval workflow, character limit validation, and scheduled posting. No API costs - uses browser automation like WhatsApp watcher.
---

# X/Twitter Poster

## Overview

This skill enables automated X/Twitter posting using Playwright browser automation (similar to the WhatsApp watcher pattern). It bypasses the expensive X API by using browser automation, handles persistent authentication, integrates with the approval workflow system, and supports scheduled posting through the scheduler-manager.

**Key Features:**
- Browser automation via Playwright (no API costs)
- Persistent session (login once, stay logged in)
- 280 character limit validation
- Human-in-the-loop approval workflow
- Complete activity logging
- Headless and visible modes
- Integration with scheduler-manager

## Quick Start

### Basic Tweet Creation

```bash
# Create tweet with approval workflow
python scripts/x_post.py --message "Exciting announcement about our AI service!" --create-approval
```

This creates an approval request in `/Pending_Approval` for human review before posting.

### First-Time Setup

```bash
# Authenticate (run in visible mode first time)
python scripts/x_post.py --authenticate --no-headless

# Check login status
python scripts/x_post.py --check-login
```

## Core Workflows

### Workflow 1: Create and Post Tweet

1. **Generate tweet content** (manual or from template)
2. **Create approval request** with `--create-approval`
3. **Human reviews** tweet preview and character count
4. **Human approves** by moving file to `/Approved` folder
5. **Approval processor** detects approval and calls this skill
6. **Post to X/Twitter** via Playwright browser automation
7. **Log activity** to Dashboard and audit logs

### Workflow 2: Scheduled Tweets

1. **Create scheduled post** via scheduler-manager
2. **Scheduler triggers** at specified time
3. **Creates approval request** automatically
4. **Follows standard approval workflow**
5. **Posts automatically** after human approval

### Workflow 3: Dry Run Testing

1. **Test tweet content** with `--dry-run` flag
2. **Preview character count** and formatting
3. **Verify login status** before creating approval
4. **Submit for approval** when ready

## Initial Setup

### Prerequisites

- **Python 3.9+** installed
- **Playwright** installed (already available from WhatsApp watcher)
- **Chromium browser** installed via Playwright

### Verify Installation

```bash
# Check Playwright
python -c "import playwright; print('Playwright OK')"

# Check Chromium
playwright show-browsers

# Expected output: chromium ... installed
```

### First-Time Authentication

**Important:** Always run authentication in visible mode first time.

```bash
# Step 1: Authenticate with X/Twitter
python scripts/x_post.py --authenticate --no-headless
```

This will:
1. Open browser to Twitter login page
2. Wait for you to manually enter credentials
3. Complete 2FA if required
4. Detect successful login
5. Save session to `assets/session/` directory

**Session persists:** You only need to authenticate once. The session is saved and reused for all future posts.

### Test Login Status

```bash
# Verify you're logged in
python scripts/x_post.py --check-login
```

### Create First Tweet

```bash
# Dry run to test
python scripts/x_post.py --message "Hello World from my AI Employee!" --dry-run

# Create approval request
python scripts/x_post.py --message "Hello World from my AI Employee!" --create-approval
```

## Tweet Creation

### Method 1: Direct Command Line

```bash
# Create tweet with approval
python scripts/x_post.py \
  --message "Just launched our new AI automation service! Learn more at example.com" \
  --create-approval

# Character count: 68/280
```

### Method 2: Via Claude Code

Simply ask Claude:
- "Post to X/Twitter about our new feature"
- "Create a tweet announcing this achievement"
- "Tweet about our latest update"

Claude will automatically use this skill and create an approval request.

### Method 3: Scheduled Posts

```bash
# Schedule daily tweet at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "x-daily-update" \
  --command "python .claude/skills/x-poster/scripts/x_post.py --message 'Daily business update!' --create-approval" \
  --schedule "0 9 * * *"
```

## Approval Workflow Integration

### Creating Approval Requests

When using `--create-approval`, a file is created in `/Pending_Approval`:

**File:** `X_POST_2026-01-14T10-30-00.md`

```markdown
---
type: x_post
action: post_to_x
message: "Your tweet content here"
created: 2026-01-14T10:30:00Z
expires: 2026-01-15T10:30:00Z
status: pending
---

# X/Twitter Post Approval Request

## Tweet Preview

Your tweet content here

**Character count:** 45/280

---

## Post Details

- **Type:** X/Twitter Post
- **Character Count:** 45/280
- **Created:** 2026-01-14 10:30:00
- **Expires:** 2026-01-15 10:30:00

## Approval Instructions

**To Approve:** Move this file to `/Approved` folder
**To Reject:** Move this file to `/Rejected` folder

**Note:** This approval expires in 24 hours
```

### Processing Approved Posts

The `approval-processor` skill automatically detects approved X posts and executes:

```bash
# Approval processor automatically calls:
python scripts/x_post.py --execute-approved /path/to/approved/file.md
```

**On Success:** File moved to `/Done` folder
**On Failure:** File moved to `/Failed` folder with error logged

## Character Limit Handling

X/Twitter has a strict **280 character limit** for tweets.

### Validation

Character validation happens at **two points**:

1. **Approval Creation:** Invalid tweets are rejected before creating approval file
2. **Posting:** Double-checked before actual post

```bash
# This will fail with clear error
python scripts/x_post.py --message "$(python -c 'print("A" * 300)')" --create-approval

# Output: ❌ Invalid tweet: Tweet exceeds 280 character limit (300 chars)
```

### Character Counting

- Regular characters: 1 char each
- Emojis: 1-2 chars (Unicode)
- Line breaks: 1 char (`\n`)
- URLs: Auto-shortened by Twitter (all count as 23 chars)

**Pro Tip:** Keep tweets under 270 characters to account for potential URL shortening variations.

## Best Practices

### Posting Frequency

- **Optimal:** 3-5 tweets per week
- **Minimum:** 2 tweets per week
- **Maximum:** 10 tweets per day (avoid spam)
- **Best times:** Tuesday-Thursday, 9 AM - 5 PM local time

### Content Guidelines

- **Length:** 150-240 characters (optimal engagement)
- **Hashtags:** 1-3 relevant hashtags (2 is ideal)
- **Call-to-action:** Include in 70% of tweets
- **Links:** Always include when promoting content
- **Authenticity:** Personal voice > corporate speak
- **Engagement:** Ask questions to drive replies

### Hashtag Strategy

**Industry Hashtags (Always relevant):**
- #AI
- #Automation
- #BusinessAutomation
- #Productivity
- #EntrepreneurLife

**Topic-Specific:**
- Tech: #TechInnovation, #AITools
- Business: #SmallBusiness, #StartupLife
- Productivity: #WorkSmart, #Efficiency

**Engagement Hashtags:**
- #MondayMotivation
- #TechTuesday
- #ThursdayThoughts
- #FridayFeeling

**Rule:** Maximum 3 hashtags per tweet. 2 is optimal for engagement.

## Error Handling

### Common Issues

**Session Expired:**
```bash
# Re-authenticate
python scripts/x_post.py --authenticate --no-headless
```

**UI Selectors Changed:**
- X/Twitter frequently updates their UI
- Script uses multiple fallback selectors
- If all selectors fail, clear error message shown
- See `references/selectors_guide.md` for updating selectors

**Character Limit Exceeded:**
```bash
# Error before approval is created
❌ Invalid tweet: Tweet exceeds 280 character limit (285 chars)
```

**Not Logged In:**
```bash
# Check login status
python scripts/x_post.py --check-login

# If not logged in, re-authenticate
python scripts/x_post.py --authenticate --no-headless
```

**Rate Limited:**
- Twitter may throttle if posting too frequently
- Wait 15-30 minutes before retrying
- Reduce posting frequency

### Logs

All activity logged to:
- `AI_Employee_Vault/Logs/x_activity_[date].json` - API calls and responses
- `AI_Employee_Vault/Logs/approval_activity_[date].json` - Approval workflow
- `Dashboard.md` - Recent activity section

## Integration with Other Skills

### With approval-processor

Automatically posts after approval:
```python
# approval-processor detects approved X posts (type: x_post)
# and calls this skill to execute via Playwright
```

### With scheduler-manager

Schedule tweets in advance:
```bash
# Schedule weekly update every Monday at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "x-weekly-update" \
  --command "python .claude/skills/x-poster/scripts/x_post.py --message 'Weekly update tweet' --create-approval" \
  --schedule "0 9 * * 1"
```

### With dashboard-updater

Track X/Twitter activity:
- Tweets created
- Tweets approved/rejected
- Posting frequency
- Success/failure rates

## Scripts Reference

### x_post.py

Main posting script with Playwright automation.

**Usage:**
```bash
# Authenticate
python scripts/x_post.py --authenticate --no-headless

# Check login status
python scripts/x_post.py --check-login

# Create tweet with approval
python scripts/x_post.py --message "Content" --create-approval

# Execute approved tweet
python scripts/x_post.py --execute-approved /path/to/file.md

# Test mode (dry run)
python scripts/x_post.py --message "Test" --dry-run

# Visible mode (for debugging)
python scripts/x_post.py --message "Debug" --dry-run --no-headless
```

**Arguments:**
- `--authenticate` - Interactive login flow
- `--check-login` - Verify login status
- `--message "text"` - Tweet content (max 280 chars)
- `--create-approval` - Create approval request
- `--execute-approved path` - Post approved tweet
- `--dry-run` - Preview without posting
- `--no-headless` - Run browser in visible mode

## Security Considerations

### Session Data Protection

**Session stored in:** `.claude/skills/x-poster/assets/session/`

**Contains:**
- Browser cookies (authentication tokens)
- Local storage
- Session storage
- Cache

**NEVER commit to git:**
- All session data is gitignored
- Re-authentication required if session cleared
- No passwords stored in code

### Approval Workflow Security

**Benefits:**
- Human oversight prevents automated spam
- Review before posting prevents mistakes
- Audit trail in JSON logs
- 24-hour expiration prevents stale posts

**Risks Mitigated:**
- No unauthorized posting
- No accidental sensitive data sharing
- No posting during off-hours without approval
- Complete accountability

## Troubleshooting

### Tweets Not Appearing

1. Check login status: `python scripts/x_post.py --check-login`
2. Verify session not expired
3. Check for Twitter account issues (suspended, limited)
4. Review X/Twitter posting guidelines

### Authentication Issues

1. Clear session: `rm -rf .claude/skills/x-poster/assets/session/*`
2. Re-authenticate: `python scripts/x_post.py --authenticate --no-headless`
3. Complete 2FA manually if required
4. Check for IP-based restrictions

### Selector Failures

1. Run in visible mode: `--no-headless --dry-run`
2. Manually inspect Twitter UI
3. Update selectors in `x_post.py` (SELECTORS dict)
4. See `references/selectors_guide.md` for details

### Browser Crashes

1. Update Playwright: `pip install --upgrade playwright`
2. Reinstall browsers: `playwright install chromium`
3. Clear session and re-authenticate
4. Check system resources (RAM, disk space)

## Advanced Usage

### Headless vs Visible Mode

**Headless (default):**
- Runs in background
- Faster execution
- No browser window shown
- Use for production

**Visible (`--no-headless`):**
- Shows browser window
- Required for first-time auth
- Use for debugging
- See what's happening

### Dry Run Testing

Always test before creating approval:

```bash
# Test with visible browser
python scripts/x_post.py --message "Test tweet" --dry-run --no-headless

# Quick headless test
python scripts/x_post.py --message "Test tweet" --dry-run
```

### Manual Posting (No Approval)

**Not recommended**, but possible:

```bash
# Post directly without approval
python scripts/x_post.py --message "Emergency tweet" --headless

# WARNING: Bypasses approval workflow
```

## Future Enhancements

### Planned Features (Not Yet Implemented)

1. **Thread Support**
   - Automatically split long content into tweet threads
   - Number tweets (1/3, 2/3, 3/3)
   - Preview entire thread before approval

2. **Image Attachments**
   - Upload images with tweets
   - Image validation (size, format)
   - Alt text for accessibility

3. **Reply Handling**
   - Reply to mentions automatically
   - Thread replies
   - Quote tweets

4. **Analytics**
   - Track tweet performance
   - Engagement metrics (likes, retweets, replies)
   - Best performing tweets
   - Optimal posting time analysis

5. **Link Shortening**
   - Custom URL shortener integration
   - Click tracking
   - UTM parameter support

## References

- `references/twitter_setup.md` - Complete setup guide
- `references/best_practices.md` - X/Twitter posting best practices
- `references/selectors_guide.md` - Selector maintenance and updates

## Related Skills

- `approval-processor` - Processes approved tweets
- `scheduler-manager` - Schedule tweets in advance
- `dashboard-updater` - Track X/Twitter activity
- `linkedin-poster` - Similar posting for LinkedIn
- `social-media-manager` - Multi-platform posting

---

**Note:** This skill uses Playwright browser automation, not the X API. No API credentials or subscriptions required. Session persists indefinitely unless manually cleared or expired by Twitter.
