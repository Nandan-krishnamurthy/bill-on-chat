# Week 01 - Day 02 Prompt

## 1) Day Objective
Implement and validate the core /chat API contract: request/response schemas, validation rules, stub route behavior, and contract tests.

## 2) Why This Task Belongs On This Day
The contract seam is the highest-priority integration boundary for both Phase 1 web chat and Phase 2 transport adapter reuse. It must be stable before UI wiring and provider integration.

## 3) What Must Already Be Completed Before Starting
- Day 01 readiness is complete (environment + skeleton).
- FastAPI app bootstrap path exists.
- Agreed payload contract fields are confirmed from roadmap/spec:
  - request: business_id, mode, message
  - response: reply_text, attachments

## 4) What Must NOT Be Implemented Yet
- No full orchestrator/agent routing.
- No database operations.
- No GST or invoice logic.
- No WhatsApp/OpenClaw transport.
- No payment/report/customer/product domain features.

## 5) Complete Execution Prompt (Paste Into Copilot Chat)
```text
You are implementing Project Beta Week 1 Day 02.

Before writing code, read and cross-check:
1) PROJECT_SPEC_CLEAN.md
2) PROJECT_EXECUTION_ROADMAP.md
3) ROADMAP_VALIDATION_REPORT.md
4) PROJECT_SCHEDULE.md
5) RISK_REGISTER.md
6) IMPLEMENTATION_LOG.md
7) DEVELOPMENT_GUARDRAILS.md

Day 02 scope (strict):
- Define /chat request and response Pydantic schemas.
- Enforce validation for required fields and invalid mode values.
- Implement stub /chat endpoint returning valid response shape.
- Add contract tests for valid + invalid payloads.

Hard constraints:
- Follow spec and roadmap exactly.
- Stay within Day 02 scope.
- Avoid future milestone work.
- Generate only code required for contract stability.
- Keep transport-agnostic architecture intact.

Out of scope:
- Agent implementation.
- Tool calls and DB access.
- Any business feature logic.

Expected output:
1) Code changes with file-level rationale.
2) Verification commands and outcomes.
3) Brief compliance check vs roadmap/spec constraints.
4) Ready-to-paste IMPLEMENTATION_LOG.md entry.

Verification steps (must run):
- Run schema validation tests.
- Run endpoint contract tests.
- Confirm response always includes reply_text and attachments.

Provide this IMPLEMENTATION_LOG.md block at the end:

Date: 2026-06-02
Week/Day: Week 1 / Day 02
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
- Revert Day 02 contract commits if schema changes break API compatibility.
Next action:
- Day 03 web chat integration to /chat.
```
