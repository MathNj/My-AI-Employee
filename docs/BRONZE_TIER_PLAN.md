# Bronze Tier Implementation Plan

## Overview
This plan outlines the step-by-step implementation of the Bronze tier for the Personal AI Employee Hackathon 0. The Bronze tier establishes the foundational layer with basic automation capabilities.

## Bronze Tier Requirements
- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ One working Watcher script (File system monitoring)
- ✅ Claude Code successfully reading from and writing to the vault
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done
- ✅ All AI functionality implemented as Agent Skills

## Agent Skills Architecture

### 1. vault-setup (Foundational Skill)
**Purpose:** Initialize and maintain Obsidian vault structure
**Triggers:** "Set up vault", "Create vault structure", "Initialize AI employee"
**Capabilities:**
- Create folder structure (/Inbox, /Needs_Action, /Done, /Logs, /Plans, /Pending_Approval, /Approved, /Rejected)
- Generate Dashboard.md template
- Generate Company_Handbook.md template
- Validate existing vault structure

### 2. watcher-manager (Monitoring Skill)
**Purpose:** Create and manage watcher scripts for monitoring inputs
**Triggers:** "Create watcher", "Set up file monitoring", "Monitor folder"
**Capabilities:**
- Generate file system watcher script
- Configure watcher parameters (folder path, file types, interval)
- Start/stop watchers
- Test watcher functionality

### 3. task-processor (Core Processing Skill)
**Purpose:** Process tasks from Needs_Action folder
**Triggers:** "Process tasks", "Check Needs_Action", "Handle pending items"
**Capabilities:**
- Read files from /Needs_Action
- Analyze task requirements
- Create Plan.md files
- Move completed tasks to /Done
- Log all actions

### 4. dashboard-updater (Status Skill)
**Purpose:** Update Dashboard.md with current status
**Triggers:** "Update dashboard", "Show status", "Generate report"
**Capabilities:**
- Collect current system status
- Update recent activity log
- Show pending tasks count
- Display latest actions

## Implementation Phases

### Phase 1: Foundation Setup (Agent Skills Creation)
1. Create vault-setup skill
2. Create watcher-manager skill
3. Create task-processor skill
4. Create dashboard-updater skill
5. Package all skills using package_skill.py

### Phase 2: Vault Infrastructure
1. Run vault-setup skill to create folder structure
2. Initialize Dashboard.md with template
3. Initialize Company_Handbook.md with rules
4. Verify Claude Code can read/write to vault

### Phase 3: Watcher Implementation
1. Set up Python UV environment
2. Use watcher-manager skill to generate file system watcher
3. Configure watcher to monitor /Inbox folder
4. Test watcher creates files in /Needs_Action

### Phase 4: Processing Workflow
1. Test task-processor skill with sample tasks
2. Verify Plan.md generation
3. Test moving completed tasks to /Done
4. Validate logging functionality

### Phase 5: Integration & Testing
1. End-to-end workflow test
2. Update dashboard with dashboard-updater skill
3. Document the workflow
4. Create demo scenario

## Folder Structure
```
AI_Employee_Vault/
├── .claude/
│   └── skills/
│       ├── vault-setup/
│       ├── watcher-manager/
│       ├── task-processor/
│       └── dashboard-updater/
├── Inbox/              # Drop zone for new items
├── Needs_Action/       # Tasks to process
├── Plans/              # Generated plans
├── Pending_Approval/   # Items awaiting approval
├── Approved/           # Approved actions
├── Rejected/           # Rejected actions
├── Done/               # Completed tasks
├── Logs/               # Audit logs
├── watchers/           # Watcher scripts
│   └── filesystem_watcher.py
├── Dashboard.md        # Real-time status
├── Company_Handbook.md # Rules & guidelines
└── BRONZE_TIER_PLAN.md # This file
```

## Demo Workflow
1. User drops a file in /Inbox
2. Watcher detects file and creates task in /Needs_Action
3. Task-processor reads task and creates Plan.md
4. Task-processor executes plan (simple processing)
5. Task-processor moves completed task to /Done
6. Dashboard-updater refreshes Dashboard.md
7. User reviews Dashboard.md for status

## Success Criteria
- [ ] All 4 agent skills created and packaged
- [ ] Vault structure created with all folders
- [ ] Dashboard.md shows current status
- [ ] Company_Handbook.md has basic rules
- [ ] File system watcher running and detecting files
- [ ] Tasks flow: Inbox → Needs_Action → Done
- [ ] Logs capture all actions
- [ ] End-to-end demo works successfully

## Estimated Timeline
- Phase 1: 2-3 hours (Skills creation)
- Phase 2: 1 hour (Vault setup)
- Phase 3: 2 hours (Watcher implementation)
- Phase 4: 2 hours (Processing workflow)
- Phase 5: 1-2 hours (Integration & testing)
**Total: 8-10 hours**

## Next Steps
Start with Phase 1 by creating the vault-setup skill using the init_skill.py script.
