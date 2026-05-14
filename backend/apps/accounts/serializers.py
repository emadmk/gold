from __future__ import annotations

import re

from rest_framework import serializers

from .models import KYCSubmission, User


PHONE_RE = re.compile(r"^09\d{9}$")

# Persian + Arabic-Indic digits → Latin digits
_DIGIT_MAP = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _normalise_digits(value: str) -> str:
    return value.strip().translate(_DIGIT_MAP)


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value: str) -> str:
        value = _normalise_digits(value)
        if not PHONE_RE.match(value):
            raise serializers.ValidationError(
                "شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد."
            )
        return value


class OTPVerifySerializer(PhoneSerializer):
    code = serializers.CharField(min_length=6, max_length=6)

    def validate_code(self, value: str) -> str:
        value = _normalise_digits(value)
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("کد باید ۶ رقم باشد.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "phone", "email", "first_name", "last_name",
            "is_verified", "is_phone_verified", "is_vendor",
            "tier", "two_factor_enabled", "created_at",
        ]
        read_only_fields = fields


class KYCSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCSubmission
        fields = [
            "id", "state",
            "national_card_front", "national_card_back",
            "selfie_with_card", "birth_certificate", "video_attestation",
            "card_pan_masked", "rejection_reason",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "state", "rejection_reason", "created_at", "updated_at"]
