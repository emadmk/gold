"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api, type Wallet } from "@/lib/api";
import { formatRial, toPersianNumber } from "@/lib/format";

export default function RialWalletPage() {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [topup, setTopup] = useState("");
  const [withdraw, setWithdraw] = useState("");
  const [otp, setOtp] = useState("");
  const [gateway, setGateway] = useState("zarinpal");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);

  async function load() {
    try {
      setWallet(await api<Wallet>("/wallet"));
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function doTopup() {
    setErr(null);
    setOk(null);
    try {
      const tomanRial = Number(topup) * 10;
      const res = await api<{ redirect_url: string }>("/wallet/topup", {
        method: "POST",
        body: JSON.stringify({ amount_rial: tomanRial, gateway }),
      });
      if (res.redirect_url) window.location.href = res.redirect_url;
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  async function sendWithdrawOtp() {
    await api("/wallet/withdraw/otp", { method: "POST" });
    setOk("کد یکبارمصرف برای برداشت ارسال شد.");
  }

  async function doWithdraw() {
    setErr(null);
    setOk(null);
    try {
      const tomanRial = Number(withdraw) * 10;
      await api("/wallet/withdraw", {
        method: "POST",
        body: JSON.stringify({ amount_rial: tomanRial, otp }),
      });
      setOk("درخواست برداشت ثبت شد.");
      setWithdraw("");
      setOtp("");
      load();
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">کیف پول ریالی</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        <Card>
          <CardBody>
            <p className="text-sm text-[var(--color-text-muted)]">موجودی قابل برداشت</p>
            <p className="text-3xl font-bold text-[var(--color-primary)] mt-1">
              {formatRial(wallet?.rial.available_rial ?? 0)}
            </p>
            <p className="text-xs text-[var(--color-text-muted)] mt-1">
              {wallet?.rial.locked_rial
                ? `${toPersianNumber((wallet.rial.locked_rial / 10).toLocaleString("fa-IR"))} تومان قفل شده`
                : "بدون مبلغ قفل‌شده"}
            </p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h2 className="font-bold">شارژ کیف پول</h2></CardHeader>
          <CardBody className="space-y-3">
            <Input
              label="مبلغ (تومان)"
              inputMode="numeric"
              dir="ltr"
              placeholder="100000"
              value={topup}
              onChange={(e) => setTopup(e.target.value)}
              hint="حداقل ۱۰,۰۰۰ تومان"
            />
            <label className="block text-sm">
              <span className="block mb-1">درگاه پرداخت</span>
              <select
                value={gateway}
                onChange={(e) => setGateway(e.target.value)}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2"
              >
                <option value="zarinpal">زرین‌پال</option>
                <option value="idpay">آیدی‌پی</option>
                <option value="payping">پی‌پینگ</option>
              </select>
            </label>
            <Button onClick={doTopup} fullWidth>
              ادامه به درگاه
            </Button>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h2 className="font-bold">برداشت ریالی</h2></CardHeader>
          <CardBody className="space-y-3">
            <Input
              label="مبلغ (تومان)"
              inputMode="numeric"
              dir="ltr"
              placeholder="100000"
              value={withdraw}
              onChange={(e) => setWithdraw(e.target.value)}
              hint="به شبا تأییدشده پروفایل واریز می‌شود."
            />
            <div className="flex gap-2">
              <Input
                label="کد یکبارمصرف"
                inputMode="numeric"
                dir="ltr"
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="text-center tracking-widest"
              />
              <Button variant="ghost" onClick={sendWithdrawOtp} className="self-end">
                ارسال کد
              </Button>
            </div>
            <Button variant="primary" onClick={doWithdraw} fullWidth disabled={!otp}>
              ثبت درخواست برداشت
            </Button>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
