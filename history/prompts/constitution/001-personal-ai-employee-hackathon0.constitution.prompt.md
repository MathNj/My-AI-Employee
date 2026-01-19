---
id: 001
title: Personal AI Employee Hackathon0 Constitution
stage: constitution
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: Najma-LP
command: /sp.constitution
labels: ["constitution", "hackathon", "governance", "principles", "agents", "skills", "mcp"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md (Version 1.0.0 - 8 core principles, governance, versioning)
tests:
  - Constitution principles validated against Requirements2.md
  - All 8 core principles mapped to hackathon requirements
  - Sync Impact Report generated for template updates
---

## Prompt

Read and understand @Requirements2.md and all work we have done, mentian agents and skills and their purproses according to requirements. make constitution for the Hacathone

## Response snapshot

Created comprehensive constitution for Personal AI Employee Hackathon 0 project (Version 1.0.0):

**Constitution File**: .specify/memory/constitution.md

**8 Core Principles Established**:

1. **I. Local-First & Data Sovereignty**: All data, state, and processing MUST reside on local storage (Obsidian vault). No cloud dependencies except API calls to external services (Gmail, Xero, LinkedIn, Slack, WhatsApp, Google Calendar). User retains full ownership and control.

2. **II. Agent Skills Architecture (MCP Integration)**: All AI functionality MUST be implemented as Agent Skills (SKILL.md files in `.claude/commands/` directory). Skills expose tools for Claude Code to invoke. Complex functionality builds on Model Context Protocol (MCP) servers for external actions.

3. **III. Multi-Tier Incremental Architecture**: System MUST follow tiered progression: Bronze (8-12 hours) → Silver (20-30 hours) → Gold (40+ hours) → Platinum (60+ hours). Each tier validates architectural principles before scaling. Gold Tier is minimum viable Digital FTE. Platinum adds cloud+local hybrid.

4. **IV. Watcher Pattern: Perception → Action File → Reasoning → Action**: All system perception MUST follow Watcher Pattern: Watcher detects event → Create Action File (/Inbox → /Needs_Action → /Done) → Claude Code reads via Agent Skills → Reasoning → Action via MCP servers. No bypassing Action File workflow.

5. **V. File-Based State Management**: All system state (except ephemeral process state) MUST be stored as files in Obsidian vault. No database for Bronze/Silver/Gold tiers. PostgreSQL only in Platinum Tier for cloud component. State files: watchers_state.json, audit_*.json, scheduled_tasks_*.log, actions_*.json.

6. **VI. Human-in-the-Loop Approval Workflow**: All sensitive actions (emails, social media posts, financial transactions >$100, data deletion) MUST route through human approval workflow: /Pending_Approval → /Approved → /Rejected → /Done. Approval files include risk_level, deadline, potential_impact, reasoning.

7. **VII. Ralph Wiggum Autonomous Loop (Stop Hook Pattern)**: For complex multi-step tasks, Claude Code MUST iterate autonomously until all tasks complete. Stop hook pattern: after each action, check if work remains; if yes, continue; if no, exit. Ralph Loop continues until user intervenes or all tasks done.

8. **VIII. MCP Server External Action Layer**: All external actions (send email, post to social media, query accounting, calendar ops) MUST execute via Model Context Protocol (MCP) servers. MCP servers provide tools with defined schemas: send_email, post_linkedin, xero_query, calendar_create, slack_send, whatsapp_send.

**Additional Constraints**:
- Security & Privacy: API credentials in .env files (never committed). OAuth 2.0 for third-party services. Data encryption at rest. Audit logging for all actions.
- Performance & Scalability: Watchers poll every 5 minutes. CPU usage <30%. Multi-watcher deduplication. State rotation to prevent bloat.
- Error Handling & Recovery: Retry logic with exponential backoff. Deadlock prevention. Graceful degradation. Health monitoring.
- Platform & Compatibility: Windows (PowerShell, Task Scheduler), Linux/macOS (cron, bash). Cross-platform path handling.
- File Organization: Obsidian vault as single source of truth. /Inbox, /Needs_Action, /Done, /Pending_Approval, /Approved, /Rejected, /Scheduled, /Plans folders.

**Governance Model**:
- Amendment Procedure: Requires 2/3 majority vote and documented ADR
- Versioning Policy: MAJOR.MINOR.PATCH (1.0.0 initial)
- Compliance Review: Quarterly audits against constitution principles
- Review Process: ADR required for significant architectural decisions

**Sync Impact Report** (HTML comment):
- Templates requiring updates flagged: plan.md, spec.md, tasks.md, README.md, .specify/templates/commands/*.md

## Outcome

- ✅ Impact: Comprehensive constitution (Version 1.0.0) established for Personal AI Employee Hackathon 0 project. Defines 8 core principles derived from Requirements2.md: Local-First, Agent Skills Architecture, Multi-Tier Incremental, Watcher Pattern, File-Based State, Approval Workflow, Ralph Wiggum Loop, MCP External Action Layer. Establishes governance model with amendment procedure, versioning policy (MAJOR.MINOR.PATCH), and compliance review. Ratified 2026-01-17.
- 🧪 Tests: Constitution principles validated against Requirements2.md. All 8 core principles mapped to hackathon requirements (agents, skills, MCP, watchers, tiers, approval workflow, Ralph Loop, file-based state). Sync Impact Report generated identifying templates requiring updates to align with constitutional principles.
- 📁 Files: Created .specify/memory/constitution.md (Version 1.0.0) with complete governance model, 8 principles, additional constraints, versioning policy, compliance review procedure.
- 🔁 Next prompts: Update identified templates (plan.md, spec.md, tasks.md, README.md) to align with constitutional principles. Propagate constitutional constraints to all tier specifications. Ensure all PHRs reference constitution as governing document.
- 🧠 Reflection: Constitution successfully captures architectural principles from Requirements2.md while providing governance framework for hackathon project. Key achievement: establishing Agent Skills as primary AI abstraction (all functionality as SKILL.md files) with MCP servers for external actions. File-based state management continues from Bronze tier simplicity while providing scalability path to Platinum tier's PostgreSQL cloud component. Human-in-the-loop approval workflow ensures safety for sensitive actions. Ralph Wiggum autonomous loop provides transparent multi-step reasoning. Multi-tier incremental architecture ensures each tier validates principles before scaling. Recommendation: Sync constitution principles with existing Bronze/Silver/Gold specifications before implementation begins.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution creation successful. PHR creation initially failed due to missing file_path parameter, resolved by providing explicit file path.
- Graders run and results (PASS/FAIL): Constitution Validation - PASSED (8 core principles defined, all mapped to Requirements2.md). Governance Model - COMPLETE (amendment procedure, versioning policy, compliance review defined). Sync Impact Report - GENERATED (5 templates flagged for updates). Requirements Coverage - COMPLETE (agents, skills, MCP, watchers, tiers, approval, Ralph Loop, file-based state all addressed).
- Prompt variant (if applicable): Standard /sp.constitution workflow with user input specifying: "Read and understand @Requirements2.md and all work we have done, mentian agents and skills and their purproses according to requirements. make constitution for the Hacathone". Successfully interpreted intent to create comprehensive constitutional document for hackathon project with emphasis on agents and skills architecture.
- Next experiment (smallest change to try): For future constitution creation, consider adding "Compliance Checklist" section with automated validation rules (e.g., "All Agent Skills MUST have SKILL.md file", "All external actions MUST route through MCP servers", "All sensitive actions MUST require approval"). Current constitution provides principles but no automated compliance checking. Alternative: Create "Constitution Tests" section with pytest tests to validate compliance (e.g., test_all_agents_have_skill_files(), test_all_actions_via_mcp(), test_approval_workflow_for_sensitive_actions()).
