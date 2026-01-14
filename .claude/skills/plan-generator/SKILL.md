---
name: plan-generator
description: Converts tasks, events, or requests into deterministic, auditable execution plans. Performs analysis and decomposition only - never executes actions. Maps tasks to downstream skills, identifies approval points, and creates structured Plan.md files. Core skill for Claude reasoning loop.
---

# plan-generator

## Overview

The **plan-generator** skill converts **tasks, events, or requests** into **deterministic, auditable execution plans** saved as `Plan.md` files.

**Critical Constraint:** This skill performs **ANALYSIS AND DECOMPOSITION ONLY**. It never executes actions, never calls MCP servers, and never moves approval files.

---

## Quick Start

```bash
# Generate plan from single task
python .claude/skills/plan-generator/scripts/generate_plan.py /path/to/task.md

# Scan all tasks in Needs_Action
python .claude/skills/plan-generator/scripts/generate_plan.py --scan-needs-action

# Custom output location
python .claude/skills/plan-generator/scripts/generate_plan.py task.md --output /Plans/custom.md
```

---

## When to Use This Skill

### ✅ Use when:
- New items appear in `/Needs_Action`
- A task requires multi-step reasoning
- Dependencies and sequencing must be defined
- Approval points must be identified
- User asks:
  - "Create a plan for this"
  - "What are the next steps?"
  - "Break this task down"

### ❌ Do NOT use when:
- Task is single, already-approved action
- System is executing or approving actions
- Only dashboard updates needed
- Plan already exists for task

---

## Authority & Safety Rules

### Hard Constraints

1. **Planning Only**
   - No execution
   - No side effects beyond writing plan file
   - Read-only access to vault (except /Plans)

2. **Approval Awareness**
   - Explicitly mark steps requiring human approval
   - Reference thresholds from `Company_Handbook.md`
   - Default to requiring approval when uncertain

3. **Skill Isolation**
   - Each step maps to ONE downstream skill
   - No combined or ambiguous steps
   - Clear skill responsibility

4. **No Truth Claims**
   - If external facts needed, reference `web-researcher` outputs
   - Plans must cite evidence sources when applicable
   - Never assume or fabricate information

5. **No Memory Mutation**
   - Must not write to long-term memory
   - Persistence decisions belong to downstream skills
   - Plans are ephemeral execution guides

---

## Inputs (Read-Only)

**Required:**
- `/Needs_Action/*.md` - New tasks
- `/Inbox/*.md` - Incoming items
- `/Active_Projects/*.md` - Ongoing work

**Optional:**
- `Company_Handbook.md` - Rules and thresholds
- `Business_Goals.md` - Strategic context
- Research outputs - Evidence from web-researcher
- Files explicitly referenced by task

---

## Outputs (Write-Only)

**Allowed:**
- `/Plans/PLAN_<task_name>_<YYYY-MM-DD>.md`

**Forbidden:**
- `/Approved`
- `/Pending_Approval`
- `/Done`
- `/Rejected`
- Any execution or approval actions

---

## Core Workflow

### Step 1: Task Analysis

```
Read task file
    ↓
Parse frontmatter + body
    ↓
Determine:
  - Task type (email, research, multi-step)
  - Complexity (simple, medium, complex)
  - Required skills
  - Approval needs
```

### Step 2: Task Decomposition

```
Break into atomic steps
    ↓
Map each step to ONE skill
    ↓
Identify dependencies
    ↓
Flag approval checkpoints
```

### Step 3: Plan Generation

```
Generate structured Plan.md
    ↓
Include:
  - Step-by-step instructions
  - Skill assignments
  - Approval checkpoints
  - Dependencies
  - Estimated times
    ↓
Save to /Plans
```

---

## Plan Structure

Every generated plan follows this format:

```markdown
---
task_file: TASK_example.md
created: 2026-01-12T10:30:00Z
status: pending
complexity: medium
estimated_steps: 5
requires_approval: true
---

# Execution Plan: Task Name

## Task Summary
[Brief overview]

## Original Task
[First 500 chars of task]

## Analysis
- Estimated Steps: 5
- Requires Research: Yes/No
- Requires Approval: Yes/No
- Skills Involved: skill1, skill2

## Execution Steps

### Step 1: [Description]
**Skill:** `skill-name`
**Approval Required:** Yes/No
**Dependencies:** None or Steps X, Y
**Estimated Time:** X minutes
**Notes:** Additional context

- [ ] Step 1 complete

[... more steps ...]

## Approval Checkpoints
[List of steps requiring approval]

## Safety & Constraints
[Safety reminders]

## Next Actions
[What to do next]
```

---

## Skill Mappings

The plan-generator maps task types to downstream skills:

| Task Type | Downstream Skill |
|-----------|------------------|
| `email` | email-sender |
| `linkedin_post` | linkedin-poster |
| `web_research` | web-researcher |
| `dashboard_update` | dashboard-updater |
| `schedule_task` | scheduler-manager |
| `file_operation` | Manual (vault management) |

**Unknown types:** Default to manual review

---

## Approval Detection

Plans automatically identify approval requirements based on:

1. **Company_Handbook.md thresholds**
   - Email to new contacts: Requires approval
   - Email to known contacts: May not require
   - All LinkedIn posts: Require approval
   - All payments: Require approval

