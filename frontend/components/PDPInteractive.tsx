"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";

type Props = {
  product: {
    id: string;
    title: string;
    gallery: string[];
    computed_price_rial: number;
    stock: number;
  };
};

export function PDPInteractive({ product }: Props) {
  const router = useRouter();
  const [active, setActive] = useState(0);
  const [zoom, setZoom] = useState(false);
  const [qty, setQty] = useState(1);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function addToCart() {
    setErr(null);
    setOk(null);
    setBusy(true);
    try {
      await api("/cart/items", {
        method: "POST",
        body: JSON.stringify({ product_id: product.id, quantity: qty }),
      });
      setOk("به سبد خرید اضافه شد.");
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const main = product.gallery[active];

  return (
    <div className="space-y-3">
      <div
        className={`aspect-square rounded-2xl bg-[var(--color-bg-alt)] overflow-hidden cursor-zoom-in ${
          zoom ? "ring-4 ring-[var(--color-primary)]" : ""
        }`}
        onClick={() => setZoom((z) => !z)}
      >
        {main ? (
          <img
            src={main}
            alt={product.title}
            className={`w-full h-full object-cover transition ${zoom ? "scale-150" : ""}`}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-9xl">🥇</div>
        )}
      </div>

      {product.gallery.length > 1 && (
        <div className="flex gap-2 overflow-x-auto">
          {product.gallery.map((url, i) => (
            <button
              key={url}
              onClick={() => setActive(i)}
              className={`shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 ${
                i === active ? "border-[var(--color-primary)]" : "border-transparent"
              }`}
            >
              <img src={url} alt="" className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-2 items-center mt-4">
        <label className="text-sm">تعداد:</label>
        <input
          type="number"
          min={1}
          max={product.stock}
          value={qty}
          onChange={(e) => setQty(Math.max(1, Math.min(product.stock, Number(e.target.value))))}
          className="w-20 rounded-lg border border-[var(--color-border)] px-2 py-1 text-sm text-center"
        />
        <Button
          variant="gold"
          fullWidth
          loading={busy}
          disabled={product.stock < 1}
          onClick={addToCart}
        >
          {product.stock < 1 ? "ناموجود" : "افزودن به سبد خرید"}
        </Button>
      </div>
      <Button variant="ghost" fullWidth onClick={() => router.push("/cart")}>
        مشاهده سبد خرید
      </Button>

      {err && <Alert kind="danger">{err}</Alert>}
      {ok && <Alert kind="success">{ok}</Alert>}
    </div>
  );
}
