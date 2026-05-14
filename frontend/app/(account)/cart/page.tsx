"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { useOrderCountdown } from "@/hooks/useOrderCountdown";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

type Item = {
  id: string;
  product: {
    id: string;
    title: string;
    slug: string;
    weight_mg: number;
    karat: number;
    image_urls: string[];
    vendor: { shop_name: string };
  };
  quantity: number;
  locked_unit_price_rial: number;
  locked_at: string;
};

type LockState = {
  item_id: string;
  product_id: string;
  title: string;
  locked: number;
  current: number;
  delta: number;
  changed: boolean;
  expired: boolean;
  locked_at: string;
};

type Totals = {
  subtotal_rial: number;
  shipping_rial: number;
  discount_rial: number;
  final_rial: number;
  items_count: number;
  discount_code: string | null;
};

type Cart = {
  id: string;
  items: Item[];
  shipping_address: unknown;
  shipping_method: string;
  payment_method: string;
  lock_state: LockState[];
  totals: Totals;
};

function CartItemRow({
  item,
  state,
  onChange,
  onRemove,
}: {
  item: Item;
  state?: LockState;
  onChange: (qty: number) => void;
  onRemove: () => void;
}) {
  const cd = useOrderCountdown(
    new Date(new Date(item.locked_at).getTime() + 6 * 60 * 1000).toISOString(),
  );
  return (
    <Card>
      <CardBody className="grid grid-cols-[80px_1fr_auto] gap-3 items-center">
        <Link href={`/marketplace/${item.product.slug}`}>
          {item.product.image_urls?.[0] ? (
            <img
              src={item.product.image_urls[0]}
              alt={item.product.title}
              className="w-20 h-20 rounded-md object-cover"
            />
          ) : (
            <div className="w-20 h-20 rounded-md bg-[var(--color-gold-light)] flex items-center justify-center text-2xl">
              🥇
            </div>
          )}
        </Link>
        <div className="text-sm space-y-1">
          <p className="font-bold">{item.product.title}</p>
          <p className="text-xs text-[var(--color-text-muted)]">
            {item.product.vendor.shop_name} · {formatMg(item.product.weight_mg)} · عیار{" "}
            {toPersianNumber(item.product.karat)}
          </p>
          <p className="text-xs">
            قیمت قفل‌شده: <b>{formatRial(item.locked_unit_price_rial)}</b>
          </p>
          {state?.changed && (
            <p className="text-xs text-[var(--color-warning)]">
              قیمت روز تغییر کرده — جدید: {formatRial(state.current)} (
              {state.delta > 0 ? "+" : ""}
              {formatRial(state.delta)})
            </p>
          )}
          {state?.expired && (
            <Badge tone="danger">قفل قیمت منقضی شده — برای ادامه به‌روزرسانی کنید</Badge>
          )}
          {!state?.expired && (
            <p className="text-xs text-[var(--color-text-muted)]">
              زمان باقی‌مانده‌ی قفل: <span dir="ltr">{cd.label}</span>
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2">
          <input
            type="number"
            min={0}
            value={item.quantity}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-16 rounded-lg border border-[var(--color-border)] px-2 py-1 text-sm text-center"
          />
          <Button variant="ghost" size="sm" onClick={onRemove}>
            حذف
          </Button>
          <p className="text-sm font-bold">
            {formatRial(item.locked_unit_price_rial * item.quantity)}
          </p>
        </div>
      </CardBody>
    </Card>
  );
}

export default function CartPage() {
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [code, setCode] = useState("");

  const [authed, setAuthed] = useState<boolean | null>(null);

  async function load() {
    setErr(null);
    try {
      const r = await fetch("/api/v1/cart", { credentials: "include" });
      if (r.status === 401 || r.status === 403) {
        setAuthed(false);
        return;
      }
      if (!r.ok) {
        setErr(`HTTP ${r.status}`);
        return;
      }
      setAuthed(true);
      setCart((await r.json()) as Cart);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function setQty(id: string, qty: number) {
    if (qty <= 0) return remove(id);
    try {
      await api(`/cart/items/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ quantity: qty }),
      });
      load();
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  async function remove(id: string) {
    await api(`/cart/items/${id}`, { method: "DELETE" });
    load();
  }
  async function relock() {
    await api("/cart/relock", { method: "POST" });
    load();
  }
  async function applyDiscount() {
    setErr(null);
    try {
      await api("/cart/discount", { method: "POST", body: JSON.stringify({ code }) });
      load();
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  if (authed === false) {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-20 max-w-md text-center space-y-3">
          <div className="text-6xl">🛒</div>
          <h1 className="text-xl font-bold">برای مشاهده‌ی سبد خرید وارد شوید</h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            سبد خرید شما نزد KeyhanGold امن نگه‌داری می‌شود و قیمت‌ها برای ۶ دقیقه قفل می‌شوند.
          </p>
          <Link
            href="/login?next=/cart"
            className="inline-block px-6 py-3 rounded-xl bg-[var(--color-primary)] text-white font-medium"
          >
            ورود / ثبت‌نام
          </Link>
        </main>
        <Footer />
      </>
    );
  }
  if (!cart) {
    return (
      <>
        <Header />
        <main className="container mx-auto px-4 py-10">
          {err ? <Alert kind="danger">{err}</Alert> : <p>در حال بارگذاری…</p>}
        </main>
        <Footer />
      </>
    );
  }

  const lockMap = Object.fromEntries(cart.lock_state.map((s) => [s.item_id, s]));
  const anyChanged = cart.lock_state.some((s) => s.changed);
  const anyExpired = cart.lock_state.some((s) => s.expired);

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-4xl space-y-4">
        <h1 className="text-2xl font-bold">سبد خرید</h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {anyChanged && (
          <Alert kind="warning">
            قیمت زنده‌ی برخی محصولات تغییر کرده است. می‌توانید با کلیک روی
            «به‌روزرسانی قیمت‌ها» سبد را با نرخ روز بازنشانی کنید.
          </Alert>
        )}
        {anyExpired && (
          <Alert kind="danger">
            قفل قیمت ۶ دقیقه‌ای منقضی شده — برای ادامه «به‌روزرسانی قیمت‌ها» را بزنید.
          </Alert>
        )}

        {cart.items.length === 0 ? (
          <Card>
            <CardBody>
              <p className="text-sm text-[var(--color-text-muted)]">
                سبد خرید شما خالی است.{" "}
                <Link href="/marketplace" className="text-[var(--color-primary)]">
                  مشاهده محصولات
                </Link>
              </p>
            </CardBody>
          </Card>
        ) : (
          <>
            <div className="space-y-2">
              {cart.items.map((i) => (
                <CartItemRow
                  key={i.id}
                  item={i}
                  state={lockMap[i.id]}
                  onChange={(qty) => setQty(i.id, qty)}
                  onRemove={() => remove(i.id)}
                />
              ))}
            </div>

            <Card>
              <CardHeader>
                <h3 className="font-bold">کد تخفیف</h3>
              </CardHeader>
              <CardBody className="flex gap-2">
                <Input
                  dir="ltr"
                  placeholder="OFF10"
                  value={code}
                  onChange={(e) => setCode(e.target.value.toUpperCase())}
                  className="flex-1"
                />
                <Button onClick={applyDiscount}>اعمال</Button>
              </CardBody>
            </Card>

            <Card>
              <CardBody className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>مجموع محصولات</span>
                  <span>{formatRial(cart.totals.subtotal_rial)}</span>
                </div>
                <div className="flex justify-between">
                  <span>هزینه ارسال</span>
                  <span>{formatRial(cart.totals.shipping_rial)}</span>
                </div>
                {cart.totals.discount_rial > 0 && (
                  <div className="flex justify-between text-[var(--color-success)]">
                    <span>تخفیف ({cart.totals.discount_code})</span>
                    <span>- {formatRial(cart.totals.discount_rial)}</span>
                  </div>
                )}
                <div className="flex justify-between font-bold text-lg pt-2 border-t border-[var(--color-border)]">
                  <span>مبلغ قابل پرداخت</span>
                  <span>{formatRial(cart.totals.final_rial)}</span>
                </div>
              </CardBody>
            </Card>

            <div className="flex gap-2">
              <Button variant="ghost" onClick={relock}>
                به‌روزرسانی قیمت‌ها
              </Button>
              <Button
                variant="gold"
                fullWidth
                disabled={anyExpired}
                onClick={() => router.push("/checkout/address")}
              >
                ادامه به انتخاب آدرس
              </Button>
            </div>
          </>
        )}
      </main>
      <Footer />
    </>
  );
}
