"""Pricing formulas — pluggable via the `register` decorator (strategy registry)."""
from __future__ import annotations

from decimal import Decimal
from functools import lru_cache
from typing import Callable

from django.conf import settings

from .models import PricingFormula


_strategies: dict[str, Callable] = {}


def register(name: str) -> Callable[[Callable], Callable]:
    def deco(fn: Callable) -> Callable:
        _strategies[name] = fn
        return fn
    return deco


def get_strategy(name: str) -> Callable:
    if name in _strategies:
        return _strategies[name]
    raise KeyError(f"unknown pricing strategy: {name}")


def coefficient(key: str) -> Decimal:
    """Read a coefficient — DB row > settings default."""
    try:
        f = PricingFormula.objects.get(key=key)
        return Decimal(f.value)
    except PricingFormula.DoesNotExist:
        return Decimal(settings.DOMAIN_DEFAULTS[key])


@register("gold_buy")
def gold_buy_per_mg(base_18k_rial_per_g: int) -> int:
    spread = coefficient("buy_spread")
    commission = coefficient("commission_buy")
    per_mg = Decimal(base_18k_rial_per_g) / Decimal(1000)
    return int((per_mg * (Decimal(1) + spread) * (Decimal(1) + commission)).to_integral_value())


@register("gold_sell")
def gold_sell_per_mg(base_18k_rial_per_g: int) -> int:
    spread = coefficient("sell_spread")
    commission = coefficient("commission_sell")
    per_mg = Decimal(base_18k_rial_per_g) / Decimal(1000)
    return int((per_mg * (Decimal(1) - spread) * (Decimal(1) - commission)).to_integral_value())


@register("silver_buy")
def silver_buy_per_mg(base_999_rial_per_g: int) -> int:
    spread = coefficient("silver_buy_spread")
    commission = coefficient("silver_commission")
    per_mg = Decimal(base_999_rial_per_g) / Decimal(1000)
    return int((per_mg * (Decimal(1) + spread) * (Decimal(1) + commission)).to_integral_value())


@register("silver_sell")
def silver_sell_per_mg(base_999_rial_per_g: int) -> int:
    spread = coefficient("silver_sell_spread")
    commission = coefficient("silver_commission")
    per_mg = Decimal(base_999_rial_per_g) / Decimal(1000)
    return int((per_mg * (Decimal(1) - spread) * (Decimal(1) - commission)).to_integral_value())


@lru_cache(maxsize=1)
def list_strategies() -> tuple[str, ...]:
    return tuple(sorted(_strategies.keys()))
