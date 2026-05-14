"""Payping v2."""
from __future__ import annotations

import httpx
from django.conf import settings

from .base import BaseGateway, PaymentRequest, PaymentResponse, VerifyResponse, register


@register("payping")
class PaypingGateway(BaseGateway):
    name = "payping"

    def _headers(self) -> dict[str, str]:
        cfg = settings.PAYMENT_GATEWAYS["payping"]
        return {
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def request(self, req: PaymentRequest) -> PaymentResponse:
        # PayPing API expects amount in toman, not rial.
        amount_toman = req.amount_rial // 10
        try:
            with httpx.Client(timeout=15, headers=self._headers()) as c:
                r = c.post(
                    "https://api.payping.ir/v2/pay",
                    json={
                        "amount": amount_toman,
                        "payerIdentity": req.mobile or "",
                        "returnUrl": req.callback_url,
                        "description": req.description[:255],
                        "clientRefId": req.order_id,
                    },
                )
            if r.status_code in (200, 201):
                data = r.json()
                code = data.get("code")
                if code:
                    return PaymentResponse(True, code,
                                           f"https://api.payping.ir/v2/pay/gotoipg/{code}")
            return PaymentResponse(False, "", "", str(r.status_code), r.text)
        except Exception as exc:  # noqa: BLE001
            return PaymentResponse(False, "", "", "exc", repr(exc))

    def verify(self, authority: str, amount_rial: int) -> VerifyResponse:
        amount_toman = amount_rial // 10
        try:
            with httpx.Client(timeout=15, headers=self._headers()) as c:
                r = c.post(
                    "https://api.payping.ir/v2/pay/verify",
                    json={"refId": authority, "amount": amount_toman},
                )
            data = r.json() if r.text else {}
            if r.status_code in (200, 201) and (data.get("cardNumber") or data.get("amount")):
                return VerifyResponse(True, authority, data.get("cardNumber", ""), data)
            return VerifyResponse(False, "", None, data)
        except Exception as exc:  # noqa: BLE001
            return VerifyResponse(False, "", None, {"error": repr(exc)})
