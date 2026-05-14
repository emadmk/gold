import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, toPersianNumber } from "@/lib/format";

type Product = {
  id: string;
  vendor: { shop_slug: string; shop_name: string };
  category: string;
  title: string;
  slug: string;
  weight_mg: number;
  karat: number;
  image_urls: string[];
};

const CAT_LABEL: Record<string, string> = {
  melted: "طلای آب‌شده",
  jewelry: "طلای ساخته‌شده",
  coin: "سکه",
  silver: "نقره",
};

export default async function MarketplacePage() {
  let data: { results: Product[] } | null = null;
  try {
    data = await api<{ results: Product[] }>("/marketplace/products", { cache: "no-store" });
  } catch {
    data = null;
  }
  const products = data?.results ?? [];
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold mb-4">مارکت‌پلیس</h1>
        {products.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">محصولی برای نمایش نیست.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {products.map((p) => (
              <Link key={p.id} href={`/marketplace/${p.slug}`}>
                <Card className="hover:shadow-[var(--shadow-card-hover)] transition h-full">
                  <CardBody className="space-y-2">
                    {p.image_urls?.[0] ? (
                      <img src={p.image_urls[0]} alt={p.title}
                        className="w-full h-32 object-cover rounded-md" />
                    ) : (
                      <div className="w-full h-32 rounded-md bg-[var(--color-gold-light)] flex items-center justify-center text-3xl">
                        {p.category === "coin" ? "🪙" : "🥇"}
                      </div>
                    )}
                    <div className="flex justify-between items-start">
                      <p className="font-bold text-sm">{p.title}</p>
                      <Badge tone="gold">{CAT_LABEL[p.category]}</Badge>
                    </div>
                    <p className="text-xs text-[var(--color-text-muted)]">
                      {formatMg(p.weight_mg)} · عیار {toPersianNumber(p.karat)}
                    </p>
                    <p className="text-xs text-[var(--color-primary)]">
                      {p.vendor.shop_name}
                    </p>
                  </CardBody>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
