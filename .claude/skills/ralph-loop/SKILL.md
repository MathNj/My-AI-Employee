---
name: ralph-loop
description: "Autonomous task completion loop that keeps Claude working until all tasks in a plan are done. Use when you need multi-step autonomous execution. Triggers: run ralph loop, autonomous task processing, complete all tasks, ralph execute, keep working until done."
---

# Ralph Loop - Autonomous Task Completion

**Gold Tier Requirement #10** - Implements the "Ralph Wiggum" pattern from Requirements1.md Section 2D

Enables Claude Code to work autonomously on multi-step tasks until completion, solving the "one-shot" limitation through a Stop hook that intercepts exit and re-injects prompts until tasks are complete.

---

## What Is The Ralph Wiggum Pattern?

From Requirements1.md Section 2D:

> Claude Code runs in interactive mode - after processing a prompt, it waits for more input. To keep your AI Employee working autonomously until a task is complete, use the **Ralph Wiggum pattern**: a Stop hook that intercepts Claude's exit and feeds the prompt back.

### The Problem: One-Shot Limitation

Without Ralph Loop:
- Claude processes a task → exits
- Waits for next manual prompt
- Multi-step workflows require constant human intervention
- No autonomous operation

### The Solution: Stop Hook Pattern

With Ralph Loop:
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. **Stop hook checks:** Is task file in /Done?
5. **YES** → Allow exit (complete)
6. **NO** → Block exit, re-inject prompt, let Claude see its own previous failed output (loop continues)
7. Repeat until complete or max iterations

---

## How Ralph Loop Works

```
┌──────────────────────────────────────────────────────────┐
│              RALPH LOOP ARCHITECTURE                     │
└──────────────────────────────────────────────────────────┘

Orchestrator creates state file
    ↓
┌─────────────────────────────┐
│  ITERATION 1                │
│  - Spawn fresh Claude       │
│  - Read state + progress    │
│  - Process task             │
│  - Try to exit              │
└─────────────┬───────────────┘
              ↓
         Stop Hook Checks:
         Task in /Done?
              ↓
          ┌───┴───┐
          NO      YES
          ↓        ↓
    Re-inject   Allow
    prompt      exit
          ↓        ↓
┌─────────────────────────────┐
│  ITERATION 2                │
│  - Fresh context            │
│  - See previous output      │
│  - Self-correct errors      │
│  - Continue working         │
└─────────────┬───────────────┘
              ↓
         (repeat until
          complete or
          max iterations)
```

---

## Two Completion Strategies

### 1. Promise-Based (Simple)

Claude outputs a completion promise:

```markdown
<promise>TASK_COMPLETE</promise>
```

Stop hook detects the promise and allows exit.

**Use when:** Simple scripts or one-off tasks

### 2. File Movement (Advanced - Gold Tier)

Stop hook detects when task file moves to /Done:

```
/Needs_Action/EMAIL_client_request.md
    → Claude processes
    → Creates approval
    → Executes action
    → Moves to /Done/EMAIL_client_request.md
```

**Stop hook checks:** File exists in /Done → Allow exit

**Use when:**
- Production AI Employee workflows
- Integration with watcher system
- Natural workflow completion
- More reliable than promise-based

**Why better:** Completion is natural part of workflow, not artificial promise

---

## Integration With AI Employee Workflow

Ralph Loop seamlessly integrates with the Perception → Reasoning → Action architecture:

### Complete Autonomous Flow

```
1. PERCEPTION (Watchers)
   Gmail Watcher detects urgent email
   → Creates EMAIL_urgent_client.md in /Needs_Action

2. REASONING (Ralph Loop Starts)
   Iteration 1:
   - Claude reads /Needs_Action/EMAIL_urgent_client.md
   - Analyzes: Client needs invoice
   - Creates /Plans/PLAN_send_invoice.md
   - Generates invoice PDF
   - Creates approval request in /Pending_Approval
   - Tries to exit
   - Stop hook: File NOT in /Done → Loop continues

   Iteration 2:
   - Claude checks /Pending_Approval status
   - File still pending (human hasn't approved yet)
   - Waits (or processes other tasks)
   - Tries to exit
   - Stop hook: File NOT in /Done → Loop continues

3. ACTION (Human Approves)
   Human moves approval to /Approved

   Iteration 3:
   - Claude detects file in /Approved
   - Calls email MCP server
   - Sends invoice email
   - Moves EMAIL_urgent_client.md to /Done
   - Tries to exit
   - Stop hook: File IN /Done → Allow exit ✓
```

