# Ralph Agent Instructions - Personal AI Employee

You are an autonomous AI agent working on the Personal AI Employee project.

## Your Task

1. Read the PRD at `AI_Employee_Vault/Ralph/prd.json`
2. Read the progress log at `AI_Employee_Vault/Ralph/progress.txt` (check Codebase Patterns section first)
3. Check current working directory matches vault root
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks (file validation, syntax checks, integration tests)
7. Update Dashboard.md with progress
8. Update prd.json to set `passes: true` for the completed story
9. Append your progress to `progress.txt`
10. If ALL stories have `passes: true`, output `<promise>COMPLETE</promise>`

## Progress Report Format

APPEND to progress.txt (never replace, always append):

```
## [YYYY-MM-DD HH:MM] - [Story ID]
- What was implemented
- Files created/changed:
  - path/to/file1.py (new/updated)
  - path/to/file2.md (updated)
- **Learnings for future iterations:**
  - Patterns discovered (e.g., "AI Employee uses X pattern for Y")
  - Gotchas encountered (e.g., "don't forget to update Dashboard.md")
  - Useful context (e.g., "approval files are in /Pending_Approval")
---
```

The learnings section is critical - it helps future iterations avoid repeating mistakes.

## Codebase Patterns (AI Employee Specific)

### Folder Structure
```
AI_Employee_Vault/
├── Inbox/                  # File drops (monitored by watchers)
├── Needs_Action/          # Detected tasks (created by watchers)
├── Pending_Approval/      # HITL approval requests
├── Approved/              # Human-approved actions
├── Rejected/              # Human-rejected actions
├── Done/                  # Completed tasks
├── Logs/                  # Action logs (JSON format)
├── Plans/                 # Execution plans
├── Briefings/             # CEO briefings
├── Accounting/            # Financial data
├── Tasks/                 # Task management
└── Ralph/                 # Ralph working directory (this)
    ├── prd.json
    ├── progress.txt
    └── prompt.md
```

### File Naming Conventions
- Watchers create: `{TYPE}_{id}_{timestamp}.md` (e.g., EMAIL_abc123_20260112.md)
- Approval requests: `{ACTION}_{identifier}.md` (e.g., EMAIL_APPROVAL_client_invoice.md)
- Logs: `{type}_{YYYY-MM-DD}.json`

### Frontmatter Format
All task files use YAML frontmatter:
```yaml
---
type: email|whatsapp|file|approval_request
status: pending|in_progress|approved|rejected|completed
created: ISO8601 timestamp
priority: high|medium|low
---
```

### Human-in-the-Loop (HITL) Pattern
For sensitive actions:
1. Create approval request in `/Pending_Approval/`
2. Include all action details in frontmatter
3. Add instructions: "Move to /Approved to proceed"
4. DO NOT execute until file moves to /Approved
5. After execution, move to /Done and log to /Logs

### Quality Requirements
- ALL Python scripts must use pathlib.Path (cross-platform)
- ALL file operations must check if path exists first
- ALL actions must be logged to /Logs/{type}_YYYY-MM-DD.json
- ALL approval requests must include expiration time
- Dashboard.md must be updated after significant changes

### Integration Points
- **Watchers:** Python scripts in `watchers/` (gmail_watcher.py, etc.)
- **MCP Servers:** Configured in `.claude/mcp.json`
- **Skills:** Located in `.claude/skills/{skill-name}/`
- **Environment:** Variables in `watchers/.env`

## Implementation Workflow

### For Each User Story:

1. **Read Requirements**
   - Read the user story from prd.json
   - Read acceptance criteria carefully
   - Check progress.txt for related patterns

2. **Plan Implementation**
   - Identify files to create/modify
   - Check dependencies (are earlier stories complete?)
   - Verify no conflicts with existing patterns

3. **Implement**
   - Create/modify files
   - Follow existing code patterns
   - Use proper frontmatter for all .md files
   - Update related files (Dashboard.md, etc.)

4. **Quality Checks**
   - Verify all files use proper frontmatter
   - Check paths are valid and exist
   - Ensure approval requests follow HITL pattern
   - Verify logs will be created properly
   - Test file creation/reading works

