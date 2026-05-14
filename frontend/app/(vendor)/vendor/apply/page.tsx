"use client";
import { useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

export default function VendorApplyPage() {
  const [form, setForm] = useState({
    shop_name: "", shop_slug: "", legal_name: "", iban: "", city: "", description: "",
  });
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);

  async function submit() {
    setErr(null); setOk(null);
    try {
      await api("/vendor/apply", { method: "POST", body: JSON.stringify(form) });
      setOk("درخواست فروشندگی ثبت شد. پس از تأیید ادمین، می‌توانید محصول اضافه کنید.");
    } catch (e) { setErr((e as Error).message); }
  }
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-md">
        <h1 className="text-2xl font-bold mb-4">درخواست فروشندگی</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        <Card>
          <CardBody className="space-y-3">
            <Input label="نام فروشگاه" value={form.shop_name}
              onChange={(e) => setForm({ ...form, shop_name: e.target.value })} />
            <Input label="آدرس URL (انگلیسی)" dir="ltr" value={form.shop_slug}
              onChange={(e) => setForm({ ...form, shop_slug: e.target.value })} />
            <Input label="نام حقوقی" value={form.legal_name}
              onChange={(e) => setForm({ ...form, legal_name: e.target.value })} />
            <Input label="شبا" dir="ltr" value={form.iban}
              onChange={(e) => setForm({ ...form, iban: e.target.value })} />
            <Input label="شهر" value={form.city}
              onChange={(e) => setForm({ ...form, city: e.target.value })} />
            <label className="block">
              <span className="block mb-1 text-sm">توضیحات</span>
              <textarea value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm min-h-24" />
            </label>
            <Button onClick={submit} fullWidth>ثبت درخواست</Button>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
