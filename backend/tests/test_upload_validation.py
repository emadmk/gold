"""Upload validation (size, MIME, magic-byte)."""
from __future__ import annotations

import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.security.uploads import (
    DEFAULT_DOC_MIMES,
    DEFAULT_IMAGE_MIMES,
    validate_upload,
)

JPEG_HEADER = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PNG_HEADER = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
PDF_HEADER = b"%PDF-1.4\n" + b"\x00" * 100


def _upload(content: bytes, name: str, ctype: str) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content, content_type=ctype)


def test_accepts_real_jpeg():
    validate_upload(_upload(JPEG_HEADER, "x.jpg", "image/jpeg"))


def test_accepts_png():
    validate_upload(_upload(PNG_HEADER, "x.png", "image/png"))


def test_pdf_rejected_when_only_images_allowed():
    with pytest.raises(ValidationError):
        validate_upload(
            _upload(PDF_HEADER, "x.pdf", "application/pdf"),
            allowed_mimes=DEFAULT_IMAGE_MIMES,
        )


def test_pdf_accepted_in_doc_set():
    validate_upload(
        _upload(PDF_HEADER, "x.pdf", "application/pdf"),
        allowed_mimes=DEFAULT_DOC_MIMES,
    )


def test_oversize_rejected():
    big = JPEG_HEADER + b"\x00" * (1024 * 1024)
    with pytest.raises(ValidationError):
        validate_upload(
            _upload(big, "x.jpg", "image/jpeg"),
            max_bytes=512 * 1024,
        )


def test_empty_rejected():
    with pytest.raises(ValidationError):
        validate_upload(_upload(b"", "x.jpg", "image/jpeg"))


def test_extension_lie_caught_by_magic():
    """A `.jpg` file whose bytes are actually a PDF must be rejected
    when only images are allowed."""
    fake = _upload(PDF_HEADER, "actually.pdf.jpg", "image/jpeg")
    with pytest.raises(ValidationError):
        validate_upload(fake, allowed_mimes=DEFAULT_IMAGE_MIMES)
