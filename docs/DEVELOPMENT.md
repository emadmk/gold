# KeyhanGold — Local Development

A complete guide to running KeyhanGold on your laptop in <5 minutes.

## Prerequisites

* Docker 24+ and `docker compose` v2
* `make` (GNU make)
* ~3 GiB of free disk space and 4 GiB of RAM

That's it — Python, Node, Postgres, Redis, Elasticsearch and everything
else run inside containers.

## Quick start

```bash
# 1. Clone
git clone <repo> keyhan-gold
cd keyhan-gold

# 2. Provide environment variables
cp .env.example .env
# (You can run with the defaults; if you want SMS to actually be sent
#  and live prices to update, fill in KAVENEGAR_API_KEY and the gateway
#  credentials.)

# 3. Start the full stack
make up                       # builds + brings up every service

# 4. Apply migrations & seed reference data
make migrate
make seed                     # super-admin password is printed once

# 5. Open
#    Frontend:        http://localhost:3000
#    Backend API:     http://localhost:8000/api/v1/
#    OpenAPI swagger: http://localhost:8000/api/v1/schema/swagger-ui/
#    Django admin:    http://localhost:8000/admin/
#    Kibana:          http://localhost:5601
#    MinIO console:   http://localhost:9001  (keyhan / keyhansecret)
#    Mailhog:         http://localhost:8025
```

## What `make up` brings up

| Service | Port | What |
|---------|------|------|
| `postgres` | 5432 | Domain database |
| `redis` | 6379 | Cache, broker, Channels layer, event bus |
| `minio` | 9000 / 9001 | S3-compatible object storage |
| `backend` | 8000 | Django ASGI (`runserver` in dev) |
| `celery_worker` | — | Background tasks |
| `celery_beat` | — | Scheduled tasks |
| `frontend` | 3000 | Next.js 16 dev server |
| `elasticsearch` | 9200 | Event index |
| `logstash` | 5044 | Redis Streams + Beats → ES |
| `kibana` | 5601 | Dashboards |
| `filebeat` | — | Container log shipper |
| `mailhog` | 1025 / 8025 | Outgoing-email sink |

## Daily workflow

```bash
# Start
make up

# Tail backend logs in another terminal
make logs

# Enter the backend shell (manage.py, pytest, ipython, …)
make backend
# then inside:
python manage.py createsuperuser  # if you want another admin
python manage.py shell_plus       # django-extensions
python manage.py emit_test_event --kind wallet.gold.buy

# Enter the frontend shell
make frontend
# then inside:
npm run typecheck
npm run lint

# Stop
make down
```

## Tests

```bash
make test                     # 115 backend tests
make observability-check      # event_coverage + catalogue + sm_coverage
make seam-check               # 20 roadmap seams intact
make all-checks               # everything CI runs
```

## Common tasks

**Reset the database.**
```bash
docker compose -f compose.dev.yml down -v
make up
make migrate seed
```

**Generate a new migration.**
```bash
make backend
python manage.py makemigrations <app_label>
```

**Crawl prices manually.**
```bash
make backend
python manage.py shell -c "from apps.pricing.tasks import crawl_all; print(crawl_all())"
```

**Promote yourself to vendor.**
```bash
make backend
python manage.py shell -c "
from apps.accounts.models import User
u = User.objects.get(phone='09123456789')
u.is_vendor = True; u.is_verified = True; u.save()
"
```

**Manually trigger an event (debug Kibana).**
```bash
make backend
python manage.py shell -c "
from apps.audit.emit import emit_event
emit_event('wallet.gold.buy', data={'asset':'gold','mg_amount':1000})
"
```

## Project layout (high-level)

See [ARCHITECTURE.md §3 + §7](ARCHITECTURE.md#3-backend-layout).

## Environment variables you'll commonly need

| Var | Purpose | Default |
|-----|---------|---------|
| `DJANGO_SECRET_KEY` | Django crypto | `dev-secret-change-me` |
| `DATABASE_URL` | Postgres DSN | inside compose |
| `REDIS_URL` | Redis DSN | inside compose |
| `KAVENEGAR_API_KEY` | SMS sender | empty (skips real send) |
| `ZARINPAL_MERCHANT_ID` / `…_SANDBOX` | Payment gateway | empty / true |
| `BOOTSTRAP_ADMIN_PHONE` | Seeded admin's phone | `09120000000` |

A complete annotated list is in [`.env.example`](../.env.example).

## Debugging tips

1. **HTTP 4xx returns a Persian `detail` field** — check the network tab.
2. **Look at Kibana** at `http://localhost:5601` → Discover → `keyhan-events-*` → paste your `request_id` (returned in `X-Request-Id` header) for the full chain.
3. **Postgres** — `make backend && python manage.py dbshell`.
4. **Redis** — `docker compose -f compose.dev.yml exec redis redis-cli`.
5. **Celery beat schedule** — see in Django admin → "Periodic Tasks".

## Pre-commit hygiene

```bash
# Run from the repo root
make lint                 # ruff + tsc + eslint
make test                 # backend tests
make observability-check  # event/SM coverage
make seam-check
```

CI runs the same gates — so if these pass, your PR is green.

## Adding a new feature

1. Read `docs/CONTRIBUTING.md` — short rules.
2. If it touches money or state: add the transition in
   `apps/audit/state_machine.py` first.
3. If it emits a new event kind: register it in
   `apps/audit/catalogue.py` first.
4. Then implement the service in `apps/<x>/services.py`.
5. Add a test in `backend/tests/`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `connection refused` to postgres | Container still starting | `make ps` then retry |
| Migration error after pulling | New migration needs apply | `make migrate` |
| Event coverage check fails | New SM transition emits an unregistered kind | Register kind in `apps/audit/catalogue.py` |
| Frontend can't reach `/api/*` | `BACKEND_URL` env wrong | `make down && make up` |
| `make seed` fails on prices | Network blocked from container | `make seed` then `make backend && python manage.py seed_dev --skip-prices` |
