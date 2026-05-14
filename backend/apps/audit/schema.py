"""
Event envelope — pydantic models that validate every event before it goes
to Redis Streams or the structlog sink.

This file is the canonical contract referenced by `docs/OBSERVABILITY.md §2`.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

EventCategory = Literal["domain", "security", "system", "aml", "ux"]
EventSeverity = Literal["debug", "info", "warning", "error", "critical"]
EventOutcome = Literal["success", "failure", "denied"]


class Actor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["user", "admin", "system", "vendor", "gateway", "anonymous"] = "system"
    id: str = ""
    ip: str = ""
    user_agent: str = ""
    session_id: str = ""
    roles: list[str] = Field(default_factory=list)
    kyc_level: int = 0


class Target(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str
    id: str
    owner_id: str = ""


class Correlation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    trace_id: str = ""
    span_id: str = ""
    request_id: str = ""
    causation_id: str = ""
    session_id: str = ""


class StateTransition(BaseModel):
    model_config = ConfigDict(extra="ignore")
    machine: str
    from_: str = Field(alias="from")
    to: str
    trigger: str

    @classmethod
    def of(cls, machine: str, frm: str, to: str, trigger: str) -> "StateTransition":
        return cls.model_validate({"machine": machine, "from": frm, "to": to, "trigger": trigger})


class Service(BaseModel):
    name: str = "keyhan-backend"
    version: str = "0.1.0"
    env: str = "dev"
    host: str = ""


class EventMeta(BaseModel):
    id: str
    kind: str
    version: int = 1
    category: EventCategory = "domain"
    severity: EventSeverity = "info"
    outcome: EventOutcome = "success"


class Envelope(BaseModel):
    """The shape every event must take when it hits Redis Streams / Logstash."""

    model_config = ConfigDict(populate_by_name=True)

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="@timestamp")
    event: EventMeta
    actor: Actor = Field(default_factory=Actor)
    target: Target | None = None
    correlation: Correlation = Field(default_factory=Correlation)
    state: StateTransition | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    service: Service = Field(default_factory=Service)

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, mode="json", exclude_none=True)
