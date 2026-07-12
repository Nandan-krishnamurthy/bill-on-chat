# PROJECT EXECUTION ROADMAP

## 1. Project Understanding

### 1.1 Architecture in Plain Engineering Terms
Project Beta is a transport-agnostic conversational GST billing platform with one backend core and two channel adapters:

- Phase 1 channel: Web chat UI
- Phase 2 channel: WhatsApp via OpenClaw
- Shared core (both phases): FastAPI + LangGraph agents + tools layer + PostgreSQL

Non-negotiable architectural constraints from the spec:

- The agent layer must stay identical across web and WhatsApp.
- All channel-specific code must live in transport.py, and nowhere else.
- Agents only receive text plus attachment references as output.
- The /chat contract remains the sole integration seam between transports and the core.

The core design seam is the chat contract:

- Input: business_id, mode, message (Phase 1)
- Output: reply_text, attachments

Core product principles:

- Zero UI friction: avoid complex forms/screens in v1; prioritize chat-first execution.
- Agents over workflows: rely on intent reasoning with deterministic tools, not menu trees.
- Conversational state: preserve recent context, infer missing fields carefully, ask clarifications when needed.
- Indian-first behavior: GST-safe outputs in INR, with mixed Hindi/Kannada/Tamil + English input support.
- Transport agnostic core: identical agent and tool behavior across web and WhatsApp.

In Phase 2, business and mode are resolved from sender identity, but agent and tool logic stays unchanged.

This separation is the strongest architectural decision in the spec. It keeps transport work from contaminating billing logic and enables independent testing of the hard part first: GST-safe business operations.

### 1.2 Owner Mode vs Customer Mode
Owner Mode and Customer Mode are not UI states; they are permission domains.

Owner Mode:

- Audience: business owner or authorized operator
- Scope: full operational access
- Capabilities: customer management, product management, invoice creation, payment recording, dues, reminders, reporting

Customer Mode:

- Audience: end customer of that business
- Scope: sales interaction only
- Capabilities: availability check, sell price quote, draft order creation
- Explicitly disallowed: invoice creation, payment actions, dues, other customers, reports, exact stock, cost, margin, customer balances, sales totals, GST summaries

Customer Mode is a hard security boundary, not a prompt style choice. Tool binding and query scoping enforce the boundary server-side before the LLM runs.

Owner Mode and Customer Mode must be resolved from identity in production:

- Phase 1 owner identity: web session / selected business context
- Phase 1 customer identity: web persona toggle only for testing
- Phase 2 owner identity: registered WhatsApp number
- Phase 2 customer identity: shared customer entry point mapped to one business and one customer scope

Critical rule: the boundary is enforced by server-side mode resolution plus tool binding, not by prompt wording.

### 1.3 Agent Architecture
The agent system is mode-aware orchestration over deterministic tools.

- Orchestrator Agent:
  - Receives resolved mode and business context before LLM reasoning
  - Binds only tools allowed for that mode
  - Routes intent to specialist agent or asks clarification question

Owner specialists:

- Customer Agent
- Product Agent
- Invoice Agent
- Payment Agent
- Report Agent

Customer specialist:

- Sales Agent only

Agent behavior contracts:

- Customer Agent (Owner Mode): create/update customer, fuzzy lookup, list/filter customers.
- Product Agent (Owner Mode): create/update product, stock updates, low-stock alerts, inventory queries.
- Invoice Agent (Owner Mode): create invoice, apply discounts, convert draft order to invoice, generate PDF, and trigger compliance tools in Phase 2 when required.
- Payment Agent (Owner Mode): record partial/full payments, update invoice status, compute balances/dues, schedule reminders.
- Report Agent (Owner Mode): sales summaries by period, GSTR-1 and GSTR-3B summaries, top customers/products.
- Sales Agent (Customer Mode): availability + sell price + create_draft_order for one scoped customer only.

LLM responsibility:

- Intent understanding
- Argument extraction
- Clarification questions
- Tool selection

Clarification is required when intent is ambiguous. The orchestrator should ask one question instead of guessing when customer/product resolution, invoice line items, or date/period scope are unclear.

Deterministic code responsibility:

- All tax math
- Database writes and read aggregations
- Security scoping
- PDF generation
- Idempotency checks
- GST arithmetic and rounding
- Duplicate delivery protection

### 1.4 Database Design
The spec defines a nine-table multi-tenant data model. Every business-facing row carries business_id.

Core tables:

- businesses: tenant root metadata (GSTIN, state, WhatsApp mapping)
- customers: per-business customer master
- products: per-business catalog and inventory
- draft_orders: customer-mode pending orders (pending, confirmed, rejected)
- invoices: invoice header totals, status, compliance fields, pdf_url
- invoice_items: invoice line items
- payments: payment records against invoices
- conversations: active conversational state (JSONB snapshot)
- message_log: inbound and outbound audit history

Phase 1 schema requirement:

- businesses.whatsapp_number must be nullable in Phase 1.
- Phase 1 must not require a destructive migration when Phase 2 backfills WhatsApp identity mapping.
- The Phase 2 lookup adds whatsapp_number -> business_id + mode resolution without changing the core schema shape.

Key design implications:

- Hard tenant isolation at query level
- Conversation continuity without overloading active prompt state
- Smooth migration from Phase 1 to Phase 2 by backfilling WhatsApp mapping
- Tenant isolation enforced at query level through business_id filters in every data access path

