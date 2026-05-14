"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useMe } from "@/hooks/useMe";
import { useOrderCountdown } from "@/hooks/useOrderCountdown";
import type { Quote } from "@/lib/api";
import { toPersianNumber } from "@/lib/format";

export default function BuyGoldPage() {
  const me = useMe();
  const [asset, setAsset] = useState<"gold" | "silver">("gold");
  const [mg, setMg] = useState("");
  const [quote, setQuote] = useState<Quote | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const cd = useOrderCountdown(quote?.valid_until ?? null);

  useEffect(() => setQuote(null), [asset]);

  async function newQuote() {
    setErr(null);
    setOk(null);
    setBusy(true);
    try {
      const r = await fetch("/api/v1/prices/quote", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset, side: "buy" }),
      });
      if (r.status === 401 || r.status === 403) {
        setErr("برای دریافت نرخ، ابتدا وارد شوید.");
        return;
      }
      const data = await r.json();
      if (!r.ok) {
        setErr(data.detail ?? `HTTP ${r.status}`);
        return;
      }
      setQuote(data as Quote);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function placeOrder() {
    if (!quote || cd.expired) {
      setErr("نرخ منقضی شده — مجدداً تأیید کنید.");
      return;
    }
    setErr(null);
    setOk(null);
    setBusy(true);
    try {
      const r = await fetch(`/api/v1/trade/buy/${asset}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quote_id: quote.quote_id, mg_amount: Number(mg) }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        setErr(data.detail ?? `HTTP ${r.status}`);
        return;
      }
      setOk("سفارش با موفقیت ثبت شد.");
      setQuote(null);
      setMg("");
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const mgNum = Number(mg) || 0;
  const total = quote ? mgNum * quote.price_per_mg_rial : 0;

  // Auth gate
  if (me.status === "anonymous") {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 max-w-md text-center space-y-3">
          <div className="text-6xl">🔒</div>
          <h1 className="text-xl font-bold">برای خرید طلا ابتدا وارد شوید</h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            پس از ورود می‌توانید با کیف پول دیجیتال خود طلا یا نقره بخرید.
          </p>
          <Link
            href="/login?next=/trade/buy"
            className="inline-block px-6 py-3 rounded-xl bg-[var(--color-primary)] text-white font-medium"
          >
            ورود / ثبت‌نام
          </Link>
        </main>
        <Footer />
      </>
    );
  }
  if (me.status === "authenticated" && !me.user.is_verified) {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 max-w-md text-center space-y-3">
          <div className="text-6xl">🪪</div>
          <h1 className="text-xl font-bold">برای خرید نیاز به احراز هویت دارید</h1>
          <Link
            href="/kyc"
            className="inline-block px-6 py-3 rounded-xl bg-[var(--color-primary)] text-white font-medium"
          >
            تکمیل احراز هویت
          </Link>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-md space-y-4">
        <h1 className="text-2xl font-bold">
          خرید {asset === "gold" ? "طلا" : "نقره"}
        </h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}

        <Card>
          <CardHeader>
            <div className="flex gap-2">
              {(["gold", "silver"] as const).map((a) => (
                <button
                  key={a}
                  type="button"
                  onClick={() => setAsset(a)}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    asset === a
                      ? "bg-[var(--color-primary)] text-white"
                      : "bg-[var(--color-bg)]"
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
              <div className="rounded-lg bg-[var(--color-bg)] p-3 space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>نرخ هر میلی‌گرم</span>
                  <span dir="ltr">
                    {toPersianNumber(Math.floor(quote.price_per_mg_rial / 10).toLocaleString("fa-IR"))} تومان
                  </span>
                </div>
                <div className="flex justify-between font-bold">
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
              <Button
                onClick={newQuote}
                fullWidth
                loading={busy}
                disabled={!mg || mgNum < 1}
              >
                دریافت نرخ
              </Button>
            ) : (
              <Button onClick={placeOrder} variant="gold" fullWidth loading={busy}>
                تأیید خرید
              </Button>
            )}
            <p className="text-xs text-[var(--color-text-muted)]">
              اگر دکمه غیرفعال است، حداقل ۱ میلی‌گرم وارد کنید.
            </p>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
