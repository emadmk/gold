import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KeyhanGold | خرید و فروش آنلاین طلا و نقره",
  description:
    "پلتفرم تخصصی خرید و فروش طلای ۱۸ عیار، نقره ۹۹۹، سکه و طلای ساخته‌شده — مدل میلی‌گرم.",
  metadataBase: new URL("https://keyhan.gold"),
  openGraph: {
    title: "KeyhanGold",
    description: "خرید و فروش لحظه‌ای طلا و نقره با کیف پول دیجیتال.",
    locale: "fa_IR",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fa" dir="rtl">
      <body className="min-h-dvh antialiased">{children}</body>
    </html>
  );
}
