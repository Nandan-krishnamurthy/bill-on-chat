# Week 01 - Day 04 Prompt

## 1) Day Objective
Add and verify payload plumbing for mode and business_id across web and backend, including explicit handling for Phase 1 testing toggle behavior.

## 2) Why This Task Belongs On This Day
Mode and tenant context must be present end-to-end before provider wiring and before any future mode-specific tool binding work in later milestones.

## 3) What Must Already Be Completed Before Starting
- Day 03 browser-to-backend round-trip is stable.
- /chat contract and validation tests exist.
- Minimal web UI can send requests and render responses.

## 4) What Must NOT Be Implemented Yet
- No mode-based tool binding logic (that belongs later milestones).
- No customer/owner domain tools.
- No DB-backed tenant isolation implementation.
- No Phase 2 identity mapping or transport integration.

## 5) Complete Execution Prompt (Paste Into Copilot Chat)
```text
You are implementing Project Beta Week 1 Day 04.

Before coding, read and cross-check:
1) PROJECT_SPEC_CLEAN.md
2) PROJECT_EXECUTION_ROADMAP.md
3) ROADMAP_VALIDATION_REPORT.md
4) PROJECT_SCHEDULE.md
5) RISK_REGISTER.md
6) IMPLEMENTATION_LOG.md
7) DEVELOPMENT_GUARDRAILS.md

Day 04 scope:
- Ensure web payload always includes business_id and mode.
- Ensure backend accepts and validates mode/business_id per contract.
- Confirm persona toggle is clearly marked as Phase 1 testing-only behavior.
- Add verification that payload values are logged/traceable for debugging.

Hard constraints:
- Stay strictly in Day 04 scope.
- Keep transport-agnostic architecture.
- Do not introduce mode-specific business logic yet.
- Do not add future milestone features.

Out of scope:
- Agent security boundary enforcement via tool binding.
- Database tenant filters.
- Invoice/GST/payment/report logic.
- WhatsApp/OpenClaw identity mapping.

Expected output:
1) Files changed and rationale.
2) How mode/business payload path was validated.
3) What was intentionally deferred.
4) Ready-to-paste IMPLEMENTATION_LOG.md entry.

Verification steps (must run):
- Send owner-mode request and confirm payload path.
- Send customer-mode request and confirm payload path.
- Confirm neither path introduces future scope features.

Provide this IMPLEMENTATION_LOG.md block at the end:

Date: 2026-06-04
Week/Day: Week 1 / Day 04
Milestone: Milestone 1 - Platform Skeleton and Chat Contract
Requirement Source: PROJECT_SPEC_CLEAN.md Section 2; PROJECT_EXECUTION_ROADMAP.md Week 1
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
- Revert Day 04 payload-plumbing commits if mode/business path introduces instability.
Next action:
- Day 05 LLM provider factory integration and Week 1 checkpoint.
```
