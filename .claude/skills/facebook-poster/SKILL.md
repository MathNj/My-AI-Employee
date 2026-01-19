---
name: facebook-poster
description: Automatically create and post to Facebook using Playwright browser automation. Supports text posts, image posts with text-to-image conversion, persistent authentication, approval workflow, and scheduled posting. No API costs - uses browser automation like WhatsApp watcher and X/Twitter poster.
---

# Facebook Poster

## Overview

This skill enables automated Facebook posting using Playwright browser automation. It bypasses the Facebook API by using browser automation, handles persistent authentication, integrates with the approval workflow system, and supports both text and image posts. The skill can automatically convert text messages into images for more engaging posts.

**Key Features:**
- Browser automation via Playwright (no API costs)
- Persistent session (login once, stay logged in)
- Text and image post support
- Automatic text-to-image conversion
- 63,206 character limit validation (Facebook's limit)
- Human-in-the-loop approval workflow
- Complete activity logging
- Headless and visible modes
- Integration with scheduler-manager
- Multiple image styles (gradient, solid, branded)

## Quick Start

### Basic Facebook Post

```bash
# Create text post with approval workflow
python scripts/facebook_post.py --text "Exciting announcement about our AI service!" --create-approval
```

This creates an approval request in `/Pending_Approval` for human review before posting.

### Post with Image

```bash
# Create post with image (text converted to image)
python scripts/facebook_post.py --message "AI Employee - 24/7 Automation" --text "Transform your business with AI automation!" --create-approval
```

### First-Time Setup

```bash
# Authenticate (run in visible mode first time)
python scripts/facebook_post.py --authenticate --no-headless

# Check login status
python scripts/facebook_post.py --check-login
```

## Core Workflows

### Workflow 1: Create and Post Text

1. **Generate post content** (manual or from template)
2. **Create approval request** with `--create-approval`
3. **Human reviews** post preview and character count
4. **Human approves** by moving file to `/Approved` folder
5. **Approval processor** detects approval and calls this skill
6. **Post to Facebook** via Playwright browser automation
7. **Log activity** to Dashboard and audit logs

### Workflow 2: Create and Post with Image

1. **Generate image message** (text for image)
2. **Generate caption text** (post caption)
3. **Create approval request** showing image preview
4. **Human approves** image post
5. **Script generates image** automatically (text-to-image)
6. **Post to Facebook** with image attached
7. **Log activity** and move to `/Done`

### Workflow 3: Scheduled Posts

1. **Create scheduled post** via scheduler-manager
2. **Scheduler triggers** at specified time
3. **Creates approval request** automatically
4. **Follows standard approval workflow**
5. **Posts automatically** after human approval

## Initial Setup

### Prerequisites

- **Python 3.9+** installed
- **Playwright** installed (already available from WhatsApp watcher)
- **Chromium browser** installed via Playwright
- **PIL (Pillow)** for image generation

### Verify Installation

```bash
# Check Playwright
python -c "import playwright; print('Playwright OK')"

# Check PIL
python -c "from PIL import Image; print('PIL OK')"

# Check Chromium
playwright show-browsers

# Expected output: chromium ... installed
```

If PIL is missing:
```bash
pip install Pillow
```

### First-Time Authentication

**Important:** Always run authentication in visible mode first time.

```bash
# Step 1: Authenticate with Facebook
python scripts/facebook_post.py --authenticate --no-headless
```

This will:
1. Open browser to Facebook login page
2. Wait for you to manually enter credentials
3. Complete 2FA if required
4. Detect successful login
5. Save session to `assets/session/` directory

**Session persists:** You only need to authenticate once. The session is saved and reused for all future posts.

### Test Login Status

```bash
# Verify you're logged in
python scripts/facebook_post.py --check-login
```

### Create First Post

```bash
# Dry run to test
python scripts/facebook_post.py --text "Hello World from my AI Employee!" --dry-run

# Create approval request
python scripts/facebook_post.py --text "Hello World from my AI Employee!" --create-approval
```

## Post Creation

### Method 1: Text-Only Post

```bash
# Create text post with approval
python scripts/facebook_post.py \
  --text "Just launched our new AI automation service! Learn more at example.com" \
  --create-approval

# Character count: 68/63206
```

### Method 2: Text with Image

```bash
# Create post with image
python scripts/facebook_post.py \
  --message "AI Employee
Transform Your Business
24/7 Automation" \
  --text "Check out our new AI automation service!" \
  --create-approval
```

**Image Generation:**
- Default size: 1200x630 (Facebook optimal)
- Font size: 50px
- Style: gradient background
- Output: Saved to `assets/images/` with timestamp

### Method 3: Via Claude Code

Simply ask Claude:
- "Post to Facebook about our new feature"
- "Create a Facebook post announcing this achievement"
- "Post this image and caption to Facebook"

Claude will automatically use this skill and create an approval request.

### Method 4: Scheduled Posts

```bash
# Schedule daily post at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "facebook-daily-post" \
  --command "python .claude/skills/facebook-poster/scripts/facebook_post.py --text 'Daily business update!' --create-approval" \
  --schedule "0 9 * * *"
```

## Approval Workflow Integration

### Creating Approval Requests

When using `--create-approval`, a file is created in `/Pending_Approval`:

**File:** `FACEBOOK_POST_2026-01-14T10-30-00.md`

```markdown
---
type: facebook_post
action: post_to_facebook
text: "Your post content here"
message: "Text for image (optional)"
image: "path/to/image.png"
created: 2026-01-14T10:30:00Z
expires: 2026-01-15T10:30:00Z
status: pending
---

# Facebook Post Approval Request

## Post Preview

Your post content here

**Character count:** 45/63206

## Image Preview (if applicable)

[Image will be generated on approval]

---

## Post Details

- **Type:** Facebook Post
- **Character Count:** 45/63206
- **Has Image:** Yes/No
- **Created:** 2026-01-14 10:30:00
- **Expires:** 2026-01-15 10:30:00

## Approval Instructions

**To Approve:** Move this file to `/Approved` folder
**To Reject:** Move this file to `/Rejected` folder

**Note:** This approval expires in 24 hours
```

### Processing Approved Posts

The `approval-processor` skill automatically detects approved Facebook posts and executes:

```bash
# Approval processor automatically calls:
python scripts/facebook_post.py --execute-approved /path/to/approved/file.md
```

**On Success:** File moved to `/Done` folder
**On Failure:** File moved to `/Failed` folder with error logged

## Character Limit Handling

Facebook has a generous **63,206 character limit** for posts (much higher than Twitter's 280).

### Validation

Character validation happens at **two points**:

1. **Approval Creation:** Warns if post is unusually long (>10,000 chars)
2. **Posting:** Ensures post is under the 63,206 limit

```bash
# This will succeed but warn
python scripts/facebook_post.py --text "$(python -c 'print("A" * 15000)')" --create-approval

# Output: ⚠️ Warning: Post is very long (15000 chars)
```

### Character Counting

- Regular characters: 1 char each
- Emojis: 1-2 chars (Unicode)
- Line breaks: 1 char (`\n`)
- URLs: Full length (Facebook doesn't auto-shorten)

## Image Generation

### Automatic Text-to-Image

When you use `--message`, the script automatically generates an image:

```bash
# Generate image with text
python scripts/facebook_post.py \
  --message "AI Employee
24/7 Automation" \
  --text "Transform your business!" \
  --create-approval
```

**Image Features:**
- **Default Size:** 1200x630 (Facebook optimal)
- **Background:** Gradient (configurable)
- **Font:** Auto-sized to fit text
- **Text Centering:** Automatic
- **Output:** PNG format

### Image Styles

Configure style in `facebook_post.py`:

```python
# Available styles
'gradient'  # Gradient background (default)
'solid'     # Solid color background
'branded'   # Your brand colors (configure)
```

### Custom Image Dimensions

```bash
# Square image
python scripts/facebook_post.py \
  --message "Test" \
  --image-width 1080 \
  --image-height 1080 \
  --create-approval
```

**Recommended Sizes:**
- Feed posts: 1200x630 (landscape)
- Square posts: 1080x1080
- Stories: 1080x1920 (portrait)

## Best Practices

### Posting Frequency

- **Optimal:** 3-5 posts per week
- **Minimum:** 2 posts per week
- **Maximum:** 2 posts per day (avoid spam)
- **Best times:** Tuesday-Thursday, 9 AM - 3 PM local time

### Content Guidelines

- **Length:** 40-250 characters (optimal engagement)
- **Images:** Use images for 80% of posts (higher engagement)
- **Hashtags:** 3-5 relevant hashtags (2 is ideal)
- **Call-to-action:** Include in 70% of posts
- **Links:** Always include when promoting content
- **Authenticity:** Personal voice > corporate speak
- **Engagement:** Ask questions to drive comments

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

**Rule:** Maximum 5 hashtags per post. 3 is optimal for engagement.

### Image Tips

- **Use text images** for announcements (higher engagement)
- **Keep image text short** (3-5 words max)
- **High contrast** text for readability
- **Brand consistency** in colors and fonts
- **Test on mobile** (most users view on mobile)

## Error Handling

### Common Issues

**Session Expired:**
```bash
# Re-authenticate
python scripts/facebook_post.py --authenticate --no-headless
```

**UI Selectors Changed:**
- Facebook frequently updates their UI
- Script uses multiple fallback selectors
- If all selectors fail, clear error message shown
- Update selectors in `facebook_post.py` (SELECTORS dict)

**Character Limit Exceeded:**
```bash
# Error before approval is created
❌ Invalid post: Post exceeds 63206 character limit
```

**Not Logged In:**
```bash
# Check login status
python scripts/facebook_post.py --check-login

# If not logged in, re-authenticate
python scripts/facebook_post.py --authenticate --no-headless
```

**Image Generation Failed:**
```bash
# Check PIL installation
python -c "from PIL import Image; print('PIL OK')"

# Reinstall if needed
pip install --upgrade Pillow
```

**Rate Limited:**
- Facebook may throttle if posting too frequently
- Wait 15-30 minutes before retrying
- Reduce posting frequency

### Logs

All activity logged to:
- `Logs/audit_YYYY-MM-DD.json` - All actions in standard format
- `Logs/facebook_activity_YYYY-MM-DD.json` - Facebook-specific logs
- `Dashboard.md` - Recent activity section

## Integration with Other Skills

### With approval-processor

Automatically posts after approval:
```python
# approval-processor detects approved Facebook posts (type: facebook_post)
# and calls this skill to execute via Playwright
```

### With scheduler-manager

Schedule posts in advance:
```bash
# Schedule weekly update every Monday at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "facebook-weekly-update" \
  --command "python .claude/skills/facebook-poster/scripts/facebook_post.py --text 'Weekly update post' --create-approval" \
  --schedule "0 9 * * 1"
```

### With dashboard-updater

Track Facebook activity:
- Posts created
- Posts approved/rejected
- Image posts vs text posts
- Posting frequency
- Success/failure rates

## Scripts Reference

### facebook_post.py

Main posting script with Playwright automation.

**Usage:**
```bash
# Authenticate
python scripts/facebook_post.py --authenticate --no-headless

# Check login status
python scripts/facebook_post.py --check-login

# Create text post with approval
python scripts/facebook_post.py --text "Content" --create-approval

# Create image post with approval
python scripts/facebook_post.py --message "Image text" --text "Caption" --create-approval

# Execute approved post
python scripts/facebook_post.py --execute-approved /path/to/file.md

# Test mode (dry run)
python scripts/facebook_post.py --text "Test" --dry-run

# Visible mode (for debugging)
python scripts/facebook_post.py --text "Debug" --dry-run --no-headless
```

**Arguments:**
- `--authenticate` - Interactive login flow
- `--check-login` - Verify login status
- `--text "content"` - Post text content
- `--message "text"` - Text for image generation
- `--create-approval` - Create approval request
- `--execute-approved path` - Post approved content
- `--dry-run` - Preview without posting
- `--no-headless` - Run browser in visible mode
- `--image-width W` - Custom image width
- `--image-height H` - Custom image height
- `--image-style STYLE` - Image style (gradient/solid/branded)

## Security Considerations

### Session Data Protection

**Session stored in:** `.claude/skills/facebook-poster/assets/session/`

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

### Posts Not Appearing

1. Check login status: `python scripts/facebook_post.py --check-login`
2. Verify session not expired
3. Check for Facebook account issues (suspended, limited)
4. Review Facebook posting guidelines
5. Check if posting to correct page/profile

### Authentication Issues

1. Clear session: `rm -rf .claude/skills/facebook-poster/assets/session/*`
2. Re-authenticate: `python scripts/facebook_post.py --authenticate --no-headless`
3. Complete 2FA manually if required
4. Check for IP-based restrictions
5. Verify Facebook account is in good standing

### Selector Failures

1. Run in visible mode: `--no-headless --dry-run`
2. Manually inspect Facebook UI
3. Update selectors in `facebook_post.py` (SELECTORS dict)
4. Report persistent issues for selector updates

### Image Generation Issues

1. Verify PIL installation: `pip list | grep Pillow`
2. Check disk space in `assets/images/`
3. Verify write permissions
4. Test image generation: `python -c "from PIL import Image; Image.new('RGB', (100,100)).save('test.png')"`

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
python scripts/facebook_post.py --text "Test post" --dry-run --no-headless

# Quick headless test
python scripts/facebook_post.py --text "Test post" --dry-run
```

### Custom Image Generation

Create branded images:

```python
# In facebook_post.py, customize:
DEFAULT_IMAGE_STYLE = 'branded'
BRAND_COLORS = {
    'primary': '#3B82F6',
    'secondary': '#10B981',
    'text': '#FFFFFF'
}
```

### Manual Posting (No Approval)

**Not recommended**, but possible:

```bash
# Post directly without approval
python scripts/facebook_post.py --text "Emergency post" --headless

# WARNING: Bypasses approval workflow
```

## Future Enhancements

### Planned Features (Not Yet Implemented)

1. **Video Support**
   - Upload videos with posts
   - Video validation (size, format, duration)
   - Thumbnail generation

2. **Multiple Images**
   - Upload up to 10 photos per post
   - Image carousel format
   - Individual image captions

3. **Page Management**
   - Post to multiple pages
   - Page switching automation
   - Analytics per page

4. **Analytics**
   - Track post performance
   - Engagement metrics (likes, comments, shares)
   - Best performing posts
   - Optimal posting time analysis

5. **Comment Handling**
   - Reply to comments automatically
   - Engage with followers
   - sentiment analysis

## References

## Related Skills

- `approval-processor` - Processes approved Facebook posts
- `scheduler-manager` - Schedule Facebook posts in advance
- `dashboard-updater` - Track Facebook activity
- `linkedin-poster` - Similar posting for LinkedIn
- `x-poster` - Similar posting for X/Twitter
- `instagram-poster` - Similar posting for Instagram
- `social-media-manager` - Multi-platform posting

---

**Note:** This skill uses Playwright browser automation, not the Facebook API. No API credentials or subscriptions required. Session persists indefinitely unless manually cleared or expired by Facebook. Facebook's 63,206 character limit is much higher than Twitter's 280, allowing for more detailed posts and storytelling.
