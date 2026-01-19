---
name: auto-approver
description: AI-powered auto-approval for pending requests using Claude reasoning. Monitors /Pending_Approval, analyzes each request with Claude AI, makes intelligent approve/reject decisions based on context and Company_Handbook.md rules, and maintains an audit trail of all decisions.
---

# Auto-Approver Skill

## Overview

The **auto-approver** skill uses Claude's AI reasoning to automatically evaluate and approve/reject pending action requests. Unlike rule-based systems, this skill uses actual AI understanding of context, intent, and safety to make intelligent decisions while maintaining a complete audit trail.

## Key Features

- **AI-Powered Decisions**: Claude reads and understands each request, not just pattern matching
- **Context-Aware**: Considers request type, recipient, content, timing, and patterns
- **Safety-First**: errs on the side of human review for uncertain cases
- **Audit Trail**: Logs every decision with full reasoning
- **Learning**: Improves from your corrections and feedback
- **Configurable**: Adjust confidence thresholds and safety levels

## Quick Start

### Monitor and Auto-Approve

```bash
# Run continuously (checks every 30 seconds)
cd .claude/skills/auto-approver
python scripts/auto_approve.py
```

### One-Time Batch Processing

```bash
# Process all pending approvals once
python scripts/auto_approve.py --once
```

### Dry Run (See What Would Be Approved)

```bash
# Analyze and show decisions without executing
python scripts/auto_approve.py --dry-run
```

## How AI Auto-Approval Works

### Decision Process

For each file in `/Pending_Approval`:

1. **Read Request**
   - Parse frontmatter (type, recipient, subject, etc.)
   - Read content body
   - Extract metadata (timestamp, urgency, attachments)

2. **Consult Context**
   - Read `Company_Handbook.md` for rules
   - Check known contacts database
   - Review past approval patterns
   - Consider request history

3. **AI Analysis (Claude)**
   ```
   Analyzing request:
   - Type: email reply
   - Recipient: boss@company.com (known contact: 45 interactions)
   - Subject: Weekly Report Attached
   - Content: Status report with metrics

   Context:
   - Routine weekly email (pattern: every Monday)
   - No sensitive information
   - Standard business communication
   - Recipient verified in 15 previous approvals

   Company_Handbook Rules:
   - "Email replies to known contacts" → Can auto-approve
   - "No financial/legal commitments" → Safe
   - "Routine business communication" → Safe

   Decision: ✅ APPROVE
   Confidence: 95%
   Reasoning: This is a routine weekly status report to a known verified contact.
   ```

4. **Make Decision**
   - **Approve**: Move to `/Approved`, log reasoning
   - **Reject**: Move to `/Rejected`, explain why
   - **Hold**: Keep in `/Pending_Approval`, flag for human review

5. **Audit Log**
   - Save decision with full AI reasoning
   - Track confidence score
   - Record timestamp and outcome

## Auto-Approval Criteria

### ✅ Auto-Approve When

**Email:**
- Recipient is known contact (5+ previous interactions)
- Is a reply (not new conversation)
- Content is routine business communication
- No sensitive/controversial topics
- Matches established patterns

**Social Media:**
- Pre-scheduled post
- Content is professional/appropriate
- No controversial topics
- Platform approved in Company_Handbook

**File Operations:**
- Reading files
- Creating plans/drafts
- Moving to `/Done` folder

### ❌ Require Human Review When

**Any Request With:**
- New contact (first interaction)
- Financial transactions/payments
- Legal commitments/contracts
- Sensitive personal information
- Controversial topics
- Bulk operations
- High urgency flag
- Attachments (unless verified safe)

## Configuration

### Settings

**File:** `config/config.json`

```json
{
  "check_interval": 30,
  "confidence_threshold": 0.85,
  "dry_run": false,
  "learn_from_corrections": true,
  "rules": {
    "email": {
      "known_contact_threshold": 5,
      "pattern_match_required": true,
      "max_recipients": 1
    },
    "social_media": {
      "scheduled_only": true,
      "controversial_keywords": ["politics", "religion"],
      "max_posts_per_day": 3
    },
    "payments": {
      "auto_approve": false,
      "max_amount": 0
    }
  }
}
```

### Known Contacts

**File:** `config/known_contacts.json`

```json
{
  "contacts": {
    "boss@company.com": {
      "name": "John Smith",
      "interactions": 45,
      "first_approved": "2025-12-01",
      "last_approved": "2026-01-19",
      "trust_score": 0.98,
      "typical_content": ["weekly reports", "status updates"]
    },
    "client@business.com": {
      "name": "ABC Client",
      "interactions": 12,
      "first_approved": "2026-01-10",
      "last_approved": "2026-01-18",
      "trust_score": 0.85,
      "typical_content": ["project updates", "invoices"]
    }
  }
}
```

## Usage Examples

### Example 1: Auto-Approve Routine Email

**Input:** `/Pending_Approval/EMAIL_2026-01-19T10-00-00.md`

```yaml
---
type: email
recipient: boss@company.com
subject: Weekly Report Attached
---
Hi Boss,

Please find attached the weekly status report.
All metrics are on track.

Best,
AI Employee
```

**AI Analysis:**
```
✅ Known contact: boss@company.com (45 interactions)
✅ Routine pattern: Weekly reports (every Monday)
✅ Safe content: Status update, no sensitive info
✅ No attachments requiring review

Decision: APPROVE (Confidence: 96%)
Reasoning: Routine weekly status report to verified known contact.
```

**Action:** Move to `/Approved`, log decision

### Example 2: Hold for Human Review

**Input:** `/Pending_Approval/EMAIL_2026-01-19T11-30-00.md`

