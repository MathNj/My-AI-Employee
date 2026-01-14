# Action Types Reference

Complete specification for all supported action types in the approval workflow system.

## Overview

Each action type has a specific schema, executor, and validation rules. This document provides the complete specification for implementing new action types.

---

## Email Actions

### Type Identifier
```yaml
type: email
```

### Executor
- **Skill:** email-sender
- **Script:** `.claude/skills/email-sender/scripts/send_email.py`
- **Execution:** `python send_email.py --execute-approved <file_path>`

### Required Fields

```yaml
type: email                    # Action type identifier
action: send_email             # Specific action
to: "recipient@example.com"    # Recipient email address
subject: "Email subject"       # Email subject line
body_full: |                   # Full email body (multiline)
  Email content goes here...
created: "2026-01-12T10:00:00Z"  # ISO 8601 timestamp
expires: "2026-01-13T10:00:00Z"  # ISO 8601 timestamp
status: pending                # Always 'pending' for new requests
```

### Optional Fields

```yaml
cc: ["cc1@example.com", "cc2@example.com"]  # CC recipients
bcc: ["bcc@example.com"]                     # BCC recipients
attachments: ["/path/to/file.pdf"]           # File paths
html: true                                    # Use HTML format
reply_to: "reply@example.com"                # Reply-to address
priority: high                                # Email priority
```

### Validation Rules

1. **Email addresses:** Must be valid RFC 5322 format
2. **Attachments:** Must exist and be readable
3. **Body:** Cannot be empty
4. **Subject:** Recommended max 78 characters
5. **Attachment size:** Combined max 25 MB (Gmail limit)

### Example Files

**Simple email:**
```markdown
---
type: email
action: send_email
to: "client@example.com"
subject: "Invoice #1234"
body_full: |
  Dear Client,

  Please find your invoice attached.

  Best regards,
  Your Company
created: "2026-01-12T10:00:00Z"
expires: "2026-01-13T10:00:00Z"
status: pending
attachments: ["/path/to/invoice.pdf"]
---

# Email Approval Request

Sending invoice to client@example.com

## To Approve
Move to /Approved

## To Reject
Move to /Rejected
```

**Reply email:**
```markdown
---
type: email
action: send_email
to: "sender@example.com"
subject: "Re: Question about pricing"
body_full: |
  Hi,

  Thank you for your inquiry. Our pricing starts at $500/month.

  Let me know if you have questions.

  Best regards
reply_to: "support@mycompany.com"
created: "2026-01-12T10:30:00Z"
expires: "2026-01-13T10:30:00Z"
status: pending
---

# Reply Email Approval

Replying to pricing inquiry

Move to /Approved to send
```

---

## LinkedIn Post Actions

### Type Identifier
```yaml
type: linkedin_post
```

### Executor
- **Skill:** linkedin-poster
- **Script:** `.claude/skills/linkedin-poster/scripts/linkedin_post.py`
- **Execution:** `python linkedin_post.py --execute-approved <file_path>`

### Required Fields

```yaml
type: linkedin_post             # Action type identifier
action: post_to_linkedin        # Specific action
message: "Post content..."      # Post content (max 3000 chars)
created: "2026-01-12T10:00:00Z" # ISO 8601 timestamp
expires: "2026-01-13T10:00:00Z" # ISO 8601 timestamp
status: pending                 # Always 'pending' for new requests
```

### Optional Fields

```yaml
hashtags: ["BusinessGrowth", "AI"]  # Hashtags (max 3 recommended)
link_url: "https://example.com"     # URL to share
link_title: "Read more"             # Link display title
scheduled_time: "2026-01-13T09:00:00Z"  # Future posting time
visibility: "PUBLIC"                # PUBLIC, CONNECTIONS, or PRIVATE
```

### Validation Rules

1. **Message length:** Max 3000 characters
2. **Hashtags:** Max 3 recommended, 10 absolute max
3. **Links:** Must be valid HTTPS URLs
4. **Visibility:** Must be PUBLIC, CONNECTIONS, or PRIVATE
5. **Content:** Professional tone required

