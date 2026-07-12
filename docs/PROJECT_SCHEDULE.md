# PROJECT_SCHEDULE

## Alignment Verification

This schedule was cross-checked against:
- PROJECT_SPEC_CLEAN.md
- PROJECT_EXECUTION_ROADMAP.md
- ROADMAP_VALIDATION_REPORT.md
- RISK_REGISTER.md

Alignment rules applied:
- No new milestones were introduced.
- No major phase order changes were made.
- Work remains in roadmap sequence: Phase 1 Weeks 1-6, Phase 2 Weeks 7-9.
- Risk controls are embedded where relevant (boundary security, GST correctness, idempotency, external dependency resilience).
- Every day ends with a testable output.
- Every Friday includes:
  - Stable Git commit
  - Git push
  - IMPLEMENTATION_LOG.md update

---

## Week 1 (2026-06-02 to 2026-06-05)

Goal:
- Foundations and web chat contract.

Deliverables:
- FastAPI skeleton
- /chat request/response schema
- Minimal web chat
- LLM factory seam

Success criteria:
- Browser message round-trip works through /chat.

### Day 0 - Monday (2026-06-01) [Preparation Day]
- Morning tasks:
  - Finalize implementation plan and week execution checklist.
  - Prepare local environment prerequisites and verify toolchain.
- Afternoon tasks:
  - Create project structure skeleton and environment template.
  - Set up readiness notes for Day 1 execution.
- Estimated hours: 8 (4 morning, 4 afternoon)
- Completion checklist:
  - Plan reviewed and locked for Week 1.
  - Environment and prerequisites are ready.
  - Execution starts cleanly on Day 1.
- Definition of Done:
  - Project is fully prepared for execution starting tomorrow.

### Day 1 - Tuesday (2026-06-02)
- Morning tasks:
  - Define chat request and response schemas.
  - Add payload validation rules.
- Afternoon tasks:
  - Implement stubbed /chat route.
  - Add contract tests for valid/invalid payloads.
- Estimated hours: 8
- Completion checklist:
  - Schema validation test passes.
  - /chat endpoint responds with expected shape.
  - Contract docs added to IMPLEMENTATION_LOG.md.
- Definition of Done:
  - /chat contract is stable and test-covered.

### Day 2 - Wednesday (2026-06-03)
- Morning tasks:
  - Build minimal web chat page and request client.
  - Add message input and output rendering.
- Afternoon tasks:
  - Wire web client to /chat.
  - Smoke test browser-to-backend loop.
- Estimated hours: 8
- Completion checklist:
  - UI sends message and receives reply.
  - Network payload matches contract.
  - One integration smoke test note recorded.
- Definition of Done:
  - Web chat can complete one full message cycle.

### Day 3 - Thursday (2026-06-04)
- Morning tasks:
  - Add persona toggle and business input field.
  - Wire payload to include mode and business_id.
- Afternoon tasks:
  - Add server-side mode acceptance path for Phase 1.
  - Verify mode and tenant values are persisted in logs.
- Estimated hours: 8
- Completion checklist:
  - Payload contains mode and business_id in every request.
  - Toggle behavior verified manually.
  - Boundary note added (toggle is testing-only).
- Definition of Done:
  - Phase 1 mode/tenant plumbing is complete and testable.

### Day 4 - Friday (2026-06-05)
- Morning tasks:
  - Implement LLM provider factory wiring.
  - Add env-based provider switch config.
- Afternoon tasks:
  - Run provider switch validation and week smoke suite.
  - Prepare week checkpoint package.
- Estimated hours: 8
- Completion checklist:
  - Factory path works with selected provider.
  - Week 1 success criteria pass.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 1 checkpoint is stable and recoverable from Git.

---

## Week 2 (2026-06-08 to 2026-06-12)

Goal:
- Database and first operational Customer Agent vertical slice.

Deliverables:
- Postgres connectivity
- Baseline models and Alembic migration
- create_customer tool + Customer Agent

Success criteria:
- Chat command creates customer row under selected business.

### Day 5 - Monday (2026-06-08)
- Morning tasks:
  - Configure local Postgres stack.
  - Add async DB session setup.
- Afternoon tasks:
  - Validate DB connection and migration bootstrap.
  - Record operational startup steps.
- Estimated hours: 8
- Completion checklist:
  - DB connection test passes.
  - Migration scaffolding exists.
  - Environment notes captured.
