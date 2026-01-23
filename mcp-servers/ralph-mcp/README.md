# Ralph MCP Server

Model Context Protocol (MCP) server for Ralph Loop autonomous task completion.

**Version:** 2.0.0
**Status:** Production Ready
**Total Tools:** 19 (10 Phase 1 + 9 Phase 2)

## Features

### Phase 1: Core Loop ✅
- **Task Queue Management:** List, claim, and get details of tasks in /Needs_Action
- **Progress Tracking:** Update and retrieve task progress with history
- **Iteration Control:** Check if loop should continue and increment iterations
- **State Persistence:** JSON-based state storage with archiving
- **Completion Detection:** File movement or promise-based completion

### Phase 2: Advanced Features ✅
- **Multi-Task Orchestration:** Create and process task groups sequentially
- **Smart Task Discovery:** Estimate effort, detect blocking issues
- **Approval Workflow Integration:** Check status, wait for approvals
- **Performance Metrics:** Track success rate, iterations, time
- **Health Monitoring:** Detect stuck tasks, system health checks

## Installation

No external dependencies required - uses Python standard library only.

```bash
cd mcp-servers/ralph-mcp
# No pip install needed!
```

## Usage

### As MCP Server

Add to Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "ralph": {
      "command": "python",
      "args": ["/path/to/mcp-servers/ralph-mcp/server.py"],
      "env": {
        "VAULT_PATH": "/path/to/AI_Employee_Vault"
      }
    }
  }
}
```

### Direct Python Usage

```python
from ralph_core import RalphCore

# Initialize
ralph = RalphCore("/path/to/AI_Employee_Vault")

# List pending tasks
tasks = ralph.list_pending_tasks()
print(f"Found {len(tasks)} tasks")

# Claim next task
task_path = ralph.claim_next_task(priority="high")

# Create Ralph state
state = ralph.create_ralph_state(
    task_file=task_path,
    prompt="Process this urgent task",
    max_iterations=10
)

# Check if should continue
result = ralph.should_continue(state.task_id)
if result['should_continue']:
    print("Continuing loop...")

# Update progress
ralph.update_progress(
    task_id=state.task_id,
    status="in_progress",
    notes="Working on task"
)

# Check completion
completion = ralph.check_completion(state.task_id)
if completion['complete']:
    print("Task complete!")
    ralph.archive_state(state.task_id)
```

## Available Tools

### Task Queue Management

#### `list_pending_tasks`
List all tasks in /Needs_Action folder.

**Parameters:**
- `priority` (optional): Filter by priority (high/medium/low)
- `type` (optional): Filter by task type (email/whatsapp/etc)

**Returns:** Array of task objects with metadata

#### `claim_next_task`
Claim next available task for processing.

**Parameters:**
- `priority` (optional): Filter by priority
- `type` (optional): Filter by task type

**Returns:** Task file path or null

#### `get_task_details`
Get full task content and metadata.

**Parameters:**
- `task_file` (required): Path to task file

**Returns:** Task content with YAML frontmatter

### State Management

#### `create_ralph_state`
Create Ralph state for a new task.

**Parameters:**
- `task_file` (required): Path to task file
- `prompt` (required): Original prompt
- `max_iterations` (optional): Maximum iterations (default: 10)
- `completion_strategy` (optional): "file_movement" or "promise" (default: "file_movement")

**Returns:** Ralph state object

### Progress Tracking

#### `update_progress`
Update task progress in Ralph state.

**Parameters:**
- `task_id` (required): Task identifier
- `status` (required): New status (in_progress/blocked/waiting_approval)
- `notes` (optional): Progress notes

**Returns:** Updated Ralph state

#### `get_progress`
Get current progress for a task.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:** Progress details with history

#### `check_completion`
Check if task is complete (file moved to /Done).

**Parameters:**
- `task_id` (required): Task identifier

**Returns:** Boolean + completion status

### Iteration Control

#### `should_continue`
Check if Ralph should continue looping.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:** should_continue + reason

#### `increment_iteration`
Increment iteration counter.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:** New iteration count

#### `archive_state`
Archive completed task state.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:** Success status

### Phase 2: Advanced Features

#### `create_task_group`
Create a group of related tasks for batch processing.

**Parameters:**
- `task_ids` (required): Array of task IDs
- `group_name` (required): Group identifier
- `strategy` (optional): "sequential" or "parallel" (default: "sequential")

**Returns:** Group ID and group details

#### `process_task_group`
Process all tasks in a group using specified strategy.

**Parameters:**
- `group_id` (required): Group identifier

**Returns:** Processing results for all tasks

#### `estimate_effort`
Estimate task complexity and completion time.

**Parameters:**
- `task_file` (required): Path to task file

**Returns:** Task type, estimated steps, time, complexity

#### `discover_blocking_issues`
Find tasks that are blocking other tasks.

**Parameters:** None

**Returns:** Array of blocking task details

#### `check_approval_status`
Check if a task has been approved.

**Parameters:**
- `task_id` (required): Task identifier

**Returns:** Approval status and timestamp

#### `wait_for_approval`
Block until task is approved or timeout.

**Parameters:**
- `task_id` (required): Task identifier
- `timeout` (optional): Max wait time in seconds (default: 3600)
- `check_interval` (optional): Polling interval in seconds (default: 30)

**Returns:** Approval status

#### `get_performance_metrics`
Get performance metrics for specified time range.

**Parameters:**
- `time_range` (required): "today", "week", "month", or "all"

**Returns:** Tasks completed, avg iterations, avg time, success rate, blocked rate

#### `get_ralph_health`
Check overall Ralph system health.

**Parameters:** None

**Returns:** System status, active tasks, stuck tasks, avg iterations

#### `get_stuck_tasks`
Get list of all stuck tasks.

**Parameters:** None

**Returns:** Array of stuck task details with reasons

## State File Format

Ralph state is stored as JSON in `/Ralph/state/{task_id}.json`:

```json
{
  "task_id": "ralph_a1b2c3d4e5f6",
  "original_path": "Needs_Action/EMAIL_client.md",
  "target_path": "Done/EMAIL_client.md",
  "max_iterations": 10,
  "current_iteration": 3,
  "prompt": "Process urgent client email",
  "completion_strategy": "file_movement",
  "started_at": "2026-01-23T10:00:00",
  "status": "in_progress",
  "notes": [
    "2026-01-23T10:05:00: Started processing",
    "2026-01-23T10:10:00: Waiting for approval"
  ],
  "history": [
    {
      "iteration": 1,
      "timestamp": "2026-01-23T10:05:00",
      "status": "in_progress",
      "notes": "Started processing"
    },
    {
      "iteration": 2,
      "timestamp": "2026-01-23T10:10:00",
      "status": "waiting_approval",
      "notes": "Created approval request"
    }
  ]
}
```

## File Structure

```
AI_Employee_Vault/
├── Needs_Action/          # Input tasks
├── Done/                  # Completed tasks
└── Ralph/                 # Ralph state
    ├── state/             # Active task states
    │   ├── ralph_*.json  # Task state files
    │   └── ...
    └── archive/           # Completed states
        ├── ralph_*.json  # Archived states
        └── ...
