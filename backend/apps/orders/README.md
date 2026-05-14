# `apps.orders` — Order lifecycle

## Models

| Model | Purpose |
|-------|---------|
| `Order` | The transaction envelope. `kind` ∈ `buy_gold / sell_gold / buy_silver / sell_silver / marketplace / wallet_topup / dca / subscription / auction_bid`. `state` follows the `order` state machine. Carries `payment_deadline` (now + 30 min) and `metadata` JSON. |
| `OrderItem` | Marketplace line item. Snapshots `title`, `unit_price_rial`, `line_total_rial` so future price changes don't rewrite history. |

## Services (`services.py`)

* `submit_buy_gold / submit_sell_gold / submit_buy_silver / submit_sell_silver` —
  validate the quote, create the order, then either settle in-wallet
  (if balance ≥ cost) or leave in `awaiting_payment` for the gateway.
* `complete_buy_order` — debit rial, credit asset, advance through
  `processing → completed`, generate the invoice PDF.
* `cancel_order`, `expire_order` — terminal branches; unlock rial.

## State machine

Declared in `apps.audit.state_machine.order_sm`. See
[`OBSERVABILITY.md §3.2`](../../../docs/OBSERVABILITY.md#32-order-state-machine).

## Invoice PDF

`apps/orders/invoices.py::generate_invoice(order)` renders
`templates/invoices/order.html` with weasyprint and stores the bytes
on `order.invoice_pdf` (MinIO). Called automatically on `settle`.

## Background tasks

* `orders.expire_due` — every 60 s, transitions
  `awaiting_payment → expired` for any order past `payment_deadline`.

## Endpoints

```
POST /api/v1/trade/buy/gold  /sell/gold  /buy/silver  /sell/silver
GET  /api/v1/orders          GET /api/v1/orders/{id}
POST /api/v1/orders/{id}/cancel
GET  /api/v1/orders/{id}/invoice
```

## Events emitted

`orders.created / paid / processing / completed / failed / refunded / expired / cancelled / timer.tick`.

## Tests

`tests/test_state_machines.py::test_order_*`,
`tests/test_e2e_smoke.py::test_topup_buy_gold_sell_gold` and
`::test_order_expiry`.
