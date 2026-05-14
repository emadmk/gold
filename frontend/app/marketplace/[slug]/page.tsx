"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

type Product = {
  id: string;
  title: string;
  description: string;
  weight_mg: number;
  karat: number;
  computed_price_rial: number;
  stock: number;
  image_urls: string[];
  vendor: { shop_name: string };
};

export default function ProductDetailPage() {
  const params = useParams<{ slug: string }>();
  const [p, setP] = useState<Product | null>(null);
  const [qty, setQty] = useState("1");
  const [shipping, setShipping] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  useEffect(() => {
    api<Product>(`/marketplace/products/${params.slug}`).then(setP)
      .catch((e) => setErr(e.message));
  }, [params.slug]);

  async function buy() {
    if (!p) return;
    setErr(null); setOk(null);
    try {
      await api("/marketplace/checkout", {
        method: "POST",
        body: JSON.stringify({
          items: [{ product_id: p.id, quantity: Number(qty) }],
          shipping_address: shipping,
          recipient_name: name,
          recipient_phone: phone,
        }),
      });
      setOk("سفارش با موفقیت ثبت شد.");
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  if (!p) return <p className="p-8">در حال بارگذاری…</p>;
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        <Card>
          <CardBody className="grid md:grid-cols-2 gap-6">
            <div>
              {p.image_urls?.[0] ? (
                <img src={p.image_urls[0]} alt={p.title} className="w-full rounded-lg" />
              ) : (
                <div className="aspect-square rounded-lg bg-[var(--color-gold-light)] flex items-center justify-center text-9xl">
                  🥇
                </div>
              )}
            </div>
            <div className="space-y-2">
              <h1 className="text-2xl font-bold">{p.title}</h1>
              <p className="text-sm text-[var(--color-text-muted)]">{p.vendor.shop_name}</p>
              <div className="text-sm">
                <p>وزن: {formatMg(p.weight_mg)}</p>
                <p>عیار: {toPersianNumber(p.karat)}</p>
                <p>موجودی: {toPersianNumber(p.stock)}</p>
              </div>
              <p className="text-2xl font-bold text-[var(--color-primary)]">
                {formatRial(p.computed_price_rial)}
              </p>
              <Input label="تعداد" type="number" min={1} max={p.stock}
                value={qty} onChange={(e) => setQty(e.target.value)} />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h2 className="font-bold">آدرس تحویل</h2></CardHeader>
          <CardBody className="space-y-3">
            <Input label="نام گیرنده" value={name} onChange={(e) => setName(e.target.value)} />
            <Input label="موبایل گیرنده" dir="ltr" maxLength={11}
              value={phone} onChange={(e) => setPhone(e.target.value)} />
            <label className="block">
              <span className="block mb-1 text-sm">آدرس کامل</span>
              <textarea value={shipping} onChange={(e) => setShipping(e.target.value)}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm min-h-24" />
            </label>
            <Button onClick={buy} fullWidth disabled={!shipping || !name || !phone}>
              تأیید و پرداخت
            </Button>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
