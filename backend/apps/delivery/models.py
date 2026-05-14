"""Physical delivery requests."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryRequest(models.Model):
    STATES = [
        ("pending", _("در انتظار تأیید")),
        ("approved", _("تأیید شد")),
        ("minting", _("در حال ضرب و پلمپ")),
        ("shipped", _("ارسال شد")),
        ("delivered", _("تحویل داده شد")),
        ("cancelled", _("لغو شد")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="delivery_requests"
    )
    asset = models.CharField(max_length=10, default="gold")
    requested_mg = models.BigIntegerField()
    bars_breakdown = models.JSONField(default=dict, blank=True)
    processing_fee_rial = models.BigIntegerField(default=0)
    tracking_code = models.CharField(max_length=40, blank=True)
    shipping_address = models.TextField()
    recipient_name = models.CharField(max_length=120)
    recipient_national_id = models.CharField(max_length=10)
    recipient_phone = models.CharField(max_length=15)
    state = models.CharField(max_length=20, choices=STATES, default="pending")
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
