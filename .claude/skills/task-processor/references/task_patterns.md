# Task Processing Patterns

## Common Task Types

### File Drop Tasks

**Metadata:**
```yaml
type: file_drop
source_file: document.pdf
size_bytes: 102400
priority: medium
```

**Processing pattern:**
1. Identify file type
2. Determine content/purpose
3. Suggest categorization
4. Archive or process

**Example actions:**
- PDF: Extract text, summarize content
- Image: Describe image, suggest tags
- Document: Review content, categorize
- Data file: Validate format, preview data

### Email Tasks (Future)

**Metadata:**
```yaml
type: email
from: client@example.com
subject: Invoice Request
priority: high
```

**Processing pattern:**
1. Parse email content
2. Identify action needed
3. Draft response
4. Request approval
5. Send after approval

### Message Tasks (Future)

**Metadata:**
```yaml
type: message
source: whatsapp
from: Client Name
keywords: urgent, invoice
```

**Processing pattern:**
1. Analyze message content
2. Check urgency keywords
3. Determine response
4. Request approval for external sends

## Priority Handling

### High Priority
**Triggers:**
- Keywords: urgent, ASAP, critical, emergency
- Payment-related
- Client escalations

**Actions:**
- Process immediately
- Create alert in Dashboard
- Flag for human review if needed

### Medium Priority
**Triggers:**
- Standard file drops
- Routine requests
- Scheduled tasks

**Actions:**
- Process in order received
- Create standard plan
- Follow normal workflow

### Low Priority
**Triggers:**
- Informational items
- Archive requests
- Cleanup tasks

**Actions:**
- Process when queue is clear
- Simple categorization
- Minimal intervention

## Approval Decision Logic

### Always Require Approval
- Sending emails (Bronze tier)
- Deleting files
- Financial transactions
- External API calls
- Modifying existing data

### Usually Auto-Approve
- Reading files
- Creating plans
- Moving to /Done
- Logging actions
- Updating dashboard

### Contextual Approval
Check Company_Handbook.md for:
- Contact-specific rules
- Dollar amount thresholds
- Time-sensitive rules
- Custom business logic

## Plan Creation Best Practices

### Good Plan Structure

```markdown
---
task_id: FILE_2026-01-11_document.md
created: 2026-01-11T10:30:00
status: pending
requires_approval: no
---

# Action Plan: Review Document

## Objective
Review uploaded document and categorize appropriately

## Analysis
- File type: PDF
- Size: 2.4 MB
- Detected: 2026-01-11 at 10:30

## Proposed Actions
- [x] Read file metadata
- [ ] Extract text content
- [ ] Identify document type
- [ ] Suggest categorization
- [ ] Archive to appropriate folder

## Expected Outcome
Document categorized and filed appropriately
```

### Poor Plan Structure

```markdown
# Plan

Process the file.

Actions:
- Do stuff
```

**Why poor:**
- No metadata
- Vague objectives
- No structured actions
- No expected outcome

## Execution Logging

Log every action with this format:

```json
{
  "timestamp": "2026-01-11T10:30:00Z",
  "action": "task_processed",
  "details": {
    "task": "FILE_2026-01-11_document.md",
    "type": "file_drop",
    "plan": "PLAN_FILE_2026-01-11_document.md",
    "outcome": "success"
  }
}
```

## Error Handling Patterns

### File Not Found
```python
try:
    content = task_file.read_text()
except FileNotFoundError:
    logger.error(f"Task file disappeared: {task_file}")
    # Skip this task, it may have been manually moved
    return None
```

### Permission Denied
```python
try:
    task_file.rename(done_path)
except PermissionError:
    logger.error(f"Cannot move file: {task_file}")
    # Create a copy instead
    shutil.copy2(task_file, done_path)
```

### Corrupted Metadata
```python
try:
    metadata = parse_frontmatter(content)
except ValueError:
    logger.warning(f"Invalid metadata in {task_file}")
    # Use defaults
    metadata = {"type": "unknown", "priority": "medium"}
```

## Batch Processing vs. Single Task

### Batch Processing (Default)
```python
# Process all tasks in Needs_Action
for task in get_pending_tasks():
    process_task(task)
```

**Best for:**
- Scheduled runs
- Catching up after downtime
- Regular processing cycles

### Single Task Processing
```python
# Process specific task
task = find_task_by_id("FILE_2026-01-11_document.md")
process_task(task)
```

**Best for:**
- Interactive mode
- High-priority items
- Testing/debugging

## Integration with Dashboard

After processing, update Dashboard with:
- Number of tasks processed
- Any errors encountered
- Current pending count
- Latest actions taken

```python
def update_dashboard_stats(processed_count, error_count):
    dashboard_path = VAULT_PATH / "Dashboard.md"
    # Update stats in dashboard
    # Add to recent activity
    # Log any alerts
```
