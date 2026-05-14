# KeyhanGold — Production Deployment

This guide takes you from a fresh Linux host to a live, TLS-terminated
KeyhanGold deployment with Traefik, ELK, Prometheus and Grafana.

## 1. Prerequisites

* A Linux host (Ubuntu 22.04+ recommended)
* Docker 24+ and `docker compose` v2
* A domain (e.g. `keyhan.gold`) with DNS pointing all of these A-records
  at the host:
  * `keyhan.gold` (and `www.keyhan.gold`)
  * `api.keyhan.gold`
  * `kibana.keyhan.gold`
  * `grafana.keyhan.gold`
  * `minio.keyhan.gold`
* Ports 80 and 443 open to the internet
* ≥ 4 vCPU, ≥ 8 GiB RAM, ≥ 60 GiB disk

## 2. Provision secrets

```bash
# Create the env file from the template
cp .env.example .env
# Edit it — at minimum set:
#   DOMAIN, DJANGO_SECRET_KEY, DB_PASS, REDIS_PASS,
#   MINIO_ACCESS_KEY / MINIO_SECRET_KEY,
#   ELASTICSEARCH_PASSWORD, KIBANA_SYSTEM_PASSWORD,
#   GRAFANA_ADMIN_PASSWORD,
#   KAVENEGAR_API_KEY, ZARINPAL_MERCHANT_ID, IDPAY_API_KEY, PAYPING_API_KEY,
#   JWT_PRIVATE_KEY / JWT_PUBLIC_KEY  (see § 3)
```

### 2.1 Generate `DJANGO_SECRET_KEY`

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 2.2 Generate Ed25519 JWT keys

```bash
openssl genpkey -algorithm ed25519 -out jwt.pem
openssl pkey -in jwt.pem -pubout -out jwt.pub
echo "JWT_PRIVATE_KEY=$(cat jwt.pem | base64 -w0)"
echo "JWT_PUBLIC_KEY=$(cat jwt.pub  | base64 -w0)"
# Paste the base64-encoded values into .env, then `base64 -d` at app start.
# (Or store the multi-line PEM directly, escaped — django-environ handles
#  both.)
```

> Never commit `.env` or `jwt.pem`. They are in `.gitignore`.

## 3. Deploy

```bash
# Pull the repo
git clone <repo> /opt/keyhan && cd /opt/keyhan

# Build + bring up
docker compose -f compose.yml up -d --build

# Wait for Postgres to be ready
docker compose -f compose.yml exec backend python manage.py migrate
docker compose -f compose.yml exec backend python manage.py seed_dev
# ↑ prints the super-admin password ONCE — save it.

# Apply ILM policies + index templates to Elasticsearch
make es-bootstrap

# Import Kibana dashboards
make kibana-import
```

After a few minutes:

* `https://keyhan.gold` — public site
* `https://api.keyhan.gold/api/v1/schema/swagger-ui/` — API explorer
* `https://api.keyhan.gold/admin/` — Django admin
* `https://kibana.keyhan.gold` — Kibana
* `https://grafana.keyhan.gold` — Grafana
* `https://minio.keyhan.gold` — MinIO console

Traefik serves Let's Encrypt certs automatically; the first request
may take ~30 s while ACME provisions.

## 4. Verify

```bash
# Quick smoke
curl -fsS https://keyhan.gold | head -2
curl -fsS https://api.keyhan.gold/health
docker compose -f compose.yml ps

# Observability gates (must all be OK)
make observability-check
make seam-check
```

## 5. Day-2 operations

### 5.1 Backups

`scripts/backup.sh` runs `pg_dump` + a MinIO mirror, age-encrypts the
result with your recipient key, and uploads to a remote bucket.

Recommended cron (on the host):
```cron
0 2 * * *   cd /opt/keyhan && ./scripts/backup.sh
```

### 5.2 Updates

```bash
git pull
docker compose -f compose.yml up -d --build
docker compose -f compose.yml exec backend python manage.py migrate
```

Zero-downtime: Traefik keeps serving the old container until the new
one passes its health check.

### 5.3 Scaling

* **Backend**: increase `--workers` on gunicorn (currently `-w 4`) or
  run multiple `backend` replicas behind the Traefik service — they're
  stateless.
* **Celery**: spin up another `celery_worker` container; broker queues
  fan out.
* **Postgres**: move to managed Postgres or set up logical replication.
* **Elasticsearch**: increase `ES_JAVA_OPTS -Xms/Xmx` then add a node
  and switch to a 3-node cluster.

### 5.4 On-call

The runbooks in [`runbooks/`](runbooks/) cover the headline scenarios:

* SYSTEM_HALT (emergency freeze of money writes)
* Ledger drift (`audit.consistency.violation`)
* Pricing feed stale

## 6. Security checklist before going live

- [ ] All passwords in `.env` are >= 24 chars and unique.
- [ ] `DJANGO_SECRET_KEY` rotated; old value purged.
- [ ] `JWT_PRIVATE_KEY` rotated; verifier still accepts old key for
      its lifetime.
- [ ] HTTPS preload requested
      (https://hstspreload.org/?domain=keyhan.gold).
- [ ] CSP header verified
      (https://csp-evaluator.withgoogle.com/?csp=https://keyhan.gold).
- [ ] Firewall locks ports 5432 / 6379 / 9000 / 9200 / 9300 to localhost.
- [ ] `pg_audit` (or pgaudit logical replication) writes to a separate
      bucket.
- [ ] Off-site backup tested by restoring into a staging env.
- [ ] PagerDuty hooked up to `audit.consistency.violation`,
      `aml.sanctions.hit`, `security.login.brute_force`.
- [ ] SBOM signed with cosign + verified at pull.
- [ ] Sentry DSN set; first error visible end-to-end.
- [ ] Privacy + Terms pages reviewed by legal.

## 7. Rolling back

```bash
# Find the previous green tag
git log --oneline --tags

# Roll back containers
git checkout <prev-tag>
docker compose -f compose.yml up -d --build

# If a migration is incompatible: restore the latest pre-migration
# Postgres dump (see scripts/backup.sh) and apply only the safe subset.
```

## 8. Cost note

A single-host deployment runs comfortably on a 4-vCPU / 8-GiB VM for
the first few hundred concurrent users. The bottleneck at scale is
Elasticsearch ingestion (~5 K events/s on this host) — see the
horizontal-scaling note in §5.3.
