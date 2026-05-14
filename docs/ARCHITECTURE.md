# KeyhanGold — Architecture

A 30-minute read for an engineer who needs to understand the whole
system before changing anything important.

## 1. Bird's-eye view

```
                       ┌─────────────────────────────┐
   user browser ─────► │  Traefik 3 (TLS 1.3 + ACME) │
                       └──────┬──────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ┌─────────────────┐           ┌────────────────────┐
      │  Next.js 16     │  /api/*   │  Django 5.2 ASGI   │
      │  React 19       │ ────────► │  Gunicorn+Uvicorn  │
      │  SSR + Edge     │           │  (HTTP REST + WS)  │
      └─────────────────┘           └──────────┬─────────┘
                                               │
              ┌────────────────────────────────┼──────────────────┐
              ▼                                ▼                  ▼
      ┌───────────────┐                ┌───────────────┐   ┌──────────────┐
      │ PostgreSQL 16 │                │   Redis 7     │   │  MinIO       │
      │ (the ledger)  │                │ cache, broker,│   │ (S3 — KYC,   │
      │               │                │ channel layer,│   │  invoices,   │
      │               │                │ event stream  │   │  blog covers)│
      └───────────────┘                └──────┬────────┘   └──────────────┘
                                              │
            ┌─────────────────────────────────┼──────────────────────────┐
            │ Celery worker(s)                │  Channels / Daphne       │
            │ ┌─────────────────────────┐     │  (WebSocket prices,      │
            │ │ pricing.crawl_all  (30s)│     │   per-user notifs)       │
            │ │ orders.expire_due (60s) │     └──────────────────────────┘
            │ │ wallet.consistency (5m) │
            │ │ audit.reconcile   (1h)  │
            │ │ security.aml_tick (10m) │
            │ │ marketplace.settle (1d) │
            │ │ wallet.daily_yield (1d) │
            │ └─────────────────────────┘
            │
            ▼
      ┌──────────────────────────────────────────────────────┐
      │  Redis Streams  ─►  Logstash  ─►  Elasticsearch 8    │
      │  domain_events.*    pipelines    keyhan-events-*-yyyy│
      │                                                      │
      │  Filebeat (stdout)  ──────────►  keyhan-logs-*       │
      │                                                      │
      │                                  Kibana  +  Grafana  │
      └──────────────────────────────────────────────────────┘
```

## 2. The seven layers

| Layer | Code | What it does | Owns |
|-------|------|--------------|------|
| **Edge** | `docker/traefik` | TLS termination, HSTS/CSP, ACME, rate-limit shield | Public IPs |
| **Web** | `frontend/` + `core/asgi` | SSR + HTTP API + WebSocket | URL routes |
| **Domain** | `apps/{orders,wallet,…}/services.py` | Pure business logic; lives in `services.py` modules | Domain invariants |
| **State** | `apps.audit.state_machine` | All transitions; emits events as side-effects | State legality |
| **Ledger** | PostgreSQL tables `wallet_*`, `orders_*` | Append-only money truth | Money invariants |
| **Bus** | Redis Streams (`domain_events.*`) | Decoupled transport for events | At-least-once delivery |
| **Observability** | Elasticsearch + Kibana + Prometheus + Grafana + Sentry | Search, dashboards, traces, alerts | Replay-ability |

## 3. Backend layout

```
backend/
├── core/
│   ├── settings/{base,dev,prod,test}.py    ← split settings
│   ├── celery.py                           ← beat schedule + signals
│   ├── urls.py                             ← root URLconf
│   ├── asgi.py                             ← HTTP + WebSocket router
│   └── wsgi.py
├── apps/
│   ├── audit/         ← Observability core (see backend/apps/audit/README.md)
│   ├── security/      ← Middleware, rate limit, crypto, feature flags, risk
│   ├── accounts/      ← User, OTP, KYC, 2FA, JWT
│   ├── wallet/        ← Rial + gold + silver, transfer, yield
│   ├── pricing/       ← Crawler, ticks, formulas, quotes, WS
│   ├── orders/        ← Order lifecycle, invoice
│   ├── payments/      ← 3 gateways behind one ABC
│   ├── marketplace/   ← Vendor + Product + Settlement
│   ├── delivery/      ← Physical delivery + state machine
│   ├── notifications/ ← Per-user push (DB + WS + SMS)
│   ├── blog/          ← Editorial
│   ├── coins/         ← Coin reference data
│   ├── jewelry/       ← Jewelry taxonomy
│   ├── admin_panel/   ← Custom admin aggregations + Persian branding
│   └── api/v1_urls.py ← Composes every app's urls under /api/v1/
└── tests/                                 ← Cross-app integration + race tests
```

