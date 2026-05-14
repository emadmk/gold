import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function PricesPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold mb-6">قیمت‌های لحظه‌ای</h1>
        <p className="text-[var(--color-text-muted)]">
          قیمت‌ها از منبع <code>tgju.org</code> هر ۳۰ ثانیه به‌روزرسانی می‌شوند.
          نوار بالای صفحه قیمت زنده را نشان می‌دهد.
        </p>
      </main>
      <Footer />
    </>
  );
}
