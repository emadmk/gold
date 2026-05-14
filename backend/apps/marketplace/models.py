"""Vendor + Product."""
from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Vendor(models.Model):
    STATES = [
        ("applied", _("در انتظار")),
        ("approved", _("تأیید شد")),
        ("suspended", _("تعلیق")),
        ("rejected", _("رد شد")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor_profile"
    )
    shop_name = models.CharField(max_length=120)
    shop_slug = models.SlugField(unique=True)
    legal_name = models.CharField(max_length=200)
    business_license = models.FileField(upload_to="vendor/licenses/", blank=True, null=True)
    union_license = models.FileField(upload_to="vendor/licenses/", blank=True, null=True)
    iban = models.CharField(max_length=255, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.02"))
    state = models.CharField(max_length=20, choices=STATES, default="applied")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_sales = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="vendor/logos/", blank=True, null=True)
    city = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.shop_name


class Product(models.Model):
    CATEGORIES = [
        ("melted", _("طلای آب‌شده")),
        ("jewelry", _("طلای ساخته‌شده")),
        ("coin", _("سکه")),
        ("silver", _("نقره")),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=40, default="default", db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="products")
    category = models.CharField(max_length=10, choices=CATEGORIES)
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    sku = models.CharField(max_length=40, unique=True)
    weight_mg = models.BigIntegerField()
    karat = models.PositiveSmallIntegerField(default=750)
    manufacturing_fee_pct = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    vendor_margin_pct = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    fixed_extra_rial = models.BigIntegerField(default=0)
    coin_type = models.CharField(max_length=20, blank=True)
    image_urls = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["vendor", "category", "-created_at"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.sku} — {self.title}"
