"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";

import { Card, CardBody, CardHeader } from "@/components/ui/Card";

type Facets = {
  brands: string[];
  sub_categories: string[];
  categories: string[];
  karats: number[];
  weight_buckets: { label: string; min: number; max: number }[];
} | null;

const CAT_LABEL: Record<string, string> = {
  melted: "طلای آب‌شده",
  jewelry: "طلای ساخته‌شده",
  coin: "سکه",
  silver: "نقره",
  ingot: "شمش طلا",
  leather_bracelet: "دستبند چرمی",
};

const SORTS = [
  ["newest", "جدیدترین"],
  ["cheapest", "ارزان‌ترین"],
  ["expensive", "گران‌ترین"],
  ["bestseller", "پرفروش‌ترین"],
] as const;

export function MarketplaceFilters({
  facets,
  initial,
}: {
  facets: Facets;
  initial: Record<string, string>;
}) {
  const router = useRouter();
  const params = useSearchParams();
  const set = (k: string, v: string | null) => {
    const next = new URLSearchParams(params);
    if (v) next.set(k, v);
    else next.delete(k);
    router.push(`/marketplace?${next.toString()}`);
  };

  const current = useMemo(() => Object.fromEntries(params), [params]);

  if (!facets) {
    return (
      <Card>
        <CardBody>فیلترها بارگذاری نشدند.</CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-3 sticky top-32">
      <Card>
        <CardHeader>
          <h3 className="font-bold text-sm">دسته</h3>
        </CardHeader>
        <CardBody className="space-y-1 text-sm">
          {facets.categories.map((c) => (
            <button
              key={c}
              onClick={() => set("category", current.category === c ? null : c)}
              className={`block w-full text-right px-2 py-1 rounded ${
                current.category === c
                  ? "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)]"
                  : "hover:bg-[var(--color-bg-alt)]"
              }`}
            >
              {CAT_LABEL[c] ?? c}
            </button>
          ))}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="font-bold text-sm">عیار</h3>
        </CardHeader>
        <CardBody className="flex flex-wrap gap-2 text-sm">
          {facets.karats.map((k) => (
            <button
              key={k}
              onClick={() => set("karat", current.karat === String(k) ? null : String(k))}
              className={`px-3 py-1 rounded-md ${
                current.karat === String(k)
                  ? "bg-[var(--color-primary)] text-white"
                  : "bg-[var(--color-bg-alt)]"
              }`}
            >
              {k}
            </button>
          ))}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="font-bold text-sm">وزن</h3>
        </CardHeader>
        <CardBody className="space-y-1 text-sm">
          {facets.weight_buckets.map((b) => {
            const minOk = current.weight_mg_min === String(b.min);
            const maxOk = b.max === 0
              ? !current.weight_mg_max
              : current.weight_mg_max === String(b.max);
            const active = minOk && maxOk;
            return (
              <button
                key={b.label}
                onClick={() => {
                  set("weight_mg_min", String(b.min));
                  set("weight_mg_max", b.max ? String(b.max) : null);
                }}
                className={`block w-full text-right px-2 py-1 rounded ${
                  active
                    ? "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)]"
                    : "hover:bg-[var(--color-bg-alt)]"
                }`}
              >
                {b.label}
              </button>
            );
          })}
        </CardBody>
      </Card>

      {facets.brands.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="font-bold text-sm">برند</h3>
          </CardHeader>
          <CardBody className="space-y-1 text-sm">
            {facets.brands.map((b) => (
              <button
                key={b}
                onClick={() => set("brand", current.brand === b ? null : b)}
                className={`block w-full text-right px-2 py-1 rounded ${
                  current.brand === b
                    ? "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)]"
                    : "hover:bg-[var(--color-bg-alt)]"
                }`}
              >
                {b}
              </button>
            ))}
          </CardBody>
        </Card>
      )}

      <Card>
        <CardHeader>
          <h3 className="font-bold text-sm">مرتب‌سازی</h3>
        </CardHeader>
        <CardBody className="space-y-1 text-sm">
          {SORTS.map(([k, l]) => (
            <button
              key={k}
              onClick={() => set("sort", k)}
              className={`block w-full text-right px-2 py-1 rounded ${
                (current.sort ?? "newest") === k
                  ? "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)]"
                  : "hover:bg-[var(--color-bg-alt)]"
              }`}
            >
              {l}
            </button>
          ))}
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={current.in_stock === "1"}
              onChange={(e) => set("in_stock", e.target.checked ? "1" : null)}
            />
            فقط کالاهای موجود
          </label>
        </CardBody>
      </Card>

      <button
        onClick={() => router.push("/marketplace")}
        className="w-full text-xs underline text-[var(--color-text-muted)]"
      >
        پاک کردن همه فیلترها
      </button>
    </div>
  );
}
