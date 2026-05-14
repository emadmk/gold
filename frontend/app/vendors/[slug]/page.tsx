import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, toPersianNumber } from "@/lib/format";

type Vendor = {
  id: string;
  shop_name: string;
  shop_slug: string;
  state: string;
  rating: number;
  total_sales: number;
  description: string;
  city: string;
};

type Product = {
  id: string;
  title: string;
  slug: string;
  category: string;
  weight_mg: number;
  karat: number;
  vendor: { shop_slug: string };
};

const CAT_LABEL: Record<string, string> = {
  melted: "آب‌شده",
  jewelry: "ساخته‌شده",
  coin: "سکه",
  silver: "نقره",
};

export default async function VendorPublicPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  let vendor: Vendor | null = null;
  let products: Product[] = [];
  try {
    vendor = await api<Vendor>(`/marketplace/vendors/${slug}`, { cache: "no-store" });
    const all = await api<{ results: Product[] }>("/marketplace/products", { cache: "no-store" });
    products = (all.results ?? []).filter((p) => p.vendor.shop_slug === slug);
  } catch {
    vendor = null;
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl space-y-4">
        {!vendor ? (
          <p>فروشگاه یافت نشد.</p>
        ) : (
          <>
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <h1 className="text-2xl font-bold">{vendor.shop_name}</h1>
                    <p className="text-sm text-[var(--color-text-muted)]">
                      {vendor.city} · امتیاز {toPersianNumber(vendor.rating)} · فروش {toPersianNumber(vendor.total_sales)}
                    </p>
                  </div>
                  <Badge tone={vendor.state === "approved" ? "success" : "neutral"}>
                    {vendor.state}
                  </Badge>
                </div>
              </CardHeader>
              <CardBody>
                <p className="text-sm">{vendor.description || "توضیحاتی ثبت نشده."}</p>
              </CardBody>
            </Card>

            <h2 className="font-bold mt-6">محصولات فروشگاه</h2>
            {products.length === 0 ? (
              <p className="text-sm text-[var(--color-text-muted)]">
                محصول فعالی برای این فروشگاه وجود ندارد.
              </p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {products.map((p) => (
                  <Link key={p.id} href={`/marketplace/${p.slug}`}>
                    <Card className="hover:shadow-[var(--shadow-card-hover)] transition">
                      <CardBody>
                        <p className="font-bold text-sm">{p.title}</p>
                        <p className="text-xs text-[var(--color-text-muted)]">
                          {CAT_LABEL[p.category] ?? p.category} · {formatMg(p.weight_mg)}
                        </p>
                      </CardBody>
                    </Card>
                  </Link>
                ))}
              </div>
            )}
          </>
        )}
      </main>
      <Footer />
    </>
  );
}
