---
name: ralph-converter
description: "Convert PRD markdown files to prd.json format for Ralph Loop execution. Use when you have a PRD and need to convert it to Ralph's JSON format. Triggers: convert this prd, turn into ralph format, create prd.json, ralph json from prd."
---

# Ralph Converter - PRD to JSON

Converts markdown PRDs into the prd.json format that Ralph Loop uses for autonomous execution.

---

## What It Does

Takes a markdown PRD and converts it to structured JSON with:
- Sequential user story IDs
- Priority ordering
- All stories marked as `passes: false`
- Proper branch naming
- Verifiable acceptance criteria

**Input:** `prd-{feature}.md` (markdown)
**Output:** `prd.json` (JSON for Ralph Loop)

---

## Usage

```bash
/ralph-converter "AI_Employee_Vault/Ralph/tasks/prd-email-workflow.md"
```

The skill will:
1. Read the markdown PRD
2. Extract user stories
3. Convert to JSON format
4. Archive previous prd.json (if different feature)
5. Save new prd.json
6. Reset progress.txt for new run

---

## Output Format

```json
{
  "project": "AI Employee",
  "branchName": "ralph/feature-name",
  "description": "[Feature description from PRD]",
  "userStories": [
    {
      "id": "US-001",
      "title": "[Story title]",
      "description": "As [user], I want [feature] so that [benefit]",
      "acceptanceCriteria": [
        "Criterion 1",
        "Criterion 2",
        "Criterion 3"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

---

## Conversion Rules

### 1. Project Name
Always: `"AI Employee"`

### 2. Branch Name
Format: `"ralph/{feature-name}"`

Derived from PRD filename:
- `prd-email-workflow.md` → `"ralph/email-workflow"`
- `prd-whatsapp-responder.md` → `"ralph/whatsapp-responder"`

### 3. Description
First paragraph of PRD Introduction section.

### 4. User Stories

Each `### US-XXX:` section becomes one JSON entry:

**From PRD:**
```markdown
### US-001: Create email approval request structure
**Description:** As the AI Employee, I need to create structured approval requests.

**Acceptance Criteria:**
- [ ] Create template in /Pending_Approval
- [ ] Include frontmatter fields
- [ ] Add approval instructions
```

**To JSON:**
```json
{
  "id": "US-001",
  "title": "Create email approval request structure",
  "description": "As the AI Employee, I need to create structured approval requests.",
  "acceptanceCriteria": [
    "Create template in /Pending_Approval",
    "Include frontmatter fields",
    "Add approval instructions"
  ],
  "priority": 1,
  "passes": false,
  "notes": ""
}
```

### 5. IDs
Sequential: US-001, US-002, US-003, etc.

### 6. Priority
Based on document order (1 = first story, 2 = second, etc.)

### 7. Initial Status
All stories: `"passes": false`, `"notes": ""`

---

## Story Size Validation

The converter checks that each story is appropriately sized for one Ralph iteration.

### Right-sized ✅
- 2-4 acceptance criteria
- Focused on 1-3 file changes
- Clear, verifiable outcomes

### Too large ❌
- > 6 acceptance criteria
- Multiple integration points
- Vague or broad scope

**If too large:** The converter warns you and suggests splitting the story.

---

## Acceptance Criteria Validation

The converter ensures criteria are verifiable, not vague.

### Good criteria ✅
- Includes specific file paths
- Mentions exact fields/formats
- References integration points
- Clear success conditions

### Bad criteria ❌
- "Works correctly"
- "Good performance"
- "User-friendly"
- "Handles edge cases"

**If too vague:** The converter warns you and suggests more specific wording.

---

## Archiving Previous Runs

Before writing a new prd.json, the converter checks if there's an existing one from a different feature.

**Archive process:**
1. Read current prd.json (if exists)
2. Check if `branchName` differs from new feature
3. If different AND progress.txt has content:
   - Create: `archive/YYYY-MM-DD-{old-feature-name}/`
   - Copy: prd.json and progress.txt to archive
   - Reset: progress.txt with fresh header

**This prevents losing work from previous Ralph runs.**

---

## Example Conversion

### Input: `prd-email-workflow.md`

```markdown
# PRD: Email Approval Workflow

## Introduction
Implement HITL approval workflow for email sending.

## User Stories

### US-001: Create email approval request structure
**Description:** As the AI Employee, I need to create structured approval requests.

**Acceptance Criteria:**
- [ ] Create EMAIL_APPROVAL_template.md in /Pending_Approval
- [ ] Include frontmatter: type, status, created, expires, email_to
- [ ] Include email body preview section
- [ ] Add approval instructions

### US-002: Monitor Approved folder
**Description:** As the AI Employee, I need to detect approvals.

**Acceptance Criteria:**
- [ ] Create monitoring script in email-sender skill
- [ ] Check /Approved folder every 10 seconds
- [ ] Parse EMAIL_APPROVAL_*.md frontmatter
- [ ] Validate expiration time
```

### Output: `prd.json`

```json
{
  "project": "AI Employee",
  "branchName": "ralph/email-workflow",
  "description": "Implement HITL approval workflow for email sending.",
  "userStories": [
    {
      "id": "US-001",
      "title": "Create email approval request structure",
      "description": "As the AI Employee, I need to create structured approval requests.",
      "acceptanceCriteria": [
        "Create EMAIL_APPROVAL_template.md in /Pending_Approval",
        "Include frontmatter: type, status, created, expires, email_to",
        "Include email body preview section",
        "Add approval instructions"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-002",
      "title": "Monitor Approved folder",
      "description": "As the AI Employee, I need to detect approvals.",
      "acceptanceCriteria": [
        "Create monitoring script in email-sender skill",
        "Check /Approved folder every 10 seconds",
        "Parse EMAIL_APPROVAL_*.md frontmatter",
        "Validate expiration time"
      ],
      "priority": 2,
      "passes": false,
      "notes": ""
    }
  ]
}
```

