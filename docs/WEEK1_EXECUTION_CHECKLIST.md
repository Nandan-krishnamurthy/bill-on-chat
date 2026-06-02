# WEEK 1 EXECUTION CHECKLIST

Purpose: Keep Day 02-Day 05 implementation tightly aligned to Milestone 1 without leaking into future scope.

## Daily focus gates

- Day 02:
  - Finalize /chat request and response schema.
  - Add contract validation tests for valid and invalid payloads.
- Day 03:
  - Build minimal web chat shell.
  - Verify browser to backend round-trip through /chat.
- Day 04:
  - Add mode and business_id payload plumbing end-to-end.
  - Mark persona toggle as testing-only behavior.
- Day 05:
  - Add LLM provider factory seam.
  - Verify provider selection via environment configuration.
  - Execute Week 1 smoke checks and checkpoint prep.

## Scope guardrails for Week 1

- Do not implement agent business workflows.
- Do not add DB migrations or SQL models yet.
- Do not add GST calculator or invoice logic.
- Do not add WhatsApp transport integration.

## Week 1 completion checks

- /chat contract is stable and validated.
- Minimal web chat loop is functioning.
- Payload includes mode and business_id consistently.
- Provider seam is configuration-driven.
- Friday checkpoint package is ready with log updates.
