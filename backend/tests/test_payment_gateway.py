"""Payment-gateway tests with mocked HTTPX responses."""
from __future__ import annotations

import pytest

from apps.payments.gateways import PaymentRequest, get as get_gateway


def _patch_httpx_client(monkeypatch, *, post_response):
    """Replace httpx.Client.post + .get with a stub that returns
    `post_response` (a dict that becomes .json() and 200 by default)."""

    class _StubResponse:
        def __init__(self, payload, status_code=200, text=""):
            self._payload = payload
            self.status_code = status_code
            self.text = text or str(payload)

        def json(self):
            return self._payload

    class _StubClient:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, *a, **kw):
            return _StubResponse(post_response, post_response.get("_status", 200))

        def get(self, *a, **kw):
            return _StubResponse(post_response, post_response.get("_status", 200))

    import httpx

    monkeypatch.setattr(httpx, "Client", _StubClient)


def test_zarinpal_request_ok(monkeypatch):
    _patch_httpx_client(monkeypatch, post_response={
        "data": {"code": 100, "authority": "A0000000000000000000000000000000000001"},
    })
    gw = get_gateway("zarinpal")
    resp = gw.request(PaymentRequest(
        order_id="KG-1", amount_rial=100_000, callback_url="https://x/cb",
        description="t",
    ))
    assert resp.success
    assert resp.authority.startswith("A")
    assert "/StartPay/" in resp.redirect_url


def test_zarinpal_request_failure(monkeypatch):
    _patch_httpx_client(monkeypatch, post_response={
        "errors": {"code": -9, "message": "bad merchant"},
    })
    gw = get_gateway("zarinpal")
    resp = gw.request(PaymentRequest(
        order_id="KG-2", amount_rial=100_000, callback_url="https://x",
        description="t",
    ))
    assert not resp.success
    assert "bad merchant" in (resp.error_message or "")


def test_zarinpal_verify_ok(monkeypatch):
    _patch_httpx_client(monkeypatch, post_response={
        "data": {"code": 100, "ref_id": 123456, "card_pan": "6037***0000"},
    })
    gw = get_gateway("zarinpal")
    v = gw.verify("AUTH-X", 100_000)
    assert v.success and v.ref_id == "123456"


def test_idpay_request_ok(monkeypatch):
    _patch_httpx_client(monkeypatch, post_response={
        "_status": 201, "id": "idpay-abc", "link": "https://idpay.ir/p/idpay-abc",
    })
    gw = get_gateway("idpay")
    resp = gw.request(PaymentRequest("KG-3", 100_000, "https://x", "t"))
    assert resp.success
    assert resp.redirect_url.endswith("idpay-abc")


def test_payping_verify_ok(monkeypatch):
    _patch_httpx_client(monkeypatch, post_response={
        "_status": 200, "amount": 10_000, "cardNumber": "6037***1234",
    })
    gw = get_gateway("payping")
    v = gw.verify("REF1", 100_000)  # 100_000 rial = 10_000 toman
    assert v.success
