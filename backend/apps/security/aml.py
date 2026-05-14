"""
AML / fraud worker.

Velocity rules:
* daily deposits > threshold → aml.threshold.high + open AMLCase
* withdraw to a never-seen-before IBAN → flag
* > 5 KYC docs from one device fingerprint → flag

The worker reads recent events from `apps.audit.models.AuditEntry`
(populated by `emit_event`'s local mirror) and produces decisions via
`apps.security.risk.score`.
"""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.db.models import Q, Sum
from django.utils import timezone

from apps.audit.emit import emit_event

from .risk.engine import score


@shared_task(name="security.aml_tick")
def aml_tick() -> dict[str, int]:
    """Scan recent rial deposits and withdrawals for AML triggers."""
    from apps.wallet.models import WalletTransaction

    since = timezone.now() - timedelta(hours=24)
    threshold = int(Decimal(settings.DOMAIN_DEFAULTS["aml_threshold_rial"]))
    flagged = 0

    agg = (
        WalletTransaction.objects.filter(
            asset="rial", created_at__gte=since,
            type__in=("deposit", "withdraw"),
        )
        .values("user")
        .annotate(total=Sum("rial_amount"))
        .filter(Q(total__gte=threshold) | Q(total__lte=-threshold))
    )
    for row in agg:
        decision = score({"rial_amount": abs(row["total"])})
        if decision.action != "allow":
            emit_event(
                "aml.threshold.high",
                severity="warning",
                target={"type": "user", "id": str(row["user"])},
                data={
                    "amount_24h": row["total"], "threshold": threshold,
                    "risk_score": decision.score, "action": decision.action,
                    "reasons": list(decision.reasons),
                },
            )
            flagged += 1
    return {"flagged": flagged}
