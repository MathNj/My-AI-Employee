# Testing WhatsApp MCP Server

This guide walks through testing the WhatsApp MCP Server functionality.

## Prerequisites

1. **Playwright installed**: ✅ Already installed
2. **Chromium browser**: Install with:
   ```bash
   playwright install chromium
   ```

3. **WhatsApp Web authenticated**: Run WhatsApp Watcher first

## Test Scenarios

### Test 1: Verify Installation

```bash
cd mcp-servers/whatsapp-mcp

# Check Playwright can be imported
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"

# Check Chromium installed
playwright install chromium
```

### Test 2: Browser Initialization (Visible Mode)

```bash
# Run in visible mode to see what happens
python whatsapp_sender.py --to "Test Contact" --message "Test" --visible
```

**What should happen:**
1. Browser window opens
2. Navigates to WhatsApp Web
3. If authenticated: Shows chat list
4. If not authenticated: Shows QR code

**If QR code appears:**
- Scan with your phone
- Wait for chat list to load
- Close browser
- Test again

### Test 3: Send Test Message

⚠️ **WARNING: This will actually send a WhatsApp message!**

```bash
# Send a test message to a real contact
python whatsapp_sender.py \
  --to "CONTACT_NAME" \
  --message "Test message from WhatsApp MCP!" \
  --visible
```

**Replace `CONTACT_NAME` with a real contact in your WhatsApp.**

**What should happen:**
1. Browser opens WhatsApp Web
2. Searches for contact
3. Opens chat
4. Types message
5. Sends message (Enter key)
6. Confirms sent

**Expected output:**
```
[OK] Message sent successfully!
  To: CONTACT_NAME
  Time: 2026-01-22T10:30:15
```

### Test 4: Headless Mode (Production)

```bash
# Run without visible browser
python whatsapp_sender.py \
  --to "CONTACT_NAME" \
  --message "Test message in headless mode!"
```

**What should happen:**
- Same as Test 3 but without visible browser
- Message sent silently
- Check your phone to confirm

### Test 5: Approval Workflow Integration

1. **Create a test approval file** in `/Pending_Approval`:

```markdown
---
type: whatsapp
to: CONTACT_NAME
message_id: test_001
priority: medium
status: pending
---

## Message

This is a test message sent via the approval workflow!

Testing the WhatsApp MCP Server integration.

Best regards,
AI Employee
```

2. **Move to `/Approved` folder** (in Obsidian or file manager)

3. **Run approval processor**:
```bash
cd watchers
python approval_processor.py --once
```

**What should happen:**
- Approval processor detects the approved file
- Initializes WhatsApp sender
- Sends the message
- Moves file to `/Done` with success note

4. **Verify**:
   - Check your phone for the message
   - Check `/Done` folder for completion note
   - Check `Logs/whatsapp_YYYY-MM-DD.json` for audit log

### Test 6: Error Handling

#### Test 6a: Invalid Contact

```bash
python whatsapp_sender.py \
  --to "ThisContactDoesNotExist12345" \
  --message "Test"
```

**Expected:** Error message "Chat not found"

#### Test 6b: Empty Message

```bash
python whatsapp_sender.py \
  --to "CONTACT_NAME" \
  --message ""
```

**Expected:** Error handling or graceful failure

#### Test 6c: Not Authenticated

1. Close all browser windows
2. Delete session folder: `rm -rf watchers/whatsapp_session/`
3. Try sending message again

**Expected:** Error "WhatsApp Web not authenticated"

**Fix:** Run WhatsApp Watcher to re-authenticate

## Troubleshooting Tests

### "Chromium not installed"

**Error:**
```
Executable doesn't exist at: ...chromium
```

**Fix:**
```bash
playwright install chromium
```

### "Playwright not found"

**Error:**
```
ModuleNotFoundError: No module named 'playwright'
```

**Fix:**
```bash
pip install playwright
playwright install chromium
```

### "Browser crashes"

**Symptoms:**
- Test fails with browser error
- Target closed error

**Fix:**
1. Update Playwright: `pip install --upgrade playwright`
2. Reinstall browsers: `playwright install --force chromium`
3. Clear session: `rm -rf watchers/whatsapp_session/`
4. Re-authenticate

### "Chat not found"

**Error:**
```
Failed to send message: Chat not found: CONTACT_NAME
```

**Fix:**
1. Verify contact exists in your WhatsApp
2. Use exact spelling (case-sensitive)
3. Try sending manually via WhatsApp Web first
4. For groups, use full group name

### "Message not sending"

**Symptoms:**
- Browser opens, chat loads, but message doesn't send

**Debug:**
1. Run with `--visible` flag
2. Watch what happens in browser
3. Check if message input box is found
4. Check if send button is clicked
5. Check logs: `cat logs/whatsapp-mcp.log`

## Integration Test Checklist

Use this checklist to verify full integration:

- [ ] Playwright installed: `python -c "from playwright.sync_api import sync_playwright"`
- [ ] Chromium installed: `playwright install chromium`
- [ ] WhatsApp Web authenticated: Run watcher, scan QR code
- [ ] Session folder exists: `ls watchers/whatsapp_session/`
- [ ] Can send test message (visible mode)
- [ ] Can send test message (headless mode)
- [ ] Approval processor imports WhatsApp sender
- [ ] Test approval file gets processed
- [ ] Message appears on phone
- [ ] File moved to `/Done`
- [ ] Audit log created: `ls Logs/whatsapp_*.json`
- [ ] MCP server starts: `python server.py` (should wait for input)
- [ ] Skill documentation exists: `.claude/skills/whatsapp-sender/SKILL.md`

## Performance Benchmarks

Expected performance metrics:

| Operation | Target | Acceptable |
|-----------|--------|------------|
| Browser init | < 10s | < 15s |
| Chat search | < 3s | < 5s |
| Message send | < 5s | < 10s |
| Total (warm) | < 10s | < 20s |
| Total (cold) | < 20s | < 30s |

**Measure:**
```bash
time python whatsapp_sender.py --to "Contact" --message "Test"
```

## Next Steps After Testing

Once all tests pass:

1. ✅ Add to Claude Code MCP configuration
2. ✅ Update Company Handbook
3. ✅ Create example messages
4. ✅ Train auto-approver (if needed)
5. ✅ Monitor logs for issues
6. ✅ Document contact names for automation

## Test Template

Use this template for custom tests:

```python
#!/usr/bin/env python3
from whatsapp_sender import WhatsAppSender
import logging

logging.basicConfig(level=logging.INFO)

# Create sender
sender = WhatsAppSender(headless=False)

# Initialize
if not sender._initialize_browser():
    print("Failed to initialize")
    exit(1)

# Your test here
result = sender.send_message(
    to="CONTACT_NAME",
    message="Test message"
)

print(f"Result: {result}")

# Cleanup
sender.cleanup()
```

Save as `my_test.py` and run: `python my_test.py`

---

**Testing Status:**
- Playwright: ✅ Installed
- Chromium: ⚠️ Needs installation
- Auth: ⚠️ Needs WhatsApp Web login
- Tests: ⚠️ Ready to run (requires authentication)

**Next Action:** Run `playwright install chromium` then authenticate with WhatsApp Watcher.
