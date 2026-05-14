import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function GoldShippingPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl leading-7 text-sm">
        <h1 className="text-2xl font-bold mb-4">شرایط ارسال طلا</h1>
        <ul className="list-disc pr-6 space-y-2">
          <li>ارسال توسط مرچنت (فروشنده) و با بسته‌بندی امن و بیمه‌شده انجام می‌شود.</li>
          <li>روش‌های ارسال: پست پیشتاز، تیپاکس، اسنپ‌باکس.</li>
          <li>هزینه ارسال در صفحه محصول و در سبد خرید نمایش داده می‌شود.</li>
          <li>کد رهگیری پس از ارسال در پنل کاربر و از طریق پیامک ارسال می‌شود.</li>
          <li>زمان آماده‌سازی + ارسال معمولاً ۱ تا ۳ روز کاری است.</li>
          <li>تحویل کالا فقط به گیرنده اعلام‌شده و با احراز هویت انجام می‌شود.</li>
        </ul>
      </main>
      <Footer />
    </>
  );
}
