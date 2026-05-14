/* Home — SSR, GSM.ir-style.
 *
 * Sections, top to bottom:
 *   1. Promotional banner row (credit / fast onboarding)
 *   2. Header (sticky)
 *   3. Hero grid — main banner + 2 side cards (gold buy, sell)
 *   4. Trust badges
 *   5. Category icon grid
 *   6. Featured-products carousel (latest marketplace listings)
 *   7. Service strip
 *   8. Footer
 */
import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

export const dynamic = "force-dynamic";

type Product = {
  id: string;
  title: string;
  slug: string;
  weight_mg: number;
  karat: number;
  category: string;
  image_urls: string[];
  computed_price_rial?: number;
  vendor: { shop_name: string };
};

const CATEGORIES = [
  { code: "ingot", label: "شمش طلا", emoji: "🥇" },
  { code: "coin", label: "سکه", emoji: "🪙" },
  { code: "jewelry", label: "طلای ساخته‌شده", emoji: "💍" },
  { code: "melted", label: "آب‌شده", emoji: "✨" },
  { code: "silver", label: "نقره", emoji: "🔘" },
  { code: "leather_bracelet", label: "دستبند چرمی", emoji: "📿" },
];

const SERVICES = [
  {
    icon: "🔒",
    title: "پرداخت امن",
    body: "تمام تراکنش‌ها روی TLS و درگاه‌های بانکی معتبر.",
  },
  {
    icon: "⚖️",
    title: "قیمت منصفانه",
    body: "قیمت لحظه‌ای از مرجع رسمی tgju؛ بدون اجرت روی طلای آب‌شده.",
  },
  {
    icon: "🚚",
    title: "تحویل سریع",
    body: "ارسال با پست پیشتاز، تیپاکس و اسنپ‌باکس.",
  },
  {
    icon: "✅",
    title: "ضمانت اصالت",
    body: "همه‌ی فروشندگان دارای پروانه اتحادیه‌ی طلا و جواهر.",
  },
];

