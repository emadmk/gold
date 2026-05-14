import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function PrivacyPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl prose prose-sm">
        <h1 className="text-2xl font-bold mb-4">حریم خصوصی</h1>
        <p>
          اطلاعات شناسایی شما (کد ملی، شبا، شماره کارت) با AES-256-GCM
          رمزنگاری شده در ذخیره‌سازی می‌شوند. کلیه ارتباطات روی TLS 1.3 هستند.
        </p>
        <p>
          ما هرگز اطلاعات شما را با اشخاص ثالث بدون رضایت صریح به‌اشتراک نمی‌گذاریم؛
          مگر در موارد قانونی الزام‌آور.
        </p>
        <p>
          شما حق دسترسی به داده‌های خود و درخواست حذف آن‌ها را دارید
          (ماده ۱۳ قانون انتشار و دسترسی آزاد به اطلاعات).
        </p>
      </main>
      <Footer />
    </>
  );
}
