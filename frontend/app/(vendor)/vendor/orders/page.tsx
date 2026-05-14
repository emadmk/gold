"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api, type Order } from "@/lib/api";
import { formatRial, toPersianNumber } from "@/lib/format";

export default function VendorOrdersPage() {
  const [list, setList] = useState<Order[]>([]);
  useEffect(() => {
    api<{ results: Order[] }>("/vendor/orders").then((r) => setList(r.results ?? []))
      .catch(() => null);
  }, []);

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl">
        <h1 className="text-2xl font-bold mb-4">سفارش‌های دریافت‌شده</h1>
        {list.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">
            هنوز سفارشی برای فروشگاه شما ثبت نشده است.
          </p>
        ) : (
          list.map((o) => (
            <Card key={o.id} className="mb-2">
              <CardBody className="flex justify-between items-center">
                <div>
                  <p className="font-bold">{toPersianNumber(o.order_number)}</p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    {new Date(o.created_at).toLocaleString("fa-IR")}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <Badge tone={o.state === "completed" ? "success" : "primary"}>{o.state}</Badge>
                  <span className="text-sm">{formatRial(o.rial_amount)}</span>
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
