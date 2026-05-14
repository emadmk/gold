"""Notification service: persist + push via WebSocket + (optional) SMS."""
from __future__ import annotations

from typing import Any

import httpx
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

from .models import Notification


def notify(
    *,
    user,
    kind: str = "info",
    title: str,
    body: str = "",
    url: str = "",
    sms: bool = False,
    metadata: dict[str, Any] | None = None,
) -> Notification:
    """Persist + push notification + (optionally) SMS."""
    notif = Notification.objects.create(
        user=user, kind=kind, title=title, body=body, url=url,
        metadata=metadata or {},
    )
    layer = get_channel_layer()
    if layer is not None:
        try:
            async_to_sync(layer.group_send)(
                f"user-{user.id}",
                {
                    "type": "user_notify",
                    "payload": {
                        "id": str(notif.id), "kind": kind, "title": title,
                        "body": body, "url": url,
                        "created_at": notif.created_at.isoformat(),
                    },
                },
            )
        except Exception:  # noqa: BLE001
            pass
    if sms and settings.KAVENEGAR_API_KEY:
        try:
            sms_url = (
                f"https://api.kavenegar.com/v1/{settings.KAVENEGAR_API_KEY}/sms/send.json"
            )
            with httpx.Client(timeout=8) as c:
                c.get(sms_url, params={"receptor": user.phone, "message": f"{title}\n{body}"})
        except Exception:  # noqa: BLE001
            pass
    return notif
