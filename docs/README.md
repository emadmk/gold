# KeyhanGold — Documentation Index

The complete documentation for the KeyhanGold platform, organised by
audience and use case.

## 📚 Foundational documents (must-read)

| File | Audience | Purpose |
|------|----------|---------|
| [`SECURITY.md`](SECURITY.md) | All engineers | 10/10 security posture: OWASP ASVS L3 matrix, RBAC, crypto, ledger invariants, AML, CI gates |
| [`OBSERVABILITY.md`](OBSERVABILITY.md) | All engineers | Event taxonomy, state machine, Redis Streams → Logstash → Elasticsearch pipeline, ILM, SLOs |
| [`ROADMAP.md`](ROADMAP.md) | Product + Eng | 20 future capabilities and the v1 architectural seams that already support them |

## 🏗️ Architecture & system design

| File | Purpose |
|------|---------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | High-level system overview, services, data flow, dependencies |
| [`DOMAIN.md`](DOMAIN.md) | Business logic reference: units, formulas, state machines, invariants |
| [`API.md`](API.md) | REST + WebSocket endpoint reference |

## 🚀 Operations

| File | Purpose |
|------|---------|
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | Local development setup (Docker Compose) |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Production deployment with Traefik + Let's Encrypt |
| [`TESTING.md`](TESTING.md) | Testing strategy + CI gates |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to land a clean PR |

## 📦 Per-application docs

Each backend app has its own README:

| App | Role |
|-----|------|
| [`backend/apps/audit/`](../backend/apps/audit/README.md) | Observability core: state machine, event catalogue, emit, sinks |
| [`backend/apps/security/`](../backend/apps/security/README.md) | Middleware, rate limiter, crypto, feature flags, risk engine, upload validation |
| [`backend/apps/accounts/`](../backend/apps/accounts/README.md) | User, OTP, KYC, 2FA TOTP, JWT cookie auth |
| [`backend/apps/wallet/`](../backend/apps/wallet/README.md) | Rial + gold + silver wallets, transfer, daily yield, ledger invariants |
| [`backend/apps/pricing/`](../backend/apps/pricing/README.md) | TGJU crawler, price ticks, formulas, quotes, live WebSocket |
| [`backend/apps/orders/`](../backend/apps/orders/README.md) | Order lifecycle, payment timer, invoice PDF |
| [`backend/apps/payments/`](../backend/apps/payments/README.md) | Multi-gateway abstraction (Zarinpal / IDPay / PayPing), idempotent webhooks |
| [`backend/apps/marketplace/`](../backend/apps/marketplace/README.md) | Vendor + product CRUD, cart, checkout, daily vendor settlement |
| [`backend/apps/delivery/`](../backend/apps/delivery/README.md) | Physical-delivery requests + state machine |
| [`backend/apps/notifications/`](../backend/apps/notifications/README.md) | Persistent + WebSocket notifications, SMS dispatch |
| [`backend/apps/blog/`](../backend/apps/blog/README.md) | Editorial: categories, tags, posts, published-only API |
| [`backend/apps/coins/`](../backend/apps/coins/README.md) | Coin catalogue (Iran national mint specs) |
| [`backend/apps/jewelry/`](../backend/apps/jewelry/README.md) | Jewelry-category taxonomy |
| [`backend/apps/admin_panel/`](../backend/apps/admin_panel/README.md) | Admin-only aggregations + Persian branding of the Django admin |

## 🧭 ADRs (Architecture Decision Records)

Numbered, immutable design decisions. New ADRs go in
[`decisions/`](decisions/) with an incrementing prefix.

| # | Title |
|---|-------|
| 0001 | [Money in rial, weight in milligram — integers only](decisions/0001-money-and-weight-in-integers.md) |
| 0002 | [State machine is the only mutator](decisions/0002-state-machine-is-the-only-mutator.md) |
| 0003 | [Redis Streams as the event bus](decisions/0003-redis-streams-as-event-bus.md) |
| 0004 | [TGJU primary + brsapi fallback for prices](decisions/0004-tgju-primary-brsapi-fallback.md) |

## 🆘 Runbooks (on-call)

Short, scenario-based playbooks. Each one starts with "when to use".

| Scenario | Runbook |
|----------|---------|
| Emergency freeze of all money writes | [`runbooks/SYSTEM_HALT.md`](runbooks/SYSTEM_HALT.md) |
| Audit consistency violation (drift) | [`runbooks/ledger-drift.md`](runbooks/ledger-drift.md) |
| Price feed stale (TGJU + brsapi down) | [`runbooks/pricing-stale.md`](runbooks/pricing-stale.md) |

## 🗺️ Documentation map

```
KeyhanGold/
├── README.md              ← Project README (start here)
├── docs/
│   ├── README.md          ← THIS FILE
│   ├── ARCHITECTURE.md    ← System overview
│   ├── DOMAIN.md          ← Business logic reference
│   ├── API.md             ← Endpoint reference
│   ├── SECURITY.md        ← 10/10 posture
│   ├── OBSERVABILITY.md   ← Events, ES, state machines
│   ├── DEVELOPMENT.md     ← Local dev setup
│   ├── DEPLOYMENT.md      ← Production deploy
│   ├── TESTING.md         ← Test strategy
│   ├── ROADMAP.md         ← 20 future features
│   ├── CONTRIBUTING.md    ← PR workflow
│   ├── decisions/         ← ADRs
│   └── runbooks/          ← On-call playbooks
├── backend/apps/<app>/README.md   ← per-app docs
└── frontend/README.md     ← Next.js frontend
```

## 🇮🇷 یادداشت زبان

* مستندات همگی به انگلیسی نوشته شده‌اند تا تیم بین‌المللی هم بتواند مشارکت کند.
* پیام‌های نمایش به کاربر در محصول، فارسی است (با `_("…")` / `t()`).
* لاگ‌های ساختاری انگلیسی هستند تا در Kibana بدون مشکل قابل جست‌وجو باشند.
