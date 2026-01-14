# 🧪 Personal AI Employee - Complete Test Plan

**Purpose:** Verify all components are working correctly
**Estimated Time:** 15-20 minutes
**Date:** 2026-01-11

## Pre-Test Checklist

- [x] Vault structure created (9 folders)
- [x] Dashboard.md and Company_Handbook.md exist
- [x] 4 Agent Skills created
- [x] Filesystem watcher script created
- [x] Gmail watcher script created
- [ ] Python dependencies installed
- [ ] Watchers tested

## Test Suite

### Test 1: Verify Installation ⏳

**Purpose:** Check all dependencies are installed

**Commands:**
```bash
# Check Python version (should be 3.13+)
python --version

# Check watchdog library
python -c "from watchdog.observers import Observer; print('✓ Watchdog installed')"

# Check vault structure
ls -la
```

**Expected Results:**
- Python 3.13 or higher
- Watchdog library imports successfully
- All 9 folders visible (Inbox, Needs_Action, Plans, etc.)

---

### Test 2: Filesystem Watcher - Basic Detection ⏳

**Purpose:** Verify filesystem watcher detects new files

**Steps:**

1. **Start the watcher:**
   ```bash
   python watchers/filesystem_watcher.py
   ```

   **Expected output:**
   ```
   Personal AI Employee - Filesystem Watcher
   Vault: C:\Users\Najma-LP\Desktop\My Vault\AI_Employee_Vault
   Watching: ...\Inbox
   ✓ Watcher started successfully
   ```

2. **In a NEW terminal, create test file:**
   ```bash
   echo "This is a test document" > Inbox/test-file.txt
   ```

3. **Check watcher terminal:**
   **Expected output:**
   ```
   ✓ Created task for: test-file.txt
   ```

4. **Verify task file created:**
   ```bash
   ls Needs_Action/
   ```

   **Expected:** File like `FILE_2026-01-11-*.txt.md`

5. **View task content:**
   ```bash
   cat Needs_Action/FILE_*.md
   ```

   **Expected:** Markdown file with metadata and suggested actions

6. **Stop watcher:** Press `Ctrl+C`

**Success Criteria:**
- ✅ Watcher starts without errors
- ✅ File detected within 1 second
- ✅ Task file created in Needs_Action
- ✅ Task file has proper format
- ✅ Log entry created

---

### Test 3: Task Processor - Create Plans ⏳

**Purpose:** Verify task processor creates action plans

**Steps:**

1. **Check current pending tasks:**
   ```bash
   python .claude/skills/task-processor/scripts/process_tasks.py status
   ```

   **Expected output:**
   ```
   TASK PROCESSOR STATUS
   Pending Tasks:     1
   Action Plans:      0
   Completed Tasks:   0
   ```

2. **Process tasks:**
   ```bash
   python .claude/skills/task-processor/scripts/process_tasks.py
   ```

   **Expected output:**
   ```
   === Task Processor Started ===
   Found 1 pending task(s)
   Processing: FILE_2026-01-11_test-file.txt.md
   ✓ Created plan for: FILE_2026-01-11_test-file.txt.md
   === Processed 1 task(s) ===
   ```

3. **Verify plan created:**
   ```bash
   ls Plans/
   cat Plans/PLAN_*.md
   ```

   **Expected:** Plan file with analysis and proposed actions

4. **Check logs:**
   ```bash
   cat Logs/actions_2026-01-11.json
   ```

   **Expected:** JSON log with task_processed entry

**Success Criteria:**
- ✅ Task processor finds pending tasks
- ✅ Plan file created in Plans folder
- ✅ Plan has proper structure
- ✅ Action logged to JSON file

---

### Test 4: Dashboard Updater ⏳

**Purpose:** Verify dashboard shows current status

**Steps:**

1. **Update dashboard:**
   ```bash
   python .claude/skills/dashboard-updater/scripts/update_dashboard.py
   ```

   **Expected output:**
   ```
   Updating Dashboard...
   ✓ Dashboard updated successfully
   ```

2. **View dashboard:**
   ```bash
   cat Dashboard.md
   ```

   **Expected in dashboard:**
   - Pending Tasks: 1
   - Plans Generated: 1
   - Recent Activity: Shows file_detected and task_processed
   - Last refreshed timestamp updated

