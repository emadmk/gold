/* PDP — Server-Side-Rendered.
 *
 * Fetches the product on the server, hydrates a small Gallery + add-to-cart
 * client component for interactivity.
 */
import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { PDPInteractive } from "@/components/PDPInteractive";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

export const dynamic = "force-dynamic";

type Product = {
  id: string;
  title: string;
  description: string;
  weight_mg: number;
  karat: number;
  category: string;
  sub_category_code: string;
  brand: string;
  sku: string;
  image_urls: string[];
  metadata: {
    accessory_prices_rial?: number[];
    weight_variants?: number[];
    gallery?: string[];
    video_url?: string;
  };
  shipping_cost_rial: number;
  shipping_methods: string[];
  computed_price_rial: number;
  stock: number;
  is_low_stock: boolean;
  discount_pct: string;
  vendor: { shop_name: string; shop_slug: string };
};

const CAT_LABEL: Record<string, string> = {
  melted: "طلای آب‌شده",
  jewelry: "طلای ساخته‌شده",
  coin: "سکه",
  silver: "نقره",
  ingot: "شمش طلا",
  leather_bracelet: "دستبند چرمی",
};

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  let p: Product | null = null;
  try {
    p = await api<Product>(`/marketplace/products/${slug}`, { cache: "no-store" });
  } catch {
    p = null;
  }

  if (!p) {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-10">محصول یافت نشد.</main>
        <Footer />
      </>
    );
  }

  const accessories = p.metadata?.accessory_prices_rial ?? [];
  const accessoriesTotal = accessories.reduce((a, b) => a + b, 0);
  const gallery = p.metadata?.gallery ?? p.image_urls ?? [];
  const discount = Number(p.discount_pct) > 0
    ? Math.round(p.computed_price_rial * Number(p.discount_pct))
    : 0;
  const priceAfterDiscount = p.computed_price_rial - discount;

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-6 max-w-5xl">
        <nav className="text-xs text-[var(--color-text-muted)] mb-4 flex items-center gap-2">
          <Link href="/">خانه</Link>
          <span>›</span>
          <Link href="/marketplace">مارکت‌پلیس</Link>
          <span>›</span>
          <Link href={`/marketplace?category=${p.category}`}>
            {CAT_LABEL[p.category] ?? p.category}
          </Link>
          <span>›</span>
          <span className="text-[var(--color-text)]">{p.title}</span>
        </nav>

        <div className="grid md:grid-cols-2 gap-6">
          <PDPInteractive
            product={{
              id: p.id,
              title: p.title,
              gallery,
              computed_price_rial: p.computed_price_rial,
              stock: p.stock,
            }}
          />

          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">{p.title}</h1>
              <Badge tone="gold">{CAT_LABEL[p.category] ?? p.category}</Badge>
            </div>
            <p className="text-[var(--color-text-muted)]">
              فروشنده:{" "}
              <Link href={`/vendors/${p.vendor.shop_slug}`} className="text-[var(--color-primary)]">
                {p.vendor.shop_name}
              </Link>
            </p>
            <Card>
              <CardBody className="space-y-2">
                <p><span className="text-[var(--color-text-muted)]">کد محصول:</span> <span dir="ltr">{p.sku}</span></p>
                <p><span className="text-[var(--color-text-muted)]">برند:</span> {p.brand || "—"}</p>
                <p><span className="text-[var(--color-text-muted)]">عیار:</span> {toPersianNumber(p.karat)}</p>
                <p>
                  <span className="text-[var(--color-text-muted)]">وزن:</span>{" "}
                  {formatMg(p.weight_mg)}{" "}
                  <span className="text-xs text-[var(--color-text-muted)]">
                    (با دو رقم اعشار: {toPersianNumber((p.weight_mg / 1000).toFixed(2))} گرم)
                  </span>
                </p>
                {accessories.length > 0 && (
                  <p>
                    <span className="text-[var(--color-text-muted)]">قیمت متعلقات (سنگ/چرم):</span>{" "}
                    {formatRial(accessoriesTotal)}
                  </p>
                )}
                <p>
                  <span className="text-[var(--color-text-muted)]">موجودی:</span>{" "}
                  {p.stock > 0 ? toPersianNumber(p.stock) : "ناموجود"}
                </p>
                {p.is_low_stock && (
                  <p className="text-[var(--color-warning)] font-bold">
                    تنها چند عدد باقی مانده
                  </p>
                )}
              </CardBody>
            </Card>

            <Card>
              <CardBody className="space-y-1">
                {discount > 0 ? (
                  <>
                    <p className="text-xs text-[var(--color-text-muted)] line-through">
                      {formatRial(p.computed_price_rial)}
                    </p>
                    <p className="text-2xl font-bold text-[var(--color-primary)]">
                      {formatRial(priceAfterDiscount)}
                    </p>
                    <Badge tone="success">
                      {toPersianNumber((Number(p.discount_pct) * 100).toFixed(0))}% تخفیف
                    </Badge>
                  </>
                ) : (
                  <p className="text-2xl font-bold text-[var(--color-primary)]">
                    {formatRial(p.computed_price_rial)}
                  </p>
                )}
                <p className="text-xs text-[var(--color-text-muted)]">
                  قیمت در لحظه بر اساس قیمت روز طلای ۱۸ عیار محاسبه می‌شود.
                </p>
              </CardBody>
            </Card>

            <Card>
              <CardBody className="text-xs space-y-1">
                <p className="font-bold">ارسال</p>
                <p>هزینه ارسال: {formatRial(p.shipping_cost_rial)}</p>
                {p.shipping_methods.length > 0 && (
                  <p>روش‌ها: {p.shipping_methods.join(" · ")}</p>
                )}
              </CardBody>
            </Card>

            <p className="text-xs">
              <Link href="/legal/gold-rules" className="text-[var(--color-primary)]">
                قوانین خرید طلا (شامل ارسال و مرجوعی)
              </Link>
            </p>
          </div>
        </div>

        {p.description && (
          <section className="mt-8 leading-7 text-sm">
            <h2 className="font-bold mb-2">توضیحات محصول</h2>
            <p>{p.description}</p>
          </section>
        )}
      </main>
      <Footer />
    </>
  );
}
