"""WebSocket consumer: broadcasts the live price snapshot."""
from __future__ import annotations

import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer

GROUP = "prices_live"


class PriceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        await self.channel_layer.group_add(GROUP, self.channel_name)
        await self.accept()
        # On connect, send the last cached snapshot if any
        from django.conf import settings
        try:
            import redis as redis_lib

            r = redis_lib.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            data: dict[str, int] = {}
            for key in r.scan_iter("price:*"):
                value = r.get(key)
                if value:
                    data[key.split(":", 1)[1]] = int(value)
            await self.send_json({"type": "snapshot", "data": data})
        except Exception:  # noqa: BLE001
            pass

    async def disconnect(self, code: int) -> None:  # noqa: ARG002
        await self.channel_layer.group_discard(GROUP, self.channel_name)

    async def price_update(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
