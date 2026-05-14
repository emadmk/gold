# KeyhanGold — Forward Roadmap (20 future features)

> **Don't build any of these yet.** This document lists the 20 capabilities
> we expect to deliver in the 18 months following GA, and — for each one —
> the architectural seam that has **already been included** in v1 so the
> feature can be delivered as an additive change (no rewrite, no
> data-model break, no API-version bump).
>
> When a future PR delivers one of these, it must update the **"Status"**
> column and link back to the relevant ADR.

The pattern is the same for every entry:

> *Capability* → *Seam in v1* → *Estimated cost when picked up*

The seams listed below are real: they are referenced in the code today
and protected by a CI check (`make seam-check`).

---

## Cross-cutting seams used by many of the 20 features

These exist in v1 even though no feature uses them yet:

- **Feature flags** — `apps/security/feature_flags.py` (Redis-backed,
  per-user / per-role / per-percentage rollout). Toggle is itself
  audited via `system.feature_flag.toggled`.
- **Event bus (Redis Streams)** — already carries domain events; any new
  feature can register a `consumer_group` to react to existing events
  with **zero coupling** to producers.
- **Strategy registry** — `apps/<domain>/strategies/__init__.py`
  exposes a `register(name)` decorator. We use it today for pricing
  formulas and gateways; tomorrow it'll host new fee, AML, fraud, and
  yield strategies.
- **Plugin loader** — `apps/security/plugins.py` walks
  `entry_points("keyhan.plugins")` so third-party extensions can be
  shipped as separate packages.
- **Polymorphic `Order.kind`** — already an enum; new kinds (loans,
  subscriptions, gifting) drop in without schema migration.
- **Polymorphic `WalletTransaction.asset`** — supports `rial`, `gold`,
  `silver` today and will accept `usdt`, `xau-token`, etc., on day one.
- **`metadata: JSONField`** on every `Order`, `OrderItem`, `Product`,
  `PaymentAttempt`, `DeliveryRequest`, `KYCSubmission`, `Vendor`.
- **Event versioning** — `event.version` in the envelope; consumers must
  switch on it.
- **`X-Request-Id` + OpenTelemetry trace context** — propagated by every
  service, so any new service joining the bus is observable from day 1.
