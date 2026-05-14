"""Smoke tests for the audit envelope and catalogue."""
from __future__ import annotations

import pytest

from apps.audit.catalogue import CATALOGUE
from apps.audit.schema import Envelope, EventMeta
from apps.audit.state_machine import all_declared_event_kinds


def test_envelope_minimal_roundtrip() -> None:
    env = Envelope(event=EventMeta(id="01HX5T8V7Q5MZF1J0K6Q9A4P3B", kind="orders.created"))
    payload = env.to_payload()
    assert payload["event"]["kind"] == "orders.created"
    assert payload["@timestamp"]


def test_state_machine_events_are_registered() -> None:
    missing = all_declared_event_kinds() - set(CATALOGUE.keys())
    assert missing == set(), f"unregistered SM events: {missing}"


@pytest.mark.parametrize("kind", sorted(CATALOGUE.keys()))
def test_each_catalogue_entry_has_known_category(kind: str) -> None:
    spec = CATALOGUE[kind]
    assert spec.category in {"domain", "security", "system", "aml", "ux"}
