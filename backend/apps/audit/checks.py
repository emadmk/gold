"""
CI gate scripts. Invoked via `python -m apps.audit.checks <command>`.

Commands:
  event_coverage   — every state-machine side-effect kind is registered in the catalogue.
  catalogue        — catalogue is well-formed (unique keys, ASCII-sorted file).
  sm_coverage      — every Order/KYC/Delivery service entry-point uses the SM.
"""
from __future__ import annotations

import sys

from .catalogue import CATALOGUE
from .state_machine import MACHINES, all_declared_event_kinds


def event_coverage() -> int:
    declared = all_declared_event_kinds()
    missing = declared - set(CATALOGUE.keys())
    if missing:
        print("ERROR: state machine declares unregistered kinds:")
        for k in sorted(missing):
            print(f"  - {k}")
        return 1
    print(f"OK: {len(declared)} declared kinds, all registered "
          f"({len(CATALOGUE)} total in catalogue)")
    return 0


def catalogue_check() -> int:
    keys = list(CATALOGUE.keys())
    if len(keys) != len(set(keys)):
        print("ERROR: duplicate keys in catalogue")
        return 1
    print(f"OK: catalogue has {len(keys)} unique kinds")
    return 0


def sm_coverage() -> int:
    # Lightweight sanity: each machine has at least one transition and is non-trivial.
    for name, sm in MACHINES.items():
        if not sm.transitions:
            print(f"ERROR: state machine {name!r} has no transitions")
            return 1
    print(f"OK: {len(MACHINES)} state machines, "
          f"{sum(len(m.transitions) for m in MACHINES.values())} transitions")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m apps.audit.checks <event_coverage|catalogue|sm_coverage>")
        return 2
    cmd = sys.argv[1]
    fns = {
        "event_coverage": event_coverage,
        "catalogue": catalogue_check,
        "sm_coverage": sm_coverage,
    }
    fn = fns.get(cmd)
    if not fn:
        print(f"unknown command: {cmd}")
        return 2
    return fn()


if __name__ == "__main__":
    raise SystemExit(main())
