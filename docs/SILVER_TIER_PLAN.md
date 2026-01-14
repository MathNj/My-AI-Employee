# Silver Tier Implementation Plan

**Date:** 2026-01-11
**Status:** Ready to Implement
**Current Progress:** 50% (4/8 requirements complete)

---

## Executive Summary

This plan outlines the step-by-step implementation of Silver Tier for the Personal AI Employee, building on the completed Bronze Tier foundation. All new AI functionality will be implemented as Agent Skills using the skill-creator workflow.

---

## Silver Tier Requirements Analysis

### Requirements from Requirements.md (Lines 133-151)

| # | Requirement | Status | Priority | Estimated Time |
|---|-------------|--------|----------|----------------|
| 1 | All Bronze requirements | ✅ COMPLETE | - | - |
| 2 | Two or more Watcher scripts | ✅ COMPLETE | - | Already have 2 |
| 3 | Automatically Post on LinkedIn | ❌ TODO | HIGH | 4-6 hours |
| 4 | Claude reasoning loop creates Plan.md | ✅ COMPLETE | - | Already working |
| 5 | One working MCP server | ❌ TODO | HIGH | 3-4 hours |
| 6 | Human-in-the-loop approval workflow | ⚠️ PARTIAL | HIGH | 3-4 hours |
| 7 | Basic scheduling via cron/Task Scheduler | ❌ TODO | MEDIUM | 2-3 hours |
| 8 | All AI functionality as Agent Skills | ✅ COMPLETE | - | Ongoing |

**Total Estimated Time:** 12-17 hours (matching Silver tier 20-30 hour estimate)

---

## Gap Analysis

### What We Have (Bronze Tier):
- ✅ Vault structure with all folders including approval workflow folders
- ✅ 2 working watchers (Filesystem + Gmail)
- ✅ Claude Code integration with 5 agent skills
- ✅ Task processing with Plan.md generation
- ✅ Dashboard and Company_Handbook
- ✅ Comprehensive logging system

### What We Need (Silver Tier):
- ❌ **LinkedIn Integration:** Auto-posting capability
- ❌ **MCP Server:** Email sending capability
- ❌ **Approval Workflow:** Process for /Pending_Approval → /Approved → Execution
- ❌ **Scheduler:** Automated execution via cron/Task Scheduler
- ❌ **WhatsApp Watcher:** (Optional - requirements say "or more" watchers)

---

## New Agent Skills to Create

Using the skill-creator workflow, we need to create **4 new agent skills**:

### 1. linkedin-poster (Social Media Automation)
**Purpose:** Automatically post business updates to LinkedIn to generate sales leads
**Triggers:** "post to linkedin", "create linkedin post", "share on linkedin"
**Resources Needed:**
- `scripts/linkedin_post.py` - LinkedIn API integration
- `references/linkedin_api.md` - LinkedIn API documentation
- `references/post_templates.md` - Business post templates
- `assets/brand_guidelines.md` - Brand voice and messaging

### 2. email-sender (MCP Integration)
**Purpose:** Send emails via MCP server after approval
**Triggers:** "send email", "reply to email", "send approved email"
**Resources Needed:**
- `scripts/email_mcp_client.py` - MCP client for email
- `scripts/setup_email_mcp.py` - MCP server setup script
- `references/email_mcp_api.md` - Email MCP documentation
- `references/email_templates.md` - Email templates

### 3. approval-processor (Human-in-the-Loop)
**Purpose:** Process approval workflow from /Pending_Approval to execution
**Triggers:** "process approvals", "check pending approvals", "handle approval queue"
**Resources Needed:**
- `scripts/process_approvals.py` - Main approval processor
- `scripts/execute_approved_action.py` - Action executor
- `references/approval_rules.md` - Approval rules and thresholds
- `references/action_types.md` - Types of actions that need approval

### 4. scheduler-manager (Task Scheduling)
**Purpose:** Set up and manage scheduled tasks via cron/Task Scheduler
**Triggers:** "schedule task", "set up automation", "create scheduled job"
**Resources Needed:**
- `scripts/create_schedule.py` - Schedule creator (cross-platform)
- `scripts/windows_task_scheduler.py` - Windows Task Scheduler integration
- `scripts/cron_scheduler.py` - Cron integration (Linux/Mac)
- `references/scheduling_patterns.md` - Common scheduling patterns

---

## Implementation Phases

### Phase 1: Preparation (1 hour)

**Objectives:**
- Understand skill-creator workflow
- Gather LinkedIn API credentials
- Set up MCP server prerequisites
- Review approval workflow requirements

