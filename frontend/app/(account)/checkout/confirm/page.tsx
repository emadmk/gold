"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { CheckoutSteps } from "@/components/CheckoutSteps";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { formatMg, formatRial, toPersianNumber } from "@/lib/format";

type Cart = {
  items: Array<{
    id: string;
    product: {
      title: string;
      weight_mg: number;
      karat: number;
      vendor: { shop_name: string };
    };
    quantity: number;
    locked_unit_price_rial: number;
  }>;
  shipping_address: {
    title: string;
    recipient_name: string;
    recipient_phone: string;
    province: string;
    city: string;
    address: string;
  } | null;
  shipping_method: string;
  payment_method: string;
  totals: {
    subtotal_rial: number;
    shipping_rial: number;
    discount_rial: number;
    final_rial: number;
    discount_code: string | null;
  };
};

const SHIPPING_LABEL: Record<string, string> = {
  "post-pishtaz": "پست پیشتاز",
  tipax: "تیپاکس",
  "snapp-box": "اسنپ‌باکس",
};
const PAYMENT_LABEL: Record<string, string> = {
  online: "پرداخت آنلاین",
  snappay: "اسنپ پی",
  gsmpay: "جی‌اس‌ام پی",
};

export default function CheckoutConfirmPage() {
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<Cart>("/cart").then(setCart).catch((e) => setErr(e.message));
  }, []);

  async function place() {
    setBusy(true);
    setErr(null);
    try {
      const order = await api<{ id: string; state: string }>("/cart/checkout", {
        method: "POST",
      });
      // If payment is online + state still awaits payment, kick off topup-style payment
      if (cart?.payment_method === "online") {
        // The order was created; redirect to the success page —
        // a real online-pay flow could start a PaymentAttempt here.
        router.push(`/checkout/success?order=${order.id}`);
      } else {
        router.push(`/checkout/success?order=${order.id}`);
      }
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
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

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">تأیید نهایی سفارش</h1>
        <CheckoutSteps step={4} />
        {err && <Alert kind="danger">{err}</Alert>}

        <Card>
          <CardHeader>
            <h2 className="font-bold">آدرس ارسال</h2>
          </CardHeader>
          <CardBody className="text-sm">
            {cart.shipping_address ? (
              <>
                <p>
                  <b>{cart.shipping_address.title}</b> ·{" "}
                  {cart.shipping_address.recipient_name} ·{" "}
                  {cart.shipping_address.recipient_phone}
                </p>
                <p>
                  {cart.shipping_address.province}، {cart.shipping_address.city}،{" "}
                  {cart.shipping_address.address}
                </p>
              </>
            ) : (
              <Alert kind="danger">آدرس انتخاب نشده است.</Alert>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="font-bold">روش ارسال و پرداخت</h2>
          </CardHeader>
          <CardBody className="text-sm space-y-1">
            <p>
              ارسال: {SHIPPING_LABEL[cart.shipping_method] ?? cart.shipping_method || "—"}
            </p>
            <p>
              پرداخت: {PAYMENT_LABEL[cart.payment_method] ?? cart.payment_method || "—"}
            </p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="font-bold">اقلام</h2>
          </CardHeader>
          <CardBody className="space-y-2 text-sm">
            {cart.items.map((i) => (
              <div key={i.id} className="flex justify-between">
                <span>
                  {i.product.title} · {formatMg(i.product.weight_mg)} · ع{" "}
                  {toPersianNumber(i.product.karat)} ×{" "}
                  {toPersianNumber(i.quantity)}
                </span>
                <span>{formatRial(i.locked_unit_price_rial * i.quantity)}</span>
              </div>
            ))}
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
              <span>مبلغ نهایی</span>
              <span>{formatRial(cart.totals.final_rial)}</span>
            </div>
          </CardBody>
        </Card>

        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => router.back()}>
            مرحله قبل
          </Button>
          <Button
            variant="gold"
            fullWidth
            loading={busy}
            disabled={!cart.shipping_address}
            onClick={place}
          >
            ثبت سفارش و انتقال به درگاه
          </Button>
        </div>
        <p className="text-xs text-[var(--color-text-muted)] text-center">
          بعد از ثبت سفارش، ۲۰ دقیقه فرصت پرداخت در درگاه دارید.
        </p>
      </main>
      <Footer />
    </>
  );
}
