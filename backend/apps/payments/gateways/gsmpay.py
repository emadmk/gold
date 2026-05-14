"""GSM Pay — GSM.ir's in-house wallet/credit gateway (placeholder).

Implements the same `BaseGateway` interface so it can be picked from
the payment-method dropdown. Real merchant credentials + endpoints
land via `PAYMENT_GATEWAYS["gsmpay"]` once available.
"""
from __future__ import annotations

import httpx
from django.conf import settings

from .base import BaseGateway, PaymentRequest, PaymentResponse, VerifyResponse, register


@register("gsmpay")
class GsmPayGateway(BaseGateway):
    name = "gsmpay"

    def _cfg(self) -> dict:
        return settings.PAYMENT_GATEWAYS.get("gsmpay", {})

    def request(self, req: PaymentRequest) -> PaymentResponse:
        cfg = self._cfg()
        if not cfg.get("api_key"):
            return PaymentResponse(
                False, "", "", "no_credentials",
                "GSM Pay credentials are not configured.",
            )
        endpoint = cfg.get("request_url", "https://pay.gsm.ir/v1/payment/init")
        try:
            with httpx.Client(timeout=15, headers={"Authorization": f"Bearer {cfg['api_key']}"}) as c:
                r = c.post(endpoint, json={
                    "amount_rial": req.amount_rial,
                    "callback_url": req.callback_url,
                    "order_id": req.order_id,
                    "description": req.description[:255],
                    "mobile": req.mobile or "",
                })
            data = r.json() if r.text else {}
            if r.status_code in (200, 201) and data.get("token"):
                return PaymentResponse(
                    True, data["token"],
                    cfg.get("redirect_base", "https://pay.gsm.ir/p/") + data["token"],
                )
            return PaymentResponse(False, "", "", str(data.get("code")),
                                   str(data.get("message", "gsmpay error")))
        except Exception as exc:  # noqa: BLE001
            return PaymentResponse(False, "", "", "exc", repr(exc))

    def verify(self, authority: str, amount_rial: int) -> VerifyResponse:
        cfg = self._cfg()
        endpoint = cfg.get("verify_url", "https://pay.gsm.ir/v1/payment/verify")
        try:
            with httpx.Client(timeout=15, headers={"Authorization": f"Bearer {cfg.get('api_key', '')}"}) as c:
                r = c.post(endpoint, json={"token": authority, "amount_rial": amount_rial})
            data = r.json() if r.text else {}
            if r.status_code == 200 and data.get("status") == "ok":
                return VerifyResponse(True, str(data.get("ref_id", "")),
                                      data.get("card_pan_masked", ""), data)
            return VerifyResponse(False, "", None, data)
        except Exception as exc:  # noqa: BLE001
            return VerifyResponse(False, "", None, {"error": repr(exc)})
