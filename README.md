# KeyhanGold — Online Gold & Silver Trading Platform

> A production-ready, end-to-end platform for buying & selling gold and silver
> (mili-gold model + multi-vendor marketplace) — built for the Iranian market.

This repository is a **monorepo** with the following layout:

```
keyhan-gold/
├── backend/         # Django 5.2 LTS + DRF + Channels + Celery
├── frontend/        # Next.js 16 (App Router) + React 19 + Tailwind v4 + shadcn/ui
├── docker/          # Dockerfiles, Traefik & ELK config
├── docs/            # Architecture decisions, observability, security, roadmap
├── compose.yml      # Production stack (Traefik + ELK + Prometheus + Grafana)
├── compose.dev.yml  # Local development stack
└── README.md
```

## Quick start (development)

```bash
# 1) Clone & enter
git clone <repo> keyhan-gold && cd keyhan-gold

# 2) Copy env files (and edit them!)
cp .env.example .env

# 3) Bring the dev stack up
docker compose -f compose.dev.yml up --build

# 4) Apply migrations & seed
docker compose -f compose.dev.yml exec backend python manage.py migrate
docker compose -f compose.dev.yml exec backend python manage.py seed_dev

# 5) Open
#    Frontend:        http://localhost:3000
#    Backend API:     http://localhost:8000/api/v1/
#    OpenAPI schema:  http://localhost:8000/api/v1/schema/swagger-ui/
#    Kibana:          http://localhost:5601
#    Grafana:         http://localhost:3001
#    MinIO console:   http://localhost:9001
#    Mailhog:         http://localhost:8025
```

## Foundational documents

Three documents define the **non-negotiable** properties of this codebase.
Every contribution must respect them.

| File | What it guarantees |
|------|--------------------|
| [`docs/SECURITY.md`](docs/SECURITY.md) | A reproducible **10/10** security posture: threat model, control matrix, OWASP ASVS L3 coverage, key management, AML rules, deployment hardening. |
| [`docs/OBSERVABILITY.md`](docs/OBSERVABILITY.md) | Every domain event is **traceable in Elasticsearch**. Defines the event taxonomy, state-machine instrumentation, structured logs, and the audit pipeline (structlog → Filebeat → Logstash → ES). |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | 20 future capabilities and the architectural seams already in place so they can be delivered **without rewrites**. |

## Tech stack

- **Backend:** Python 3.13 · Django 5.2 LTS · DRF · Celery 5.4 · Channels 4 · PostgreSQL 16 · Redis 7
- **Frontend:** Next.js 16 (App Router) · React 19 · TypeScript strict · Tailwind v4 · shadcn/ui · Zustand · react-hook-form · zod
- **Observability:** Elasticsearch 8 · Logstash · Kibana · Filebeat · Sentry · Prometheus · Grafana · OpenTelemetry
- **Storage:** MinIO (S3 compatible) for KYC / invoice attachments
- **Edge:** Traefik 3 with automatic Let's Encrypt SSL
- **Tests:** pytest + factory-boy + Vitest + Playwright

## Development discipline

1. Follow [Conventional Commits](https://www.conventionalcommits.org/).
2. All money is **rial (int64)**, all weight is **milligram (int64)** — no floats.
3. Every state transition flows through the central state machine (`apps/audit/state_machine.py`).
4. Every domain event is emitted via `emit_event(...)` and ends up in ES.
5. `mypy --strict` and `ruff check` must pass; `tsc --noEmit` must pass.
6. New endpoints must appear in the OpenAPI schema (drf-spectacular) and have a Persian error-message contract.

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for the full guide.
