import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";

type Vendor = {
  shop_name: string;
  shop_slug: string;
  state: string;
  rating: number;
  total_sales: number;
};

export default async function VendorDashboardPage() {
  let v: Vendor | null = null;
  try {
    v = await api<Vendor>("/vendor/me", { cache: "no-store" });
  } catch {
    v = null;
  }
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">پنل فروشنده</h1>
        {!v ? (
          <p>
            هنوز فروشنده نشده‌اید.{" "}
            <Link href="/vendor/apply" className="text-[var(--color-primary)]">
              درخواست فروشندگی
            </Link>
          </p>
        ) : (
          <>
            <Card>
              <CardBody>
                <p className="font-bold">{v.shop_name}</p>
                <p className="text-sm text-[var(--color-text-muted)]">
                  وضعیت: {v.state} · امتیاز: {v.rating} · فروش کل: {v.total_sales}
                </p>
              </CardBody>
            </Card>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <Link href="/vendor/products">
                <Card className="hover:shadow-[var(--shadow-card-hover)] transition">
                  <CardBody className="text-center">محصولات</CardBody>
                </Card>
              </Link>
              <Link href="/vendor/orders">
                <Card className="hover:shadow-[var(--shadow-card-hover)] transition">
                  <CardBody className="text-center">سفارش‌ها</CardBody>
                </Card>
              </Link>
              <Link href="/vendor/settlements">
                <Card className="hover:shadow-[var(--shadow-card-hover)] transition">
                  <CardBody className="text-center">تسویه‌ها</CardBody>
                </Card>
              </Link>
            </div>
          </>
        )}
      </main>
      <Footer />
    </>
  );
}
