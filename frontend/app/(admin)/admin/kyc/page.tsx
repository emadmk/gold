"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { api } from "@/lib/api";

type KYC = {
  id: string;
  state: string;
  rejection_reason: string;
  created_at: string;
};

export default function AdminKYCPage() {
  const [items, setItems] = useState<KYC[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    try {
      const r = await api<{ results: KYC[] }>("/admin/kyc-queue");
      setItems(r.results ?? []);
    } catch (e) { setErr((e as Error).message); }
  }
  useEffect(() => { load(); }, []);

  async function approve(id: string) {
    await api(`/admin/kyc/${id}/approve`, { method: "POST" });
    load();
  }
  async function reject(id: string) {
    const reason = prompt("دلیل رد:");
    if (!reason) return;
    await api(`/admin/kyc/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
    load();
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl">
        <h1 className="text-2xl font-bold mb-4">صف KYC</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {items.length === 0 ? (
          <p>صف خالی است.</p>
        ) : (
          items.map((k) => (
            <Card key={k.id} className="mb-3">
              <CardHeader>
                <p className="text-sm">
                  وضعیت: <b>{k.state}</b> · ایجاد: {new Date(k.created_at).toLocaleString("fa-IR")}
                </p>
              </CardHeader>
              <CardBody className="flex gap-2">
                <Button onClick={() => approve(k.id)}>تأیید</Button>
                <Button variant="danger" onClick={() => reject(k.id)}>رد</Button>
              </CardBody>
            </Card>
          ))
        )}
      </main>
      <Footer />
    </>
  );
}
