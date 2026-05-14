"use client";

import { useEffect, useState } from "react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";

type Formula = { key: string; value: string; description: string; updated_at?: string };

const DOC: Record<string, string> = {
  buy_spread: "اسپرد قیمت خرید طلا (مقدار بالاتر از مظنه)",
  sell_spread: "اسپرد قیمت فروش طلا (مقدار پایین‌تر از مظنه)",
  commission_buy: "کارمزد خرید طلا",
  commission_sell: "کارمزد فروش طلا",
  silver_buy_spread: "اسپرد قیمت خرید نقره",
  silver_sell_spread: "اسپرد قیمت فروش نقره",
  silver_commission: "کارمزد نقره",
  min_commission_fixed_mg: "حداقل کارمزد ثابت (میلی‌گرم)",
  withdraw_fee_rial: "کارمزد ثابت برداشت ریالی",
  delivery_processing_fee_pct: "درصد کارمزد ضرب/پلمپ تحویل فیزیکی",
  min_physical_delivery_mg: "حداقل وزن تحویل فیزیکی (میلی‌گرم)",
  delivery_lot_step_mg: "ضریب گام تحویل (میلی‌گرم)",
  daily_yield_apr: "نرخ پاداش وفاداری سالانه",
  aml_threshold_rial: "آستانه AML (ریال)",
  vat_pct: "نرخ مالیات ارزش افزوده",
};

export default function AdminFormulasPage() {
  const [items, setItems] = useState<Formula[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      setItems(await api<Formula[]>("/admin/formulas"));
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function save() {
    setErr(null);
    setOk(null);
    setBusy(true);
    try {
      await api("/admin/formulas", { method: "PUT", body: JSON.stringify(items) });
      setOk("فرمول‌ها به‌روزرسانی شد.");
      load();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">فرمول‌های قیمت‌گذاری</h1>
      <p className="text-xs text-[var(--color-text-muted)]">
        هر تغییری یک رویداد <code dir="ltr">pricing.formula.updated</code> در
        Kibana ثبت می‌کند. مقدار درصدی به‌صورت اعشار (مثل 0.005 برای ۰.۵٪)
        و مقدار ریالی به‌صورت عدد صحیح بدون کاما نوشته می‌شود.
      </p>
      {err && <Alert kind="danger">{err}</Alert>}
      {ok && <Alert kind="success">{ok}</Alert>}

      <Card>
        <CardBody>
          <div className="space-y-2">
            {items.map((f, i) => (
              <div key={f.key} className="grid grid-cols-[1fr_140px] md:grid-cols-[160px_1fr_160px] gap-2 items-center text-sm">
                <code className="text-xs font-mono" dir="ltr">{f.key}</code>
                <span className="text-xs text-[var(--color-text-muted)] hidden md:block">
                  {DOC[f.key] ?? f.description}
                </span>
                <input
                  dir="ltr"
                  value={f.value}
                  onChange={(e) => {
                    const next = [...items];
                    next[i] = { ...f, value: e.target.value };
                    setItems(next);
                  }}
                  className="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-sm text-center"
                />
              </div>
            ))}
          </div>
          <Button onClick={save} fullWidth loading={busy} className="mt-4">
            ذخیره همه
          </Button>
        </CardBody>
      </Card>
    </div>
  );
}
