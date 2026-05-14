import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function HomePage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10">
        <section className="grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold leading-tight">
              خرید و فروش لحظه‌ای طلای ۱۸ عیار،
              <br />
              از همین <span className="text-[var(--color-gold)]">۱ میلی‌گرم</span>.
            </h1>
            <p className="mt-4 text-[var(--color-text-muted)] leading-7">
              کیف پول دیجیتال طلا، قیمت لحظه‌ای، تحویل فیزیکی شمش ۱، ۲، ۵ و ۱۰ گرمی،
              و یک مارکت‌پلیس تخصصی برای فروشندگان معتبر.
            </p>
            <div className="mt-6 flex gap-3">
              <Link
                href="/signup"
                className="px-6 py-3 rounded-xl bg-[var(--color-primary)] text-white font-medium hover:bg-[var(--color-primary-hover)] transition"
              >
                همین حالا شروع کن
              </Link>
              <Link
                href="/prices"
                className="px-6 py-3 rounded-xl border border-[var(--color-border)] hover:bg-[var(--color-bg-alt)] transition"
              >
                مشاهده قیمت‌ها
              </Link>
            </div>
          </div>
          <div className="aspect-square rounded-2xl bg-gradient-to-br from-[var(--color-primary-light)] to-[var(--color-gold-light)] flex items-center justify-center text-9xl">
            🥇
          </div>
        </section>

        <section className="grid md:grid-cols-3 gap-4 mt-16">
          {[
            { t: "بدون اجرت", d: "خرید طلای آب‌شده ۱۸ عیار بدون اجرت ساخت." },
            { t: "از ۱ میلی‌گرم", d: "خرید/فروش هر مقدار طلا — حتی کسری از یک گرم." },
            { t: "تحویل فیزیکی", d: "شمش‌های ۱، ۲، ۵ و ۱۰ گرمی، ضرب و پلمپ‌شده در محل." },
          ].map(({ t, d }) => (
            <div
              key={t}
              className="rounded-2xl bg-[var(--color-card)] border border-[var(--color-border)] p-5"
            >
              <h3 className="font-bold mb-1">{t}</h3>
              <p className="text-sm text-[var(--color-text-muted)]">{d}</p>
            </div>
          ))}
        </section>
      </main>
      <Footer />
    </>
  );
}
