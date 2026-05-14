import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
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
  created_at: string;
};

export default async function AuditLogPage() {
  let r: { results: Entry[] } | null = null;
  try { r = await api<{ results: Entry[] }>("/admin/audit-log", { cache: "no-store" }); } catch { r = null; }
  const list = r?.results ?? [];
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-5xl">
        <h1 className="text-2xl font-bold mb-4">لاگ ممیزی</h1>
        <p className="text-sm text-[var(--color-text-muted)] mb-3">
          نمای محلی — برای جست‌وجوی کامل، به Kibana مراجعه کنید: <code>kibana.{`{domain}`}</code>
        </p>
        {list.map((e) => (
          <Card key={e.id} className="mb-2">
            <CardBody className="flex items-center justify-between text-sm">
              <div>
                <code dir="ltr" className="text-xs">{e.kind}</code>
                <p className="text-xs text-[var(--color-text-muted)]">
                  {new Date(e.created_at).toLocaleString("fa-IR")} · {e.target_type}:{e.target_id}
                </p>
              </div>
              <Badge tone={e.severity === "critical" ? "danger"
                : e.severity === "warning" ? "warning"
                : e.severity === "error" ? "danger" : "neutral"}>{e.severity}</Badge>
            </CardBody>
          </Card>
        ))}
      </main>
      <Footer />
    </>
  );
}
