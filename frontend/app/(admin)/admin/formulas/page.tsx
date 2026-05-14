"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";

type Formula = { key: string; value: string; description: string };

export default function AdminFormulasPage() {
  const [items, setItems] = useState<Formula[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);

  async function load() {
    setItems(await api<Formula[]>("/admin/formulas"));
  }
  useEffect(() => { load().catch((e) => setErr(e.message)); }, []);

  async function save() {
    setErr(null); setOk(null);
    try {
      await api("/admin/formulas", { method: "PUT", body: JSON.stringify(items) });
      setOk("ذخیره شد.");
    } catch (e) { setErr((e as Error).message); }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        <h1 className="text-2xl font-bold mb-4">فرمول‌های قیمت‌گذاری</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        <Card>
          <CardBody className="space-y-2">
            {items.map((f, i) => (
              <div key={f.key} className="flex gap-3 items-center">
                <code className="text-xs flex-1" dir="ltr">{f.key}</code>
                <input
                  value={f.value} dir="ltr"
                  onChange={(e) => {
                    const next = [...items];
                    next[i] = { ...f, value: e.target.value };
                    setItems(next);
                  }}
                  className="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-sm w-32"
                />
              </div>
            ))}
            <Button onClick={save} fullWidth>ذخیره همه</Button>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