### 1.5 End-to-End Execution Flow
1. Channel adapter receives user message.
2. Backend resolves tenant and mode server-side.
3. Conversation state is loaded (recent context + durable logs).
4. Orchestrator binds mode-allowed tools only.
5. LLM routes to specialist and calls validated tools.
6. Tool layer performs deterministic operations (DB, GST logic, PDF, reports).
7. Results persist to DB and message logs.
8. Backend returns reply_text plus attachment references.
9. Channel adapter renders/sends response (web preview or WhatsApp media).

For customer order flow:

- Customer creates draft order only.
- Owner receives pending draft.
- Owner confirms/edits/rejects.
- Confirmation triggers normal invoice path with GST and PDF.
- In customer mode, only draft orders are possible; payment and invoice finalization remain owner actions.

### 1.6 Read and Query Tool Surface

Owner-mode read tools (deterministic query functions):

- get_inventory(filter)
- get_product(name)
- get_outstanding_dues()
- get_customer_balance(name)
- list_customers(filter)
- get_invoice(number_or_customer)
- get_sales_summary(period)
- get_gst_summary(period)
- get_top(customers|products)

Customer-mode read tools (strictly filtered):

- check_availability(product_name): returns available / not available only
- get_sell_price(product_name): returns sell price only

Cross-table reads (dues, balances, summaries) must be implemented as named query functions in report/payment layers, never as LLM-assembled SQL.

---

## 2. Architectural Review

### 2.1 Implement Exactly as Written
- One shared chat API and identical agent layer across both phases.
- Server-side mode resolution before orchestrator execution.
- Tool-binding as the security boundary.
- Customer Mode restricted to filtered reads + draft order only.
- Deterministic GST logic outside LLM.
- business_id scoping in all relevant data operations.
- Idempotency for repeated message delivery.
- Confirmation gates before money-impacting actions.
- Pydantic validation on every tool input.
- GST math must be deterministic and unit tested; the LLM never performs tax arithmetic.
- Customer mode must never be able to reach owner data, even through adversarial prompts.
- Channel-specific behavior must stay in transport.py only.

### 2.2 Simplify Initially (without violating architecture)
- Start with plain HTML chat page instead of React.
- Use one LLM provider in dev (Groq) through abstraction seam.
- Keep report scope minimal only as an implementation order choice, not a permanent product constraint.
- Use basic reportlab PDF template before advanced styling.
- Keep reminder delivery in-app in Phase 1 before external transports.
- Preserve the full spec feature set in the roadmap even if implementation order is staged.

### 2.3 Postpone Until Later
- Voice transcription tuning and mixed-language quality hardening, but the feature itself is part of Phase 2.
- E-Invoice and E-Way Bill integration are Phase 2 deliverables when required, not stretch-only items.
- Multi-provider retry/fallback policies.
- Advanced analytics and dashboard-level outputs.
- Production-grade observability stack beyond essentials.

### 2.4 Highest Technical Risks
- Security boundary leakage between Owner and Customer toolsets.
- Incorrect GST computation due to extraction ambiguity or rounding errors.
- Cross-tenant data leakage from missing business_id filters.
- Idempotency failures leading to duplicate invoices/payments.
- Orchestrator state drift across long conversations.
- WhatsApp transport retries causing replay side effects.
- LLM hallucinations accepted without Pydantic validation.
- Incorrect or delayed customer-mode draft order notification to the owner.
- Missing compliance data propagation into invoice records and PDFs.

---

## 3. Development Strategy

### 3.1 Recommended Build Order
1. Skeleton service and chat contract
2. Database schema and migrations
3. Single agent vertical slice (Customer create)
4. Product and memory continuity
5. Invoice and deterministic GST + PDF
6. Payments, query tools, reports
7. Customer Mode security boundary + Sales Agent + draft order flow
8. Phase 2 transport integration
9. Compliance and channel hardening
10. Mixed-language and voice support validation
11. Final acceptance harness and specification parity review

### 3.2 Why This Order Works
- You validate the integration seam early (chat request/response).
- You stabilize persistence before adding complex workflows.
- You prove the agent-to-tool loop with one simple write use case.
- You defer high-risk GST and money operations until platform basics are stable.
- You complete full owner loop before adding customer-facing constraints.
- You add transport only after core product behavior is already production-like.

### 3.3 Dependency Graph (Practical)
- Chat endpoint depends on config + LLM factory + basic routing.
- Agents depend on tool contracts.
- Tools depend on DB session + models + validators.
- Invoice flow depends on customer/product lookups + GST service + PDF service.
- Payment/status logic depends on invoice totals.
- Reports depend on mature transactional data and indexed queries.
- Customer mode depends on orchestrator binding policy and scoped tools.
- WhatsApp adapter depends only on stable /chat contract.
- E-invoice and e-way bill depend on a GSP adapter layer that sits behind the invoice toolset.
- Voice transcription depends on a text normalization layer before the orchestrator.
- Mixed-language handling depends on prompt, normalization, and regression fixtures.

---

## 4. Milestones

### Milestone 1: Platform Skeleton and Chat Echo
- Goal: reachable chat loop with mode and tenant payload.
- Deliverables: FastAPI app, /chat route, web chat shell, env config, LLM seam.
- Success criteria: message in browser returns backend reply.
- Risks: overbuilding UI before backend contract stabilizes.

