"""
Seed production-ready reference data.

What this command writes is ONLY reference data that is part of the
domain itself — not fake demo content. Specifically:

* the bootstrap super-admin (with a generated random password the first
  time, printed to stdout so the operator can save it)
* the pricing-formula coefficients (so the admin panel can edit them)
* the coin catalogue (Iran's standard sekke types with real weights)
* the live price snapshot fetched **from TGJU** — no hard-coded numbers.

There are **no** fake vendors, no fake products, no fake users. Real
vendors apply through `/vendor/apply`; real products are entered via the
vendor panel; KYC files are uploaded by real users.
"""
from __future__ import annotations

import asyncio
import os
import secrets
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.coins.models import CoinType
from apps.pricing.crawler import fetch_with_fallback
from apps.pricing.models import SOURCE_KEYS, PriceTick, PricingFormula
from apps.wallet.services import ensure_wallets


# Real coin catalogue (Iran national mint specifications).
COIN_CATALOGUE = [
    ("emami", "سکه امامی", 8133, 7320),       # 8.1333g, 22k → 7.32g pure gold
    ("bahar", "سکه بهار آزادی", 8133, 7320),
    ("half", "نیم سکه", 4067, 3660),
    ("quarter", "ربع سکه", 2034, 1830),
    ("gerami", "سکه گرمی", 1016, 915),
]


class Command(BaseCommand):
    help = (
        "Seed reference data only: super-admin, pricing formulas, coin "
        "catalogue, real live prices from TGJU. No mock data."
    )

    def add_arguments(self, parser) -> None:  # type: ignore[no-untyped-def]
        parser.add_argument(
            "--admin-phone",
            default=os.environ.get("BOOTSTRAP_ADMIN_PHONE", "09120000000"),
            help="phone for the bootstrap super-admin",
        )
        parser.add_argument(
            "--skip-prices",
            action="store_true",
            help="skip the live-price fetch (offline bootstrap)",
        )

    def handle(self, *_args: object, **options: object) -> None:
        self._seed_admin(options["admin_phone"])  # type: ignore[arg-type]
        self._seed_formulas()
        self._seed_coins()
        if not options["skip_prices"]:
            self._seed_prices()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    # ---- admin ----
    def _seed_admin(self, phone: str) -> None:
        admin, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True,
                "is_phone_verified": True,
            },
        )
        ensure_wallets(admin)
        if created or not admin.has_usable_password():
            password = secrets.token_urlsafe(16)
            admin.set_password(password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                f"Bootstrap super-admin created:\n"
                f"  phone:    {phone}\n"
                f"  password: {password}\n"
                f"Save this NOW — it will not be shown again."
            ))
        else:
            self.stdout.write(
                f"Super-admin {phone} already exists; password unchanged."
            )

    # ---- pricing formulas ----
    def _seed_formulas(self) -> None:
        for key, default in settings.DOMAIN_DEFAULTS.items():
            PricingFormula.objects.get_or_create(
                key=key,
                defaults={"value": Decimal(default), "description": f"default {key}"},
            )
        self.stdout.write(
            f"Pricing formulas: {PricingFormula.objects.count()} rows."
        )

    # ---- coin catalogue ----
    def _seed_coins(self) -> None:
        for code, title, weight_mg, gold_mg in COIN_CATALOGUE:
            CoinType.objects.get_or_create(
                code=code,
                defaults={"title_fa": title, "weight_mg": weight_mg, "gold_content_mg": gold_mg},
            )
        self.stdout.write(f"Coin catalogue: {CoinType.objects.count()} rows.")

    # ---- live prices ----
    def _seed_prices(self) -> None:
        """Fetch every source from TGJU (with brsapi fallback) and store ticks."""
        loop = asyncio.new_event_loop()
        try:
            inserted = 0
            for key in SOURCE_KEYS:
                try:
                    price, source = loop.run_until_complete(fetch_with_fallback(key))
                    PriceTick.objects.create(
                        source_key=key,
                        rial_price=int(price),
                        captured_at=timezone.now(),
                        source=source,
                    )
                    inserted += 1
                except Exception as exc:  # noqa: BLE001
                    self.stderr.write(self.style.WARNING(
                        f"  ! could not seed {key}: {exc!r}"
                    ))
            self.stdout.write(
                f"Live prices: {inserted}/{len(SOURCE_KEYS)} source(s) captured."
            )
        finally:
            loop.close()
