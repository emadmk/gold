"use client";

import Link from "next/link";
import { useEffect } from "react";

import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    if (typeof console !== "undefined") {
      console.error("[error.tsx]", error);
    }
  }, [error]);

  return (
    <main className="container mx-auto px-4 py-20 max-w-md text-center">
      <Card>
        <CardBody className="space-y-3">
          <div className="text-6xl">⚠️</div>
          <h1 className="text-xl font-bold text-[var(--color-danger)]">
            خطایی در رندر صفحه رخ داد
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            اگر هنوز وارد نشده‌اید، با کلیک روی «ورود» وارد شوید و دوباره
            تلاش کنید. اگر مشکل ادامه دارد، با پشتیبانی تماس بگیرید.
          </p>
          <pre
            dir="ltr"
            className="text-xs bg-[var(--color-bg)] rounded-md px-3 py-2 text-start overflow-auto max-h-32 font-mono"
          >
            {error.message}
            {error.digest ? `\n[digest ${error.digest}]` : ""}
          </pre>
          <div className="flex gap-2 justify-center">
            <Button onClick={reset}>تلاش مجدد</Button>
            <Link
              href="/"
              className="px-5 py-2 rounded-xl border border-[var(--color-border)] text-sm"
            >
              صفحه‌ی اصلی
            </Link>
            <Link
              href="/login"
              className="px-5 py-2 rounded-xl bg-[var(--color-primary)] text-white text-sm"
            >
              ورود
            </Link>
          </div>
        </CardBody>
      </Card>
    </main>
  );
}
