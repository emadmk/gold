"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";

type Notif = {
  id: string;
  kind: "info" | "success" | "warning" | "error";
  title: string;
  body: string;
  url: string;
  read: boolean;
  created_at: string;
};

const TONE: Record<Notif["kind"], "primary" | "success" | "warning" | "danger"> = {
  info: "primary",
  success: "success",
  warning: "warning",
  error: "danger",
};

export default function NotificationsPage() {
  const [list, setList] = useState<Notif[]>([]);

  async function load() {
    const r = await api<{ results: Notif[] }>("/notifications");
    setList(r.results ?? []);
  }

  useEffect(() => {
    load().catch(() => null);
  }, []);

  async function markAll() {
    await api("/notifications/read-all", { method: "POST" });
    load();
  }
  async function markOne(id: string) {
    await api(`/notifications/${id}/read`, { method: "POST" });
    load();
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">اعلان‌ها</h1>
          <Button variant="ghost" size="sm" onClick={markAll}>
            علامت همه به‌عنوان خوانده‌شده
          </Button>
        </div>
        {list.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">
            هیچ اعلانی ندارید.
          </p>
        ) : (
          list.map((n) => (
            <Card
              key={n.id}
              className={`mb-2 ${n.read ? "opacity-60" : ""}`}
              onClick={() => !n.read && markOne(n.id)}
            >
              <CardBody className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="font-bold text-sm flex items-center gap-2">
                    {n.title}
                    {!n.read && <Badge tone="primary">جدید</Badge>}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)] mt-1">
                    {n.body}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)] mt-1">
                    {new Date(n.created_at).toLocaleString("fa-IR")}
                  </p>
                </div>
                <Badge tone={TONE[n.kind]}>{n.kind}</Badge>
              </CardBody>
            </Card>
          ))
        )}
      </main>
      <Footer />
    </>
  );
}
