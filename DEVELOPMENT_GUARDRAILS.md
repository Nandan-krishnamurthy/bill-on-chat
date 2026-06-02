# DEVELOPMENT GUARDRAILS

Purpose: Ensure the project is recoverable at any stage, with clear answers to what was built, why it was built, when it was built, and how to revert safely.

## 1. Git Strategy

### Branch strategy
- Use trunk-based flow with short-lived branches.
- Keep main always releasable.
- Branch naming:
  - feature/weekX-topic
  - fix/weekX-issue
  - hotfix/production-issue
  - chore/docs-or-tooling
- One branch should map to one milestone objective or one bounded bug.

### Commit strategy
- Commit small, atomic changes only.
- One commit should represent one logical unit:
  - Schema migration
  - One tool contract
  - One agent routing change
  - One test suite addition
- Commit message format:
  - type(scope): summary
  - Include why in commit body (business/compliance/security reason).
- Required commit footer metadata:
  - Requirement source section
  - Week and day
  - Risk level (low/medium/high)
  - Rollback note

### When to create checkpoints
- Daily checkpoint at end of day.
- Weekly checkpoint at end of each week.
- Milestone checkpoint at each milestone exit.
- Extra checkpoint before:
  - Migrations
  - Security boundary changes
  - Tax logic changes
  - Idempotency changes
  - Transport integration changes

### When to merge to main
- Merge only when all are true:
  - Unit tests pass for touched domains.
  - Integration tests pass for affected flows.
  - No known critical regression in owner/customer boundary.
  - Implementation log updated.
  - Rollback path documented.
- Use pull request reviews for all non-trivial changes.

### Recovery workflow
- Find latest stable tag.
- Create recovery branch from latest stable tag.
- Cherry-pick only verified commits from broken branch.
- Re-run required test gates.
- Merge recovery branch after validation.
- Never force-push main.
- Never use destructive history rewrites on shared branches.

## 2. Milestone Checkpoints

For each major milestone, checkpoint requires four gates: committed, tested, documented, stable verification.

### Milestone 1: Platform Skeleton and Chat Echo
- Must be committed:
  - Basic app bootstrap
  - Chat endpoint contract
  - Minimal web chat round-trip
- Must be tested:
  - Contract validation tests
  - Smoke test for browser to backend response
- Must be documented:
  - API request and response schema
  - Environment variable list
- Stable verification:
  - Fresh clone setup works and chat loop runs on first attempt

### Milestone 2: Persistent Core Data Model
- Must be committed:
  - Baseline models and migrations
  - Tenant scoping fields
- Must be tested:
  - Migration up and down
  - Multi-tenant data isolation checks
- Must be documented:
  - Table map and schema intent
  - Migration rollback notes
- Stable verification:
  - Clean database bootstrap reproducible

### Milestone 3: First Operational Agent (Customer)
- Must be committed:
  - Customer agent and create customer tool
  - Input validation
- Must be tested:
  - Happy path and duplicate handling
  - Validation failures
- Must be documented:
  - Agent tool contract and examples
- Stable verification:
  - Natural language customer create flow works with deterministic outcomes

### Milestone 4: Product Agent and Context Continuity
- Must be committed:
  - Product toolset
  - Conversation state persistence
- Must be tested:
  - Multi-turn slot filling
  - Fuzzy lookup and disambiguation
- Must be documented:
  - State trimming policy
- Stable verification:
  - Context survives multi-turn interactions without wrong writes

### Milestone 5: Invoicing Core (GST and PDF)
- Must be committed:
  - Deterministic GST service
  - Invoice creation and PDF generation
- Must be tested:
  - Intra-state and inter-state tax logic
  - Rounding and exempt item tests
  - DB to text to PDF reconciliation
- Must be documented:
  - GST rules and assumptions
  - PDF field mapping
- Stable verification:
  - Invoice totals match across storage, response, and PDF

### Milestone 6: Payment and Reporting Loop
- Must be committed:
  - Payment flows and report query tools
  - Reminder scheduling path
- Must be tested:
  - Partial and full payment status transitions
  - Report aggregation correctness
- Must be documented:
  - Report definitions
  - Reminder semantics and confirmation behavior
- Stable verification:
  - Full owner operational loop works end-to-end

### Milestone 7: Customer Boundary and Draft Orders
- Must be committed:
  - Mode resolver and scoped sales tools
  - Draft order lifecycle
- Must be tested:
  - Adversarial boundary tests
  - Draft to owner confirmation to invoice path
- Must be documented:
  - Boundary policy and disallowed data matrix
- Stable verification:
  - Customer mode cannot access owner-only data under any tested prompt

### Milestone 8: WhatsApp Transport Integration
- Must be committed:
  - Transport adapter and identity mapping
  - Idempotency handling
