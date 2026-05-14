# ADR-0004 — TGJU as the primary price feed, brsapi.ir as fallback

* **Status:** Accepted (2026-05-14)

## Context

The platform needs a reliable price feed for ~14 instruments. TGJU is the
de-facto reference in the Iranian market but is occasionally rate-limited
or returns stale numbers under load.

## Decision

* The crawler attempts TGJU first (HTML scrape with three fallback
  selectors). On any failure (timeout, parse error, HTTP error) we emit
  `pricing.source.failover` and try brsapi.ir's free webservice.
* Each successful fetch writes a `PriceTick` row stamped with `source`
  so analytics can attribute discrepancies.
* If both sources fail consecutively we emit `pricing.tick.stale` and
  surface a `Stale` badge in the UI; trade endpoints reject quotes more
  than 90s old (configurable).

## Consequences

* Two competing implementations exist (`TgjuCrawler`, `BrsApiFallback`).
* When TGJU changes its DOM, the fallback keeps us live until we patch.
* Bug reports must include the `source` field from `PriceTick`.
