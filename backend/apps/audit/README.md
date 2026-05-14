# `apps.audit` — Observability core

This app is the **single source of truth** for events, state transitions
and traceability.  It implements everything described in
[`docs/OBSERVABILITY.md`](../../../docs/OBSERVABILITY.md).

## What's here

| File | Purpose |
|------|---------|
| `context.py`        | `contextvars`-based correlation IDs (request_id, trace_id, user_id) |
| `middleware.py`     | Sets the request context on every HTTP request |
| `log.py`            | structlog bootstrap with PII redaction + correlation injection |
| `schema.py`         | pydantic Envelope — every event MUST validate against this |
| `catalogue.py`      | The authoritative list of event kinds. Adding an event without registering it here breaks CI. |
| `state_machine.py`  | Central state machines (order / kyc / delivery / vendor / payment_attempt). Every transition declares the events it emits. |
| `sinks.py`          | `RedisStreamSink` (prod) and `InMemorySink` (tests) |
| `emit.py`           | `emit_event(...)` — the function the rest of the code calls |
| `bootstrap.py`      | One-shot setup: structlog, Sentry, OpenTelemetry |
| `checks.py`         | CI scripts: `event_coverage`, `catalogue`, `sm_coverage` |
| `views.py`          | `/health`, `/metrics` |
| `models.py`         | `IdempotencyKey` (webhook dedup) + `AuditEntry` (forensic copy) |

## Usage

```python
from apps.audit.emit import emit_event
from apps.audit.state_machine import order_sm

# Fire a transition (also emits declared side_effects):
order_sm.fire(order, trigger="payment.verified", data={"amount": 17_241_600})

# Or emit a standalone event:
emit_event(
    "wallet.gold.buy",
    actor={"type": "user", "id": str(user.id)},
    target={"type": "order", "id": str(order.id)},
    data={"asset": "gold", "mg_amount": 1000},
)
```

If `kind` is not in `catalogue.py`, `emit_event` raises immediately.

## CI gates

```bash
make observability-check
# == python -m apps.audit.checks event_coverage
# == python -m apps.audit.checks catalogue
# == python -m apps.audit.checks sm_coverage
```