**Success Criteria:**
- ✅ Dashboard updates without errors
- ✅ Task counts are accurate
- ✅ Recent activity shows our test
- ✅ Timestamp is current

---

### Test 5: Complete Workflow - Multiple Files ⏳

**Purpose:** Test handling multiple files at once

**Steps:**

1. **Start filesystem watcher:**
   ```bash
   python watchers/filesystem_watcher.py
   ```

2. **In NEW terminal, create multiple test files:**
   ```bash
   echo "Invoice for January" > Inbox/invoice-jan-2026.pdf
   echo "Meeting notes" > Inbox/meeting-notes.docx
   echo "URGENT client request" > Inbox/urgent-client-request.txt
   ```

3. **Wait 2 seconds and check:**
   ```bash
   ls Needs_Action/
   ```

   **Expected:** 3 new task files

4. **Process all tasks:**
   ```bash
   python .claude/skills/task-processor/scripts/process_tasks.py
   ```

   **Expected:** 3 plans created

5. **Update dashboard:**
   ```bash
   python .claude/skills/dashboard-updater/scripts/update_dashboard.py
   cat Dashboard.md
   ```

6. **Stop watcher:** Ctrl+C

**Success Criteria:**
- ✅ All 3 files detected
- ✅ All 3 tasks created
- ✅ All 3 plans created
- ✅ Dashboard shows correct counts
- ✅ Priority correctly assigned to "urgent" file

---

### Test 6: Gmail Watcher - Authentication ⏳

**Purpose:** Verify Gmail API credentials and authentication

**Prerequisites:**
- `client_secret.json` placed in `watchers/credentials/` (renamed to `credentials.json`)
- Or path specified when running watcher

**Steps:**

1. **Check credentials file exists:**
   ```bash
   ls watchers/credentials/credentials.json
   ```

   **Expected:** File exists

2. **Start Gmail watcher:**
   ```bash
   python watchers/gmail_watcher.py
   ```

3. **OAuth2 flow:**
   - Browser should open automatically
   - Sign in with Google account
   - Click "Advanced" → "Go to app (unsafe)"
   - Grant permissions (read-only Gmail access)
   - Return to terminal

   **Expected output:**
   ```
   ✓ Gmail API authenticated successfully
   Gmail Watcher started
   Monitoring for: unread important emails
   ```

4. **Verify token created:**
   ```bash
   ls watchers/credentials/token.pickle
   ```

   **Expected:** File exists

5. **Stop watcher:** Ctrl+C

**Success Criteria:**
- ✅ OAuth2 flow completes successfully
- ✅ token.pickle created
- ✅ Watcher starts monitoring
- ✅ No authentication errors

---

### Test 7: Gmail Watcher - Email Detection ⏳

**Purpose:** Verify Gmail watcher detects emails

**Prerequisites:**
- Gmail watcher authenticated (Test 6 passed)

**Steps:**

1. **Start Gmail watcher:**
   ```bash
   python watchers/gmail_watcher.py
   ```

2. **Send test email:**
   - From another account (or same), send email to yourself
   - **Subject:** "Test: Invoice Question"
   - **Body:** "Hi, I have a question about my invoice..."
   - **Mark as Important** (star it or use priority inbox)
   - **Keep it unread**

3. **Wait 2 minutes** (watcher checks every 2 minutes)

   **Expected output:**
   ```
   Found 1 new important email(s)
   ✓ Created task for email from: sender@example.com
   ```

4. **Verify email task created:**
   ```bash
   ls Needs_Action/EMAIL_*.md
   cat Needs_Action/EMAIL_*.md
   ```

   **Expected:** Email task with subject, sender, preview, Gmail link

5. **Stop watcher:** Ctrl+C

**Success Criteria:**
- ✅ Email detected within 2 minutes
- ✅ Task file created
- ✅ Email metadata correct
- ✅ Gmail link works
- ✅ Logged to actions file

---

### Test 8: Both Watchers Running Together ⏳

**Purpose:** Verify both watchers can run simultaneously

**Steps:**

1. **Terminal 1 - Start filesystem watcher:**
   ```bash
   python watchers/filesystem_watcher.py
   ```

