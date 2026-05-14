import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
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

export default async function AdminHomePage() {
  let kpi: KPI | null = null;
  try {
    kpi = await api<KPI>("/admin/kpi", { cache: "no-store" });
  } catch {
    kpi = null;
  }
  const tiles = [
    ["کاربران", toPersianNumber(kpi?.users_total ?? 0)],
    ["کاربران احرازشده", toPersianNumber(kpi?.users_verified ?? 0)],
    ["فروشندگان فعال", toPersianNumber(kpi?.vendors_total ?? 0)],
    ["سفارش‌ها", toPersianNumber(kpi?.orders_total ?? 0)],
    ["جمع ریال", formatRial(kpi?.rial_total ?? 0)],
    ["ریال قفل‌شده", formatRial(kpi?.rial_locked ?? 0)],
    ["جمع طلا", formatMg(kpi?.gold_total_mg ?? 0)],
    ["جمع نقره", formatMg(kpi?.silver_total_mg ?? 0)],
  ] as const;
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold mb-4">پنل مدیریت</h1>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {tiles.map(([t, v]) => (
            <Card key={t}>
              <CardBody>
                <p className="text-xs text-[var(--color-text-muted)]">{t}</p>
                <p className="text-lg font-bold mt-1">{v}</p>
              </CardBody>
            </Card>
          ))}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
          {[
            ["KYC", "/admin/kyc"],
            ["کاربران", "/admin/users"],
            ["فروشندگان", "/admin/vendors"],
            ["سفارش‌ها", "/admin/orders"],
            ["پرداخت‌ها", "/admin/payments"],
            ["تحویل‌ها", "/admin/delivery"],
            ["فرمول‌ها", "/admin/formulas"],
            ["تسویه‌ها", "/admin/settlements"],
            ["لاگ", "/admin/audit"],
          ].map(([t, h]) => (
            <Link key={h} href={h}>
              <Card className="hover:shadow-[var(--shadow-card-hover)] transition">
                <CardBody className="text-center text-sm">{t}</CardBody>
              </Card>
            </Link>
          ))}
        </div>
      </main>
      <Footer />
    </>
  );
}
