"""
Seed reference data — everything the platform needs to function out of
the box without containing any mock / demo content.

What this command writes:

* the bootstrap super-admin (with a generated random password the first
  time, printed to stdout so the operator can save it),
* the pricing-formula coefficients (so the admin panel can edit them),
* the coin catalogue (Iran's standard sekke types with real weights),
* the jewelry-category taxonomy (rings / necklaces / …),
* the blog-category taxonomy (news / education / market analysis / …),
* the Celery-beat periodic-task rows for production-grade scheduling,
* the live price snapshot fetched **from TGJU** — no hard-coded numbers.

There are NO fake vendors, NO fake products, NO fake users. Real
vendors apply through `/vendor/apply`; real products are entered via
the vendor panel; KYC files are uploaded by real users.
"""
from __future__ import annotations

import asyncio
import json
import os
import secrets
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.blog.models import Category as BlogCategory
from apps.coins.models import CoinType
from apps.jewelry.models import JewelryCategory
from apps.pricing.crawler import fetch_with_fallback
from apps.pricing.models import SOURCE_KEYS, PriceTick, PricingFormula
from apps.wallet.services import ensure_wallets


# Real coin catalogue (Iran national mint specifications).
# (code, title_fa, total_weight_mg, pure_gold_content_mg)
COIN_CATALOGUE = [
    ("emami", "سکه امامی", 8133, 7320),
    ("bahar", "سکه بهار آزادی", 8133, 7320),
    ("half", "نیم سکه", 4067, 3660),
    ("quarter", "ربع سکه", 2034, 1830),
    ("gerami", "سکه گرمی", 1016, 915),
]

# Standard jewelry taxonomy (Persian retail conventions).
# (code, title_fa, sort)
JEWELRY_CATEGORIES = [
    ("ring", "انگشتر", 10),
    ("necklace", "گردنبند", 20),
    ("bracelet", "دستبند", 30),
    ("bangle", "النگو", 40),
    ("earring", "گوشواره", 50),
    ("set", "سرویس / نیم‌ست", 60),
    ("pendant", "آویز", 70),
    ("anklet", "پابند", 80),
    ("watch", "ساعت", 90),
]

# Blog categories.
BLOG_CATEGORIES = [
    ("news", "اخبار بازار", 10),
    ("education", "آموزش و راهنما", 20),
    ("analysis", "تحلیل قیمت", 30),
    ("faq", "پرسش‌های پرتکرار", 40),
    ("announcement", "اعلانات سامانه", 50),
]

# Celery-beat periodic-task rows. The schedule itself also lives in
# core/celery.py::app.conf.beat_schedule — this seeds the DatabaseScheduler
# rows for environments that use django-celery-beat.
BEAT_TASKS = [
    {"name": "pricing-crawl-every-30s", "task": "pricing.crawl_all", "every": 30},
    {"name": "orders-expire-due-every-60s", "task": "orders.expire_due", "every": 60},
    {"name": "wallet-consistency-every-5m", "task": "wallet.consistency_tick", "every": 300},
    {"name": "audit-reconcile-every-1h", "task": "audit.reconcile", "every": 3600},
    {"name": "security-aml-every-10m", "task": "security.aml_tick", "every": 600},
    {"name": "marketplace-settle-daily-0100", "task": "marketplace.settle_vendors",
     "crontab": {"hour": "1", "minute": "0"}},
    {"name": "wallet-daily-yield-0005", "task": "wallet.daily_yield",
     "crontab": {"hour": "0", "minute": "5"}},
]


