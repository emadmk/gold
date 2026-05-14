"""TOTP 2FA — RFC 6238 with HMAC-SHA1 and 30-second windows."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time

PERIOD = 30
DIGITS = 6


def generate_secret() -> str:
    return base64.b32encode(os.urandom(20)).decode().rstrip("=")


def _hotp(secret_b32: str, counter: int) -> str:
    key = base64.b32decode(secret_b32 + "=" * (-len(secret_b32) % 8))
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**DIGITS)
    return f"{code:0{DIGITS}d}"


def now_code(secret: str) -> str:
    return _hotp(secret, int(time.time() // PERIOD))


def verify(secret: str, code: str, window: int = 1) -> bool:
    """Accept the current code and ±window steps for clock drift."""
    if not code.isdigit() or len(code) != DIGITS:
        return False
    counter = int(time.time() // PERIOD)
    for delta in range(-window, window + 1):
        if hmac.compare_digest(_hotp(secret, counter + delta), code):
            return True
    return False


def provisioning_uri(secret: str, label: str, issuer: str = "KeyhanGold") -> str:
    from urllib.parse import quote

    return (
        f"otpauth://totp/{quote(issuer)}:{quote(label)}"
        f"?secret={secret}&issuer={quote(issuer)}&algorithm=SHA1&digits={DIGITS}&period={PERIOD}"
    )
