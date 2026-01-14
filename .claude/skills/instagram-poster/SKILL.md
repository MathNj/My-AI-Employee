# Instagram Poster Skill

**Automatically create text-to-image posts and publish to Instagram via Playwright browser automation**

## Overview

The Instagram Poster skill converts text messages into beautiful images and posts them to Instagram using browser automation. This skill is ideal for:

- Posting quote graphics and text-based content
- Sharing business updates with visual appeal
- Creating consistent branded social media presence
- Avoiding Instagram API costs (no API required)

**Key Features:**
- Text-to-image conversion with multiple styles
- Persistent browser sessions (login once, stay logged in)
- Human approval workflow integration
- Caption support (up to 2,200 characters)
- Headless and visible mode support
- Comprehensive activity logging

## Quick Start

### 1. First-Time Authentication

```bash
# Authenticate with Instagram (opens visible browser)
python .claude/skills/instagram-poster/scripts/instagram_post.py --authenticate --no-headless
```

**Manual steps:**
1. Enter your Instagram username/email
2. Enter your password
3. Complete any 2FA or security checks
4. Wait for home feed to load
5. Session will be saved automatically

### 2. Verify Login

```bash
# Check if you're still logged in
python .claude/skills/instagram-poster/scripts/instagram_post.py --check-login
```

### 3. Create Your First Post

```bash
# Create an approval request
python .claude/skills/instagram-poster/scripts/instagram_post.py \
  --message "My AI Employee is working!" \
  --caption "Excited to share that my automated business assistant is now live!" \
  --create-approval
```

This will:
- Generate an image with your text
- Create an approval request in `/Pending_Approval`
- Wait for you to approve by moving the file to `/Approved`

### 4. Approve and Post

1. Check the generated image in `.claude/skills/instagram-poster/assets/images/`
2. Move the approval file from `/Pending_Approval` to `/Approved`
3. Run the approval processor:

```bash
python .claude/skills/approval-processor/scripts/process_approvals.py
```

The post will be published automatically!

## Core Workflows

### Workflow 1: Standard Approval Workflow (Recommended)

```
Create Approval → Human Review → Approve → Auto-Post
```

**Step-by-step:**

1. **Create approval request:**
```bash
python instagram_post.py --message "Your text here" --create-approval
```

2. **Review generated image:**
- Check `.claude/skills/instagram-poster/assets/images/instagram_YYYYMMDD_HHMMSS.png`
- Review the approval file in `/Pending_Approval`

3. **Approve:**
- Move file from `/Pending_Approval` to `/Approved`

4. **Auto-execute:**
- Approval processor detects approved file
- Posts to Instagram automatically
- Moves file to `/Done` on success or `/Failed` on error

### Workflow 2: Direct Posting (No Approval)

```bash
# Post directly without approval (headless)
python instagram_post.py --message "Quick update" --caption "Short caption"

# Post in visible mode to watch it work
python instagram_post.py --message "Test post" --no-headless
```

### Workflow 3: Dry Run Testing

```bash
# Generate image but don't post
python instagram_post.py --message "Test text" --dry-run

# Test with custom image style
python instagram_post.py --message "Test" --image-style solid --font-size 60 --dry-run
```

## Image Generation

### Image Styles

The skill supports three image styles:

#### 1. Gradient (Default)
Blue to purple gradient background - professional and eye-catching.

```bash
--image-style gradient
```

#### 2. Solid
Clean solid color background - minimalist and professional.

```bash
--image-style solid
```

#### 3. Pattern
Geometric pattern background - modern and distinctive.

```bash
--image-style pattern
```

### Custom Image Settings

```bash
# Large font for short text
python instagram_post.py --message "Big Text" --font-size 80 --create-approval

# Custom dimensions (square by default)
python instagram_post.py --message "Text" \
  --image-width 1080 \
  --image-height 1080 \
  --create-approval

# Combine options
python instagram_post.py --message "Custom Post" \
  --caption "Professional look" \
  --image-style solid \
  --font-size 50 \
  --create-approval
```

### Font Size Guidelines

