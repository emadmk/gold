# `apps.marketplace` — Vendors, products, checkout, settlement

## Models

| Model | Purpose |
|-------|---------|
| `Vendor` | Shop profile, licenses, commission rate, state (`applied / approved / suspended / rejected`). |
| `Product` | Vendor's offerings. `category` ∈ `melted / jewelry / coin / silver`. Carries `karat`, `weight_mg`, fee % and margin %. |
| `VendorSettlement` | Daily payout row (`gross / commission / net`). |

## Services (`services.py`)

* `compute_product_price(product)` — combines latest tick + formula
  with 9 % VAT only on jewelry's `manufacturing_fee + vendor_margin`
  (per Iranian retail-jewelry law).
* `apply_to_vendor(...)` — multipart vendor onboarding.
* `approve_vendor(v, admin=…) / suspend_vendor(v, admin=…)` —
  transitions via `vendor_sm` and emits events.
* `checkout(user, items, …)` — atomic: creates Order + OrderItem rows,
  decrements stock, locks rial, settles immediately if the wallet has
  enough rial.

## Background

* `marketplace.settle_vendors` — daily at 01:00. Aggregates yesterday's
  completed `Order(kind="marketplace")` per vendor, subtracts
  `vendor.commission_rate`, credits the vendor's rial wallet, records
  a `VendorSettlement`.

## Endpoints

```
GET  /api/v1/marketplace/products             /products/{slug}
GET  /api/v1/marketplace/vendors              /vendors/{shop_slug}
POST /api/v1/marketplace/checkout
POST /api/v1/vendor/apply                     (multipart)
GET  /api/v1/vendor/me                        PATCH /vendor/me
GET  /api/v1/vendor/products                  POST /vendor/products
GET  /api/v1/vendor/orders                    GET /vendor/settlements
POST /api/v1/admin/vendors/{id}/approve      /suspend
```

## Events emitted

`marketplace.vendor.applied / approved / suspended`,
`marketplace.product.published / delisted`,
`marketplace.settlement.run`.

## Notes

* Single-vendor carts only (multi-vendor would require parallel
  settlement flows — premature).
* `Product.metadata` JSONField is the seam for roadmap features
  (auction, live-stream, gift).