class Command(BaseCommand):
    help = (
        "Seed reference data only: super-admin, pricing formulas, coin "
        "catalogue, jewelry categories, blog categories, periodic tasks, "
        "live prices from TGJU. NO mock data is created."
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
        parser.add_argument(
            "--skip-beat",
            action="store_true",
            help="skip django-celery-beat schedule seeding",
        )

    def handle(self, *_args: object, **options: object) -> None:
        self._seed_admin(options["admin_phone"])  # type: ignore[arg-type]
        self._seed_formulas()
        self._seed_coins()
        self._seed_jewelry_categories()
        self._seed_blog_categories()
        if not options["skip_beat"]:
            self._seed_beat_schedule()
        if not options["skip_prices"]:
            self._seed_prices()
        self.stdout.write(self.style.SUCCESS("\nSeed complete."))

    # ---------------------------------------------------------------- admin
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
                f"\n┌─ Bootstrap super-admin created ─\n"
                f"│  phone:    {phone}\n"
                f"│  password: {password}\n"
                f"└─ Save this NOW — it will not be shown again.\n"
            ))
        else:
            self.stdout.write(
                f"Super-admin {phone} already exists; password unchanged."
            )

    # -------------------------------------------------------------- formulas
    def _seed_formulas(self) -> None:
        for key, default in settings.DOMAIN_DEFAULTS.items():
            PricingFormula.objects.get_or_create(
                key=key,
                defaults={"value": Decimal(default),
                          "description": f"default {key}"},
            )
        self.stdout.write(
            f"Pricing formulas: {PricingFormula.objects.count()} rows."
        )

    # ------------------------------------------------------------------ coins
    def _seed_coins(self) -> None:
        for code, title, weight_mg, gold_mg in COIN_CATALOGUE:
            CoinType.objects.update_or_create(
                code=code,
                defaults={"title_fa": title, "weight_mg": weight_mg,
                          "gold_content_mg": gold_mg},
            )
        self.stdout.write(f"Coin catalogue: {CoinType.objects.count()} rows.")

    # ---------------------------------------------------- jewelry categories
    def _seed_jewelry_categories(self) -> None:
        for code, title, sort in JEWELRY_CATEGORIES:
            JewelryCategory.objects.update_or_create(
                code=code, defaults={"title_fa": title, "sort": sort},
            )
        self.stdout.write(
            f"Jewelry categories: {JewelryCategory.objects.count()} rows."
        )

    # ------------------------------------------------------- blog categories
    def _seed_blog_categories(self) -> None:
        for code, title, sort in BLOG_CATEGORIES:
            BlogCategory.objects.update_or_create(
                code=code, defaults={"title_fa": title, "sort": sort},
            )
        self.stdout.write(
            f"Blog categories: {BlogCategory.objects.count()} rows."
        )

    # ----------------------------------------------------- celery-beat tasks
    def _seed_beat_schedule(self) -> None:
        """Create django-celery-beat rows so the beat DatabaseScheduler picks
        the canonical schedule up immediately. Existing rows are not
        overwritten (the admin can tune intervals from the UI)."""
        try:
            from django_celery_beat.models import (
                CrontabSchedule,
                IntervalSchedule,
                PeriodicTask,
            )
        except Exception:  # noqa: BLE001
            return
        created = 0
        for spec in BEAT_TASKS:
            kwargs: dict[str, object] = {"name": spec["name"], "task": spec["task"]}
            if "every" in spec:
                sched, _ = IntervalSchedule.objects.get_or_create(
                    every=spec["every"], period=IntervalSchedule.SECONDS,
                )
                kwargs["interval"] = sched
            else:
                c = spec["crontab"]
                sched, _ = CrontabSchedule.objects.get_or_create(
                    minute=c["minute"], hour=c["hour"],
                )
                kwargs["crontab"] = sched
            _, made = PeriodicTask.objects.get_or_create(
                name=spec["name"],
                defaults={**kwargs, "kwargs": json.dumps({}),
                          "enabled": True},
            )
            if made:
                created += 1
        self.stdout.write(
            f"Celery beat: {PeriodicTask.objects.count()} tasks "
            f"({created} new)."
        )

    # ------------------------------------------------------------- prices
    def _seed_prices(self) -> None:
        """Fetch every source from TGJU (brsapi fallback) and store ticks."""
        loop = asyncio.new_event_loop()
        try:
            inserted = 0
            for key in SOURCE_KEYS:
                try:
                    price, source = loop.run_until_complete(fetch_with_fallback(key))
                    PriceTick.objects.create(
                        source_key=key, rial_price=int(price),
                        captured_at=timezone.now(), source=source,
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
