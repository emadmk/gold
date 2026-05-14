"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { formatMg, toPersianNumber } from "@/lib/format";

type P = {
  id: string;
  title: string;
  sku: string;
  category: string;
  weight_mg: number;
  karat: number;
  stock: number;
  is_active: boolean;
};

export default function VendorProductsPage() {
  const [items, setItems] = useState<P[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [draft, setDraft] = useState({
    title: "", sku: "", category: "melted", slug: "",
    weight_mg: "5000", karat: "750",
    manufacturing_fee_pct: "0", vendor_margin_pct: "0.01",
    stock: "1",
  });

  async function load() {
    try {
      const res = await api<{ results: P[] }>("/vendor/products");
      setItems(res.results ?? []);
    } catch (e) { setErr((e as Error).message); }
  }
  useEffect(() => { load(); }, []);

  async function create() {
    try {
      await api("/vendor/products", {
        method: "POST",
        body: JSON.stringify({
          ...draft,
          weight_mg: Number(draft.weight_mg),
          karat: Number(draft.karat),
          stock: Number(draft.stock),
          manufacturing_fee_pct: draft.manufacturing_fee_pct,
          vendor_margin_pct: draft.vendor_margin_pct,
        }),
      });
      load();
    } catch (e) { setErr((e as Error).message); }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">محصولات فروشگاه</h1>
        {err && <Alert kind="danger">{err}</Alert>}

        <Card>
          <CardHeader><h2 className="font-bold">افزودن محصول</h2></CardHeader>
          <CardBody className="space-y-3 grid grid-cols-2 gap-3">
            <Input label="عنوان" value={draft.title}
              onChange={(e) => setDraft({ ...draft, title: e.target.value })} />
            <Input label="SKU" dir="ltr" value={draft.sku}
              onChange={(e) => setDraft({ ...draft, sku: e.target.value })} />
            <Input label="Slug" dir="ltr" value={draft.slug}
              onChange={(e) => setDraft({ ...draft, slug: e.target.value })} />
            <label className="block">
              <span className="block mb-1 text-sm">دسته</span>
              <select value={draft.category}
                onChange={(e) => setDraft({ ...draft, category: e.target.value })}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2">
                <option value="melted">طلای آب‌شده</option>
                <option value="jewelry">طلای ساخته‌شده</option>
                <option value="coin">سکه</option>
                <option value="silver">نقره</option>
              </select>
            </label>
            <Input label="وزن (mg)" dir="ltr" value={draft.weight_mg}
              onChange={(e) => setDraft({ ...draft, weight_mg: e.target.value })} />
            <Input label="عیار" dir="ltr" value={draft.karat}
              onChange={(e) => setDraft({ ...draft, karat: e.target.value })} />
            <Input label="درصد اجرت" dir="ltr" value={draft.manufacturing_fee_pct}
              onChange={(e) => setDraft({ ...draft, manufacturing_fee_pct: e.target.value })} />
            <Input label="درصد سود" dir="ltr" value={draft.vendor_margin_pct}
              onChange={(e) => setDraft({ ...draft, vendor_margin_pct: e.target.value })} />
            <Input label="موجودی" dir="ltr" value={draft.stock}
              onChange={(e) => setDraft({ ...draft, stock: e.target.value })} />
            <div className="col-span-2"><Button onClick={create} fullWidth>افزودن</Button></div>
          </CardBody>
        </Card>

        <h2 className="font-bold mt-6">لیست محصولات</h2>
        {items.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">هنوز محصولی ندارید.</p>
        ) : (
          items.map((p) => (
            <Card key={p.id}>
              <CardBody className="flex justify-between">
                <div>
                  <p className="font-bold">{p.title}</p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    SKU: {p.sku} · {p.category} · {formatMg(p.weight_mg)} · عیار {toPersianNumber(p.karat)}
                  </p>
                </div>
                <div className="text-sm">موجودی: {toPersianNumber(p.stock)}</div>
              </CardBody>
            </Card>
          ))
        )}
      </main>
      <Footer />
    </>
  );
}
