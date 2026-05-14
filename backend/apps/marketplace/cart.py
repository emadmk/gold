"""
Persistent server-side cart.

The cart is the lived experience of a buyer between "I want this" and
"I've paid". It stores items with their **locked price** for 6 minutes
(`PRICE_LOCK_SECONDS`). If the live price moves while the user is in
the cart, the API emits a `price.changed` flag and the UI shows a
banner — but the existing items keep their locked price until the
lock expires.
"""
from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

PRICE_LOCK_SECONDS = 6 * 60  # 6 minutes per mohem.docx §7


class Cart(models.Model):
    """One open cart per (user, tenant_id)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    discount_code = models.ForeignKey(
        "DiscountCode", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="active_carts",
    )
    shipping_address = models.ForeignKey(
        "ShippingAddress", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="carts",
    )
    shipping_method = models.CharField(
        max_length=40, blank=True,
        help_text='e.g. "post-pishtaz" / "tipax" / "snapp-box"',
    )
    payment_method = models.CharField(
        max_length=20, blank=True,
        help_text='"online" / "snappay" / "gsmpay"',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "Product", on_delete=models.PROTECT, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    locked_unit_price_rial = models.BigIntegerField()
    locked_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = (("cart", "product"),)
        indexes = [models.Index(fields=["cart", "-locked_at"])]

    @property
    def lock_expired(self) -> bool:
        return (timezone.now() - self.locked_at) > timedelta(seconds=PRICE_LOCK_SECONDS)


class DiscountCode(models.Model):
    KINDS = [
        ("percent", _("درصدی")),
        ("flat", _("مبلغ ثابت (ریال)")),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=40, unique=True, db_index=True)
    kind = models.CharField(max_length=10, choices=KINDS)
    value = models.DecimalField(
        max_digits=12, decimal_places=4,
        help_text="0.10 for percent; 100000 for flat rial.",
    )
    max_uses = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    uses = models.PositiveIntegerField(default=0)
    min_order_rial = models.BigIntegerField(default=0)
    max_discount_rial = models.BigIntegerField(default=0, help_text="0 = no cap")
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.code

    def is_currently_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.max_uses and self.uses >= self.max_uses:
            return False
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True

    def amount_off(self, order_rial: int) -> int:
        if order_rial < self.min_order_rial:
            return 0
        if self.kind == "flat":
            off = int(self.value)
        else:
            off = int(Decimal(order_rial) * Decimal(self.value))
        if self.max_discount_rial and off > self.max_discount_rial:
            off = self.max_discount_rial
        return min(off, order_rial)


class ShippingAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="shipping_addresses",
    )
    title = models.CharField(max_length=80, help_text="e.g. خانه / محل کار")
    recipient_name = models.CharField(max_length=120)
    recipient_phone = models.CharField(max_length=15)
    recipient_national_id = models.CharField(max_length=10, blank=True)
    province = models.CharField(max_length=60)
    city = models.CharField(max_length=80)
    address = models.TextField()
    postal_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "-updated_at"])]

    def __str__(self) -> str:
        return f"{self.title} — {self.city}"
