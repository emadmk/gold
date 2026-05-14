"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";

type V = {
  id: string;
  shop_name: string;
  shop_slug: string;
  state: string;
  rating: number;
  total_sales: number;
};

export default function AdminVendorsPage() {
  const [list, setList] = useState<V[]>([]);
  async function load() {
    const r = await api<{ results: V[] }>("/admin/vendors-list");
    setList(r.results ?? []);
  }
  useEffect(() => { load(); }, []);
  async function approve(v: V) {
    await api(`/admin/vendors/${v.id}/approve`, { method: "POST" });
    load();
  }
  async function suspend(v: V) {
    const reason = prompt("دلیل تعلیق:") ?? "";
    await api(`/admin/vendors/${v.id}/suspend`, {
      method: "POST", body: JSON.stringify({ reason }),
    });
    load();
  }
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl">
        <h1 className="text-2xl font-bold mb-4">فروشندگان</h1>
        {list.map((v) => (
          <Card key={v.id} className="mb-2">
            <CardBody className="flex justify-between items-center">
              <div>
                <p className="font-bold">{v.shop_name}</p>
                <p className="text-xs">{v.shop_slug}</p>
              </div>
              <div className="flex gap-2 items-center">
                <Badge tone={v.state === "approved" ? "success" : "warning"}>{v.state}</Badge>
                {v.state === "applied" && <Button size="sm" onClick={() => approve(v)}>تأیید</Button>}
                {v.state === "approved" && <Button size="sm" variant="danger" onClick={() => suspend(v)}>تعلیق</Button>}
              </div>
            </CardBody>
          </Card>
        ))}
      </main>
      <Footer />
    </>
  );
}
