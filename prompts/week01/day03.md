# Week 01 - Day 03 Prompt

## 1) Day Objective
Build a minimal web chat client and wire it to the Day 02 /chat contract for an end-to-end browser round-trip.

## 2) Why This Task Belongs On This Day
UI integration is scheduled only after contract stabilization so frontend work is anchored to a tested API seam and avoids rework.

## 3) What Must Already Be Completed Before Starting
- Day 02 contract schemas and tests are passing.
- Stub /chat endpoint is live and returns contract-compliant JSON.
- Run instructions exist for backend startup.

## 4) What Must NOT Be Implemented Yet
- No agent orchestration.
- No DB-backed logic.
- No persona boundary enforcement logic beyond payload plumbing.
- No transport adapter code.
- No invoice/payment/report features.

## 5) Complete Execution Prompt (Paste Into Copilot Chat)
```text
You are implementing Project Beta Week 1 Day 03.

First read and cross-check:
1) PROJECT_SPEC_CLEAN.md
2) PROJECT_EXECUTION_ROADMAP.md
3) ROADMAP_VALIDATION_REPORT.md
4) PROJECT_SCHEDULE.md
5) RISK_REGISTER.md
6) IMPLEMENTATION_LOG.md
7) DEVELOPMENT_GUARDRAILS.md

Day 03 scope:
- Build minimal web chat UI (input + output rendering).
- Connect web client to /chat endpoint.
- Ensure payload shape remains aligned with Day 02 contract.
- Add smoke verification for browser -> backend -> browser round-trip.

Hard constraints:
- Stay within Day 03 scope.
- Follow spec and roadmap architecture.
- No future milestone work.
- Keep implementation minimal and testable.

Out of scope:
- Agent/tool implementations.
- DB persistence.
- Mode security boundary enforcement details.
- Transport/WhatsApp features.

Expected output:
1) Files changed and why.
2) Manual smoke test steps and result.
3) Any contract mismatches found/fixed.
4) Ready-to-paste IMPLEMENTATION_LOG.md entry.

Verification steps (must run):
- Launch backend and web UI.
- Send a sample message from browser.
- Confirm response renders and network payload matches schema.

Provide this IMPLEMENTATION_LOG.md block at the end:

Date: 2026-06-03
Week/Day: Week 1 / Day 03
Milestone: Milestone 1 - Platform Skeleton and Chat Contract
Requirement Source: PROJECT_SPEC_CLEAN.md Sections 0, 3; PROJECT_EXECUTION_ROADMAP.md Week 1
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
- Revert Day 03 UI integration commits if client payloads diverge from contract.
Next action:
- Day 04 mode + business payload plumbing.
```
