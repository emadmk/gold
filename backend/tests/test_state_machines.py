"""State machine — legal transitions, guards, side-effect events."""
from __future__ import annotations

import pytest

from apps.audit.state_machine import (
    IllegalTransition,
    delivery_sm,
    kyc_sm,
    order_sm,
    payment_attempt_sm,
    vendor_sm,
)


class _Stub:
    """A fake model instance with the minimum SM contract."""

    def __init__(self, state: str) -> None:
        self.state = state

    def save(self, **_):  # noqa: ANN001
        pass


def test_order_legal_path():
    o = _Stub("draft")
    order_sm.fire(o, "order.submitted")
    assert o.state == "awaiting_payment"
    order_sm.fire(o, "payment.verified")
    assert o.state == "paid"
    order_sm.fire(o, "order.process")
    assert o.state == "processing"
    order_sm.fire(o, "order.settle")
    assert o.state == "completed"


def test_order_illegal_transition():
    o = _Stub("draft")
    with pytest.raises(IllegalTransition):
        order_sm.fire(o, "payment.verified")


def test_kyc_lifecycle():
    s = _Stub("empty")
    kyc_sm.fire(s, "kyc.submit")
    assert s.state == "submitted"
    kyc_sm.fire(s, "kyc.start_review")
    assert s.state == "under_review"
    kyc_sm.fire(s, "kyc.approve")
    assert s.state == "approved"


def test_delivery_lifecycle():
    d = _Stub("pending")
    delivery_sm.fire(d, "delivery.approve")
    delivery_sm.fire(d, "delivery.mint")
    delivery_sm.fire(d, "delivery.ship")
    delivery_sm.fire(d, "delivery.deliver")
    assert d.state == "delivered"


def test_vendor_lifecycle():
    v = _Stub("applied")
    vendor_sm.fire(v, "vendor.approve")
    assert v.state == "approved"
    vendor_sm.fire(v, "vendor.suspend")
    assert v.state == "suspended"
    vendor_sm.fire(v, "vendor.reinstate")
    assert v.state == "approved"


def test_payment_attempt_lifecycle():
    p = _Stub("pending")
    payment_attempt_sm.fire(p, "payment.redirect")
    payment_attempt_sm.fire(p, "payment.verify_ok")
    assert p.state == "succeeded"


def test_payment_attempt_failure_path():
    p = _Stub("pending")
    payment_attempt_sm.fire(p, "payment.redirect")
    payment_attempt_sm.fire(p, "payment.verify_fail")
    assert p.state == "failed"
