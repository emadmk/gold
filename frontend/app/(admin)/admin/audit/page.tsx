"use client";

import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";

type Entry = {
  id: string;
  kind: string;
  category: string;
  severity: string;
  outcome: string;
  actor_id: string;
  target_type: string;
  target_id: string;
  request_id: string;
  trace_id: string;
  data: Record<string, unknown>;
  created_at: string;
};

const SEV_TONE: Record<string, "neutral" | "primary" | "warning" | "danger"> = {
  debug: "neutral",
  info: "primary",
  warning: "warning",
  error: "danger",
  critical: "danger",
};

export default function AuditLogPage() {
  const [list, setList] = useState<Entry[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [filterKind, setFilterKind] = useState("");

  useEffect(() => {
    api<{ results: Entry[] }>("/admin/audit-log")
      .then((r) => setList(r.results ?? []))
      .catch((e) => setErr((e as Error).message));
  }, []);

  const shown = useMemo(
    () => (filterKind ? list.filter((e) => e.kind.includes(filterKind)) : list),
    [list, filterKind],
  );

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">لاگ ممیزی</h1>
      <p className="text-xs text-[var(--color-text-muted)]">
        نمای محلی (آخرین رویدادها). برای جست‌وجوی کامل و رفرنس از Kibana
        استفاده کنید: <code>kibana.{`{domain}`}</code> → index{" "}
        <code dir="ltr">keyhan-events-*</code>
      </p>

      <Input
        dir="ltr"
        placeholder="فیلتر بر اساس kind (مثلاً wallet.rial)"
        value={filterKind}
        onChange={(e) => setFilterKind(e.target.value)}
      />

      {err && <Card><CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody></Card>}

      {shown.length === 0 ? (
        <Card>
          <CardBody className="text-center text-sm text-[var(--color-text-muted)] py-8">
            موردی یافت نشد.
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-2">
          {shown.map((e) => (
            <Card key={e.id}>
              <CardBody className="grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr] gap-2 items-center text-xs">
                <div>
                  <code dir="ltr" className="font-mono text-xs">{e.kind}</code>
                  <p className="text-[var(--color-text-muted)] mt-1">
                    {e.target_type ? `${e.target_type}: ${e.target_id}` : "—"}
                  </p>
                </div>
                <div className="space-x-1 space-x-reverse">
                  <Badge tone={SEV_TONE[e.severity] ?? "neutral"}>{e.severity}</Badge>
                  <Badge tone={e.outcome === "failure" ? "danger" : "neutral"}>{e.outcome}</Badge>
                </div>
                <span className="text-[var(--color-text-muted)] justify-self-end">
                  {new Date(e.created_at).toLocaleString("fa-IR")}
                </span>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
