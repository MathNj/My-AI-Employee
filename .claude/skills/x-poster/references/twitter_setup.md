# X/Twitter Setup Guide

Complete step-by-step guide for setting up the X/Twitter poster skill.

## Prerequisites

### 1. Python Environment

Check Python version:
```bash
python --version
# Required: Python 3.9 or higher
```

### 2. Playwright Installation

Playwright is already installed (from WhatsApp watcher). Verify:
```bash
python -c "import playwright; print('✓ Playwright installed')"
```

If not installed:
```bash
pip install playwright
playwright install chromium
```

### 3. Check Browser

Verify Chromium browser is installed:
```bash
playwright show-browsers
# Expected output: chromium ... installed
```

## Initial Setup

### Step 1: Verify Directory Structure

The x-poster skill should have this structure:
```
.claude/skills/x-poster/
├── SKILL.md
├── scripts/
│   └── x_post.py
├── references/
│   ├── twitter_setup.md (this file)
│   ├── best_practices.md
│   └── selectors_guide.md
└── assets/
    └── session/
        └── .gitkeep
```

### Step 2: Test Script Accessibility

```bash
# Navigate to skill directory
cd ".claude/skills/x-poster/scripts"

# Test script help
python x_post.py --help

# Expected: Help message showing all available options
```

### Step 3: First-Time Authentication

**IMPORTANT:** Always run authentication in **visible mode** for first-time setup.

```bash
# Run authentication
python x_post.py --authenticate --no-headless
```

**What happens:**
1. ✓ Browser window opens automatically
2. ✓ Navigates to Twitter login page
3. ⏳ **You manually enter your credentials**
4. ⏳ **Complete 2FA if prompted**
5. ⏳ **Wait for home feed to load**
6. ✓ Script detects successful login
7. ✓ Session saved to `assets/session/` directory

**Authentication Flow:**

```
┌─────────────────────────────────────────────┐
│  Browser Opens → Twitter Login Page         │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Enter Username/Email/Phone                 │
│  Click "Next"                               │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Enter Password                             │
│  Click "Log in"                             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Complete 2FA (if enabled)                  │
│  - SMS code, or                             │
│  - Authenticator app code                   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Home Feed Loads                            │
│  ✓ Script Detects Login Success            │
│  ✓ Session Saved                           │
└─────────────────────────────────────────────┘
```

**Troubleshooting Authentication:**

| Issue | Solution |
|-------|----------|
| Browser doesn't open | Check Chromium installation: `playwright install chromium` |
| Stuck on login page | Manually complete all prompts, wait up to 5 minutes |
| 2FA timeout | Complete 2FA quickly, re-run if timeout occurs |
| Session not saved | Check write permissions on `assets/session/` directory |

### Step 4: Verify Login Status

After authentication, verify you're logged in:

```bash
# Check login (headless mode)
python x_post.py --check-login

# Expected output:
# 🔍 Checking login status...
# ✓ User is logged in
```

**If login check fails:**
```bash
# Re-authenticate
python x_post.py --authenticate --no-headless
```

### Step 5: Test with Dry Run

Test posting functionality without actually posting:

```bash
# Dry run test
python x_post.py --message "Hello World! Testing my AI Employee." --dry-run

# Expected output:
# 🧪 DRY RUN - Tweet preview:
# ────────────────────────────────────────────────────────────
# Hello World! Testing my AI Employee.
# ────────────────────────────────────────────────────────────
# Character count: 36/280
```

### Step 6: Create First Approval

Create your first tweet approval request:

```bash
# Create approval
python x_post.py --message "Excited to announce my AI Employee is now posting to X/Twitter!" --create-approval

# Expected output:
# ✅ Approval request created: X_POST_2026-01-14T10-30-00.md
#    Location: C:\Users\...\AI_Employee_Vault\Pending_Approval\X_POST_...md
#    Expires: 2026-01-15 10:30:00
```

### Step 7: Approve and Post

**Manual approval:**
1. Open `AI_Employee_Vault/Pending_Approval/` folder
2. Find the `X_POST_*.md` file
3. Review the tweet content
4. Move file to `AI_Employee_Vault/Approved/` folder

**Automatic execution (via approval-processor):**

If approval-processor is running as a watcher:
- It automatically detects the approved file
- Executes the tweet
- Moves file to `/Done` on success

**Manual execution:**
```bash
# Execute approved post manually
python x_post.py --execute-approved "C:\Users\...\AI_Employee_Vault\Approved\X_POST_*.md"
```

### Step 8: Verify Success

Check that tweet was posted:
1. ✓ Open X/Twitter in browser
2. ✓ Check your profile timeline
3. ✓ Verify tweet is visible

Check logs:
```bash
# View today's activity log
cat "AI_Employee_Vault/Logs/x_activity_2026-01-14.json"
```