## 4. Request lifecycle

For `POST /api/v1/trade/buy/gold`:

```
1. Browser  ─────► Traefik
2. Traefik  ─────► Next.js (no auth concerns; just proxies /api/*)
3. Next.js  ─────► Django ASGI
4. Middleware (in order):
     • PrometheusBeforeMiddleware            — counter +1
     • apps.audit.middleware.RequestContext  — bind request_id / trace_id / IP
     • SecurityMiddleware (Django)
     • CorsMiddleware
     • SessionMiddleware
     • CommonMiddleware
     • CsrfViewMiddleware
     • AuthenticationMiddleware
     • apps.security.middleware.SecurityHeaders
     • apps.security.middleware.RateLimit    — Redis sliding-window
5. URL resolver → apps.orders.views.BuyGoldView
6. DRF: CookieJWTAuthentication, IsAuthenticated, IsKYCVerified
7. Serializer validates payload
8. apps.orders.services.submit_buy_gold():
     • re-fetch wallet (avoid stale cache)
     • if available_rial >= cost:
         order_sm.fire(order, "order.submitted")   ─► event 'orders.created'
         wallet_svc.lock_rial()                    ─► event 'wallet.rial.locked'
         order_sm.fire(order, "payment.verified")  ─► event 'orders.paid'
         complete_buy_order():
             unlock_rial → debit_rial → credit_asset
             order_sm.fire(order, "order.settle")  ─► event 'orders.completed'
             generate_invoice()                    ─► invoice PDF in MinIO
     • else: order stays in 'awaiting_payment' for the payment gateway
9. emit_event() writes:
     • to Redis Streams domain_events.domain   ─► Logstash → ES
     • to structlog stdout                     ─► Filebeat → ES
10. Response → DRF → Middleware (reverse) → Next.js → browser
```

## 5. Concurrency model

* **Database writes** are wrapped in `transaction.atomic()` and use
  `SELECT … FOR UPDATE` on the wallet row. Postgres row-level locking
  serialises mutations on the same wallet without blocking everyone.
* **Idempotency keys** (`audit.IdempotencyKey`) deduplicate webhook
  callbacks (a gateway may retry).
* **Celery tasks** propagate `request_id` through task headers so a
  whole chain is traceable in Kibana.
* **Channels group messages** are fanned out via `redis://… group_send`.

## 6. Data model overview

A simplified ERD (lines = FK, → singular, →* plural):

```
User ──→ RialWallet, GoldWallet
User ──→* Order ──* OrderItem ──→? Product ──→ Vendor ──→ User
User ──→* WalletTransaction ──→? Order
User ──→* KYCSubmission
User ──→? Vendor ──→* VendorSettlement
User ──→* Notification
User ──→* DeliveryRequest
User ──→* OTPCode
PriceTick (independent rows, indexed by source_key + captured_at)
PriceQuote ──→ User, PriceTick
PricingFormula (key/value, admin-editable)
PaymentAttempt ──→ Order
Order ──→? Vendor (only for kind='marketplace')
Blog: Post ──→ User (author), Category, →* Tag
AuditEntry, IdempotencyKey (independent)
```

`tenant_id` column lives on User, Order, Product, Vendor, RialWallet
(default `"default"`); white-label multi-tenancy is a config switch.

## 7. Frontend layout

