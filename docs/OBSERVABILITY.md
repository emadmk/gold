# KeyhanGold — Observability & Event Tracing

> **Rule zero.** Every meaningful action in the system produces a
> structured event, every state transition is mediated by the state
> machine, and **every event ends up in Elasticsearch within ≤ 5 seconds**
> with the same `correlation_id` that crossed the HTTP/WS boundary.
>
> If a code path mutates state without going through `state_machine.transition(...)`
> and emitting `emit_event(...)`, it is a bug — and CI breaks the build.

This document defines:

1. The event taxonomy and schema (so analysts can write Kibana queries
   today and tomorrow).
2. The state-machine model (so audits are deterministic).
3. The transport pipeline (structlog → Filebeat → Logstash → ES).
4. The dashboards and SLOs.

---

## 1. The pipeline at a glance

```
┌─────────────────────┐    JSON     ┌──────────┐
│ Django / Channels / │  to stdout  │          │
│ Celery / Daphne     │ ──────────► │ Filebeat │
└─────────────────────┘             │ (sidecar)│
        │                           └────┬─────┘
        │ structlog                      │
        │ +OpenTelemetry trace_id        │
        ▼                                ▼
┌─────────────────────┐             ┌──────────┐         ┌────────────┐
│  Redis Streams      │ ──────────► │ Logstash │ ──────► │ Elastic-   │
│  domain_events.*    │   ingest    │ pipelines│ index   │ search 8.x │
└─────────────────────┘             └────┬─────┘         └─────┬──────┘
        ▲                                │                     │
        │                                │                     ▼
        │ emit_event()                   │              ┌────────────┐
        │                                │              │  Kibana    │
┌─────────────────────┐                  │              │ dashboards │
│ state_machine       │ ─────────────────┘              └────────────┘
│ .transition(...)    │
└─────────────────────┘
```

Two transports, **on purpose**:

- **Filebeat** ships the *process log* (errors, request access logs,
  Celery worker chatter). Used for debugging.
- **Redis Streams → Logstash** ships *domain events* — typed, schema'd,
  business-meaningful. Used for audit and analytics.

A domain event therefore lands in ES twice: once as a log line
(`keyhan-logs-*`) and once as a typed document (`keyhan-events-*`).
The `correlation_id` ties them together.

---

## 2. Event taxonomy

Every event is a JSON document with this **mandatory** envelope. The schema
is enforced by `apps/audit/schema.py` (pydantic v2); the Logstash pipeline
re-validates and routes invalid events to `keyhan-events-dlq-*`.

```jsonc
{
  "@timestamp":     "2026-05-14T17:30:00.123Z",
  "event": {
    "id":           "01HX5T8V7Q5MZF1J0K6Q9A4P3B",   // ULID
    "kind":         "wallet.gold.buy",              // see catalogue below
    "version":      1,
    "category":     "domain",                       // domain | security | system | aml | ux
    "severity":     "info",                         // debug | info | warning | error | critical
    "outcome":      "success"                       // success | failure | denied
  },
  "actor": {
    "type":         "user",                          // user | admin | system | vendor | gateway
    "id":           "9c3a…uuid",
    "ip":           "5.232.10.4",
    "user_agent":   "Mozilla/5.0…",
    "session_id":   "…",
    "roles":        ["user"],
    "kyc_level":    2
  },
  "target": {
    "type":         "order",
    "id":           "KG-202605-000001",
    "owner_id":     "9c3a…uuid"
  },
  "correlation": {
    "trace_id":     "1234abcd…",                     // OpenTelemetry W3C
    "span_id":      "ab12cd34",
    "request_id":   "01HX5T8VAA…",
    "causation_id": "01HX5T8VAB…",                  // event that caused this one
    "session_id":   "…"
  },
  "state": {
    "machine":      "order",
    "from":         "awaiting_payment",
    "to":           "paid",
    "trigger":      "payment.verified"
  },
  "data": {
    "asset":        "gold",
    "mg_amount":    1000,
    "rial_amount":  17241600,
    "price_per_mg": 17241,
    "fee_rial":     0
  },
  "tags":           ["money", "gold", "buy"],
  "service": {
    "name":         "keyhan-backend",
    "version":      "0.1.0",
    "env":          "prod",
    "host":         "backend-7c8f"
  }
}
```

### 2.1 Top-level categories

