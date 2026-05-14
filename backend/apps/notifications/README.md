# `apps.notifications` — In-app + SMS notifications

## Model

`Notification` — `user`, `kind` (`info / success / warning / error`),
`title`, `body`, `url`, `read`, `metadata`, `created_at`. Indexed on
`(user, read, -created_at)` for the unread-first list.

## Service

```python
from apps.notifications.services import notify

notify(user=u, kind="success", title="پرداخت موفق",
       body="سفارش KG-2026... تکمیل شد.", url=f"/orders/{order.id}",
       sms=False)
```

It:
1. Persists a `Notification` row.
2. Pushes via Channels to group `user-<uuid>` (the user's open `/ws/me/` socket).
3. Optionally sends a Kavenegar SMS when `sms=True`.

## Channels consumer

`apps/notifications/consumers.py::UserNotificationConsumer` joins the
group `user-<id>` on connect and forwards every `user_notify`
group message verbatim.

## Endpoints

```
GET  /api/v1/notifications
POST /api/v1/notifications/<id>/read
POST /api/v1/notifications/read-all
WS   /ws/me/                              ← live push
```

## Use cases

Call `notify(...)` from anywhere a user-visible event happens —
order completion, KYC decision, delivery state change, withdraw
processed, AML flag (admin-only), etc. The pattern is: emit the audit
event first (for ES), then `notify` (for the user).
