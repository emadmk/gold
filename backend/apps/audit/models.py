"""
Idempotency + persistent audit storage.

Even though events live primarily in Redis Streams → Elasticsearch, we keep
a relational copy of two critical concerns:

* `IdempotencyKey` — payment webhooks (and any other duplicate-detection
  path) record the (gateway, key) pair to short-circuit replays.
* `AuditEntry` — a slim local record of state transitions, useful for
  forensic SQL queries and for the eventual-consistency reconciliation
  job (see OBSERVABILITY.md §13).
"""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class IdempotencyKey(models.Model):
    """Stops duplicate webhook / external callback processing."""

    scope = models.CharField(max_length=40, db_index=True)
    key = models.CharField(max_length=128, db_index=True)
    response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = (("scope", "key"),)
        verbose_name = _("Idempotency key")

    def __str__(self) -> str:
        return f"{self.scope}:{self.key}"


class AuditEntry(models.Model):
    """Local copy of an event for SQL-side forensics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=80, db_index=True)
    category = models.CharField(max_length=20, db_index=True)
    actor_id = models.CharField(max_length=64, blank=True, db_index=True)
    target_type = models.CharField(max_length=40, blank=True, db_index=True)
    target_id = models.CharField(max_length=64, blank=True, db_index=True)
    request_id = models.CharField(max_length=64, blank=True, db_index=True)
    trace_id = models.CharField(max_length=64, blank=True, db_index=True)
    severity = models.CharField(max_length=10, default="info")
    outcome = models.CharField(max_length=10, default="success")
    state_from = models.CharField(max_length=40, blank=True)
    state_to = models.CharField(max_length=40, blank=True)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["kind", "-created_at"]),
            models.Index(fields=["actor_id", "-created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]
        verbose_name = _("Audit entry")
        verbose_name_plural = _("Audit entries")
