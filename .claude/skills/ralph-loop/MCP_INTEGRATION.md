# Ralph Loop MCP Integration Guide

**Date:** 2026-01-23
**Version:** 1.0.0
**Status:** ✅ Production Ready

---

## Overview

The Ralph Loop skill now integrates with the **Ralph MCP Server** for enhanced state management, progress tracking, and iteration control.

---

## Quick Start

### Option 1: Using Python Script (Recommended)

```bash
cd .claude/skills/ralph-loop/scripts

# Process next high-priority task
python ralph_mcp.py --priority high

# Process next email task (max 15 iterations)
python ralph_mcp.py --type email --max-iterations 15

# Process any available task
python ralph_mcp.py
```

### Option 2: Using MCP Tools Directly

From Claude Code, call Ralph MCP tools:

```
1. ralph.list_pending_tasks({priority: "high"})
2. ralph.claim_next_task({priority: "high"})
3. ralph.create_ralph_state({
     task_file: "Needs_Action/EMAIL_urgent.md",
     prompt: "Process this urgent email",
     max_iterations: 10
   })
4. # Claude processes task...
5. ralph.should_continue({task_id: "ralph_abc123"})
6. ralph.update_progress({
     task_id: "ralph_abc123",
     status: "in_progress",
     notes: "Working on task"
   })
7. ralph.check_completion({task_id: "ralph_abc123"})
8. ralph.increment_iteration({task_id: "ralph_abc123"})
9. # Repeat until complete...
10. ralph.archive_state({task_id: "ralph_abc123"})
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Ralph Loop Skill (Orchestrator)                       │
│  - Claims next task                                     │
│  - Creates Ralph state                                  │
│  - Manages iterations                                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Ralph MCP Server (State Management)                   │
│  - list_pending_tasks()                                │
│  - claim_next_task()                                   │
│  - create_ralph_state()                                │
│  - should_continue()                                   │
│  - update_progress()                                   │
│  - check_completion()                                  │
│  - increment_iteration()                               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Ralph Core (Persistence Layer)                        │
│  - JSON state files                                    │
│  - Progress tracking                                   │
│  - History logging                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Workflow Example

### Scenario: Process Urgent Email

```bash
# Step 1: Start Ralph Loop
python .claude/skills/ralph-loop/scripts/ralph_mcp.py \
  --priority high \
  --max-iterations 10

# Step 2: Ralph claims next high-priority task
# Output: Claimed task: EMAIL_urgent_client.md

# Step 3: Ralph creates state
# Output: Task ID: ralph_3e34db7eb802

# Step 4: Claude Code processes task (Ralph waits)
# - Claude reads task from /Needs_Action
# - Analyzes email content
# - Creates invoice PDF
# - Creates approval request in /Pending_Approval

# Step 5: Ralph checks completion
# Output: Task incomplete - not in /Done yet

# Step 6: Ralph updates progress
# Output: Iteration 1: Processing task...

# Step 7: Human approves
# - Human reviews /Pending_Approval
# - Moves to /Approved

# Step 8: Next iteration
# Output: ITERATION 2/10

# Step 9: Claude sends email
# - Approval processor executes
# - Email sent via Gmail MCP
# - Task moved to /Done

# Step 10: Ralph detects completion
# Output: ✓ Task complete: File found in /Done folder

# Step 11: Ralph archives state
# Output: State archived: ralph_3e34db7eb802

