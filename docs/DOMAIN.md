# KeyhanGold — Domain Reference

The business logic, codified. If you're writing a service that touches
money or weight, this is the cheat-sheet to keep next to your screen.

## 1. Units (non-negotiable)

| Concept | Type | Unit | Notes |
|---------|------|------|-------|
| Money | `BigIntegerField` | **rial** | Display layer converts to toman (×10⁻¹) |
| Gold | `BigIntegerField` | **milligram** | 1 g = 1000 mg |
| Silver | `BigIntegerField` | **milligram** | same |
| Coefficients | `Decimal` | unit-less | Stored in `PricingFormula.value` |

**No floats. Anywhere. Ever.** See [ADR-0001](decisions/0001-money-and-weight-in-integers.md).

## 2. Reference data

### 2.1 Coin catalogue

Real Iran national mint specifications, seeded by `seed_dev`.

| `code` | name (fa) | weight | pure gold |
|--------|-----------|--------|-----------|
| `emami` | سکه امامی | 8.133 g | 7.320 g |
| `bahar` | سکه بهار آزادی | 8.133 g | 7.320 g |
| `half` | نیم سکه | 4.067 g | 3.660 g |
| `quarter` | ربع سکه | 2.034 g | 1.830 g |
| `gerami` | سکه گرمی | 1.016 g | 0.915 g |

### 2.2 Jewelry categories

`ring`, `necklace`, `bracelet`, `bangle`, `earring`, `set`,
`pendant`, `anklet`, `watch`.

### 2.3 Blog categories

`news`, `education`, `analysis`, `faq`, `announcement`.

## 3. Pricing formulas

All coefficients live in `PricingFormula` (admin-editable). Defaults
come from `settings.DOMAIN_DEFAULTS`.

### 3.1 18k gold

```
buy_per_mg  = (base_18k_rial_per_gram / 1000) × (1 + buy_spread)  × (1 + commission_buy)
sell_per_mg = (base_18k_rial_per_gram / 1000) × (1 − sell_spread) × (1 − commission_sell)
```

`base_18k_rial_per_gram` is the latest TGJU tick (`source_key="gold_18k_750"`).

Defaults: `buy_spread = sell_spread = commission_buy = commission_sell = 0.005`.

### 3.2 999 silver

```
buy_per_mg  = (base_999_rial_per_gram / 1000) × (1 + silver_buy_spread)  × (1 + silver_commission)
sell_per_mg = (base_999_rial_per_gram / 1000) × (1 − silver_sell_spread) × (1 − silver_commission)
```

Defaults: `silver_buy_spread = silver_sell_spread = 0.01`,
`silver_commission = 0.01`.

### 3.3 Mesghal ⟷ gram conversion

```
gram_18k_rial = mesghal × 750 / (4.6083 × 705)
              = mesghal × 0.23080
```

Implemented only if needed in the UI; the platform stores the gram
price directly.

### 3.4 Marketplace product (jewelry / melted / ingot / leather_bracelet)

Implements the formula from `mohem.docx §6`:

```
base        = weight_mg × karat / 750 × per_gram_18k / 1000
wage        = base × manufacturing_fee_pct
margin      = (base + wage) × vendor_margin_pct           ← COMPOUNDED on (base + wage)
accessories = sum(product.metadata["accessory_prices_rial"])
vat         = (wage + margin + accessories) × 0.09       ← jewelry only
final       = base + wage + margin + accessories + vat + fixed_extra_rial
```

* **Margin is compounded on (base + wage)** — not on base alone.
* **Accessories** (stones, leather, etc.) are listed as integer rial
  values in `Product.metadata["accessory_prices_rial"]: list[int]`.
* **VAT** (مالیات بر ارزش افزوده) is 9 % applied to
  *(wage + margin + accessories)*, never to the raw gold value.
* Test: `backend/tests/test_product_pricing.py::test_formula_matches_docx_example`
  verifies the docx-quoted worked example (1 g × 20M toman, 14% wage,
  7% margin → 247,916,400 rial).

### 3.5 Marketplace product (coin)

```
equiv_18k_mg = weight_mg × karat / 750
base         = equiv_18k_mg × per_gram_18k / 1000
final        = base + fixed_extra_rial
```

### 3.6 Marketplace product (melted)

```
equiv_18k_mg = weight_mg × karat / 750
base         = equiv_18k_mg × per_gram_18k / 1000
fee          = base × manufacturing_fee_pct
margin       = base × vendor_margin_pct
final        = base + fee + margin + fixed_extra_rial
```

(Same as jewelry but without VAT.)

### 3.7 Physical delivery fee

```
fee_rial = round(rial_value_of_gold × delivery_processing_fee_pct)
```

Default `delivery_processing_fee_pct = 0.03` (3 %). Minimum delivery
size: `min_physical_delivery_mg = 5000` (5 g). Step: `delivery_lot_step_mg = 1000` (1 g multiples).

### 3.8 Daily yield

```
daily_yield_rial = floor(available_rial × daily_yield_apr / 365)
```

* Calculated nightly at 00:05 over `RialWallet.balance_rial - locked_rial`.
* Skips wallets with available < 10 000 (1 000 toman).
* Default `daily_yield_apr = 0.24` (24 % p.a.).
* Reported in `WalletTransaction(type="yield_payout")`.
* In Terms of Service this is the "پاداش وفاداری" (loyalty reward)
  — not interest.

