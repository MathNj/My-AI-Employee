---
id: 001
title: Gold Tier Implementation Plan
stage: plan
date: 2026-01-17
surface: agent
model: claude-sonnet-4-5
feature: 002-gold-tier-ai-employee
branch: 002-gold-tier-ai-employee
user: Najma-LP
command: /sp.plan
labels: ["gold-tier", "plan", "architecture", "implementation", "orchestrator", "mcp"]
links:
  spec: specs/002-gold-tier-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-gold-tier-ai-employee/plan.md (comprehensive implementation plan with 10 research decisions, 7-phase sequence)
  - specs/002-gold-tier-ai-employee/research.md (technology decisions with rationale and alternatives)
  - specs/002-gold-tier-ai-employee/data-model.md (entity definitions, relationships, validation rules)
  - specs/002-gold-tier-ai-employee/quickstart.md (setup guide with 7 phases)
  - specs/002-gold-tier-ai-employee/contracts/gmail-mcp-schema.json (Gmail MCP tool schema)
  - specs/002-gold-tier-ai-employee/contracts/xero-mcp-schema.json (Xero MCP tool schemas)
  - specs/002-gold-tier-ai-employee/contracts/linkedin-mcp-schema.json (LinkedIn MCP tool schema)
  - specs/002-gold-tier-ai-employee/contracts/x-poster-mcp-schema.json (Twitter/X MCP tool schema)
  - specs/002-gold-tier-ai-employee/contracts/facebook-mcp-schema.json (Facebook MCP tool schema)
  - specs/002-gold-tier-ai-employee/contracts/instagram-mcp-schema.json (Instagram MCP tool schema)
tests:
  - Constitution Check: PASSED (all 8 principles satisfied)
  - Research Decisions: COMPLETE (10 technology decisions documented)
  - Data Model: COMPLETE (6 entity definitions with validation rules)
  - MCP Contracts: COMPLETE (6 MCP server schemas with tool definitions)
  - Implementation Sequence: COMPLETE (7 phases, 40-50 hours estimated)
---

## Prompt

for Gold Tier

## Response snapshot

Created comprehensive Gold Tier implementation plan with architectural foundation:

**Implementation Plan**: specs/002-gold-tier-ai-employee/plan.md

**Gold Tier Scope - Autonomous Employee (40+ hours)**:

**Core Enhancements Over Silver Tier**:

1. **6+ Coordinated Watchers**: Gmail (2 min), WhatsApp (30 sec), Xero (5 min), Calendar (10 min), Slack (1 min), Filesystem (real-time)
2. **6+ MCP Servers**: Gmail send, Xero read/write, LinkedIn post, X/Twitter post, Facebook post, Instagram post
3. **Orchestrator + Watchdog**: Master process management with health monitoring and auto-restart
4. **Ralph Wiggum Loop**: Autonomous multi-step task completion with Stop hook pattern
5. **CEO Briefing**: Weekly Sunday 7 AM autonomous business audit and proactive recommendations
6. **Comprehensive Audit Logging**: 90-day structured JSON audit trail for all actions
7. **Cross-Domain Event Correlation**: Consolidate related events across watchers into unified plans

**Technical Stack**:
- **Orchestration**: Python 3.13+ (orchestrator.py, watchdog.py, 6 watcher scripts)
- **MCP Servers**: Node.js v24+ LTS with TypeScript SDK (6 servers)
- **Browsers**: Playwright for WhatsApp, Twitter/X (visible mode, persistent sessions)
- **Storage**: File-based (Obsidian vault markdown + JSON logs) - no database
- **Scheduling**: OS-native (cron/Task Scheduler) for CEO briefing and log rotation

**Phase 0 Research - 10 Technology Decisions** (documented in research.md):
1. Orchestrator Architecture: Independent Python processes (not threads) for process isolation
2. Watchdog Pattern: Separate watchdog.py process monitors orchestrator, restarts if crashed
3. Ralph Wiggum Stop Hook: File movement completion strategy (check if file moved to /Done)
4. Cross-Domain Event Correlation: Batch consolidation during Claude Code processing
5. MCP Server Communication: stdio (subprocess) for Gold tier, HTTP reserved for Platinum
6. Xero Token Refresh: Proactive refresh 5 minutes before 30-minute expiry
7. CEO Briefing Data Sources: Query live data from Xero API and scan /Done folder
8. Social Media Posting: Single unified approval file with platform-specific sections
9. WhatsApp Session Persistence: Persistent browser profile with QR scan only on first run
10. Audit Log Retention: Daily rotation with 90-day retention (separate file per day)

**Architecture Validation Principles** (7 principles to prove):
1. Multi-watcher coordination: 6 watchers concurrent without interference
2. Process isolation: Watcher crash doesn't affect other watchers or orchestrator
3. MCP server scalability: 6 servers work concurrently, adding more is straightforward
4. Ralph loop autonomy: Multi-step tasks complete without additional human prompts
5. CEO briefing value: Weekly business audit identifies cost optimizations and bottlenecks
6. Audit logging completeness: 100% of actions logged with searchable JSON trail
7. Orchestrator reliability: 99%+ uptime over 7-day period with auto-restart

**Constraints** (Gold tier limits):
- Exactly 6 watchers (not 2 - Silver tier, not 10+ - Platinum tier)
- Exactly 6 MCP servers (not 1 - Silver tier, not 10+ - Platinum tier)
- Local-only architecture (no cloud deployment - Platinum tier feature)
- File-based state (no database - Platinum tier may add PostgreSQL)
- No Agent-to-Agent (A2A) communication (reserved for Platinum tier)

