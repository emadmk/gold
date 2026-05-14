"""Unit conversions and constants."""
from __future__ import annotations

WEIGHT_UNIT = "milligram"  # 1 g = 1000 mg
MONEY_UNIT = "rial"        # 1 toman = 10 rial

GRAM_MG = 1000


def mg_to_g(mg: int) -> float:
    return mg / GRAM_MG


def g_to_mg(g: float) -> int:
    return int(round(g * GRAM_MG))


def rial_to_toman(rial: int) -> int:
    return rial // 10


def toman_to_rial(toman: int) -> int:
    return toman * 10


def equivalent_18k_mg(weight_g: float, karat: int) -> int:
    """Pure-gold equivalence: weight in 18k equivalent milligrams."""
    return int(round((weight_g * karat) / 750.0 * GRAM_MG))
