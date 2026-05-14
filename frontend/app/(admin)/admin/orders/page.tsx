"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api, type Order } from "@/lib/api";
import { formatRial, toPersianNumber } from "@/lib/format";

const STATE_TONE: Record<string, "primary" | "success" | "warning" | "danger" | "neutral"> = {
  draft: "neutral",
  awaiting_payment: "warning",
  paid: "primary",
  processing: "primary",
  completed: "success",
  expired: "neutral",
  cancelled: "neutral",
  refunded: "neutral",
  failed: "danger",
};

const KIND_LABEL: Record<string, string> = {
  buy_gold: "خرید طلا",
  sell_gold: "فروش طلا",
  buy_silver: "خرید نقره",
  sell_silver: "فروش نقره",
  marketplace: "مارکت‌پلیس",
  wallet_topup: "شارژ کیف",
};

export default function AdminOrdersPage() {
  const [list, setList] = useState<Order[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("");

  async function load() {
    try {
      const r = await api<{ results: Order[] }>("/admin/orders");
      setList(r.results ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  const shown = filter ? list.filter((o) => o.state === filter) : list;
  const counts = list.reduce<Record<string, number>>((m, o) => {
    m[o.state] = (m[o.state] ?? 0) + 1;
    return m;
  }, {});

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">همه سفارش‌ها</h1>
      {err && <Card><CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody></Card>}

      <div className="flex flex-wrap gap-2 text-xs">
        <button
          onClick={() => setFilter("")}
          className={`px-3 py-1 rounded-full border ${
            !filter ? "bg-[var(--color-primary)] text-white" : "bg-white"
          }`}
        >
          همه ({toPersianNumber(list.length)})
        </button>
        {Object.entries(counts).map(([s, n]) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded-full border ${
              filter === s ? "bg-[var(--color-primary)] text-white" : "bg-white"
            }`}
          >
            {s} ({toPersianNumber(n)})
          </button>
        ))}
      </div>

      {shown.length === 0 ? (
        <Card>
          <CardBody className="text-sm text-[var(--color-text-muted)] text-center py-8">
            موردی یافت نشد.
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-2">
          {shown.map((o) => (
            <Card key={o.id}>
              <CardBody className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm items-center">
                <span className="font-mono text-xs" dir="ltr">{o.order_number}</span>
                <span>{KIND_LABEL[o.kind] ?? o.kind}</span>
                <Badge tone={STATE_TONE[o.state] ?? "neutral"}>{o.state}</Badge>
                <span className="font-bold">{formatRial(o.rial_amount)}</span>
                <Link
                  href={`/orders/${o.id}`}
                  className="text-[var(--color-primary)] text-xs justify-self-end"
                >
                  جزئیات ›
                </Link>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
