"""Pricing formula snapshot tests."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def default_formulas(db):
    from decimal import Decimal
    from django.conf import settings
    from apps.pricing.models import PricingFormula

    for k, v in settings.DOMAIN_DEFAULTS.items():
        PricingFormula.objects.get_or_create(key=k, defaults={"value": Decimal(v)})


def test_gold_buy_higher_than_base():
    from apps.pricing.formulas import gold_buy_per_mg, gold_sell_per_mg

    base = 100_000_000  # 100M rial per gram (a round number)
    buy = gold_buy_per_mg(base)
    sell = gold_sell_per_mg(base)
    assert buy > base // 1000 > sell, (buy, sell, base // 1000)


def test_silver_buy_higher_than_base():
    from apps.pricing.formulas import silver_buy_per_mg, silver_sell_per_mg

    base = 4_000_000
    buy = silver_buy_per_mg(base)
    sell = silver_sell_per_mg(base)
    assert buy > base // 1000 > sell


def test_spread_changes_take_effect():
    from decimal import Decimal
    from apps.pricing.formulas import gold_buy_per_mg
    from apps.pricing.models import PricingFormula

    base = 100_000_000
    before = gold_buy_per_mg(base)
    PricingFormula.objects.filter(key="buy_spread").update(value=Decimal("0.05"))
    after = gold_buy_per_mg(base)
    assert after > before