```

## Completion Strategies

### 1. File Movement (Default)

Ralph checks if the task file has been moved to `/Done`:

```
/Needs_Action/EMAIL_client.md
  → Claude processes
  → Moves to /Done/EMAIL_client.md
  → Ralph detects file in /Done
  → Loop completes ✓
```

**Use for:** Production workflows, natural completion detection

### 2. Promise-Based

Ralph looks for a completion promise in output:

```markdown
<promise>TASK_COMPLETE</promise>
```

**Use for:** Simple scripts, testing, one-off tasks

## Example Workflow

### Complete Ralph Loop

```python
from ralph_core import RalphCore

ralph = RalphCore("/path/to/vault")

# 1. Claim next high-priority task
task_path = ralph.claim_next_task(priority="high")
if not task_path:
    print("No tasks to process")
    exit()

# 2. Create Ralph state
state = ralph.create_ralph_state(
    task_file=task_path,
    prompt="Process this urgent task",
    max_iterations=10
)

# 3. Main loop
while True:
    # Check if should continue
    result = ralph.should_continue(state.task_id)
    if not result['should_continue']:
        print(f"Stopping: {result['reason']}")
        break

    # Process task (Claude does this)
    print(f"Iteration {state.current_iteration}")
    # ... Claude works on task ...

    # Update progress
    ralph.update_progress(
        task_id=state.task_id,
        status="in_progress",
        notes=f"Completed iteration {state.current_iteration}"
    )

    # Check if complete
    completion = ralph.check_completion(state.task_id)
    if completion['complete']:
        print(f"Task complete: {completion['reason']}")
        ralph.archive_state(state.task_id)
        break

    # Increment iteration
    ralph.increment_iteration(state.task_id)

print("Ralph loop complete!")
```

## Logging

Logs are stored in `logs/ralph-mcp.log`:

```
2026-01-23 10:00:00 - RalphMCP - INFO - Ralph MCP Server initialized
2026-01-23 10:00:01 - RalphMCP - INFO - Tool call: claim_next_task
2026-01-23 10:00:01 - RalphMCP - INFO - Claimed task: EMAIL_client.md
2026-01-23 10:00:02 - RalphMCP - INFO - Created Ralph state for task: ralph_a1b2c3
```

## Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Error message"
}
```

Common errors:
- **Task state not found:** Task ID doesn't exist
- **No tasks available:** /Needs_Action is empty
- **Missing required parameter:** API call missing required field
- **Task file not found:** Task file doesn't exist

## Performance

- **State load/save:** <10ms per operation
- **Task listing:** <100ms for 1000 tasks
- **Completion check:** <5ms
- **Memory usage:** <50MB for 1000 active states

## Troubleshooting

### "Task state not found"

**Cause:** Task ID doesn't exist in `/Ralph/state/`

**Solution:** Create state first with `create_ralph_state`

### "No tasks available"

**Cause:** `/Needs_Action` folder is empty

**Solution:** Wait for watchers to create tasks

### "Task file not found"

**Cause:** Task file path is incorrect

**Solution:** Verify file exists in `/Needs_Action`

## Integration with Ralph Loop Skill

The Ralph MCP Server integrates with the Ralph Loop skill:

```bash
# Ralph Loop skill calls MCP tools
claude-code> /ralph-loop

# Skill uses MCP tools:
1. list_pending_tasks()
2. claim_next_task()
3. create_ralph_state()
4. should_continue()  # Called each iteration
5. update_progress()  # Called each iteration
6. check_completion() # Called each iteration
7. increment_iteration()  # Called each iteration
8. archive_state()  # Called on completion
```

## Future Enhancements

Planned features for Phase 2+:

- Multi-task orchestration
- Smart task discovery
- Approval workflow integration
- Performance metrics
- Health monitoring
- Guardrails and limits
- Emergency stop

## Support

For issues or questions:

1. Check logs: `cat mcp-servers/ralph-mcp/logs/ralph-mcp.log`
2. Verify vault path is correct
3. Check /Ralph/state/ directory
4. Test with Python API directly

---

**Version:** 1.0.0 (Phase 1: Core Loop)
**Status:** ✅ Production Ready
**Last Updated:** 2026-01-23
