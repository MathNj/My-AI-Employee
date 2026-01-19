---
action_type: [SEND_EMAIL | POST_LINKEDIN | POST_FACEBOOK | POST_INSTAGRAM | PROCESS_PAYMENT | DELETE_FILE]
target: [recipient email address | social platform | payment recipient]
context: [Why this action is needed - reasoning from Claude Code]
impact: [What happens if approved - business impact, risks]
risk_level: [LOW | MEDIUM | HIGH | CRITICAL]
created_timestamp: [ISO 8601 timestamp when request created]
deadline_timestamp: [ISO 8601 timestamp for approval deadline - default 24 hours]
expiration_timestamp: [ISO 8601 timestamp for auto-rejection - default 7 days]
instructions: [Move to /Approved to proceed, /Rejected to cancel]
approval_metadata:
  action_summary: [Summary of what the action will do]
  data: [Email subject/content, LinkedIn post content, payment details]
  attachments: [List of file paths for attachments]
  parameters: [Specific action parameters]

---

# Approval Request: [Action Summary]

## Context
[context]

## Action Details
- **Type**: [action_type]
- **Target**: [target]
- **Risk Level**: [risk_level]

## Impact
[impact]

## Approval Instructions
Move this file to `/Approved` to proceed with the action, or to `/Rejected` to cancel.

**Deadline**: [deadline_timestamp]
**Auto-rejection**: Will be auto-rejected after [expiration_timestamp]

---
