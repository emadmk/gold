# `apps.pricing` — Crawler, ticks, formulas, quotes, WebSocket

## Models

| Model | Purpose |
|-------|---------|
| `PriceTick` | Immutable history. One row per `(source_key, captured_at)`. Indexed for "most recent". |
| `PricingFormula` | Admin-editable coefficient registry. Defaults from `settings.DOMAIN_DEFAULTS`. |
| `PriceQuote` | Frozen price (per mg, rial) we showed a user. Valid for **30 seconds**; consumed when an order is placed. |

## Crawler

`apps/pricing/crawler.py`:
* `TgjuCrawler.fetch(source_key)` — primary, with 3 fallback selectors.
* `BrsApiFallback.fetch(source_key)` — secondary.
* `fetch_with_fallback(source_key)` — combines both; emits
  `pricing.source.failover` when it falls through.

Sources (`SOURCE_KEYS`): `gold_18k_750`, `gold_18k_740`, `gold_24k`,
`mesghal`, `gold_melted_cash`, `coin_emami`, `coin_bahar`, `coin_half`,
`coin_quarter`, `coin_gerami`, `silver_999`, `silver_925`, `ons_gold`,
`usd_free`.

## Formulas (strategy registry)

`apps/pricing/formulas.py` registers strategies with `@register(name)`.
Defaults: `gold_buy`, `gold_sell`, `silver_buy`, `silver_sell`. Each
strategy reads coefficients via `coefficient(key)` which prefers the
DB row to the settings default — so the admin panel can re-tune live.

See [`DOMAIN.md §3`](../../../docs/DOMAIN.md#3-pricing-formulas).

## Background tasks

* `pricing.crawl_all` — every 30 s: fetches every source, writes a
  tick, caches in Redis (`price:<key>`, TTL 120 s), publishes to
  Redis pub/sub channel `prices:live`.
* `pricing.tick.stale` is emitted when a source misses two
  consecutive cycles.

## WebSocket

`apps/pricing/consumers.py::PriceConsumer` joins group `prices_live`
on connect, sends the cached snapshot, then forwards every
`price_update` message. URL: `ws://…/ws/prices/`.

## Endpoints

```
GET  /api/v1/prices                ← public snapshot
POST /api/v1/prices/quote          ← request a 30 s quote
WS   /ws/prices/                    ← live updates
```

## Events emitted

`pricing.tick.captured / stale`, `pricing.quote.issued`,
`pricing.formula.updated`, `pricing.source.failover`.

## Tests

`tests/test_pricing_formulas.py` — buy > base > sell sanity, spread
flow-through.
