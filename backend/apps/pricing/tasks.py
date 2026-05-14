"""Celery tasks for price ingestion + broadcast."""
from __future__ import annotations

import asyncio
import json

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.audit.emit import emit_event

from .crawler import fetch_with_fallback
from .formulas import gold_buy_per_mg, gold_sell_per_mg, silver_buy_per_mg, silver_sell_per_mg
from .models import PriceTick, SOURCE_KEYS


def _redis():  # pragma: no cover
    import redis
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


@shared_task(name="pricing.crawl_all")
def crawl_all() -> dict:
    """Crawl every source, persist a PriceTick, push a snapshot to Redis."""
    snapshot: dict[str, int] = {}
    loop = asyncio.new_event_loop()
    try:
        for key in SOURCE_KEYS:
            try:
                price, source = loop.run_until_complete(fetch_with_fallback(key))
                rial = int(price)
                PriceTick.objects.create(
                    source_key=key,
                    rial_price=rial,
                    captured_at=timezone.now(),
                    source=source,
                )
                snapshot[key] = rial
                _redis().set(f"price:{key}", rial, ex=120)
                emit_event(
                    "pricing.tick.captured",
                    severity="debug",
                    target={"type": "price", "id": key},
                    data={"source": source, "rial": rial},
                )
            except Exception as exc:  # noqa: BLE001
                emit_event(
                    "pricing.tick.stale", severity="warning", outcome="failure",
                    target={"type": "price", "id": key},
                    data={"error": repr(exc)},
                )
    finally:
        loop.close()

    # Push computed quotes too
    if "gold_18k_750" in snapshot:
        snapshot["buy_per_mg"] = gold_buy_per_mg(snapshot["gold_18k_750"])
        snapshot["sell_per_mg"] = gold_sell_per_mg(snapshot["gold_18k_750"])
    if "silver_999" in snapshot:
        snapshot["silver_buy_per_mg"] = silver_buy_per_mg(snapshot["silver_999"])
        snapshot["silver_sell_per_mg"] = silver_sell_per_mg(snapshot["silver_999"])

    payload = {"type": "price_update", "ts": timezone.now().isoformat(), "data": snapshot}
    _redis().publish("prices:live", json.dumps(payload))
    return snapshot