# Step 12: Ralph exits successfully
# Output: RALPH LOOP COMPLETE
```

---

## Ralph MCP Tool Reference

### Task Queue Tools

#### `list_pending_tasks`
List all tasks in /Needs_Action folder.

**Parameters:**
- `priority` (optional): "high", "medium", or "low"
- `type` (optional): "email", "whatsapp", "linkedin_post", etc.

**Returns:**
```json
{
  "success": true,
  "count": 16,
  "tasks": [
    {
      "file_path": "Needs_Action/EMAIL_urgent.md",
      "file_name": "EMAIL_urgent.md",
      "type": "email",
      "priority": "high",
      "status": "pending",
      "created": "2026-01-23T10:00:00",
      "size_bytes": 1234
    }
  ]
}
```

#### `claim_next_task`
Claim next available task for processing.

**Parameters:**
- `priority` (optional): Filter by priority
- `type` (optional): Filter by task type

**Returns:**
```json
{
  "success": true,
  "task_path": "/path/to/Needs_Action/EMAIL_urgent.md"
}
```

#### `get_task_details`
Get full task content and metadata.

**Parameters:**
- `task_file` (required): Path to task file

**Returns:**
```json
{
  "success": true,
  "data": {
    "file_path": "Needs_Action/EMAIL_urgent.md",
    "file_name": "EMAIL_urgent.md",
    "metadata": {
      "type": "email",
      "priority": "high",
      "subject": "Urgent client request"
    },
    "body": "# Urgent client request\n...",
    "full_content": "---\ntype: email\n---\n..."
  }
}
```

### State Management Tools

#### `create_ralph_state`
Create Ralph state for a new task.

**Parameters:**
- `task_file` (required): Path to task file
- `prompt` (required): Original prompt
- `max_iterations` (optional): Maximum iterations (default: 10)
- `completion_strategy` (optional): "file_movement" or "promise" (default: "file_movement")

**Returns:**
```json
{
  "success": true,
  "data": {
    "task_id": "ralph_3e34db7eb802",
    "original_path": "Needs_Action/EMAIL_urgent.md",
    "target_path": "Done/EMAIL_urgent.md",
    "max_iterations": 10,
    "current_iteration": 1,
    "status": "in_progress",
    "notes": [],
    "history": []
  }
}
```

#### `update_progress`
Update task progress in Ralph state.

**Parameters:**
- `task_id` (required): Task identifier
- `status` (required): "in_progress", "blocked", "waiting_approval"
- `notes` (optional): Progress notes

**Returns:**
```json
{
  "success": true,
  "data": {
    "task_id": "ralph_3e34db7eb802",
    "status": "in_progress",
    "notes": ["2026-01-23T10:05:00: Working on task"],
    "current_iteration": 1
  }
}
```

#### `get_progress`
Get current progress for a task.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:**
```json
{
  "success": true,
  "data": {
    "task_id": "ralph_3e34db7eb802",
    "status": "in_progress",
    "current_iteration": 3,
    "max_iterations": 10,
    "started_at": "2026-01-23T10:00:00",
    "elapsed_minutes": 5.2,
    "notes": ["note1", "note2"],
    "history": [...]
  }
}
```

### Completion & Iteration Tools

#### `check_completion`
Check if task is complete (file moved to /Done).

**Parameters:**
- `task_id` (required): Task identifier

**Returns:**
```json
{
  "success": true,
  "data": {
    "complete": true,
    "reason": "File found in Done folder",
    "file_path": "Done/EMAIL_urgent.md"
  }
}
```

#### `should_continue`
Check if Ralph should continue looping.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:**
```json
{
  "success": true,
  "data": {
    "should_continue": true,
    "reason": "Task in progress"
  }
}
```

#### `increment_iteration`
Increment iteration counter.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:**
```json
{
  "success": true,
  "data": {
    "iteration": 2
  }
}
```

#### `archive_state`
Archive completed task state.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:**
```json
{
  "success": true,
  "data": {
    "task_id": "ralph_3e34db7eb802",
    "archived": true
  }
}
```

---

## Usage Patterns

### Pattern 1: Single Task Processing

```python
from ralph_core import RalphCore

ralph = RalphCore("/path/to/vault")

# Claim next high-priority task
task_path = ralph.claim_next_task(priority="high")

# Create state
state = ralph.create_ralph_state(
    task_file=task_path,
    prompt="Process this urgent task",
    max_iterations=10
)

# Loop until complete
while True:
    # Claude processes task here
    # ...

    # Check completion
    completion = ralph.check_completion(state.task_id)
    if completion['complete']:
        print("Task complete!")
        ralph.archive_state(state.task_id)
        break

    # Update progress
    ralph.update_progress(
        task_id=state.task_id,
        status="in_progress",
        notes="Still working..."
    )

    # Check should continue
    should = ralph.should_continue(state.task_id)
    if not should['should_continue']:
        print(f"Stopping: {should['reason']}")
        break

    # Increment iteration
    ralph.increment_iteration(state.task_id)
```

### Pattern 2: Batch Task Processing

```python
from ralph_core import RalphCore

ralph = RalphCore("/path/to/vault")

# Process all high-priority tasks
while True:
    # Claim next task
    task_path = ralph.claim_next_task(priority="high")

    if not task_path:
        print("No more tasks")
        break

    # Process task (using pattern above)
    # ...

    print("Task complete, claiming next...")
```

### Pattern 3: Filtered Task Processing

```python
from ralph_core import RalphCore

ralph = RalphCore("/path/to/vault")

# Process only email tasks
while True:
    task_path = ralph.claim_next_task(
        priority="medium",
        task_type="email"
    )

    if not task_path:
        break

    # Process email task
    # ...
```

---

## State File Locations

```
AI_Employee_Vault/
├── Ralph/
│   ├── state/                    # Active task states
│   │   ├── ralph_3e34db7eb802.json
│   │   ├── ralph_dd42444fce63.json
│   │   └── ...
│   ├── archive/                  # Completed states
│   │   ├── ralph_abc123.json
│   │   └── ...
│   ├── progress_mcp.txt          # Progress log
│   └── prd.json                  # Task list (legacy)
```

---

## Progress File Format

The progress file (`Ralph/progress_mcp.txt`) tracks all iterations:

```markdown
# Ralph Progress Log (MCP Integration)
Started: 2026-01-23 16:30:00
Vault: /path/to/vault
Max Iterations: 10