**Tasks:**
1. Review skill-creator documentation
2. Create LinkedIn Developer account and get API credentials
3. Install MCP prerequisites (Node.js packages)
4. Document current approval workflow folders

**Deliverables:**
- [ ] LinkedIn API credentials obtained
- [ ] MCP server framework installed
- [ ] Approval workflow documented
- [ ] Scheduling requirements defined

---

### Phase 2: LinkedIn Auto-Posting Skill (4-6 hours)

**Objective:** Create linkedin-poster skill for automated business posting

#### Step 1: Understand the Skill (30 min)
**Questions to explore:**
- What types of posts should be automated? (business updates, achievements, blog posts)
- How should post content be generated? (templates, AI-generated, manual)
- What approval is needed? (all posts, only certain types)
- How to track post performance? (engagement, reach)

**Expected Concrete Examples:**
- "Post about our new service offering"
- "Share this week's business achievement on LinkedIn"
- "Create a thought leadership post about AI automation"

#### Step 2: Plan Reusable Contents (30 min)
**Scripts:**
- `linkedin_post.py` - Post to LinkedIn via API
- `generate_post_content.py` - Generate post from template
- `schedule_post.py` - Schedule posts for optimal times

**References:**
- `linkedin_api.md` - LinkedIn API documentation
- `post_templates.md` - Template library (service announcements, achievements, tips)
- `best_practices.md` - Posting frequency, timing, hashtags

**Assets:**
- `brand_voice.md` - Company voice and tone guidelines
- `hashtag_library.txt` - Relevant hashtags for industry

#### Step 3: Initialize the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/init_skill.py linkedin-poster --path .claude/skills/
```

#### Step 4: Implement the Skill (2-3 hours)
1. **Implement LinkedIn API integration:**
   - OAuth2 authentication
   - Post creation and publishing
   - Media upload (images, documents)
   - Error handling and retry logic

2. **Create post templates:**
   - Service announcement template
   - Achievement celebration template
   - Thought leadership template
   - Behind-the-scenes template

3. **Write SKILL.md:**
   - Frontmatter with triggers
   - Posting workflow instructions
   - Template selection guidance
   - Approval requirements
   - Performance tracking

4. **Test scripts:**
   ```bash
   python .claude/skills/linkedin-poster/scripts/linkedin_post.py --test
   ```

#### Step 5: Package the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/linkedin-poster
```

#### Step 6: Integration Testing (30 min)
1. Create test post via skill
2. Verify approval workflow
3. Post to LinkedIn test page
4. Log action in Dashboard
5. Iterate based on results

**Deliverables:**
- [ ] linkedin-poster.skill packaged
- [ ] LinkedIn API working
- [ ] Post templates created
- [ ] Integration tested
- [ ] Documentation complete

---

### Phase 3: Email MCP Server Skill (3-4 hours)

**Objective:** Create email-sender skill with MCP integration

#### Step 1: Understand the Skill (30 min)
**Questions to explore:**
- What email operations are needed? (send, reply, draft)
- Which email service? (Gmail, Outlook, generic SMTP)
- What triggers email sending? (approved tasks, scheduled reports)
- How to handle attachments? (invoices, reports, documents)

**Expected Concrete Examples:**
- "Send approved invoice email to client"
- "Reply to customer inquiry email"
- "Send weekly business report email"

#### Step 2: Plan Reusable Contents (30 min)
**Scripts:**
- `email_mcp_client.py` - MCP client for email operations
- `setup_email_mcp.py` - MCP server installation and configuration
- `send_email.py` - Email sending via MCP
- `test_mcp_connection.py` - MCP connection testing

**References:**
- `email_mcp_api.md` - Email MCP server documentation
- `email_templates.md` - Email templates (invoice, inquiry response, report)
- `mcp_setup.md` - MCP server setup guide

**Assets:**
- `email_signature.txt` - Professional email signature
- `email_templates/` - HTML email templates