| `event.category` | Index alias | Retention |
|------------------|-------------|-----------|
| `domain`         | `keyhan-events-domain-*`   | 5 years   |
| `security`       | `keyhan-events-security-*` | 5 years   |
| `aml`            | `keyhan-events-aml-*`      | 10 years  |
| `system`         | `keyhan-events-system-*`   | 30 days   |
| `ux`             | `keyhan-events-ux-*`       | 90 days   |

### 2.2 Event catalogue

> Every kind below is registered in `apps/audit/catalogue.py`. New events
> must be added there or the `make event-coverage` check fails.

**Accounts & KYC**

| `event.kind`                  | When                                    |
|-------------------------------|-----------------------------------------|
| `accounts.otp.requested`      | OTP send queued                         |
| `accounts.otp.delivered`      | Provider ack                            |
| `accounts.otp.verified`       | Code matched                            |
| `accounts.otp.rejected`       | Code wrong / expired                    |
| `accounts.user.registered`    | First successful OTP                    |
| `accounts.session.opened`     | JWT pair issued                         |
| `accounts.session.refreshed`  | Refresh-token rotation                  |
| `accounts.session.revoked`    | Logout / blacklist                      |
| `kyc.submitted`               | User submits docs                       |
| `kyc.approved` / `kyc.rejected` | Reviewer decision                    |
| `kyc.flag.aml`                | AML hit during review                   |

**Pricing**

| `event.kind`                | When                                    |
|----------------------------|-----------------------------------------|
| `pricing.tick.captured`     | New `PriceTick` row written             |
| `pricing.tick.stale`        | Crawler missed two consecutive cycles   |
| `pricing.quote.issued`      | User saw a price                        |
| `pricing.formula.updated`   | Admin changed a coefficient             |
| `pricing.source.failover`   | TGJU fallback to brsapi triggered       |

**Wallet**

| `event.kind`            | When                                        |
|-------------------------|---------------------------------------------|
| `wallet.rial.deposit`   | Gateway-confirmed deposit                   |
| `wallet.rial.withdraw`  | Withdraw request created                    |
| `wallet.rial.locked` / `…unlocked` | Funds frozen for an order        |
| `wallet.gold.buy` / `wallet.gold.sell` | Trade settled               |
| `wallet.silver.buy` / `wallet.silver.sell` | …                       |
| `wallet.transfer.out` / `wallet.transfer.in` | Internal P2P transfer |
| `wallet.yield.payout`   | Nightly yield credit                        |
| `wallet.adjustment`     | Admin correction                            |

**Orders**

| `event.kind`            | When                                        |
|-------------------------|---------------------------------------------|
| `orders.created`        | Order persisted in `awaiting_payment`       |
| `orders.expired`        | 30-min timer fired                          |
| `orders.cancelled`      | User cancelled                              |
| `orders.paid`           | Gateway verified or wallet debited          |
| `orders.completed`      | Asset credited / item shipped               |
| `orders.failed`         | Terminal failure (refund)                   |
| `orders.refunded`       | Refund pushed                               |
| `orders.timer.tick`     | Every 60 s for orders still awaiting payment|

**Payments**

| `event.kind`                | When                                    |
|----------------------------|-----------------------------------------|
| `payments.attempt.created`  | Gateway request started                 |
| `payments.attempt.redirected`| User sent to gateway URL               |
| `payments.attempt.callback` | Gateway hit our callback                |
| `payments.attempt.verified` | Gateway verify succeeded                |
| `payments.attempt.failed`   | Verify failed / gateway error           |
| `payments.webhook.duplicate`| Idempotency replay caught               |

**Delivery & Marketplace**

| `event.kind`                | When                                    |
|----------------------------|-----------------------------------------|
| `delivery.requested`        | User asked for physical delivery        |
| `delivery.state.*`          | One per state transition (see SM)       |
| `marketplace.vendor.applied`| Vendor signup                           |
| `marketplace.vendor.approved`/`…suspended` | Admin action          |
| `marketplace.product.published`/`…delisted`| Vendor / admin action |
| `marketplace.settlement.run`| Daily payout to vendors                 |

**Security & system**

| `event.kind`                       | When                                |
|------------------------------------|-------------------------------------|
| `security.login.brute_force`       | 5 failed OTPs                       |
| `security.ratelimit.breach`        | Limit exceeded                      |
| `security.csrf.failure`            | CSRF check failed                   |
| `security.permission.denied`       | RBAC denied access                  |
| `security.token.blacklisted`       | JWT revoked                         |
| `audit.consistency.violation`      | Invariant failure (see SECURITY §8) |
| `system.feature_flag.toggled`      | Flag changed                        |
| `system.celery.task.failed`        | Task hit max retries                |