---

## Workflow

### 1. Create PRD
```bash
/prd "Email approval workflow"
```
Output: `AI_Employee_Vault/Ralph/tasks/prd-email-workflow.md`

### 2. Convert to JSON
```bash
/ralph-converter "AI_Employee_Vault/Ralph/tasks/prd-email-workflow.md"
```
Output: `AI_Employee_Vault/Ralph/prd.json`

### 3. Run Ralph Loop
```bash
/ralph-loop --max-iterations 10
```
Ralph reads prd.json and executes stories.

---

## Validation Checks

The converter performs these validations:

### Structure Checks ✅
- PRD has user stories section
- Each story has description
- Each story has acceptance criteria
- Story IDs are sequential

### Size Checks ✅
- Stories have 2-6 acceptance criteria
- Descriptions are < 200 characters
- Titles are < 80 characters

### Content Checks ✅
- Criteria are specific (mention files/paths)
- No vague terms ("good", "easily", "correctly")
- Proper "As [user], I want [feature]" format

### Ordering Checks ✅
- Stories ordered by dependencies
- No later story depends on earlier story

**If validation fails:** The converter shows warnings and suggestions.

---

## Special Handling

### Long Descriptions
If story description > 200 chars:
- Truncate to first sentence
- Add full description to `notes` field

### Missing Story IDs
If PRD doesn't use US-XXX format:
- Auto-generate IDs based on position
- Warn user to update PRD format

### Duplicate IDs
If PRD has duplicate US-XXX:
- Renumber sequentially
- Warn user about duplicates

---

## Output Location

Writes to: `AI_Employee_Vault/Ralph/prd.json`

**Why this location:**
- Ralph Loop looks here by default
- Keeps all Ralph files together
- Easy to find and edit

---

## Manual Editing

After conversion, you can manually edit prd.json:

```json
{
  "userStories": [
    {
      "id": "US-001",
      "priority": 1,    // Change priority order
      "passes": false,  // Reset if you want to re-run
      "notes": "Started but needs retry"  // Add notes
    }
  ]
}
```

**Then re-run Ralph:**
```bash
/ralph-loop
```

Ralph will pick up from where you modified.

---

## Checklist Before Converting

Before running the converter, verify your PRD has:

- [ ] User Stories section with ### US-XXX: headers
- [ ] Each story has **Description:** line
- [ ] Each story has **Acceptance Criteria:** list
- [ ] Criteria are specific (mention files, paths, formats)
- [ ] Stories ordered by dependencies
- [ ] Each story is small enough for one iteration
- [ ] No vague terms in acceptance criteria

---

## Troubleshooting

### Converter can't find user stories

**Symptom:** Error: "No user stories found in PRD"

**Fix:** Ensure PRD has section headers:
```markdown
## User Stories

### US-001: Story Title
**Description:** ...
**Acceptance Criteria:**
- [ ] ...
```

### Stories marked too large

**Symptom:** Warning: "US-003 has too many acceptance criteria"

**Fix:** Split story into multiple smaller stories:
- US-003a: Part 1
- US-003b: Part 2

### Vague criteria warnings

**Symptom:** Warning: "Criterion 'Works correctly' is too vague"

**Fix:** Make specific:
- ❌ "Works correctly"
- ✅ "Creates file in /Done with proper frontmatter"

### Previous prd.json overwritten

**Symptom:** Lost previous Ralph run data

**Fix:** Check archive folder:
```bash
ls AI_Employee_Vault/Ralph/archive/
```

Previous runs are automatically archived there.

---

## Integration

Works seamlessly with:
- **prd-generator**: Creates the markdown PRD
- **ralph-loop**: Executes the prd.json
- **task-processor**: Processes individual tasks
- **plan-generator**: Creates execution plans from PRD

---

## Files Created/Modified

```
AI_Employee_Vault/Ralph/
├── prd.json                   # Main output (created/updated)
├── progress.txt               # Reset if new feature
└── archive/                   # Previous runs
    └── YYYY-MM-DD-old-feature/
        ├── prd.json          # Archived previous PRD
        └── progress.txt      # Archived previous progress
```

---

## Advanced: Manual prd.json Creation

You can create prd.json manually without a PRD:

```json
{
  "project": "AI Employee",
  "branchName": "ralph/my-feature",
  "description": "My feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "First task",
      "description": "As a user, I want X so that Y",
      "acceptanceCriteria": [
        "Specific criterion 1",
        "Specific criterion 2"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

Then run Ralph:
```bash
/ralph-loop
```

---

## Best Practices

### 1. Use the Full Workflow
PRD → Converter → Ralph Loop (don't skip PRD step)

### 2. Review Before Converting
Read the PRD carefully, ensure stories are properly sized

### 3. Check Validation Warnings
Don't ignore warnings - they prevent Ralph failures

### 4. Archive Intentionally
Let the converter archive automatically, don't delete old runs

### 5. Version Control
Commit prd.json and PRD files to git for history

---

## References

- See prd-generator skill for creating PRDs
- See ralph-loop skill for executing prd.json
- See Requirements1.md for Ralph Wiggum pattern
- See original ralph-main/skills/ralph/SKILL.md for advanced options

---

**Status:** Ready to use
**Integration:** Bridges prd-generator and ralph-loop
**Output:** prd.json in AI_Employee_Vault/Ralph/
