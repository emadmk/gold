# Runbook — Ledger drift (`audit.consistency.violation`)

`consistency_tick` runs every 5 minutes and verifies the invariants in
`SECURITY.md §8`. When it emits `audit.consistency.violation` with
`severity=critical`, follow these steps.

## 1. Acknowledge

* PagerDuty alert routes to the on-call DBA.
* Within 5 minutes: page secondary if not picked up.

## 2. Triage

In Kibana, search `event.kind:audit.consistency.violation` and grab the
affected `target.id` (wallet UUID).

```sql
-- via psql:
SELECT u.phone, w.balance_rial, w.locked_rial
FROM wallet_rialwallet w JOIN accounts_user u ON u.id = w.user_id
WHERE w.id = '<target.id>';

SELECT type, asset, rial_amount, mg_amount, created_at, description
FROM wallet_wallettransaction
WHERE user_id = '<user uuid>' ORDER BY created_at DESC LIMIT 50;
```

Compute `sum(rial_amount) WHERE asset='rial'` and compare to
`balance_rial`. The delta tells you exactly what's missing.

## 3. Containment

If active fraud is suspected: `SYSTEM_HALT` (see other runbook).

If a single user is affected: freeze the user
(`/admin/users/<id>/freeze`).

## 4. Root cause

Common causes:
* `emit_event` failed; check `keyhan_audit_emit_failed_total` metric in
  Prometheus and the `audit.reconcile` task's last run.
* A migration changed a column default — review recent migration logs.
* A direct DB write bypassed services — search the audit log for
  the suspected change window.

## 5. Reconciliation

After root cause is fixed, write a one-off `WalletTransaction(type="adjustment")`
that brings the balance back in line and document it in an ADR.

Re-run `consistency_tick` manually:

```bash
docker compose exec celery_worker celery -A core call wallet.consistency_tick
```
