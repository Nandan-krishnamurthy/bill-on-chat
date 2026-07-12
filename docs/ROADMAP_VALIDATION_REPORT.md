# ROADMAP VALIDATION REPORT (SECOND PASS)

This second validation compares the current PROJECT_EXECUTION_ROADMAP.md against the available specification source PROJECT_BETA_SPEC_EXTRACT.txt.

Constraint: PROJECT_SPEC.txt is not present in the workspace. Validation was performed against PROJECT_BETA_SPEC_EXTRACT.txt (the extracted specification text).

## 1. Coverage Summary

- Coverage percentage (strict): 95%
- Major areas fully covered:
  - Two-phase architecture with unchanged core /chat contract.
  - Owner vs Customer server-side mode resolution and hard security boundary.
  - Customer-mode draft-order-only flow with owner confirmation to invoice.
  - Deterministic GST calculation with explicit anti-LLM arithmetic constraint.
  - Nine-table multi-tenant model and non-destructive Phase 1 to Phase 2 WhatsApp mapping.
  - Phase 2 commitments for e-invoice, e-way bill, voice input, mixed-language handling.
  - DoD quantification for Phase 1 (5 customers, 10 products, 3-line invoice) and Phase 2 ship test.
- Major areas partially covered:
  - Some spec tables are represented as equivalent bullet contracts rather than table-for-table reproduction.
  - Weekly reporting cadence is present, but the source section is truncated and may contain additional fields not visible in the extract.
- Major areas missing:
  - One requirement remains unresolved due truncated source text in Section 15 (weekly reporting payload details beyond the visible prefix).

## 2. Requirement-by-Requirement Comparison

### 0. Why Two Phases
- Requirement: Split product and transport work while keeping one shared backend core.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.1, 3.1, 4, 9.3
- Notes: Preserved exactly in architecture and milestones.

### 1. What You Are Building
- Requirement: Conversational GST billing for SMEs with web first, WhatsApp second.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.1, 1.2, 5, 9
- Notes: Includes Indian-first and mixed-language requirements.

### 2. Two Operating Modes
- Requirement: Owner and Customer personas with strict permission separation.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.2, 2.1, 5.6, 7.4, 9.2
- Notes: Boundary is tool-binding + query scoping, not prompts.

### 3. Architecture Overview
- Requirement: One backend, one agent layer, two transport adapters.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.1, 1.5, 5.7
- Notes: Transport seam and adapter invariants are explicit.

### 4. LLM Provider Abstraction
- Requirement: One factory seam; provider swapping via env variable; GST safety caveat.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.3, 2.1, 5.1, 8.6
- Notes: LLM never does tax arithmetic is explicit.

### 5. Feature Set (v1 Scope)
- Requirement: Owner operations + customer sales flow + Phase 2 compliance features.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.3, 1.6, 4, 5, 9
- Notes: Discounts, low-stock behavior, GSTR-3B, reminders, and compliance are now present.

### 6. Agents
- Requirement: Mode-aware orchestrator and specialist agent behavior contracts.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.3, 4.3 through 4.9, 5.2 through 5.8
- Notes: Sales Agent-only customer mode and owner-only tools are explicit.

### 7. Read and Query Operations
- Requirement: Named owner read tools + 2 filtered customer read tools.
- Covered in roadmap: Yes
- Location in roadmap: Section 1.6, Week 5, Section 7.4
- Notes: Includes cross-table query constraint (named deterministic query functions).

### 8. Data Model
- Requirement: 9-table schema with business_id scoping and Phase 1 nullable whatsapp_number.
- Covered in roadmap: Yes
- Location in roadmap: Sections 1.4, 4.2, 5.2
- Notes: Non-destructive migration path is explicit.

### 9. Phase 1 Build
- Requirement: Week-by-week Phase 1 build with checkpoints.
- Covered in roadmap: Yes
- Location in roadmap: Sections 5.1 through 5.6, 6, 9.2
- Notes: Reframed as milestone + weekly + daily plan while preserving required outcomes.

### 10. Phase 2 Build
- Requirement: OpenClaw mapping, idempotency, media, voice, GST compliance, edge cases.
- Covered in roadmap: Yes
- Location in roadmap: Sections 5.7 through 5.9, 7, 9.3
- Notes: Compliance scope is committed, not stretch-only.

### 11. Suggested Folder Structure
- Requirement: Canonical module layout including transport seam.
- Covered in roadmap: Partial
- Location in roadmap: Weeks 1 through 9 file plans
- Notes: The roadmap includes equivalent file paths and module intent, but not a single full tree block reproduced exactly as in the spec.

### 12. Key Things to Get Right
- Requirement: transport seam, idempotency, mode boundary, tenant boundary, validation, confirmations, GST rigor, secrets, state trimming.
- Covered in roadmap: Yes
- Location in roadmap: Sections 2.1, 2.4, 7, 8.1, 8.5
- Notes: All visible key constraints are represented.

### 13. Free / Cheap APIs and Tools
- Requirement: practical provider/tool options for cost-conscious build.
- Covered in roadmap: Yes
- Location in roadmap: Section 8.6
- Notes: Included as guidance list rather than a detailed pricing table.

### 14. Definition of Done
- Requirement: explicit Phase 1 and Phase 2 acceptance checks and ship test.
- Covered in roadmap: Yes
- Location in roadmap: Sections 9.2, 9.3
- Notes: Quantified acceptance criteria are present.

### 15. Weekly Reporting Cadence
- Requirement: Friday reporting cadence.
- Covered in roadmap: Partial
- Location in roadmap: Section 8.5
- Notes: Source spec section is truncated, so exact unseen fields cannot be fully verified.

## 3. Missing Requirements

- Weekly reporting cadence payload details beyond the visible "Every Friday, send:" prefix in Section 15 cannot be fully verified from the available extract and remain a strict open requirement.

## 4. Simplifications

These are acceptable representation simplifications, not functional omissions:
- Spec tables are represented in equivalent bullet contracts and weekly milestones.
- Free/cheap API recommendations are represented as concise guidance instead of a full tabular reference.
- Suggested folder structure is represented through weekly file creation plans rather than a single tree diagram block.

## 5. Architectural Deviations

Confirmed architectural deviations: 0

No material architecture mismatch was found in the current roadmap against the visible specification content.

## 6. Risk Assessment

### High-risk areas
- Security boundary leakage under adversarial prompts.
- GST correctness and rounding regressions.
- Idempotency/replay handling in WhatsApp transport.
- External dependency instability in GSP/voice integrations.

### Areas likely to cause implementation delays
- Compliance adapter integration and certification-style test depth.
- Mixed-language quality tuning and regression hardening.
- End-to-end parity testing across web and WhatsApp paths.

### Areas likely to cause architectural rework
- Low likelihood if transport seam and tool-binding boundaries stay enforced.
- Moderate likelihood if cross-table query rules are bypassed by ad hoc query logic.

## 7. Recommended Corrections

1. Add a full tree-style folder structure appendix only if strict document parity with spec formatting is required.
2. If PROJECT_SPEC.txt (full text) becomes available, re-run Section 15 cadence validation against complete content.
3. Keep a fixed compliance test matrix (IRN/e-way triggers + replay behavior) to prevent late-phase regressions.

## 8. Final Verdict

Roadmap mostly aligned with minor corrections.

The implementation roadmap is functionally aligned with the visible specification requirements and is close to implementation-ready. The remaining gap is primarily documentation-format parity and one truncated-source verification item, not core product architecture or feature scope.
