"use client";
import { useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

export default function DeliveryPage() {
  const [mg, setMg] = useState("");
  const [addr, setAddr] = useState("");
  const [name, setName] = useState("");
  const [nid, setNid] = useState("");
  const [phone, setPhone] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);

  async function submit() {
    setErr(null); setOk(null);
    try {
      await api("/delivery/request", {
        method: "POST",
        body: JSON.stringify({
          requested_mg: Number(mg),
          shipping_address: addr,
          recipient_name: name,
          recipient_national_id: nid,
          recipient_phone: phone,
        }),
      });
      setOk("درخواست تحویل فیزیکی ثبت شد. در پنل سفارش‌ها قابل پیگیری است.");
      setMg(""); setAddr(""); setName(""); setNid(""); setPhone("");
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-md">
        <h1 className="text-2xl font-bold mb-4">درخواست تحویل فیزیکی</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        <Card>
          <CardHeader>
            <p className="text-sm">حداقل ۵ گرم — مضربی از ۱ گرم</p>
          </CardHeader>
          <CardBody className="space-y-3">
            <Input label="وزن (میلی‌گرم)" inputMode="numeric" dir="ltr"
              value={mg} onChange={(e) => setMg(e.target.value)} hint="مثلاً ۵۰۰۰ برای ۵ گرم" />
            <Input label="نام گیرنده" value={name} onChange={(e) => setName(e.target.value)} />
            <Input label="کد ملی گیرنده" maxLength={10} dir="ltr"
              value={nid} onChange={(e) => setNid(e.target.value)} />
            <Input label="موبایل گیرنده" maxLength={11} dir="ltr"
              value={phone} onChange={(e) => setPhone(e.target.value)} />
            <label className="block">
              <span className="block mb-1 text-sm">آدرس کامل</span>
              <textarea
                value={addr}
                onChange={(e) => setAddr(e.target.value)}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm min-h-24"
              />
            </label>
            <Button onClick={submit} fullWidth
              disabled={!mg || !addr || !name || !nid || !phone}>
              ثبت درخواست
            </Button>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