- Definition of Done:
  - Database baseline is runnable from clean setup.

### Day 6 - Tuesday (2026-06-09)
- Morning tasks:
  - Define businesses, customers, products models.
  - Enforce business_id scoping fields.
- Afternoon tasks:
  - Generate and apply initial migration.
  - Verify up/down migration path.
- Estimated hours: 8
- Completion checklist:
  - Migration applies cleanly.
  - Migration rollback works.
  - whatsapp_number nullable requirement preserved.
- Definition of Done:
  - Schema baseline is stable and reversible.

### Day 7 - Wednesday (2026-06-10)
- Morning tasks:
  - Implement create_customer input schema and validation.
  - Build create_customer tool.
- Afternoon tasks:
  - Build Customer Agent tool call path.
  - Add duplicate handling and validation tests.
- Estimated hours: 8
- Completion checklist:
  - Happy path customer creation works.
  - Duplicate customer handling is tested.
  - Validation rejects malformed data.
- Definition of Done:
  - Customer vertical slice is deterministic and test-covered.

### Day 8 - Thursday (2026-06-11)
- Morning tasks:
  - Wire orchestrator route to Customer Agent.
  - Add owner intent mapping for customer creation.
- Afternoon tasks:
  - Run end-to-end test from chat message to DB row.
  - Verify tenant isolation for two businesses.
- Estimated hours: 8
- Completion checklist:
  - End-to-end create customer test passes.
  - Tenant scoping test passes.
  - Traceability entry recorded.
- Definition of Done:
  - Customer creation works via natural language with tenant isolation.

### Day 9 - Friday (2026-06-12)
- Morning tasks:
  - Add business selector utility endpoint and UI integration.
  - Clean and stabilize Week 2 flows.
- Afternoon tasks:
  - Run regression for Week 1+2 critical tests.
  - Finalize Week 2 checkpoint.
- Estimated hours: 8
- Completion checklist:
  - Week 2 success criteria pass.
  - Migration and customer flow verified from clean DB.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 2 checkpoint is stable, testable, and recoverable.

---

## Week 3 (2026-06-15 to 2026-06-19)

Goal:
- Product Agent and conversation continuity.

Deliverables:
- Product tools and agent routing
- Conversation state persistence
- Fuzzy lookup and disambiguation

Success criteria:
- Product operations are conversational and stateful across turns.

### Day 10 - Monday (2026-06-15)
- Morning tasks:
  - Add product model fields and migration updates.
  - Define low-stock threshold fields.
- Afternoon tasks:
  - Build add/update product tool schemas.
  - Add required field validation tests.
- Estimated hours: 8
- Completion checklist:
  - Product schema/migration stable.
  - Validation tests pass.
  - Low-stock data modeled.
- Definition of Done:
  - Product data layer is complete and reversible.

### Day 11 - Tuesday (2026-06-16)
- Morning tasks:
  - Build Product Agent intent handling.
  - Add orchestrator route for product intents.
- Afternoon tasks:
  - Verify tool invocation flow.
  - Add regression tests for basic product ops.
- Estimated hours: 8
- Completion checklist:
  - Product add/update works via chat.
  - Routing tests pass.
  - No regressions in customer flow.
- Definition of Done:
  - Product vertical slice works in chat.

### Day 12 - Wednesday (2026-06-17)
- Morning tasks:
  - Implement conversation state persistence hooks.
  - Wire load/save around orchestrator execution.
- Afternoon tasks:
  - Add multi-turn tests for omitted fields.
  - Verify state keying by tenant/session.
- Estimated hours: 8
- Completion checklist:
  - State persists across turns.
  - Tenant/session isolation confirmed.
  - State storage documented.
- Definition of Done:
  - Multi-turn continuity works without tenant leakage.

### Day 13 - Thursday (2026-06-18)
- Morning tasks:
  - Implement fuzzy lookup and candidate disambiguation.
  - Add ambiguity clarification prompts.
- Afternoon tasks:
  - Run ambiguous entity tests.
  - Ensure no wrong writes on unresolved ambiguity.
- Estimated hours: 8
- Completion checklist:
  - Ambiguous names trigger clarification.
  - Wrong-write prevention verified.
  - Test evidence logged.
- Definition of Done:
  - Disambiguation behavior is safe and predictable.

### Day 14 - Friday (2026-06-19)
- Morning tasks:
  - Implement state trimming policy and archival to message log.
  - Validate bounded active context.
