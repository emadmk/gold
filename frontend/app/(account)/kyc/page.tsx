"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";

const STATE_LABELS: Record<string, string> = {
  empty: "ارسال نشده",
  submitted: "ارسال شد",
  under_review: "در حال بررسی",
  approved: "تأیید شد",
  rejected: "رد شد",
  requires_more: "نیاز به اطلاعات بیشتر",
};

const STATE_TONE: Record<string, "primary" | "success" | "warning" | "danger" | "neutral"> = {
  empty: "neutral",
  submitted: "primary",
  under_review: "primary",
  approved: "success",
  rejected: "danger",
  requires_more: "warning",
};

type KYC = {
  state: string;
  rejection_reason?: string;
};

export default function KYCPage() {
  const [data, setData] = useState<KYC | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    try {
      const res = await fetch("/api/v1/kyc", { credentials: "include" });
      const body = await res.json();
      setData(body);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function submit(form: FormData) {
    setSubmitting(true); setErr(null); setOk(null);
    try {
      const res = await fetch("/api/v1/kyc", {
        method: "POST", body: form, credentials: "include",
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `HTTP ${res.status}`);
      }
      setOk("مدارک با موفقیت ارسال شد. تا ۲۴ ساعت کاری بررسی می‌شود.");
      load();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-2xl space-y-4">
        <h1 className="text-2xl font-bold flex items-center gap-3">
          احراز هویت
          {data?.state ? (
            <Badge tone={STATE_TONE[data.state] ?? "neutral"}>
              {STATE_LABELS[data.state] ?? data.state}
            </Badge>
          ) : null}
        </h1>

        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}
        {data?.rejection_reason ? (
          <Alert kind="warning">دلیل رد: {data.rejection_reason}</Alert>
        ) : null}

        {data?.state === "approved" ? (
          <Card>
            <CardBody>
              <p className="text-[var(--color-success)] font-bold">
                احراز هویت شما تأیید شده است.
              </p>
              <p className="text-sm text-[var(--color-text-muted)] mt-1">
                می‌توانید از تمام امکانات سامانه استفاده کنید.
              </p>
            </CardBody>
          </Card>
        ) : (
          <Card>
            <CardHeader><h2 className="font-bold">ارسال مدارک</h2></CardHeader>
            <CardBody>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  submit(new FormData(e.currentTarget));
                }}
                className="space-y-3"
              >
                <FileField name="national_card_front" label="تصویر روی کارت ملی" />
                <FileField name="national_card_back" label="تصویر پشت کارت ملی" />
                <FileField name="selfie_with_card" label='سلفی با کارت ملی + دست‌نوشت تاریخ روز + متن "این تصویر برای KeyhanGold است"' />
                <FileField name="birth_certificate" label="تصویر شناسنامه (اختیاری)" required={false} />
                <FileField name="video_attestation" label="ویدیوی ۵ ثانیه‌ای متن خواندنی (اختیاری)" required={false} />
                <Button type="submit" fullWidth loading={submitting}>
                  ارسال مدارک
                </Button>
              </form>
            </CardBody>
          </Card>
        )}
      </main>
      <Footer />
    </>
  );
}

function FileField({ name, label, required = true }: { name: string; label: string; required?: boolean }) {
  return (
    <label className="block">
      <span className="block text-sm mb-1">{label}</span>
      <input type="file" name={name} required={required}
        className="block w-full text-sm" />
    </label>
  );
}
