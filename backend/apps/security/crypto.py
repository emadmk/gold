"""Cryptographic primitives used across the platform."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from django.conf import settings
from cryptography.fernet import Fernet


def _key() -> bytes:
    raw = settings.SECRET_KEY.encode()
    # derive a stable Fernet key from SECRET_KEY (32 bytes → urlsafe b64)
    h = hashlib.sha256(raw).digest()
    return base64.urlsafe_b64encode(h)


def encrypt_field(plaintext: str) -> str:
    if not plaintext:
        return ""
    return Fernet(_key()).encrypt(plaintext.encode()).decode()


def decrypt_field(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    return Fernet(_key()).decrypt(ciphertext.encode()).decode()


def constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())


def random_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def hash_sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
