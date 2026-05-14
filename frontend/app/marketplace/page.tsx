/* PLP — Server-Side-Rendered.
 *
 * Initial query params come from the URL searchParams (so the server
 * can render the right filter state for SEO and crawlers); a small
 * `<MarketplaceFilters />` client component then re-fetches when the
 * user toggles a filter. The initial product grid below is rendered
 * server-side from the same query.
 */
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { MarketplaceFilters } from "@/components/MarketplaceFilters";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";
import Link from "next/link";

export const dynamic = "force-dynamic"; // ensure SSR per request

type Product = {
  id: string;
  vendor: { shop_slug: string; shop_name: string };
  category: string;
  sub_category_code: string;
  brand: string;
  title: string;
  slug: string;
  weight_mg: number;
  karat: number;
  image_urls: string[];
  is_low_stock: boolean;
  discount_pct: string;
  computed_price_rial?: number;
};

type Facets = {
  weight_mg_min: number;
  weight_mg_max: number;
  brands: string[];
  sub_categories: string[];
  categories: string[];
  karats: number[];
  weight_buckets: { label: string; min: number; max: number }[];
};

const CAT_LABEL: Record<string, string> = {
  melted: "طلای آب‌شده",
  jewelry: "طلای ساخته‌شده",
  coin: "سکه",
  silver: "نقره",
  ingot: "شمش طلا",
  leather_bracelet: "دستبند چرمی",
};

export default async function MarketplacePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(sp)) {
    if (typeof v === "string" && v) qs.set(k, v);
  }
  let products: Product[] = [];
  let facets: Facets | null = null;
  try {
    const [list, f] = await Promise.all([
      api<{ results: Product[] }>(`/marketplace/products?${qs.toString()}`, { cache: "no-store" }),
      api<Facets>("/marketplace/facets", { cache: "no-store" }),
    ]);
    products = list.results ?? [];
    facets = f;
  } catch {
    /* ignore */
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 grid md:grid-cols-[280px_1fr] gap-6">
        <aside>
          <MarketplaceFilters facets={facets} initial={Object.fromEntries(qs)} />
        </aside>
        <section>
          <h1 className="text-2xl font-bold mb-4">
            مارکت‌پلیس طلا{" "}
            <span className="text-sm font-normal text-[var(--color-text-muted)]">
              ({toPersianNumber(products.length)} محصول)
            </span>
          </h1>
          {products.length === 0 ? (
            <p className="text-sm text-[var(--color-text-muted)]">
              با این فیلترها محصولی یافت نشد.
            </p>
          ) : (
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
              {products.map((p) => (
                <Link key={p.id} href={`/marketplace/${p.slug}`}>
                  <Card className="hover:shadow-[var(--shadow-card-hover)] transition h-full">
                    <CardBody className="space-y-2">
                      {p.image_urls?.[0] ? (
                        <img
                          src={p.image_urls[0]}
                          alt={p.title}
                          className="w-full h-40 object-cover rounded-md"
                        />
                      ) : (
                        <div className="w-full h-40 rounded-md bg-[var(--color-gold-light)] flex items-center justify-center text-4xl">
                          {p.category === "coin" ? "🪙" : "🥇"}
                        </div>
                      )}
                      <div className="flex justify-between items-start">
                        <p className="font-bold text-sm">{p.title}</p>
                        <Badge tone="gold">{CAT_LABEL[p.category] ?? p.category}</Badge>
                      </div>
                      <p className="text-xs text-[var(--color-text-muted)]">
                        {formatMg(p.weight_mg)} · عیار {toPersianNumber(p.karat)}
                        {p.brand ? ` · ${p.brand}` : ""}
                      </p>
                      {p.is_low_stock && (
                        <p className="text-xs text-[var(--color-warning)] font-bold">
                          تنها چند عدد باقی مانده
                        </p>
                      )}
                      {p.computed_price_rial !== undefined && (
                        <p className="text-sm font-bold text-[var(--color-primary)]">
                          {formatRial(p.computed_price_rial)}
                        </p>
                      )}
                      <p className="text-xs text-[var(--color-primary)]">
                        {p.vendor.shop_name}
                      </p>
                    </CardBody>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>
      <Footer />
    </>
  );
}
