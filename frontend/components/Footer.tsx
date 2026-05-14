import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-[var(--color-footer)] text-[var(--color-footer-text)] mt-16">
      <div className="container mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm">
        <div>
          <h3 className="text-white font-bold mb-3">درباره KeyhanGold</h3>
          <p>پلتفرم خرید و فروش آنلاین طلای ۱۸ عیار، نقره ۹۹۹، سکه و جواهر — مدل میلی‌گرم با کیف پول دیجیتال.</p>
        </div>
        <div>
          <h3 className="text-white font-bold mb-3">دسترسی سریع</h3>
          <ul className="space-y-2">
            <li><Link href="/trade/buy">خرید طلا</Link></li>
            <li><Link href="/trade/sell">فروش طلا</Link></li>
            <li><Link href="/delivery">تحویل فیزیکی</Link></li>
            <li><Link href="/marketplace">مارکت‌پلیس</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="text-white font-bold mb-3">قوانین</h3>
          <ul className="space-y-2">
            <li><Link href="/terms">قوانین و مقررات</Link></li>
            <li><Link href="/privacy">حریم خصوصی</Link></li>
            <li><Link href="/faq">سؤالات متداول</Link></li>
            <li><Link href="/contact">تماس با ما</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="text-white font-bold mb-3">نمادهای اعتماد</h3>
          <div className="flex gap-2 opacity-80">
            <div className="bg-white/10 rounded-md px-3 py-2 text-xs">eNamad</div>
            <div className="bg-white/10 rounded-md px-3 py-2 text-xs">Samandehi</div>
          </div>
        </div>
      </div>
      <div className="border-t border-white/10 py-4 text-center text-xs">
        © {new Date().getFullYear()} KeyhanGold — تمام حقوق محفوظ است.
      </div>
    </footer>
  );
}
