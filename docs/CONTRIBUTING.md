# Contributing to KeyhanGold

Welcome — this document is the **shortest path** to land a clean change.

## TL;DR

```bash
make up              # bring the dev stack up
make migrate seed    # apply migrations + seed dev data
make test            # 97+ tests must pass
make all-checks      # observability + seam check
```

Then open a PR; CI must be green.

## Rules of engagement

1. **Money in rials, weight in milligrams, both `int64`.** No floats.
   See `docs/decisions/0001`.
2. **No state change without `state_machine.fire(...)`.** See `0002`.
3. **No event without `catalogue.register(...)`.** CI breaks otherwise.
4. **Every new endpoint** must appear in the OpenAPI schema (drf-spectacular
   does this automatically when you use DRF views).
5. **Persian** for end-user strings; English for log lines.
6. **HttpOnly cookies** for tokens — never localStorage.
7. **Conventional Commits** for git messages
   (e.g. `feat(orders): add 30min expiry`).

## Adding a new event kind

```python
# 1) Register in apps/audit/catalogue.py
_r("orders.gift_redeemed", "domain")

# 2) Emit
from apps.audit.emit import emit_event
emit_event("orders.gift_redeemed", target={"type": "order", "id": ...})

# 3) Update the side_effects in the relevant Transition declaration
#    in apps/audit/state_machine.py
```

`make observability-check` verifies (1) and (3) are in sync.

## Adding a state-machine transition

Open `apps/audit/state_machine.py`, find the right machine, append:

```python
order_sm.add(Transition(
    "order", "completed", "shipped", "order.ship",
    side_effects=("orders.shipped", "delivery.requested"),
))
```

Then re-register `orders.shipped` in `catalogue.py`. CI will tell you if
you missed something.

## Adding a payment gateway (roadmap #14)

```python
# apps/payments/gateways/<name>.py
from .base import BaseGateway, register

@register("yourgateway")
class YourGateway(BaseGateway):
    def request(self, req): ...
    def verify(self, authority, amount_rial): ...
```

The gateway is now selectable from the user's topup page and the admin
panel — no other changes needed.

## Tests

Anything money-touching MUST have a test. See `backend/tests/` for
patterns:

* `test_wallet_invariants.py` — DB-level checks
* `test_state_machines.py` — SM transitions
* `test_e2e_smoke.py` — full flow
* `test_pricing_formulas.py` — formula sensitivity

Run with `pytest -q`; goal: ≥ 80 % branch coverage on
`apps/{wallet,orders,payments,pricing}`.

## Code review checklist

Reviewers should reject if:
* Floats appear in money/weight arithmetic.
* A `state` field is set directly (without `state_machine.fire`).
* A new `emit_event` kind is missing from the catalogue.
* Tokens or PII are logged in plaintext.
* New PII columns aren't encrypted (`EncryptedCharField`).
* `tenant_id` was removed from any aggregate.
* `metadata` JSON field was removed from any aggregate.

## Releasing

1. Bump `SERVICE_VERSION` in `.env`.
2. Tag the commit `vX.Y.Z`.
3. Push the tag; CI builds + signs the container with `cosign` and
   attaches the SBOM.
