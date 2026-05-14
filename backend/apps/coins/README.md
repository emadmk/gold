# `apps.coins` — Coin reference data

Lightweight reference table — the standard sekke types Iran's national
mint issues.

## Model

`CoinType(code, title_fa, weight_mg, gold_content_mg, image, is_active)`.

Seeded by `seed_dev`:

| `code` | name (fa) | total weight | pure gold |
|--------|-----------|--------------|-----------|
| `emami` | سکه امامی | 8133 mg | 7320 mg |
| `bahar` | سکه بهار آزادی | 8133 mg | 7320 mg |
| `half` | نیم سکه | 4067 mg | 3660 mg |
| `quarter` | ربع سکه | 2034 mg | 1830 mg |
| `gerami` | سکه گرمی | 1016 mg | 915 mg |

## How it's used

* `Product.coin_type` is a CharField holding the `code`.
* The pricing service uses `weight_mg` and `karat=910` (≈ 22k) when
  computing a coin product's price (see
  [`DOMAIN.md §3.5`](../../../docs/DOMAIN.md#35-marketplace-product-coin)).

## Admin

Standard `ModelAdmin` — usually edited by an admin to add a newly
issued series (e.g. a commemorative coin).