- Must be tested:
  - Webhook replay behavior
  - Owner and customer mapping correctness
- Must be documented:
  - Transport contract and retry model
- Stable verification:
  - WhatsApp flow parity with web flow on core scenarios

### Milestone 9: Compliance and Hardening
- Must be committed:
  - E-invoice and E-way integrations
  - Voice path and mixed-language handling
- Must be tested:
  - Compliance contract tests
  - Fault and fallback tests
  - Final end-to-end ship tests
- Must be documented:
  - Compliance trigger conditions
  - External dependency failure playbook
- Stable verification:
  - Ship test passes with no critical known blocker

## 3. Daily Development Rules

### How to start the day
- Pull latest main.
- Review previous day checkpoint status.
- Choose one bounded objective aligned to current week and milestone.
- Write day plan in implementation log before coding.
- Create branch before first code change.

### How to end the day
- Ensure code compiles and tests for touched scope pass.
- Commit all coherent work (no hidden local-only changes).
- Update implementation log with outcomes and blockers.
- Create daily checkpoint tag only if day meets stable-day criteria.
- Push branch to remote.

### What must be recorded in IMPLEMENTATION_LOG.md
- Date and time window
- Week, day, milestone
- Requirement source section
- What was built
- Why it was built
- Files changed
- Tests run and results
- Risks discovered
- Rollback note
- Next action

## 4. Rollback Strategy

If something breaks, use controlled rollback rather than panic edits.

### How to identify the last stable version
- Prefer most recent stable milestone tag.
- If no milestone tag, use most recent stable weekly tag.
- If no weekly tag, use latest stable daily tag.
- Verify selected tag has passing test evidence in implementation log.

### How to revert safely
- Do not reset main history.
- Revert using dedicated recovery branch:
  - Create branch from main
  - Revert suspect commit range
  - Re-run required tests
  - Merge recovery branch after review
- For migration breakage:
  - Restore to last migration-safe checkpoint
  - Apply corrective migration forward
  - Avoid destructive manual DB edits where possible

### How to recover work without losing progress
- Preserve broken branch for forensic review.
- Cherry-pick known-good commits into recovery branch.
- Re-implement only failed slices behind feature flags if needed.
- Document root cause and prevention rule in implementation log and risk register.

## 5. Traceability Strategy

For every feature, maintain a trace record with mandatory fields:
- Requirement source:
  - Spec section and requirement text summary
- Files changed:
  - Exact changed files
- Tests written:
  - Unit, integration, and end-to-end references
- Related commits:
  - Commit hashes and branch name

Required implementation: add one traceability block per feature completion in IMPLEMENTATION_LOG.md and keep a running index.

Suggested trace record template:
- Feature name
- Requirement source section
- Week and day built
- Files changed
- Tests added or updated
- Related commits
- Rollback commit or tag reference

## 6. Definition of Stable Checkpoint

### Stable Day
A day is stable only if:
- Day objective is complete or safely paused.
- Touched tests pass.
- No known critical regression introduced.
- Implementation log entry is complete.
- Branch is pushed and recoverable.

### Stable Week
A week is stable only if:
- Weekly completion criteria from roadmap are met.
- All required week-level tests pass.
- Risks and blockers are documented with owner and next action.
- Weekly summary and recovery notes are recorded.
- Weekly tag created.

### Stable Milestone
A milestone is stable only if:
- Milestone deliverables are complete.
- Milestone test matrix passes.
- Security and data-boundary checks pass where applicable.
- Documentation is updated for setup, behavior, and rollback.
- Milestone tag created and verified from fresh clone.

## 7. Backup Strategy

### GitHub backup
- Push all active branches daily.
- Protect main with pull request requirement and no force-push.
- Create release or checkpoint tags for stable day, week, milestone.
- Keep remote as source-of-truth for recovery.

### Local backup
- Keep one daily local bundle or archive of repo state.
- Keep database snapshot for migration-heavy weeks.
- Keep environment setup notes and dependency lock references.

### Documentation backup
- Commit documentation changes with code changes on same day.
- Ensure IMPLEMENTATION_LOG.md is updated daily.
- Keep ROADMAP and RISK_REGISTER synchronized with actual state.
- At each weekly checkpoint, export a concise status snapshot for rapid re-onboarding.

## Rapid Return Protocol (After Long Pause)

When returning after 1 month:
- Read latest milestone tag notes.
- Read last 10 entries of IMPLEMENTATION_LOG.md.
- Read open risks in RISK_REGISTER.md.
- Checkout latest stable checkpoint tag first, then branch for new work.
- Run baseline test suite before any new change.

If this protocol is followed, project state should be understandable and recoverable within one working session.
