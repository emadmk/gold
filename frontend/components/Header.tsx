import Link from "next/link";

import { PriceTicker } from "./PriceTicker";

const NAV: Array<{ label: string; href: string }> = [
  { label: "خرید طلا", href: "/trade/buy" },
  { label: "فروش طلا", href: "/trade/sell" },
  { label: "مارکت‌پلیس", href: "/marketplace" },
  { label: "تحویل فیزیکی", href: "/delivery" },
  { label: "قیمت لحظه‌ای", href: "/prices" },
  { label: "وبلاگ", href: "/blog" },
  { label: "راهنما", href: "/legal/gold-guide" },
];

export function Header() {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[var(--color-border)] shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
      <PriceTicker />

      {/* Top row: logo · search · auth/cart */}
      <div className="container mx-auto flex items-center gap-4 px-4 py-3">
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <svg width="32" height="32" viewBox="0 0 32 32" aria-hidden>
            <defs>
              <linearGradient id="hdr-g" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#D4AF37" />
                <stop offset="100%" stopColor="#FFD86A" />
              </linearGradient>
            </defs>
            <rect x="2" y="6" width="28" height="20" rx="4" fill="url(#hdr-g)" />
            <text
              x="16" y="22" textAnchor="middle"
              fontFamily="system-ui" fontWeight="900" fontSize="14"
              fill="#1A2540"
            >K</text>
          </svg>
          <span className="font-bold text-lg leading-none">
            Keyhan<span className="text-[var(--color-gold)]">Gold</span>
          </span>
        </Link>

        {/* Search */}
        <form
          action="/marketplace"
          method="GET"
          className="flex-1 max-w-2xl hidden md:block"
        >
          <label className="relative block">
            <span className="absolute inset-y-0 right-3 flex items-center text-[var(--color-text-muted)]">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="7" />
                <path d="M21 21l-3.5-3.5" />
              </svg>
            </span>
            <input
              name="q"
              type="search"
              placeholder="جست‌وجو در محصولات طلا و جواهر…"
              className="w-full rounded-xl bg-[var(--color-bg)] border border-[var(--color-border)] pr-10 pl-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </label>
        </form>

        <div className="flex items-center gap-2 shrink-0">
          <Link
            href="/cart"
            className="hidden sm:inline-flex items-center gap-1 px-3 py-2 rounded-lg border border-[var(--color-border)] text-sm hover:bg-[var(--color-bg)]"
            aria-label="سبد خرید"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="9" cy="21" r="1.5" />
              <circle cx="18" cy="21" r="1.5" />
              <path d="M3 4h2l2.4 11.5a2 2 0 0 0 2 1.5h8.6a2 2 0 0 0 2-1.5L22 7H6" />
            </svg>
            <span>سبد</span>
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center px-4 py-2 rounded-xl bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-hover)] transition"
          >
            ورود / ثبت‌نام
          </Link>
        </div>
      </div>

      {/* Bottom row: nav links */}
      <nav className="border-t border-[var(--color-border)] bg-white">
        <div className="container mx-auto px-4 flex items-center gap-1 overflow-x-auto no-scrollbar text-sm">
          {NAV.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className="px-3 py-3 whitespace-nowrap text-[var(--color-text)] hover:text-[var(--color-primary)]"
            >
              {n.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
