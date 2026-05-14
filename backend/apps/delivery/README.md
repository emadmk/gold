# `apps.delivery` — Physical delivery requests

When a user wants their gold delivered as a sealed bar.

## Model

`DeliveryRequest` — `state` ∈ `pending / approved / minting / shipped /
delivered / cancelled`. Carries weight (`requested_mg`),
`bars_breakdown` (e.g. `{"1g": 2, "5g": 1}`), shipping address +
recipient KYC info, optional `tracking_code`, and `processing_fee_rial`.

## Service

`request_delivery(user, mg, address, name, nid, phone, bars=None)`:
* validates against `min_physical_delivery_mg` (default 5000 mg = 5 g),
* computes `processing_fee_rial = rial_value × delivery_processing_fee_pct`
  (default 3 %),
* atomically burns the gold (`wallet.debit_asset`) and debits the fee,
* creates the `DeliveryRequest(state="pending")`.

`transition(req, trigger, actor=…)` advances the SM
(`delivery.approve / mint / ship / deliver / cancel`).

## Endpoints

```
GET  /api/v1/delivery                  ← user's own
POST /api/v1/delivery/request          (KYC required)
GET  /api/v1/admin/delivery            ← open queue
POST /api/v1/admin/delivery/<id>/<action>
  action ∈ approve / mint / ship / deliver / cancel
  body {tracking_code} when shipping
```

## Events emitted

`delivery.requested`, `delivery.state.changed`.

## Admin actions

The Django admin also exposes bulk actions for the same five
transitions; each one runs through `delivery_sm.fire(...)` so events
are emitted exactly as the API path would.