**Result:** Autonomous operation with only 1 human intervention (approval)

---

## Setup

### File Structure

```
AI_Employee_Vault/
├── Needs_Action/          # Input tasks from watchers
├── Plans/                 # Claude creates execution plans
├── Pending_Approval/      # HITL approval requests
├── Approved/              # Human-approved actions
├── Done/                  # Completed tasks
├── Logs/                  # Audit trail
└── Ralph/                 # Ralph state files
    ├── prd.json          # Task list with completion status
    ├── progress.txt      # Learnings from iterations
    ├── state.json        # Current state
    └── archive/          # Previous runs
```

### Ralph State File Format

```json
{
  "task_file": "EMAIL_urgent_client.md",
  "original_location": "/Needs_Action",
  "target_location": "/Done",
  "max_iterations": 10,
  "current_iteration": 3,
  "prompt": "Process urgent client email, create invoice, send via approval workflow",
  "completion_strategy": "file_movement",
  "started_at": "2026-01-14T10:00:00Z"
}
```

---

## Usage

### Quick Start - Process Single Task

```bash
# Process a specific task file until in /Done
/ralph-loop "Process EMAIL_urgent_client.md until moved to /Done" \
  --max-iterations 10 \
  --completion-strategy file_movement
```

### Process All Pending Tasks

```bash
# Process all files in /Needs_Action
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --max-iterations 20
```

### Promise-Based Completion

```bash
# Simple script execution with promise
/ralph-loop "Generate weekly CEO briefing" \
  --completion-promise "BRIEFING_COMPLETE" \
  --max-iterations 5
```

### PRD-Based Multi-Task Workflow

```bash
# 1. Create PRD
/prd "Email approval workflow implementation"

# 2. Convert to Ralph format
/ralph-converter "AI_Employee_Vault/Ralph/tasks/prd-email-workflow.md"

# 3. Run Ralph loop
/ralph-loop --max-iterations 15
```

---

## PRD JSON Format

For complex multi-step projects:

```json
{
  "project": "AI Employee",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Create approval file structure",
      "description": "Implement HITL approval file format",
      "acceptanceCriteria": [
        "YAML frontmatter with type, action, status",
        "Expiration timestamp (24 hours)",
        "Human-readable instructions",
        "Files created in /Pending_Approval"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

**Each task should be completable in one iteration (one context window)**

---

## Stop Hook Implementation

### Windows (PowerShell) - ralph.ps1

```powershell
# Ralph Loop - Stop Hook Pattern
param(
    [int]$MaxIterations = 10,
    [string]$TaskFile = "",
    [string]$CompletionStrategy = "file_movement"
)

$iteration = 0
$complete = $false

while (-not $complete -and $iteration -lt $MaxIterations) {
    $iteration++
    Write-Host "[ITERATION $iteration/$MaxIterations]"

    # Spawn fresh Claude Code instance
    & claude --prompt (Get-Content ralph_prompt.md)

    # Check completion strategy
    if ($CompletionStrategy -eq "file_movement") {
        # Check if task file moved to /Done
        $doneFile = "AI_Employee_Vault/Done/$TaskFile"
        if (Test-Path $doneFile) {
            Write-Host "✓ Task complete - file in /Done"
            $complete = $true
        }
    } else {
        # Check for completion promise in output
        $output = Get-Content ".last-output.txt"
        if ($output -match "<promise>TASK_COMPLETE</promise>") {
            Write-Host "✓ Task complete - promise detected"
            $complete = $true
        }
    }

    if (-not $complete) {
        Write-Host "Task incomplete - continuing loop..."
        Start-Sleep -Seconds 2
    }
}

if (-not $complete) {
    Write-Host "⚠ Max iterations reached without completion"
    exit 1
}
```

### Linux/Mac (Bash) - ralph.sh

```bash
#!/bin/bash
MAX_ITERATIONS=${1:-10}
TASK_FILE=${2:-""}
iteration=0
complete=false

