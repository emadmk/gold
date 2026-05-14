"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api, type User } from "@/lib/api";

export default function AdminUsersPage() {
  const [list, setList] = useState<User[]>([]);
  async function load() {
    const r = await api<{ results: User[] }>("/admin/users");
    setList(r.results ?? []);
  }
  useEffect(() => { load(); }, []);
  async function freeze(u: User) {
    const reason = prompt("دلیل مسدودسازی:") ?? "";
    await api(`/admin/users/${u.id}/freeze`, {
      method: "POST", body: JSON.stringify({ reason }),
    });
    load();
  }
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl">
        <h1 className="text-2xl font-bold mb-4">کاربران</h1>
        {list.map((u) => (
          <Card key={u.id} className="mb-2">
            <CardBody className="flex justify-between items-center">
              <div>
                <p dir="ltr">{u.phone}</p>
                <p className="text-xs text-[var(--color-text-muted)]">
                  {u.first_name} {u.last_name}
                </p>
              </div>
              <div className="flex gap-2 items-center">
                {u.is_verified && <Badge tone="success">احراز</Badge>}
                {u.is_vendor && <Badge tone="primary">فروشنده</Badge>}
                <Badge tone="gold">{u.tier}</Badge>
                <Button variant="danger" size="sm" onClick={() => freeze(u)}>
                  مسدود
                </Button>
              </div>
            </CardBody>
          </Card>
        ))}
      </main>
      <Footer />
    </>
  );
}