- Afternoon tasks:
  - Execute Week 3 regression suite.
  - Finalize Week 3 checkpoint.
- Estimated hours: 8
- Completion checklist:
  - State growth remains bounded.
  - Week 3 success criteria pass.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 3 checkpoint is stable and recoverable.

---

## Week 4 (2026-06-22 to 2026-06-26)

Goal:
- Invoicing core with deterministic GST and PDF output.

Deliverables:
- Invoice and invoice_items flow
- GST calculator with tests
- PDF generation and serving

Success criteria:
- GST-valid invoice PDF can be generated from chat.

### Day 15 - Monday (2026-06-22)
- Morning tasks:
  - Add invoice and invoice_items models/migrations.
  - Prepare lookup helpers for customer and product.
- Afternoon tasks:
  - Verify lookup integration and transactional boundaries.
  - Add basic invoice persistence tests.
- Estimated hours: 8
- Completion checklist:
  - Invoice schema stable.
  - Lookup path tested.
  - Migration rollback validated.
- Definition of Done:
  - Invoice data structures are production-ready baseline.

### Day 16 - Tuesday (2026-06-23)
- Morning tasks:
  - Implement deterministic gst_calculator.
  - Cover intra/inter-state logic and rounding.
- Afternoon tasks:
  - Add tests for exempt items and mixed slabs.
  - Add golden scenario test vectors.
- Estimated hours: 8
- Completion checklist:
  - GST tests pass for all required branches.
  - No LLM arithmetic path remains.
  - Assumptions documented.
- Definition of Done:
  - GST logic is deterministic and test-backed.

### Day 17 - Wednesday (2026-06-24)
- Morning tasks:
  - Implement create_invoice transactional tool.
  - Add discount handling at line and invoice level.
- Afternoon tasks:
  - Wire Invoice Agent orchestration.
  - Add transaction integrity tests.
- Estimated hours: 8
- Completion checklist:
  - Invoice creation path works with discounts.
  - Transaction rollback behavior verified.
  - Traceability record added.
- Definition of Done:
  - Invoice tool path is stable and reversible.

### Day 18 - Thursday (2026-06-25)
- Morning tasks:
  - Implement PDF generation template.
  - Add serving path and attachment response wiring.
- Afternoon tasks:
  - Add PDF reconciliation checks against DB totals.
  - Validate inline preview and download behavior.
- Estimated hours: 8
- Completion checklist:
  - PDF generation deterministic.
  - Totals reconcile (DB/text/PDF).
  - Delivery path verified.
- Definition of Done:
  - PDF output is correct and testable end-to-end.

### Day 19 - Friday (2026-06-26)
- Morning tasks:
  - Run end-to-end invoice scenarios with multi-line items.
  - Fix week-level defects.
- Afternoon tasks:
  - Execute Week 4 regression suite.
  - Finalize Week 4 checkpoint.
- Estimated hours: 8
- Completion checklist:
  - Week 4 success criteria pass.
  - GST and invoice tests green.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 4 checkpoint is stable and recoverable.

---

## Week 5 (2026-06-29 to 2026-07-03)

Goal:
- Payments, reminders, and reporting loop.

Deliverables:
- Payment agent and status transitions
- Owner read/query tools
- Reports (sales, GSTR-1, GSTR-3B, top entities)

Success criteria:
- Owner can run full operations loop from chat.

### Day 20 - Monday (2026-06-29)
- Morning tasks:
  - Add payments model and migration.
  - Implement record_payment base logic.
- Afternoon tasks:
  - Add partial/full payment rules and validation.
  - Unit test overpayment and partial cases.
- Estimated hours: 8
- Completion checklist:
  - Payment persistence is stable.
  - Validation rules pass tests.
  - Migration rollback verified.
- Definition of Done:
  - Payment write path is deterministic and safe.

### Day 21 - Tuesday (2026-06-30)
- Morning tasks:
  - Integrate Payment Agent in orchestrator.
  - Add status transition logic.
- Afternoon tasks:
  - Test unpaid/partial/paid transitions.
  - Validate no duplicate status update issues.
- Estimated hours: 8
- Completion checklist:
  - Status transitions correct.
  - Agent integration tests pass.
  - Regression check completed.
- Definition of Done:
  - Payment workflow is stable in chat.