while [ "$complete" = false ] && [ $iteration -lt $MAX_ITERATIONS ]; do
    ((iteration++))
    echo "[ITERATION $iteration/$MAX_ITERATIONS]"

    # Spawn fresh Claude instance
    claude --prompt "$(cat ralph_prompt.md)"

    # Check if task file in /Done
    if [ -f "AI_Employee_Vault/Done/$TASK_FILE" ]; then
        echo "✓ Task complete - file in /Done"
        complete=true
    fi

    [ "$complete" = false ] && sleep 2
done

[ "$complete" = false ] && echo "⚠ Max iterations reached" && exit 1
```

---

## Memory Persistence

Ralph maintains memory across iterations via files:

### progress.txt - Learnings

```markdown
## Codebase Patterns Discovered
- All approval files use YAML frontmatter
- MCP credentials path must be absolute
- Email sends require /Approved → /Done workflow
- Dashboard.md updates are mandatory

---

## 2026-01-14 10:15 - Iteration 1
**Task:** Process urgent client email
**Action:** Created invoice PDF, approval request
**Result:** Pending approval (incomplete)
**Learning:** Need to wait for human approval before proceeding

---

## 2026-01-14 10:30 - Iteration 2
**Task:** Check approval status
**Action:** Detected approval, sent email via MCP
**Result:** Task moved to /Done (complete ✓)
**Learning:** File movement is reliable completion signal
```

### state.json - Current State

Tracks iteration count, completion status, errors encountered.

---

## Security & HITL Integration

### Ralph Respects Human Approval

```
Claude creates:
  /Pending_Approval/PAYMENT_invoice_500.md

Ralph Loop:
  Iteration 1: Creates approval request → waits
  Iteration 2: Checks status → still pending → waits
  Iteration 3: Detects /Approved → executes → completes

KEY: Ralph NEVER auto-approves sensitive actions
```

### No Auto-Approval Actions

Ralph requires human approval for:
- Email sends to external contacts
- Social media posts
- Payment transactions
- API calls to external services
- File deletions outside vault

### Audit Trail

Every iteration logged to:
- `progress.txt` - What was attempted
- `/Logs/ralph_YYYY-MM-DD.json` - Structured logs
- Git commits (optional)

---

## Configuration

### Max Iterations

```bash
/ralph-loop --max-iterations 20  # Default: 10
```

**Guideline:**
- Simple tasks: 3-5 iterations
- Multi-step workflows: 10-15 iterations
- Complex features: 20-30 iterations

### Completion Strategy

```bash
# File movement (recommended for production)
/ralph-loop --completion-strategy file_movement

# Promise-based (simpler, less reliable)
/ralph-loop --completion-strategy promise
```

### Working Directory

```bash
/ralph-loop --ralph-dir "AI_Employee_Vault/Ralph"
```

---

## Best Practices

### 1. Task Sizing

**Right-sized (one iteration):**
- Create single approval file
- Update Dashboard.md with metrics
- Send one email via approval workflow
- Process one task from /Needs_Action

**Too large (split into smaller tasks):**
- "Build entire email system"
- "Implement all watchers"
- "Create complete HITL workflow"

**Rule:** If task can't be described in 2-3 sentences, it's too big.

### 2. Verifiable Completion Criteria

Good:
- ✅ "File EMAIL_*.md exists in /Done folder"
- ✅ "Approval request created in /Pending_Approval with required fields"
- ✅ "Dashboard.md updated with timestamp"

Bad:
- ❌ "Email system works"
- ❌ "Workflow is complete"
- ❌ "Everything done"

### 3. Proper Dependency Ordering

```
1. Data structures (file formats, schemas)
2. Creation logic (write files, generate content)
3. Monitoring logic (watch folders, detect changes)
4. Execution logic (send emails, call APIs)
5. Cleanup logic (move to /Done, update logs)
```

### 4. Progress Documentation

Add learnings to progress.txt after each iteration:
- Patterns discovered (reusable knowledge)
- Gotchas encountered (avoid future mistakes)
- Context for next iteration (state continuity)

---

## Troubleshooting

### Issue: Ralph stops after first iteration

**Cause:** Claude outputs `<promise>COMPLETE</promise>` prematurely

**Fix:** Use file_movement strategy instead of promise-based

### Issue: Infinite loop, never completes

**Cause:** Task file never moves to /Done (logic error)

**Fix:**
1. Check progress.txt for error messages
2. Verify completion criteria are achievable
3. Add debug logging to track file movements
4. Reduce max iterations to catch issue faster

### Issue: Tasks marked complete but not actually done

**Cause:** Vague acceptance criteria

**Fix:** Make criteria specific and verifiable (see Best Practices #2)

### Check Status

```bash
# View current state
cat AI_Employee_Vault/Ralph/state.json

