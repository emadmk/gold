"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatRial } from "@/lib/format";

type Payment = {
  id: string;
  order: string;
  gateway: string;
  amount_rial: number;
  state: string;
  authority: string;
  ref_id: string;
  card_pan_masked: string;
  created_at: string;
};

const TONE: Record<string, "primary" | "success" | "warning" | "danger" | "neutral"> = {
  pending: "neutral",
  redirected: "primary",
  succeeded: "success",
  failed: "danger",
  cancelled: "neutral",
  expired: "warning",
};

const GATEWAY_LABEL: Record<string, string> = {
  zarinpal: "زرین‌پال",
  idpay: "آیدی‌پی",
  payping: "پی‌پینگ",
  snappay: "اسنپ‌پی",
  gsmpay: "جی‌اس‌ام‌پی",
};

export default function AdminPaymentsPage() {
  const [list, setList] = useState<Payment[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<{ results: Payment[] }>("/admin/payments")
      .then((r) => setList(r.results ?? []))
      .catch((e) => setErr((e as Error).message));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">تراکنش‌های درگاه</h1>
      {err && <Card><CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody></Card>}

      {list.length === 0 ? (
        <Card>
          <CardBody className="text-sm text-[var(--color-text-muted)] text-center py-8">
            هیچ تراکنشی ثبت نشده است.
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-2">
          {list.map((p) => (
            <Card key={p.id}>
              <CardBody className="grid grid-cols-2 md:grid-cols-6 gap-2 text-xs items-center">
                <span>{GATEWAY_LABEL[p.gateway] ?? p.gateway}</span>
                <Badge tone={TONE[p.state] ?? "neutral"}>{p.state}</Badge>
                <span className="font-bold text-sm">{formatRial(p.amount_rial)}</span>
                <span dir="ltr" className="truncate" title={p.ref_id}>{p.ref_id || "—"}</span>
                <span dir="ltr" className="truncate">{p.card_pan_masked || "—"}</span>
                <span className="text-[var(--color-text-muted)]">
                  {new Date(p.created_at).toLocaleString("fa-IR")}
                </span>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
