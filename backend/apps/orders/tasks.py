"""Background tasks: expire awaiting_payment orders."""
from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from apps.audit.emit import emit_event

from .models import Order
from .services import expire_order


@shared_task(name="orders.expire_due")
def expire_due() -> int:
    now = timezone.now()
    due = Order.objects.filter(state="awaiting_payment", payment_deadline__lte=now)
    n = 0
    for o in due.iterator():
        try:
            expire_order(o)
            n += 1
        except Exception as exc:  # noqa: BLE001
            emit_event("system.celery.task.failed", severity="error",
                       data={"task": "orders.expire_due", "order_id": str(o.id), "error": repr(exc)})
    return n
