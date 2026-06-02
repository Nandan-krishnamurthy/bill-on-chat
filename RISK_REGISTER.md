# Project Beta Risk Register

## Risk 1 - Owner/Customer Boundary Leakage

Priority: Critical
Phase: 1 & 2

Description:
Customer Mode must never access owner-only information such as dues, reports, customer balances, exact inventory quantities, cost price, or margins.

Mitigation:
- Server-side mode resolution
- Mode-specific tool binding
- Adversarial security tests
- Fail closed on ambiguity

Status:
Open

---

## Risk 2 - GST Computation Errors

Priority: Critical
Phase: 1 & 2

Description:
Incorrect GST calculations may produce invalid invoices and compliance issues.

Mitigation:
- Deterministic GST engine
- Unit tests
- Golden test datasets
- Invoice/PDF reconciliation

Status:
Open

---

## Risk 3 - WhatsApp Idempotency

Priority: High
Phase: 2

Description:
Duplicate WhatsApp deliveries may create duplicate invoices or payments.

Mitigation:
- Message deduplication
- Idempotent operations
- Replay testing

Status:
Deferred until Phase 2

---

## Risk 4 - External Provider Dependency

Priority: High
Phase: 2

Description:
GST APIs, E-Invoice providers, and voice providers may fail or change.

Mitigation:
- Adapter layer
- Retry policy
- Graceful degradation

Status:
Deferred until Phase 2