# View progress log
cat AI_Employee_Vault/Ralph/progress.txt

# Check which iteration
jq '.current_iteration' AI_Employee_Vault/Ralph/state.json

# List files in /Done
ls AI_Employee_Vault/Done/
```

---

## Advanced: Schedule Ralph Runs

### Windows Task Scheduler

```powershell
# Run Ralph every hour to process /Needs_Action
schtasks /create /tn "AI Employee Ralph Loop" \
  /tr "powershell C:\vault\.claude\skills\ralph-loop\scripts\ralph.ps1" \
  /sc hourly
```

### Linux/Mac Cron

```bash
# Run Ralph every hour
0 * * * * cd /vault && ./.claude/skills/ralph-loop/scripts/ralph.sh 10
```

### Orchestrator Integration

```python
# orchestrator.py - Auto-trigger Ralph when tasks detected
from pathlib import Path
import subprocess

def check_and_run_ralph():
    needs_action = Path("AI_Employee_Vault/Needs_Action")

    # If tasks exist, run Ralph
    if any(needs_action.glob("*.md")):
        subprocess.run([
            "powershell",
            ".claude/skills/ralph-loop/scripts/ralph.ps1",
            "-MaxIterations", "10",
            "-CompletionStrategy", "file_movement"
        ])
```

---

## Example: End-to-End Invoice Flow

### Without Ralph (Manual - 5 interventions)

1. Gmail Watcher → /Needs_Action/EMAIL_*.md
2. **You:** "Process this email" → Claude creates plan
3. **You:** "Execute plan" → Claude creates invoice
4. **You:** "Create approval" → Approval file created
5. **You:** Move to /Approved
6. **You:** "Send email" → Email sent
7. **You:** "Move to Done"

### With Ralph (Autonomous - 1 intervention)

1. Gmail Watcher → /Needs_Action/EMAIL_*.md
2. **Ralph starts automatically** (scheduled)
3. Ralph Loop:
   - Iteration 1: Read email, create invoice, create approval → wait
   - Iteration 2: Check approval → still pending → wait
   - **[YOU APPROVE]** - Move to /Approved (only human action)
   - Iteration 3: Detect approval, send email, move to /Done → complete ✓

**Result:** 1 human action instead of 5

---

## References

- **Official Pattern:** [Ralph Wiggum by Geoffrey Huntley](https://ghuntley.com/ralph/)
- **Reference Implementation:** [github.com/anthropics/claude-code/.claude/plugins/ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- **Requirements:** Requirements1.md Section 2D - Persistence (The "Ralph Wiggum" Loop)
- **Original Ralph:** [github.com/snarktank/ralph](https://github.com/snarktank/ralph)

---

## Summary

Ralph Loop implements Gold Tier Requirement #10 by:

✅ **Stop hook** that intercepts Claude's exit
✅ **Re-injects prompt** if task incomplete
✅ **File movement detection** for reliable completion
✅ **Promise-based fallback** for simple scripts
✅ **Memory persistence** via progress.txt
✅ **Fresh context** each iteration (self-correction)
✅ **HITL respect** - never auto-approves sensitive actions
✅ **Max iteration safety** prevents infinite loops
✅ **Audit trail** for all iterations
✅ **Scheduler integration** for 24/7 autonomous operation

**Status:** Production-ready
**Tier:** Gold Tier Requirement #10 ✓
**Integration:** Seamless with AI Employee architecture
