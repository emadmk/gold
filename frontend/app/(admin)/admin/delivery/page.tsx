"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, toPersianNumber } from "@/lib/format";

type Delivery = {
  id: string;
  user: string;
  asset: string;
  requested_mg: number;
  state: string;
  tracking_code: string;
  recipient_name: string;
  recipient_phone: string;
  shipping_address: string;
  created_at: string;
};

const TONE: Record<string, "primary" | "success" | "warning" | "danger" | "neutral"> = {
  pending: "warning",
  approved: "primary",
  minting: "primary",
  shipped: "primary",
  delivered: "success",
  cancelled: "neutral",
};

export default function AdminDeliveryPage() {
  const [list, setList] = useState<Delivery[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    try {
      const r = await api<{ results: Delivery[] }>("/admin/delivery");
      setList(r.results ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function act(d: Delivery, action: string) {
    const body: Record<string, string> = {};
    if (action === "ship") {
      const code = prompt("کد رهگیری پست/تیپاکس:");
      if (!code) return;
      body.tracking_code = code;
    }
    if (action === "cancel" && !confirm(`واقعاً لغو شود؟`)) return;
    await api(`/admin/delivery/${d.id}/${action}`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    load();
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">صف تحویل فیزیکی</h1>
      <p className="text-xs text-[var(--color-text-muted)]">
        فقط درخواست‌های فعال (به‌جز تحویل‌شده‌ها) نشان داده می‌شوند.
      </p>
      {err && <Card><CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody></Card>}

      {list.length === 0 ? (
        <Card><CardBody className="text-center text-sm py-8 text-[var(--color-text-muted)]">
          صف خالی است.
        </CardBody></Card>
      ) : (
        list.map((d) => (
          <Card key={d.id}>
            <CardBody className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-3 items-start">
              <div className="text-sm space-y-1">
                <p className="font-bold">
                  {d.recipient_name} ·{" "}
                  <span dir="ltr">{toPersianNumber(d.recipient_phone)}</span>
                </p>
                <p className="text-xs">{d.shipping_address}</p>
                <p className="text-xs text-[var(--color-text-muted)]">
                  {formatMg(d.requested_mg)} ({d.asset}) ·{" "}
                  {new Date(d.created_at).toLocaleString("fa-IR")}
                </p>
                {d.tracking_code && (
                  <p className="text-xs">
                    کد رهگیری: <span dir="ltr" className="font-mono">{d.tracking_code}</span>
                  </p>
                )}
              </div>
              <div className="flex flex-col items-end gap-2">
                <Badge tone={TONE[d.state] ?? "neutral"}>{d.state}</Badge>
                <div className="flex flex-wrap gap-1 justify-end">
                  {d.state === "pending" && <Button size="sm" onClick={() => act(d, "approve")}>تأیید</Button>}
                  {d.state === "approved" && <Button size="sm" onClick={() => act(d, "mint")}>ضرب</Button>}
                  {d.state === "minting" && <Button size="sm" onClick={() => act(d, "ship")}>ارسال</Button>}
                  {d.state === "shipped" && <Button size="sm" onClick={() => act(d, "deliver")}>تحویل</Button>}
                  {!["delivered", "cancelled"].includes(d.state) && (
                    <Button size="sm" variant="danger" onClick={() => act(d, "cancel")}>لغو</Button>
                  )}
                </div>
              </div>
            </CardBody>
          </Card>
        ))
      )}
    </div>
  );
}
