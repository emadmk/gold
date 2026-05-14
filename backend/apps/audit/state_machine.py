"""
Central state machine.

Every meaningful state change in the domain (Order, KYC, Delivery,
Vendor, PaymentAttempt) is declared here and executed through
`StateMachine.transition`. The transition:

* validates the (from, trigger) pair,
* invokes the guard (must return True),
* runs the on_enter callback,
* emits all declared side-effect events,
* returns the new state.

CI gate `make event-coverage` reads `Transition.side_effects` and
verifies that every declared event kind exists in `catalogue.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .emit import emit_event
from .schema import StateTransition


class IllegalTransition(RuntimeError):
    """Raised when an illegal transition is attempted."""


@dataclass(frozen=True, slots=True)
class Transition:
    machine: str
    from_: str
    to: str
    trigger: str
    guard: Callable[..., bool] | None = None
    on_enter: Callable[..., None] | None = None
    side_effects: tuple[str, ...] = ()


@dataclass
class StateMachine:
    name: str
    transitions: list[Transition] = field(default_factory=list)

    def add(self, t: Transition) -> "StateMachine":
        if t.machine != self.name:
            raise ValueError(f"Transition machine {t.machine!r} != {self.name!r}")
        self.transitions.append(t)
        return self

    def find(self, frm: str, trigger: str) -> Transition:
        for t in self.transitions:
            if t.from_ == frm and t.trigger == trigger:
                return t
        raise IllegalTransition(
            f"No transition for machine={self.name} from={frm!r} trigger={trigger!r}"
        )

    def fire(
        self,
        instance: Any,
        trigger: str,
        *,
        actor: Any = None,
        target: Any = None,
        data: dict[str, Any] | None = None,
        causation_id: str = "",
        **guard_kwargs: Any,
    ) -> str:
        """
        Run the transition. The instance must expose:
          * a `state` attribute (string),
          * an `id` (for the target identifier),
          * a `save(update_fields=[...])` method.
        """
        current = getattr(instance, "state", None) or getattr(instance, "status", None)
        if current is None:
            raise IllegalTransition(f"{instance!r} has no 'state' or 'status' attribute")

        t = self.find(current, trigger)
        if t.guard and not t.guard(instance, **guard_kwargs):
            raise IllegalTransition(
                f"Guard rejected transition {self.name} {current} -> {t.to} via {trigger}"
            )

        # commit
        if hasattr(instance, "state"):
            instance.state = t.to
        else:
            instance.status = t.to

        # Save the field if the model is Django-backed
        if hasattr(instance, "save"):
            field_name = "state" if hasattr(instance, "state") and "state" in {
                f.name for f in getattr(instance, "_meta").fields  # type: ignore[union-attr]
            } else "status"
            try:
                instance.save(update_fields=[field_name, "updated_at"])
            except Exception:  # noqa: BLE001
                instance.save(update_fields=[field_name])

        if t.on_enter:
            t.on_enter(instance)

        st = StateTransition.of(self.name, t.from_, t.to, trigger)

        # Always emit a generic state-changed event for SM-level observers
        last_id = emit_event(
            f"{self.name}s.{'state.changed' if self.name not in {'orders'} else trigger.replace('order.', '').replace('payment.', '')}",
            actor=actor,
            target=target,
            state=st,
            data=data,
            causation_id=causation_id,
        ) if False else ""  # disabled: we use declared side_effects only

        # Emit declared side effects
        for kind in t.side_effects:
            last_id = emit_event(
                kind,
                actor=actor,
                target=target,
                state=st,
                data=data,
                causation_id=causation_id,
            )
        return last_id

    def graph(self) -> str:
        """Render a graphviz dot of the machine."""
        lines = [f'digraph "{self.name}" {{', '  rankdir=LR;']
        for t in self.transitions:
            label = t.trigger.replace('"', '\\"')
            lines.append(f'  "{t.from_}" -> "{t.to}" [label="{label}"];')
        lines.append("}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Concrete machines
# ---------------------------------------------------------------------------
order_sm = StateMachine("order")
order_sm.add(Transition("order", "draft", "awaiting_payment", "order.submitted",
                        side_effects=("orders.created", "wallet.rial.locked")))
order_sm.add(Transition("order", "awaiting_payment", "paid", "payment.verified",
                        side_effects=("orders.paid", "payments.attempt.verified")))
order_sm.add(Transition("order", "awaiting_payment", "expired", "order.timeout",
                        side_effects=("orders.expired", "wallet.rial.unlocked")))
order_sm.add(Transition("order", "awaiting_payment", "cancelled", "order.cancel",
                        side_effects=("orders.cancelled", "wallet.rial.unlocked")))
order_sm.add(Transition("order", "paid", "processing", "order.process",
                        side_effects=()))
order_sm.add(Transition("order", "processing", "completed", "order.settle",
                        side_effects=("orders.completed",)))
order_sm.add(Transition("order", "processing", "failed", "order.fail",
                        side_effects=("orders.failed",)))
order_sm.add(Transition("order", "failed", "refunded", "order.refund",
                        side_effects=("orders.refunded", "wallet.rial.deposit")))

kyc_sm = StateMachine("kyc")
kyc_sm.add(Transition("kyc", "empty", "submitted", "kyc.submit",
                      side_effects=("kyc.submitted",)))
kyc_sm.add(Transition("kyc", "submitted", "under_review", "kyc.start_review",
                      side_effects=()))
kyc_sm.add(Transition("kyc", "under_review", "approved", "kyc.approve",
                      side_effects=("kyc.approved",)))
kyc_sm.add(Transition("kyc", "under_review", "rejected", "kyc.reject",
                      side_effects=("kyc.rejected",)))
kyc_sm.add(Transition("kyc", "under_review", "requires_more", "kyc.require_more",
                      side_effects=("kyc.requires_more",)))
kyc_sm.add(Transition("kyc", "requires_more", "submitted", "kyc.submit",
                      side_effects=("kyc.submitted",)))

delivery_sm = StateMachine("delivery")
delivery_sm.add(Transition("delivery", "pending", "approved", "delivery.approve",
                           side_effects=("delivery.state.changed",)))
delivery_sm.add(Transition("delivery", "approved", "minting", "delivery.mint",
                           side_effects=("delivery.state.changed",)))
delivery_sm.add(Transition("delivery", "minting", "shipped", "delivery.ship",
                           side_effects=("delivery.state.changed",)))
delivery_sm.add(Transition("delivery", "shipped", "delivered", "delivery.deliver",
                           side_effects=("delivery.state.changed",)))
for fr in ("pending", "approved", "minting"):
    delivery_sm.add(Transition("delivery", fr, "cancelled", "delivery.cancel",
                               side_effects=("delivery.state.changed",)))

vendor_sm = StateMachine("vendor")
vendor_sm.add(Transition("vendor", "applied", "approved", "vendor.approve",
                         side_effects=("marketplace.vendor.approved",)))
vendor_sm.add(Transition("vendor", "applied", "rejected", "vendor.reject",
                         side_effects=()))
vendor_sm.add(Transition("vendor", "approved", "suspended", "vendor.suspend",
                         side_effects=("marketplace.vendor.suspended",)))
vendor_sm.add(Transition("vendor", "suspended", "approved", "vendor.reinstate",
                         side_effects=("marketplace.vendor.approved",)))

payment_attempt_sm = StateMachine("payment_attempt")
payment_attempt_sm.add(Transition("payment_attempt", "pending", "redirected", "payment.redirect",
                                  side_effects=("payments.attempt.redirected",)))
payment_attempt_sm.add(Transition("payment_attempt", "redirected", "succeeded", "payment.verify_ok",
                                  side_effects=("payments.attempt.verified",)))
payment_attempt_sm.add(Transition("payment_attempt", "redirected", "failed", "payment.verify_fail",
                                  side_effects=("payments.attempt.failed",)))
payment_attempt_sm.add(Transition("payment_attempt", "redirected", "cancelled", "payment.cancel",
                                  side_effects=("payments.attempt.failed",)))
payment_attempt_sm.add(Transition("payment_attempt", "redirected", "expired", "payment.expire",
                                  side_effects=("payments.attempt.failed",)))


MACHINES: dict[str, StateMachine] = {
    sm.name: sm for sm in (order_sm, kyc_sm, delivery_sm, vendor_sm, payment_attempt_sm)
}


def all_declared_event_kinds() -> set[str]:
    """Used by CI to verify every declared kind is in the catalogue."""
    kinds: set[str] = set()
    for sm in MACHINES.values():
        for t in sm.transitions:
            kinds.update(t.side_effects)
    return kinds