**AML**

| `event.kind`               | When                                     |
|---------------------------|------------------------------------------|
| `aml.threshold.high`      | Velocity / amount rule fired             |
| `aml.case.opened` / `…closed` | Admin opened / closed case           |
| `aml.sanctions.hit`       | Sanctions match at KYC time              |

---

## 3. The state machine

The state machine is the single point of truth for **transitions** in the
domain. Every transition emits at least one event. The CI gate
`make event-coverage` parses the SM and verifies coverage.

### 3.1 Implementation contract

```python
# apps/audit/state_machine.py
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Transition:
    machine:   str            # "order", "kyc", "delivery", …
    from_:     str
    to:        str
    trigger:   str            # event-like name, e.g. "payment.verified"
    guard:     Callable | None = None
    on_enter:  Callable | None = None
    side_effects: tuple[str, ...] = ()   # event kinds emitted by the transition
```

Every transition declares the event kinds it emits. That declaration is
what `make event-coverage` reads — so removing the `emit_event(...)` call
without updating `side_effects` is forbidden.

### 3.2 `order` state machine

```
                  ┌────────────────┐
                  │     draft      │
                  └───────┬────────┘
                          │ submit
                          ▼
                  ┌────────────────┐
                  │ awaiting_payment│◄────────────────────┐
                  └───────┬────────┘                      │
       ┌──────────┬───────┴─────┬───────────┐             │
       │ expire   │ pay         │ cancel    │ retry_pay   │
       ▼          ▼             ▼           │             │
   ┌────────┐ ┌───────┐    ┌──────────┐     │             │
   │expired │ │ paid  │    │cancelled │─────┘             │
   └────────┘ └───┬───┘    └──────────┘                   │
                  │ process                               │
                  ▼                                       │
              ┌───────────┐                               │
              │processing │ ───── fail ──► failed ─► refunded
              └────┬──────┘
                   │ settle
                   ▼
              ┌───────────┐
              │ completed │
              └───────────┘
```

Triggers and side-effects:

| from → to                       | trigger                  | emits                                            |
|---------------------------------|--------------------------|--------------------------------------------------|
| draft → awaiting_payment        | `order.submitted`        | `orders.created`, `wallet.rial.locked`           |
| awaiting_payment → paid         | `payment.verified`       | `orders.paid`, `payments.attempt.verified`       |
| awaiting_payment → expired      | `order.timeout`          | `orders.expired`, `wallet.rial.unlocked`         |
| awaiting_payment → cancelled    | `order.cancel`           | `orders.cancelled`, `wallet.rial.unlocked`       |
| paid → processing               | `order.process`          | `wallet.gold.buy` (or sibling)                   |
| processing → completed          | `order.settle`           | `orders.completed`                               |
| processing → failed             | `order.fail`             | `orders.failed`                                  |
| failed → refunded               | `order.refund`           | `orders.refunded`, `wallet.rial.deposit`         |

### 3.3 `kyc` state machine

```
empty → submitted → under_review ─┬─► approved
                                   ├─► requires_more → submitted
                                   └─► rejected
```

### 3.4 `delivery` state machine

```
pending → approved → minting → shipped → delivered
                          └─► cancelled (any time before shipped)
```

### 3.5 `vendor` state machine

```
applied → approved ─┬─► suspended ─► approved
                    └─► retired
applied → rejected
```

### 3.6 `payment_attempt` state machine

```
pending → redirected ─┬─► succeeded
                       ├─► failed
                       ├─► cancelled
                       └─► expired
```

A guard ensures that we move to `succeeded` **only** after the gateway
verify call returns `ok` AND `amount` matches. A duplicate webhook
hits the `audit_idempotency_keys` table and emits
`payments.webhook.duplicate`.

---

## 4. Correlation IDs

