"""
Secure file-upload validation.

Validates:
* size cap (default 20 MiB)
* declared Content-Type whitelist
* magic-byte sniff via python-magic — never trust the extension
* image re-encoding via Pillow (re-saved JPEG/PNG so any embedded
  payload is stripped)

Used by KYC + vendor onboarding + blog cover image.
"""
from __future__ import annotations

import io
from typing import Iterable

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile

DEFAULT_MAX_BYTES = 20 * 1024 * 1024
DEFAULT_IMAGE_MIMES = ("image/jpeg", "image/png", "image/webp")
DEFAULT_DOC_MIMES = ("image/jpeg", "image/png", "image/webp", "application/pdf")
DEFAULT_VIDEO_MIMES = ("video/mp4", "video/webm", "video/quicktime")

# Mapping from magic-byte detected MIME to declared MIME
_MAGIC_AS_MIME: dict[bytes, str] = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",   # webp also starts with RIFF
    b"%PDF-": "application/pdf",
    b"\x00\x00\x00\x18ftypmp42": "video/mp4",
    b"\x00\x00\x00\x20ftypisom": "video/mp4",
    b"\x1aE\xdf\xa3": "video/webm",
}


def _sniff(head: bytes) -> str | None:
    for prefix, mime in _MAGIC_AS_MIME.items():
        if head.startswith(prefix):
            return mime
    # python-magic fallback
    try:
        import magic  # type: ignore[import-not-found]

        return magic.from_buffer(head, mime=True)
    except Exception:  # noqa: BLE001 — libmagic might not be installed
        return None


def validate_upload(
    f: UploadedFile,
    *,
    allowed_mimes: Iterable[str] = DEFAULT_IMAGE_MIMES,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> None:
    """Raise ValidationError if the upload is unacceptable."""
    if f.size is None or f.size <= 0:
        raise ValidationError("فایل خالی است.")
    if f.size > max_bytes:
        raise ValidationError(
            f"حجم فایل بیش از حد مجاز است (سقف {max_bytes // (1024 * 1024)} مگابایت)."
        )
    if f.content_type and f.content_type not in allowed_mimes:
        raise ValidationError(
            f"نوع فایل مجاز نیست؛ مجازها: {', '.join(allowed_mimes)}."
        )
    head = f.read(4096)
    f.seek(0)
    sniffed = _sniff(head)
    if sniffed and sniffed not in allowed_mimes:
        raise ValidationError(
            f"محتوای فایل با نوع اعلام‌شده مطابقت ندارد ({sniffed})."
        )


def reencode_image(f: UploadedFile) -> InMemoryUploadedFile:
    """Strip metadata + re-encode image via Pillow so embedded payloads die.

    Returns a NEW InMemoryUploadedFile; the caller should assign it to
    the model field. Non-image files are returned unchanged.
    """
    if not (f.content_type or "").startswith("image/"):
        return f  # type: ignore[return-value]
    from PIL import Image

    try:
        img = Image.open(f).convert("RGB")
    except Exception:  # noqa: BLE001
        raise ValidationError("تصویر معتبر نیست.")  # noqa: B904
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    buf.seek(0)
    return InMemoryUploadedFile(
        buf, field_name=f.name or "file",
        name=(f.name or "file").rsplit(".", 1)[0] + ".jpg",
        content_type="image/jpeg",
        size=buf.getbuffer().nbytes, charset=None,
    )
