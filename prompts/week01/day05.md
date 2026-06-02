# Week 01 - Day 05 Prompt (Friday Checkpoint)

## 1) Day Objective
Implement LLM provider factory wiring with environment-driven model selection, validate provider seam behavior, and close Week 1 with a stable checkpoint.

## 2) Why This Task Belongs On This Day
Provider abstraction completes Milestone 1 architecture groundwork while preserving transport-agnostic design and enabling low-cost dev model usage before domain agents are built.

## 3) What Must Already Be Completed Before Starting
- Day 01-04 tasks are complete.
- /chat contract and minimal web round-trip are stable.
- Mode and business payload plumbing works end-to-end.

## 4) What Must NOT Be Implemented Yet
- No specialist agents (Customer/Product/Invoice/etc.).
- No domain tools or DB transactions.
- No GST math implementation.
- No WhatsApp/OpenClaw transport code.
- No compliance and reporting features.

## 5) Complete Execution Prompt (Paste Into Copilot Chat)
```text
You are implementing Project Beta Week 1 Day 05 (Friday checkpoint).

Before coding, read and cross-check:
1) PROJECT_SPEC_CLEAN.md
2) PROJECT_EXECUTION_ROADMAP.md
3) ROADMAP_VALIDATION_REPORT.md
4) PROJECT_SCHEDULE.md
5) RISK_REGISTER.md
6) IMPLEMENTATION_LOG.md
7) DEVELOPMENT_GUARDRAILS.md

Day 05 scope:
- Add LLM provider factory abstraction seam.
- Add env-driven model/provider selection.
- Ensure /chat path uses the factory seam (no provider-specific hardcoding).
- Run week smoke verification for Day 01-05 deliverables.

Hard constraints:
- Follow specification and roadmap.
- Stay inside Week 1 scope.
- Avoid future milestone work.
- Keep code minimal and testable.

Friday mandatory actions:
- Create stable Git commit.
- Push to remote.
- Update IMPLEMENTATION_LOG.md with week checkpoint evidence.

Out of scope:
- Agent business workflows.
- DB model/migrations.
- GST and invoice logic.
- Transport integration.

Expected output:
1) File changes + rationale.
2) Provider-switch verification evidence.
3) Week 1 completion check against schedule criteria.
4) Ready-to-paste IMPLEMENTATION_LOG.md entry.

Verification steps (must run):
- Confirm default model config loads from environment.
- Confirm switching model/provider needs config change only, not code rewrite.
- Re-run Week 1 smoke: API contract + browser round-trip + mode/business payload.

Provide this IMPLEMENTATION_LOG.md block at the end:

Date: 2026-06-05
Week/Day: Week 1 / Day 05
Milestone: Milestone 1 - Platform Skeleton and Chat Contract
Requirement Source: PROJECT_SPEC_CLEAN.md Sections 3, 4; PROJECT_EXECUTION_ROADMAP.md Week 1
What was built:
- [fill]
Why it was built:
- [fill]
Files changed:
- [fill]
Tests/verification run:
- [fill]
Risks/blockers:
- [fill]
Rollback note:
- Revert Day 05 provider-seam commits if provider abstraction breaks chat stability.
Next action:
- Start Week 2 database and Customer Agent vertical slice.
```