| Layer        | How it's propagated |
|--------------|---------------------|
| Browser → API | Generates `X-Request-Id` if missing, returns the same value in response |
| Next.js SSR  | Adds it to its outgoing fetch headers |
| Django middleware | `apps/audit/middleware.RequestContextMiddleware` reads or generates `X-Request-Id`, stores it in `contextvars` |
| structlog    | Binds `request_id`, `trace_id`, `user_id`, `session_id` automatically |
| Channels     | The middleware works for WS too — `scope["request_id"]` is set on connect |
| Celery       | `apps/audit/celery.py` propagates `request_id` through task kwargs (`headers={"request_id": …}`) |
| Outgoing HTTP | `httpx` client wrapper attaches `X-Request-Id` so gateway/crawler responses can be cross-referenced |
| Webhooks in  | The gateway provides an `Idempotency-Key`; we record it and start a *new* chain with `causation_id` pointing to the original order |

Result: in Kibana you can paste any `request_id` or `trace_id` and see
the **whole** life of a request — HTTP, Celery, WS push, AML, ledger
entries — across all categories.

---

## 5. The `emit_event` API

```python
# apps/audit/emit.py
def emit_event(
    kind: str,
    *,
    actor: Actor | None = None,
    target: Target | None = None,
    state: StateTransition | None = None,
    data: dict | None = None,
    tags: list[str] | None = None,
    severity: Literal["debug","info","warning","error","critical"] = "info",
    outcome: Literal["success","failure","denied"] = "success",
) -> str: ...
```

What it does, in order:

1. Validates `kind` against `catalogue.py`.
2. Fills the envelope from `contextvars` (correlation, service, host).
3. Validates the full document against the pydantic envelope.
4. Writes synchronously to `Redis Streams` key `domain_events.{category}`
   (XADD, MAXLEN ~ 1_000_000).
5. Writes a log line via structlog (so Filebeat picks it up too).
6. Returns the event's ULID, so callers may store it (e.g. in
   `WalletTransaction.event_id`) for forward references.

Redis Streams gives us:

- **Durability** with bounded memory (`MAXLEN ~`).
- **At-least-once** delivery to Logstash (the input plugin uses
  `XREADGROUP`).
- **Backpressure isolation** — if ES is down, Logstash lags but the
  request path is unaffected.

---

## 6. Logstash pipeline (`docker/logstash/pipeline/keyhan.conf`)

```text
input {
  redis {
    host => "redis"
    key  => "domain_events.domain"
    data_type => "stream"
    consumer_group => "logstash"
    consumer => "${HOSTNAME}"
  }
  redis { … other categories … }

  beats { port => 5044 }      # Filebeat ships process logs here
}

filter {
  if [event][kind] {
    json { source => "message" target => "doc" remove_field => "message" }
    ruby { code => "event.set('@metadata][index]', 'keyhan-events-' +
                    event.get('[event][category]') + '-' +
                    event.get('@timestamp').time.strftime('%Y.%m.%d'))" }
  } else {
    mutate { add_field => { "[@metadata][index]" => "keyhan-logs-%{+YYYY.MM.dd}" } }
  }
  # PII redaction defence-in-depth — server-side strip
  mutate { remove_field => ["[actor][national_id]", "[actor][iban]"] }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    user  => "${ES_USER}"
    password => "${ES_PASS}"
    index => "%{[@metadata][index]}"
    ilm_enabled => true
    ilm_rollover_alias => "%{[@metadata][index]}"
  }
  if "_jsonparsefailure" in [tags] {
    elasticsearch { index => "keyhan-events-dlq-%{+YYYY.MM.dd}" hosts => ["http://elasticsearch:9200"] }
  }
}
```

---

## 7. Index lifecycle (ILM)

| Alias                    | Hot   | Warm  | Cold  | Delete  |
|--------------------------|-------|-------|-------|---------|
| `keyhan-events-domain`   | 7 d   | 30 d  | 1 y   | 5 y     |
| `keyhan-events-security` | 7 d   | 30 d  | 1 y   | 5 y     |
| `keyhan-events-aml`      | 14 d  | 90 d  | 2 y   | 10 y    |
| `keyhan-events-system`   | 3 d   | 7 d   | —     | 30 d    |
| `keyhan-events-ux`       | 3 d   | 14 d  | —     | 90 d    |
| `keyhan-logs`            | 3 d   | 14 d  | —     | 90 d    |

ILM policies live in `docker/elasticsearch/ilm/*.json` and are applied on
container start by `docker/elasticsearch/bootstrap.sh`.

---

## 8. Kibana saved objects (shipped on bootstrap)

- **Dashboard: Money Pulse** — orders/min, success/failure ratio, total
  rial volume, mg volume by asset, P95 order-to-paid latency.
