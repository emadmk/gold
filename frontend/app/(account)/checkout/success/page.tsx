import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";

export default async function CheckoutSuccessPage({
  searchParams,
}: {
  searchParams: Promise<{ order?: string }>;
}) {
  const { order } = await searchParams;
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-16 max-w-md text-center">
        <Card>
          <CardBody className="space-y-3">
            <div className="text-7xl">🎉</div>
            <h1 className="text-2xl font-bold text-[var(--color-success)]">
              سفارش شما با موفقیت ثبت شد
            </h1>
            <p className="text-sm text-[var(--color-text-muted)]">
              می‌توانید جزئیات سفارش، فاکتور و وضعیت ارسال را در پنل کاربری خود پیگیری کنید.
            </p>
            {order && (
              <Link href={`/orders/${order}`}>
                <Button variant="gold" fullWidth>
                  مشاهده سفارش
                </Button>
              </Link>
            )}
            <Link href="/marketplace">
              <Button variant="ghost" fullWidth>
                بازگشت به مارکت‌پلیس
              </Button>
            </Link>
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
