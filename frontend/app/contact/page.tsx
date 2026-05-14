import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function ContactPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        <h1 className="text-2xl font-bold mb-4">تماس با ما</h1>
        <ul className="space-y-2 text-sm">
          <li>پشتیبانی: <span dir="ltr">support@keyhan.gold</span></li>
          <li>تلفن: <span dir="ltr">021-XXXXXXXX</span></li>
          <li>نشانی: تهران، خیابان نمونه، پلاک ۰</li>
        </ul>
      </main>
      <Footer />
    </>
  );
}
