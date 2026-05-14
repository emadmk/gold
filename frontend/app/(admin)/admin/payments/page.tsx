import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatRial } from "@/lib/format";

type Payment = {
  id: string;
  order: string;
  gateway: string;
  amount_rial: number;
  state: string;
  ref_id: string;
  card_pan_masked: string;
  created_at: string;
};

const TONE: Record<string, "primary" | "success" | "warning" | "danger" | "neutral"> = {
  pending: "neutral",
  redirected: "primary",
  succeeded: "success",
  failed: "danger",
  cancelled: "neutral",
  expired: "warning",
};

export default async function AdminPaymentsPage() {
  let r: { results: Payment[] } | null = null;
  try {
    r = await api<{ results: Payment[] }>("/admin/payments", { cache: "no-store" });
  } catch {
    r = null;
  }
  const list = r?.results ?? [];
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-5xl">
        <h1 className="text-2xl font-bold mb-4">تراکنش‌های درگاه</h1>
        {list.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">
            تراکنشی ثبت نشده.
          </p>
        ) : (
          list.map((p) => (
            <Card key={p.id} className="mb-2">
              <CardBody className="flex justify-between text-sm">
                <span dir="ltr">{p.gateway}</span>
                <Badge tone={TONE[p.state] ?? "neutral"}>{p.state}</Badge>
                <span>{formatRial(p.amount_rial)}</span>
                <span dir="ltr" className="text-xs">{p.ref_id || "—"}</span>
                <span dir="ltr" className="text-xs">{p.card_pan_masked || "—"}</span>
                <span className="text-xs">
                  {new Date(p.created_at).toLocaleString("fa-IR")}
                </span>
              </CardBody>
            </Card>
          ))
        )}
      </main>
      <Footer />
    </>
  );
}