### Milestone 2: Persistent Core Data Model
- Goal: durable multi-tenant schema and migrations.
- Deliverables: SQLAlchemy models, Alembic baseline, DB session management.
- Success criteria: CRUD smoke tests for businesses, customers, products.
- Risks: weak tenant constraints and missing indexes.
 - Exit criteria: businesses.whatsapp_number remains nullable and Phase 2 mapping can be backfilled without destructive schema changes.

### Milestone 3: First Operational Agent (Customer)
- Goal: agent-driven customer creation via chat.
- Deliverables: Customer Agent, create_customer tool, Pydantic validation.
- Success criteria: natural language creates customer rows correctly.
- Risks: unvalidated LLM arguments and duplicate customer entries.

### Milestone 4: Product Agent and Context Continuity
- Goal: product ops and multi-turn slot filling.
- Deliverables: Product tools, ILIKE search, conversation state persistence.
- Success criteria: assistant can complete incomplete product requests over turns.
- Risks: stale state and ambiguous entity resolution.
 - Exit criteria: low-stock thresholds and inventory query paths are in place, even if alerts are initially only surfaced in owner chat.

### Milestone 5: Invoicing Core (GST + PDF)
- Goal: reliable invoice generation with deterministic tax.
- Deliverables: gst_calculator service, invoice tools, discounts, reportlab PDF output.
- Success criteria: GST-tested invoice with downloadable PDF from chat.
- Risks: tax math defects and PDF mismatch with invoice data.
 - Exit criteria: invoice totals, line items, discounts, and tax breakup round-trip through DB, chat, and PDF consistently.

### Milestone 6: Payment and Reporting Loop
- Goal: close business cycle with dues visibility.
- Deliverables: Payment Agent, reminders scheduler, report/query tools, GSTR-1 and GSTR-3B summaries, top customers/products.
- Success criteria: partial/full payment updates status; reports reconcile.
- Risks: reconciliation inaccuracies and scheduler duplication.
 - Exit criteria: owner can query inventory, invoice, customer balance, dues, and summary reports through dedicated tools.

### Milestone 7: Customer Mode Boundary and Draft Orders
- Goal: secure dual-mode system.
- Deliverables: mode resolver, Sales Agent, filtered tools, draft_orders flow, owner notification path, boundary tests.
- Success criteria: customer can place draft only; owner confirms to invoice.
- Risks: boundary bypass through wrong tool binding.
 - Exit criteria: customer mode cannot access owner-only data under adversarial prompts.

### Milestone 8: WhatsApp Transport Integration
- Goal: end-to-end chatbot via OpenClaw with unchanged core.
- Deliverables: OpenClaw skill, sender mapping, idempotency key handling, media delivery, owner onboarding, customer scoping.
- Success criteria: WhatsApp message triggers same backend behavior as web.
- Risks: webhook retries, mapping errors, duplicate side effects.
 - Exit criteria: messages can be replayed safely without duplicate writes.

### Milestone 9: Compliance Extensions and Production Hardening
- Goal: compliance, multilingual support, and operational robustness.
- Deliverables: e-invoice/e-way integrations, voice input path, fallback handling, multilingual text handling, compliance metadata in PDFs.
- Success criteria: full flow runs on WhatsApp including compliance where applicable and mixed-language input behaves correctly.
- Risks: third-party API instability and edge-case regressions.
 - Exit criteria: ship test passes on web and WhatsApp with compliance cases and mixed-language prompts.

---

## 5. Weekly Plan

### Week 1: Foundations and Web Chat Contract
- Objectives:
  - Initialize backend and minimal web chat.
  - Implement /chat request-response contract.
  - Add mode and business payload plumbing.
- Files and folders to create:
  - app/main.py
  - app/routes/chat.py
  - app/config.py
  - app/llm.py
  - web/index.html
  - web/app.js
  - pyproject.toml
  - .env.example
  - README.md
- Dependencies to install:
  - fastapi, uvicorn, pydantic-settings, httpx
  - langgraph, langchain
  - langchain[groq] for development
  - langchain extras for anthropic, openai, and google-genai via the same factory seam
- Features to build:
  - POST /chat accepts business_id, mode, message.
  - Returns reply_text, attachments.
  - Web chat supports message entry and persona toggle.
  - Persona toggle is testing-only; production mode is identity-resolved.
- Testing requirements:
  - API contract test for valid/invalid payloads.
  - Browser manual smoke test for round trip.
  - LLM factory test that proves provider switching happens via one env line.
- Completion criteria:
  - Working browser-to-backend chat loop with stable JSON schema.

### Week 2: Database and Customer Agent Vertical Slice
- Objectives:
  - Stand up Postgres and migrations.
  - Implement first real tool call via Customer Agent.
- Files and folders to create:
  - app/db/models.py
  - app/db/session.py
  - app/db/migrations/
  - app/agents/customer_agent.py
  - app/tools/customer_tools.py
  - tests/test_customer_agent.py
- Dependencies to install:
  - sqlalchemy[asyncio], asyncpg, alembic
- Features to build:
  - Multi-tenant models baseline.
  - create_customer tool with validation.
  - Business selector in web UI.
  - businesses.whatsapp_number remains nullable and does not force a Phase 2 migration.
