# Playwright Selector Maintenance Guide

## Overview

Twitter/X frequently updates their user interface, which can break Playwright selectors. This guide explains the selector strategy, how to diagnose failures, and how to update selectors when Twitter's UI changes.

## Understanding Selectors

### What Are Selectors?

Selectors are patterns that identify specific elements on a web page. They tell Playwright which button to click, which textbox to type in, etc.

**Example:**
```python
'a[data-testid="SideNav_NewTweet_Button"]'
```

This selector finds the "Compose Tweet" button by its `data-testid` attribute.

### Selector Types

**1. Data Attributes (Most Reliable)**
```python
'button[data-testid="tweetButton"]'
```
- Twitter uses `data-testid` for testing
- Most stable across UI updates
- **Use as primary selector**

**2. ARIA Attributes (Moderate Reliability)**
```python
'button[aria-label="Tweet"]'
```
- Accessibility attributes
- More stable than classes
- Good fallback option

**3. Text-Based (Flexible)**
```python
'button:has-text("Post")'
```
- Finds elements by visible text
- Can break with localization
- Good for unique text

**4. CSS Classes (Least Reliable)**
```python
'button.css-18t94o4'
```
- Twitter uses auto-generated classes
- Changes frequently
- **Avoid unless necessary**

## Current Selector Strategy

### Multi-Selector Fallback

The x_post.py script uses **multiple fallback selectors** for each UI element:

```python
SELECTORS = {
    'compose_tweet': [
        'a[data-testid="SideNav_NewTweet_Button"]',  # Primary
        'a[href="/compose/tweet"]',                   # Secondary
        'a[aria-label="Tweet"]'                       # Tertiary
    ]
}
```

**How it works:**
1. Try primary selector (most specific)
2. If timeout, try secondary
3. If timeout, try tertiary
4. If all fail, return error

### Current Selector Mapping

**Login Flow:**
```python
'login': {
    'username_input': [
        'input[autocomplete="username"]',      # Most reliable
        'input[name="text"]',                  # Fallback 1
        'input[type="text"]'                   # Fallback 2
    ],
    'password_input': [
        'input[autocomplete="current-password"]',
        'input[name="password"]',
        'input[type="password"]'
    ]
}
```

**Logged-In State:**
```python
'logged_in': {
    'compose_tweet': [
        'a[data-testid="SideNav_NewTweet_Button"]',
        'a[href="/compose/tweet"]',
        'a[aria-label="Tweet"]',
        'div[data-testid="SideNav_NewTweet_Button"]'
    ]
}
```

**Tweet Composition:**
```python
'compose': {
    'tweet_textbox': [
        'div[data-testid="tweetTextarea_0"]',
        'div[role="textbox"][data-testid*="tweet"]',
        'div[role="textbox"][contenteditable="true"]'
    ],
    'tweet_button': [
        'button[data-testid="tweetButtonInline"]',
        'button[data-testid="tweetButton"]',
        'div[data-testid="tweetButton"]'
    ]
}
```

## Diagnosing Selector Failures

### Symptoms

**Common errors indicating selector failure:**
```
Could not find compose tweet button. UI may have changed.
Could not find tweet textbox. UI may have changed.
Could not find post button. UI may have changed.
```

### Step 1: Run in Visible Mode

Always debug in visible mode to see what's happening:

```bash
python x_post.py --message "Test" --dry-run --no-headless
```

**What to observe:**
- Does browser navigate to correct page?
- Is the element visible on screen?
- Does element appear after waiting?
- Is there an overlay blocking the element?

### Step 2: Use Browser DevTools

**Manual inspection:**
1. Open visible browser during script execution
2. Pause script (add `time.sleep(60)` in code temporarily)
3. Right-click element → Inspect
4. Look at element attributes in DevTools

**Example inspection:**
```html
<button
  data-testid="tweetButtonInline"
  aria-label="Post"
  role="button"
  class="css-18t94o4">
  <span>Post</span>
</button>
```

**Good selectors from this:**
- `button[data-testid="tweetButtonInline"]` (best)
- `button[aria-label="Post"]` (good fallback)
- `button:has-text("Post")` (OK fallback)

### Step 3: Check Selector in Playwright Inspector

Use Playwright's built-in inspector:

```bash
# Add this to x_post.py temporarily
page.pause()  # Opens Playwright Inspector
```

Then test selectors in the inspector:
- Type selector in inspector
- See if element highlights
- Try variations until you find working selector