#### Step 3: Initialize the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/init_skill.py email-sender --path .claude/skills/
```

#### Step 4: Implement the Skill (1.5-2 hours)
1. **Set up Email MCP Server:**
   ```bash
   npm install -g @modelcontextprotocol/server-email
   ```

2. **Configure Claude Code for MCP:**
   Update `~/.config/claude-code/mcp.json`:
   ```json
   {
     "servers": [
       {
         "name": "email",
         "command": "npx",
         "args": ["@modelcontextprotocol/server-email"],
         "env": {
           "EMAIL_PROVIDER": "gmail",
           "EMAIL_USER": "your-email@gmail.com"
         }
       }
     ]
   }
   ```

3. **Implement email sending scripts:**
   - MCP client connection
   - Email composition from template
   - Attachment handling
   - Error handling

4. **Create email templates:**
   - Invoice email template
   - Customer inquiry response
   - Weekly report email
   - General business email

5. **Write SKILL.md:**
   - Frontmatter with triggers
   - MCP setup instructions
   - Email sending workflow
   - Template usage guide

6. **Test MCP integration:**
   ```bash
   python .claude/skills/email-sender/scripts/test_mcp_connection.py
   ```

#### Step 5: Package the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/email-sender
```

#### Step 6: Integration Testing (30 min)
1. Test MCP server connection
2. Send test email via MCP
3. Verify approval workflow integration
4. Test with attachments
5. Iterate based on results

**Deliverables:**
- [ ] email-sender.skill packaged
- [ ] MCP server configured
- [ ] Email templates created
- [ ] Send/reply working
- [ ] Documentation complete

---

### Phase 4: Approval Workflow Skill (3-4 hours)

**Objective:** Create approval-processor skill for HITL workflow

#### Step 1: Understand the Skill (30 min)
**Questions to explore:**
- What types of actions need approval? (emails, payments, posts, deletions)
- How does approval happen? (file movement, CLI command, web interface)
- What happens after approval? (execute action, log, notify)
- What happens on rejection? (log reason, notify, archive)

**Expected Concrete Examples:**
- "Process pending approval requests"
- "Execute approved email sends"
- "Handle rejected payment request"

#### Step 2: Plan Reusable Contents (30 min)
**Scripts:**
- `process_approvals.py` - Main approval processor (watches folders)
- `execute_approved_action.py` - Action executor (routes to MCP, scripts)
- `create_approval_request.py` - Helper to create approval files
- `approval_watcher.py` - Continuous monitoring of approval folders

**References:**
- `approval_rules.md` - When to require approval (from Company_Handbook)
- `action_types.md` - Types of actions (email, payment, post, deletion)
- `approval_workflow.md` - Complete workflow documentation

#### Step 3: Initialize the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/init_skill.py approval-processor --path .claude/skills/
```

#### Step 4: Implement the Skill (1.5-2 hours)
1. **Implement approval processor:**
   - Watch /Pending_Approval folder
   - Detect file movement to /Approved or /Rejected
   - Parse action metadata from frontmatter
   - Route approved actions to correct executor

2. **Implement action executor:**
   - Email actions → email-sender skill
   - LinkedIn actions → linkedin-poster skill
   - File actions → direct file operations
   - Payment actions → (future: payment MCP)

3. **Implement approval request creator:**
   - Template for approval requests
   - Auto-populate from context
   - Set expiration times
   - Priority levels

4. **Write SKILL.md:**
   - Frontmatter with triggers
   - Approval workflow overview
   - Creating approval requests
   - Processing approvals
   - Action execution

5. **Test approval workflow:**
   ```bash
   # Create test approval
   python .claude/skills/approval-processor/scripts/create_approval_request.py \
     --type email \
     --to "test@example.com" \
     --subject "Test Email"

   # Move to approved (manual)
   # Then process
   python .claude/skills/approval-processor/scripts/process_approvals.py
   ```

#### Step 5: Package the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/approval-processor
```

#### Step 6: Integration Testing (30 min)
1. Create test approval requests (email, LinkedIn post)
2. Approve and process
3. Verify execution via MCP
4. Test rejection workflow
5. Check logging to Dashboard
6. Iterate based on results

**Deliverables:**
- [ ] approval-processor.skill packaged
- [ ] Approval workflow working
- [ ] Action routing functional
- [ ] Expiration handling working
- [ ] Documentation complete

---

### Phase 5: Scheduler Management Skill (2-3 hours)

**Objective:** Create scheduler-manager skill for automated task execution

#### Step 1: Understand the Skill (30 min)
**Questions to explore:**
- What tasks should be scheduled? (dashboard update, email check, reports)
- What frequency? (every hour, daily, weekly)
- What platform? (Windows, Linux, Mac - need cross-platform)
- How to handle errors? (retry, alert, log)

**Expected Concrete Examples:**
- "Run dashboard update every hour"
- "Process approvals every 5 minutes"
- "Generate weekly business report every Monday at 8 AM"
- "Check for new Gmail every 2 minutes" (already scheduled via watcher)

