"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

type Vendor = {
  shop_name: string;
  shop_slug: string;
  description: string;
  city: string;
  address: string;
  phone: string;
  iban: string;
  state: string;
  rating: number;
  total_sales: number;
};

export default function VendorProfilePage() {
  const [v, setV] = useState<Vendor | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);

  useEffect(() => {
    api<Vendor>("/vendor/me").then(setV).catch((e) => setErr(e.message));
  }, []);

  async function save() {
    if (!v) return;
    setErr(null);
    setOk(null);
    try {
      const next = await api<Vendor>("/vendor/me", {
        method: "PATCH",
        body: JSON.stringify({
          shop_name: v.shop_name,
          description: v.description,
          city: v.city,
          address: v.address,
          phone: v.phone,
          iban: v.iban,
        }),
      });
      setV(next);
      setOk("اطلاعات فروشگاه ذخیره شد.");
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  if (!v) {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-10 max-w-2xl">
          {err ? <Alert kind="danger">{err}</Alert> : <p>در حال بارگذاری…</p>}
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-2xl space-y-4">
        <h1 className="text-2xl font-bold">پروفایل فروشگاه</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        <Card>
          <CardHeader>
            <p className="text-sm">
              وضعیت: <b>{v.state}</b> · امتیاز: {v.rating}/۵
            </p>
          </CardHeader>
          <CardBody className="space-y-3">
            <Input
              label="نام فروشگاه"
              value={v.shop_name}
              onChange={(e) => setV({ ...v, shop_name: e.target.value })}
            />
            <label className="block">
              <span className="block mb-1 text-sm">توضیحات</span>
              <textarea
                value={v.description}
                onChange={(e) => setV({ ...v, description: e.target.value })}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm min-h-24"
              />
            </label>
            <Input
              label="شهر"
              value={v.city}
              onChange={(e) => setV({ ...v, city: e.target.value })}
            />
            <label className="block">
              <span className="block mb-1 text-sm">آدرس</span>
              <textarea
                value={v.address}
                onChange={(e) => setV({ ...v, address: e.target.value })}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm"
              />
            </label>
            <Input
              label="تلفن"
              dir="ltr"
              value={v.phone}
              onChange={(e) => setV({ ...v, phone: e.target.value })}
            />
            <Input
              label="شبا"
              dir="ltr"
              value={v.iban}
              onChange={(e) => setV({ ...v, iban: e.target.value })}
            />
            <Button onClick={save}>ذخیره تغییرات</Button>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
