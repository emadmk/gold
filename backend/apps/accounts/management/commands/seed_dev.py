"""Seed local development data."""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.coins.models import CoinType
from apps.marketplace.models import Product, Vendor
from apps.pricing.models import PriceTick, PricingFormula
from apps.wallet.services import ensure_wallets


class Command(BaseCommand):
    help = "Seed local dev data (super-admin, formulas, a few vendors, products, ticks)."

    def handle(self, *_args: object, **_kwargs: object) -> None:
        admin, _ = User.objects.get_or_create(
            phone="09120000000",
            defaults={
                "is_staff": True, "is_superuser": True,
                "is_verified": True, "is_phone_verified": True,
                "first_name": "ادمین", "last_name": "کلید",
            },
        )
        if not admin.has_usable_password():
            admin.set_password("changeme-please")
            admin.save()
        ensure_wallets(admin)
        self.stdout.write(self.style.SUCCESS(f"admin: phone={admin.phone} password=changeme-please"))

        # Formulas — seed defaults from settings.DOMAIN_DEFAULTS
        for k, v in settings.DOMAIN_DEFAULTS.items():
            PricingFormula.objects.get_or_create(
                key=k, defaults={"value": Decimal(v), "description": f"default {k}"}
            )
        self.stdout.write(self.style.SUCCESS(f"formulas seeded: {len(settings.DOMAIN_DEFAULTS)}"))

        # Coins
        coins_data = [
            ("emami", "سکه امامی", 8133, 7320),
            ("bahar", "سکه بهار آزادی", 8133, 7320),
            ("half", "نیم سکه", 4067, 3660),
            ("quarter", "ربع سکه", 2034, 1830),
            ("gerami", "سکه گرمی", 1016, 915),
        ]
        for code, title, weight_mg, gold_mg in coins_data:
            CoinType.objects.get_or_create(
                code=code,
                defaults={"title_fa": title, "weight_mg": weight_mg, "gold_content_mg": gold_mg},
            )

        # Vendors
        for i in range(1, 4):
            v_user, _ = User.objects.get_or_create(
                phone=f"0912100000{i}",
                defaults={"is_phone_verified": True, "is_verified": True, "is_vendor": True},
            )
            ensure_wallets(v_user)
            Vendor.objects.get_or_create(
                user=v_user,
                defaults={
                    "shop_name": f"طلا فروشی نمونه {i}",
                    "shop_slug": f"sample-shop-{i}",
                    "legal_name": f"شرکت نمونه {i}",
                    "iban": f"IR{i:024d}",
                    "state": "approved",
                    "city": "تهران",
                },
            )

        # Products
        for v in Vendor.objects.filter(state="approved"):
            Product.objects.get_or_create(
                sku=f"ABS-{v.id.hex[:6]}",
                defaults={
                    "vendor": v,
                    "category": "melted",
                    "title": f"طلای آب‌شده ۱۸ — {v.shop_name}",
                    "slug": f"melted-{v.id.hex[:6]}",
                    "weight_mg": 5000,
                    "karat": 750,
                    "manufacturing_fee_pct": Decimal("0"),
                    "vendor_margin_pct": Decimal("0.01"),
                },
            )

        # A few ticks so /api/v1/prices returns data even before crawler runs
        for key, rial in [
            ("gold_18k_750", 17_241_600 * 100),
            ("silver_999", 396_000 * 100),
            ("coin_emami", 480_000_000 * 100),
            ("usd_free", 870_000 * 100),
        ]:
            PriceTick.objects.get_or_create(
                source_key=key, captured_at=timezone.now(),
                defaults={"rial_price": rial, "source": "seed"},
            )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
