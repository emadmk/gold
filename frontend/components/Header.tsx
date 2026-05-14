import Link from "next/link";

import { PriceTicker } from "./PriceTicker";

export function Header() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-md bg-white/85 border-b border-[var(--color-border)]">
      <PriceTicker />
      <div className="container mx-auto flex items-center justify-between gap-4 py-3 px-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="font-bold text-lg text-[var(--color-text)]">
            KeyhanGold<span className="text-[var(--color-gold)]">.</span>
          </span>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link href="/trade/buy">خرید طلا</Link>
          <Link href="/trade/sell">فروش طلا</Link>
          <Link href="/marketplace">مارکت‌پلیس</Link>
          <Link href="/prices">قیمت لحظه‌ای</Link>
          <Link href="/about">درباره ما</Link>
        </nav>
        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="px-4 py-2 rounded-lg bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-hover)]"
          >
            ورود / ثبت‌نام
          </Link>
        </div>
      </div>
    </header>
  );
}