- **Dashboard: Security** — login failures, rate-limit breaches, RBAC
  denials, top offending IPs, distinct devices per user.
- **Dashboard: AML** — open cases, threshold hits, sanctions, velocity
  outliers.
- **Dashboard: SLOs** — see §10 below.
- **Discover saved search: "Trace by request_id"** — single field input.

Saved objects are JSON in `docker/kibana/saved_objects/` and imported
automatically by `docker/kibana/import.sh`.

---

## 9. Logs vs events vs metrics

| Concept        | Where                | Example                                |
|----------------|----------------------|----------------------------------------|
| **Log line**   | `keyhan-logs-*`      | `Pricing crawler: connection reset`    |
| **Domain event** | `keyhan-events-*`  | `wallet.gold.buy` with mg & rial       |
| **Metric**     | Prometheus / Grafana | `keyhan_orders_paid_total{kind="buy_gold"}` |
| **Trace**      | OpenTelemetry → Tempo (optional) | Whole span tree for a request |

Don't confuse them. **Metrics are derived from events** (Logstash
emits Prometheus counters via the `prometheus_exporter` filter) so the
two views never diverge.

---

## 10. SLOs

| SLI                                 | Target                | Burn-rate alert |
|-------------------------------------|-----------------------|-----------------|
| Order-to-paid p95 latency           | ≤ 4 s                 | 2 % over 1 h    |
| Pricing crawler freshness           | ≥ 1 successful tick / 60 s for each source | missing > 5 min |
| Event-to-ES lag (XADD → indexed)    | p95 ≤ 5 s             | > 30 s for 5 min |
| Payment webhook success ratio       | ≥ 99.9 % / day        | drop below 99.5 % |
| API availability                    | ≥ 99.9 % / 30 d       | error budget burn |
| Ledger invariants (§ SECURITY 8)    | 0 violations          | 1 violation = page |

---

## 11. Developer affordances

- `python manage.py emit_test_event --kind wallet.gold.buy` — for
  experimenting in dev.
- `python manage.py trace <request_id>` — prints the full event chain.
- `python manage.py state_machine_graph order > order.dot` — generates a
  Graphviz diagram from the SM declaration.
- VS Code launch config for `apps/audit/replay.py` — re-emit a stored
  event in dev for testing dashboards.

---

## 12. PII / redaction

The structlog processor `apps/audit/log.py::RedactionProcessor` strips
or hashes the following before write:

| Field                    | Treatment        |
|--------------------------|------------------|
| `actor.password`         | DROP             |
| `actor.national_id`      | SHA-256 truncated (`nid_sha256`) |
| `actor.iban`             | SHA-256 truncated |
| `actor.email`            | mask local part  |
| `actor.phone`            | mask middle (e.g. `0912***6789`) |
| any field named `*token*`| DROP             |
| any field matching `\b\d{16}\b` (PAN) | mask |

Logstash repeats the same redaction (defence in depth — see §6).

---

## 13. Failure modes

| What fails                  | What happens                                                    |
|----------------------------|------------------------------------------------------------------|
| Redis down                  | `emit_event` writes only to structlog; Filebeat still ships → `keyhan-logs-*`. App degraded but operational. Alert. |
| Logstash down               | Redis Streams buffer up to `MAXLEN ~ 1_000_000`; older events drop. ES catches up when LS returns. |
| ES down                     | Logstash buffers on disk (`dead_letter_queue`); reads to ES retry. |
| Filebeat down               | Process logs missing from ES; pod restart. |
| `emit_event` raises         | NEVER raises into business code — it logs at ERROR and increments `keyhan_audit_emit_failed_total`. The state-machine transition still committed; eventual-consistency reconciliation job (`apps/audit/reconcile.py`, runs hourly) backfills events from DB rows. |

---

## 14. CI gates

| Check                       | Script                                |
|----------------------------|---------------------------------------|
| Every SM transition emits   | `python -m apps.audit.checks event_coverage` |
| Every public mutation calls SM | `python -m apps.audit.checks sm_coverage`  |
| Catalogue is sorted & unique | `python -m apps.audit.checks catalogue`     |
| pydantic schema accepts all sample envelopes | `pytest tests/audit/test_envelope.py` |
| Kibana saved-objects parse | `node docker/kibana/lint.js`           |

Run them all locally with `make observability-check`.
