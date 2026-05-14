import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function GoldReturnPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl leading-7 text-sm">
        <h1 className="text-2xl font-bold mb-4">شرایط مرجوعی طلا</h1>
        <p>
          خریدار محترم، با توجه به ماهیت کالای طلا، شرایط مرجوعی به شرح زیر است:
        </p>
        <ul className="list-disc pr-6 mt-3 space-y-2">
          <li>طلای ساخته‌شده تا ۲۴ ساعت پس از تحویل، در صورت سالم بودن کالا و عدم استفاده، قابل مرجوع است.</li>
          <li>اجرت ساخت پس از تحویل قابل بازگشت نیست.</li>
          <li>قیمت طلا بر اساس نرخ روز در زمان بازگرداندن کالا محاسبه می‌شود.</li>
          <li>سکه و شمش فقط در صورت ایراد کارخانه‌ای قابل مرجوع است.</li>
          <li>برای ثبت درخواست مرجوعی به پنل سفارش‌ها مراجعه کنید یا با پشتیبانی تماس بگیرید.</li>
        </ul>
      </main>
      <Footer />
    </>
  );
}
