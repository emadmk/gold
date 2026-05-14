"""
Eventual-consistency reconciliation.

For each `AuditEntry` row in the lookback window, ask Elasticsearch
whether an event with the matching ULID exists. If not, re-emit it.

If Elasticsearch is unreachable, the task degrades gracefully: every
entry not marked `synced=True` is re-emitted (at-least-once).
"""
from __future__ import annotations

from datetime import timedelta

import httpx
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .emit import emit_event
from .models import AuditEntry


def _es_has_event(event_id: str) -> bool | None:
    """Return True/False if ES is reachable, None on transport error."""
    if not settings.ELASTICSEARCH_HOSTS:
        return None
    host = settings.ELASTICSEARCH_HOSTS[0]
    auth = (settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
    try:
        with httpx.Client(timeout=5, auth=auth) as c:
            r = c.get(
                f"{host}/keyhan-events-*/_count",
                params={"q": f"event.id:{event_id}"},
            )
        if r.status_code != 200:
            return None
        return int(r.json().get("count", 0)) > 0
    except Exception:  # noqa: BLE001
        return None


@shared_task(name="audit.reconcile")
def reconcile_entries(limit: int = 1000, lookback_hours: int = 24) -> int:
    """Re-emit audit entries missing from Elasticsearch."""
    since = timezone.now() - timedelta(hours=lookback_hours)
    qs = (
        AuditEntry.objects.filter(created_at__gte=since)
        .order_by("-created_at")[:limit]
    )
    re_emitted = 0
    for e in qs:
        if e.data and e.data.get("synced"):
            continue
        present = _es_has_event(str(e.id))
        if present is True:
            e.data = {**(e.data or {}), "synced": True}
            e.save(update_fields=["data"])
            continue
        emit_event(
            e.kind,
            actor={"type": "system", "id": e.actor_id} if e.actor_id else None,
            target={"type": e.target_type, "id": e.target_id} if e.target_type else None,
            data=e.data or {},
            severity=e.severity,  # type: ignore[arg-type]
            outcome=e.outcome,  # type: ignore[arg-type]
        )
        re_emitted += 1
        e.data = {**(e.data or {}), "synced": True}
        e.save(update_fields=["data"])
    return re_emitted
