# KeyhanGold — API Reference

This document is the human-readable mirror of the OpenAPI 3.1 schema
served at `GET /api/v1/schema/swagger-ui/`. When in doubt, the
swagger-ui is always more current.

## Conventions

* **Base URL**: `/api/v1`
* **Authentication**: JWT in HttpOnly cookie `keyhan_access` (default)
  or `Authorization: Bearer <token>` header.
* **Refresh**: `keyhan_refresh` cookie; rotation is automatic, the old
  refresh is blacklisted.
* **Errors**: `400` returns `{"detail": "خطای فارسی", "errors": …}`
* **Pagination**: list endpoints return
  `{ "count", "next", "previous", "results": [...] }`.
* **Correlation**: every response carries `X-Request-Id`; paste it
  into Kibana to see the entire chain.

## 1. Auth & profile (`apps.accounts`)

| Verb | Path | Auth | Purpose |
|------|------|------|---------|
| POST | `/auth/otp/request` | none | Send a 6-digit SMS code to the phone |
| POST | `/auth/otp/verify`  | none | Verify the code and start a session (sets JWT cookies) |
| POST | `/auth/logout` | user | Blacklist refresh, clear cookies |
| GET  | `/me` | user | Current user |
| PATCH| `/me` | user | Update first_name / last_name / email / address / share_trades |
| GET  | `/kyc` | user | Current KYC state + reasons |
| POST | `/kyc` | user | Multipart upload of national-card / selfie / video. Each file is magic-byte validated; images are re-encoded |
| POST | `/me/2fa/enroll` | user | Generate a TOTP secret, return `otpauth://` URI |
| POST | `/me/2fa/confirm` | user | Confirm enrollment with a fresh TOTP code |
| POST | `/me/2fa/disable` | user | Disable 2FA after confirming with a TOTP code |

## 2. Wallet (`apps.wallet`)

| Verb | Path | Auth | Purpose |
|------|------|------|---------|
| GET  | `/wallet` | user | Combined rial + gold + silver snapshot |
| GET  | `/wallet/transactions` | user | List of `WalletTransaction` rows |
| POST | `/wallet/withdraw/otp` | user | Send OTP for a withdraw request |
| POST | `/wallet/withdraw` | user (+KYC) | Submit withdraw with rial amount + OTP |
| POST | `/wallet/transfer/otp` | user (+KYC) | Send OTP for an internal transfer |
| POST | `/wallet/transfer` | user (+KYC) | Move gold/silver to another wallet address with OTP |

## 3. Pricing (`apps.pricing`)

| Verb | Path | Auth | Purpose |
|------|------|------|---------|
| GET  | `/prices` | none | Snapshot of every `source_key` (rial, integer) |
| POST | `/prices/quote` | user | Issue a 30-second `PriceQuote` for (asset, side) |
| WS   | `/ws/prices/` | none | Live price updates every ~30 s |

## 4. Trade (`apps.orders`)

| Verb | Path | Auth | Purpose |
|------|------|------|---------|
| POST | `/trade/buy/gold` | user (+KYC) | Quote-then-place: body `{quote_id, mg_amount}` |
| POST | `/trade/sell/gold` | user (+KYC) | same |
| POST | `/trade/buy/silver` | user (+KYC) | same |
| POST | `/trade/sell/silver` | user (+KYC) | same |
| GET  | `/orders` | user | List user's orders |
| GET  | `/orders/{id}` | user | Detail (with payment_deadline countdown) |
| POST | `/orders/{id}/cancel` | user | Cancel an `awaiting_payment` order |
| GET  | `/orders/{id}/invoice` | user | Stream the PDF (auto-generates if missing) |

## 5. Payments (`apps.payments`)

| Verb | Path | Auth | Purpose |
|------|------|------|---------|
| POST | `/wallet/topup` | user | Start a topup; body `{amount_rial, gateway}`; returns `redirect_url` |
| GET/POST | `/payments/callback/{gateway}` | none | Gateway callback; idempotent — second call with same `Authority` is a no-op and emits `payments.webhook.duplicate` |

## 6. Delivery (`apps.delivery`)

| Verb | Path | Auth | Purpose |
|------|------|------|---------|
| GET  | `/delivery` | user | List user's delivery requests |
| POST | `/delivery/request` | user (+KYC) | Body: `{requested_mg, shipping_address, recipient_name, recipient_national_id, recipient_phone, bars_breakdown}` |

## 7. Marketplace (`apps.marketplace`)

### Public
| Verb | Path | Purpose |
|------|------|---------|
| GET  | `/marketplace/products` | List active products |
| GET  | `/marketplace/products/{slug}` | Product detail with `computed_price_rial` |
| GET  | `/marketplace/vendors` | List approved vendors |
| GET  | `/marketplace/vendors/{shop_slug}` | Vendor detail |

