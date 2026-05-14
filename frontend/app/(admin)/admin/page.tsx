"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

type KPI = {
  users_total: number;
  users_verified: number;
  vendors_total: number;
  orders_total: number;
  rial_locked: number;
  rial_total: number;
  gold_total_mg: number;
  silver_total_mg: number;
};

export default function AdminHomePage() {
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<KPI>("/admin/kpi")
      .then(setKpi)
      .catch((e) => setErr((e as Error).message));
  }, []);

  const tiles: Array<[string, string]> = [
    ["کاربران کل", toPersianNumber(kpi?.users_total ?? 0)],
    ["کاربران احرازشده", toPersianNumber(kpi?.users_verified ?? 0)],
    ["فروشندگان فعال", toPersianNumber(kpi?.vendors_total ?? 0)],
    ["سفارش‌های کل", toPersianNumber(kpi?.orders_total ?? 0)],
    ["جمع ریال", formatRial(kpi?.rial_total ?? 0)],
    ["ریال قفل‌شده", formatRial(kpi?.rial_locked ?? 0)],
    ["جمع طلا", formatMg(kpi?.gold_total_mg ?? 0)],
    ["جمع نقره", formatMg(kpi?.silver_total_mg ?? 0)],
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">داشبورد مدیریت</h1>
        <p className="text-xs text-[var(--color-text-muted)]">
          آخرین به‌روزرسانی: {new Date().toLocaleString("fa-IR")}
        </p>
      </div>

      {err && (
        <Card>
          <CardBody className="text-sm text-[var(--color-danger)]">
            {err}
          </CardBody>
        </Card>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {tiles.map(([t, v]) => (
          <Card key={t}>
            <CardBody>
              <p className="text-xs text-[var(--color-text-muted)]">{t}</p>
              <p className="text-lg font-bold mt-1">{kpi ? v : "…"}</p>
            </CardBody>
          </Card>
        ))}
      </div>

      <Card>
        <CardBody>
          <h2 className="font-bold mb-3">میان‌برهای پرکاربرد</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            <Link
              href="/admin/kyc"
              className="rounded-lg bg-[var(--color-warning-light)] text-amber-800 px-3 py-2 text-center hover:opacity-80"
            >
              صف KYC
            </Link>
            <Link
              href="/admin/vendors"
              className="rounded-lg bg-[var(--color-primary-light)] text-[var(--color-primary-hover)] px-3 py-2 text-center hover:opacity-80"
            >
              فروشندگان منتظر
            </Link>
            <Link
              href="/admin/delivery"
              className="rounded-lg bg-[var(--color-success-light)] text-[var(--color-success)] px-3 py-2 text-center hover:opacity-80"
            >
              صف تحویل
            </Link>
            <Link
              href="/admin/formulas"
              className="rounded-lg bg-[var(--color-gold-light)] text-[var(--color-gold-deep)] px-3 py-2 text-center hover:opacity-80"
            >
              فرمول‌ها
            </Link>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
