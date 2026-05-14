"""KYC service: submit, review, approve, reject."""
from __future__ import annotations

from typing import Any

from django.utils import timezone

from apps.audit.state_machine import kyc_sm

from ..models import KYCSubmission, User


def submit_kyc(user: User, **files: Any) -> KYCSubmission:
    submission, _ = KYCSubmission.objects.get_or_create(user=user)
    for k, v in files.items():
        if v is not None and hasattr(submission, k):
            setattr(submission, k, v)
    submission.save()

    # advance state machine
    if submission.state == "empty":
        kyc_sm.fire(
            submission,
            trigger="kyc.submit",
            target={"type": "kyc", "id": str(submission.id), "owner_id": str(user.id)},
        )
    elif submission.state == "requires_more":
        kyc_sm.fire(
            submission,
            trigger="kyc.submit",
            target={"type": "kyc", "id": str(submission.id), "owner_id": str(user.id)},
        )
    return submission


def start_review(submission: KYCSubmission, reviewer: User) -> KYCSubmission:
    kyc_sm.fire(
        submission,
        trigger="kyc.start_review",
        actor={"type": "admin", "id": str(reviewer.id)},
        target={"type": "kyc", "id": str(submission.id), "owner_id": str(submission.user_id)},
    )
    return submission


def approve(submission: KYCSubmission, reviewer: User) -> KYCSubmission:
    kyc_sm.fire(
        submission,
        trigger="kyc.approve",
        actor={"type": "admin", "id": str(reviewer.id)},
        target={"type": "kyc", "id": str(submission.id), "owner_id": str(submission.user_id)},
    )
    submission.reviewed_by = reviewer
    submission.reviewed_at = timezone.now()
    submission.save(update_fields=["reviewed_by", "reviewed_at"])
    submission.user.is_verified = True
    submission.user.save(update_fields=["is_verified"])
    return submission


def reject(submission: KYCSubmission, reviewer: User, reason: str) -> KYCSubmission:
    submission.rejection_reason = reason
    submission.reviewed_by = reviewer
    submission.reviewed_at = timezone.now()
    submission.save(update_fields=["rejection_reason", "reviewed_by", "reviewed_at"])
    kyc_sm.fire(
        submission,
        trigger="kyc.reject",
        actor={"type": "admin", "id": str(reviewer.id)},
        target={"type": "kyc", "id": str(submission.id), "owner_id": str(submission.user_id)},
        data={"reason": reason},
    )
    return submission
