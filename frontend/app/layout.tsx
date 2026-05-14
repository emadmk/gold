import type { Metadata, Viewport } from "next";
import { Vazirmatn } from "next/font/google";

import "./globals.css";

const vazir = Vazirmatn({
  subsets: ["arabic", "latin"],
  variable: "--font-vazir",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "KeyhanGold | خرید و فروش آنلاین طلا و نقره",
    template: "%s | KeyhanGold",
  },
  description:
    "پلتفرم تخصصی خرید و فروش طلای ۱۸ عیار، نقره ۹۹۹، سکه و طلای ساخته‌شده — مدل میلی‌گرم با کیف پول دیجیتال.",
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? "https://keyhan.gold",
  ),
  openGraph: {
    title: "KeyhanGold",
    description: "خرید و فروش لحظه‌ای طلا و نقره با کیف پول دیجیتال.",
    locale: "fa_IR",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#2D87F0",
  colorScheme: "light",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fa" dir="rtl" className={vazir.variable}>
      <body className="min-h-dvh antialiased">{children}</body>
    </html>
  );
}
