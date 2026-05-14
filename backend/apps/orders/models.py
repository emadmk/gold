"""Orders + OrderItems."""
from __future__ import annotations

import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_order_number() -> str:
    from datetime import datetime

    today = datetime.utcnow().strftime("%Y%m")
    rnd = secrets.token_hex(3).upper()
    return f"KG-{today}-{rnd}"


class Order(models.Model):
    KINDS = [
        ("buy_gold", _("خرید طلا از سامانه")),
        ("sell_gold", _("فروش طلا به سامانه")),
        ("buy_silver", _("خرید نقره از سامانه")),
        ("sell_silver", _("فروش نقره به سامانه")),
        ("marketplace", _("خرید از فروشنده")),
        ("wallet_topup", _("شارژ کیف پول")),
        # Roadmap seams (#3 DCA, #6 stop-loss, #7 margin, #8 loan, #17 sub, …)
        ("dca", _("خرید دوره‌ای")),
        ("subscription", _("اشتراک ویژه")),
        ("auction_bid", _("پیشنهاد در حراج")),
    ]
    STATES = [
        ("draft", _("پیش‌نویس")),
        ("awaiting_payment", _("در انتظار پرداخت")),
        ("paid", _("پرداخت شد")),
        ("processing", _("در حال پردازش")),
        ("completed", _("تکمیل شد")),
        ("expired", _("منقضی شد")),
        ("cancelled", _("لغو شد")),
        ("refunded", _("بازگشت داده شد")),
        ("failed", _("ناموفق")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)
    order_number = models.CharField(max_length=24, unique=True, db_index=True, default=generate_order_number)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    kind = models.CharField(max_length=20, choices=KINDS)
    state = models.CharField(max_length=20, choices=STATES, default="draft")

    quote = models.ForeignKey(
        "pricing.PriceQuote", on_delete=models.PROTECT, null=True, blank=True
    )
    price_per_mg_rial = models.BigIntegerField(default=0)
    mg_amount = models.BigIntegerField(default=0)
    rial_amount = models.BigIntegerField(default=0)
    commission_rial = models.BigIntegerField(default=0)
    commission_mg = models.BigIntegerField(default=0)

    payment_deadline = models.DateTimeField(null=True, blank=True)
    payment_gateway = models.CharField(max_length=20, blank=True)
    payment_ref = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    vendor = models.ForeignKey(
        "marketplace.Vendor", on_delete=models.PROTECT, null=True, blank=True, related_name="orders"
    )
    invoice_pdf = models.FileField(upload_to="invoices/", null=True, blank=True)

    # Roadmap seam — every new feature can stash data here without migrations
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["state", "payment_deadline"]),
            models.Index(fields=["vendor", "-created_at"]),
            models.Index(fields=["tenant_id", "kind", "-created_at"]),
        ]
        verbose_name = _("Order")

    def __str__(self) -> str:
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "marketplace.Product", on_delete=models.PROTECT, null=True, blank=True
    )
    title_snapshot = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_rial = models.BigIntegerField()
    line_total_rial = models.BigIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