- Testing requirements:
  - Migration up/down test.
  - Create customer happy-path and duplicate handling tests.
  - Tenant isolation tests for all business-scoped rows.
- Completion criteria:
  - Chat command can create customer row under selected business.

### Week 3: Product Agent and Conversation Memory
- Objectives:
  - Add product lifecycle operations.
  - Introduce multi-turn continuity.
- Files and folders to create:
  - app/agents/product_agent.py
  - app/tools/product_tools.py
  - app/tools/query_tools.py (initial inventory reads)
  - tests/test_product_agent.py
  - tests/test_conversation_state.py
- Dependencies to install:
  - rapidfuzz (optional) for matching support
- Features to build:
  - Add/update product with slot filling.
  - Fuzzy product lookup and disambiguation.
  - Persist conversation snapshots with trimming policy.
  - Low-stock threshold data and alerts are modeled, even if alert delivery starts in owner chat.
- Testing requirements:
  - Multi-turn slot completion tests.
  - Ambiguous name disambiguation tests.
  - Inventory query tests that prove exact counts stay hidden from customer mode.
- Completion criteria:
  - Product flows feel conversational and stateful.

### Week 4: Invoice Agent, Deterministic GST, PDF
- Objectives:
  - Build invoice creation end to end.
  - Guarantee GST correctness through deterministic service.
- Files and folders to create:
  - app/agents/invoice_agent.py
  - app/tools/invoice_tools.py
  - app/services/gst_calculator.py
  - app/tools/pdf_generator.py
  - tests/test_gst_calculation.py
  - tests/test_invoice_flow.py
- Dependencies to install:
  - reportlab
- Features to build:
  - Customer/product lookup to invoice line resolution.
  - Discounts on invoice lines and totals.
  - CGST+SGST vs IGST logic and rounding.
  - PDF generation and web preview/download.
  - Compliance fields on invoices: IRN, e-way bill, pdf_url.
- Testing requirements:
  - Unit tests for tax scenarios, exempt items, mixed slabs.
  - Integration test from message to stored invoice + PDF URL.
  - Golden tests for round-trip totals across chat, DB, and PDF.
- Completion criteria:
  - A GST-valid invoice PDF can be created from chat.
  - Discounts and tax totals remain consistent across output surfaces.

### Week 5: Payments, Reminders, Reports, Owner Read Tools
- Objectives:
  - Complete owner billing cycle and analytics reads.
- Files and folders to create:
  - app/agents/payment_agent.py
  - app/agents/report_agent.py
  - app/tools/payment_tools.py
  - app/tools/query_tools.py (expand)
  - tests/test_payments.py
  - tests/test_reports.py
- Dependencies to install:
  - apscheduler
- Features to build:
  - Full/partial payment recording and invoice status updates.
  - Outstanding dues and balance reads.
  - Sales, GSTR-1, and GSTR-3B summaries.
  - Top customers and top products queries.
  - Reminder scheduler with confirmation gate.
  - Reminder surfacing in chat (and optional reminders view in Phase 1).
  - Owner read tools for inventory, customer balances, invoice lookup, and dues.
- Testing requirements:
  - Payment reconciliation tests.
  - Query correctness tests against seeded data.
  - Boundary tests proving customer mode cannot reach owner reads.
- Completion criteria:
  - Owner can run complete operational loop from chat.
  - Reminder delivery and reporting work against real tenant-scoped data.

### Week 6: Customer Mode, Sales Agent, Boundary Enforcement
- Objectives:
  - Implement secure dual persona behavior.
- Files and folders to create:
  - app/auth/mode.py
  - app/agents/orchestrator.py
  - app/agents/sales_agent.py
  - app/tools/sales_tools.py
  - tests/test_mode_boundary.py
  - tests/test_sales_agent.py
- Dependencies to install:
  - none required beyond current stack
- Features to build:
  - Mode-resolved tool binding.
  - Customer filtered reads and draft order creation.
  - Owner confirmation path from draft order to invoice.
  - Owner notification path for pending draft orders.
  - Toolset binding map that excludes owner-only tools from customer mode.
- Testing requirements:
  - Adversarial prompts to verify owner tools are unreachable in customer mode.
  - Draft order lifecycle tests.
  - Tests proving customer mode only sees availability and sell price, never exact stock or cost.
- Completion criteria:
  - Phase 1 definition met in browser for both modes.
  - Customer mode can create draft orders only, and the owner can confirm them into invoices.

### Week 7: OpenClaw Transport and Identity Mapping
- Objectives:
  - Integrate WhatsApp transport without touching core logic.
- Files and folders to create:
  - app/tools/transport.py
  - openclaw-skills/billing/
  - tests/test_transport_adapter.py
- Dependencies to install:
  - OpenClaw runtime dependencies per deployment target
- Features to build:
  - Incoming WhatsApp -> existing /chat.
  - Sender mapping to business_id and mode.
  - First-time owner onboarding from WhatsApp: business name, GSTIN, state.
  - Shared customer entry point mapped to one business and one customer scope.
  - Idempotent processing by client_message_id.
  - Channel-specific formatting and attachment handling remain in app/tools/transport.py only.
- Testing requirements:
  - Replay tests for duplicate webhook events.
  - Owner vs customer mapping tests by sender identity.
  - Tests proving transport code is isolated from core agent logic.
- Completion criteria:
  - WhatsApp messages drive existing agent core successfully.
  - WhatsApp owner and customer flows are parity-checked against web behavior.

