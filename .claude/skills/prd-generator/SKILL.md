---
name: prd-generator
description: "Generate Product Requirements Documents for AI Employee features. Use when planning a feature or task breakdown. Triggers: create a prd, write prd for, plan this feature, requirements for, spec out, break down this task."
---

# PRD Generator - Personal AI Employee

Create detailed Product Requirements Documents for AI Employee features that Ralph Loop can execute autonomously.

---

## What It Does

Converts natural language feature descriptions into structured PRDs with:
- Small, focused user stories
- Verifiable acceptance criteria
- Proper ordering by dependencies
- AI Employee-specific patterns

**Perfect for:**
- Planning new AI Employee features
- Breaking down complex tasks
- Creating Ralph Loop task lists
- Documenting feature requirements

---

## Usage

```
/prd "Email auto-response workflow with approval"
```

The skill will:
1. Ask 3-5 clarifying questions
2. Generate structured PRD
3. Save to `AI_Employee_Vault/Ralph/tasks/prd-{feature-name}.md`

---

## Workflow

### Step 1: Feature Description

Provide a brief description:
```
"Add LinkedIn posting approval workflow"
"Create WhatsApp auto-responder for urgent keywords"
"Build weekly business summary report"
```

### Step 2: Clarifying Questions

The skill asks essential questions:

```
1. What is the primary goal?
   A. Automate business communication
   B. Generate business insights
   C. Improve task processing
   D. Other: [specify]

2. Who approves actions?
   A. Human approval required (HITL)
   B. Fully autonomous
   C. Conditional (based on criteria)

3. What is the scope?
   A. Minimal viable version
   B. Full-featured implementation
   C. Backend/logic only
   D. Integration with existing features
```

### Step 3: PRD Generation

Creates structured document with:
- Introduction/Overview
- Goals (measurable)
- User Stories (small, focused)
- Functional Requirements
- Non-Goals (scope boundaries)
- Technical Considerations
- Success Metrics

### Step 4: Save

Saves to: `AI_Employee_Vault/Ralph/tasks/prd-{feature-name}.md`

---

## PRD Structure

### Introduction
Brief description of feature and problem it solves.

### Goals
Specific, measurable objectives:
- Enable X functionality
- Reduce Y time by Z%
- Automate A process

### User Stories

Each story follows this format:

```markdown
### US-001: [Title]
**Description:** As [user/system], I want [feature] so that [benefit].

**Acceptance Criteria:**
- [ ] Specific verifiable criterion 1
- [ ] Specific verifiable criterion 2
- [ ] Files created in correct locations
- [ ] Follows AI Employee patterns
```

**Important:**
- Each story must be completable in one Ralph iteration
- Criteria must be verifiable (not vague)
- Include file creation/location requirements
- Reference AI Employee patterns

### Functional Requirements
Numbered list of specific functionalities:
- FR-1: The system must create files in /Pending_Approval
- FR-2: The system must use YAML frontmatter format
- FR-3: The system must log all actions to /Logs

### Non-Goals (Out of Scope)
What this feature will NOT include:
- No automatic email deletion
- No custom AI models
- No external database requirements

### Technical Considerations
- Integration with existing watchers
- MCP server requirements
- Environment variables needed
- Dependencies on other features

### Success Metrics
How success is measured:
- Approval workflow reduces manual steps by 80%
- All actions properly logged
- Zero unauthorized actions executed

---

## Story Size Guidelines

Each user story must be completable in ONE Ralph iteration (one context window).

### Right-sized stories ✅
- Create approval request file template
- Add monitoring for /Approved folder
- Implement email send via MCP
- Update Dashboard with new metrics
- Add logging to /Logs

### Too big ❌ (split these)
- "Build entire email system"
  → Split into: approval structure, monitoring, execution, logging

- "Create all watchers"
  → Split into: one story per watcher

- "Implement HITL workflow"
  → Split into: file structure, monitoring, execution, validation

