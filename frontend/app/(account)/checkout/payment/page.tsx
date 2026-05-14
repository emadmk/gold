"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { CheckoutSteps } from "@/components/CheckoutSteps";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";

const METHODS = [
  ["online", "پرداخت آنلاین بانکی (زرین‌پال / آیدی‌پی / پی‌پینگ)"],
  ["snappay", "اسنپ پی (پرداخت قسطی)"],
  ["gsmpay", "جی‌اس‌ام پی"],
] as const;

export default function CheckoutPaymentPage() {
  const router = useRouter();
  const [method, setMethod] = useState<string>("online");

  async function next() {
    await api("/cart/payment-method", {
      method: "POST",
      body: JSON.stringify({ method }),
    });
    router.push("/checkout/confirm");
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-2xl space-y-4">
        <h1 className="text-2xl font-bold">روش پرداخت</h1>
        <CheckoutSteps step={3} />
        <Card>
          <CardBody className="space-y-2">
            {METHODS.map(([code, label]) => (
              <label
                key={code}
                className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer ${
                  method === code
                    ? "bg-[var(--color-primary-light)] border border-[var(--color-primary)]"
                    : "border border-[var(--color-border)]"
                }`}
              >
                <input
                  type="radio"
                  name="pm"
                  value={code}
                  checked={method === code}
                  onChange={(e) => setMethod(e.target.value)}
                />
                <span>{label}</span>
              </label>
            ))}
          </CardBody>
        </Card>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => router.back()}>
            مرحله قبل
          </Button>
          <Button onClick={next} fullWidth>
            مرحله بعد
          </Button>
        </div>
      </main>
      <Footer />
    </>
  );
}
