"""Wallet invariants — balance never negative, locked ≤ balance, etc."""
from __future__ import annotations

import pytest

from apps.wallet.services import (
    InsufficientFunds,
    credit_rial,
    debit_asset,
    debit_rial,
    ensure_wallets,
    lock_rial,
    unlock_rial,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    u = django_user_model.objects.create(phone="09120001234")
    ensure_wallets(u)
    return u


def test_debit_below_zero_blocked(user):
    with pytest.raises(InsufficientFunds):
        debit_rial(user, 1, kind="withdraw")


def test_overdraft_lock_blocked(user):
    credit_rial(user, 100, kind="deposit")
    with pytest.raises(InsufficientFunds):
        lock_rial(user, 101)


def test_unlock_never_negative(user):
    credit_rial(user, 100, kind="deposit")
    lock_rial(user, 50)
    unlock_rial(user, 1000)  # excessive — should just floor to 0
    user.refresh_from_db()
    assert user.rial_wallet.locked_rial == 0


def test_gold_debit_below_zero_blocked(user):
    with pytest.raises(InsufficientFunds):
        debit_asset(user, "gold", 1, kind="adjustment")


def test_sum_of_transactions_matches_balance(user):
    """SECURITY.md §8 invariant #6, run as a unit test."""
    from django.db.models import Sum

    from apps.wallet.models import WalletTransaction

    credit_rial(user, 1_000, kind="deposit")
    credit_rial(user, 2_500, kind="deposit")
    debit_rial(user, 1_000, kind="withdraw")
    user.refresh_from_db()

    agg = WalletTransaction.objects.filter(user=user, asset="rial").aggregate(
        s=Sum("rial_amount")
    )["s"]
    assert agg == user.rial_wallet.balance_rial == 2_500
