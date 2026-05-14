"""Per-user WebSocket: notifications, order updates."""
from __future__ import annotations

import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class UserNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return
        self.group = f"user-{user.id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code: int) -> None:  # noqa: ARG002
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def user_notify(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
