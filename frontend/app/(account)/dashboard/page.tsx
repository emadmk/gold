"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { useMe } from "@/hooks/useMe";
import { formatMg, formatRial } from "@/lib/format";

type Wallet = {
  rial: { balance_rial: number; locked_rial: number; available_rial: number; currency: string };
  gold: {
    address: string;
    balance_mg: number;
    available_gold_mg: number;
    silver_balance_mg: number;
    available_silver_mg: number;
  };
};

export default function DashboardPage() {
  const me = useMe();
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (me.status !== "authenticated") return;
    fetch("/api/v1/wallet", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setWallet)
      .catch((e: Error) => setErr(e.message));
  }, [me]);

  if (me.status === "loading") {
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
  if (me.status === "anonymous") {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 max-w-md text-center space-y-3">
          <div className="text-6xl">🔒</div>
          <h1 className="text-xl font-bold">برای ورود به داشبورد، احراز هویت کنید</h1>
          <Link
            href="/login?next=/dashboard"
            className="inline-block px-6 py-3 rounded-xl bg-[var(--color-primary)] text-white"
          >
            ورود / ثبت‌نام
          </Link>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-8 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">خوش آمدید 👋</h1>
            <p className="text-sm text-[var(--color-text-muted)]">
              {me.user.first_name || me.user.phone}
              {me.user.is_verified ? (
                <Badge tone="success" className="mx-2">احراز شده</Badge>
              ) : (
                <Badge tone="warning" className="mx-2">KYC ناقص</Badge>
              )}
            </p>
          </div>
        </div>

        {err && <Alert kind="danger">{err}</Alert>}
        {!me.user.is_verified && (
          <Alert kind="warning">
            احراز هویت شما هنوز کامل نشده است.{" "}
            <Link href="/kyc" className="font-bold underline">
              همین حالا کامل کنید
            </Link>
          </Alert>
        )}

        <div className="grid md:grid-cols-3 gap-3">
          <BalanceCard
            title="کیف پول ریالی"
            value={formatRial(wallet?.rial.available_rial ?? 0)}
            color="var(--color-primary)"
            href="/wallet/rial"
            cta="شارژ / برداشت"
          />
          <BalanceCard
            title="کیف پول طلا"
            value={formatMg(wallet?.gold.available_gold_mg ?? 0)}
            color="var(--color-gold-deep)"
            href="/wallet/gold"
            cta="انتقال / تحویل"
          />
          <BalanceCard
            title="کیف پول نقره"
            value={formatMg(wallet?.gold.available_silver_mg ?? 0)}
            color="var(--color-text-muted)"
            href="/wallet/gold"
            cta="مدیریت"
          />
        </div>

        <Card>
          <CardBody>
            <h2 className="font-bold mb-3">میان‌برهای پرکاربرد</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              <Link href="/trade/buy" className="rounded-lg bg-[var(--color-primary-light)] text-[var(--color-primary-hover)] px-3 py-2.5 text-center hover:opacity-80">خرید طلا</Link>
              <Link href="/trade/sell" className="rounded-lg bg-[var(--color-gold-light)] text-[var(--color-gold-deep)] px-3 py-2.5 text-center hover:opacity-80">فروش طلا</Link>
              <Link href="/transfer" className="rounded-lg bg-[var(--color-success-light)] text-[var(--color-success)] px-3 py-2.5 text-center hover:opacity-80">انتقال</Link>
              <Link href="/delivery" className="rounded-lg bg-[var(--color-warning-light)] text-amber-800 px-3 py-2.5 text-center hover:opacity-80">تحویل فیزیکی</Link>
              <Link href="/orders" className="rounded-lg bg-white border border-[var(--color-border)] px-3 py-2.5 text-center hover:bg-[var(--color-bg)]">سفارش‌ها</Link>
              <Link href="/marketplace" className="rounded-lg bg-white border border-[var(--color-border)] px-3 py-2.5 text-center hover:bg-[var(--color-bg)]">مارکت‌پلیس</Link>
              <Link href="/notifications" className="rounded-lg bg-white border border-[var(--color-border)] px-3 py-2.5 text-center hover:bg-[var(--color-bg)]">اعلان‌ها</Link>
              <Link href="/profile" className="rounded-lg bg-white border border-[var(--color-border)] px-3 py-2.5 text-center hover:bg-[var(--color-bg)]">پروفایل</Link>
            </div>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}

function BalanceCard({
  title,
  value,
  color,
  href,
  cta,
}: {
  title: string;
  value: string;
  color: string;
  href: string;
  cta: string;
}) {
  return (
    <Card>
      <CardBody className="space-y-3">
        <p className="text-xs text-[var(--color-text-muted)]">{title}</p>
        <p className="text-2xl font-bold" style={{ color }}>{value}</p>
        <Link
          href={href}
          className="block text-center text-sm rounded-lg bg-[var(--color-bg)] hover:bg-[var(--color-bg-alt)] py-2"
        >
          {cta}
        </Link>
      </CardBody>
    </Card>
  );
}