**Upgrade Path to Platinum Tier**:
- Cloud deployment (24/7 cloud VM with always-on watchers)
- Work-zone specialization (Cloud: drafts, Local: approvals/executions)
- Vault synchronization (Git or Syncthing between Cloud and Local)
- Claim-by-move rule (/In_Progress/<agent>/ prevents double-work)
- Odoo Community ERP (self-hosted local accounting)
- A2A communication (optional Phase 2 upgrade)

**Implementation Sequence** (7 phases, 40-50 hours):
1. Orchestrator & Watchdog Foundation (6-8 hours) - Launch and monitor 6 watchers
2. Complete All 6 Watchers (10-12 hours) - Gmail, WhatsApp, Xero, Calendar, Slack, Filesystem
3. Implement 6 MCP Servers (12-15 hours) - Gmail, Xero, LinkedIn, Twitter, Facebook, Instagram
4. Ralph Wiggum Loop Implementation (4-5 hours) - Stop hook with completion detection
5. CEO Briefing Generator (5-6 hours) - Weekly Sunday 7 AM business audit
6. Comprehensive Audit Logging (3-4 hours) - 90-day structured JSON audit trail
7. Polish & Documentation (5-6 hours) - End-to-end testing, demo video, upgrade guide

**Constitution Check Result**: ✅ ALL PRINCIPLES SATISFIED (no violations)

## Outcome

- ✅ Impact: Comprehensive Gold Tier implementation plan created with architectural foundation, 10 technology research decisions, 7-phase implementation sequence (40-50 hours). Builds incrementally on Silver Tier (feature 001) with orchestrator + watchdog, 6 coordinated watchers, 6 MCP servers, Ralph Wiggum autonomous loop, CEO briefing, and comprehensive audit logging. All constitutional principles validated without violations.
- 🧪 Tests: Constitution Check PASSED (8 principles validated: local-first, Agent Skills, multi-tier incremental, Watcher pattern, file-based state, approval workflow, Ralph loop, MCP external action). Architecture Validation Principles DEFINED (7 principles to prove in Gold tier). Success Criteria mapped with implementation strategies (28 success criteria from spec.md).
- 📁 Files: Created specs/002-gold-tier-ai-employee/plan.md with comprehensive technical context, research decisions, project structure, implementation sequence, risk mitigation, upgrade path to Platinum tier. Created research.md with 10 technology decisions (rationale, alternatives, implementation). Created data-model.md with 6 entity definitions (Action File, Approval Request, Plan, Audit Log Entry, Watcher Process, Business Goal). Created quickstart.md with 7-phase setup guide. Created 6 MCP server schema files (contracts/).
- 🔁 Next prompts: /sp.tasks (generate detailed task breakdown), then implement following 7-phase sequence, validate success criteria, record demo video.
- 🧠 Reflection: Gold Tier plan successfully scales from Silver tier's 2 watchers + 1 MCP server to 6 watchers + 6 MCP servers while maintaining architectural principles. Key achievement: Orchestrator + watchdog pattern enables 99%+ uptime with auto-restart, critical for 24/7 autonomous operation. Ralph Wiggum loop (file movement completion strategy) provides transparent autonomous multi-step execution. CEO briefing transforms AI from reactive assistant to proactive business partner (Monday Morning CEO Briefing is standout feature). Comprehensive audit logging (90-day retention) ensures accountability and compliance. MCP server communication via stdio (local-only) simplifies Gold tier, HTTP reserved for Platinum tier cloud deployment. Recommendation: Implement Gmail send MCP server first (builds on Silver Gmail API, lowest risk), then Xero MCP (most complex, OAuth 30-min refresh), then social MCP servers (LinkedIn → Twitter → Facebook → Instagram). Orchestrator foundation should be implemented first (Phase 1) before individual watcher enhancements (Phase 2).

## Evaluation notes (flywheel)

- Failure modes observed: None - plan creation successful. Fixed Gold Tier spec.md feature branch reference from 001-gold-tier-ai-employee to 002-gold-tier-ai-employee (correction from earlier numbering). All research decisions documented with rationale and alternatives. All MCP server schemas created with complete tool definitions.
- Graders run and results (PASS/FAIL): Constitution Check - PASSED (8 principles validated: local-first, Agent Skills, multi-tier incremental, Watcher pattern, file-based state, approval workflow, Ralph loop, MCP external action). Technology Decisions - COMPLETE (10 decisions documented: orchestrator architecture, watchdog pattern, Ralph loop completion, event correlation, MCP communication, Xero token refresh, CEO briefing data sources, social media approval, WhatsApp session, audit log rotation). Architecture Validation - DEFINED (7 principles to prove in Gold tier: multi-watcher coordination, process isolation, MCP scalability, Ralph autonomy, CEO briefing value, audit completeness, orchestrator reliability). Success Criteria - MAPPED (28 success criteria from spec.md mapped to implementation phases). Scope Constraints - CLEAR (exactly 6 watchers, exactly 6 MCP servers, local-only, file-based state, no A2A).
- Prompt variant (if applicable): Standard /sp.plan workflow with user input: "for Gold Tier". Successfully interpreted intent to create implementation plan for Gold Tier (feature 002) following Phase 0 research + Phase 1 design workflow.
- Next experiment (smallest change to try): For future implementation plans, consider adding "Sequence Diagrams" section showing Orchestrator → Watchers → Action Files → Claude Code → MCP Servers communication flow. Current approach has detailed text descriptions but visual sequence diagram would clarify multi-process architecture. Alternative: Create "State Transition Diagrams" for key workflows (Ralph loop state transitions, approval workflow state machine, watcher lifecycle states).

**Note**: Phase 1 artifacts (data-model.md, contracts/, quickstart.md) have been generated. Ready for /sp.tasks command to generate detailed task breakdown.
