"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { useMe } from "@/hooks/useMe";
import type { Order } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

const STATE_TONE: Record<string, "primary" | "success" | "warning" | "danger" | "neutral"> = {
  awaiting_payment: "warning",
  paid: "primary",
  processing: "primary",
  completed: "success",
  expired: "neutral",
  cancelled: "neutral",
  refunded: "neutral",
  failed: "danger",
};

const STATE_LABEL: Record<string, string> = {
  draft: "پیش‌نویس",
  awaiting_payment: "در انتظار پرداخت",
  paid: "پرداخت شد",
  processing: "در حال پردازش",
  completed: "تکمیل شد",
  expired: "منقضی شد",
  cancelled: "لغو شد",
  refunded: "بازگشت داده شد",
  failed: "ناموفق",
};

const KIND_LABEL: Record<string, string> = {
  buy_gold: "خرید طلا",
  sell_gold: "فروش طلا",
  buy_silver: "خرید نقره",
  sell_silver: "فروش نقره",
  marketplace: "خرید از فروشنده",
  wallet_topup: "شارژ کیف پول",
};

export default function OrdersPage() {
  const me = useMe();
  const [list, setList] = useState<Order[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (me.status !== "authenticated") return;
    fetch("/api/v1/orders", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((r) => setList(r.results ?? []))
      .catch((e: Error) => setErr(e.message));
  }, [me]);

  if (me.status === "loading") {
    return <Loading />;
  }
  if (me.status === "anonymous") {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 max-w-md text-center space-y-3">
          <div className="text-6xl">📦</div>
          <h1 className="text-xl font-bold">برای مشاهده سفارش‌ها وارد شوید</h1>
          <Link
            href="/login?next=/orders"
            className="inline-block px-6 py-3 rounded-xl bg-[var(--color-primary)] text-white"
          >
            ورود
          </Link>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        <h1 className="text-2xl font-bold mb-4">سفارش‌های من</h1>
        {err && (
          <Card className="mb-3">
            <CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody>
          </Card>
        )}
        {list.length === 0 ? (
          <Card>
            <CardBody className="text-sm text-[var(--color-text-muted)] text-center py-8">
              هنوز سفارشی ثبت نکرده‌اید.{" "}
              <Link href="/trade/buy" className="text-[var(--color-primary)]">
                همین حالا شروع کنید ›
              </Link>
            </CardBody>
          </Card>
        ) : (
          <div className="space-y-3">
            {list.map((o) => (
              <Link key={o.id} href={`/orders/${o.id}`} className="block">
                <Card className="hover:shadow-[var(--shadow-card-hover)] transition">
                  <CardBody className="flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm">
                        {KIND_LABEL[o.kind] ?? o.kind}
                      </p>
                      <p className="text-xs text-[var(--color-text-muted)] mt-1">
                        {toPersianNumber(o.order_number)} ·{" "}
                        {new Date(o.created_at).toLocaleDateString("fa-IR")}
                      </p>
                    </div>
                    <div className="text-left">
                      <Badge tone={STATE_TONE[o.state] ?? "neutral"}>
                        {STATE_LABEL[o.state] ?? o.state}
                      </Badge>
                      {o.mg_amount > 0 && (
                        <p className="text-sm mt-1">{formatMg(o.mg_amount)}</p>
                      )}
                      <p className="text-xs text-[var(--color-text-muted)]">
                        {formatRial(o.rial_amount)}
                      </p>
                    </div>
                  </CardBody>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}

function Loading() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-20 text-center text-sm text-[var(--color-text-muted)]">
        در حال بارگذاری…
      </main>
      <Footer />
    </>
  );
}
