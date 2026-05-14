"""
`emit_event` — the single function the rest of the codebase uses to log
domain events.

Contract:
  * Validates `kind` against the catalogue.
  * Auto-fills correlation IDs from contextvars.
  * Writes to Redis Streams (production) or InMemorySink (tests).
  * Echoes the event to structlog so Filebeat picks it up too.
  * Never raises into business code — failures are logged + counted.

Returns the event's ULID.
"""
from __future__ import annotations

import socket
from datetime import datetime, timezone
from typing import Any, Literal

from django.conf import settings
from ulid import ULID

from .catalogue import get as get_spec
from .context import get_context
from .log import get_logger
from .schema import (
    Actor,
    Correlation,
    Envelope,
    EventMeta,
    Service,
    StateTransition,
    Target,
)
from .sinks import get_sink

_log = get_logger("audit.emit")
_HOST = socket.gethostname()


def emit_event(
    kind: str,
    *,
    actor: Actor | dict | None = None,
    target: Target | dict | None = None,
    state: StateTransition | None = None,
    data: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    severity: Literal["debug", "info", "warning", "error", "critical"] | None = None,
    outcome: Literal["success", "failure", "denied"] = "success",
    category: str | None = None,
    causation_id: str = "",
) -> str:
    spec = get_spec(kind)
    event_id = str(ULID())

    ctx = get_context()

    if isinstance(actor, dict):
        actor_obj = Actor.model_validate(actor)
    elif actor is None:
        actor_obj = Actor(
            type="user" if ctx.user_id else "system",
            id=ctx.user_id,
            ip=ctx.ip,
            user_agent=ctx.user_agent,
            session_id=ctx.session_id,
            roles=list(ctx.roles),
        )
    else:
        actor_obj = actor

    if isinstance(target, dict):
        target_obj: Target | None = Target.model_validate(target)
    else:
        target_obj = target

    envelope = Envelope(
        timestamp=datetime.now(timezone.utc),
        event=EventMeta(
            id=event_id,
            kind=kind,
            category=category or spec.category,  # type: ignore[arg-type]
            severity=severity or spec.default_severity,
            outcome=outcome,
        ),
        actor=actor_obj,
        target=target_obj,
        correlation=Correlation(
            trace_id=ctx.trace_id,
            span_id=ctx.span_id,
            request_id=ctx.request_id,
            causation_id=causation_id or ctx.causation_id,
            session_id=ctx.session_id,
        ),
        state=state,
        data=data or {},
        tags=tags or [],
        service=Service(
            name=getattr(settings, "SERVICE_NAME", "keyhan-backend"),
            version=getattr(settings, "SERVICE_VERSION", "0.1.0"),
            env=getattr(settings, "SERVICE_ENV", "dev"),
            host=_HOST,
        ),
    )

    payload = envelope.to_payload()
    # 1) ship to the structured sink
    try:
        get_sink().write(envelope)
    except Exception as exc:  # noqa: BLE001
        _log.error("audit_sink_failed", error=repr(exc), kind=kind)
    # 2) also echo to logs (Filebeat) — never raise
    try:
        _log.info("event", **payload)
    except Exception:  # noqa: BLE001
        pass
    return event_id
