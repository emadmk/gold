# ADR-0003 — Redis Streams as the event bus

* **Status:** Accepted (2026-05-14)
* **Related:** `docs/OBSERVABILITY.md §1`

## Context

We need a durable, low-latency transport between `emit_event` and Logstash
that survives a Logstash restart without dropping events but doesn't
require a Kafka cluster.

## Decision

* Use Redis Streams (`XADD … MAXLEN ~ 1_000_000`) keyed by event category:
  `domain_events.domain`, `…security`, `…aml`, `…system`, `…ux`.
* Logstash consumes via `XREADGROUP` (consumer group "logstash") so the
  read offset survives restarts.
* If Redis itself is down, `emit_event` falls back to structlog → Filebeat
  → Logstash (degraded but not silent).

## Alternatives considered

* **Kafka** — overkill for the present volume.
* **RabbitMQ** — extra operational surface; we already need Redis.
* **Postgres LISTEN/NOTIFY** — no durability when there's no listener.

## Consequences

* Single failure domain (Redis) — but we use Redis for the cache & broker
  anyway, so it's not a new dependency.
* Bounded memory by `MAXLEN ~`; old events drop after the configured limit.
* Migration path: a new transport can register a second Logstash input
  and run side-by-side with Redis.
