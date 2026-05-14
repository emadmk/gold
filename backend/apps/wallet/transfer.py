"""Internal P2P transfer (gold/silver) — atomic + audited + OTP-gated."""
from __future__ import annotations

from django.db import transaction

from apps.audit.emit import emit_event

from .models import GoldWallet, WalletTransaction
from .services import InsufficientFunds


@transaction.atomic
def transfer(*, sender, recipient_address: str, asset: str, mg: int, otp_code: str) -> tuple[WalletTransaction, WalletTransaction]:
    """Move `mg` of `asset` (gold or silver) from sender to the wallet at
    `recipient_address`. Both wallets are SELECT FOR UPDATE; both
    transactions are written; matching IN / OUT events are emitted with
    a shared causation_id."""
    from apps.accounts.services import otp as otp_svc

    if asset not in ("gold", "silver"):
        raise ValueError("asset must be 'gold' or 'silver'")
    if mg <= 0:
        raise ValueError("mg must be > 0")
    if not otp_svc.verify_otp(sender.phone, otp_code, purpose="transfer"):
        raise PermissionError("کد یکبارمصرف معتبر نیست.")

    sender_w = GoldWallet.objects.select_for_update().get(user=sender)
    try:
        recipient_w = GoldWallet.objects.select_for_update().get(address=recipient_address)
    except GoldWallet.DoesNotExist as exc:
        raise ValueError("آدرس مقصد یافت نشد.") from exc
    if recipient_w.user_id == sender.id:
        raise ValueError("ارسال به آدرس خودتان مجاز نیست.")

    field = "balance_mg" if asset == "gold" else "silver_balance_mg"
    sender_balance = getattr(sender_w, field)
    if asset == "gold":
        locked = sender_w.locked_mg
        available = sender_balance - locked
    else:
        locked = sender_w.silver_locked_mg
        available = sender_balance - locked
    if available < mg:
        raise InsufficientFunds("موجودی قابل ارسال کافی نیست.")

    setattr(sender_w, field, sender_balance - mg)
    setattr(recipient_w, field, getattr(recipient_w, field) + mg)
    sender_w.save(update_fields=[field, "updated_at"])
    recipient_w.save(update_fields=[field, "updated_at"])

    causation = emit_event(
        f"wallet.transfer.out",
        actor={"type": "user", "id": str(sender.id)},
        target={"type": "wallet", "id": str(sender_w.id), "owner_id": str(sender.id)},
        data={"asset": asset, "mg_amount": -mg, "to_address": recipient_address},
    )
    emit_event(
        f"wallet.transfer.in",
        actor={"type": "user", "id": str(recipient_w.user_id)},
        target={"type": "wallet", "id": str(recipient_w.id), "owner_id": str(recipient_w.user_id)},
        data={"asset": asset, "mg_amount": mg, "from_user": str(sender.id)},
        causation_id=causation,
    )
    out = WalletTransaction.objects.create(
        user=sender, type="transfer_out", asset=asset, mg_amount=-mg,
        balance_after_mg=getattr(sender_w, field), event_id=causation,
        description=f"انتقال {asset} به {recipient_address}",
    )
    inc = WalletTransaction.objects.create(
        user=recipient_w.user, type="transfer_in", asset=asset, mg_amount=mg,
        balance_after_mg=getattr(recipient_w, field),
        description=f"دریافت {asset} از کیف {sender.phone}",
    )
    return out, inc