### Week 8: Media, Voice, and Compliance Integrations
- Objectives:
  - Add practical production channels and compliance features.
- Files and folders to create:
  - app/tools/gst_api.py
  - app/services/voice_transcription.py
  - tests/test_compliance_integration.py
- Dependencies to install:
  - provider SDKs for chosen GSP sandbox
  - whisper client stack (provider dependent)
- Features to build:
  - PDF as WhatsApp attachment.
  - Voice note transcription pipeline.
  - E-invoice IRN and E-way bill flow where required.
  - Persist IRN, signed QR metadata, and e-way bill references on invoices.
  - Compliance metadata embedded into invoice PDFs.
- Testing requirements:
  - Contract tests for external API adapters.
  - E2E scenario with compliance metadata in output.
  - Message replay tests do not duplicate compliance side effects.
- Completion criteria:
  - Legal/compliance path works for target scenarios.
  - Voice and mixed-language text can reach the orchestrator through the same chat contract.

### Week 9: Hardening and Full Acceptance
- Objectives:
  - Eliminate high-risk edge case failures before handoff.
- Files and folders to create:
  - tests/test_e2e.py
  - tests/test_idempotency.py
  - docs/runbook.md
- Dependencies to install:
  - optional observability libraries (sentry-sdk, structlog)
- Features to build:
  - Robust error recovery and fallback messaging.
  - Mixed-language quality pass for Hindi/Kannada/Tamil + English.
  - Final acceptance harness for definition-of-done checks.
  - Full ship-test coverage for web and WhatsApp parity.
- Testing requirements:
  - End-to-end regression suite for owner and customer journeys.
  - Fault injection tests for external dependency downtime.
  - Penetration-style prompt tests for customer-mode boundary leakage.
- Completion criteria:
  - Phase 2 ship test passes: full workflow on WhatsApp only.
  - The same workflow also remains accessible and verifiable in web chat as a fallback harness.

---

## 6. Daily Execution Plan

Assumption: 9 weeks x 5 working days = 45 implementation days.

### Week 1

Day 1
- Morning tasks: Initialize repository structure, pyproject, environment config template, FastAPI app bootstrap.
- Afternoon tasks: Add base health route and run local server.
- Expected outcome: service starts reliably with configuration loading.
- Verification checklist: server boot test, env variable validation test, lint pass.

Day 2
- Morning tasks: Implement chat request and response schemas.
- Afternoon tasks: Create /chat route with stubbed response logic.
- Expected outcome: stable API contract for chat loop.
- Verification checklist: schema validation tests, HTTP contract tests.

Day 3
- Morning tasks: Build minimal web chat page and request client.
- Afternoon tasks: Render reply messages and attachment placeholders.
- Expected outcome: browser to backend text round trip.
- Verification checklist: manual chat smoke run, network payload check.

Day 4
- Morning tasks: Add mode toggle and business input fields in UI.
- Afternoon tasks: Pass mode and business_id through /chat payload.
- Expected outcome: end-to-end payload plumbing works.
- Verification checklist: request payload assertions in dev tools.

Day 5
- Morning tasks: Add LLM abstraction factory and provider selection config.
- Afternoon tasks: Return simple intent echo from LLM path.
- Expected outcome: LLM is integrated through one seam.
- Verification checklist: provider switch via env changes behavior without code changes.

### Week 2

Day 6
- Morning tasks: Add docker compose for Postgres and database connectivity.
- Afternoon tasks: Create SQLAlchemy base models skeleton.
- Expected outcome: backend connects to Postgres with async session.
- Verification checklist: DB connection test and migration bootstrap.

Day 7
- Morning tasks: Define businesses, customers, products tables.
- Afternoon tasks: Generate and apply initial Alembic migration.
- Expected outcome: baseline schema in local DB.
- Verification checklist: migration up/down works from clean DB.

Day 8
- Morning tasks: Implement customer tool input schemas and create_customer tool.
- Afternoon tasks: Build Customer Agent to call tool.
- Expected outcome: customer creation via tool path.
- Verification checklist: unit tests for validation and insert behavior.

Day 9
- Morning tasks: Wire orchestrator minimal routing to Customer Agent.
- Afternoon tasks: Connect /chat owner intent to customer creation flow.
- Expected outcome: natural language creates customer rows.
- Verification checklist: integration test from message to DB row.

Day 10
- Morning tasks: Add business selector in UI and create/list business utility endpoint.
- Afternoon tasks: End-to-end cleanup and docs update.
- Expected outcome: tenant-aware customer creation in UI.
- Verification checklist: two-business isolation test for customer inserts.

### Week 3

Day 11
- Morning tasks: Add product model fields and migration updates if needed.
- Afternoon tasks: Create add_product tool and validations.
- Expected outcome: product records can be created safely.
- Verification checklist: unit tests for required product fields.

Day 12
- Morning tasks: Build Product Agent intent handling.
- Afternoon tasks: Route product intents in orchestrator.
- Expected outcome: product add/update works through chat.
- Verification checklist: product tool invocation tests.

Day 13
- Morning tasks: Implement conversation state persistence table usage.
- Afternoon tasks: Add state load/save hooks around orchestrator calls.
- Expected outcome: follow-up messages retain context.
- Verification checklist: multi-turn test with omitted fields.

