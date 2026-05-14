"""End-to-end smoke test: register → KYC → topup → buy → sell → transfer."""
from __future__ import annotations

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    u = django_user_model.objects.create(
        phone="09123456789", is_phone_verified=True, is_verified=True,
    )
    from apps.wallet.services import ensure_wallets
    ensure_wallets(u)
    return u


@pytest.fixture
def other_user(django_user_model):
    u = django_user_model.objects.create(
        phone="09127654321", is_phone_verified=True, is_verified=True,
    )
    from apps.wallet.services import ensure_wallets
    ensure_wallets(u)
    return u


@pytest.fixture
def price_tick():
    from apps.pricing.models import PriceTick
    return PriceTick.objects.create(
        source_key="gold_18k_750", rial_price=17_000_000, captured_at=timezone.now(),
    )


def test_topup_buy_gold_sell_gold(user, price_tick):
    """Whole money cycle, all in-wallet (no gateway)."""
    from apps.wallet.services import credit_rial
    from apps.pricing.services import issue_quote
    from apps.orders.services import submit_buy_gold, submit_sell_gold

    # Pretend we just got a gateway-confirmed deposit
    credit_rial(user, 100_000_000, kind="deposit")
    user.refresh_from_db()
    assert user.rial_wallet.balance_rial == 100_000_000

    # Buy 1 gram (1000 mg)
    quote_buy = issue_quote(user=user, asset="gold", side="buy")
    order_buy = submit_buy_gold(user=user, quote=quote_buy, mg_amount=1000)
    assert order_buy.state == "completed"
    user.refresh_from_db()
    assert user.gold_wallet.balance_mg == 1000
    assert user.rial_wallet.balance_rial < 100_000_000

    # Sell 500 mg back
    quote_sell = issue_quote(user=user, asset="gold", side="sell")
    order_sell = submit_sell_gold(user=user, quote=quote_sell, mg_amount=500)
    assert order_sell.state == "completed"
    user.refresh_from_db()
    assert user.gold_wallet.balance_mg == 500


def test_transfer_gold(user, other_user, price_tick, monkeypatch):
    """Internal P2P transfer with mocked OTP."""
    from apps.pricing.services import issue_quote
    from apps.orders.services import submit_buy_gold
    from apps.wallet.services import credit_rial
    from apps.wallet.transfer import transfer
    from apps.accounts.services import otp as otp_svc

    credit_rial(user, 100_000_000, kind="deposit")
    quote = issue_quote(user=user, asset="gold", side="buy")
    submit_buy_gold(user=user, quote=quote, mg_amount=2000)

    # Force OTP to verify
    monkeypatch.setattr(otp_svc, "verify_otp", lambda *a, **k: True)

    other_user.refresh_from_db()
    target_addr = other_user.gold_wallet.address

    transfer(sender=user, recipient_address=target_addr,
             asset="gold", mg=300, otp_code="123456")

    user.refresh_from_db()
    other_user.refresh_from_db()
    assert user.gold_wallet.balance_mg == 1700
    assert other_user.gold_wallet.balance_mg == 300


def test_order_expiry(user, price_tick):
    """An order whose payment_deadline has passed transitions to 'expired'."""
    from datetime import timedelta
    from apps.orders.models import Order
    from apps.orders.tasks import expire_due

    o = Order.objects.create(
        user=user, kind="buy_gold", state="awaiting_payment",
        price_per_mg_rial=17_000, mg_amount=1000, rial_amount=17_000_000,
        payment_deadline=timezone.now() - timedelta(minutes=1),
    )
    n = expire_due()
    assert n >= 1
    o.refresh_from_db()
    assert o.state == "expired"


def test_idempotent_payment_callback(user, price_tick):
    """Re-running the callback for the same authority short-circuits."""
    from apps.orders.models import Order
    from apps.payments.models import PaymentAttempt
    from apps.payments.services import handle_callback
    from apps.audit.models import IdempotencyKey

    o = Order.objects.create(
        user=user, kind="wallet_topup", state="awaiting_payment",
        rial_amount=1_000_000,
    )
    attempt = PaymentAttempt.objects.create(
        order=o, gateway="zarinpal", amount_rial=1_000_000,
        authority="AUTH-TEST-XYZ", state="redirected",
    )
    # First call (will fail verify because we have no network, but it will
    # also create the idempotency row). We catch broadly because the
    # gateway HTTP call errors out in tests.
    try:
        handle_callback(gateway="zarinpal", authority="AUTH-TEST-XYZ")
    except Exception:  # noqa: BLE001
        pass
    assert IdempotencyKey.objects.filter(scope="payment.callback").exists()

    # Second call must NOT raise — idempotent
    attempt2 = handle_callback(gateway="zarinpal", authority="AUTH-TEST-XYZ")
    assert attempt2.id == attempt.id
