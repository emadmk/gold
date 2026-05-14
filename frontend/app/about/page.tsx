import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function AboutPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl prose prose-sm">
        <h1 className="text-2xl font-bold">درباره KeyhanGold</h1>
        <p>
          KeyhanGold یک پلتفرم تخصصی خرید و فروش آنلاین طلای ۱۸ عیار، نقره ۹۹۹،
          سکه و طلای ساخته‌شده است که زیر نظر اتحادیه‌ی صنف طلا و جواهر فعالیت می‌کند.
        </p>
        <p>
          ما با مدل میلی‌گرم، خرید طلا را از کسری از یک گرم ممکن کرده‌ایم تا کاربران
          بتوانند بدون نیاز به مبالغ سنگین، در طلا سرمایه‌گذاری کنند.
        </p>
      </main>
      <Footer />
    </>
  );
}
