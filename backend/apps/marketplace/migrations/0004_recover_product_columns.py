"""
Idempotent recovery migration.

When the original `0003_cart_cartitem_discountcode_shippingaddress_and_more`
migration was applied on some early development databases, the file's
content was different (the marketplace.Product was extended with
`brand`, `sub_category_code`, `discount_pct`, `shipping_cost_rial`,
`shipping_methods`, `views`, `sold_count` only later, in the same
filename). Django's migration framework keys off the FILENAME alone,
so when the file was edited in place those databases ended up with
`marketplace_product` still missing those columns even though
`django_migrations` says 0003 is applied.

This migration checks the live schema with the information_schema /
PRAGMA APIs and adds the columns only if they are missing. Running it
on a healthy database (where 0003 created everything) is a no-op.
"""
from __future__ import annotations

from django.db import migrations


def _column_exists(cursor, vendor: str, table: str, column: str) -> bool:
    if vendor == "postgresql":
        cursor.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name=%s AND column_name=%s",
            [table, column],
        )
        return cursor.fetchone() is not None
    # SQLite
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def _table_exists(cursor, vendor: str, table: str) -> bool:
    if vendor == "postgresql":
        cursor.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name=%s",
            [table],
        )
        return cursor.fetchone() is not None
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", [table]
    )
    return cursor.fetchone() is not None


def ensure_schema(apps, schema_editor):
    conn = schema_editor.connection
    vendor = conn.vendor
    if vendor not in ("postgresql", "sqlite"):
        # Unknown backend; leave alone.
        return

    cursor = conn.cursor()

    # ---- 1. Product columns added in 0003 ----
    product_columns = [
        ("brand", "VARCHAR(80) NOT NULL DEFAULT ''"),
        ("sub_category_code", "VARCHAR(40) NOT NULL DEFAULT ''"),
        ("discount_pct", "NUMERIC(5,4) NOT NULL DEFAULT 0"),
        ("shipping_cost_rial", "BIGINT NOT NULL DEFAULT 0"),
        ("views", "INTEGER NOT NULL DEFAULT 0"),
        ("sold_count", "INTEGER NOT NULL DEFAULT 0"),
    ]
    for name, sql_type in product_columns:
        if not _column_exists(cursor, vendor, "marketplace_product", name):
            cursor.execute(
                f"ALTER TABLE marketplace_product ADD COLUMN {name} {sql_type}"
            )

    # shipping_methods is a JSONField — type differs per backend.
    if not _column_exists(cursor, vendor, "marketplace_product", "shipping_methods"):
        if vendor == "postgresql":
            cursor.execute(
                "ALTER TABLE marketplace_product "
                "ADD COLUMN shipping_methods JSONB NOT NULL DEFAULT '[]'::jsonb"
            )
        else:
            cursor.execute(
                "ALTER TABLE marketplace_product "
                "ADD COLUMN shipping_methods TEXT NOT NULL DEFAULT '[]'"
            )

    # ---- 2. Product.category width — 0003 widened it from 10 to 20 ----
    # (PostgreSQL only; SQLite has dynamic typing.)
    if vendor == "postgresql":
        try:
            cursor.execute(
                "ALTER TABLE marketplace_product "
                "ALTER COLUMN category TYPE VARCHAR(20)"
            )
        except Exception:  # noqa: BLE001 — already widened
            pass


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0003_cart_cartitem_discountcode_shippingaddress_and_more"),
    ]

    operations = [
        migrations.RunPython(ensure_schema, migrations.RunPython.noop),
    ]
