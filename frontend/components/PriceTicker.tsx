"use client";

import { useEffect, useState } from "react";

import { toPersianNumber } from "@/lib/format";

type Snapshot = Record<string, number>;

const ITEMS: { key: string; label: string }[] = [
  { key: "gold_18k_750", label: "هر گرم طلای ۱۸" },
  { key: "silver_999", label: "هر گرم نقره ۹۹۹" },
  { key: "coin_emami", label: "سکه امامی" },
  { key: "coin_bahar", label: "سکه بهار" },
  { key: "coin_half", label: "نیم سکه" },
  { key: "ons_gold", label: "اونس جهانی" },
  { key: "usd_free", label: "دلار آزاد" },
];

export function PriceTicker() {
  const [data, setData] = useState<Snapshot>({});

  useEffect(() => {
    // Initial snapshot from REST so the bar shows numbers even before WS connects.
    fetch("/api/v1/prices", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => j?.data && setData((p) => ({ ...p, ...j.data })))
      .catch(() => null);

    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(`${proto}://${window.location.host}/ws/prices/`);
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data) as { data?: Snapshot };
          if (msg.data) setData((p) => ({ ...p, ...msg.data }));
        } catch {
          /* ignore */
        }
      };
    } catch {
      /* WS optional */
    }
    return () => ws?.close();
  }, []);

  return (
    <div className="ticker overflow-hidden bg-[var(--color-footer)] text-white border-b border-black/30">
      <div className="container mx-auto flex gap-6 px-4 py-1.5 text-[11px] whitespace-nowrap no-scrollbar overflow-x-auto">
        {ITEMS.map(({ key, label }) => {
          const v = data[key];
          return (
            <span key={key} className="inline-flex items-center gap-1.5">
              <span className="text-white/60">{label}:</span>
              <span className="font-semibold text-[var(--color-gold)]">
                {v
                  ? toPersianNumber(Math.floor(v / 10).toLocaleString("fa-IR"))
                  : "—"}
              </span>
              <span className="text-white/60">تومان</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}
