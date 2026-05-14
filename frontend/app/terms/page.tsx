import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function TermsPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        <h1 className="text-2xl font-bold mb-4">قوانین و مقررات</h1>
        <div className="prose prose-sm space-y-3 text-sm leading-7">
          <p>
            استفاده از پلتفرم KeyhanGold (در ادامه «سامانه») مشروط به پذیرش این
            توافق‌نامه است. مالکیت سامانه متعلق به شرکت «کیهان کیان» می‌باشد.
          </p>
          <h2 className="font-bold">مدل کسب‌وکار</h2>
          <p>
            سامانه خدمت خرید/فروش طلا و نقره به‌صورت دیجیتال (مدل میلی‌گرم) و یک
            مارکت‌پلیس برای فروشندگان دارای پروانه‌ی اتحادیه‌ی صنف طلا و جواهر ارائه می‌دهد.
          </p>
          <h2 className="font-bold">پاداش وفاداری</h2>
          <p>
            مبلغی که در پایان هر روز به موجودی کیف پول ریالی افزوده می‌شود، «پاداش
            وفاداری» محسوب می‌شود و ربا/بهره نیست. این مقدار صرفاً برای ترغیب
            کاربران به نگهداری ارزش در سامانه پرداخت می‌شود و قابل توقف یا تغییر است.
          </p>
          <h2 className="font-bold">ریسک نوسان</h2>
          <p>
            قیمت طلا و نقره دائماً در حال نوسان است. سامانه هیچ تضمینی برای
            سودآوری ارائه نمی‌کند. تصمیم خرید/فروش بر عهده کاربر است.
          </p>
        </div>
      </main>
      <Footer />
    </>
  );
}