### Vendor self-service (`is_vendor=True`)
| Verb | Path | Purpose |
|------|------|---------|
| POST | `/vendor/apply` | Multipart: shop_name, shop_slug, legal_name, iban, business_license, union_license, logo |
| GET  | `/vendor/me` | Current vendor profile |
| PATCH| `/vendor/me` | Edit shop_name / description / city / address / phone / iban |
| GET  | `/vendor/products` | List vendor's products |
| POST | `/vendor/products` | Create product |
| GET  | `/vendor/orders` | Orders received by this vendor |
| GET  | `/vendor/settlements` | Settlement history |

### Checkout (KYC-verified user)
| Verb | Path | Purpose |
|------|------|---------|
| POST | `/marketplace/checkout` | `{items: [{product_id, quantity}], shipping_address, recipient_name, recipient_phone}` |

## 8. Notifications (`apps.notifications`)

| Verb | Path | Auth | Purpose |
|------|------|------|---------|
| GET  | `/notifications` | user | List user notifications |
| POST | `/notifications/{id}/read` | user | Mark one as read |
| POST | `/notifications/read-all` | user | Mark all as read |
| WS   | `/ws/me/` | user | Live push channel for this user |

## 9. Blog (`apps.blog`)

| Verb | Path | Purpose |
|------|------|---------|
| GET  | `/blog/posts` | Published posts only |
| GET  | `/blog/posts/{slug}` | Detail; increments `views` |

## 10. Admin (`apps.admin_panel`, role `is_staff`)

| Verb | Path | Purpose |
|------|------|---------|
| GET  | `/admin/kpi` | Aggregated KPIs (users, vendors, orders, balances) |
| GET  | `/admin/kyc-queue` | Pending KYC submissions |
| POST | `/admin/kyc/{id}/approve` | Approve KYC |
| POST | `/admin/kyc/{id}/reject` | Reject with `{reason}` |
| GET  | `/admin/users` | List users |
| POST | `/admin/users/{id}/freeze` | Freeze + emit `accounts.user.frozen` |
| POST | `/admin/users/{id}/unfreeze` | |
| GET  | `/admin/vendors-list` | All vendors |
| POST | `/admin/vendors/{id}/approve` | |
| POST | `/admin/vendors/{id}/suspend` | |
| GET  | `/admin/orders` | All orders |
| GET  | `/admin/payments` | All payment attempts |
| GET  | `/admin/delivery` | Open delivery requests |
| POST | `/admin/delivery/{id}/{action}` | Action ∈ approve/mint/ship/deliver/cancel; `{tracking_code}` for ship |
| GET  | `/admin/formulas` | List pricing formulas |
| PUT  | `/admin/formulas` | Bulk-update; each change emits `pricing.formula.updated` |
| GET  | `/admin/settlements` | Vendor settlements |
| GET  | `/admin/audit-log` | Local mirror of recent events |

## 11. Health & metrics

| Verb | Path | Purpose |
|------|------|---------|
| GET  | `/health/` | Liveness + dependency check (`db`, `redis`); 503 when any failed |
| GET  | `/metrics/` | Prometheus exposition (django-prometheus + custom) |
| GET  | `/api/v1/schema/` | OpenAPI 3.1 JSON |
| GET  | `/api/v1/schema/swagger-ui/` | Interactive swagger |
| GET  | `/api/v1/schema/redoc/` | Redoc-rendered docs |

## 12. WebSocket events

### `/ws/prices/`

Public. On connect, server sends a `snapshot` of all cached prices.
Then on every crawler tick:

```json
{
  "type": "price_update",
  "ts": "2026-05-14T17:30:00Z",
  "data": {
    "gold_18k_750": 17241600,
    "silver_999":   396000,
    "coin_emami":   480000000,
    "usd_free":     870000,
    "buy_per_mg":   17328,
    "sell_per_mg":  17155,
    "silver_buy_per_mg":  410,
    "silver_sell_per_mg": 380
  }
}
```

### `/ws/me/`

Per-user, requires auth via cookie. The backend pushes:

```json
{
  "id": "01HX...",
  "kind": "success",
  "title": "سفارش شما تکمیل شد",
  "body": "...",
  "url": "/orders/<uuid>",
  "created_at": "2026-05-14T17:31:11Z"
}
```

## 13. Rate limits

| Surface | Limit |
|---------|-------|
| `POST /auth/otp/request` | 5 / 15 min / phone |
| `POST /auth/otp/verify`  | 5 / 15 min / phone |
| `POST /wallet/withdraw`  | 3 / hour / user |
| `POST /orders/...`       | 60 / min / user |

Beyond these: per-IP fallback returns `429` with `Retry-After`.

## 14. Idempotency

* `payments/callback/{gateway}` deduplicates by
  `IdempotencyKey(scope="payment.callback", key=<gw>:<authority>)`.
  A duplicate call returns the same `PaymentAttempt` and emits
  `payments.webhook.duplicate`.

## 15. Versioning

* Schema lives under `/api/v1/`. Breaking changes will go to `/api/v2/`
  and run side-by-side for a release.
* `event.version` exists on every audit envelope for the same reason.