### Day 22 - Wednesday (2026-07-01)
- Morning tasks:
  - Implement outstanding dues and customer balance queries.
  - Enforce owner-only access for these queries.
- Afternoon tasks:
  - Add SQL aggregation tests with fixtures.
  - Validate tenant isolation in queries.
- Estimated hours: 8
- Completion checklist:
  - Dues/balance queries correct.
  - Tenant leakage tests pass.
  - Access boundary verified.
- Definition of Done:
  - Owner financial query surface is reliable and secure.

### Day 23 - Thursday (2026-07-02)
- Morning tasks:
  - Implement report queries (sales, GSTR-1, GSTR-3B, top customers/products).
  - Connect Report Agent responses.
- Afternoon tasks:
  - Add period-based report tests.
  - Validate output consistency with transactional data.
- Estimated hours: 8
- Completion checklist:
  - Required reports generated correctly.
  - Report tests pass.
  - Report definitions documented.
- Definition of Done:
  - Reporting loop is operational and test-backed.

### Day 24 - Friday (2026-07-03)
- Morning tasks:
  - Implement reminder scheduling and confirmation gate.
  - Validate reminder surfacing in chat.
- Afternoon tasks:
  - Run Week 5 regression and close defects.
  - Finalize Week 5 checkpoint.
- Estimated hours: 8
- Completion checklist:
  - Reminder flow and confirmation behavior tested.
  - Week 5 success criteria pass.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 5 checkpoint is stable and recoverable.

---

## Week 6 (2026-07-06 to 2026-07-10)

Goal:
- Customer mode boundary enforcement and draft-order lifecycle.

Deliverables:
- Mode resolver and strict tool binding
- Sales Agent filtered toolset
- Draft order to owner confirmation path

Success criteria:
- Customer mode can place draft order only; owner confirms to invoice.

### Day 25 - Monday (2026-07-06)
- Morning tasks:
  - Finalize mode resolver implementation.
  - Enforce pre-LLM mode resolution.
- Afternoon tasks:
  - Bind toolsets by mode in orchestrator.
  - Add binding-map tests.
- Estimated hours: 8
- Completion checklist:
  - Mode resolver works for owner/customer flows.
  - Tool binding tests pass.
  - Security boundary notes updated.
- Definition of Done:
  - Mode enforcement is deterministic and testable.

### Day 26 - Tuesday (2026-07-07)
- Morning tasks:
  - Add draft_orders model/migration finalization.
  - Implement check_availability and get_sell_price tools.
- Afternoon tasks:
  - Enforce filtered responses (no count/cost/margin).
  - Add response boundary tests.
- Estimated hours: 8
- Completion checklist:
  - Filtered sales reads verified.
  - Draft order schema stable.
  - Customer data exposure tests pass.
- Definition of Done:
  - Customer read surface is correctly restricted.

### Day 27 - Wednesday (2026-07-08)
- Morning tasks:
  - Implement create_draft_order scoped to one customer.
  - Integrate Sales Agent flow.
- Afternoon tasks:
  - Add ownership scoping tests.
  - Validate draft persistence and retrieval.
- Estimated hours: 8
- Completion checklist:
  - Draft order creation works from chat.
  - Scoping tests pass.
  - No cross-customer access.
- Definition of Done:
  - Draft-order flow is operational and secure.

### Day 28 - Thursday (2026-07-09)
- Morning tasks:
  - Implement owner notification for pending drafts.
  - Implement owner confirm/edit/reject path.
- Afternoon tasks:
  - Wire draft-to-invoice conversion through Invoice Agent.
  - Add lifecycle integration tests.
- Estimated hours: 8
- Completion checklist:
  - Notification path works.
  - Confirm/edit/reject outcomes validated.
  - Conversion integrity tested.
- Definition of Done:
  - Full customer-to-owner draft lifecycle is stable.

### Day 29 - Friday (2026-07-10)
- Morning tasks:
  - Run adversarial boundary suite.
  - Fix any leakage or bypass issue.
- Afternoon tasks:
  - Execute Week 6 regression and phase-1 acceptance script.
  - Finalize Week 6 checkpoint.
- Estimated hours: 8
- Completion checklist:
  - Customer mode cannot reach owner-only tools/data.
  - Week 6 success criteria pass.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 6 checkpoint is stable, secure, and recoverable.

---

## Week 7 (2026-07-13 to 2026-07-17)

