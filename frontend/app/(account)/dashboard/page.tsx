import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { formatMg, formatRial } from "@/lib/format";

type Wallet = {
  rial: { balance_rial: number; locked_rial: number; available_rial: number };
  gold: {
    address: string;
    balance_mg: number;
    available_gold_mg: number;
    silver_balance_mg: number;
    available_silver_mg: number;
  };
};

export default async function DashboardPage() {
  let wallet: Wallet | null = null;
  try {
    wallet = await api<Wallet>("/wallet", { cache: "no-store" });
  } catch {
    wallet = null;
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 grid md:grid-cols-3 gap-4">
        <Card title="کیف پول ریالی" subtitle={formatRial(wallet?.rial.available_rial ?? 0)} accent="primary" />
        <Card title="کیف پول طلا" subtitle={formatMg(wallet?.gold.available_gold_mg ?? 0)} accent="gold" />
        <Card title="کیف پول نقره" subtitle={formatMg(wallet?.gold.available_silver_mg ?? 0)} accent="muted" />
      </main>
      <Footer />
    </>
  );
}

function Card({
  title,
  subtitle,
  accent,
}: {
  title: string;
  subtitle: string;
  accent: "primary" | "gold" | "muted";
}) {
  const colors: Record<typeof accent, string> = {
    primary: "var(--color-primary)",
    gold: "var(--color-gold)",
    muted: "var(--color-text-muted)",
  };
  return (
    <div className="rounded-2xl bg-[var(--color-card)] border border-[var(--color-border)] p-5 shadow-[var(--shadow-card)]">
      <p className="text-sm text-[var(--color-text-muted)]">{title}</p>
      <p className="mt-2 text-2xl font-bold" style={{ color: colors[accent] }}>{subtitle}</p>
    </div>
  );
}
