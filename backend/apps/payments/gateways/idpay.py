"""IDPay v1.1."""
from __future__ import annotations

import httpx
from django.conf import settings

from .base import BaseGateway, PaymentRequest, PaymentResponse, VerifyResponse, register


@register("idpay")
class IdpayGateway(BaseGateway):
    name = "idpay"

    def _headers(self) -> dict[str, str]:
        cfg = settings.PAYMENT_GATEWAYS["idpay"]
        h = {"Content-Type": "application/json", "X-API-KEY": cfg["api_key"]}
        if cfg.get("sandbox"):
            h["X-SANDBOX"] = "1"
        return h

    def request(self, req: PaymentRequest) -> PaymentResponse:
        try:
            with httpx.Client(timeout=15, headers=self._headers()) as c:
                r = c.post(
                    "https://api.idpay.ir/v1.1/payment",
                    json={
                        "order_id": req.order_id,
                        "amount": req.amount_rial,
                        "callback": req.callback_url,
                        "desc": req.description[:255],
                        "phone": req.mobile or "",
                        "mail": req.email or "",
                    },
                )
            data = r.json()
            if r.status_code == 201 and data.get("id"):
                return PaymentResponse(True, data["id"], data["link"])
            return PaymentResponse(False, "", "", str(data.get("error_code")),
                                   str(data.get("error_message", "")))
        except Exception as exc:  # noqa: BLE001
            return PaymentResponse(False, "", "", "exc", repr(exc))

    def verify(self, authority: str, amount_rial: int) -> VerifyResponse:
        try:
            with httpx.Client(timeout=15, headers=self._headers()) as c:
                r = c.post(
                    "https://api.idpay.ir/v1.1/payment/verify",
                    json={"id": authority, "order_id": authority},
                )
            data = r.json()
            if data.get("status") == 100 and int(data.get("amount", 0)) == amount_rial:
                return VerifyResponse(True, str(data.get("track_id", "")),
                                      data.get("payment", {}).get("card_no", ""), data)
            return VerifyResponse(False, "", None, data)
        except Exception as exc:  # noqa: BLE001
            return VerifyResponse(False, "", None, {"error": repr(exc)})
