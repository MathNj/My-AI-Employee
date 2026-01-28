---
name: task-processor
description: Process tasks from Needs_Action folder for Personal AI Employee. Use when the user needs to process pending tasks, analyze files in Needs_Action, create action plans, or handle detected items. Triggers include "process tasks", "check needs action", "handle pending items", "process inbox", "work on tasks", or "what tasks are pending".
---

# Task Processor

## Overview

This skill processes tasks from the `/Needs_Action` folder, creates action plans, executes approved actions, and archives completed tasks to `/Done`. It's the core processing loop of the AI Employee.

## Core Workflow

The task processor follows this sequential workflow:

### 1. Read Tasks from Needs_Action

**Scan folder:**
```
Read all .md files in /Needs_Action
Parse frontmatter metadata
Extract task type, priority, and status
```

**Prioritize tasks:**
- High priority: urgent, ASAP, critical keywords
- Medium priority: standard file drops
- Low priority: informational items

### 2. Analyze Each Task

For each task file:
1. Read the full content and metadata
2. Determine task type (file_drop, email, message, etc.)
3. Identify required actions
4. Check Company_Handbook.md for relevant rules
5. Determine if approval is needed

### 3. Create Action Plan

Generate a Plan file in `/Plans` folder:

**Plan format:**
```markdown
---
task_id: [original task filename]
created: [timestamp]
status: pending
requires_approval: yes/no
---

# Action Plan: [Task Summary]

## Objective
[What needs to be accomplished]

## Analysis
[Understanding of the task]

## Proposed Actions
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Approval Required
[If yes, explain why and what approval is needed]

## Expected Outcome
[What success looks like]
```

### 4. Execute or Request Approval

**If no approval needed:**
- Execute the plan steps
- Log all actions
- Update task status

**If approval needed:**
- Create file in `/Pending_Approval`
- Wait for human to move it to `/Approved`
- Do NOT execute until approved

### 5. Complete and Archive

When task is finished:
1. Update task file with completion timestamp
2. Move task file to `/Done`
3. Move plan file to `/Done`
4. Update Dashboard with completion
5. Log the completion

## Usage Patterns

### Processing All Pending Tasks

```
1. Check /Needs_Action for .md files
2. For each file:
   - Read and analyze
   - Create plan
   - Execute or request approval
   - Archive when complete
3. Update dashboard with results
```

### Processing Single Task

```
1. Read specific task file
2. Create focused action plan
3. Execute or request approval
4. Archive and log
```

### Checking Task Status

```
1. List all tasks in /Needs_Action
2. Show priority and status
3. Highlight any blocked tasks
4. Report to dashboard
```

## Decision Tree

```
New Task Detected
    ↓
Read Task File
    ↓
Parse Metadata & Content
    ↓
Check Company Handbook Rules
    ↓
┌─ Approval Required? ─┐
│  YES          │   NO │
│   ↓           │   ↓  │
│ Create        │ Create│
│ Approval      │ Plan  │
│ Request       │   ↓   │
│   ↓           │ Execute
│ Wait for      │   ↓   │
│ Human         │       │
│   ↓           │       │
└─> Execute <───┘       │
    ↓
Archive to /Done
    ↓
Update Dashboard
```

## Task Types and Handling

### file_drop
- Analyze file content if readable
- Suggest categorization
- Recommend next steps
- Usually requires no approval

### email (future)
- Parse email content
- Draft response
- Requires approval before sending

### message (future)
- Analyze message urgency
- Draft response
- Check against contact rules

## Resources

### scripts/process_tasks.py
Basic script to run task processing loop.

### scripts/task_processor_ultimate.py
**NEW: Enhanced task processor with:**
- Parallel/concurrent task execution with ThreadPoolExecutor
- Task dependency management with DAG (Directed Acyclic Graph)
- Priority queue with aging for fair scheduling
- Progress tracking and resumption
- Structured JSON logging
- Task validation before processing
- SLA tracking and alerts
- Batch operations support
- Circular dependency detection
- Task analytics and reporting

**Usage:**
```bash
# Process all tasks with enhanced features
python .claude/skills/task-processor/scripts/task_processor_ultimate.py

# Show status with analytics
python .claude/skills/task-processor/scripts/task_processor_ultimate.py --status

# Validate task files
python .claude/skills/task-processor/scripts/task_processor_ultimate.py --validate

# Export report
python .claude/skills/task-processor/scripts/task_processor_ultimate.py --export report.json
```

### scripts/create_plan.py
Helper to generate action plan files.

### references/task_patterns.md
Common task patterns and how to handle them.

## Version History

**v2.0.0** (2026-01-26) - Ultimate Edition
- ✅ Parallel task execution with dependency management
- ✅ Priority queue with aging algorithm
- ✅ Structured JSON logging
- ✅ Task validation and SLA tracking
- ✅ Progress tracking and analytics
- ✅ Batch processing support

**v1.0.0** - Initial basic task processor