- **Tenant column** — `Order`, `Product`, `Vendor`, `Wallet` all carry
  `tenant_id` (default = `default`). Multi-tenant (#14 below) is
  therefore a config switch, not a refactor.

---

## The 20

### 1. AI-powered fraud / AML scoring
- **Why:** Replace static velocity rules with a model.
- **Seam:** AML decisions already pass through
  `apps/security/risk/engine.py::score(event_dict) -> RiskDecision`.
  v1 uses a deterministic rule-based scorer; v2 will swap it for a
  remote ML endpoint (`RISK_ENGINE_URL`). Event input is already
  schema-stable.
- **Cost when delivered:** add a strategy implementation, no model
  changes, no breaking events.

### 2. Native mobile apps (iOS / Android)
- **Why:** Reach customers without a browser.
- **Seam:** Backend is API-first (DRF + spectacular). JWT is delivered
  via cookies for web *and* via response body for `Authorization` use.
  WebSocket endpoints already accept `Sec-WebSocket-Protocol = jwt`.
- **Cost:** ship React Native shell + reuse OpenAPI client.

### 3. Recurring buy plans (DCA)
- **Why:** Lower friction for regular savers.
- **Seam:** `apps/orders` already supports `Order.kind="buy_gold"`. A
  `SubscriptionPlan` model + a Celery beat job that issues
  `Order(kind="buy_gold", source="dca")` covers it. The state machine
  needs no change.
- **Cost:** ~ 1 model, 1 cron, 1 page.

### 4. Gift gold (one-tap gifting)
- **Why:** Viral loop.
- **Seam:** Internal transfer already exists (`wallet.transfer.*`). A
  `GiftLink` token reuses the same path; recipient flow uses the
  existing OTP/KYC.
- **Cost:** ~ 1 model, 1 small page.

### 5. Referral & loyalty program
- **Why:** Acquisition.
- **Seam:** `User` has a `referred_by` FK in v1 (nullable, unused). The
  `wallet.adjustment` event will carry a `reason="referral_reward"`.
- **Cost:** 1 service, 1 dashboard panel.

### 6. Stop-loss / take-profit orders
- **Why:** Power users.
- **Seam:** `Order.kind` is an enum and `PriceTick` is queryable by
  Celery; `apps/orders/services/conditions.py` already exists with a
  stub `ConditionEngine`.
- **Cost:** add `OrderCondition` model + worker.

### 7. Margin / leverage trading
- **Why:** New revenue stream (interest + fees).
- **Seam:** Wallets already have `locked_mg`/`locked_rial` and the
  invariant check is parameterised. A `CreditLine` model can lean on
  the same locking primitives.
- **Cost:** higher (regulatory work); but the ledger is ready.

### 8. Gold-backed loans
- **Why:** Customers borrow rials against pledged gold.
- **Seam:** Same `locked_mg` primitive. `LoanContract` model.
- **Cost:** moderate; ledger and SM already support it.

### 9. Crypto-backed gold / tokenized XAU
- **Why:** Bridge to DeFi.
- **Seam:** `WalletTransaction.asset` is polymorphic; a `xau_token`
  asset and a `chain` field in `metadata` cover it. No schema change.
- **Cost:** add custody + on-chain worker.

### 10. Multi-currency wallets (USD, EUR, AED, USDT)
- **Why:** International users.
- **Seam:** `RialWallet` is really a "FiatWallet"; the column is
  `balance_rial` but a `currency` enum is already present (default
  `IRR`). Add new rows for new currencies.
- **Cost:** light refactor of presentation; data layer ready.

### 11. Multi-language (English, Arabic, Turkish)
- **Why:** Diaspora.
- **Seam:** All strings flow through `_("…")` / `t("…")`; locale router
  is in place at `/[lang]/…` (Next.js i18n).
- **Cost:** translation work + RTL toggling already supported.

### 12. AI price-prediction widgets
- **Why:** UX differentiator.
- **Seam:** WebSocket pipeline already pushes prices; a new channel
  `prices_forecast` will be added side-by-side with no consumer changes.
- **Cost:** ML pipeline + frontend chart.

### 13. Voice assistant for trades
- **Why:** Accessibility.
- **Seam:** Same API; voice frontend issues the same authenticated
  requests. No backend change required.
- **Cost:** frontend + STT/TTS.

### 14. White-label B2B API for third-party shops
- **Why:** Embed gold buying into other Iranian apps.
- **Seam:** Tenant column on every aggregate; OAuth2 client model in
  `apps/accounts/oauth.py` (stub). RBAC supports a `partner` role.
- **Cost:** OAuth flows + per-tenant rate limits.

### 15. Auction house for jewelry
- **Why:** Marketplace expansion.
- **Seam:** `Product` already supports custom `metadata`. New `Order.kind="auction_bid"` and a `bidding` Channels consumer fit on top.
- **Cost:** ~ 2 models, 1 consumer.

### 16. Live streaming with vendors
- **Why:** Engagement.
- **Seam:** Channels infrastructure (rooms by `vendor_slug`) is in
  place; storage abstraction is S3-compatible (MinIO).
- **Cost:** SFU adapter (LiveKit / Mediasoup).

### 17. Subscription tiers (Plus / Pro)
- **Why:** Recurring revenue.
- **Seam:** `User.tier` enum + `Order.kind="subscription"`. Pricing
  formulas already vary by `User.tier`.
- **Cost:** ~ 1 model, 1 cron, billing rules.

### 18. Insurance for physical delivery
- **Why:** Trust on high-value shipments.
- **Seam:** `DeliveryRequest.metadata` already accepts arbitrary keys.
  An `InsurancePolicy` model attaches via FK.
- **Cost:** integrate an Iranian insurer's API.

### 19. Tax automation & financial reports (year-end)
- **Why:** Compliance + customer service.
- **Seam:** Every `WalletTransaction` carries `rial_amount` and
  `created_at`; PDF generation pipeline (weasyprint) is already used
  for invoices.
- **Cost:** report templates.

### 20. Social trading / follow-a-trader
- **Why:** Network effects.
- **Seam:** Domain events stream is already public-by-key; a new
  consumer group `social.feed` can subscribe to `orders.completed`
  events for users that opted-in (`User.share_trades` flag — present
  in v1 schema, default `false`).
- **Cost:** privacy gating + UI.

---

## Status table

| #  | Capability                          | Status   | Owner | ADR |
|----|-------------------------------------|----------|-------|-----|
| 1  | AI fraud / AML scoring              | planned  | —     | —   |
| 2  | Native mobile apps                  | planned  | —     | —   |
| 3  | Recurring buy plans                 | planned  | —     | —   |
| 4  | Gift gold                           | planned  | —     | —   |
| 5  | Referral & loyalty                  | planned  | —     | —   |
| 6  | Stop-loss / take-profit             | planned  | —     | —   |
| 7  | Margin / leverage                   | planned  | —     | —   |
| 8  | Gold-backed loans                   | planned  | —     | —   |
| 9  | Tokenised XAU                       | planned  | —     | —   |
| 10 | Multi-currency wallets              | planned  | —     | —   |
| 11 | Multi-language                      | planned  | —     | —   |
| 12 | AI price-prediction widgets         | planned  | —     | —   |
| 13 | Voice assistant                     | planned  | —     | —   |
| 14 | White-label B2B API                 | planned  | —     | —   |
| 15 | Auction house                       | planned  | —     | —   |
| 16 | Live streaming                      | planned  | —     | —   |
| 17 | Subscription tiers                  | planned  | —     | —   |
| 18 | Delivery insurance                  | planned  | —     | —   |
| 19 | Tax automation                      | planned  | —     | —   |
| 20 | Social trading                      | planned  | —     | —   |

When a feature ships, change `planned → in-progress → released`, link
to an ADR in `docs/decisions/NNNN-feature-X.md`, and check that the
seam wasn't violated (`make seam-check` keeps you honest).

---

## Why these seams will not be removed

All the seams listed above are **referenced in the v1 code**, even when
they look unused. They are protected by the `make seam-check` script:

- Removing the `tenant_id` column → fails.
- Removing the `metadata` JSON field on the listed aggregates → fails.
- Removing `User.referred_by`, `User.tier`, `User.share_trades` → fails.
- Removing `apps/security/feature_flags.py` → fails.
- Removing the strategy-registry pattern → fails.

In other words, **the v1 code carries a paid bill of options.** The 20
features above are the options we already paid for.
