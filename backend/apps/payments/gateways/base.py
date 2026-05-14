"""Gateway abstraction — drop a new payment processor in by registering it."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True, frozen=True)
class PaymentRequest:
    order_id: str
    amount_rial: int
    callback_url: str
    description: str
    mobile: str | None = None
    email: str | None = None


@dataclass(slots=True, frozen=True)
class PaymentResponse:
    success: bool
    authority: str
    redirect_url: str
    error_code: str | None = None
    error_message: str | None = None


@dataclass(slots=True, frozen=True)
class VerifyResponse:
    success: bool
    ref_id: str
    card_pan_masked: str | None = None
    raw: dict | None = None


class BaseGateway(ABC):
    name: str

    @abstractmethod
    def request(self, req: PaymentRequest) -> PaymentResponse: ...

    @abstractmethod
    def verify(self, authority: str, amount_rial: int) -> VerifyResponse: ...


GATEWAYS: dict[str, type[BaseGateway]] = {}


def register(name: str) -> Callable[[type[BaseGateway]], type[BaseGateway]]:
    def deco(cls: type[BaseGateway]) -> type[BaseGateway]:
        GATEWAYS[name] = cls
        cls.name = name
        return cls
    return deco


def get(name: str) -> BaseGateway:
    try:
        return GATEWAYS[name]()
    except KeyError as exc:
        raise KeyError(f"unknown gateway: {name}") from exc
