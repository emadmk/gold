# `apps.payments` — Multi-gateway payment abstraction

Three Iranian payment processors hide behind one `BaseGateway` ABC.

## Architecture

```
        ┌────────────────┐
        │  Order(kind=   │
        │  "wallet_topup"│
        │  + amount_rial)│
        └────────┬───────┘
                 │
                 ▼
   PaymentAttempt (state="pending")
                 │
   ┌─────────────┴─────────────┐
   │ gateways/<name>.request() │
   └─────────────┬─────────────┘
                 │
                 ▼  (state="redirected")
        Gateway hosted page
                 │
                 ▼
   GET /payments/callback/<gw>?authority=…
   handle_callback(...) — idempotent:
   ┌───────────────────────────────┐
   │ IdempotencyKey check          │
   │ select_for_update on order    │
   │ gateways/<name>.verify()      │
   │ payment_attempt_sm.fire(...)  │
   │ order_sm.fire("payment.verified")│
   │ complete_buy_order(order)     │
   └───────────────────────────────┘
```

## Models

| Model | Purpose |
|-------|---------|
| `PaymentAttempt` | One row per gateway interaction. Stores `authority`, `ref_id`, masked PAN, `state`, raw req/resp. |

## Gateways

* `gateways/zarinpal.py` — Zarinpal v4 (sandbox + prod).
* `gateways/idpay.py` — IDPay v1.1.
* `gateways/payping.py` — PayPing v2 (note: amount in **toman**).

All registered via `@register("name")` in `gateways/base.py`. To add a
new gateway: drop a file, register, that's it.

## Idempotency

`apps/payments/services.py::handle_callback` uses a separate
`transaction.atomic()` to insert the `IdempotencyKey`, so a verify
failure in the second transaction cannot roll the key back. A
duplicate callback returns the same `PaymentAttempt` and emits
`payments.webhook.duplicate`.

## Endpoints

```
POST /api/v1/wallet/topup                ← creates Order + PaymentAttempt → redirect_url
GET  /api/v1/payments/callback/<gw>      ← idempotent
POST /api/v1/payments/callback/<gw>
```

## Events emitted

`payments.attempt.created / redirected / callback / verified / failed`,
`payments.webhook.duplicate`.

## Tests

`tests/test_payment_gateway.py` — happy + error path for each gateway
with mocked `httpx.Client`.
