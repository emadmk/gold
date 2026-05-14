"use client";
import { useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

export default function TransferPage() {
  const [asset, setAsset] = useState<"gold" | "silver">("gold");
  const [mg, setMg] = useState("");
  const [to, setTo] = useState("");
  const [otp, setOtp] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);

  async function sendOtp() {
    await api("/wallet/transfer/otp", { method: "POST" });
    setOk("کد یکبارمصرف ارسال شد.");
  }
  async function submit() {
    setErr(null); setOk(null);
    try {
      await api("/wallet/transfer", {
        method: "POST",
        body: JSON.stringify({ asset, mg: Number(mg), to_address: to, otp }),
      });
      setOk("انتقال با موفقیت انجام شد.");
      setMg(""); setOtp("");
    } catch (e) { setErr((e as Error).message); }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-md">
        <h1 className="text-2xl font-bold mb-4">انتقال طلا/نقره</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        <Card>
          <CardBody className="space-y-3">
            <div className="flex gap-2">
              {(["gold", "silver"] as const).map((a) => (
                <button key={a} onClick={() => setAsset(a)}
                  className={`px-3 py-1 rounded-lg text-sm ${asset === a
                    ? "bg-[var(--color-primary)] text-white" : "bg-[var(--color-bg-alt)]"}`}>
                  {a === "gold" ? "طلا" : "نقره"}
                </button>
              ))}
            </div>
            <Input label="آدرس کیف پول مقصد" dir="ltr" placeholder="GLD-XXXX..."
              value={to} onChange={(e) => setTo(e.target.value)} />
            <Input label="مقدار (میلی‌گرم)" inputMode="numeric" dir="ltr"
              value={mg} onChange={(e) => setMg(e.target.value)} />
            <div className="flex gap-2">
              <Input label="کد یکبارمصرف" maxLength={6} dir="ltr"
                value={otp} onChange={(e) => setOtp(e.target.value)}
                className="text-center tracking-widest" />
              <Button variant="ghost" onClick={sendOtp} className="self-end">ارسال</Button>
            </div>
            <Button onClick={submit} fullWidth disabled={!otp || !to || !mg}>
              تأیید انتقال
            </Button>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
