# 🚀 Quick Start Guide - Gold Tier

**Personal AI Employee - Fully Autonomous System**

## ✅ What's Already Done

Your Personal AI Employee is complete and operational:
- ✅ All 6 watchers (Gmail, Slack, Calendar, WhatsApp, Filesystem, Xero)
- ✅ Orchestration system with auto-restart
- ✅ Watchdog monitoring for 24/7 operation
- ✅ Approval workflow for sensitive actions
- ✅ Complete Obsidian vault structure
- ✅ Claude Code Agent Skills integration
- ✅ Auto-start on Windows boot configured

**Progress: 100% Complete - Gold Tier Achieved** 🎉

## 🎯 Start Your AI Employee (2 minutes)

### Option 1: Auto-Start (Recommended for 24/7 Operation)

**One-time setup:**
```bash
cd watchers
setup_auto_start.bat
```
(Right-click → Run as Administrator)

Your AI Employee will now start automatically when you log into Windows.

### Option 2: Manual Start

**Using batch file (easiest):**
```bash
cd watchers
start_ai_employee.bat
```

**OR using Python directly:**
```bash
cd watchers
python orchestrator.py
```

You should see:
```
======================================================================
Personal AI Employee - Orchestrator
======================================================================
Loaded config from orchestrator_config.json
Registered 6 processes
======================================================================
Orchestrator started
Health check interval: 60 seconds
Press Ctrl+C to stop
======================================================================
Starting all enabled processes...
Starting Calendar Watcher: python calendar_watcher.py
[OK] Calendar Watcher started (PID: XXXXX)
Starting Slack Watcher: python slack_watcher.py
[OK] Slack Watcher started (PID: XXXXX)
...
```

All 6 watchers are now running automatically.

### Step 2: Check System Status

Verify all watchers are running:

```bash
cd watchers
python orchestrator_cli.py status
```

You should see:
```
======================================================================
AI Employee Status
======================================================================
Orchestrator PID: XXXXX
Memory: 45.3 MB

Running Watchers:
  - Calendar Watcher (PID: XXXXX)
  - Slack Watcher (PID: XXXXX)
  - Gmail Watcher (PID: XXXXX)
  - WhatsApp Watcher (PID: XXXXX)
  - Filesystem Watcher (PID: XXXXX)
  - Xero Watcher (PID: XXXXX)
======================================================================
```

All 6 watchers are now monitoring their respective sources 24/7.

### Step 3: Test the System

**Test the Filesystem Watcher:**
```bash
# Create a test file in Inbox
echo "This is a test document for my AI Employee" > AI_Employee_Vault/Inbox/test-document.txt
```

Check the created task:
```bash
# List tasks created
dir AI_Employee_Vault\Needs_Action\

# View the created task
type AI_Employee_Vault\Needs_Action\FILE_test-document.txt.md
```

**Test the Calendar Watcher:**
- Create an event in Google Calendar for tomorrow
- Wait 5 minutes (check interval)
- Check `Needs_Action/` for `CALENDAR_EVENT_*.md`

**Test the Slack Watcher:**
- Post "test message" in #all-ai-employee-slack channel
- Wait 1 minute (check interval)
- Check `Needs_Action/` for `slack_keyword_match_*.md`

**Test the Gmail Watcher:**
- Send yourself an important email
- Wait 2 minutes (check interval)
- Check `Needs_Action/` for `EMAIL_*.md`

### Step 4: View the Dashboard

Open your Obsidian vault and view `Dashboard.md`:

```bash
# OR view in terminal
type AI_Employee_Vault\Dashboard.md
```

You'll see:
- System status overview
- Active watchers count
- Recent task activity
- Pending approvals
- Completed tasks

### Step 5: Test the Approval Workflow (Optional)

Create a LinkedIn post approval request:

```bash
python .claude/skills/linkedin-poster/scripts/linkedin_post.py --message "Testing my Personal AI Employee system! Excited about automation." --create-approval
```

You should see:
```
Creating approval request for LinkedIn post...
Created: AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_[timestamp].md
```

**To approve:**
1. Review the file in `Pending_Approval/`
2. Move it to `Approved/`
3. The approval processor will detect it and execute the post

**To reject:**
1. Move the file to `Rejected/` instead

### Step 6: Stop the System (When Needed)

```bash
cd watchers
python orchestrator_cli.py stop

# OR use the batch file
stop_ai_employee.bat
```

All 6 watchers will be gracefully stopped.

## 🎊 Success! You've Achieved Gold Tier

If you followed all steps, you now have:
- ✅ All 6 watchers running automatically (Calendar, Slack, Gmail, WhatsApp, Filesystem, Xero)
- ✅ Orchestrator managing all processes with auto-restart
- ✅ Watchdog ensuring 24/7 operation
- ✅ Approval workflow for sensitive actions
- ✅ Complete Obsidian vault integration
- ✅ Claude Code Agent Skills
- ✅ Auto-start on Windows boot
- ✅ Full audit logging and monitoring

## 📋 Daily Operation

Your AI Employee now runs continuously in the background. Here's your daily workflow:

### Morning Routine (2 minutes)
1. Open Obsidian vault
2. Review `Dashboard.md` for overnight activity
3. Check `Needs_Action/` for urgent items
4. Review calendar events detected for today

### Throughout the Day (Automatic)
- All 6 watchers continuously monitor sources
- Tasks automatically created in `Needs_Action/`
- Approval requests appear in `Pending_Approval/`
- You get notified of important events

### Evening Review (5 minutes)
1. Check `Needs_Action/` folder
2. Process tasks as needed
3. Approve/reject pending actions
4. Move completed items to `Done/`

## 🔄 Complete System Test

Test all watchers at once:

1. **Create test event in Google Calendar** (tomorrow at 10 AM)
2. **Post "test" in Slack** #all-ai-employee-slack channel
3. **Send yourself important email** with subject "Test Email"
4. **Drop file in Inbox:**
   ```bash
   echo "Test document" > AI_Employee_Vault/Inbox/test.txt
   ```

Wait a few minutes, then check `Needs_Action/`:
```bash
dir AI_Employee_Vault\Needs_Action\
```

You should see task files from all active watchers!

## 🎯 Next Steps

### Gold Tier Complete ✅
You've successfully built a fully autonomous Gold tier AI Employee!

### Further Enhancements:
- **CEO Briefing:** Set up weekly business audit reports
- **Financial Analysis:** Integrate deeper Xero analytics
- **Multi-Platform Social:** Expand to Instagram, Facebook, Twitter/X
- **Custom Watchers:** Add banking API, CRM, or other business tools
- **Advanced Automation:** Build more Claude Code Agent Skills
- **Cloud Deployment:** Move to cloud VM for true 24/7 operation
- **Team Collaboration:** Add multi-user support
- **Mobile Notifications:** Get alerts on phone for urgent items

### Scheduled Automation:
Configure Windows Task Scheduler for automated reports:
- **Daily Dashboard Update:** Every morning at 8 AM
- **Weekly CEO Briefing:** Every Monday at 7 AM
- **Monthly Financial Analysis:** First day of each month
- **Quarterly Business Audit:** Every 3 months

## 🛠️ Useful Commands

**Check system status:**
```bash
cd watchers
python orchestrator_cli.py status
```

**Start/stop/restart:**
```bash
# Start all watchers
python orchestrator_cli.py start

# Stop all watchers
python orchestrator_cli.py stop

# Restart everything
python orchestrator_cli.py restart
```

**View logs:**
```bash
# Orchestrator activity
type watchers\orchestrator.log

# Watchdog monitoring
type watchers\watchdog.log

# Specific watcher
type watchers\gmail_watcher.log

# Recent errors only
type watchers\orchestrator.log | findstr ERROR
```

**Check task counts:**
```bash
dir AI_Employee_Vault\Needs_Action\ | find /c ".md"      # Pending tasks
dir AI_Employee_Vault\Done\ | find /c ".md"              # Completed tasks
dir AI_Employee_Vault\Pending_Approval\ | find /c ".md"  # Awaiting approval
```

**Manual skill execution:**
```bash
# Process pending tasks
python .claude/skills/task-processor/scripts/process_tasks.py

# Update dashboard
python .claude/skills/dashboard-updater/scripts/update_dashboard.py

# Process approvals
python .claude/skills/approval-processor/scripts/process_approvals.py
```

## 📚 Documentation

- **Main README:** `README.md` - Complete system overview
- **Complete Workflow:** `AI_EMPLOYEE_WORKFLOW.md` - Detailed workflow documentation
- **Orchestration System:** `watchers/README_ORCHESTRATION.md` - Orchestration details
- **Full Architecture:** `Requirements1.md` - Complete architectural specification
- **Agent Skills:** `.claude/skills/*/SKILL.md` - Individual skill documentation
- **Company Rules:** `AI_Employee_Vault/Company_Handbook.md` - Business rules
- **Business Goals:** `AI_Employee_Vault/Business_Goals.md` - Targets and metrics

## 🆘 Troubleshooting

**Orchestrator won't start:**
```bash
# Check if already running
python orchestrator_cli.py status

# View error logs
type watchers\orchestrator.log

# Start manually to see errors
cd watchers
python orchestrator.py
```

**Specific watcher keeps crashing:**
1. Check orchestrator log: `type watchers\orchestrator.log | findstr ERROR`
2. Disable problematic watcher in `orchestrator_config.json`
3. Test watcher individually: `python watchers\gmail_watcher.py`
4. Fix authentication/config issue
5. Re-enable and restart orchestrator

**No tasks being created:**
1. Verify watchers are running: `python orchestrator_cli.py status`
2. Check watcher is enabled in config
3. Review watcher-specific logs
4. Test data source (send test email, post in Slack, etc.)

**WhatsApp watcher not working:**
- WhatsApp Web requires visible browser mode
- Browser window will stay open (can minimize)
- Session persists across restarts
- To disable: Set `"whatsapp": {"enabled": false}` in config

**Auto-start not working:**
```bash
# Verify scheduled task exists
schtasks /Query /TN "AI Employee Watchdog"

# Run task manually
schtasks /Run /TN "AI Employee Watchdog"

# Check Task Scheduler Event Viewer for errors
```

## 🎓 Support & Resources

- **Research Meetings:** Every Wednesday 10:00 PM on Zoom (details in Requirements1.md)
- **Video Tutorials:** See Requirements1.md for YouTube links
- **GitHub Issues:** Report bugs or request features
- **Community:** Panaversity Zoom sessions and learning resources

## 🔒 Security Notes

- All credentials stored locally in `watchers/credentials/` (gitignored)
- OAuth tokens refresh automatically
- Approval workflow prevents unauthorized actions
- Complete audit trail in activity logs
- Never commit `.env` or credential files to git

---

**🎉 Congratulations on building a Gold Tier Personal AI Employee!**

*You now have a fully autonomous system running 24/7 with:*
- *6 watchers monitoring all your inputs*
- *Automatic task creation and organization*
- *Human-in-the-loop approval for sensitive actions*
- *Complete integration with Claude Code Agent Skills*
- *Auto-restart and health monitoring*
- *Zero manual intervention required*

---

**Current Status:** Gold Tier Complete ✅
**System:** Fully Operational - 24/7 Autonomous
**Last Updated:** 2026-01-14

**Your AI Employee is now working for you, even while you sleep!** 🚀
