"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { PriceChart } from "@/components/PriceChart";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { useLivePrice } from "@/hooks/useLivePrice";
import { toPersianNumber } from "@/lib/format";

const LABELS: Record<string, string> = {
  gold_18k_750: "طلای ۱۸ عیار (گرم)",
  gold_24k: "طلای ۲۴ عیار (گرم)",
  mesghal: "مثقال ۱۷",
  coin_emami: "سکه امامی",
  coin_bahar: "سکه بهار",
  coin_half: "نیم سکه",
  coin_quarter: "ربع سکه",
  coin_gerami: "سکه گرمی",
  silver_999: "نقره ۹۹۹ (گرم)",
  ons_gold: "اونس جهانی",
  usd_free: "دلار آزاد",
};

type Point = { t: string; price: number };

export default function PricesPage() {
  const live = useLivePrice();
  const [series, setSeries] = useState<Point[]>([]);
  useEffect(() => {
    if (live.gold_18k_750) {
      const t = new Date().toLocaleTimeString("fa-IR");
      setSeries((prev) => [...prev.slice(-29), { t, price: live.gold_18k_750 }]);
    }
  }, [live.gold_18k_750]);

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl space-y-4">
        <h1 className="text-2xl font-bold">قیمت‌های لحظه‌ای</h1>
        <Card>
          <CardHeader><h2 className="font-bold">نمودار طلای ۱۸ عیار</h2></CardHeader>
          <CardBody>
            <PriceChart data={series} />
          </CardBody>
        </Card>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(LABELS).map(([k, label]) => (
            <Card key={k}>
              <CardBody>
                <p className="text-xs text-[var(--color-text-muted)]">{label}</p>
                <p className="text-lg font-bold" dir="ltr">
                  {live[k]
                    ? toPersianNumber(Math.floor(live[k] / 10).toLocaleString("fa-IR")) + " تومان"
                    : "—"}
                </p>
              </CardBody>
            </Card>
          ))}
        </div>
      </main>
      <Footer />
    </>
  );
}
