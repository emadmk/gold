"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatRial, toPersianNumber } from "@/lib/format";

type Settlement = {
  id: string;
  vendor: string;
  period_start: string;
  period_end: string;
  gross_rial: number;
  commission_rial: number;
  net_rial: number;
  orders_count: number;
  paid_at: string | null;
  notes: string;
};

export default function AdminSettlementsPage() {
  const [list, setList] = useState<Settlement[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<{ results: Settlement[] }>("/admin/settlements")
      .then((r) => setList(r.results ?? []))
      .catch((e) => setErr((e as Error).message));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">تسویه‌های فروشندگان</h1>
      <p className="text-xs text-[var(--color-text-muted)]">
        هر شب ساعت ۰۱:۰۰ سفارش‌های تکمیل‌شده‌ی روز جمع‌بندی شده و پس از کسر
        کمیسیون به کیف پول ریالی فروشنده واریز می‌گردد.
      </p>

      {err && <Card><CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody></Card>}

      {list.length === 0 ? (
        <Card>
          <CardBody className="text-sm text-[var(--color-text-muted)] text-center py-8">
            هنوز تسویه‌ای ثبت نشده است.
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-2">
          {list.map((s) => (
            <Card key={s.id}>
              <CardBody className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs items-center">
                <span className="font-mono" dir="ltr">{s.vendor.slice(0, 8)}…</span>
                <span>
                  {new Date(s.period_end).toLocaleDateString("fa-IR")}
                  <span className="text-[var(--color-text-muted)]">
                    {" "}
                    · {toPersianNumber(s.orders_count)} سفارش
                  </span>
                </span>
                <span>
                  <span className="text-[var(--color-text-muted)]">ناخالص:</span>{" "}
                  {formatRial(s.gross_rial)}
                </span>
                <span>
                  <span className="text-[var(--color-text-muted)]">کمیسیون:</span>{" "}
                  {formatRial(s.commission_rial)}
                </span>
                <div className="justify-self-end space-y-1 text-end">
                  <p className="font-bold text-[var(--color-success)] text-sm">
                    {formatRial(s.net_rial)}
                  </p>
                  <Badge tone={s.paid_at ? "success" : "warning"}>
                    {s.paid_at ? "پرداخت شد" : "در انتظار"}
                  </Badge>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