- **30-40**: Small text, long messages
- **50** (default): Medium text, balanced
- **60-80**: Large text, short impactful messages
- **100+**: Extra large, 1-3 words only

## Caption Best Practices

Instagram captions support up to 2,200 characters. Use captions to:

- Provide context for the image text
- Add hashtags for discoverability
- Include calls to action
- Link to other content (link in bio)

**Example:**

```bash
python instagram_post.py \
  --message "Innovation drives success" \
  --caption "Sharing insights from our journey building an AI-powered business assistant.

What's your biggest business automation win?

#AIEmployee #BusinessAutomation #Productivity #Entrepreneurship #Innovation" \
  --create-approval
```

**Hashtag Tips:**
- Use 10-15 relevant hashtags
- Mix popular (#Productivity) and niche (#AIEmployee) tags
- Place hashtags at the end for cleaner appearance
- Research trending hashtags in your industry

## Script Reference

### Authentication Commands

```bash
# First-time login (interactive, visible browser)
python instagram_post.py --authenticate --no-headless

# Check if logged in
python instagram_post.py --check-login
```

### Posting Commands

```bash
# Create approval request
python instagram_post.py --message "Text" --create-approval

# Create with caption
python instagram_post.py --message "Text" --caption "Caption here" --create-approval

# Execute approved post
python instagram_post.py --execute-approved /path/to/INSTAGRAM_POST_timestamp.md

# Direct post (no approval)
python instagram_post.py --message "Text" --caption "Caption"

# Dry run (test without posting)
python instagram_post.py --message "Text" --dry-run
```

### Image Customization

```bash
# Custom style
python instagram_post.py --message "Text" --image-style gradient --create-approval

# Custom font size
python instagram_post.py --message "Text" --font-size 60 --create-approval

# Custom dimensions
python instagram_post.py --message "Text" --image-width 1080 --image-height 1350 --create-approval
```

### Debugging Commands

```bash
# Run in visible mode (watch browser actions)
python instagram_post.py --message "Test" --no-headless

# Dry run with visible browser
python instagram_post.py --message "Test" --dry-run --no-headless
```

## Approval Integration

### Approval File Format

When you create an approval request, it generates a file like `INSTAGRAM_POST_20260114_120000.md`:

```yaml
---
type: instagram_post
action: post_to_instagram
message: "Your text here"
image_path: ".claude/skills/instagram-poster/assets/images/instagram_20260114_120000.png"
caption: "Your caption here"
image_style: "gradient"
font_size: 50
created: 2026-01-14T12:00:00
expires: 2026-01-21T12:00:00
status: pending
---

# Instagram Post Approval Request

## Image Preview
![Generated Image](.claude/skills/instagram-poster/assets/images/instagram_20260114_120000.png)

## Message on Image
Your text here

## Caption
Your caption here

## Image Details
- **Style**: gradient
- **Font Size**: 50
- **Dimensions**: 1080x1080
- **Caption Length**: 18/2200 characters
```

### Approval Workflow Integration

The Instagram poster integrates with the approval processor:

1. **Create approval**: `instagram_post.py --create-approval`
2. **File goes to**: `/Pending_Approval`
3. **Human reviews**: Check image and caption
4. **Human approves**: Move file to `/Approved`
5. **Auto-execute**: `process_approvals.py` detects and posts
6. **Result**: File moves to `/Done` or `/Failed`

### Executor Configuration

The approval processor knows how to execute Instagram posts via this configuration:

```python
'instagram_post': {
    'script': VAULT_PATH / '.claude' / 'skills' / 'instagram-poster' / 'scripts' / 'instagram_post.py',
    'arg': '--execute-approved'
}
```

## Scheduled Posting

Use the scheduler-manager to automate regular posts.

### Example: Daily Motivation Post

```bash
# Schedule daily post at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "instagram-daily-motivation" \
  --command "python .claude/skills/instagram-poster/scripts/instagram_post.py --message 'Daily motivation' --caption 'Your caption' --create-approval" \
  --schedule "0 9 * * *"
```

### Example: Weekly Business Update

```bash
# Schedule weekly update on Monday at 10 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "instagram-weekly-update" \
  --command "python .claude/skills/instagram-poster/scripts/instagram_post.py --message 'Weekly business update' --create-approval" \
  --schedule "0 10 * * 1"
```

## Activity Logging

All Instagram activity is logged to:
```
AI_Employee_Vault/Logs/instagram_activity_YYYYMMDD.json
```

**Log entries include:**
- Timestamp
- Action (post_executed, post_failed, etc.)
- Image path and caption
- Success/failure status
- Error details if failed

**View logs:**
```bash
# View today's activity
cat AI_Employee_Vault/Logs/instagram_activity_20260114.json

# Pretty print
python -m json.tool AI_Employee_Vault/Logs/instagram_activity_20260114.json
```

## Error Handling

### Common Issues

#### 1. "Not logged in"
**Problem**: Session expired or authentication failed
**Solution**:
```bash
python instagram_post.py --authenticate --no-headless
```

#### 2. "Could not find 'New post' button"
**Problem**: Instagram UI changed, selectors need updating
**Solution**:
- Run in visible mode to inspect: `--no-headless`
- Report issue with screenshot
- Manually check if Instagram interface loaded correctly

#### 3. "File input not found"
**Problem**: Upload dialog didn't appear or changed
**Solution**:
- Try visible mode to see what's happening
- Check if Instagram is asking for mobile app download
- Clear browser session and re-authenticate

#### 4. "Caption too long"
**Problem**: Caption exceeds 2,200 characters
**Solution**:
- Shorten caption
- Remove unnecessary hashtags
- Split into multiple posts

#### 5. "Pillow not installed"
**Problem**: Image generation library missing
**Solution**:
```bash
pip install Pillow
```

### Debug Mode

Run in visible mode to watch the automation:

```bash
python instagram_post.py --message "Debug test" --no-headless --dry-run
```

This will:
- Open visible browser window
- Show each automation step
- Not actually post (dry run)
- Help identify where issues occur

## Security Considerations

### Session Data

- **Never commit**: `.claude/skills/instagram-poster/assets/session/*`
- **Already gitignored**: Session folder is excluded from version control
- **Local only**: Browser session stays on your machine
- **Persistent**: Login once, stay logged in indefinitely

### Approval Workflow

- **Human oversight**: All posts require approval (recommended)
- **Review before posting**: Check image and caption before approving
- **Audit trail**: Complete logging in activity files
- **Expiration**: Approval requests expire after 7 days

### Rate Limiting

Instagram may flag rapid posting as spam:
- **Recommended**: 3-5 posts per day maximum
- **Spacing**: Wait 1-2 hours between posts
- **Natural behavior**: Mix posting times, don't post at exact intervals
- **Approval workflow helps**: Forces human review, naturally spaces posts

## Dependencies

The Instagram poster requires:

### Python Packages

```bash
# Install required packages
pip install playwright Pillow

# Install Playwright browsers
playwright install chromium
```

### System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **Disk space**: ~200MB for Chromium browser
- **Internet**: Required for posting

### Verify Installation

```bash
# Check Python packages
python -c "import playwright; print('Playwright OK')"
python -c "from PIL import Image; print('Pillow OK')"

# Check Playwright browsers
playwright show-browsers
```

## Integration with Other Skills

### With Social Media Manager

The Instagram poster integrates with the social-media-manager skill for unified posting:

```bash
# Post to Instagram via social media manager
python .claude/skills/social-media-manager/scripts/post_manager.py \
  --platform instagram \
  --message "Text for image" \
  --caption "Instagram caption"
```

### With Approval Processor

Automatically executed by the approval processor:

```bash
# Process all approved posts (Instagram + LinkedIn + X)
python .claude/skills/approval-processor/scripts/process_approvals.py
```

### With Scheduler Manager

Schedule regular Instagram posts:

```bash
# Daily post at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "instagram-daily" \
  --command "python instagram_post.py --message 'Text' --create-approval" \
  --schedule "0 9 * * *"
```

## Best Practices

### Content Strategy

1. **Consistency**: Post regularly (3-5 times per week)
2. **Quality over quantity**: Better fewer high-quality posts
3. **Visual variety**: Rotate image styles (gradient, solid, pattern)
4. **Caption engagement**: Ask questions, use CTAs
5. **Hashtag research**: Use relevant, trending hashtags

### Technical Best Practices

1. **Always use approval workflow**: Prevents mistakes
2. **Test with dry runs**: Verify before posting
3. **Monitor activity logs**: Track success/failures
4. **Keep session active**: Check login weekly
5. **Visible mode for debugging**: Easier troubleshooting

### Image Design Tips

1. **Short text works best**: 5-15 words ideal
2. **Font size matters**: Larger for shorter text
3. **Gradient for quotes**: Professional look
4. **Solid for announcements**: Clean and clear
5. **Pattern for variety**: Stand out in feed

## Troubleshooting

### Session Issues

```bash
# Session expired
python instagram_post.py --authenticate --no-headless

# Session corrupted
rm -rf .claude/skills/instagram-poster/assets/session/*
python instagram_post.py --authenticate --no-headless

# Check session status
python instagram_post.py --check-login
```

### Image Generation Issues

```bash
# Pillow not installed
pip install Pillow

# Font not found (uses default font automatically)
# No action needed, default font works

# Image too large
python instagram_post.py --message "Text" --image-width 1080 --image-height 1080
```

### Posting Issues

```bash
# Not logged in
python instagram_post.py --authenticate --no-headless

# Selectors not working (Instagram UI changed)
# Run in visible mode to debug
python instagram_post.py --message "Test" --no-headless --dry-run

# Upload failed
# Try visible mode, check internet connection
```

## Examples

### Example 1: Simple Announcement

```bash
python instagram_post.py \
  --message "We're Hiring!" \
  --caption "Join our growing team. Link in bio. #Hiring #JobOpening" \
  --image-style solid \
  --font-size 70 \
  --create-approval
```

### Example 2: Inspirational Quote

```bash
python instagram_post.py \
  --message "Innovation distinguishes between a leader and a follower." \
  --caption "Words to live by. - Steve Jobs

#Innovation #Leadership #Inspiration #Motivation" \
  --image-style gradient \
  --font-size 45 \
  --create-approval
```

### Example 3: Business Update

```bash
python instagram_post.py \
  --message "Milestone: 1000 customers served!" \
  --caption "Grateful for every customer who trusted us on this journey. Here's to the next 1000!

#Milestone #Business #Grateful #CustomerFirst" \
  --image-style pattern \
  --font-size 55 \
  --create-approval
```

### Example 4: Quick Update (No Approval)

```bash
python instagram_post.py \
  --message "Office closed today" \
  --caption "Back tomorrow at 9 AM" \
  --font-size 60
```

## Files and Directories

```
.claude/skills/instagram-poster/
├── SKILL.md                          # This documentation
├── scripts/
│   └── instagram_post.py             # Main automation script
├── assets/
│   ├── session/                      # Persistent browser session (gitignored)
│   │   └── .gitkeep
│   └── images/                       # Generated images
│       └── instagram_YYYYMMDD_HHMMSS.png
└── references/                       # (Optional) Additional docs

AI_Employee_Vault/
├── Pending_Approval/                 # Approval requests
│   └── INSTAGRAM_POST_*.md
├── Approved/                         # Approved posts (auto-executed)
├── Done/                             # Successfully posted
├── Failed/                           # Failed posts
└── Logs/
    └── instagram_activity_YYYYMMDD.json  # Activity logs
```

## Version History

- **v1.0.0** (2026-01-14): Initial release
  - Text-to-image conversion (3 styles)
  - Playwright browser automation
  - Persistent session support
  - Approval workflow integration
  - Caption support (2,200 chars)
  - Activity logging

## Support

For issues, questions, or feature requests:

1. Check the troubleshooting section above
2. Review activity logs for error details
3. Run in visible mode (`--no-headless`) to debug
4. Check if Instagram UI has changed (selector updates needed)

## Related Skills

- **x-poster**: Post to X/Twitter (text only)
- **linkedin-poster**: Post to LinkedIn (text only)
- **social-media-manager**: Unified posting across platforms
- **approval-processor**: Automated approval workflow execution
- **scheduler-manager**: Schedule recurring posts
