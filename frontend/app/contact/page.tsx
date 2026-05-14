import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

/**
 * Public contact info — read from server env at build time.
 *
 * Set NEXT_PUBLIC_CONTACT_EMAIL / _PHONE / _ADDRESS in `.env`. Falls
 * back to "—" so the production site never displays a fake placeholder.
 */
const EMAIL = process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? "";
const PHONE = process.env.NEXT_PUBLIC_CONTACT_PHONE ?? "";
const ADDRESS = process.env.NEXT_PUBLIC_CONTACT_ADDRESS ?? "";

export default function ContactPage() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        <h1 className="text-2xl font-bold mb-4">تماس با ما</h1>
        <dl className="space-y-3 text-sm">
          <Item label="پشتیبانی" value={EMAIL} dir="ltr" />
          <Item label="تلفن" value={PHONE} dir="ltr" />
          <Item label="نشانی" value={ADDRESS} />
        </dl>
      </main>
      <Footer />
    </>
  );
}

function Item({ label, value, dir }: { label: string; value: string; dir?: "ltr" | "rtl" }) {
  return (
    <div className="flex gap-3">
      <dt className="text-[var(--color-text-muted)] min-w-24">{label}:</dt>
      <dd dir={dir}>{value || "—"}</dd>
    </div>
  );
}