2. **Task type defaults**
   - External actions: Default YES
   - Internal operations: Default NO
   - Research: NO (evidence gathering only)

3. **Explicit markers**
   - Task includes "requires approval"
   - Task flagged as sensitive

---

## Examples

### Example 1: Simple Email Task

**Input:** `Needs_Action/EMAIL_client_inquiry.md`

```markdown
---
type: email
from: client@example.com
subject: Question about pricing
---

Customer asking about our pricing for service X.
```

**Generated Plan:**

```markdown
## Execution Steps

### Step 1: Research pricing information
**Skill:** `web-researcher` (if needed)
**Approval Required:** No

### Step 2: Compose email response
**Skill:** `email-sender`
**Approval Required:** Yes
**Notes:** Create approval request with draft response

### Step 3: Human approval
**Skill:** `approval-processor (human)`
**Dependencies:** Step 2

### Step 4: Send email
**Skill:** `approval-processor (automated)`
**Dependencies:** Step 3

### Step 5: Mark complete
**Skill:** `dashboard-updater`
**Dependencies:** Step 4
```

### Example 2: Complex Research Task

**Input:** `Needs_Action/TASK_vendor_verification.md`

```markdown
---
type: research
priority: high
---

Verify that "Acme Corp" is a legitimate vendor before
engaging. Need address, contact info, and legitimacy check.
```

**Generated Plan:**

```markdown
## Execution Steps

### Step 1: Web research on Acme Corp
**Skill:** `web-researcher`
**Approval Required:** No
**Notes:** Search for official website, address, reviews

### Step 2: Verify findings
**Skill:** `Manual review`
**Approval Required:** Yes
**Dependencies:** Step 1
**Notes:** Human validates research results

### Step 3: Document in handbook
**Skill:** `Manual (vault update)`
**Dependencies:** Step 2
**Notes:** Add to approved vendors if legitimate

### Step 4: Mark complete
**Skill:** `dashboard-updater`
**Dependencies:** Step 3
```

---

## Integration with Other Skills

### With task-processor

```
task-processor detects new file in Needs_Action
    ↓
Calls plan-generator
    ↓
Plan created in /Plans
    ↓
task-processor begins Step 1
```

### With approval-processor

```
Plan identifies approval checkpoint
    ↓
Executor skill creates approval request
    ↓
Human approves/rejects
    ↓
approval-processor executes or cancels
    ↓
Plan progresses to next step
```

### With web-researcher

```
Plan Step 1: "Research XYZ"
    ↓
web-researcher executes
    ↓
Returns evidence report
    ↓
Plan Step 2 uses evidence
```

---

## Best Practices

### Planning

1. **Be Specific**
   - Each step has ONE clear action
   - No vague "handle this" steps

2. **Map to Skills**
   - Every step assigned to skill
   - Unknown = manual review

3. **Identify Approval Points**
   - Mark ALL external actions
   - Default to safe (require approval)

4. **Document Dependencies**
   - Clear prerequisite steps
   - No circular dependencies

5. **Estimate Time**
   - Realistic estimates
   - Include human approval time

### Safety

1. **No Execution**
   - Plans define, never do
   - No MCP calls
   - No file moves

2. **No Assumptions**
   - Don't fabricate facts
   - Use web-researcher for unknowns
   - Cite sources

3. **Fail Safe**
   - Uncertain → require approval
   - Unknown skill → manual review
   - Complex → break into smaller steps

---

## Monitoring and Logging

All plan generation logged to:
`/Logs/plan_generation_YYYY-MM-DD.json`

**Log entry:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "action": "plan_generated",
  "details": {
    "task_file": "TASK_example.md",
    "plan_file": "PLAN_example_2026-01-12.md",
    "complexity": "medium",
    "steps": 5,
    "requires_approval": true
  },
  "skill": "plan-generator"
}
```

---

## Troubleshooting

### "No content in task file"

**Cause:** Empty or malformed task file

**Solution:**
- Verify file has content
- Check frontmatter format
- Ensure body text exists

### "Plan not specific enough"

**Cause:** Task too vague

**Solution:**
- Add more context to task
- Break into smaller tasks
- Manual refinement of plan

### "Too many steps"

**Cause:** Overly complex task

**Solution:**
- Task may need breaking down
- Consider multiple plans
- Review for unnecessary steps

---

## Via Claude Code

When using Claude Code, simply say:

- "Create a plan for this task"
- "Generate execution plan"
- "Break this down into steps"
- "What's the plan for [task]?"

Claude will:
1. Use plan-generator skill
2. Analyze task
3. Generate structured plan
4. Save to /Plans

---

## Security Considerations

### Read-Only Inputs

- Never modifies source tasks
- Reads Company_Handbook.md without changes
- Evidence from web-researcher used as-is

### Write-Only Outputs

- Only writes to /Plans
- Never touches /Approved or /Rejected
- No execution side effects

### Approval Defaults

- External actions: Default YES
- Unknown actions: Default YES
- Internal only: Default NO (when safe)

---

## References

- See `templates/plan_template.md` for standard format
- See `Company_Handbook.md` for approval thresholds
- See other skill docs for execution details

---

**Remember:** This skill defines WHAT and WHEN, not HOW. Execution details belong to downstream skills.