```
frontend/
├── app/
│   ├── layout.tsx           ← RTL <html lang="fa">
│   ├── page.tsx             ← Home (Hero + 3 advantages)
│   ├── (auth)/login         ← OTP flow
│   ├── (account)/
│   │   ├── dashboard
│   │   ├── wallet/{rial,gold}
│   │   ├── trade/{buy,sell}
│   │   ├── transfer
│   │   ├── orders, orders/[id]
│   │   ├── delivery
│   │   ├── kyc
│   │   ├── notifications
│   │   └── profile
│   ├── (vendor)/vendor/{dashboard,apply,products,orders,settlements,profile}
│   ├── (admin)/admin/{,kyc,users,vendors,orders,payments,delivery,formulas,settlements,audit}
│   ├── marketplace, marketplace/[slug]
│   ├── vendors/[slug]
│   ├── blog, blog/[slug]
│   ├── prices                ← Live snapshot grid + chart
│   ├── about, contact, faq, terms, privacy
│   ├── robots.ts, sitemap.ts, manifest.ts, icon.svg
├── components/
│   ├── Header.tsx, Footer.tsx, PriceTicker.tsx, PriceChart.tsx
│   └── ui/ ← Button, Input, Card, Badge, Alert
├── hooks/  ← useLivePrice, useOrderCountdown
└── lib/    ← api.ts (typed client), format.ts (Persian numbers / mg / rial), cn.ts
```

* **App Router only** — no Pages Router.
* **HttpOnly cookies** for JWTs — the client never reads tokens.
* **SSR-by-default**; client components only when interactivity demands it.
* **No fake data** — every page calls `lib/api.ts` to hit the real backend.

## 8. External integrations

| Provider | Purpose | Where |
|----------|---------|-------|
| **TGJU.org** | Live prices (primary) | `apps/pricing/crawler.py::TgjuCrawler` |
| **brsapi.ir** | Live prices (fallback) | `apps/pricing/crawler.py::BrsApiFallback` |
| **Kavenegar** | OTP SMS + transactional SMS | `apps/accounts/services/otp.py`, `apps/notifications/services.py` |
| **Zarinpal v4** | Payment gateway | `apps/payments/gateways/zarinpal.py` |
| **IDPay v1.1** | Payment gateway | `apps/payments/gateways/idpay.py` |
| **PayPing v2** | Payment gateway | `apps/payments/gateways/payping.py` |
| **MinIO** (S3) | KYC files, invoice PDFs, blog covers | Django `STORAGES["default"]` |

## 9. Background work

Celery beat schedule (also seeded as DB rows by `seed_dev`):

| Task | Frequency | Code |
|------|-----------|------|
| `pricing.crawl_all` | 30 s | `apps/pricing/tasks.py` |
| `orders.expire_due` | 60 s | `apps/orders/tasks.py` |
| `wallet.consistency_tick` | 5 m | `apps/wallet/tasks.py` |
| `security.aml_tick` | 10 m | `apps/security/aml.py` |
| `audit.reconcile` | 1 h | `apps/audit/reconcile.py` |
| `marketplace.settle_vendors` | daily 01:00 | `apps/marketplace/settlements.py` |
| `wallet.daily_yield` | daily 00:05 | `apps/wallet/tasks.py` |

## 10. Failure modes

| Component | Failure | Effect | Mitigation |
|-----------|---------|--------|------------|
| Postgres | down | API 5xx, all writes fail | Backup restore (`scripts/backup.sh`); read-replica (planned) |
| Redis | down | rate-limit fails open, events go to logs only | Filebeat → Logstash → ES still works |
| MinIO | down | KYC + invoice generation fail | retry queue (planned) |
| TGJU | down | brsapi fallback | `pricing.source.failover` event; `pricing.tick.stale` if both fail |
| Gateway | down | `payments.attempt.failed` | User retries with another gateway |
| Elasticsearch | down | Logstash buffers; emit_event still runs | ES catches up when restored |
| Logstash | down | Redis Streams buffer up to `MAXLEN ~ 1_000_000` | Auto-recover; old events drop after limit |

## 11. Performance & SLOs

Defined in [`OBSERVABILITY.md §10`](OBSERVABILITY.md). Headline targets:

* Order-to-paid p95 ≤ 4 s
* Pricing crawler freshness ≥ 1 successful tick / 60 s / source
* API availability ≥ 99.9 % / 30 d
* Event-to-ES lag p95 ≤ 5 s
* **Zero ledger-invariant violations**

## 12. Where to start reading code

If you only have an hour, read these files in order:

1. `docs/OBSERVABILITY.md` — the contract
2. `backend/apps/audit/state_machine.py` — all legal state changes
3. `backend/apps/audit/catalogue.py` — the event taxonomy
4. `backend/apps/wallet/services.py` — money invariants enforced in code
5. `backend/apps/orders/services.py` — the trade lifecycle
6. `backend/tests/test_e2e_smoke.py` — the whole flow exercised end-to-end
