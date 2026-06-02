# Week 01 - Day 01 Prompt (Preparation Day)

## 1) Day Objective
Lock execution readiness for Week 1 by finalizing plan, validating environment prerequisites, and preparing project skeleton artifacts without starting milestone implementation code.

## 2) Why This Task Belongs On This Day
The schedule marks Monday as preparation-only so delivery work can begin tomorrow without setup drag or architectural confusion. This reduces early-week churn and protects milestone sequencing.

## 3) What Must Already Be Completed Before Starting
- All current planning artifacts are available and reviewed:
  - PROJECT_SPEC_CLEAN.md
  - PROJECT_EXECUTION_ROADMAP.md
  - ROADMAP_VALIDATION_REPORT.md
  - PROJECT_SCHEDULE.md
  - RISK_REGISTER.md
  - IMPLEMENTATION_LOG.md
- You have local toolchain access (Python, package manager, terminal).
- You understand current milestone: Milestone 1 (Platform Skeleton and Chat Contract).

## 4) What Must NOT Be Implemented Yet
- No business logic agents.
- No database schema/migrations.
- No invoice/GST logic.
- No payment/report logic.
- No WhatsApp/OpenClaw code.
- No compliance integrations.

## 5) Complete Execution Prompt (Paste Into Copilot Chat)
```text
You are implementing Project Beta Week 1 Day 01 (Preparation Day).

Before writing any code, read and cross-check these files:
1) PROJECT_SPEC_CLEAN.md
2) PROJECT_EXECUTION_ROADMAP.md
3) ROADMAP_VALIDATION_REPORT.md
4) PROJECT_SCHEDULE.md
5) RISK_REGISTER.md
6) IMPLEMENTATION_LOG.md
7) DEVELOPMENT_GUARDRAILS.md

Mandatory constraints:
- Stay strictly inside Day 01 preparation scope.
- Follow specification and roadmap constraints.
- Respect architecture boundaries (transport-agnostic core, /chat seam).
- Do not implement future milestone work.
- Generate only minimal artifacts needed for readiness.

Day 01 scope:
- Validate environment prerequisites and startup assumptions.
- Create or confirm minimal folder skeleton for Week 1 work.
- Create/update .env.example baseline keys (no secrets).
- Prepare a concise Week 1 execution checklist in docs.

Out of scope today:
- /chat implementation details.
- Agent/tool implementation.
- DB migrations.
- GST/business features.

Expected output format:
1) Files created/updated today.
2) Why each change is needed for tomorrow.
3) Verification steps and results.
4) Risks/blockers found.
5) Ready-to-paste IMPLEMENTATION_LOG.md entry.

Verification steps to execute:
- Confirm project tree is ready for Day 02 coding.
- Confirm env template has required non-secret keys.
- Confirm no out-of-scope files/features were added.

Provide this IMPLEMENTATION_LOG.md block at the end:

Date: 2026-06-01
Week/Day: Week 1 / Day 01 (Preparation)
Milestone: Milestone 1 - Platform Skeleton and Chat Contract
Requirement Source: PROJECT_SPEC_CLEAN.md Sections 0, 3, 4; PROJECT_EXECUTION_ROADMAP.md Week 1
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
- Revert Day 01 prep commits if readiness artifacts conflict with Week 1 implementation.
Next action:
- Start Day 02 /chat schema + contract implementation.
```