### LinkedIn Best Practices

1. **Optimal length:** 150-300 characters for best engagement
2. **Hashtags:** 2-3 relevant hashtags
3. **Posting time:** Weekdays 7-9 AM, 12-1 PM, 5-6 PM
4. **Content mix:** 80% value, 20% promotion
5. **Engagement:** Ask questions, share insights

### Example Files

**Achievement post:**
```markdown
---
type: linkedin_post
action: post_to_linkedin
message: |
  🎉 Excited to share: We just completed our 100th client project!

  This milestone represents 3 years of dedication to helping businesses automate their workflows with AI.

  Key learnings:
  - Automation increases productivity by 40%
  - Human-in-the-loop is essential for trust
  - Local-first architecture protects privacy

  Grateful for all our clients who trusted us on this journey.

  What's your biggest automation win?
hashtags: ["BusinessGrowth", "AI", "Automation"]
created: "2026-01-12T10:00:00Z"
expires: "2026-01-13T10:00:00Z"
status: pending
---

# LinkedIn Post Approval

Achievement announcement - 100th client project

Move to /Approved to publish
```

**Thought leadership:**
```markdown
---
type: linkedin_post
action: post_to_linkedin
message: |
  The future of work isn't about replacing humans with AI.

  It's about giving every professional a tireless assistant who handles the repetitive tasks, so humans can focus on creativity and strategy.

  I've been testing a "Personal AI Employee" for 3 months:
  - Monitors email and prioritizes urgent items
  - Drafts responses for my review
  - Manages my social media schedule
  - Tracks business metrics

  Result? 10+ hours saved per week.

  The key: Human-in-the-loop approval for everything.

  Are you using AI to augment your work?
hashtags: ["FutureOfWork", "AI"]
link_url: "https://example.com/ai-employee-guide"
link_title: "Building Your AI Employee"
created: "2026-01-12T10:00:00Z"
expires: "2026-01-13T10:00:00Z"
status: pending
---

# LinkedIn Thought Leadership Post

Topic: AI augmentation vs replacement

Move to /Approved to publish
```

---

## Payment Actions (Future - Gold Tier)

### Type Identifier
```yaml
type: payment
```

### Executor
- **Skill:** payment-manager (to be created)
- **Script:** `.claude/skills/payment-manager/scripts/send_payment.py`
- **Execution:** `python send_payment.py --execute-approved <file_path>`

### Required Fields

```yaml
type: payment                   # Action type identifier
action: send_payment            # Specific action
recipient: "Client Name"        # Recipient name
recipient_id: "client_a_001"    # Internal ID
amount: 500.00                  # Amount (decimal)
currency: "USD"                 # ISO 4217 currency code
reference: "Invoice #1234"      # Payment reference
created: "2026-01-12T10:00:00Z" # ISO 8601 timestamp
expires: "2026-01-13T10:00:00Z" # ISO 8601 timestamp (short window!)
status: pending                 # Always 'pending' for new requests
```

### Optional Fields

```yaml
payment_method: "bank_transfer"  # bank_transfer, card, paypal
account_number: "****1234"       # Masked account number
bank_name: "Example Bank"        # Bank name
notes: "January invoice payment" # Internal notes
scheduled_date: "2026-01-15"     # Future payment date
```

### Validation Rules

1. **Amount:** Must be positive, max 2 decimal places
2. **Currency:** Must be valid ISO 4217 code
3. **Recipient:** Must exist in approved payees list
4. **New recipients:** Always require approval
5. **Large amounts:** Threshold defined in Company_Handbook.md
6. **Expiration:** Max 4 hours (payments should be timely)

### Security Requirements

**CRITICAL:** Payment actions require the highest security level:

1. **Short expiration:** Max 4 hours before auto-reject
2. **Verified recipients:** Check against known payees database
3. **Amount limits:** Company_Handbook.md defines thresholds
4. **Two-factor:** Consider requiring 2FA for large amounts
5. **Audit trail:** Complete logging required
6. **Reversibility:** Document reversal process

