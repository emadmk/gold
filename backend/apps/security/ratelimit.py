"""
Redis fixed-window rate limiter.

Returns (allowed, remaining, reset_unix). Uses INCR + EXPIRE — simple,
race-safe enough for our threat model. Drop-in replacement: swap for a
sliding-window or token-bucket implementation later without changing
callers.
"""
from __future__ import annotations

import time
from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def _redis():  # type: ignore[no-untyped-def]
    import redis  # local import keeps test settings happy

    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def allow(*, key: str, limit: int, window_s: int) -> tuple[bool, int, float]:
    r = _redis()
    now = int(time.time())
    bucket = now // window_s
    k = f"{key}:{bucket}"
    pipe = r.pipeline()
    pipe.incr(k)
    pipe.expire(k, window_s)
    count, _ = pipe.execute()
    remaining = max(0, limit - int(count))
    reset = (bucket + 1) * window_s
    return int(count) <= limit, remaining, float(reset)