Day 14
- Morning tasks: Add fuzzy lookup for customer/product names.
- Afternoon tasks: Add disambiguation prompt logic.
- Expected outcome: ambiguous names trigger clarification, not wrong writes.
- Verification checklist: ambiguous case tests with multiple near matches.

Day 15
- Morning tasks: Implement trimmed active context policy.
- Afternoon tasks: ensure full history goes to message_log.
- Expected outcome: stable memory with bounded context.
- Verification checklist: load test for long chat; state size does not grow unbounded.

### Week 4

Day 16
- Morning tasks: Define invoice and invoice_items models plus migration.
- Afternoon tasks: implement lookup_customer and lookup_product helpers.
- Expected outcome: invoice dependencies ready.
- Verification checklist: lookup integration tests.

Day 17
- Morning tasks: Build deterministic gst_calculator for intra/inter-state.
- Afternoon tasks: add rounding and exempt item handling.
- Expected outcome: deterministic tax computation service.
- Verification checklist: unit tests for all tax branches.

Day 18
- Morning tasks: implement create_invoice transactional tool.
- Afternoon tasks: build Invoice Agent tool orchestration.
- Expected outcome: invoices persist with line-level totals.
- Verification checklist: DB transactional integrity test.

Day 19
- Morning tasks: generate reportlab PDF template from invoice data.
- Afternoon tasks: expose PDF serving path and attachment response.
- Expected outcome: invoice PDF generated and retrievable.
- Verification checklist: PDF content assertions for totals and tax breakup.

Day 20
- Morning tasks: wire end-to-end invoice flow from chat intent.
- Afternoon tasks: fix edge cases and finalize week checkpoint demo.
- Expected outcome: invoice flow fully usable from web chat.
- Verification checklist: scenario test with 3-line item invoice and correct GST.

### Week 5

Day 21
- Morning tasks: create payments model and migration.
- Afternoon tasks: implement record_payment tool for partial/full payments.
- Expected outcome: payment records stored against invoices.
- Verification checklist: unit tests for overpayment and partial payment rules.

Day 22
- Morning tasks: build Payment Agent integration.
- Afternoon tasks: implement invoice status auto-update logic.
- Expected outcome: invoice status transitions correctly with payments.
- Verification checklist: paid/unpaid/partial transition tests.

Day 23
- Morning tasks: implement outstanding dues and customer balance queries.
- Afternoon tasks: expose owner query tools to orchestrator.
- Expected outcome: owner can ask dues questions conversationally.
- Verification checklist: SQL aggregation tests against seeded fixtures.

Day 24
- Morning tasks: build report query tools (sales summary, GST summary, top entities).
- Afternoon tasks: implement Report Agent responses.
- Expected outcome: owner receives report-ready aggregates in chat.
- Verification checklist: period-based report test cases.

Day 25
- Morning tasks: implement reminder scheduling with confirmation gate.
- Afternoon tasks: add pydantic validation sweep for all tool inputs.
- Expected outcome: operational loop stable and guarded.
- Verification checklist: scheduler dedupe test and invalid payload rejection tests.

### Week 6

Day 26
- Morning tasks: implement server-side mode resolver module.
- Afternoon tasks: update orchestrator to bind tools by mode.
- Expected outcome: mode determines reachable tool graph.
- Verification checklist: binding map tests per mode.

Day 27
- Morning tasks: add draft_orders model and migration.
- Afternoon tasks: implement sales tools check_availability and get_sell_price.
- Expected outcome: customer reads are filtered and limited.
- Verification checklist: no exact stock/cost fields in customer responses.

Day 28
- Morning tasks: implement create_draft_order tool scoped to one customer.
- Afternoon tasks: build Sales Agent interaction flow.
- Expected outcome: customer can place draft order only.
- Verification checklist: draft order persistence and ownership scoping tests.

Day 29
- Morning tasks: implement owner confirmation flow draft to invoice.
- Afternoon tasks: wire notification path for pending drafts.
- Expected outcome: owner confirms draft into real invoice.
- Verification checklist: conversion flow integration tests.

Day 30
- Morning tasks: boundary hardening and adversarial prompt testing.
- Afternoon tasks: finalize phase 1 acceptance script.
- Expected outcome: customer mode cannot access owner-only data under any prompt.
- Verification checklist: dedicated boundary suite passes.

### Week 7

Day 31
- Morning tasks: deploy or run OpenClaw and connect WhatsApp sandbox path.
- Afternoon tasks: create custom skill shell to forward messages.
- Expected outcome: transport adapter skeleton works.
- Verification checklist: inbound webhook to local endpoint smoke test.

Day 32
- Morning tasks: map sender identity to business and mode.
- Afternoon tasks: add owner onboarding path for first-time number.
- Expected outcome: automatic mode selection by identity.
- Verification checklist: mapping tests for owner and customer senders.

Day 33
- Morning tasks: implement idempotency key handling for incoming events.
- Afternoon tasks: make write tools replay-safe.
- Expected outcome: duplicate deliveries do not duplicate business actions.
- Verification checklist: replay event tests on invoice/payment actions.

Day 34
- Morning tasks: attach transport adapter in response path.
- Afternoon tasks: ensure text response formatting for WhatsApp constraints.
- Expected outcome: readable end-user WhatsApp replies.
- Verification checklist: formatting tests for long and multiline replies.

