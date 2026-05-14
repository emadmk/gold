import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api, type Order } from "@/lib/api";
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

export default async function OrdersPage() {
  let orders: { results: Order[] } | null = null;
  try {
    orders = await api<{ results: Order[] }>("/orders", { cache: "no-store" });
  } catch {
    orders = null;
  }
  const list = orders?.results ?? [];

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        <h1 className="text-2xl font-bold mb-4">سفارش‌های من</h1>
        {list.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">
            هنوز سفارشی ثبت نکرده‌اید.
          </p>
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
                      <p className="text-sm mt-1">
                        {o.mg_amount ? formatMg(o.mg_amount) : ""}
                      </p>
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
