"""
Feature flags — Redis-backed with sensible defaults from settings.

Public API:
  is_enabled(name, *, user=None, percent=0)
  set_flag(name, value)
  toggled events are emitted automatically.

Roadmap features (#1-20) all rely on this so they can be rolled out
gradually without code changes.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache

from django.conf import settings

from apps.audit.emit import emit_event


@lru_cache(maxsize=1)
def _redis():  # type: ignore[no-untyped-def]
    import redis

    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _key(name: str) -> str:
    return f"feature_flag:{name}"


def is_enabled(name: str, *, user=None, percent: int = 0) -> bool:  # type: ignore[no-untyped-def]
    """Return whether `name` is on for the (optional) user.

    Precedence: explicit Redis value > settings default > False.
    Percentage gates: if `percent > 0`, hash(user_id) % 100 < percent → on.
    """
    raw = _redis().get(_key(name))
    if raw is not None:
        if raw in ("1", "true", "True", "on"):
            return True
        if raw in ("0", "false", "False", "off"):
            return False
    default = settings.FEATURE_FLAGS_DEFAULT.get(name)
    if default is not None:
        return bool(default)
    if percent and user is not None:
        h = int(hashlib.sha256(str(user.id).encode()).hexdigest(), 16)
        return (h % 100) < percent
    return False


def set_flag(name: str, value: bool, *, actor_id: str = "") -> None:
    _redis().set(_key(name), "1" if value else "0")
    emit_event(
        "system.feature_flag.toggled",
        actor={"type": "admin", "id": actor_id} if actor_id else None,
        target={"type": "feature_flag", "id": name},
        data={"value": value},
    )
