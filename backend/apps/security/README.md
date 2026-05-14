# `apps.security` — Middleware, rate limit, crypto, feature flags, risk, uploads

The defensive layer. Everything that protects the domain lives here.

## Modules

| File | Purpose |
|------|---------|
| `middleware.py` | `SecurityHeadersMiddleware` (CSP-friendly headers; defence-in-depth alongside Traefik) and `RateLimitMiddleware` (Redis sliding-window). |
| `ratelimit.py` | True sliding window via Redis sorted-set (`ZADD`/`ZREMRANGEBYSCORE`/`ZCARD`). |
| `crypto.py` | `encrypt_field` / `decrypt_field` (Fernet), `constant_time_eq`, `random_token`, `hash_sha256`. |
| `fields.py` | `EncryptedCharField` — transparent at-rest encryption for PII columns. |
| `feature_flags.py` | Redis-backed flags with settings defaults + percentage gates. Toggle emits `system.feature_flag.toggled`. |
| `plugins.py` | `entry_points("keyhan.plugins")` loader for third-party extensions. |
| `exceptions.py` | DRF exception handler that returns Persian `detail` + emits `security.permission.denied`. |
| `uploads.py` | `validate_upload` (size + MIME whitelist + magic-byte sniffing) + `reencode_image` (strip metadata). |
| `risk/engine.py` | Deterministic AML scorer; returns `RiskDecision(score, action, reasons)`. Roadmap #1 swaps this for an ML endpoint. |
| `aml.py` | `aml_tick` Celery task — velocity rule over the last 24 h. |

## Rate-limit rules

Declared in `middleware.RateLimitMiddleware._RATE_RULES`:

| Path | Method | Limit | Window |
|------|--------|-------|--------|
| `/api/v1/auth/otp/request` | POST | 5 | 15 min |
| `/api/v1/auth/otp/verify`  | POST | 5 | 15 min |
| `/api/v1/wallet/withdraw`  | POST | 3 | 1 h |
| `/api/v1/orders/...`       | POST | 60 | 1 min |

Excess returns `429` with `Retry-After` + emits
`security.ratelimit.breach`.

## Upload validation

`validate_upload(file, allowed_mimes=…, max_bytes=…)`:
1. Size check.
2. Declared `Content-Type` whitelist.
3. Magic-byte sniff (python-magic when available; falls back to a
   prefix table for JPEG/PNG/WebP/PDF/MP4/WebM).
4. Image re-encoding (Pillow) strips metadata — embedded payloads
   die during conversion.

Used by KYC submission, vendor onboarding, and blog covers.

## Events emitted

`security.login.brute_force / ratelimit.breach / csrf.failure /
permission.denied / token.blacklisted`, `system.feature_flag.toggled`,
`aml.threshold.high`.

## CI gates owned

`security-check` (Makefile): `bandit -r apps core` + `pip-audit`.

## Tests

`tests/test_upload_validation.py` — JPEG/PNG accepted, PDF rejected
when only images allowed, oversize/empty rejected, "PDF disguised as
JPEG" caught.