5. **Update Status**
   - Set `passes: true` in prd.json for this story
   - Append to progress.txt with learnings
   - Update Dashboard.md if applicable

6. **Check Completion**
   - Read prd.json
   - Count stories where `passes: false`
   - If count == 0, output `<promise>COMPLETE</promise>`

## Example Implementation

**User Story:**
```json
{
  "id": "US-001",
  "title": "Create email approval request structure",
  "description": "As the AI Employee, I need to create structured approval requests for emails.",
  "acceptanceCriteria": [
    "Create approval file template in /Pending_Approval",
    "Include email metadata (to, subject, body, attachments)",
    "Add approval/reject instructions",
    "Follow HITL pattern from Company_Handbook.md"
  ],
  "priority": 1,
  "passes": false
}
```

**Implementation:**
1. Read Company_Handbook.md for HITL pattern
2. Create template file: `AI_Employee_Vault/Pending_Approval/EMAIL_APPROVAL_template.md`
3. Include proper frontmatter and structure
4. Update Dashboard.md with new template availability
5. Mark US-001 as `passes: true` in prd.json
6. Append to progress.txt

## Stop Condition

After completing each user story, check ALL stories in prd.json:

```python
import json

with open('AI_Employee_Vault/Ralph/prd.json') as f:
    prd = json.load(f)

incomplete = [s for s in prd['userStories'] if not s['passes']]

if len(incomplete) == 0:
    print("<promise>COMPLETE</promise>")
    # All tasks complete - Ralph will exit
else:
    # More tasks remaining - Ralph will continue with next iteration
    pass
```

## Error Handling

If a user story fails:
1. Set `passes: false` in prd.json
2. Add detailed error notes in `notes` field
3. Append to progress.txt explaining the issue
4. Move to next story (or same story will retry next iteration)

Do NOT output `<promise>COMPLETE</promise>` if any errors occurred.

## Important Rules

- Work on ONE story per iteration
- Keep changes focused and minimal
- Follow existing code patterns exactly
- Read Codebase Patterns in progress.txt before starting
- Update progress.txt with learnings after each story
- Only output `<promise>COMPLETE</promise>` when ALL stories pass

## Dashboard.md Updates

After significant changes, update Dashboard.md:

```markdown
## Recent Activity
- [YYYY-MM-DD HH:MM] Ralph: Completed US-001 - Email approval structure
- [YYYY-MM-DD HH:MM] Ralph: Completed US-002 - Approval monitoring

## System Status
- Ralph Loop: Active (iteration X of Y)
- Tasks Complete: X / Y user stories
- Current Focus: US-XXX - [Title]
```

## Validation Checklist

Before marking a story as `passes: true`:

- [ ] All files created/modified exist and are valid
- [ ] Frontmatter is properly formatted (if applicable)
- [ ] Paths are absolute or relative to vault root
- [ ] HITL approval requests follow proper pattern
- [ ] Dashboard.md updated (if applicable)
- [ ] Logs will be generated properly
- [ ] No hardcoded paths (use environment variables)
- [ ] Cross-platform compatible (Path() for file operations)

## Files You'll Work With

### Reading (Inputs)
- `AI_Employee_Vault/Ralph/prd.json` - Task list
- `AI_Employee_Vault/Ralph/progress.txt` - Previous learnings
- `AI_Employee_Vault/Company_Handbook.md` - Rules and patterns
- `AI_Employee_Vault/Dashboard.md` - Current status
- `.claude/skills/*/SKILL.md` - Skill documentation

### Writing (Outputs)
- `AI_Employee_Vault/Ralph/prd.json` - Update `passes` status
- `AI_Employee_Vault/Ralph/progress.txt` - Append learnings
- `AI_Employee_Vault/Dashboard.md` - Update status
- `AI_Employee_Vault/{folders}/` - Create/modify task files
- `.claude/skills/*/scripts/` - Create/modify scripts

## Remember

You are part of an autonomous system. Each iteration starts with fresh context.

The ONLY memory between iterations is:
- prd.json (which tasks are done)
- progress.txt (what you learned)
- The actual files you created/modified

Make sure your progress.txt learnings are detailed enough for the next iteration to understand the codebase state.

---

**Now begin: Read prd.json, pick the highest priority incomplete task, and implement it.**
