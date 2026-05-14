"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { api, type Wallet } from "@/lib/api";
import { formatMg, toPersianNumber } from "@/lib/format";
import Link from "next/link";

export default function GoldWalletPage() {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  useEffect(() => {
    api<Wallet>("/wallet").then(setWallet).catch(() => null);
  }, []);
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">کیف پول طلا</h1>
        <Card>
          <CardBody>
            <p className="text-sm text-[var(--color-text-muted)]">موجودی طلا</p>
            <p className="text-3xl font-bold text-[var(--color-gold)] mt-1">
              {formatMg(wallet?.gold.available_gold_mg ?? 0)}
            </p>
            <p className="text-xs text-[var(--color-text-muted)] mt-1">
              آدرس کیف پول: <span dir="ltr" className="font-mono">{wallet?.gold.address ?? "—"}</span>
            </p>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <p className="text-sm text-[var(--color-text-muted)]">موجودی نقره</p>
            <p className="text-3xl font-bold text-[var(--color-text-muted)] mt-1">
              {formatMg(wallet?.gold.available_silver_mg ?? 0)}
            </p>
          </CardBody>
        </Card>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Link href="/trade/buy" className="block">
            <Card className="text-center hover:shadow-[var(--shadow-card-hover)] transition">
              <CardBody>خرید طلا</CardBody>
            </Card>
          </Link>
          <Link href="/trade/sell" className="block">
            <Card className="text-center hover:shadow-[var(--shadow-card-hover)] transition">
              <CardBody>فروش طلا</CardBody>
            </Card>
          </Link>
          <Link href="/transfer" className="block">
            <Card className="text-center hover:shadow-[var(--shadow-card-hover)] transition">
              <CardBody>انتقال طلا</CardBody>
            </Card>
          </Link>
          <Link href="/delivery" className="block">
            <Card className="text-center hover:shadow-[var(--shadow-card-hover)] transition">
              <CardBody>تحویل فیزیکی</CardBody>
            </Card>
          </Link>
        </div>
      </main>
      <Footer />
    </>
  );
}
