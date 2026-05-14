"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api, type Quote } from "@/lib/api";
import { useOrderCountdown } from "@/hooks/useOrderCountdown";
import { toPersianNumber } from "@/lib/format";

export default function BuyGoldPage() {
  const [asset, setAsset] = useState<"gold" | "silver">("gold");
  const [mg, setMg] = useState("");
  const [quote, setQuote] = useState<Quote | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const cd = useOrderCountdown(quote?.valid_until ?? null);

  useEffect(() => {
    setQuote(null);
  }, [asset]);

  async function newQuote() {
    setErr(null);
    setOk(null);
    try {
      setQuote(
        await api<Quote>("/prices/quote", {
          method: "POST",
          body: JSON.stringify({ asset, side: "buy" }),
        }),
      );
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  async function placeOrder() {
    setErr(null);
    setOk(null);
    if (!quote || cd.expired) {
      setErr("نرخ منقضی شده — مجدداً تأیید کنید.");
      return;
    }
    try {
      await api(`/trade/buy/${asset}`, {
        method: "POST",
        body: JSON.stringify({ quote_id: quote.quote_id, mg_amount: Number(mg) }),
      });
      setOk("سفارش با موفقیت ثبت شد.");
      setQuote(null);
      setMg("");
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  const mgNum = Number(mg);
  const total = quote ? mgNum * quote.price_per_mg_rial : 0;

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-md space-y-4">
        <h1 className="text-2xl font-bold">خرید {asset === "gold" ? "طلا" : "نقره"}</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}

        <Card>
          <CardHeader>
            <div className="flex gap-2">
              {(["gold", "silver"] as const).map((a) => (
                <button
                  key={a}
                  onClick={() => setAsset(a)}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    asset === a
                      ? "bg-[var(--color-primary)] text-white"
                      : "bg-[var(--color-bg-alt)]"
                  }`}
                >
                  {a === "gold" ? "طلا" : "نقره"}
                </button>
              ))}
            </div>
          </CardHeader>
          <CardBody className="space-y-3">
            <Input
              label="مقدار به میلی‌گرم"
              inputMode="numeric"
              dir="ltr"
              placeholder="1000"
              value={mg}
              onChange={(e) => setMg(e.target.value)}
              hint="هر گرم = ۱۰۰۰ میلی‌گرم"
            />
            {quote ? (
              <div className="rounded-lg bg-[var(--color-bg-alt)] p-3 space-y-1">
                <div className="flex justify-between text-sm">
                  <span>نرخ هر میلی‌گرم</span>
                  <span dir="ltr">
                    {toPersianNumber(Math.floor(quote.price_per_mg_rial / 10).toLocaleString("fa-IR"))} تومان
                  </span>
                </div>
                <div className="flex justify-between text-sm font-bold">
                  <span>جمع کل</span>
                  <span dir="ltr">
                    {toPersianNumber(Math.floor(total / 10).toLocaleString("fa-IR"))} تومان
                  </span>
                </div>
                <div className="flex justify-between text-xs text-[var(--color-text-muted)]">
                  <span>اعتبار نرخ</span>
                  <span dir="ltr">{cd.label}</span>
                </div>
              </div>
            ) : null}
            {!quote || cd.expired ? (
              <Button onClick={newQuote} fullWidth disabled={!mg || mgNum < 1}>
                دریافت نرخ
              </Button>
            ) : (
              <Button onClick={placeOrder} variant="gold" fullWidth>
                تأیید خرید
              </Button>
            )}
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
