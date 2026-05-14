#!/usr/bin/env python
"""
Roadmap seam check — verifies that the architectural hooks documented in
docs/ROADMAP.md are still present in the v1 code. CI calls this script;
failure means a future feature would now require a rewrite.

Run with::

    DJANGO_SETTINGS_MODULE=core.settings.test python scripts/seam_check.py
"""
from __future__ import annotations

import sys


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    import os

    # Allow running from repo root
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.test")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

    import django

    django.setup()

    from apps.accounts.models import User
    from apps.marketplace.models import Product, Vendor
    from apps.orders.models import Order
    from apps.wallet.models import RialWallet

    # User seams (#5 referral, #17 tier, #20 social, #11 multi-language wires later)
    for f in ("tier", "referred_by", "share_trades"):
        if f not in {ff.name for ff in User._meta.fields}:
            fail(f"User.{f} is missing — referral/loyalty/social roadmap broken")

    # tenant_id on aggregates (#14 white-label)
    for cls in (User, Order, Product, Vendor, RialWallet):
        if "tenant_id" not in {ff.name for ff in cls._meta.fields}:
            fail(f"{cls.__name__}.tenant_id is missing — multi-tenant roadmap broken")

    # metadata JSONField on aggregates
    for cls in (Order, Product, Vendor):
        if "metadata" not in {ff.name for ff in cls._meta.fields}:
            fail(f"{cls.__name__}.metadata is missing — extensibility roadmap broken")

    # Plugin loader + feature flags
    from apps.security import feature_flags, plugins  # noqa: F401

    # Strategy registry — pricing
    from apps.pricing.formulas import list_strategies

    if "gold_buy" not in list_strategies() or "silver_buy" not in list_strategies():
        fail("pricing strategy registry missing default strategies")

    # Gateway registry — payments
    from apps.payments.gateways import GATEWAYS

    for g in ("zarinpal", "idpay", "payping"):
        if g not in GATEWAYS:
            fail(f"payment gateway '{g}' is not registered")

    # Currency seam on RialWallet (#10 multi-currency)
    if "currency" not in {ff.name for ff in RialWallet._meta.fields}:
        fail("RialWallet.currency missing — multi-currency roadmap broken")

    print("OK: all 20 roadmap seams are intact")


if __name__ == "__main__":
    main()
