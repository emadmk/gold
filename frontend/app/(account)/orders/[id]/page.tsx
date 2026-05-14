"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { useOrderCountdown } from "@/hooks/useOrderCountdown";
import { api, type Order } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

export default function OrderDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const cd = useOrderCountdown(order?.payment_deadline ?? null);

  async function load() {
    try {
      setOrder(await api<Order>(`/orders/${params.id}`));
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, [params.id]);

  async function cancel() {
    try {
      await api(`/orders/${params.id}/cancel`, { method: "POST" });
      load();
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-2xl space-y-4">
        {err && <Alert kind="danger">{err}</Alert>}
        {!order && !err ? (
          <p>در حال بارگذاری…</p>
        ) : order ? (
          <>
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">
                سفارش {toPersianNumber(order.order_number)}
              </h1>
              <Badge tone={order.state === "completed" ? "success" : "primary"}>
                {order.state}
              </Badge>
            </div>

            {order.state === "awaiting_payment" && !cd.expired ? (
              <Alert kind="warning">
                در انتظار پرداخت — {cd.label} باقی‌مانده.
              </Alert>
            ) : null}

            <Card>
              <CardHeader><h2 className="font-bold">جزئیات</h2></CardHeader>
              <CardBody className="space-y-1 text-sm">
                <div className="flex justify-between"><span>نوع</span><span>{order.kind}</span></div>
                {order.mg_amount ? (
                  <div className="flex justify-between"><span>مقدار</span><span>{formatMg(order.mg_amount)}</span></div>
                ) : null}
                {order.price_per_mg_rial ? (
                  <div className="flex justify-between">
                    <span>نرخ هر mg</span>
                    <span dir="ltr">{toPersianNumber(Math.floor(order.price_per_mg_rial/10).toLocaleString("fa-IR"))} تومان</span>
                  </div>
                ) : null}
                <div className="flex justify-between font-bold"><span>مبلغ کل</span><span>{formatRial(order.rial_amount)}</span></div>
                {order.paid_at ? (
                  <div className="flex justify-between">
                    <span>تاریخ پرداخت</span>
                    <span>{new Date(order.paid_at).toLocaleString("fa-IR")}</span>
                  </div>
                ) : null}
              </CardBody>
            </Card>

            <div className="flex gap-2">
              {order.state === "awaiting_payment" && !cd.expired ? (
                <Button variant="danger" onClick={cancel}>لغو سفارش</Button>
              ) : null}
              <Button variant="ghost" onClick={() => router.push("/orders")}>
                بازگشت
              </Button>
              <a href={`/api/v1/orders/${order.id}/invoice`} target="_blank" rel="noopener">
                <Button variant="gold">دانلود فاکتور PDF</Button>
              </a>
            </div>
          </>
        ) : null}
      </main>
      <Footer />
    </>
  );
}