---

## Progress

## 2026-01-23 16:30:05
Iteration 1: Processing task...

## 2026-01-23 16:30:15
Iteration 2: Processing task...

## 2026-01-23 16:30:25
Iteration 3: Task complete - File found in Done folder
```

---

## Testing

### Test Ralph MCP Integration

```bash
cd .claude/skills/ralph-loop/scripts

# Test with dry run (no actual processing)
python ralph_mcp.py --priority high --max-iterations 1

# Test with verbose output
python ralph_mcp.py --priority high --verbose

# Test filtering by type
python ralph_mcp.py --type email --max-iterations 5
```

### Expected Output

```
═══════════════════════════════════════════════════════
  Ralph MCP Integration initialized
  Vault: /path/to/vault
  Max iterations: 10
  Priority filter: high
═══════════════════════════════════════════════════════

Claiming next task...
Claimed task: EMAIL_urgent_client.md

Creating Ralph state...
Task ID: ralph_3e34db7eb802
Max iterations: 10

Starting Ralph loop...

======================================================================
RALPH ITERATION 1/10
======================================================================

Task: email
File: EMAIL_urgent_client.md

ACTION REQUIRED:
  Claude Code should process this task now.
  When complete, move the task file to /Done

Task incomplete. Waiting 2 seconds before next iteration...

[Continues until task in /Done or max iterations reached]
```

---

## Troubleshooting

### "No tasks available"

**Cause:** /Needs_Action folder is empty

**Solution:**
- Wait for watchers to create tasks
- Or manually create a test task in /Needs_Action

### "Task state not found"

**Cause:** Invalid task ID

**Solution:**
- Check /Ralph/state/ directory for valid task IDs
- Verify task was created with create_ralph_state()

### "Max iterations reached without completion"

**Cause:** Task didn't complete in time

**Solution:**
- Increase max iterations
- Split task into smaller sub-tasks
- Check progress file for errors

### "Failed to get task details"

**Cause:** Task file doesn't exist

**Solution:**
- Verify task file path is correct
- Check file exists in /Needs_Action

---

## Migration from Legacy Ralph Loop

### Legacy (No MCP)

```powershell
# Old way - manual state management
.\ralph.ps1 -MaxIterations 10
```

### New (With MCP)

```bash
# New way - automatic state management
python ralph_mcp.py --max-iterations 10
```

**Benefits:**
- ✅ Automatic state persistence
- ✅ Progress tracking with history
- ✅ Better error handling
- ✅ Task filtering by priority/type
- ✅ Detailed logging
- ✅ State archiving
- ✅ Integration with other MCP tools

---

## Best Practices

### 1. Set Appropriate Iteration Limits

```bash
# Simple tasks: 5 iterations
python ralph_mcp.py --max-iterations 5

# Complex tasks: 15-20 iterations
python ralph_mcp.py --max-iterations 20

# Unknown complexity: 10 iterations (default)
python ralph_mcp.py
```

### 2. Use Priority Filtering

```bash
# Process urgent tasks first
python ralph_mcp.py --priority high

# Then medium priority
python ralph_mcp.py --priority medium

# Then low priority
python ralph_mcp.py --priority low
```

### 3. Filter by Task Type

```bash
# Process all emails first
python ralph_mcp.py --type email

# Then WhatsApp messages
python ralph_mcp.py --type whatsapp

# Then social media posts
python ralph_mcp.py --type linkedin_post
```

### 4. Monitor Progress

```bash
# Watch progress file in real-time
tail -f Ralph/progress_mcp.txt

# Check active states
ls -la Ralph/state/

# Check archived states
ls -la Ralph/archive/
```

### 5. Handle Errors Gracefully

```python
try:
    exit_code = ralph.run()
    if exit_code == 0:
        print("✓ Success!")
    else:
        print("⚠ Task incomplete")
        # Check progress file for details
except KeyboardInterrupt:
    print("Interrupted by user")
```

---

## Next Steps

1. **Test the integration:**
   ```bash
   python .claude/skills/ralph-loop/scripts/ralph_mcp.py --max-iterations 1
   ```

2. **Process a real task:**
   ```bash
   python .claude/skills/ralph-loop/scripts/ralph_mcp.py --priority high
   ```

3. **Monitor progress:**
   ```bash
   tail -f Ralph/progress_mcp.txt
   ```

4. **Review completed states:**
   ```bash
   ls -la Ralph/archive/
   ```

---

**Integration Status:** ✅ Complete and Production Ready
**Version:** 1.0.0
**Last Updated:** 2026-01-23
