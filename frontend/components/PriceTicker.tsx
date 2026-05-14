"use client";
import { useEffect, useState } from "react";

import { toPersianNumber } from "@/lib/format";

type Snapshot = Record<string, number>;

const LABELS: Record<string, string> = {
  gold_18k_750: "هر گرم طلای ۱۸",
  silver_999: "هر گرم نقره ۹۹۹",
  coin_emami: "سکه امامی",
  coin_bahar: "سکه بهار",
  usd_free: "دلار آزاد",
};

export function PriceTicker() {
  const [data, setData] = useState<Snapshot>({});

  useEffect(() => {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/prices/`);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data) as { type: string; data: Snapshot };
        if (msg.data) setData((prev) => ({ ...prev, ...msg.data }));
      } catch {
        /* ignore malformed frames */
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div className="ticker overflow-hidden bg-[var(--color-bg-alt)] border-b border-[var(--color-border)]">
      <div className="flex gap-6 px-4 py-1 text-xs text-[var(--color-text-muted)] whitespace-nowrap">
        {Object.entries(LABELS).map(([key, label]) => (
          <span key={key} className="inline-flex items-center gap-1">
            <span>{label}:</span>
            <span className="font-medium text-[var(--color-text)]">
              {data[key] ? toPersianNumber(Math.floor(data[key] / 10).toLocaleString("fa-IR")) : "—"}
            </span>
            <span>تومان</span>
          </span>
        ))}
      </div>
    </div>
  );
}
