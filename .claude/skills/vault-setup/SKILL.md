---
name: vault-setup
description: Initialize and manage Obsidian vault structure for Personal AI Employee. Use when the user needs to set up the vault structure, create foundational folders, or initialize Dashboard.md and Company_Handbook.md templates. Triggers include "set up vault", "create vault structure", "initialize AI employee vault", "create folders", or "setup obsidian structure".
---

# Vault Setup

## Overview

This skill initializes the complete folder structure and foundational templates for the Personal AI Employee Obsidian vault. It creates all necessary folders, generates Dashboard.md and Company_Handbook.md templates, and validates the vault structure.

## Core Workflow

### 1. Create Folder Structure

Create these folders in the vault root:

```
/Inbox              - Drop zone for new items to be processed
/Needs_Action       - Tasks waiting to be processed by Claude
/Plans              - Generated action plans
/Pending_Approval   - Items awaiting human approval
/Approved           - Approved actions ready for execution
/Rejected           - Rejected actions
/Done               - Completed and archived tasks
/Logs               - Audit logs and system logs
/watchers           - Python watcher scripts
```

Use the script `scripts/create_folders.py` to create all folders at once.

### 2. Initialize Dashboard.md

Create Dashboard.md in the vault root using the template in `references/dashboard_template.md`. The dashboard provides real-time status overview.

### 3. Initialize Company_Handbook.md

Create Company_Handbook.md in the vault root using the template in `references/handbook_template.md`. This contains rules of engagement and operational guidelines.

### 4. Validate Structure

After setup, verify all folders exist and templates are created correctly.

## Usage

**To set up a new vault:**
1. Run `python scripts/create_folders.py` to create folder structure
2. Review references/dashboard_template.md and create Dashboard.md
3. Review references/handbook_template.md and create Company_Handbook.md
4. Confirm all folders exist

**To validate existing vault:**
- Check that all required folders exist
- Verify Dashboard.md and Company_Handbook.md are present
- Ensure proper folder permissions

## Resources

### scripts/create_folders.py
Python script to create all required folders in the vault structure.

### references/dashboard_template.md
Complete template for Dashboard.md with all sections.

### references/handbook_template.md
Complete template for Company_Handbook.md with example rules.
