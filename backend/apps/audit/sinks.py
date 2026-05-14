"""
Event sinks.

A sink is the destination of a validated `Envelope`. Production uses
`RedisStreamSink`; tests use `InMemorySink`. Both implement `write(envelope)`.
"""
from __future__ import annotations

import json
import threading
from typing import Protocol

from django.conf import settings

from .schema import Envelope


class EventSink(Protocol):
    def write(self, envelope: Envelope) -> None: ...


class InMemorySink:
    """Thread-safe accumulator used by tests."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.events: list[Envelope] = []

    def write(self, envelope: Envelope) -> None:
        with self._lock:
            self.events.append(envelope)

    def clear(self) -> None:
        with self._lock:
            self.events.clear()

    def filter(self, kind: str) -> list[Envelope]:
        with self._lock:
            return [e for e in self.events if e.event.kind == kind]


class RedisStreamSink:
    """Writes to Redis Streams; Logstash consumes via XREADGROUP."""

    def __init__(self) -> None:
        # Lazy import so test env without redis still loads
        import redis

        self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self._prefix = getattr(settings, "AUDIT_STREAM_PREFIX", "domain_events")
        self._maxlen = getattr(settings, "AUDIT_REDIS_MAXLEN", 1_000_000)

    def write(self, envelope: Envelope) -> None:
        payload = envelope.to_payload()
        stream = f"{self._prefix}.{envelope.event.category}"
        self._redis.xadd(
            stream,
            {"event": json.dumps(payload, separators=(",", ":"), ensure_ascii=False)},
            maxlen=self._maxlen,
            approximate=True,
        )


_sink: EventSink | None = None
_sink_lock = threading.Lock()


def get_sink() -> EventSink:
    global _sink
    if _sink is None:
        with _sink_lock:
            if _sink is None:
                path = getattr(settings, "AUDIT_SINK", "apps.audit.sinks.RedisStreamSink")
                module_name, _, cls_name = path.rpartition(".")
                module = __import__(module_name, fromlist=[cls_name])
                _sink = getattr(module, cls_name)()
    return _sink


def reset_sink() -> None:  # for tests
    global _sink
    _sink = None
