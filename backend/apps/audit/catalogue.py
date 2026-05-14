"""
Event catalogue.

Every `kind` used by `emit_event` MUST be registered here. CI gate
`make event-coverage` walks both the state machine and the codebase to
ensure parity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class EventSpec:
    kind: str
    category: Literal["domain", "security", "system", "aml", "ux"]
    default_severity: Literal["debug", "info", "warning", "error", "critical"] = "info"
    description: str = ""


CATALOGUE: dict[str, EventSpec] = {}


def register(spec: EventSpec) -> None:
    if spec.kind in CATALOGUE:
        raise RuntimeError(f"Duplicate event kind in catalogue: {spec.kind}")
    CATALOGUE[spec.kind] = spec


def _r(kind: str, category: str, **kw: object) -> None:
    register(EventSpec(kind=kind, category=category, **kw))  # type: ignore[arg-type]


# Accounts & KYC -------------------------------------------------------------
_r("accounts.otp.requested", "security", description="OTP send queued")
_r("accounts.otp.delivered", "security", description="SMS provider acknowledged delivery")
_r("accounts.otp.verified", "security", description="OTP correct, identity proven")
_r("accounts.otp.rejected", "security", default_severity="warning")
_r("accounts.user.registered", "domain")
_r("accounts.session.opened", "security")
_r("accounts.session.refreshed", "security")
_r("accounts.session.revoked", "security")
_r("accounts.user.frozen", "security", default_severity="critical")
_r("kyc.submitted", "domain")
_r("kyc.approved", "domain")
_r("kyc.rejected", "domain", default_severity="warning")
_r("kyc.requires_more", "domain", default_severity="warning")
_r("kyc.flag.aml", "aml", default_severity="warning")

# Pricing --------------------------------------------------------------------
_r("pricing.tick.captured", "domain", default_severity="debug")
_r("pricing.tick.stale", "system", default_severity="warning")
_r("pricing.quote.issued", "domain", default_severity="debug")
_r("pricing.formula.updated", "domain")
_r("pricing.source.failover", "system", default_severity="warning")

# Wallet ---------------------------------------------------------------------
for k in (
    "wallet.rial.deposit",
    "wallet.rial.withdraw",
    "wallet.rial.adjustment",
    "wallet.rial.refund",
    "wallet.rial.locked",
    "wallet.rial.unlocked",
    "wallet.gold.buy",
    "wallet.gold.sell",
    "wallet.gold.transfer",
    "wallet.gold.delivery",
    "wallet.gold.adjustment",
    "wallet.gold.locked",
    "wallet.gold.unlocked",
    "wallet.silver.buy",
    "wallet.silver.sell",
    "wallet.silver.transfer",
    "wallet.silver.delivery",
    "wallet.silver.adjustment",
    "wallet.transfer.out",
    "wallet.transfer.in",
    "wallet.yield.payout",
    "wallet.adjustment",
    "wallet.commission",
):
    _r(k, "domain")

# Orders ---------------------------------------------------------------------
for k in (
    "orders.created",
    "orders.expired",
    "orders.cancelled",
    "orders.paid",
    "orders.completed",
    "orders.failed",
    "orders.refunded",
    "orders.timer.tick",
):
    _r(k, "domain")

# Payments -------------------------------------------------------------------
for k in (
    "payments.attempt.created",
    "payments.attempt.redirected",
    "payments.attempt.callback",
    "payments.attempt.verified",
    "payments.attempt.failed",
):
    _r(k, "domain")
_r("payments.webhook.duplicate", "security", default_severity="warning")

# Delivery & marketplace -----------------------------------------------------
_r("delivery.requested", "domain")
_r("delivery.state.changed", "domain")
_r("marketplace.vendor.applied", "domain")
_r("marketplace.vendor.approved", "domain")
_r("marketplace.vendor.suspended", "domain", default_severity="warning")
_r("marketplace.product.published", "domain")
_r("marketplace.product.delisted", "domain")
_r("marketplace.settlement.run", "domain")
_r("marketplace.cart.item_added", "domain", default_severity="debug")
_r("marketplace.cart.item_removed", "domain", default_severity="debug")
_r("marketplace.cart.price_changed", "domain")
_r("marketplace.cart.discount_applied", "domain")
_r("marketplace.cart.relocked", "domain", default_severity="debug")
_r("marketplace.shipping.address_added", "domain", default_severity="debug")

# Security / system ----------------------------------------------------------
_r("security.login.brute_force", "security", default_severity="warning")
_r("security.ratelimit.breach", "security", default_severity="warning")
_r("security.csrf.failure", "security", default_severity="warning")
_r("security.permission.denied", "security", default_severity="warning")
_r("security.token.blacklisted", "security")
_r("audit.consistency.violation", "system", default_severity="critical")
_r("system.feature_flag.toggled", "system")
_r("system.celery.task.failed", "system", default_severity="error")

# AML ------------------------------------------------------------------------
_r("aml.threshold.high", "aml", default_severity="warning")
_r("aml.case.opened", "aml", default_severity="warning")
_r("aml.case.closed", "aml")
_r("aml.sanctions.hit", "aml", default_severity="critical")


def get(kind: str) -> EventSpec:
    try:
        return CATALOGUE[kind]
    except KeyError as exc:
        raise KeyError(f"Unknown event kind '{kind}' — register in apps/audit/catalogue.py") from exc
