"""
Plugin loader.

Walks `entry_points(group="keyhan.plugins")` so third-party packages can
register hooks (new gateways, AML scorers, KYC providers, etc.).
"""
from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any


def load_plugins(group: str = "keyhan.plugins") -> dict[str, Any]:
    found: dict[str, Any] = {}
    for ep in entry_points(group=group):
        try:
            found[ep.name] = ep.load()
        except Exception:  # noqa: BLE001 — non-fatal
            continue
    return found
