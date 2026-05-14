"""
Concurrency tests for the wallet ledger.

These use Python threads with retries to tolerate SQLite's exclusive
file-level lock. Under Postgres (production) the row-level lock makes
true concurrency possible; under SQLite we still get serialised access
through retries — which is enough to verify that the invariants hold.
"""
from __future__ import annotations

import threading
import time

import pytest
from django.db import OperationalError, connections
from django.db.models import Sum

from apps.wallet.models import WalletTransaction
from apps.wallet.services import (
    InsufficientFunds,
    credit_rial,
    debit_rial,
    ensure_wallets,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def funded_user(django_user_model):
    u = django_user_model.objects.create(phone="09120009999")
    ensure_wallets(u)
    credit_rial(u, 1_000_000, kind="deposit")
    return u


def _retry_op_error(fn, *, retries: int = 30, base_delay: float = 0.05):
    """Treat SQLite 'table is locked' as transient — keep retrying."""
    last: Exception | None = None
    for i in range(retries):
        try:
            return fn()
        except OperationalError as exc:
            last = exc
            time.sleep(base_delay * (1.3**i))
    if last:
        raise last


def _run_parallel(targets, *, workers):
    threads = [threading.Thread(target=t) for t in targets[:workers]]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for conn in connections.all():
        conn.close()


def test_two_concurrent_debits_no_double_spend(funded_user):
    """Two threads each debit half — both succeed, balance ends at 0."""
    results: list[bool] = []
    lock = threading.Lock()

    def worker():
        try:
            _retry_op_error(lambda: debit_rial(funded_user, 500_000, kind="withdraw"))
            with lock:
                results.append(True)
        except InsufficientFunds:
            with lock:
                results.append(False)

    _run_parallel([worker, worker], workers=2)
    funded_user.refresh_from_db()
    assert funded_user.rial_wallet.balance_rial == 0
    assert results.count(True) == 2


def test_overdraft_under_concurrency(funded_user):
    """Three threads each request 600k from a 1M balance — exactly one
    succeeds (after that, 400k < 600k)."""
    results: list[bool] = []
    lock = threading.Lock()

    def worker():
        try:
            _retry_op_error(lambda: debit_rial(funded_user, 600_000, kind="withdraw"))
            with lock:
                results.append(True)
        except InsufficientFunds:
            with lock:
                results.append(False)

    _run_parallel([worker, worker, worker], workers=3)
    funded_user.refresh_from_db()
    assert results.count(True) == 1
    assert funded_user.rial_wallet.balance_rial == 400_000


def test_transactions_sum_matches_balance_after_concurrency(funded_user):
    """Ledger invariant #6 must hold after concurrent writes."""
    errors: list[Exception] = []
    lock = threading.Lock()

    def credit_w():
        try:
            _retry_op_error(lambda: credit_rial(funded_user, 10_000, kind="deposit"))
        except Exception as exc:  # noqa: BLE001
            with lock:
                errors.append(exc)

    def debit_w():
        try:
            _retry_op_error(lambda: debit_rial(funded_user, 5_000, kind="withdraw"))
        except InsufficientFunds:
            pass

    workers = [credit_w] * 5 + [debit_w] * 5
    _run_parallel(workers, workers=10)
    assert not errors, errors

    funded_user.refresh_from_db()
    agg = WalletTransaction.objects.filter(user=funded_user, asset="rial").aggregate(
        s=Sum("rial_amount")
    )["s"]
    assert agg == funded_user.rial_wallet.balance_rial
