import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

const QAs = [
  ["مدل میلی‌گرم چیست؟",
    "در این مدل می‌توانید به‌جای خرید یک گرم کامل، مقدار دلخواه (حتی ۱ میلی‌گرم) طلا بخرید."],
  ["تحویل فیزیکی چطور انجام می‌شود؟",
    "حداقل ۵ گرم با کارمزد ضرب و پلمپ ۳٪، شمش‌های ۱، ۲، ۵ و ۱۰ گرمی به آدرس شما ارسال می‌شود."],
  ["آیا سود روزانه شرعی است؟",
    "این مبلغ به‌عنوان «پاداش وفاداری» در نظر گرفته می‌شود، نه ربا/بهره."],
  ["حداقل برداشت چقدر است؟",
    "حداقل ۱۰ هزار تومان (۱۰۰,۰۰۰ ریال). به شبا تأییدشده در پروفایل واریز می‌شود."],
];

export default function FAQPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold mb-4">سؤالات متداول</h1>
        {QAs.map(([q, a]) => (
          <div key={q} className="rounded-lg bg-[var(--color-bg-alt)] p-4">
            <p className="font-bold mb-2">{q}</p>
            <p className="text-sm">{a}</p>
          </div>
        ))}
      </main>
      <Footer />
    </>
  );
}