## 4. Money invariants

Always true. Enforced by DB CHECK constraints AND verified by
`wallet.consistency_tick` every 5 minutes.

1. `RialWallet.balance_rial >= 0`
2. `RialWallet.locked_rial  >= 0`
3. `RialWallet.locked_rial  <= RialWallet.balance_rial`
4. `GoldWallet.balance_mg >= 0`
5. `GoldWallet.silver_balance_mg >= 0`
6. `GoldWallet.locked_mg <= GoldWallet.balance_mg`
7. `GoldWallet.silver_locked_mg <= GoldWallet.silver_balance_mg`
8. `sum(WalletTransaction.rial_amount per user where asset='rial') == RialWallet.balance_rial`
9. `sum(WalletTransaction.mg_amount per (user, asset)) == respective wallet balance`
10. Every `Order` in `paid|processing|completed` has a matching wallet debit OR a successful `PaymentAttempt`.
11. No `WalletTransaction` exists without a linking row in either
   `Order` or `Adjustment`.

When any of these breaks → `audit.consistency.violation` (critical),
PagerDuty page, optional `SYSTEM_HALT`.

## 5. State machines

See [`OBSERVABILITY.md §3`](OBSERVABILITY.md#3-the-state-machine). One-paragraph summary of each:

* **`order`** — `draft → awaiting_payment → paid → processing → completed`,
  with branches to `expired`, `cancelled`, `failed → refunded`.
  A 30-min timer (`payment_deadline`) controls `awaiting_payment → expired`.
* **`kyc`** — `empty → submitted → under_review → {approved | rejected | requires_more → submitted}`.
* **`delivery`** — `pending → approved → minting → shipped → delivered`,
  with `cancelled` from the first three.
* **`vendor`** — `applied → approved ↔ suspended`, with `rejected` from
  `applied`.
* **`payment_attempt`** — `pending → redirected → {succeeded | failed | cancelled | expired}`.

## 6. Event taxonomy

See [`OBSERVABILITY.md §2.2`](OBSERVABILITY.md#22-event-catalogue) for
the complete catalogue of 76 event kinds across 5 categories. Every
event is registered in `apps/audit/catalogue.py` and is queryable in
Kibana via `event.kind:<kind>`.

## 7. Trust + KYC

Tier progression:
1. **Phone-verified** — can browse, see prices.
2. **KYC-submitted** — same access; in admin queue.
3. **KYC-approved (`is_verified`)** — full access (topup, trade,
   transfer, delivery).

The DRF permission `IsKYCVerified` gates every money endpoint:

```python
class IsKYCVerified(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and u.is_verified and not u.is_frozen
```

## 8. AML rules

`security.aml_tick` runs every 10 minutes (`apps/security/aml.py`):

* Sums rial deposits + withdrawals per user over the trailing 24 h.
* If `|sum| ≥ aml_threshold_rial` (default 10 B IRR = 1 B toman), the
  `apps.security.risk` scorer fires:
  * `score ≥ 50` → action `review` → `aml.threshold.high` (warning).
  * `score ≥ 100` → action `block` → opens an AML case.

Other rules (live in the risk engine):
* `new_iban` flag → +30
* `velocity_outlier` → +25
* `sanctions_hit` → +100 (always blocks)

## 9. Roles & RBAC

Declared in `apps/accounts/permissions.py` and enforced at the DRF
viewset boundary AND inside the state machine.

| Role | Implied by | Capabilities |
|------|------------|--------------|
| `user` | `is_authenticated` | browse + place quotes (until KYC done) |
| `kyc-verified user` | `+ is_verified` | trade, transfer, delivery, marketplace |
| `vendor` | `+ is_vendor` | vendor panel + product CRUD |
| `admin` | `is_staff` | admin panel + actions |
| `superadmin` | `is_superuser` | everything (incl. Django admin) |

## 10. Tenancy

`tenant_id = "default"` is the standard column on every aggregate
(`User`, `Order`, `Product`, `Vendor`, `RialWallet`). For roadmap #14
(white-label B2B API), a single config flip routes a partner's traffic
to its own `tenant_id` and queryset filtering keeps the data
partitioned.

## 11. Numbers people often ask about

| Question | Answer |
|----------|--------|
| Minimum buy / sell | 1 mg |
| Minimum delivery | 5000 mg (5 g) — multiples of 1 g |
| Bar denominations | 1 g, 2 g, 5 g, 10 g |
| Minimum withdraw | 100 000 rial (10 000 toman) |
| Withdraw fee | 20 000 rial (configurable) |
| Cart price-lock | 6 minutes (per mohem.docx §7) |
| Payment deadline (after gateway redirect) | 20 minutes (per mohem.docx §8) |
| Quote validity | 6 minutes (matches cart lock) |
| OTP TTL | 120 seconds |
| Max OTP attempts | 5 / window |
| Daily yield | 24 % APR / 365 (default) |
| Vendor commission | 2 % (per-vendor configurable) |
| VAT on jewelry | 9 % on (fee + margin) |
| AML threshold | 10 B IRR / 24 h |