## Updating Selectors

### When Twitter UI Changes

**Process:**
1. Identify failed selector
2. Inspect element in visible browser
3. Find new attribute or pattern
4. Update SELECTORS dict in x_post.py
5. Test thoroughly
6. Document change

### Example Update

**Scenario:** Compose button selector stopped working.

**Step 1: Diagnose**
```bash
# Run in visible mode
python x_post.py --check-login --no-headless

# Error: "Could not find compose tweet button"
```

**Step 2: Inspect Element**

Open DevTools, find compose button:
```html
<!-- OLD (stopped working) -->
<a data-testid="SideNav_NewTweet_Button">

<!-- NEW (Twitter changed it) -->
<a data-testid="SideNav_NewPost_Button">
```

**Step 3: Update x_post.py**

Find the SELECTORS dict (around line 51):

```python
# BEFORE
'compose_tweet': [
    'a[data-testid="SideNav_NewTweet_Button"]',
    'a[href="/compose/tweet"]',
    'a[aria-label="Tweet"]'
],

# AFTER
'compose_tweet': [
    'a[data-testid="SideNav_NewPost_Button"]',      # NEW primary
    'a[data-testid="SideNav_NewTweet_Button"]',     # OLD fallback
    'a[href="/compose/tweet"]',                     # Secondary fallback
    'a[aria-label="Post"]'                          # Updated text
],
```

**Step 4: Test**

```bash
# Test login check
python x_post.py --check-login

# Test dry run
python x_post.py --message "Test" --dry-run --no-headless

# Test approval creation
python x_post.py --message "Test" --create-approval
```

### Comprehensive Selector Update Example

**Full process for tweet button update:**

```python
# File: .claude/skills/x-poster/scripts/x_post.py
# Lines: 80-95 (approximate)

# Find this section:
SELECTORS = {
    # ... other selectors ...

    'compose': {
        'tweet_textbox': [
            'div[data-testid="tweetTextarea_0"]',
            'div[role="textbox"][data-testid*="tweet"]',
            'div[role="textbox"][contenteditable="true"]'
        ],
        'tweet_button': [
            # UPDATE THESE LINES:
            'button[data-testid="tweetButtonInline"]',  # Check if still valid
            'button[data-testid="tweetButton"]',         # Add if new
            'div[data-testid="tweetButton"]'             # Keep as fallback
        ]
    }
}
```

## Common Selector Patterns

### Finding Buttons

**Try in order:**
1. Data attribute: `button[data-testid="buttonName"]`
2. ARIA label: `button[aria-label="Button Text"]`
3. Role + text: `button:has-text("Button Text")`
4. Type: `button[type="submit"]`

### Finding Input Fields

**Try in order:**
1. Name: `input[name="fieldName"]`
2. Autocomplete: `input[autocomplete="username"]`
3. Placeholder: `input[placeholder="Enter text"]`
4. Type: `input[type="text"]`

### Finding Links

**Try in order:**
1. Data attribute: `a[data-testid="linkName"]`
2. Href pattern: `a[href="/path"]`
3. ARIA label: `a[aria-label="Link Text"]`
4. Text: `a:has-text("Link Text")`

### Finding Divs/Containers

**Try in order:**
1. Data attribute: `div[data-testid="containerName"]`
2. Role: `div[role="textbox"]`
3. ARIA label: `div[aria-label="Container"]`
4. Class (last resort): `div.unique-class-name`

## Testing Updated Selectors

### Test Suite

After updating selectors, run complete test suite:

```bash
# 1. Check login
python x_post.py --check-login

# 2. Dry run (visible mode to observe)
python x_post.py --message "Selector test tweet" --dry-run --no-headless

# 3. Create approval
python x_post.py --message "Selector test tweet" --create-approval

# 4. Execute approved (after manually approving)
python x_post.py --execute-approved "/path/to/approved.md"

# 5. Verify tweet appeared on Twitter
```

### Validation Checklist

After selector updates:
- [ ] Login check works
- [ ] Compose button found
- [ ] Tweet textbox found
- [ ] Post button found
- [ ] Success toast detected (or post succeeds)
- [ ] No errors in logs
- [ ] Tweet appears on Twitter timeline
- [ ] Headless mode works
- [ ] Visible mode works

## Advanced Debugging

### Add Debug Logging

Temporarily add debug output to x_post.py:

