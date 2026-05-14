"""
AML / fraud risk engine (v1: deterministic rules).

Roadmap #1 swaps the implementation for an ML endpoint — the
`score(...)` signature is intentionally minimal so consumers don't
break.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Literal

from django.conf import settings


@dataclass(frozen=True, slots=True)
class RiskDecision:
    score: int  # 0..100
    action: Literal["allow", "review", "block"]
    reasons: tuple[str, ...]


def score(event: dict[str, Any]) -> RiskDecision:
    reasons: list[str] = []
    s = 0

    amount = int(event.get("rial_amount") or 0)
    threshold = int(Decimal(settings.DOMAIN_DEFAULTS["aml_threshold_rial"]))
    if amount >= threshold:
        reasons.append("amount_over_threshold")
        s += 60
    if event.get("new_iban"):
        reasons.append("new_iban")
        s += 30
    if event.get("velocity_outlier"):
        reasons.append("velocity_outlier")
        s += 25
    if event.get("sanctions_hit"):
        reasons.append("sanctions_hit")
        s += 100

    if s >= 100:
        action: Literal["allow", "review", "block"] = "block"
    elif s >= 50:
        action = "review"
    else:
        action = "allow"
    return RiskDecision(score=min(100, s), action=action, reasons=tuple(reasons))
