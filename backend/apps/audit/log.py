"""
structlog bootstrap.

Outputs JSON to stdout — Filebeat picks it up. All Django + Celery logging
funnels through structlog so a single processor chain handles redaction and
correlation injection.
"""
from __future__ import annotations

import logging
import re
import sys
from typing import Any

import structlog

from .context import get_context

_PHONE_RE = re.compile(r"\b(0\d{2})(\d{5})(\d{3})\b")
_PAN_RE = re.compile(r"\b\d{12,19}\b")
_NID_RE = re.compile(r"\b\d{10}\b")  # rough Iranian national ID
_REDACT_KEYS = {"password", "secret", "token", "authorization", "cookie", "set-cookie", "api_key"}


def _inject_context(_logger: Any, _name: str, event: dict[str, Any]) -> dict[str, Any]:
    ctx = get_context()
    if ctx.request_id:
        event.setdefault("request_id", ctx.request_id)
    if ctx.trace_id:
        event.setdefault("trace_id", ctx.trace_id)
    if ctx.user_id:
        event.setdefault("user_id", ctx.user_id)
    return event


def _redact(_logger: Any, _name: str, event: dict[str, Any]) -> dict[str, Any]:
    for k in list(event.keys()):
        if k.lower() in _REDACT_KEYS:
            event[k] = "***"
    # Walk shallow scalars
    for k, v in list(event.items()):
        if not isinstance(v, str):
            continue
        v2 = _PHONE_RE.sub(r"\1*****\3", v)
        v2 = _PAN_RE.sub(lambda m: "*" * (len(m.group(0)) - 4) + m.group(0)[-4:], v2)
        v2 = _NID_RE.sub("**********", v2)
        if v2 != v:
            event[k] = v2
    return event


def configure_logging() -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    processors = [
        structlog.contextvars.merge_contextvars,
        _inject_context,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        _redact,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    # Route stdlib logging to structlog too
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
