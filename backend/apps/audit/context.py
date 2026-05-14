"""
Per-request context propagation.

Holds correlation IDs (request_id, trace_id, span_id, user_id, session_id)
in contextvars so that structlog and emit_event can read them without
explicit plumbing.
"""
from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RequestContext:
    request_id: str = ""
    trace_id: str = ""
    span_id: str = ""
    causation_id: str = ""
    user_id: str = ""
    session_id: str = ""
    roles: tuple[str, ...] = ()
    ip: str = ""
    user_agent: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


_ctx: contextvars.ContextVar[RequestContext] = contextvars.ContextVar(
    "keyhan_request_ctx", default=RequestContext()
)


def get_context() -> RequestContext:
    return _ctx.get()


def set_context(ctx: RequestContext) -> contextvars.Token[RequestContext]:
    return _ctx.set(ctx)


def update_context(**fields: Any) -> contextvars.Token[RequestContext]:
    cur = _ctx.get()
    new = RequestContext(**{**cur.__dict__, **fields})
    return _ctx.set(new)


def clear_context() -> None:
    _ctx.set(RequestContext())


def bind_celery_context(task_id: str | None, task_name: str, headers: Any) -> None:
    """Called from celery signal — restores correlation IDs from task headers."""
    h = getattr(headers, "headers", {}) or {}
    set_context(
        RequestContext(
            request_id=h.get("request_id", "") or task_id or "",
            trace_id=h.get("trace_id", ""),
            span_id=h.get("span_id", ""),
            causation_id=h.get("causation_id", ""),
            user_id=h.get("user_id", ""),
            extra={"task": task_name, "task_id": task_id or ""},
        )
    )
