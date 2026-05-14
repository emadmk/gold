"""
Wallet service layer.

All money mutations go through these functions. Each function:
  * runs inside transaction.atomic()
  * uses SELECT FOR UPDATE on the wallet row
  * appends a WalletTransaction
  * emits a structured event whose id is stored on the transaction
"""
from __future__ import annotations

from django.db import transaction

from apps.audit.emit import emit_event

from .models import GoldWallet, RialWallet, WalletTransaction


class InsufficientFunds(Exception):
    pass


@transaction.atomic
def credit_rial(user, amount: int, *, kind: str = "deposit", order=None, description: str = "") -> WalletTransaction:
    if amount <= 0:
        raise ValueError("amount must be > 0")
    wallet = RialWallet.objects.select_for_update().get(user=user)
    wallet.balance_rial += amount
    wallet.save(update_fields=["balance_rial", "updated_at"])
    event_id = emit_event(
        f"wallet.rial.{'deposit' if kind == 'deposit' else 'adjustment'}",
        actor={"type": "user", "id": str(user.id)},
        target={"type": "wallet", "id": str(wallet.id), "owner_id": str(user.id)},
        data={"rial_amount": amount, "balance_after": wallet.balance_rial, "reason": kind},
    )
    return WalletTransaction.objects.create(
        user=user, type=kind, asset="rial", rial_amount=amount,
        balance_after_rial=wallet.balance_rial, related_order=order,
        event_id=event_id, description=description,
    )


@transaction.atomic
def debit_rial(user, amount: int, *, kind: str = "withdraw", order=None, description: str = "") -> WalletTransaction:
    if amount <= 0:
        raise ValueError("amount must be > 0")
    wallet = RialWallet.objects.select_for_update().get(user=user)
    if wallet.available_rial < amount:
        raise InsufficientFunds("موجودی کافی نیست")
    wallet.balance_rial -= amount
    wallet.save(update_fields=["balance_rial", "updated_at"])
    event_id = emit_event(
        f"wallet.rial.{kind}",
        actor={"type": "user", "id": str(user.id)},
        target={"type": "wallet", "id": str(wallet.id), "owner_id": str(user.id)},
        data={"rial_amount": -amount, "balance_after": wallet.balance_rial, "reason": kind},
    )
    return WalletTransaction.objects.create(
        user=user, type=kind, asset="rial", rial_amount=-amount,
        balance_after_rial=wallet.balance_rial, related_order=order,
        event_id=event_id, description=description,
    )


@transaction.atomic
def lock_rial(user, amount: int) -> None:
    wallet = RialWallet.objects.select_for_update().get(user=user)
    if wallet.available_rial < amount:
        raise InsufficientFunds("موجودی قابل قفل کافی نیست")
    wallet.locked_rial += amount
    wallet.save(update_fields=["locked_rial", "updated_at"])
    emit_event(
        "wallet.rial.locked",
        actor={"type": "user", "id": str(user.id)},
        target={"type": "wallet", "id": str(wallet.id), "owner_id": str(user.id)},
        data={"rial_amount": amount, "locked_after": wallet.locked_rial},
    )


@transaction.atomic
def unlock_rial(user, amount: int) -> None:
    wallet = RialWallet.objects.select_for_update().get(user=user)
    wallet.locked_rial = max(0, wallet.locked_rial - amount)
    wallet.save(update_fields=["locked_rial", "updated_at"])
    emit_event(
        "wallet.rial.unlocked",
        actor={"type": "user", "id": str(user.id)},
        target={"type": "wallet", "id": str(wallet.id), "owner_id": str(user.id)},
        data={"rial_amount": amount, "locked_after": wallet.locked_rial},
    )


@transaction.atomic
def credit_asset(user, asset: str, mg: int, *, kind: str, order=None, description: str = "") -> WalletTransaction:
    if mg <= 0:
        raise ValueError("mg must be > 0")
    wallet = GoldWallet.objects.select_for_update().get(user=user)
    if asset == "gold":
        wallet.balance_mg += mg
    elif asset == "silver":
        wallet.silver_balance_mg += mg
    else:
        raise ValueError(f"unknown asset: {asset}")
    wallet.save(update_fields=["balance_mg", "silver_balance_mg", "updated_at"])
    event_id = emit_event(
        f"wallet.{asset}.{kind.split('_')[0]}",  # e.g. wallet.gold.buy
        actor={"type": "user", "id": str(user.id)},
        target={"type": "wallet", "id": str(wallet.id), "owner_id": str(user.id)},
        data={"asset": asset, "mg_amount": mg, "reason": kind},
    )
    balance_after = wallet.balance_mg if asset == "gold" else wallet.silver_balance_mg
    return WalletTransaction.objects.create(
        user=user, type=kind, asset=asset, mg_amount=mg,
        balance_after_mg=balance_after, related_order=order,
        event_id=event_id, description=description,
    )


@transaction.atomic
def debit_asset(user, asset: str, mg: int, *, kind: str, order=None, description: str = "") -> WalletTransaction:
    if mg <= 0:
        raise ValueError("mg must be > 0")
    wallet = GoldWallet.objects.select_for_update().get(user=user)
    if asset == "gold":
        if wallet.available_gold_mg < mg:
            raise InsufficientFunds("موجودی طلای کافی نیست")
        wallet.balance_mg -= mg
    elif asset == "silver":
        if wallet.available_silver_mg < mg:
            raise InsufficientFunds("موجودی نقره‌ی کافی نیست")
        wallet.silver_balance_mg -= mg
    else:
        raise ValueError(f"unknown asset: {asset}")
    wallet.save(update_fields=["balance_mg", "silver_balance_mg", "updated_at"])
    event_id = emit_event(
        f"wallet.{asset}.{kind.split('_')[0]}",
        actor={"type": "user", "id": str(user.id)},
        target={"type": "wallet", "id": str(wallet.id), "owner_id": str(user.id)},
        data={"asset": asset, "mg_amount": -mg, "reason": kind},
    )
    balance_after = wallet.balance_mg if asset == "gold" else wallet.silver_balance_mg
    return WalletTransaction.objects.create(
        user=user, type=kind, asset=asset, mg_amount=-mg,
        balance_after_mg=balance_after, related_order=order,
        event_id=event_id, description=description,
    )


def ensure_wallets(user) -> tuple[RialWallet, GoldWallet]:
    rw, _ = RialWallet.objects.get_or_create(user=user)
    gw, _ = GoldWallet.objects.get_or_create(user=user)
    return rw, gw