Day 35
- Morning tasks: run owner mode flows entirely through WhatsApp.
- Afternoon tasks: run customer mode flows entirely through WhatsApp.
- Expected outcome: phase 2 core transport replacement is proven.
- Verification checklist: side-by-side parity checks with web harness.

### Week 8

Day 36
- Morning tasks: send invoice PDFs as WhatsApp media attachments.
- Afternoon tasks: confirm attachment storage and retrieval reliability.
- Expected outcome: invoice media delivery works.
- Verification checklist: media delivery integration tests.

Day 37
- Morning tasks: implement voice note transcription adapter.
- Afternoon tasks: route transcript to existing orchestrator path.
- Expected outcome: voice input behaves like text input.
- Verification checklist: transcript-to-intent regression tests.

Day 38
- Morning tasks: implement e-invoice sandbox adapter.
- Afternoon tasks: persist IRN and signed metadata in invoice records.
- Expected outcome: compliance data round trip works for eligible invoices.
- Verification checklist: external API contract tests and DB persistence checks.

Day 39
- Morning tasks: implement e-way bill sandbox adapter and triggering conditions.
- Afternoon tasks: add robust fallback messaging for API downtime.
- Expected outcome: compliance branching is deterministic and resilient.
- Verification checklist: threshold and movement-condition tests.

Day 40
- Morning tasks: integrate compliance metadata into generated PDF.
- Afternoon tasks: end-to-end compliance walkthrough.
- Expected outcome: legally richer invoice outputs in channel.
- Verification checklist: E2E scenario with compliance fields in attachment.

### Week 9

Day 41
- Morning tasks: error taxonomy and retry policy implementation.
- Afternoon tasks: add user-safe error messages and developer logs.
- Expected outcome: failures are recoverable and diagnosable.
- Verification checklist: simulated outage tests.

Day 42
- Morning tasks: mixed-language prompt test matrix.
- Afternoon tasks: tune prompts and normalization utilities.
- Expected outcome: stable intent extraction for mixed-language input.
- Verification checklist: multilingual regression suite.

Day 43
- Morning tasks: security and tenant isolation review.
- Afternoon tasks: fix any leakage risks and add guard tests.
- Expected outcome: hardened isolation guarantees.
- Verification checklist: tenant boundary test suite and penetration-style prompts.

Day 44
- Morning tasks: full E2E rehearsal from onboarding to invoice/payment/report.
- Afternoon tasks: close all P1 and P2 acceptance gaps.
- Expected outcome: near-ship confidence.
- Verification checklist: complete ship checklist run with evidence artifacts.

Day 45
- Morning tasks: final cleanup, docs, runbook, deployment notes.
- Afternoon tasks: release candidate tag and handoff package.
- Expected outcome: production-ready baseline and operational guide.
- Verification checklist: all critical tests green, known issues documented.

---

## 7. Testing Strategy

### 7.1 Unit Tests
- gst_calculator: intra/inter-state, mixed slabs, exempt items, rounding, edge decimals.
- Tool validators: strict schema acceptance and rejection.
- Utility functions: fuzzy matching, mode resolver, idempotency key parser.
- Tax tests must verify the LLM never performs arithmetic.

### 7.2 Integration Tests
- Agent-to-tool integration for each specialist.
- DB transaction behavior for invoice/payment updates.
- Draft-order to invoice conversion path.
- Scheduler reminders against seeded overdue invoices.
- GSP adapter contract tests for e-invoice and e-way bill integration.
- OpenClaw webhook replay tests.

### 7.3 End-to-End Tests
- Owner journey: customer create -> product add -> invoice -> payment -> report.
- Customer journey: availability -> quote -> draft order -> owner confirm.
- Channel parity: same journey via web and WhatsApp.
- Mixed-language journey: Hindi/Kannada/Tamil + English input through web and WhatsApp.

### 7.4 Security Boundary Tests
- Customer mode cannot access owner tools under adversarial prompts.
- Customer mode cannot query other customers or dues.
- Cross-tenant test matrix to ensure business_id isolation.
- Tool binding assertions run before each agent execution.
- Customer mode cannot observe exact stock, cost, margin, sales totals, or GST summaries.
- Business and WhatsApp identity mapping tests prove the right tenant and mode are selected.

### 7.5 GST Calculation Tests
- Golden dataset for tax scenarios and expected totals.
- Line-item and invoice-level reconciliation checks.
- Round-trip check: DB totals, response text, and PDF totals must match.
- Regression tests on every change to pricing, discount, or tax logic.
- Tests cover CGST+SGST intra-state, IGST inter-state, rounding, exempt items, and mixed slabs.

---

## 8. Development Rules

### 8.1 Coding Standards
- Python style: black + ruff + type hints on public interfaces.
- Strict Pydantic models for all external and tool inputs.
- Deterministic services isolated from LLM logic.
- No raw SQL from agent responses; only predefined query functions.
- Secrets live in .env and are loaded through pydantic-settings.
- Any query that joins tables lives in named query functions, not ad hoc agent-generated SQL.

### 8.2 Git Workflow
- Trunk-based with short-lived feature branches.
- Daily rebase on main to reduce integration drift.
- Pull requests required for all non-trivial changes.

### 8.3 Branch Strategy
- main: releasable branch
- feature/<scope>: implementation branches
- hotfix/<scope>: urgent production fixes

