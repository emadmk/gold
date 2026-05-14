"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
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
  async function load() {
    const r = await api<{ results: Delivery[] }>("/admin/delivery");
    setList(r.results ?? []);
  }
  useEffect(() => {
    load().catch(() => null);
  }, []);

  async function act(d: Delivery, action: string) {
    const body: Record<string, string> = {};
    if (action === "ship") {
      const code = prompt("کد رهگیری پست/تیپاکس:") ?? "";
      if (!code) return;
      body.tracking_code = code;
    }
    await api(`/admin/delivery/${d.id}/${action}`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    load();
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-5xl">
        <h1 className="text-2xl font-bold mb-4">صف تحویل فیزیکی</h1>
        {list.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">صف خالی است.</p>
        ) : (
          list.map((d) => (
            <Card key={d.id} className="mb-2">
              <CardBody className="flex justify-between items-start gap-3">
                <div className="flex-1 text-sm">
                  <p className="font-bold">
                    {d.recipient_name} ·{" "}
                    <span dir="ltr">{toPersianNumber(d.recipient_phone)}</span>
                  </p>
                  <p className="text-xs">{d.shipping_address}</p>
                  <p className="text-xs text-[var(--color-text-muted)] mt-1">
                    {formatMg(d.requested_mg)} ·{" "}
                    {new Date(d.created_at).toLocaleString("fa-IR")}
                  </p>
                  {d.tracking_code && (
                    <p className="text-xs mt-1">
                      کد رهگیری: <span dir="ltr">{d.tracking_code}</span>
                    </p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-1">
                  <Badge tone={TONE[d.state] ?? "neutral"}>{d.state}</Badge>
                  <div className="flex gap-1">
                    {d.state === "pending" && (
                      <Button size="sm" onClick={() => act(d, "approve")}>تأیید</Button>
                    )}
                    {d.state === "approved" && (
                      <Button size="sm" onClick={() => act(d, "mint")}>ضرب</Button>
                    )}
                    {d.state === "minting" && (
                      <Button size="sm" onClick={() => act(d, "ship")}>ارسال</Button>
                    )}
                    {d.state === "shipped" && (
                      <Button size="sm" onClick={() => act(d, "deliver")}>تحویل</Button>
                    )}
                    {!["delivered", "cancelled"].includes(d.state) && (
                      <Button size="sm" variant="danger" onClick={() => act(d, "cancel")}>
                        لغو
                      </Button>
                    )}
                  </div>
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