## Session Management

### Session Persistence

**Location:** `.claude/skills/x-poster/assets/session/`

**Contains:**
- Browser cookies (auth tokens)
- Local storage
- Session storage
- Cache

**Duration:**
- Typical: 30-90 days
- Depends on X/Twitter policies
- Can expire if logged out on web

### Session Expiration

**Symptoms:**
- Login check fails
- "Not logged in" error when posting
- Browser redirects to login page

**Solution:**
```bash
# Re-authenticate
python x_post.py --authenticate --no-headless
```

### Clear Session

To start fresh or troubleshoot:

**Windows:**
```cmd
rmdir /s /q ".claude\skills\x-poster\assets\session"
mkdir ".claude\skills\x-poster\assets\session"
```

**Linux/Mac:**
```bash
rm -rf .claude/skills/x-poster/assets/session/*
```

Then re-authenticate:
```bash
python x_post.py --authenticate --no-headless
```

## Integration Setup

### With Approval-Processor

The approval-processor should already be configured (added during installation).

**Verify integration:**
```bash
# Check approval-processor configuration
grep -A 3 "x_post" .claude/skills/approval-processor/scripts/process_approvals.py

# Expected output:
# 'x_post': {
#     'script': VAULT_PATH / '.claude' / 'skills' / 'x-poster' / 'scripts' / 'x_post.py',
#     'arg': '--execute-approved'
# }
```

### With Scheduler-Manager

Schedule tweets in advance:

```bash
# Daily tweet at 9 AM
python .claude/skills/scheduler-manager/scripts/create_schedule.py \
  --name "x-daily-update" \
  --command "python C:\Users\...\Desktop\My Vault\.claude\skills\x-poster\scripts\x_post.py --message 'Daily update!' --create-approval" \
  --schedule "0 9 * * *"
```

**Cron schedule format:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └── Day of week (0-7, 0=Sunday)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

**Examples:**
- `0 9 * * *` - Daily at 9:00 AM
- `0 9 * * 1` - Every Monday at 9:00 AM
- `0 9,14 * * *` - Daily at 9:00 AM and 2:00 PM
- `*/30 * * * *` - Every 30 minutes

## Testing Checklist

Before production use, verify all functionality:

- [ ] Playwright installed
- [ ] Chromium browser installed
- [ ] Script runs without errors
- [ ] Authentication successful
- [ ] Login check returns success
- [ ] Dry run works
- [ ] Approval file created correctly
- [ ] Character validation works (test >280 chars)
- [ ] Approved post executes successfully
- [ ] Tweet appears on X/Twitter
- [ ] Logs created correctly
- [ ] File moved to /Done folder
- [ ] Approval-processor integration works
- [ ] Scheduler integration works (if using)

## Security Checklist

- [ ] Session directory gitignored
- [ ] No credentials in code
- [ ] Approval workflow enabled
- [ ] Session files have proper permissions
- [ ] Logs don't contain sensitive data
- [ ] 2FA enabled on X/Twitter account (recommended)

## Maintenance

### Weekly Tasks

1. Check login status: `python x_post.py --check-login`
2. Review activity logs
3. Clear old logs (>30 days)

### Monthly Tasks

1. Update Playwright: `pip install --upgrade playwright`
2. Reinstall browsers: `playwright install chromium`
3. Review and update selectors if Twitter UI changed
4. Check approval workflow folder sizes

### When Twitter UI Changes

If selectors stop working:
1. Run in visible mode: `--no-headless --dry-run`
2. Inspect elements in browser
3. Update SELECTORS dict in `x_post.py`
4. See `selectors_guide.md` for details
5. Test thoroughly before production

## Troubleshooting

### Common Errors

**"playwright module not found"**
```bash
pip install playwright
playwright install chromium
```

**"Session expired"**
```bash
python x_post.py --authenticate --no-headless
```

**"Could not find compose button"**
- Twitter UI may have changed
- Update selectors (see `selectors_guide.md`)
- Or run in visible mode to debug

**"Character limit exceeded"**
- Tweet is >280 characters
- Shorten message or split into thread (future feature)

**"Approval file not found"**
- Check file path is correct
- Verify file exists in /Approved folder
- Check file permissions

## Support

For issues:
1. Check logs in `AI_Employee_Vault/Logs/`
2. Review this guide and troubleshooting section
3. See `SKILL.md` for detailed usage
4. Check `selectors_guide.md` for UI changes
5. Test in visible mode (`--no-headless`) to debug

## Next Steps

After successful setup:
1. Read `best_practices.md` for posting guidelines
2. Set up scheduled tweets via scheduler-manager
3. Configure approval-processor for automatic execution
4. Customize tweet templates for your business
5. Monitor logs and adjust posting frequency

---

**Setup Complete!** You're ready to start posting to X/Twitter via your AI Employee.
