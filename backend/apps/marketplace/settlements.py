"""Daily vendor settlement task.

For each approved vendor, sums the marketplace orders that completed
yesterday, subtracts the platform commission, and creates a
`VendorSettlement` row plus a wallet credit transaction.
"""
from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db import models, transaction
from django.utils import timezone

from apps.audit.emit import emit_event


class VendorSettlement(models.Model):
    """A settlement run: one row per (vendor, day)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        "marketplace.Vendor", on_delete=models.PROTECT, related_name="settlements"
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    gross_rial = models.BigIntegerField(default=0)
    commission_rial = models.BigIntegerField(default=0)
    net_rial = models.BigIntegerField(default=0)
    orders_count = models.PositiveIntegerField(default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "marketplace"
        verbose_name = "Vendor settlement"
        indexes = [models.Index(fields=["vendor", "-period_end"])]


@shared_task(name="marketplace.settle_vendors")
def settle_vendors() -> dict[str, int]:
    """Aggregate yesterday's completed marketplace orders per vendor."""
    from apps.orders.models import Order
    from apps.wallet.services import credit_rial

    from .models import Vendor

    now = timezone.now()
    start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(hour=23, minute=59, second=59)
    runs = 0
    with transaction.atomic():
        for v in Vendor.objects.filter(state="approved"):
            qs = Order.objects.filter(
                kind="marketplace", vendor=v, state="completed",
                paid_at__gte=start, paid_at__lte=end,
            )
            gross = qs.aggregate(s=models.Sum("rial_amount"))["s"] or 0
            if gross == 0:
                continue
            commission = int((Decimal(gross) * Decimal(v.commission_rate)).to_integral_value())
            net = gross - commission
            s = VendorSettlement.objects.create(
                vendor=v, period_start=start, period_end=end,
                gross_rial=gross, commission_rial=commission, net_rial=net,
                orders_count=qs.count(),
            )
            if net > 0:
                try:
                    credit_rial(v.user, net, kind="adjustment",
                                description=f"تسویه روزانه فروشگاه {v.shop_name}")
                    s.paid_at = timezone.now()
                    s.save(update_fields=["paid_at"])
                except Exception as exc:  # noqa: BLE001
                    s.notes = f"credit failed: {exc!r}"
                    s.save(update_fields=["notes"])
            emit_event(
                "marketplace.settlement.run",
                target={"type": "vendor", "id": str(v.id)},
                data={"gross": gross, "commission": commission, "net": net,
                      "orders": qs.count()},
            )
            runs += 1
    return {"runs": runs}
