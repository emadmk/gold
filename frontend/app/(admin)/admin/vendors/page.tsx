"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { toPersianNumber } from "@/lib/format";

type Vendor = {
  id: string;
  shop_name: string;
  shop_slug: string;
  state: string;
  rating: number;
  total_sales: number;
  city: string;
};

const STATE_TONE: Record<string, "success" | "warning" | "danger" | "neutral"> = {
  applied: "warning",
  approved: "success",
  suspended: "danger",
  rejected: "neutral",
};

export default function AdminVendorsPage() {
  const [list, setList] = useState<Vendor[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    try {
      const r = await api<{ results: Vendor[] }>("/admin/vendors-list");
      setList(r.results ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function approve(v: Vendor) {
    if (!confirm(`فروشگاه «${v.shop_name}» تأیید شود؟`)) return;
    await api(`/admin/vendors/${v.id}/approve`, { method: "POST" });
    load();
  }
  async function suspend(v: Vendor) {
    const reason = prompt(`دلیل تعلیق «${v.shop_name}»؟`);
    if (reason == null) return;
    await api(`/admin/vendors/${v.id}/suspend`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
    load();
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">فروشندگان</h1>
      {err && <Card><CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody></Card>}

      {list.length === 0 ? (
        <Card><CardBody className="text-center text-sm py-8 text-[var(--color-text-muted)]">
          هنوز فروشنده‌ای ثبت‌نام نکرده است.
        </CardBody></Card>
      ) : (
        <div className="space-y-2">
          {list.map((v) => (
            <Card key={v.id}>
              <CardBody className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-2 items-center">
                <div className="text-sm space-y-1">
                  <p className="font-bold">{v.shop_name}</p>
                  <p className="text-xs" dir="ltr">{v.shop_slug}</p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    {v.city || "—"} · امتیاز {toPersianNumber(v.rating)} ·{" "}
                    {toPersianNumber(v.total_sales)} فروش
                  </p>
                </div>
                <div className="flex flex-col gap-1 items-end">
                  <Badge tone={STATE_TONE[v.state] ?? "neutral"}>{v.state}</Badge>
                  <div className="flex gap-2">
                    {v.state === "applied" && (
                      <Button size="sm" onClick={() => approve(v)}>تأیید</Button>
                    )}
                    {v.state === "approved" && (
                      <Button size="sm" variant="danger" onClick={() => suspend(v)}>تعلیق</Button>
                    )}
                    {v.state === "suspended" && (
                      <Button size="sm" onClick={() => approve(v)}>بازفعال</Button>
                    )}
                  </div>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