### 8.4 Commit Strategy
- Small, atomic commits by logical change.
- Conventional style examples:
  - feat(agent): add sales agent draft order flow
  - fix(gst): correct IGST rounding for exempt line mix
  - test(boundary): add adversarial customer mode suite

### 8.5 Documentation Strategy
- Keep README current with setup, run, and test commands.
- Maintain docs/runbook.md for operational actions and incidents.
- Add architecture decision notes for major tradeoffs (mode boundary, idempotency, GST handling).
- Update this roadmap when implementation decisions materially change scope/order.
- Keep a short note of compliance assumptions and provider choices so the Phase 2 handoff is reproducible.
- Weekly reporting cadence: every Friday send completed work, pending work, blockers, risks, and next-week checkpoints.

### 8.6 Free/Cheap API and Tool Guidance
- LLM dev default: Groq.
- LLM alternatives: Google Gemini, Cerebras, Ollama, OpenRouter.
- LLM production: Anthropic Claude or OpenAI via LLM_MODEL swap.
- Voice transcription: Whisper provider path in Phase 2.
- Database: local Docker Postgres for dev; managed Postgres optional for prod.
- Transport: OpenClaw (self-hosted) for WhatsApp.
- Compliance sandbox: GSP sandbox (for example Masters India or ClearTax).

---

## 9. Definition of Done

### 9.1 Week 1 Complete When
- Web chat sends and receives messages through /chat.
- business_id and mode are included in request flow.
- LLM factory is working behind one config seam.
- Basic contract and smoke tests pass.
- Persona toggle is clearly marked as testing-only.

### 9.2 Phase 1 Complete When
Owner mode in web chat can:
- create/select business with name, GSTIN, and state
- add at least 5 customers and 10 products
- create a GST-correct invoice with 3 line items and generate PDF
- record full and partial payments
- retrieve sales and GSTR-1 summaries for the month

Customer mode in web chat can:
- check availability and sell price
- place draft order only
- never see exact stock, cost, margin, dues, other customers, or reports

Boundary guarantees verified:
- customer cannot access dues, reports, other customers, or exact stock
- owner can confirm draft order into invoice
- boundary tests explicitly prove the owner toolset is unreachable in customer mode

### 9.3 Phase 2 Complete When
Using WhatsApp only, system can:
- onboard owner by first-time number
- auto-resolve owner vs customer mode from sender identity
- deliver invoice PDFs as media
- send a payment reminder to a customer on WhatsApp
- support voice note input path
- execute e-invoice and e-way flows for applicable cases
- handle mixed-language text in Hindi/Kannada/Tamil + English
- preserve transport and agent parity with the web harness

Ship test passes:
- full billing cycle works without opening browser

---

## 10. Future Guidance

For future implementation discussions, treat this roadmap as the baseline plan.

Operating stance for future chats:
- Role: Senior Software Architect + Senior Backend Engineer + Technical Mentor
- Decision principle: smallest working increment first, then iterative hardening
- Priority order: correctness and boundaries before feature breadth
- Review focus: risk, regression prevention, and testability before code volume

When you ask future questions, recommendations should reference:
- current milestone
- current week/day objective
- explicit tradeoff and risk impact
- verification steps before moving forward

This document is the master implementation guide unless superseded by a revised roadmap with explicit change notes.

---

## 11. Specification Coverage Matrix

| Major requirement | Roadmap location |
| --- | --- |
| Two-phase split with shared core and unchanged /chat contract | Sections 1.1, 3.1, 4, 5.7, 9.3 |
| Owner Mode vs Customer Mode as a server-side security boundary | Sections 1.2, 2.1, 7.4, 9.2 |
| Customer-mode draft order flow with owner confirmation | Sections 1.5, 4.7, 5.6, 9.2 |
| Named owner/customer read-tool surface and strict query scoping | Sections 1.6, 5.5, 7.4 |
| LLM provider abstraction with one factory and env-based swapping | Sections 1.3, 5.1, 8.1 |
| Deterministic GST with unit tests and no LLM arithmetic | Sections 1.3, 2.1, 4, 7.5 |
| Nine-table multi-tenant PostgreSQL schema with business_id on every row | Sections 1.4, 3.3, 5.2, 7.4 |
| Customer creation, product management, invoice creation, payments, and reports | Sections 3.1, 4.3 through 4.6, 5.2 through 5.5, 9.2 |
| Customer-mode availability and sell-price-only surface | Sections 1.2, 4.6, 5.6, 7.4 |
| Transport seam and OpenClaw WhatsApp integration | Sections 1.1, 3.3, 4.8, 5.7 |
| PDF generation and inline/download delivery | Sections 1.1, 4.5, 5.4, 5.8 |
| Compliance features: e-invoice, e-way bill, GSP integration | Sections 4.8, 5.8, 9.3 |
| Voice input and mixed-language support | Sections 5.8, 5.9, 9.3 |
| Exact Phase 1 and Phase 2 Definition of Done criteria | Sections 9.2, 9.3 |
| Security, idempotency, tenant isolation, and confirmation gates | Sections 2.1, 2.4, 7.4, 8.1 |
| Free/cheap API guidance and provider strategy | Sections 5.1, 8.6 |
| Weekly reporting cadence | Section 8.5 |
| Documentation, testing, and operational guidance | Sections 7, 8.5, 9.1, 10 |
