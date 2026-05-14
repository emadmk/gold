"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api, type User } from "@/lib/api";

type AdminUser = User & { is_frozen?: boolean };

export default function AdminUsersPage() {
  const [list, setList] = useState<AdminUser[]>([]);
  const [filter, setFilter] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    try {
      const r = await api<{ results: AdminUser[] }>("/admin/users");
      setList(r.results ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function freeze(u: AdminUser) {
    const reason = prompt(`دلیل مسدودسازی ${u.phone}؟`);
    if (reason == null) return;
    await api(`/admin/users/${u.id}/freeze`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
    load();
  }
  async function unfreeze(u: AdminUser) {
    await api(`/admin/users/${u.id}/unfreeze`, { method: "POST" });
    load();
  }

  const shown = filter
    ? list.filter(
        (u) =>
          u.phone.includes(filter) ||
          (u.first_name + " " + u.last_name).includes(filter),
      )
    : list;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">کاربران</h1>
      <Input
        dir="ltr"
        placeholder="جست‌وجو بر اساس موبایل یا نام"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      {err && (
        <Card>
          <CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody>
        </Card>
      )}

      {shown.length === 0 ? (
        <Card><CardBody className="text-center text-sm py-8 text-[var(--color-text-muted)]">
          کاربری یافت نشد.
        </CardBody></Card>
      ) : (
        <div className="space-y-2">
          {shown.map((u) => (
            <Card key={u.id}>
              <CardBody className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-2 items-center">
                <div className="text-sm space-y-1">
                  <p className="font-bold" dir="ltr">{u.phone}</p>
                  <p className="text-xs">
                    {u.first_name || "—"} {u.last_name}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {u.is_verified && <Badge tone="success">KYC تأیید</Badge>}
                    {!u.is_verified && u.is_phone_verified && <Badge tone="warning">KYC ناقص</Badge>}
                    {u.is_vendor && <Badge tone="primary">فروشنده</Badge>}
                    {u.two_factor_enabled && <Badge tone="neutral">2FA</Badge>}
                    {u.is_frozen && <Badge tone="danger">مسدود</Badge>}
                    <Badge tone="gold">{u.tier}</Badge>
                  </div>
                </div>
                <div className="flex gap-2">
                  {u.is_frozen ? (
                    <Button size="sm" onClick={() => unfreeze(u)}>بازفعال</Button>
                  ) : (
                    <Button size="sm" variant="danger" onClick={() => freeze(u)}>مسدود</Button>
                  )}
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
