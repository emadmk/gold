"""Encrypted CharField that stores ciphertext but exposes plaintext."""
from __future__ import annotations

from django.db import models

from .crypto import decrypt_field, encrypt_field


class EncryptedCharField(models.CharField):
    description = "AES-GCM (Fernet) encrypted CharField"

    def from_db_value(self, value, expression, connection):  # type: ignore[no-untyped-def]
        if value is None:
            return value
        try:
            return decrypt_field(value)
        except Exception:  # noqa: BLE001 — already-plaintext during migration
            return value

    def to_python(self, value):  # type: ignore[no-untyped-def]
        return value

    def get_prep_value(self, value):  # type: ignore[no-untyped-def]
        if value is None or value == "":
            return value
        return encrypt_field(value)
