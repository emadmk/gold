"""SnapPay installment payment gateway (placeholder implementation).

SnapPay is an Iranian buy-now-pay-later provider; this module implements
the same `BaseGateway` interface as Zarinpal/IDPay/PayPing so it can be
selected from the user's payment-method dropdown without any other code
change. Real REST endpoints / merchant credentials are filled in via the
`PAYMENT_GATEWAYS["snappay"]` settings stanza when the merchant account
is ready.
"""
from __future__ import annotations

import uuid

import httpx
from django.conf import settings

from .base import BaseGateway, PaymentRequest, PaymentResponse, VerifyResponse, register


@register("snappay")
class SnappayGateway(BaseGateway):
    name = "snappay"

    def _cfg(self) -> dict:
        return settings.PAYMENT_GATEWAYS.get("snappay", {})

    def request(self, req: PaymentRequest) -> PaymentResponse:
        cfg = self._cfg()
        endpoint = cfg.get("request_url", "https://api.snappay.ir/api/online/payment/v1/init")
        api_key = cfg.get("api_key", "")
        if not api_key:
            return PaymentResponse(
                False, "", "", "no_credentials",
                "SnapPay merchant credentials are not configured.",
            )
        try:
            with httpx.Client(timeout=15, headers={"Authorization": f"Bearer {api_key}"}) as c:
                r = c.post(endpoint, json={
                    "amount": req.amount_rial // 10,  # toman
                    "mobile": req.mobile or "",
                    "description": req.description[:255],
                    "returnURL": req.callback_url,
                    "merchantOrderId": req.order_id,
                    "transactionId": str(uuid.uuid4()),
                })
            data = r.json()
            if r.status_code in (200, 201) and data.get("paymentToken"):
                return PaymentResponse(
                    True, data["paymentToken"],
                    cfg.get("redirect_base", "https://app.snappay.ir/online/payment/") + data["paymentToken"],
                )
            return PaymentResponse(
                False, "", "", str(data.get("errorCode")),
                str(data.get("errorMessage", "snappay error")),
            )
        except Exception as exc:  # noqa: BLE001
            return PaymentResponse(False, "", "", "exc", repr(exc))

    def verify(self, authority: str, amount_rial: int) -> VerifyResponse:
        cfg = self._cfg()
        endpoint = cfg.get("verify_url", "https://api.snappay.ir/api/online/payment/v1/verify")
        api_key = cfg.get("api_key", "")
        try:
            with httpx.Client(timeout=15, headers={"Authorization": f"Bearer {api_key}"}) as c:
                r = c.post(endpoint, json={"paymentToken": authority})
            data = r.json() if r.text else {}
            if r.status_code == 200 and data.get("successful"):
                return VerifyResponse(True, str(data.get("transactionId", "")),
                                      data.get("cardNumber", ""), data)
            return VerifyResponse(False, "", None, data)
        except Exception as exc:  # noqa: BLE001
            return VerifyResponse(False, "", None, {"error": repr(exc)})
