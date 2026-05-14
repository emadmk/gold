# ADR-0001 — Money in rial (int64), weight in milligram (int64)

* **Status:** Accepted (2026-05-14)
* **Deciders:** Backend team
* **Related:** `docs/SECURITY.md §8`, `apps/wallet/units.py`

## Context

We process gold and silver volumes plus rial amounts in every financial
transition. Many Iranian gold platforms store gram values as floating-point
which leads to ε drifts at the third decimal — exactly the place where the
domain cares (1 mg = 1/1000 g, prices per mg are in the order of 17,000 IRR).

## Decision

* All money is stored as `BigIntegerField` of **rials** — never tomans or
  floats.
* All weight is stored as `BigIntegerField` of **milligrams** — never grams
  or floats.
* Conversion (to gram/tomān) is a presentation-layer concern only.
* Coefficients use `Decimal` (not float), still applied via the integer
  cast at the boundary.

## Consequences

* Floating-point drift is impossible.
* Every CHECK constraint, every audit-event consistency check, every test
  asserts integer equalities (not "approximately").
* Front-end formatters must always divide by 10 for tomans and by 1000 for
  grams; this lives in `lib/format.ts`.
