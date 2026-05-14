# `apps.admin_panel` — Admin aggregations + branding

Two things live here:

1. **Persian branding** of `django.contrib.admin` — `admin.py` sets
   `site_header`, `site_title`, `index_title`.
2. **JSON aggregation endpoints** that power the Next.js admin pages
   under `/admin/*` (separate from Django's own admin UI).

## Endpoints

```
GET /api/v1/admin/kpi                      ← dashboard tiles
GET /api/v1/admin/kyc-queue
GET /api/v1/admin/users
POST /api/v1/admin/users/<id>/freeze       /unfreeze
GET /api/v1/admin/vendors-list
GET /api/v1/admin/orders
GET /api/v1/admin/payments
GET /api/v1/admin/delivery
POST /api/v1/admin/delivery/<id>/<action>  ← approve/mint/ship/deliver/cancel
GET /api/v1/admin/formulas                  PUT /api/v1/admin/formulas
GET /api/v1/admin/settlements
GET /api/v1/admin/audit-log
```

All gated by `IsAuthenticated + IsAdminRole`.

## Why two admins?

* **Django admin** (`/admin/`) — record-level CRUD, audit log, full
  fieldsets, bulk actions. Used by superusers and operations.
* **Next.js admin** (`/admin/*` on the frontend) — friendlier
  dashboards for KYC reviewers, finance, support. Both speak to the
  same database, but the Next.js admin exposes pre-aggregated views
  via this app's endpoints.

## Branding

The Django admin renders in Persian:

```
پنل مدیریت KeyhanGold
خانه
```

Set up in `admin_panel/admin.py` (loaded by `AdminPanelConfig.ready`).
