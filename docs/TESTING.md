# KeyhanGold — Testing Strategy

How we keep the platform correct + fast over the years.

## 1. The test pyramid (current state)

```
                ┌──────────────────┐
                │  E2E smoke (4)   │   ← whole flow, no mocks
                └────────┬─────────┘
                ┌────────┴─────────────────┐
                │  Integration (Django,    │   ← DB + ORM + services
                │  DRF API client) (~30)   │
                └────────┬─────────────────┘
        ┌────────────────┴───────────────────┐
        │  Service unit tests (~70)          │
        │  (wallet, pricing, state machine,  │
        │   audit envelope, upload, etc.)    │
        └────────────────────────────────────┘
               115 tests total — all green
```

## 2. What we test (by file)

| File | What it covers |
|------|----------------|
| `tests/test_audit_envelope.py` | Catalogue parity, envelope round-trip, category check |
| `tests/test_state_machines.py` | Legal/illegal transitions on all 5 SMs |
| `tests/test_wallet_invariants.py` | Debit-below-zero blocked; locked ≤ balance; sum(tx) == balance |
| `tests/test_pricing_formulas.py` | buy > base > sell; spread changes flow through |
| `tests/test_payment_gateway.py` | Zarinpal / IDPay / PayPing happy + error path, all with mocked httpx |
| `tests/test_upload_validation.py` | JPEG/PNG/PDF whitelist, oversize/empty rejection, magic-byte lie detection |
| `tests/test_blog_api.py` | Drafts hidden, view counter, 404 on unpublished |
| `tests/test_race_conditions.py` | Two-thread debit, overdraft under concurrency, ledger invariant after concurrent mixed ops |
| `tests/test_e2e_smoke.py` | Full flow: register → topup → buy → sell → transfer → expire → idempotent callback |

## 3. The four CI gates

These four checks must all be green; CI rejects the PR otherwise.

| Gate | What it verifies | Command |
|------|------------------|---------|
| `event_coverage` | Every kind a state-machine transition declares is registered in the catalogue | `python -m apps.audit.checks event_coverage` |
| `catalogue` | Catalogue has no duplicates | `python -m apps.audit.checks catalogue` |
| `sm_coverage` | Every state machine has ≥ 1 transition | `python -m apps.audit.checks sm_coverage` |
| `seam_check` | 20 roadmap seams are still present in the v1 code | `python scripts/seam_check.py` |

Plus the standard ones: `ruff`, `mypy`, `pytest`, `tsc`, `eslint`.

## 4. Running tests

```bash
# Inside the dev stack
make test                     # backend pytest -q
make observability-check      # the 3 audit gates
make seam-check               # the seam gate
make all-checks               # all the above

# Or from the host (with a local venv)
cd backend && DJANGO_SETTINGS_MODULE=core.settings.test pytest -q
```

## 5. Test conventions

* **DB**: `pytest-django` with SQLite in-memory by default.
* **`@pytest.mark.django_db`** on every test that touches models.
* **`@pytest.mark.django_db(transaction=True)`** for threaded tests
  (`test_race_conditions.py`) — required because each thread needs to
  own a transaction.
* **HTTP boundary**: use `rest_framework.test.APIClient`, not raw
  Django `Client`, so DRF's auth/parsing/exception paths are
  exercised.
* **Network**: never. Monkeypatch `httpx.Client` (see
  `test_payment_gateway.py`).
* **Time**: use `freezegun` for time-sensitive tests
  (order expiry, OTP TTL) — already in `requirements/dev.txt`.
* **Files**: build `SimpleUploadedFile` with real magic-byte headers,
  not Lorem-ipsum bytes (see `test_upload_validation.py`).

## 6. What we don't test (yet) and why

| Gap | Why it's acceptable today | When to fix |
|-----|---------------------------|-------------|
| Playwright frontend E2E | Requires a long-running browser in CI | When we add a UI regression |
| Load test (locust / k6) | Premature; we have no production load yet | Pre-launch |
| Real ES round-trip | Adds 30 s+ to CI; reconcile + emit cover it logically | If reconcile starts misbehaving |
| Real Postgres in CI | SQLite + retry covers our race tests | When we hit a Postgres-only feature (`RETURNING`, …) |

## 7. Adding a test for a new feature

1. **State change?** Add a unit test in `test_state_machines.py`
   covering the new transition (legal + illegal).
2. **Event emitted?** Make sure the envelope is correct in
   `test_audit_envelope.py` parameter list.
3. **Money mutation?** Add an invariant test in
   `test_wallet_invariants.py`.
4. **API endpoint?** Add an `APIClient` test in an app-specific file
   (e.g. `test_marketplace_api.py`).
5. **External call?** Mock with `monkeypatch.setattr(httpx, "Client", …)`
   à la `test_payment_gateway.py`.

## 8. Coverage targets

| Area | Target | Tool |
|------|--------|------|
| `apps/wallet`, `apps/orders`, `apps/payments`, `apps/pricing` | ≥ 80 % branch | `pytest --cov` |
| Rest of `apps/*` | ≥ 60 % branch | same |
| `apps/audit` | 100 % line on `state_machine.py`, `catalogue.py`, `schema.py` | same |

Run with:

```bash
pytest --cov=apps --cov-report=term-missing
```

(The coverage report is not a CI gate today; we'll wire one in once
the platform stabilises.)

## 9. Test fixtures

Where to add them:

* **Per-file**: `@pytest.fixture` at the top of the test file.
* **Per-app**: a `conftest.py` in `backend/apps/<app>/tests/conftest.py`
  (none yet — opportunity).
* **Repo-wide**: a `backend/tests/conftest.py`. Currently empty.

Recommended factories (factory-boy) — already a dep — for high-volume
tests:

```python
# backend/tests/factories.py
class UserFactory(factory.django.DjangoModelFactory):
    class Meta: model = User
    phone = factory.Sequence(lambda n: f"0912000{n:04d}")
```

## 10. Pre-commit

Set up locally (one-time):

```bash
pip install pre-commit
pre-commit install
```

The hooks run `ruff`, `black --check`, `eslint`, `tsc --noEmit`,
`gitleaks`, and the 4 CI gates on every commit.

## 11. Continuous integration

Workflow file: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

Jobs:
* **`backend`** — install → catalogue + SM + seam checks → ruff →
  pytest.
* **`frontend`** — install → typecheck → lint.
* **`security`** — gitleaks → pip-audit → bandit → trivy.

A PR is mergeable only when all three jobs are green.
