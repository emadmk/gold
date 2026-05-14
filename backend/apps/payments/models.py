"""Payment attempt model: one row per gateway interaction."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentAttempt(models.Model):
    GATEWAYS = [
        ("zarinpal", _("زرین‌پال")),
        ("idpay", _("آیدی‌پی")),
        ("payping", _("پی‌پینگ")),
    ]
    STATES = [
        ("pending", _("در انتظار")),
        ("redirected", _("در درگاه")),
        ("succeeded", _("موفق")),
        ("failed", _("ناموفق")),
        ("cancelled", _("لغو شده")),
        ("expired", _("منقضی")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        "orders.Order", on_delete=models.PROTECT, related_name="payment_attempts"
    )
    gateway = models.CharField(max_length=20, choices=GATEWAYS)
    amount_rial = models.BigIntegerField()
    authority = models.CharField(max_length=120, blank=True, db_index=True)
    ref_id = models.CharField(max_length=120, blank=True, db_index=True)
    card_pan_masked = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, choices=STATES, default="pending")
    raw_request = models.JSONField(default=dict, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "-created_at"]),
            models.Index(fields=["gateway", "state"]),
        ]
        verbose_name = _("Payment attempt")