```yaml
---
type: email
recipient: new-vendor@unknown.com
subject: URGENT: Invoice Payment $5000
---
Please approve urgent payment for new vendor.
```

**AI Analysis:**
```
❌ Unknown contact: new-vendor@unknown.com (0 interactions)
❌ Financial transaction: $5000 payment request
❌ High urgency: URGENT flag
❌ New vendor: No payment history

Decision: HOLD for human review (Confidence: 99% that review needed)
Reasoning: New vendor payment request requires human verification.
```

**Action:** Keep in `/Pending_Approval`, add flag `⚠️ Awaiting Human Review`

## Scripts

### auto_approve.py

Main script for monitoring and auto-approving.

**Usage:**
```bash
# Continuous monitoring
python scripts/auto_approve.py

# One-time processing
python scripts/auto_approve.py --once

# Dry run (no changes)
python scripts/auto_approve.py --dry-run

# Verbose output
python scripts/auto_approve.py --verbose
```

**Features:**
- Monitors `/Pending_Approval` every 30 seconds
- Analyzes each request with AI
- Makes approve/reject/hold decisions
- Logs all decisions to `/Logs/auto_approver_YYYY-MM-DD.json`
- Tracks approval patterns for learning

### decision_analyzer.py

AI-powered analysis engine.

**Usage:**
```bash
# Analyze single file
python scripts/decision_analyzer.py /path/to/request.md

# Show reasoning
python scripts/decision_analyzer.py /path/to/request.md --explain
```

**Features:**
- Reads request content and metadata
- Consults Company_Handbook.md rules
- Checks known contacts database
- Evaluates safety and context
- Returns decision with confidence and reasoning

### learn_from_corrections.py

Learns from your manual overrides.

**Usage:**
```bash
# Learn from recent corrections
python scripts/learn_from_corrections.py

# Show learning summary
python scripts/learn_from_corrections.py --summary
```

**Features:**
- Detects when you override AI decision
- Updates known contacts database
- Adjusts confidence thresholds
- Improves pattern recognition

## Audit Trail

All decisions logged to: `/Logs/auto_approver_YYYY-MM-DD.json`

```json
{
  "timestamp": "2026-01-19T10:05:00Z",
  "request_file": "EMAIL_2026-01-19T10-00-00.md",
  "decision": "approve",
  "confidence": 0.96,
  "reasoning": "Routine weekly status report to verified known contact with 45 previous interactions.",
  "context": {
    "type": "email",
    "recipient": "boss@company.com",
    "known_contact": true,
    "interactions": 45,
    "trust_score": 0.98
  },
  "action_taken": "moved to /Approved"
}
```

## Safety Features

### Confidence Threshold

Default: **0.85** (85% confident)

- If AI confidence < 85% → **HOLD for human review**
- You can adjust this in `config/config.json`

### Err on Caution

When uncertain:
- Always defaults to **human review**
- Never approves financial transactions
- Never approves new contacts on first interaction
- Flags controversial content immediately

### Emergency Stop

```bash
# Stop auto-approver immediately
echo "stop" > /tmp/auto_approver_stop

# Resume
rm /tmp/auto_approver_stop
```

## Integration with Other Skills

### approval-processor

Auto-approver **feeds into** approval-processor:
1. Auto-approver decides → `/Approved`
2. approval-processor executes → `/Done`

### email-sender / linkedin-poster

Auto-approver makes decisions **before** these skills execute:
1. Create request → `/Pending_Approval`
2. Auto-approver evaluates → `/Approved` or `/Rejected`
3. email-sender executes (if approved)

## Configuration Examples

### Conservative (Safe)

```json
{
  "confidence_threshold": 0.95,
  "rules": {
    "email": {
      "known_contact_threshold": 10,
      "auto_approve_replies": false
    }
  }
}
```

### Balanced (Recommended)

```json
{
  "confidence_threshold": 0.85,
  "rules": {
    "email": {
      "known_contact_threshold": 5,
      "auto_approve_replies": true
    }
  }
}
```

### Aggressive (Fast)

```json
{
  "confidence_threshold": 0.70,
  "rules": {
    "email": {
      "known_contact_threshold": 3,
      "auto_approve_replies": true
    }
  }
}
```

## Monitoring

### Check Auto-Approver Status

```bash
# Show statistics
python scripts/check_status.py

# Output:
📊 Auto-Approver Status

Today's Decisions:
  Approved: 23
  Rejected: 3
  Held for Review: 5

Success Rate: 82%
Average Confidence: 89%

Top Approved Contacts:
  - boss@company.com: 15 approvals
  - team@company.com: 8 approvals
```

## Troubleshooting

### Auto-Approver Not Running

Check logs:
```bash
tail -f Logs/auto_approver_*.log
```

### Too Many Holds for Review

Lower confidence threshold:
```json
{
  "confidence_threshold": 0.75  // was 0.85
}
```

### False Approvals (Should Have Been Reviewed)

Raise threshold:
```json
{
  "confidence_threshold": 0.95  // was 0.85
}
```

## Best Practices

1. **Start Conservative**: Use 0.95 threshold initially
2. **Monitor Daily**: Review approved decisions first week
3. **Provide Feedback**: Override decisions when wrong
4. **Update Handbook**: Add rules as patterns emerge
5. **Trust But Verify**: Check logs weekly

## Version History

**v1.0.0** (2026-01-19)
- Initial AI-powered auto-approver
- Claude reasoning integration
- Known contacts tracking
- Audit trail
- Learning from corrections

---

**Status:** Production Ready
**Confidence:** High
**Safety:** Human-in-the-loop for uncertain cases
