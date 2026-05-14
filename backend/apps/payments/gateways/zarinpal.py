"""Zarinpal v4 (sandbox + prod)."""
from __future__ import annotations

import httpx
from django.conf import settings

from .base import BaseGateway, PaymentRequest, PaymentResponse, VerifyResponse, register


@register("zarinpal")
class ZarinpalGateway(BaseGateway):
    name = "zarinpal"

    def _config(self):
        cfg = settings.PAYMENT_GATEWAYS["zarinpal"]
        if cfg.get("sandbox", True):
            return {
                "merchant": cfg["merchant_id"] or "00000000-0000-0000-0000-000000000000",
                "request": "https://sandbox.zarinpal.com/pg/v4/payment/request.json",
                "verify": "https://sandbox.zarinpal.com/pg/v4/payment/verify.json",
                "start": "https://sandbox.zarinpal.com/pg/StartPay/",
            }
        return {
            "merchant": cfg["merchant_id"],
            "request": "https://api.zarinpal.com/pg/v4/payment/request.json",
            "verify": "https://api.zarinpal.com/pg/v4/payment/verify.json",
            "start": "https://www.zarinpal.com/pg/StartPay/",
        }

    def request(self, req: PaymentRequest) -> PaymentResponse:
        cfg = self._config()
        body = {
            "merchant_id": cfg["merchant"],
            "amount": req.amount_rial,
            "callback_url": req.callback_url,
            "description": req.description[:255],
            "metadata": {"mobile": req.mobile or "", "email": req.email or ""},
        }
        try:
            with httpx.Client(timeout=15) as c:
                r = c.post(cfg["request"], json=body)
            data = r.json()
            d = data.get("data") or {}
            if d.get("code") == 100 and d.get("authority"):
                return PaymentResponse(
                    success=True,
                    authority=d["authority"],
                    redirect_url=cfg["start"] + d["authority"],
                )
            errs = data.get("errors") or {}
            return PaymentResponse(
                success=False,
                authority="",
                redirect_url="",
                error_code=str(errs.get("code")) if isinstance(errs, dict) else "",
                error_message=str(errs.get("message")) if isinstance(errs, dict) else str(errs),
            )
        except Exception as exc:  # noqa: BLE001
            return PaymentResponse(False, "", "", "exc", repr(exc))

    def verify(self, authority: str, amount_rial: int) -> VerifyResponse:
        cfg = self._config()
        try:
            with httpx.Client(timeout=15) as c:
                r = c.post(
                    cfg["verify"],
                    json={"merchant_id": cfg["merchant"], "amount": amount_rial, "authority": authority},
                )
            data = r.json()
            d = data.get("data") or {}
            if d.get("code") in (100, 101):
                return VerifyResponse(
                    success=True,
                    ref_id=str(d.get("ref_id", "")),
                    card_pan_masked=d.get("card_pan", ""),
                    raw=data,
                )
            return VerifyResponse(False, "", None, data)
        except Exception as exc:  # noqa: BLE001
            return VerifyResponse(False, "", None, {"error": repr(exc)})