2. **Terminal 2 - Start Gmail watcher:**
   ```bash
   python watchers/gmail_watcher.py
   ```

3. **Terminal 3 - Create test file:**
   ```bash
   echo "Test while both running" > Inbox/both-watchers-test.txt
   ```

4. **Send test email** (mark important, keep unread)

5. **Wait 2 minutes, then check:**
   ```bash
   ls Needs_Action/
   ```

   **Expected:** Both FILE_* and EMAIL_* tasks

6. **Process all tasks:**
   ```bash
   python .claude/skills/task-processor/scripts/process_tasks.py
   ```

7. **Update dashboard:**
   ```bash
   python .claude/skills/dashboard-updater/scripts/update_dashboard.py
   cat Dashboard.md
   ```

8. **Stop both watchers:** Ctrl+C in each terminal

**Success Criteria:**
- ✅ Both watchers run without conflicts
- ✅ File detected by filesystem watcher
- ✅ Email detected by Gmail watcher
- ✅ Both tasks processed successfully
- ✅ Dashboard shows all activity

---

### Test 9: Error Handling ⏳

**Purpose:** Verify graceful error handling

**Test 9a: Missing Inbox folder**
```bash
# Temporarily rename Inbox
mv Inbox Inbox_backup

# Start watcher (should create Inbox)
python watchers/filesystem_watcher.py

# Verify Inbox recreated
ls Inbox/

# Restore
rmdir Inbox
mv Inbox_backup Inbox
```

**Test 9b: Invalid file**
```bash
# Create locked file (Windows - open in editor, Linux - chmod 000)
echo "test" > Inbox/locked.txt
# Open in Notepad to lock it

# Watcher should log error but continue
```

**Test 9c: Gmail token expired**
```bash
# Delete token
rm watchers/credentials/token.pickle

# Run watcher - should re-authenticate
python watchers/gmail_watcher.py
```

**Success Criteria:**
- ✅ Watchers handle missing folders
- ✅ Watchers handle file errors
- ✅ Gmail watcher re-authenticates when needed

---

### Test 10: Performance Check ⏳

**Purpose:** Verify system performance

**Steps:**

1. **Create many files at once:**
   ```bash
   for i in {1..10}; do echo "Test file $i" > Inbox/test-$i.txt; done
   ```

2. **Check detection:**
   ```bash
   ls Needs_Action/ | wc -l
   ```

   **Expected:** 10 files detected

3. **Process all:**
   ```bash
   time python .claude/skills/task-processor/scripts/process_tasks.py
   ```

   **Expected:** Completes in < 5 seconds

4. **Check memory usage:**
   ```bash
   # Windows
   tasklist | findstr python

   # Linux/Mac
   ps aux | grep watcher
   ```

   **Expected:** < 100 MB per watcher

**Success Criteria:**
- ✅ Handles bulk files
- ✅ Processing is fast
- ✅ Memory usage reasonable

---

## Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Verify Installation | ⏳ | |
| 2. Filesystem Watcher | ⏳ | |
| 3. Task Processor | ⏳ | |
| 4. Dashboard Updater | ⏳ | |
| 5. Complete Workflow | ⏳ | |
| 6. Gmail Auth | ⏳ | |
| 7. Gmail Detection | ⏳ | |
| 8. Both Watchers | ⏳ | |
| 9. Error Handling | ⏳ | |
| 10. Performance | ⏳ | |

## Cleanup After Testing

```bash
# Clean up test files
rm Inbox/test-*.txt
rm Needs_Action/FILE_*.md
rm Plans/PLAN_*.md

# Or keep them as examples!
```

## If All Tests Pass ✅

**Congratulations!** Your Personal AI Employee is fully functional:
- ✅ Filesystem monitoring working
- ✅ Gmail monitoring working
- ✅ Task processing working
- ✅ Dashboard updating working
- ✅ All agent skills operational

**Bronze Tier: 100% Complete** 🎉
**Silver Tier: 60% Complete** 🚀

## Next Steps After Testing

1. **Run watchers 24/7** using PM2 or background mode
2. **Set up approval workflows** for sensitive actions
3. **Add more watchers** (WhatsApp, LinkedIn)
4. **Configure MCP servers** for external actions
5. **Move to Gold tier** features

---

**Ready to start testing? Let's go!**