Goal:
- Phase 2 transport integration via OpenClaw.

Deliverables:
- Transport adapter and OpenClaw skill
- Identity mapping and onboarding
- Idempotency on inbound events

Success criteria:
- WhatsApp messages trigger core behavior with correct mode and tenant.

### Day 30 - Monday (2026-07-13)
- Morning tasks:
  - Set up OpenClaw runtime and WhatsApp sandbox path.
  - Create transport adapter shell.
- Afternoon tasks:
  - Forward inbound event to existing /chat endpoint.
  - Verify basic webhook handshake.
- Estimated hours: 8
- Completion checklist:
  - Inbound event reaches backend.
  - Adapter structure documented.
  - Smoke test evidence captured.
- Definition of Done:
  - Transport skeleton is running and testable.

### Day 31 - Tuesday (2026-07-14)
- Morning tasks:
  - Implement sender identity mapping to business_id and mode.
  - Build first-time owner onboarding path.
- Afternoon tasks:
  - Add owner/customer mapping tests.
  - Validate onboarding field collection.
- Estimated hours: 8
- Completion checklist:
  - Mapping logic correct for both personas.
  - Onboarding flow tested.
  - Tenant-mode boundary preserved.
- Definition of Done:
  - Identity resolution is stable for Phase 2.

### Day 32 - Wednesday (2026-07-15)
- Morning tasks:
  - Implement client_message_id dedupe.
  - Add idempotent guards on money-impacting operations.
- Afternoon tasks:
  - Run replay tests for duplicate deliveries.
  - Patch duplicate-side-effect defects.
- Estimated hours: 8
- Completion checklist:
  - Replay tests pass.
  - Duplicate invoices/payments prevented.
  - Idempotency behavior documented.
- Definition of Done:
  - Replay-safe event handling is operational.

### Day 33 - Thursday (2026-07-16)
- Morning tasks:
  - Implement outbound reply and attachment mapping.
  - Handle channel formatting constraints.
- Afternoon tasks:
  - Verify PDF media sending path.
  - Validate long-message formatting behavior.
- Estimated hours: 8
- Completion checklist:
  - Outbound text/media path works.
  - Formatting tests pass.
  - Transport parity notes recorded.
- Definition of Done:
  - WhatsApp response path is stable and testable.

### Day 34 - Friday (2026-07-17)
- Morning tasks:
  - Run owner-mode WhatsApp scenarios.
  - Run customer-mode WhatsApp scenarios.
- Afternoon tasks:
  - Execute Week 7 regression and parity checks.
  - Finalize Week 7 checkpoint.
- Estimated hours: 8
- Completion checklist:
  - Week 7 success criteria pass.
  - Web and WhatsApp core behavior parity verified.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 7 checkpoint is stable and recoverable.

---

## Week 8 (2026-07-20 to 2026-07-24)

Goal:
- Compliance, media robustness, and voice pipeline.

Deliverables:
- E-invoice and E-way integration adapters
- Voice transcription path
- Compliance metadata persistence

Success criteria:
- Compliance flows and media/voice path work for target scenarios.

### Day 35 - Monday (2026-07-20)
- Morning tasks:
  - Harden PDF media delivery path for WhatsApp.
  - Add storage/retrieval reliability checks.
- Afternoon tasks:
  - Add integration tests for attachment delivery.
  - Verify error handling for attachment failures.
- Estimated hours: 8
- Completion checklist:
  - Media delivery tests pass.
  - Retry/failure behavior validated.
  - Docs updated.
- Definition of Done:
  - Attachment delivery is reliable and test-backed.

### Day 36 - Tuesday (2026-07-21)
- Morning tasks:
  - Build voice transcription adapter.
  - Normalize transcript before orchestrator routing.
- Afternoon tasks:
  - Add transcript-to-intent regression tests.
  - Validate no mode/boundary leakage through voice path.
- Estimated hours: 8
- Completion checklist:
  - Voice input reaches same core path as text.
  - Regression tests pass.
  - Known limitations documented.
- Definition of Done:
  - Voice path is integrated and testable.

### Day 37 - Wednesday (2026-07-22)
- Morning tasks:
  - Implement E-invoice sandbox integration.
  - Persist IRN and signed metadata fields.
- Afternoon tasks:
  - Add provider contract tests.
  - Validate DB persistence and retrieval.
- Estimated hours: 8
- Completion checklist:
  - E-invoice contract tests pass.
  - IRN metadata persisted correctly.
  - Compliance trace logged.
