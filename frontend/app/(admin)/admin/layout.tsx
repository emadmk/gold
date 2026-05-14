"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { useMe } from "@/hooks/useMe";

const NAV: { href: string; label: string; icon: string }[] = [
  { href: "/admin", label: "داشبورد", icon: "📊" },
  { href: "/admin/kyc", label: "صف KYC", icon: "🪪" },
  { href: "/admin/users", label: "کاربران", icon: "👥" },
  { href: "/admin/vendors", label: "فروشندگان", icon: "🏪" },
  { href: "/admin/orders", label: "سفارش‌ها", icon: "📦" },
  { href: "/admin/payments", label: "پرداخت‌ها", icon: "💳" },
  { href: "/admin/delivery", label: "صف تحویل", icon: "🚚" },
  { href: "/admin/formulas", label: "فرمول‌ها", icon: "📐" },
  { href: "/admin/settlements", label: "تسویه‌ها", icon: "💼" },
  { href: "/admin/audit", label: "لاگ ممیزی", icon: "🔍" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const me = useMe();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (me.status === "anonymous") {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [me, router, pathname]);

  if (me.status === "loading") {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 text-center text-sm text-[var(--color-text-muted)]">
          در حال بررسی دسترسی…
        </main>
        <Footer />
      </>
    );
  }
  if (me.status === "anonymous") {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 text-center text-sm">
          لطفاً وارد شوید…
        </main>
        <Footer />
      </>
    );
  }

  // me.status === "authenticated"
  const isStaff =
    Boolean((me.user as unknown as { is_staff?: boolean }).is_staff) ||
    Boolean((me.user as unknown as { is_superuser?: boolean }).is_superuser);

  if (!isStaff) {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 text-center space-y-3">
          <div className="text-6xl">🔒</div>
          <h1 className="text-xl font-bold">دسترسی غیرمجاز</h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            این بخش فقط برای ادمین‌های سامانه قابل دسترسی است.
          </p>
          <Link
            href="/dashboard"
            className="inline-block px-5 py-2 rounded-xl bg-[var(--color-primary)] text-white text-sm"
          >
            بازگشت به داشبورد
          </Link>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-6 grid md:grid-cols-[240px_1fr] gap-6">
        <aside className="space-y-2">
          <div className="rounded-xl bg-white border border-[var(--color-border)] p-4">
            <p className="text-xs text-[var(--color-text-muted)]">ادمین</p>
            <p className="font-bold text-sm mt-1">{me.user.phone}</p>
            {me.user.first_name && (
              <p className="text-xs">
                {me.user.first_name} {me.user.last_name}
              </p>
            )}
          </div>
          <nav className="rounded-xl bg-white border border-[var(--color-border)] overflow-hidden">
            {NAV.map((n) => {
              const active = pathname === n.href;
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={`flex items-center gap-2 px-4 py-2.5 text-sm border-b border-[var(--color-border)] last:border-0 ${
                    active
                      ? "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)] font-medium"
                      : "hover:bg-[var(--color-bg)]"
                  }`}
                >
                  <span>{n.icon}</span>
                  <span>{n.label}</span>
                </Link>
              );
            })}
          </nav>
          <a
            href="/admin/"
            className="block text-center text-xs text-[var(--color-text-muted)] mt-3 underline"
          >
            باز کردن Django admin
          </a>
        </aside>
        <section>{children}</section>
      </main>
      <Footer />
    </>
  );
}
