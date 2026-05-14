"use client";

import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { useMe } from "@/hooks/useMe";

type Check = {
  ok: boolean | "pending";
  label: string;
  detail?: string;
};

async function probe(path: string): Promise<Check> {
  try {
    const r = await fetch(path, { credentials: "include" });
    return {
      ok: r.ok,
      label: path,
      detail: `HTTP ${r.status}`,
    };
  } catch (e) {
    return { ok: false, label: path, detail: (e as Error).message };
  }
}

export default function StatusPage() {
  const me = useMe();
  const [checks, setChecks] = useState<Check[]>([
    { ok: "pending", label: "/api/v1/health/" },
    { ok: "pending", label: "/api/v1/prices" },
    { ok: "pending", label: "/api/v1/marketplace/products" },
    { ok: "pending", label: "/api/v1/marketplace/facets" },
    { ok: "pending", label: "/api/v1/blog/posts" },
  ]);
  const [snapshot, setSnapshot] = useState<Record<string, number>>({});

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      probe("/health/"),
      probe("/api/v1/prices"),
      probe("/api/v1/marketplace/products"),
      probe("/api/v1/marketplace/facets"),
      probe("/api/v1/blog/posts"),
    ]).then((rs) => {
      if (!cancelled) setChecks(rs);
    });
    fetch("/api/v1/prices", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (!cancelled && j?.data) setSnapshot(j.data);
      })
      .catch(() => null);
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">وضعیت سامانه</h1>
        <p className="text-xs text-[var(--color-text-muted)]">
          این صفحه برای رفع اشکال طراحی شده — هر زمان چیزی کار نکند، اینجا
          سریع‌ترین راه فهمیدن این است که کدام لایه خراب است.
        </p>

        <Card>
          <CardHeader>
            <h2 className="font-bold">احراز هویت شما</h2>
          </CardHeader>
          <CardBody className="text-sm space-y-1">
            {me.status === "loading" && <p>در حال بررسی…</p>}
            {me.status === "anonymous" && (
              <Badge tone="warning">واردنشده — برای دسترسی به امکانات وارد شوید</Badge>
            )}
            {me.status === "authenticated" && (
              <>
                <p>
                  <Badge tone="success">واردشده</Badge> &nbsp;
                  <span dir="ltr">{me.user.phone}</span>
                </p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {me.user.is_verified ? <Badge tone="success">KYC</Badge> : <Badge tone="warning">بدون KYC</Badge>}
                  {me.user.is_vendor && <Badge tone="primary">فروشنده</Badge>}
                  {me.user.is_staff && <Badge tone="gold">staff</Badge>}
                  {me.user.is_superuser && <Badge tone="gold">superuser</Badge>}
                  {me.user.is_frozen && <Badge tone="danger">مسدود</Badge>}
                </div>
              </>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="font-bold">دسترسی به API</h2>
          </CardHeader>
          <CardBody className="space-y-2 text-sm">
            {checks.map((c) => (
              <div key={c.label} className="flex justify-between items-center">
                <code dir="ltr" className="text-xs">{c.label}</code>
                {c.ok === "pending" ? (
                  <Badge tone="neutral">…</Badge>
                ) : c.ok ? (
                  <Badge tone="success">{c.detail}</Badge>
                ) : (
                  <Badge tone="danger">{c.detail}</Badge>
                )}
              </div>
            ))}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="font-bold">آخرین قیمت‌ها</h2>
          </CardHeader>
          <CardBody className="text-sm">
            {Object.keys(snapshot).length === 0 ? (
              <p className="text-[var(--color-text-muted)]">
                هنوز قیمتی در کش نیست. در محیط dev اگر کرالر اجرا نشده باشد، با
                دستور <code dir="ltr">make seed</code> یا{" "}
                <code dir="ltr">python manage.py shell -c &quot;from apps.pricing.tasks import crawl_all; print(crawl_all())&quot;</code>{" "}
                یک snapshot بسازید.
              </p>
            ) : (
              <ul className="space-y-1">
                {Object.entries(snapshot).map(([k, v]) => (
                  <li key={k} className="flex justify-between">
                    <code dir="ltr" className="text-xs">{k}</code>
                    <span dir="ltr">{Math.floor(v / 10).toLocaleString("fa-IR")} تومان</span>
                  </li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="font-bold">راهنمای رفع اشکال سریع</h2>
          </CardHeader>
          <CardBody className="text-sm space-y-2">
            <p>
              <b>دکمه‌ها کار نمی‌کنند؟</b> یک Hard-Refresh (Ctrl+Shift+R) بزنید
              تا کش جاوااسکریپت بازنشانی شود.
            </p>
            <p>
              <b>قیمت‌ها &quot;—&quot; هستند؟</b> کرالر هنوز اجرا نشده یا
              tgju.org از داخل کانتینر در دسترس نیست. در پنل Django Admin،
              قسمت Price ticks یک رکورد دستی اضافه کنید یا کرالر را اجرا کنید.
            </p>
            <p>
              <b>صفحه ادمین خالی است؟</b> مطمئن شوید با کاربری وارد شده‌اید که
              <code dir="ltr"> is_staff=True </code>است (مثلاً سوپرادمین که{" "}
              <code dir="ltr">seed_dev</code> می‌سازد).
            </p>
            <p>
              <b>ستون marketplace_product.brand وجود ندارد؟</b> مهاجرت‌ها اجرا
              نشده‌اند. دستور{" "}
              <code dir="ltr">docker compose exec backend python manage.py migrate</code>{" "}
              را بزنید.
            </p>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
