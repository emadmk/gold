"""
Eventual-consistency reconciliation.

If `emit_event` fails (sink down) but a state transition committed to
the DB, this task rebuilds the missing events from `AuditEntry` rows.

Runs hourly via celery-beat.
"""
from __future__ import annotations

from celery import shared_task

from .emit import emit_event
from .models import AuditEntry


@shared_task(name="audit.reconcile")
def reconcile_entries(limit: int = 1000) -> int:
    """Re-emit audit entries whose ULID does not appear in the sink.

    Without a real ES query path this implementation simply re-emits the
    last `limit` entries that have not been marked as `synced`. A future
    improvement runs a search against ES and only re-emits the missing
    ones — but the API on this side is stable.
    """
    qs = AuditEntry.objects.filter(data__synced=False)[:limit]
    count = 0
    for e in qs:
        emit_event(
            e.kind,
            actor={"type": "system", "id": e.actor_id},
            target={"type": e.target_type, "id": e.target_id} if e.target_type else None,
            data=e.data or {},
            severity=e.severity,  # type: ignore[arg-type]
            outcome=e.outcome,  # type: ignore[arg-type]
        )
        count += 1
        e.data = {**(e.data or {}), "synced": True}
        e.save(update_fields=["data"])
    return count
