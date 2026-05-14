# `apps.jewelry` — Jewelry-category taxonomy

A tiny app whose only job is to hold the **standard** Persian
retail-jewelry category tree. Real jewelry products live in
`apps.marketplace.Product(category="jewelry")` and reference these
categories via `Product.metadata["jewelry_category"]` (or a future FK
when we need a constraint).

## Model

`JewelryCategory(code, title_fa, parent, icon, sort)`.

Seeded by `seed_dev`:

| `code` | name (fa) |
|--------|-----------|
| `ring` | انگشتر |
| `necklace` | گردنبند |
| `bracelet` | دستبند |
| `bangle` | النگو |
| `earring` | گوشواره |
| `set` | سرویس / نیم‌ست |
| `pendant` | آویز |
| `anklet` | پابند |
| `watch` | ساعت |

## Why a separate app?

So that future moves — sub-categories, locale-specific renames,
SEO-friendly URLs — don't have to touch the heavy `marketplace`
schema. It's also a clean home for jewelry-specific calculators
(e.g. design-aware pricing) when those land.