export default async function HomePage() {
  let products: Product[] = [];
  try {
    const r = await api<{ results: Product[] }>(
      "/marketplace/products?sort=newest",
      { cache: "no-store" },
    );
    products = (r.results ?? []).slice(0, 8);
  } catch {
    products = [];
  }

  return (
    <>
      {/* Slim promo bar (above header — like GSM "وام خرید گوشی") */}
      <div className="bg-[var(--color-secondary)] text-white text-xs">
        <div className="container mx-auto px-4 py-2 flex items-center justify-center gap-3 flex-wrap">
          <span>اعتبار خرید طلا تا ۱۰۰ میلیون تومان بدون ضامن</span>
          <Link
            href="/legal/gold-guide"
            className="bg-white/20 hover:bg-white/30 transition px-3 py-1 rounded-full"
          >
            دریافت اعتبار
          </Link>
        </div>
      </div>

      <Header />

      <main className="container mx-auto px-4 py-6 space-y-10">
        {/* ============== HERO GRID ============== */}
        <section className="grid md:grid-cols-3 gap-3">
          <div className="md:col-span-2 bg-hero-gold rounded-2xl p-6 md:p-10 relative overflow-hidden">
            <div className="max-w-md">
              <h1 className="text-2xl md:text-3xl font-bold leading-tight">
                خرید و فروش لحظه‌ای طلای ۱۸ عیار،
                <br />
                از همین <span className="text-[var(--color-gold-deep)]">۱ میلی‌گرم</span>
              </h1>
              <p className="mt-3 text-sm text-[var(--color-text-muted)] leading-7">
                کیف پول دیجیتال طلا، قیمت لحظه‌ای، تحویل فیزیکی شمش‌های ۱، ۲، ۵
                و ۱۰ گرمی، و یک مارکت‌پلیس تخصصی برای فروشندگان معتبر.
              </p>
              <div className="mt-5 flex gap-2">
                <Link
                  href="/signup"
                  className="px-5 py-2.5 rounded-xl bg-[var(--color-primary)] text-white font-medium hover:bg-[var(--color-primary-hover)] transition"
                >
                  همین حالا شروع کن
                </Link>
                <Link
                  href="/prices"
                  className="px-5 py-2.5 rounded-xl bg-white/80 hover:bg-white transition"
                >
                  مشاهده قیمت‌ها
                </Link>
              </div>
            </div>
            <div className="absolute -left-6 -bottom-6 text-[160px] opacity-20 select-none pointer-events-none">
              🥇
            </div>
          </div>

          <div className="grid grid-rows-2 gap-3">
            <Link
              href="/trade/buy"
              className="bg-hero-blue rounded-2xl p-5 hover:shadow-[var(--shadow-card-hover)] transition flex items-center justify-between"
            >
              <div>
                <p className="font-bold">خرید طلا</p>
                <p className="text-xs text-[var(--color-text-muted)] mt-1">
                  از ۱ میلی‌گرم با کیف پول دیجیتال
                </p>
              </div>
              <span className="text-4xl">💰</span>
            </Link>
            <Link
              href="/trade/sell"
              className="bg-hero-purple rounded-2xl p-5 hover:shadow-[var(--shadow-card-hover)] transition flex items-center justify-between"
            >
              <div>
                <p className="font-bold">فروش طلا</p>
                <p className="text-xs text-[var(--color-text-muted)] mt-1">
                  واریز فوری مبلغ به کیف پول ریالی
                </p>
              </div>
              <span className="text-4xl">💸</span>
            </Link>
          </div>
        </section>

        {/* ============== TRUST BADGES ============== */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {SERVICES.map((s) => (
            <Card key={s.title}>
              <CardBody className="text-center space-y-2">
                <div className="text-3xl">{s.icon}</div>
                <p className="font-bold">{s.title}</p>
                <p className="text-xs text-[var(--color-text-muted)] leading-6">
                  {s.body}
                </p>
              </CardBody>
            </Card>
          ))}
        </section>

        {/* ============== CATEGORIES ============== */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold">دسته‌بندی محصولات طلا</h2>
            <Link href="/marketplace" className="text-sm text-[var(--color-primary)]">
              مشاهده همه ›
            </Link>
          </div>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
            {CATEGORIES.map((c) => (
              <Link
                key={c.code}
                href={`/marketplace?category=${c.code}`}
                className="bg-white border border-[var(--color-border)] rounded-2xl p-4 text-center hover:shadow-[var(--shadow-card-hover)] transition"
              >
                <div className="text-4xl mb-2">{c.emoji}</div>
                <p className="text-sm font-medium">{c.label}</p>
              </Link>
            ))}
          </div>
        </section>

        {/* ============== INSTALLMENT BANNER ============== */}
        <Link
          href="/legal/gold-guide"
          className="block bg-gradient-to-l from-[var(--color-secondary)] to-[#9d83ff] rounded-2xl p-6 md:p-8 text-white relative overflow-hidden"
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h3 className="text-xl font-bold">خرید اقساطی طلا، آسان‌تر از همیشه</h3>
              <p className="text-sm opacity-90 mt-1">
                تا سقف ۱۰۰ میلیون تومان بدون نیاز به ضامن
              </p>
            </div>
            <span className="bg-white/20 hover:bg-white/30 transition px-5 py-2 rounded-xl text-sm font-medium">
              درخواست اعتبار
            </span>
          </div>
          <div className="absolute -bottom-6 -left-2 text-[120px] opacity-15 select-none pointer-events-none">
            💳
          </div>
        </Link>

        {/* ============== LATEST PRODUCTS ============== */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold">جدیدترین محصولات مارکت‌پلیس</h2>
            <Link href="/marketplace" className="text-sm text-[var(--color-primary)]">
              مشاهده همه ›
            </Link>
          </div>
          {products.length === 0 ? (
            <Card>
              <CardBody>
                <p className="text-sm text-[var(--color-text-muted)] text-center">
                  هنوز محصولی منتشر نشده است.{" "}
                  <Link href="/vendor/apply" className="text-[var(--color-primary)]">
                    فروشنده شوید
                  </Link>
                </p>
              </CardBody>
            </Card>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {products.map((p) => (
                <Link key={p.id} href={`/marketplace/${p.slug}`}>
                  <Card className="h-full hover:shadow-[var(--shadow-card-hover)] transition">
                    <CardBody className="space-y-2">
                      {p.image_urls?.[0] ? (
                        <img
                          src={p.image_urls[0]}
                          alt={p.title}
                          className="w-full h-36 object-cover rounded-md"
                        />
                      ) : (
                        <div className="w-full h-36 rounded-md bg-hero-gold flex items-center justify-center text-4xl">
                          {p.category === "coin" ? "🪙" : "🥇"}
                        </div>
                      )}
                      <p className="font-bold text-sm line-clamp-1">{p.title}</p>
                      <p className="text-xs text-[var(--color-text-muted)]">
                        {formatMg(p.weight_mg)} · عیار {toPersianNumber(p.karat)}
                      </p>
                      <p className="text-xs text-[var(--color-primary)] line-clamp-1">
                        {p.vendor.shop_name}
                      </p>
                      {p.computed_price_rial !== undefined && (
                        <p className="text-sm font-bold text-[var(--color-gold-deep)]">
                          {formatRial(p.computed_price_rial)}
                        </p>
                      )}
                    </CardBody>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </section>

        {/* ============== TRUST BAR ============== */}
        <section className="bg-white border border-[var(--color-border)] rounded-2xl p-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-xs">
          <div className="space-y-1">
            <p className="text-2xl">🛡️</p>
            <p className="font-bold">eNamad + Samandehi</p>
            <p className="text-[var(--color-text-muted)]">نمادهای رسمی</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl">💎</p>
            <p className="font-bold">طلای ۱۸ عیار آب‌شده</p>
            <p className="text-[var(--color-text-muted)]">۷۵۰ از ۱۰۰۰</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl">⏱️</p>
            <p className="font-bold">قیمت لحظه‌ای</p>
            <p className="text-[var(--color-text-muted)]">به‌روزرسانی هر ۳۰ ثانیه</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl">📞</p>
            <p className="font-bold">پشتیبانی ۷ روز هفته</p>
            <p className="text-[var(--color-text-muted)]">۹ صبح تا ۹ شب</p>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