#### Step 2: Plan Reusable Contents (30 min)
**Scripts:**
- `create_schedule.py` - Main scheduler (detects platform, routes)
- `windows_scheduler.py` - Windows Task Scheduler integration
- `cron_scheduler.py` - Cron integration (Linux/Mac)
- `list_schedules.py` - List current scheduled tasks
- `remove_schedule.py` - Remove scheduled task

**References:**
- `scheduling_patterns.md` - Common patterns (hourly, daily, weekly)
- `windows_task_scheduler.md` - Windows Task Scheduler guide
- `cron_syntax.md` - Cron syntax reference
- `scheduled_tasks.md` - Recommended tasks to schedule

#### Step 3: Initialize the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/init_skill.py scheduler-manager --path .claude/skills/
```

#### Step 4: Implement the Skill (1-1.5 hours)
1. **Implement cross-platform scheduler:**
   - Detect OS (Windows/Linux/Mac)
   - Route to appropriate scheduler
   - Unified interface for all platforms

2. **Windows Task Scheduler integration:**
   ```python
   import subprocess

   def create_windows_task(name, command, schedule):
       # Use schtasks.exe
       subprocess.run([
           'schtasks', '/create',
           '/tn', name,
           '/tr', command,
           '/sc', schedule
       ])
   ```

3. **Cron integration:**
   ```python
   from crontab import CronTab

   def create_cron_job(command, schedule):
       cron = CronTab(user=True)
       job = cron.new(command=command)
       job.setall(schedule)
       cron.write()
   ```

4. **Create scheduling templates:**
   - Hourly: dashboard update
   - Every 5 minutes: approval processing
   - Daily 8 AM: business report generation
   - Weekly Monday: weekly audit and CEO briefing

5. **Write SKILL.md:**
   - Frontmatter with triggers
   - Scheduling workflow
   - Platform-specific instructions
   - Common schedules
   - Troubleshooting

6. **Test scheduler:**
   ```bash
   # Schedule dashboard update (every hour)
   python .claude/skills/scheduler-manager/scripts/create_schedule.py \
     --name "dashboard-update" \
     --command "python .claude/skills/dashboard-updater/scripts/update_dashboard.py" \
     --schedule hourly

   # List schedules
   python .claude/skills/scheduler-manager/scripts/list_schedules.py
   ```

#### Step 5: Package the Skill (5 min)
```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/scheduler-manager
```

#### Step 6: Integration Testing (30 min)
1. Schedule dashboard update (every hour)
2. Schedule approval processor (every 5 minutes)
3. Schedule test task (runs in 2 minutes)
4. Verify task execution
5. Check logs
6. Remove test schedule
7. Iterate based on results

**Deliverables:**
- [ ] scheduler-manager.skill packaged
- [ ] Cross-platform scheduling working
- [ ] Core tasks scheduled
- [ ] Error handling functional
- [ ] Documentation complete

---

### Phase 6: Integration & Testing (2-3 hours)

**Objective:** Integrate all Silver tier components and run end-to-end tests

#### Integration Tasks:

1. **Update Company_Handbook.md** (30 min)
   - Add LinkedIn posting rules
   - Add email sending thresholds
   - Update approval requirements
   - Add scheduling guidelines

2. **Update Dashboard.md** (15 min)
   - Add LinkedIn activity section
   - Add MCP server status
   - Add scheduled tasks status
   - Add approval queue metrics

3. **Configure Scheduled Tasks** (30 min)
   ```bash
   # Dashboard update - every hour
   schedule: "0 * * * *"  # Cron format

   # Approval processor - every 5 minutes
   schedule: "*/5 * * * *"

   # LinkedIn post check - daily 9 AM
   schedule: "0 9 * * *"

   # Weekly CEO briefing - Monday 8 AM
   schedule: "0 8 * * 1"
   ```

4. **Create Orchestrator Script** (1 hour)
   - Master script that starts all watchers
   - Health monitoring
   - Auto-restart on failure
   - Logging aggregation

   ```python
   # orchestrator.py
   - Start filesystem watcher
   - Start gmail watcher
   - Start approval processor
   - Monitor health
   - Restart on failure
   - Aggregate logs
   ```

#### End-to-End Test Scenarios:

**Scenario 1: Email Workflow** (30 min)
1. Gmail watcher detects important email
2. Creates task in /Needs_Action
3. Task processor creates plan
4. Plan includes "send reply email"
5. Creates approval request in /Pending_Approval
6. Human approves → moves to /Approved
7. Approval processor detects approval
8. Executes email-sender skill via MCP
9. Email sent via Gmail
10. Dashboard updated with activity
11. All actions logged

**Scenario 2: LinkedIn Workflow** (30 min)
1. User requests: "Post about our new service on LinkedIn"
2. linkedin-poster skill triggered
3. Generates post from template
4. Creates approval request
5. Human reviews and approves
6. Approval processor executes post
7. Post published to LinkedIn
8. Dashboard shows LinkedIn activity
9. All actions logged

**Scenario 3: Scheduled Workflow** (30 min)
1. Scheduled task triggers (dashboard update)
2. Dashboard-updater collects stats
3. Updates Dashboard.md
4. Scheduled task triggers (approval processor)
5. Checks /Pending_Approval folder
6. Processes any approved items
7. Logs activity
8. All automated without human intervention

**Scenario 4: Multi-Channel Workflow** (30 min)
1. Drop file in Inbox (invoice)
2. Filesystem watcher creates task
3. Task processor creates plan: "Send invoice via email"
4. Creates email approval request with invoice attached
5. Human approves
6. Email sent via MCP with attachment
7. Post LinkedIn update: "Invoice sent to client"
8. Creates LinkedIn approval request
9. Human approves
10. LinkedIn post published
11. Dashboard shows both activities
12. All logged

#### Performance Testing:

1. **Load test:** Drop 20 files simultaneously
2. **Concurrency test:** Multiple approvals at once
3. **Error handling:** Simulate MCP failure, recovery
4. **Schedule reliability:** Verify all scheduled tasks execute

**Deliverables:**
- [ ] All 4 new skills integrated
- [ ] Company_Handbook updated
- [ ] Dashboard updated
- [ ] Orchestrator working
- [ ] All test scenarios passing
- [ ] Performance acceptable

---

## Silver Tier Success Criteria

### Requirements Checklist:

- [ ] All Bronze requirements ✅ (already complete)
- [ ] Two or more Watcher scripts ✅ (already have filesystem + gmail)
- [ ] Automatically Post on LinkedIn ✅ (linkedin-poster skill)
- [ ] Claude reasoning loop creates Plan.md ✅ (already working)
- [ ] One working MCP server ✅ (email-sender skill)
- [ ] Human-in-the-loop approval workflow ✅ (approval-processor skill)
- [ ] Basic scheduling via cron/Task Scheduler ✅ (scheduler-manager skill)
- [ ] All AI functionality as Agent Skills ✅ (all 4 new skills created)

### New Agent Skills Created:

1. [ ] linkedin-poster.skill
2. [ ] email-sender.skill
3. [ ] approval-processor.skill
4. [ ] scheduler-manager.skill

**Total Skills:** 9 (5 Bronze + 4 Silver)

### Functional Requirements:

- [ ] LinkedIn posts can be created and approved
- [ ] LinkedIn API working and posting successfully
- [ ] Email MCP server configured and functional
- [ ] Emails can be sent via MCP after approval
- [ ] Approval workflow processes /Pending_Approval → /Approved → Execution
- [ ] Rejection workflow works (/Rejected)
- [ ] Scheduled tasks execute automatically
- [ ] Dashboard update runs hourly
- [ ] Approval processor runs every 5 minutes
- [ ] Weekly CEO briefing scheduled (Gold tier preview)

### Documentation:

- [ ] Each skill has complete SKILL.md
- [ ] Company_Handbook updated with new rules
- [ ] Dashboard shows new activity types
- [ ] Setup guides for LinkedIn API and MCP
- [ ] Troubleshooting documentation

---

## Project Structure After Silver Tier

```
C:\Users\Najma-LP\Desktop\My Vault\
├── .claude/
│   └── skills/
│       ├── vault-setup/           # Bronze
│       ├── watcher-manager/       # Bronze
│       ├── task-processor/        # Bronze
│       ├── dashboard-updater/     # Bronze
│       ├── skill-creator/         # Bronze
│       ├── linkedin-poster/       # Silver - NEW
│       ├── email-sender/          # Silver - NEW
│       ├── approval-processor/    # Silver - NEW
│       └── scheduler-manager/     # Silver - NEW
│
├── AI_Employee_Vault/
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Plans/
│   ├── Pending_Approval/          # Now actively used
│   ├── Approved/                  # Now actively used
│   ├── Rejected/                  # Now actively used
│   ├── Done/
│   ├── Logs/
│   ├── Dashboard.md               # Enhanced with LinkedIn, MCP status
│   └── Company_Handbook.md        # Updated with new rules
│
├── watchers/
│   ├── credentials/
│   │   ├── gmail_credentials.json
│   │   └── linkedin_credentials.json  # NEW
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py
│   └── approval_watcher.py        # NEW - continuous approval monitoring
│
├── orchestrator.py                # NEW - master process manager
├── pyproject.toml
├── .gitignore
├── Requirements.md
├── BRONZE_TIER_VERIFICATION.md
├── SILVER_TIER_PLAN.md           # This file
└── README.md
```

---

## Timeline & Milestones

### Week 1: LinkedIn & MCP (8-10 hours)
- **Days 1-2:** LinkedIn skill (4-6 hours)
- **Days 3-4:** Email MCP skill (3-4 hours)
- **Milestone:** Can post to LinkedIn and send emails via approval

### Week 2: Approval & Scheduling (5-7 hours)
- **Days 1-2:** Approval workflow skill (3-4 hours)
- **Day 3:** Scheduler skill (2-3 hours)
- **Milestone:** Full automation with scheduled tasks

### Week 3: Integration & Testing (3-4 hours)
- **Day 1:** Integration (2-3 hours)
- **Day 2:** End-to-end testing (1 hour)
- **Milestone:** Silver tier complete

**Total Time:** 16-21 hours (within 20-30 hour Silver tier estimate)

---

## Risk Mitigation

### Potential Blockers:

1. **LinkedIn API Access**
   - **Risk:** LinkedIn API has strict approval process
   - **Mitigation:** Use Selenium/Playwright as fallback for posting
   - **Backup:** Manual approval for every post initially

2. **MCP Server Configuration**
   - **Risk:** MCP server setup might be complex
   - **Mitigation:** Use well-documented @modelcontextprotocol packages
   - **Backup:** Direct SMTP as fallback for email

3. **Cross-Platform Scheduling**
   - **Risk:** Different behavior on Windows vs Linux/Mac
   - **Mitigation:** Test on target platform early
   - **Backup:** Platform-specific instructions in docs

4. **OAuth Token Expiration**
   - **Risk:** LinkedIn/Gmail tokens might expire
   - **Mitigation:** Implement token refresh logic
   - **Backup:** Re-authentication guide in docs

---

## Next Steps - Getting Started

### Immediate Actions (Today):

1. **Review this plan** with user confirmation
2. **Set up LinkedIn Developer account**
   - Create app at https://www.linkedin.com/developers/
   - Get API credentials
   - Configure OAuth

3. **Install MCP prerequisites**
   ```bash
   npm install -g @modelcontextprotocol/server-email
   ```

4. **Start with linkedin-poster skill**
   ```bash
   python .claude/skills/skill-creator/scripts/init_skill.py linkedin-poster --path .claude/skills/
   ```

### Skill Creation Order (Recommended):

1. **linkedin-poster** (4-6 hours) - Highest value, independent
2. **email-sender** (3-4 hours) - Required for approval workflow
3. **approval-processor** (3-4 hours) - Integrates 1 & 2
4. **scheduler-manager** (2-3 hours) - Automation layer

This order allows testing each skill independently before integration.

---

## Success Metrics

### Quantitative Metrics:
- [ ] 4 new agent skills created and packaged
- [ ] 9 total agent skills (5 Bronze + 4 Silver)
- [ ] 100% of Silver tier requirements met (8/8)
- [ ] 3+ scheduled tasks running automatically
- [ ] 5+ approval workflows tested successfully
- [ ] 10+ LinkedIn posts created via automation
- [ ] 20+ emails sent via MCP

### Qualitative Metrics:
- [ ] Skills are well-documented and easy to use
- [ ] Approval workflow feels natural and safe
- [ ] Scheduling is reliable and doesn't require manual intervention
- [ ] LinkedIn integration generates business value
- [ ] System feels like a "Digital FTE" managing work autonomously

---

## Gold Tier Preview

After completing Silver tier, Gold tier will add:
- Facebook/Instagram integration
- Twitter (X) integration
- Xero accounting integration with MCP
- Weekly Business Audit with CEO Briefing
- Error recovery and watchdog processes
- Comprehensive documentation and lessons learned

**Gold Tier Estimated Time:** 40+ hours (additional 20-25 hours beyond Silver)

---

**Plan Status:** Ready for Implementation
**Next Action:** User confirmation and LinkedIn API setup

---

*This plan follows the skill-creator workflow and Agent Skills architecture from Requirements.md.*
*All new functionality will be implemented as reusable, well-documented agent skills.*
