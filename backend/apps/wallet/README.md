# `apps.wallet` — Rial & gold & silver wallets

The ledger. Append-only, integer-only, invariant-checked.

## Models

| Model | Purpose |
|-------|---------|
| `RialWallet` | `balance_rial`, `locked_rial`, `currency` (default `IRR`). DB CHECK constraints enforce `balance ≥ 0`, `locked ≥ 0`, `locked ≤ balance`. |
| `GoldWallet` | Holds **both** gold and silver. `address` is a `GLD-<hex>` short ID used for P2P transfers. CHECK constraints on every quantity. |
| `WalletTransaction` | The journal. Every credit/debit/lock/transfer is one row. Carries `event_id` (the ULID of the audit event) and an optional FK to `Order`. |

## Services (only mutators)

```python
credit_rial(user, amount, kind, order=None, description="")
debit_rial(user, amount, kind, order=None, description="")
lock_rial(user, amount)        # increase locked_rial
unlock_rial(user, amount)
credit_asset(user, "gold"|"silver", mg, kind, order=None, description="")
debit_asset(user, "gold"|"silver", mg, kind, order=None, description="")
transfer(sender, recipient_address, asset, mg, otp_code)  # in transfer.py
ensure_wallets(user)
```

All wrapped in `transaction.atomic()` + `SELECT … FOR UPDATE`. Each
emits a structured event whose ULID is stored back on the transaction.

## Invariants (`docs/SECURITY.md §8`)

Verified by `wallet.consistency_tick` (Celery, every 5 m). Failures
emit `audit.consistency.violation` (critical) → PagerDuty.

## Background tasks

* `wallet.daily_yield_payout` — every night at 00:05 credits
  `available_rial × daily_yield_apr / 365` to each verified user.
* `wallet.consistency_tick` — checks that
  `sum(WalletTransaction.rial_amount) == RialWallet.balance_rial` and
  the gold/silver analogues. Same for every asset.

## Key endpoints

```
GET  /api/v1/wallet
GET  /api/v1/wallet/transactions
POST /api/v1/wallet/withdraw/otp    POST /api/v1/wallet/withdraw
POST /api/v1/wallet/transfer/otp    POST /api/v1/wallet/transfer
```

## Events emitted

`wallet.rial.deposit / withdraw / locked / unlocked / adjustment / refund`,
`wallet.gold.buy / sell / transfer / delivery / adjustment / locked / unlocked`,
`wallet.silver.*`, `wallet.transfer.in / out`,
`wallet.yield.payout`, `wallet.commission`, `wallet.adjustment`.

## Conventions

* Use `mg` for asset quantities (`int`). Use `rial` for money (`int`).
* `kind` strings in the service map 1:1 to event suffixes:
  `kind="deposit"` → `wallet.rial.deposit`. Add new ones to the
  catalogue at the same time.

## Tests

`tests/test_wallet_invariants.py`, `tests/test_race_conditions.py`,
`tests/test_e2e_smoke.py`.
