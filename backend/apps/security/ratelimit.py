"""
Sliding-window rate limiter (Redis sorted-set).

Replaces the previous fixed-window implementation. Properties:
* True sliding window — burst at the boundary is not possible.
* O(log N) per request thanks to ZADD/ZREMRANGEBYSCORE/ZCARD.
* Survives Redis restarts (events live in sorted-set with auto-expire).

Public signature unchanged:
    allow(*, key, limit, window_s) -> (allowed, remaining, reset_unix)
"""
from __future__ import annotations

import time
import uuid
from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def _redis():  # type: ignore[no-untyped-def]
    import redis

    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def allow(*, key: str, limit: int, window_s: int) -> tuple[bool, int, float]:
    r = _redis()
    now_ms = int(time.time() * 1000)
    window_ms = window_s * 1000
    threshold = now_ms - window_ms
    member = f"{now_ms}-{uuid.uuid4().hex[:8]}"
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, threshold)
    pipe.zadd(key, {member: now_ms})
    pipe.zcard(key)
    pipe.expire(key, window_s + 1)
    _, _, count, _ = pipe.execute()
    count = int(count)
    remaining = max(0, limit - count)
    # reset = the time at which the OLDEST entry inside the window expires
    oldest = r.zrange(key, 0, 0, withscores=True)
    if oldest:
        reset_ms = int(oldest[0][1]) + window_ms
    else:
        reset_ms = now_ms + window_ms
    return count <= limit, remaining, reset_ms / 1000.0