**Rule of thumb:** If you can't describe it in 2-3 sentences, it's too big.

---

## Story Ordering

Stories execute in priority order. Order by dependencies:

**Correct order:**
1. File structures and templates
2. File creation/writing logic
3. Monitoring and detection logic
4. Execution and action logic
5. Dashboard updates and reporting

**Wrong order:**
1. Execution logic (depends on files that don't exist yet)
2. File structure creation

---

## Acceptance Criteria Rules

Each criterion must be verifiable, not vague.

### Good criteria ✅
- "Create EMAIL_APPROVAL_template.md in /Pending_Approval"
- "File includes frontmatter with fields: to, subject, body"
- "Monitoring script checks /Approved every 10 seconds"
- "Actions logged to /Logs/actions_YYYY-MM-DD.json"
- "Dashboard.md updated with approval count"

### Bad criteria ❌
- "Works correctly"
- "User can approve easily"
- "Good UX"
- "Handles edge cases"

### Always include:
- Specific file paths and names
- Frontmatter field requirements
- Integration points (watchers, MCP, skills)
- Logging requirements
- Dashboard updates (if applicable)

---

## AI Employee Patterns

All PRDs must follow these patterns:

### Folder Structure
```
/Inbox → /Needs_Action → /Pending_Approval → /Approved → /Done
                                    ↓
                               /Rejected
```

### File Naming
- Input tasks: `{TYPE}_{id}_{timestamp}.md`
- Approval requests: `{ACTION}_{identifier}.md`
- Logs: `{type}_{YYYY-MM-DD}.json`

### Frontmatter Format
```yaml
---
type: email|whatsapp|social|approval_request
status: pending|approved|rejected|completed
created: ISO8601 timestamp
priority: high|medium|low
---
```

### HITL Approval
For sensitive actions:
1. Create file in /Pending_Approval
2. Include complete action details
3. Add approval/reject instructions
4. Wait for human to move to /Approved
5. Execute only after approval
6. Move to /Done and log

---

## Example PRD

### Input
```
/prd "Email approval workflow for AI Employee"
```

### Output: `AI_Employee_Vault/Ralph/tasks/prd-email-workflow.md`

```markdown
# PRD: Email Approval Workflow

## Introduction

Implement Human-in-the-Loop (HITL) approval workflow for email sending. When AI Employee detects an email that needs to be sent, it creates an approval request and waits for human approval before sending via Gmail MCP.

## Goals

- Prevent unauthorized email sends
- Give human oversight on all email communication
- Maintain audit trail of approvals
- Enable easy approve/reject workflow

## User Stories

### US-001: Create email approval request structure
**Description:** As the AI Employee, I need to create structured approval requests for emails detected in /Needs_Action.

**Acceptance Criteria:**
- [ ] Create template: /Pending_Approval/EMAIL_APPROVAL_{recipient}_{timestamp}.md
- [ ] Include frontmatter: type, status, created, expires, email_to, email_subject
- [ ] Include email body preview
- [ ] Add approval instructions: "Move to /Approved to send"
- [ ] Add rejection instructions: "Move to /Rejected to cancel"

### US-002: Monitor Approved folder for email sends
**Description:** As the AI Employee, I need to detect when humans approve email requests.

**Acceptance Criteria:**
- [ ] Create approval_monitor.py script in email-sender skill
- [ ] Monitor /Approved folder every 10 seconds
- [ ] Detect EMAIL_APPROVAL_*.md files
- [ ] Parse frontmatter for email metadata
- [ ] Validate expiration time (reject if > 24 hours old)

### US-003: Execute approved email sends
**Description:** As the AI Employee, I need to send emails after human approval.

**Acceptance Criteria:**
- [ ] Call Gmail MCP with email metadata from approval file
- [ ] Send email via gmail-mcp server
- [ ] Handle MCP errors gracefully
- [ ] Log send action to /Logs/actions_YYYY-MM-DD.json
- [ ] Move approval file to /Done after successful send

### US-004: Update Dashboard with approval statistics
**Description:** As a user, I want to see approval workflow statistics on Dashboard.

**Acceptance Criteria:**
- [ ] Add "Pending Approvals" count to Dashboard.md
- [ ] Show last 5 approval actions in Recent Activity
- [ ] Display approval/rejection ratio
- [ ] Update after each approval action

## Functional Requirements

- FR-1: Approval files created in /Pending_Approval with unique names
- FR-2: All approval files expire after 24 hours
- FR-3: Monitoring runs continuously (background process)
- FR-4: Email sends only occur after human moves file to /Approved
- FR-5: All actions logged with timestamps and outcomes
- FR-6: Dashboard updated in real-time

## Non-Goals

- No automatic email approval (always requires human)
- No email drafting AI (just sends pre-composed emails)
- No email filtering or spam detection
- No email threading or conversation tracking

## Technical Considerations

- Uses gmail-mcp server (must be configured)
- Requires watchdog library for folder monitoring
- Uses YAML frontmatter for metadata
- Integrates with approval-processor skill
- Logs to /Logs in JSON format

## Success Metrics

- 100% of emails require human approval
- Approval workflow completes in < 2 minutes
- Zero unauthorized email sends
- All actions logged and auditable

## Open Questions

- Should expired approvals auto-move to /Rejected?
- Should we add email preview in approval file?
```

---

## Quick Response Format

Users can answer questions quickly with letter codes:

**Questions:**
```
1. Primary goal?
   A. Automation
   B. Insights
   C. Integration

2. Approval needed?
   A. Yes (HITL)
   B. No (autonomous)

3. Scope?
   A. Minimal
   B. Full
```

**User response:**
```
1A, 2A, 3A
```

The skill interprets and generates the PRD accordingly.

---

## Next Steps After PRD

1. **Review PRD**
   ```bash
   cat AI_Employee_Vault/Ralph/tasks/prd-{feature}.md
   ```

2. **Convert to Ralph format**
   ```bash
   /ralph-converter "AI_Employee_Vault/Ralph/tasks/prd-{feature}.md"
   ```

3. **Run Ralph Loop**
   ```bash
   /ralph-loop --max-iterations 10
   ```

---

## Files Created

```
AI_Employee_Vault/Ralph/tasks/
└── prd-{feature-name}.md    # Generated PRD
```

---

## Integration

Works seamlessly with:
- **ralph-converter**: Converts PRD to prd.json
- **ralph-loop**: Executes the PRD autonomously
- **task-processor**: Processes individual tasks
- **plan-generator**: Creates execution plans

---

## Best Practices

### 1. Be Specific
- ❌ "Improve email handling"
- ✅ "Add HITL approval for email sends with 24hr expiration"

### 2. Think Small
Break features into tiny stories that each create/modify 1-3 files

### 3. Order by Dependencies
Database → Backend → Frontend → Dashboard

### 4. Include File Paths
Every criterion should mention exact file locations

### 5. Follow Patterns
Use AI Employee folder structure and naming conventions

---

## Troubleshooting

### PRD stories too large

**Symptom:** Ralph iterations fail or timeout

**Fix:** Break each story into smaller pieces (1-3 file changes each)

### Vague acceptance criteria

**Symptom:** Ralph marks tasks complete but they're not actually done

**Fix:** Make criteria verifiable with specific file names and content

### Wrong execution order

**Symptom:** Later stories fail because dependencies missing

**Fix:** Reorder stories: structures → logic → execution → reporting

---

## References

- See ralph-loop skill for execution
- See ralph-converter skill for PRD → JSON conversion
- See Requirements1.md Section 2D for Ralph Wiggum pattern

---

**Status:** Ready to use
**Integration:** Works with ralph-converter and ralph-loop skills
**Output:** Markdown PRDs in AI_Employee_Vault/Ralph/tasks/