### Example File

```markdown
---
type: payment
action: send_payment
recipient: "Client A"
recipient_id: "client_a_001"
amount: 500.00
currency: "USD"
payment_method: "bank_transfer"
account_number: "****1234"
bank_name: "First National Bank"
reference: "Invoice #1234"
notes: "January services - approved by email"
created: "2026-01-12T10:00:00Z"
expires: "2026-01-12T14:00:00Z"
status: pending
---

# ⚠️  PAYMENT APPROVAL REQUIRED

**CRITICAL:** This is a real financial transaction.

## Payment Details
- **To:** Client A (client_a_001)
- **Amount:** $500.00 USD
- **Method:** Bank transfer to ****1234 (First National Bank)
- **Reference:** Invoice #1234
- **Reason:** January services - approved by email

## Verification Checklist
- [ ] Recipient is correct (Client A)
- [ ] Amount matches invoice ($500.00)
- [ ] Bank account verified
- [ ] Reference is clear
- [ ] Invoice exists and is unpaid

## To Approve
✅ Move to /Approved

## To Reject
❌ Move to /Rejected with reason

**Expires in 4 hours**
```

---

## File Operation Actions (Future)

### Type Identifier
```yaml
type: file_operation
```

### Potential Actions
- `move_file` - Move files between folders
- `delete_file` - Delete files (requires approval)
- `archive_folder` - Archive old folders

### Example

```markdown
---
type: file_operation
action: delete_file
file_path: "/path/to/old/file.pdf"
reason: "Duplicate file, original exists at /archive/"
created: "2026-01-12T10:00:00Z"
expires: "2026-01-13T10:00:00Z"
status: pending
---

# File Deletion Approval

Deleting: /path/to/old/file.pdf
Reason: Duplicate

Move to /Approved to confirm deletion
```

---

## API Call Actions (Future)

### Type Identifier
```yaml
type: api_call
```

### Potential Actions
- `webhook_call` - Call external webhooks
- `rest_api_post` - POST to external APIs
- `database_update` - Update external databases

---

## Creating New Action Types

### Implementation Checklist

To add a new action type:

1. **Define Schema**
   - Required and optional fields
   - Validation rules
   - Example files

2. **Create Executor Skill**
   - Follow skill-creator pattern
   - Support `--execute-approved` flag
   - Return success/failure status

3. **Update approval-processor**
   - Add to `EXECUTORS` dict in `process_approvals.py`:
   ```python
   EXECUTORS = {
       'email': {...},
       'linkedin_post': {...},
       'your_new_type': {
           'script': Path('...'),
           'arg': '--execute-approved'
       }
   }
   ```

4. **Document**
   - Add section to this file
   - Update SKILL.md
   - Create example files

5. **Test**
   - Create approval request
   - Approve and verify execution
   - Test rejection handling
   - Test expiration

### Validation Template

```python
def validate_action(metadata):
    """Validate action metadata."""
    action_type = metadata.get('type')

    if action_type == 'your_new_type':
        # Required fields
        required = ['field1', 'field2', 'field3']
        for field in required:
            if field not in metadata:
                raise ValueError(f"Missing required field: {field}")

        # Validation logic
        if not is_valid(metadata['field1']):
            raise ValueError(f"Invalid field1: {metadata['field1']}")

        return True

    return False
```

---

## Action Type Registry

| Type | Status | Executor | Priority |
|------|--------|----------|----------|
| `email` | ✅ Implemented | email-sender | High |
| `linkedin_post` | ✅ Implemented | linkedin-poster | High |
| `payment` | ⏳ Gold Tier | payment-manager | Critical |
| `file_operation` | 📋 Planned | file-manager | Medium |
| `api_call` | 📋 Planned | api-manager | Medium |
| `calendar_event` | 📋 Planned | calendar-manager | Low |
| `whatsapp_message` | 📋 Planned | whatsapp-manager | High |

---

**Related Documentation:**
- See `approval_workflow.md` for workflow details
- See `error_recovery.md` for failure handling
- See main `SKILL.md` for usage examples