```python
def try_multiple_selectors(page, selectors, timeout=5000):
    for selector in selectors:
        try:
            print(f"DEBUG: Trying selector: {selector}")  # ADD THIS
            element = page.wait_for_selector(selector, timeout=timeout)
            if element:
                print(f"✓ Found element using selector: {selector}")
                return element
        except PlaywrightTimeoutError:
            print(f"DEBUG: Selector failed: {selector}")  # ADD THIS
            continue
    return None
```

### Take Screenshots

Add screenshot capture for debugging:

```python
# After finding element (or failing)
page.screenshot(path='debug_screenshot.png')
print("Screenshot saved to debug_screenshot.png")
```

### Slow Down Execution

Add delays to observe what's happening:

```python
# After clicking compose button
compose_button.click()
time.sleep(5)  # Wait 5 seconds to observe
```

## Selector Best Practices

### DO's

✅ **Use data-testid as primary**
```python
'button[data-testid="tweetButton"]'
```

✅ **Provide multiple fallbacks**
```python
[
    'button[data-testid="tweetButton"]',
    'button[aria-label="Post"]',
    'button:has-text("Post")'
]
```

✅ **Be specific**
```python
'div[data-testid="tweetTextarea_0"]'  # Specific
# Not: 'div[role="textbox"]'  # Too generic
```

✅ **Use role for accessibility**
```python
'button[role="button"]'
```

✅ **Combine attributes**
```python
'button[data-testid="tweetButton"][aria-label="Post"]'
```

### DON'Ts

❌ **Don't rely on generated classes**
```python
# BAD - will break
'button.css-18t94o4.css-1dbjc4n'
```

❌ **Don't use overly complex selectors**
```python
# BAD - too fragile
'div > div > div > button.class1.class2'
```

❌ **Don't use position-based selectors**
```python
# BAD - will break if order changes
'button:nth-child(3)'
```

❌ **Don't hardcode text in non-English**
```python
# BAD - breaks with localization
'button:has-text("Tuitear")'  # Spanish
```

## Emergency Fixes

### Temporary Workarounds

If selectors break and you need immediate fix:

**Option 1: Extend timeout**
```python
# In x_post.py, increase timeout temporarily
element = try_multiple_selectors(page, selectors, timeout=30000)  # 30s
```

**Option 2: Add manual step**
```python
# Add manual intervention point
print("Please manually click the compose button")
time.sleep(30)  # Wait for manual action
```

**Option 3: Use coordinates (last resort)**
```python
# Click at specific screen position
page.mouse.click(x=100, y=200)
```

**⚠️ Warning:** These are temporary fixes. Update selectors properly ASAP.

## Maintenance Schedule

### Weekly

- [ ] Run `python x_post.py --check-login`
- [ ] Review recent logs for selector warnings
- [ ] Test one dry-run post

### Monthly

- [ ] Full test suite (login, create, approve, post)
- [ ] Review Twitter's changelog (if available)
- [ ] Update selectors proactively if Twitter announces UI changes

### After Twitter Updates

- [ ] Test all flows within 24 hours
- [ ] Update selectors if needed
- [ ] Document changes in this file
- [ ] Test thoroughly before returning to production

## Documentation

### When Updating Selectors

Document your changes:

```markdown
## Selector Update Log

### 2026-01-14 - Tweet Button Update
**Changed:** Tweet post button selector
**Reason:** Twitter renamed data-testid from "tweetButton" to "postButton"
**Old:** `button[data-testid="tweetButton"]`
**New:** `button[data-testid="postButton"]`
**Tested:** ✓ All flows working

### 2026-01-15 - Compose Button Update
**Changed:** Compose tweet button selector
**Reason:** Twitter changed sidebar layout
**Old:** `a[data-testid="SideNav_NewTweet_Button"]`
**New:** `button[data-testid="NavBar_Compose_Button"]`
**Tested:** ✓ Login check, dry run, actual post
```

## Support Resources

### Twitter Developer Changelog

Check for official UI updates:
- Twitter Developer Portal
- Twitter Engineering Blog
- @XDevelopers on Twitter

### Community Resources

- Playwright Documentation: https://playwright.dev/python/docs/selectors
- Twitter UI reverse engineering communities
- GitHub issues for similar projects

### When to Ask for Help

If you've tried everything and selectors still fail:
1. Document what you've tried
2. Include screenshots of element inspection
3. Share error messages
4. Note Twitter version/region if relevant

---

**Remember:** Selectors will break. This is normal. Follow this guide to diagnose and fix quickly.
