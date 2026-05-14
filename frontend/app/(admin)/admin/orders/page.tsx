import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api, type Order } from "@/lib/api";
import { formatRial } from "@/lib/format";

export default async function AdminOrdersPage() {
  let res: { results: Order[] } | null = null;
  try { res = await api<{ results: Order[] }>("/admin/orders", { cache: "no-store" }); }
  catch { res = null; }
  const list = res?.results ?? [];
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-5xl">
        <h1 className="text-2xl font-bold mb-4">سفارش‌های همه کاربران</h1>
        {list.length === 0 ? <p>هیچ سفارشی نیست.</p> : (
          <div className="space-y-2">
            {list.map((o) => (
              <Card key={o.id}><CardBody className="flex justify-between text-sm">
                <span dir="ltr">{o.order_number}</span>
                <span>{o.kind}</span>
                <Badge tone={o.state === "completed" ? "success" : "primary"}>{o.state}</Badge>
                <span>{formatRial(o.rial_amount)}</span>
              </CardBody></Card>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
