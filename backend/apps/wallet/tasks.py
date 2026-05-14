"""Wallet-side Celery tasks: daily yield + ledger consistency."""
from __future__ import annotations

from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.db.models import Sum

from apps.audit.emit import emit_event

from .models import GoldWallet, RialWallet, WalletTransaction
from .services import credit_rial


@shared_task(name="wallet.daily_yield")
def daily_yield_payout() -> int:
    """Pay APR/365 of available rial balance to every verified user."""
    apr = Decimal(settings.DOMAIN_DEFAULTS.get("daily_yield_apr", "0"))
    if apr <= 0:
        return 0
    daily_rate = apr / Decimal(365)
    paid = 0
    for w in RialWallet.objects.filter(user__is_verified=True).select_related("user"):
        # Reward only the available balance, not the locked portion
        base = max(0, w.balance_rial - w.locked_rial)
        if base < 10_000:  # below 1k toman: skip
            continue
        bonus = int((Decimal(base) * daily_rate).to_integral_value())
        if bonus <= 0:
            continue
        try:
            credit_rial(w.user, bonus, kind="yield_payout",
                        description="پاداش وفاداری روزانه")
            emit_event(
                "wallet.yield.payout",
                actor={"type": "system", "id": "scheduler"},
                target={"type": "user", "id": str(w.user_id)},
                data={"base_rial": base, "bonus_rial": bonus,
                      "rate": str(daily_rate)},
            )
            paid += 1
        except Exception as exc:  # noqa: BLE001
            emit_event("system.celery.task.failed", severity="error",
                       data={"task": "wallet.daily_yield",
                             "user_id": str(w.user_id), "error": repr(exc)})
    return paid


@shared_task(name="wallet.consistency_tick")
def consistency_tick() -> dict[str, int]:
    """Verify SECURITY.md §8 invariants. Emits audit.consistency.violation
    when a wallet drifts from the sum of its transactions."""
    drifted = 0
    checked = 0
    for w in RialWallet.objects.select_related("user").iterator():
        checked += 1
        agg = WalletTransaction.objects.filter(user=w.user, asset="rial").aggregate(
            s=Sum("rial_amount"))["s"] or 0
        if agg != w.balance_rial:
            drifted += 1
            emit_event(
                "audit.consistency.violation",
                severity="critical",
                outcome="failure",
                target={"type": "wallet", "id": str(w.id), "owner_id": str(w.user_id)},
                data={"asset": "rial", "expected": agg, "actual": w.balance_rial},
            )
    for w in GoldWallet.objects.select_related("user").iterator():
        checked += 1
        for asset, field in (("gold", "balance_mg"), ("silver", "silver_balance_mg")):
            agg = WalletTransaction.objects.filter(user=w.user, asset=asset).aggregate(
                s=Sum("mg_amount"))["s"] or 0
            actual = getattr(w, field)
            if agg != actual:
                drifted += 1
                emit_event(
                    "audit.consistency.violation",
                    severity="critical", outcome="failure",
                    target={"type": "wallet", "id": str(w.id), "owner_id": str(w.user_id)},
                    data={"asset": asset, "expected": agg, "actual": actual},
                )
    return {"checked": checked, "drifted": drifted}
