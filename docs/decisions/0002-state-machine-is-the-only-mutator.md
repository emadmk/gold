# ADR-0002 — Domain mutations go through `apps.audit.state_machine`

* **Status:** Accepted (2026-05-14)
* **Related:** `docs/OBSERVABILITY.md`

## Context

We need every state transition (order, payment_attempt, kyc, delivery,
vendor) to be auditable in Elasticsearch and to be safe under concurrency.

## Decision

* No service code may set `order.state = "paid"` directly.
* Instead, the service calls `order_sm.fire(order, trigger="payment.verified")`.
* The state machine validates the (from, trigger) pair, runs the guard,
  commits the new state, and emits the declared `side_effects` events.
* CI gate `event_coverage` enforces that every declared event kind is
  also in the catalogue.

## Consequences

* Every legal trajectory is documented as data, not code.
* Removing the state machine, removing a transition, or skipping a side
  effect breaks CI.
* Adding a new business event ("subscription started") is a one-line edit
  in `catalogue.py` plus a new `Transition(...)` in `state_machine.py`.