- Definition of Done:
  - E-invoice path is functional in sandbox.

### Day 38 - Thursday (2026-07-23)
- Morning tasks:
  - Implement E-way bill adapter and trigger conditions.
  - Add fallback handling for provider downtime.
- Afternoon tasks:
  - Add threshold/condition tests.
  - Run replay and idempotency checks for compliance calls.
- Estimated hours: 8
- Completion checklist:
  - E-way trigger logic correct.
  - Fallback behavior verified.
  - Replay safety confirmed.
- Definition of Done:
  - Compliance branching is deterministic and resilient.

### Day 39 - Friday (2026-07-24)
- Morning tasks:
  - Embed compliance metadata into PDF output.
  - Run compliance end-to-end walkthrough.
- Afternoon tasks:
  - Execute Week 8 regression.
  - Finalize Week 8 checkpoint.
- Estimated hours: 8
- Completion checklist:
  - Compliance metadata visible in output where expected.
  - Week 8 success criteria pass.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Week 8 checkpoint is stable and recoverable.

---

## Week 9 (2026-07-27 to 2026-07-31)

Goal:
- Hardening, full acceptance, and ship readiness.

Deliverables:
- Error recovery and fallback hardening
- Mixed-language quality pass
- Full acceptance and runbook readiness

Success criteria:
- Ship test passes with complete workflow on WhatsApp and verifiable parity with web harness.

### Day 40 - Monday (2026-07-27)
- Morning tasks:
  - Implement error taxonomy and retry policy.
  - Add user-safe failure messages.
- Afternoon tasks:
  - Add developer logs and diagnostics.
  - Execute outage simulation checks.
- Estimated hours: 8
- Completion checklist:
  - Error classes mapped and handled.
  - Retry/fallback behavior tested.
  - Incident notes documented.
- Definition of Done:
  - Failure behavior is controlled and diagnosable.

### Day 41 - Tuesday (2026-07-28)
- Morning tasks:
  - Execute mixed-language test matrix.
  - Tune prompt and normalization rules.
- Afternoon tasks:
  - Re-run multilingual regressions.
  - Capture known language edge cases.
- Estimated hours: 8
- Completion checklist:
  - Hindi/Kannada/Tamil + English tests pass target threshold.
  - Remaining known issues documented.
  - No boundary regressions introduced.
- Definition of Done:
  - Mixed-language quality gate is met.

### Day 42 - Wednesday (2026-07-29)
- Morning tasks:
  - Perform security and tenant isolation review.
  - Execute adversarial prompt suite.
- Afternoon tasks:
  - Patch leakage risks if found.
  - Re-run boundary tests.
- Estimated hours: 8
- Completion checklist:
  - Boundary and tenant tests pass.
  - No critical leakage remains.
  - Security notes updated.
- Definition of Done:
  - Security posture is hardened for release candidate.

### Day 43 - Thursday (2026-07-30)
- Morning tasks:
  - Run full end-to-end rehearsal (owner + customer + compliance).
  - Validate web/WhatsApp parity.
- Afternoon tasks:
  - Close final acceptance gaps.
  - Prepare release checklist artifacts.
- Estimated hours: 8
- Completion checklist:
  - End-to-end suites pass.
  - DoD criteria mapped to evidence.
  - Release notes drafted.
- Definition of Done:
  - Acceptance readiness is confirmed.

### Day 44 - Friday (2026-07-31)
- Morning tasks:
  - Final cleanup and runbook finalization.
  - Validate deployment and operational notes.
- Afternoon tasks:
  - Execute final regression pass.
  - Mark release candidate checkpoint.
- Estimated hours: 8
- Completion checklist:
  - Week 9 and overall success criteria pass.
  - Runbook complete.
  - Stable Git commit done.
  - Git push done.
  - IMPLEMENTATION_LOG.md updated.
- Definition of Done:
  - Project reaches planned baseline completion checkpoint.

---

## Date Outcomes

Best case completion date:
- 2026-07-31

Expected completion date:
- 2026-08-14

Worst case completion date:
- 2026-09-04

Date rationale:
- Best case assumes no critical blockers and all week gates pass on first attempt.
- Expected case includes one to two weeks of rework buffer for risks in GST, boundary, and compliance integrations.
- Worst case includes additional delay from external provider instability and hardening regressions.
