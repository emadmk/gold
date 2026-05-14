"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { CheckoutSteps } from "@/components/CheckoutSteps";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

type Addr = {
  id: string;
  title: string;
  recipient_name: string;
  recipient_phone: string;
  recipient_national_id: string;
  province: string;
  city: string;
  address: string;
  postal_code: string;
  is_default: boolean;
};

export default function CheckoutAddressPage() {
  const router = useRouter();
  const [list, setList] = useState<Addr[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [form, setForm] = useState<Partial<Addr>>({});
  const [creating, setCreating] = useState(false);

  async function load() {
    try {
      const r = await api<{ results: Addr[] }>("/addresses");
      setList(r.results ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function pick(a: Addr) {
    await api("/cart/shipping/address", {
      method: "POST",
      body: JSON.stringify({ address_id: a.id }),
    });
    router.push("/checkout/shipping");
  }
  async function create() {
    setErr(null);
    try {
      await api("/addresses", { method: "POST", body: JSON.stringify(form) });
      setCreating(false);
      setForm({});
      load();
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">انتخاب آدرس</h1>
        <CheckoutSteps step={1} />
        {err && <Alert kind="danger">{err}</Alert>}

        <div className="space-y-2">
          {list.map((a) => (
            <Card key={a.id}>
              <CardBody className="flex justify-between items-center">
                <div className="text-sm">
                  <p className="font-bold">{a.title}</p>
                  <p>
                    {a.recipient_name} · {a.recipient_phone}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    {a.province}، {a.city}، {a.address}
                  </p>
                </div>
                <Button size="sm" onClick={() => pick(a)}>
                  انتخاب
                </Button>
              </CardBody>
            </Card>
          ))}
        </div>

        {!creating ? (
          <Button variant="ghost" onClick={() => setCreating(true)} fullWidth>
            افزودن آدرس جدید
          </Button>
        ) : (
          <Card>
            <CardHeader>
              <h2 className="font-bold">آدرس جدید</h2>
            </CardHeader>
            <CardBody className="space-y-3">
              <Input label="عنوان (مثلاً خانه)" value={form.title ?? ""}
                onChange={(e) => setForm({ ...form, title: e.target.value })} />
              <Input label="نام گیرنده" value={form.recipient_name ?? ""}
                onChange={(e) => setForm({ ...form, recipient_name: e.target.value })} />
              <Input label="موبایل گیرنده" dir="ltr" maxLength={11}
                value={form.recipient_phone ?? ""}
                onChange={(e) => setForm({ ...form, recipient_phone: e.target.value })} />
              <Input label="کد ملی گیرنده" dir="ltr" maxLength={10}
                value={form.recipient_national_id ?? ""}
                onChange={(e) => setForm({ ...form, recipient_national_id: e.target.value })} />
              <Input label="استان" value={form.province ?? ""}
                onChange={(e) => setForm({ ...form, province: e.target.value })} />
              <Input label="شهر" value={form.city ?? ""}
                onChange={(e) => setForm({ ...form, city: e.target.value })} />
              <label className="block">
                <span className="block mb-1 text-sm">آدرس کامل</span>
                <textarea
                  value={form.address ?? ""}
                  onChange={(e) => setForm({ ...form, address: e.target.value })}
                  className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm min-h-24"
                />
              </label>
              <Input label="کد پستی" dir="ltr" value={form.postal_code ?? ""}
                onChange={(e) => setForm({ ...form, postal_code: e.target.value })} />
              <div className="flex gap-2">
                <Button onClick={create}>ذخیره</Button>
                <Button variant="ghost" onClick={() => setCreating(false)}>
                  انصراف
                </Button>
              </div>
            </CardBody>
          </Card>
        )}
      </main>
      <Footer />
    </>
  );
}
