"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatRial, toPersianNumber } from "@/lib/format";

type Settlement = {
  id: string;
  period_start: string;
  period_end: string;
  gross_rial: number;
  commission_rial: number;
  net_rial: number;
  orders_count: number;
  paid_at: string | null;
};

export default function VendorSettlementsPage() {
  const [list, setList] = useState<Settlement[]>([]);
  useEffect(() => {
    api<{ results: Settlement[] }>("/vendor/settlements")
      .then((r) => setList(r.results ?? []))
      .catch(() => null);
  }, []);

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl">
        <h1 className="text-2xl font-bold mb-4">تسویه‌های روزانه</h1>
        {list.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">
            هنوز تسویه‌ای ثبت نشده است.
          </p>
        ) : (
          list.map((s) => (
            <Card key={s.id} className="mb-2">
              <CardBody className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                <div>
                  <p className="text-xs text-[var(--color-text-muted)]">دوره</p>
                  <p>{new Date(s.period_end).toLocaleDateString("fa-IR")}</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--color-text-muted)]">سفارش‌ها</p>
                  <p>{toPersianNumber(s.orders_count)}</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--color-text-muted)]">ناخالص</p>
                  <p>{formatRial(s.gross_rial)}</p>
                </div>
                <div>
                  <p className="text-xs text-[var(--color-text-muted)]">واریز</p>
                  <p className="font-bold text-[var(--color-success)]">
                    {formatRial(s.net_rial)}
                  </p>
                </div>
              </CardBody>
            </Card>
          ))
        )}
      </main>
      <Footer />
    </>
  );
}
