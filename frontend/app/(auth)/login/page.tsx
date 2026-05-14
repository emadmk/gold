"use client";

import { useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

const PHONE_RE = /^09\d{9}$/;

type OtpRequestResponse = {
  detail: string;
  debug_code?: string;
};

export default function LoginPage() {
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [debugCode, setDebugCode] = useState<string | null>(null);

  async function call(path: string, body: object) {
    const r = await fetch(`/api/v1${path}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const json = await r.json().catch(() => ({}));
    if (!r.ok) {
      throw new Error(json.detail ?? `HTTP ${r.status}`);
    }
    return json;
  }

  async function requestOtp() {
    setError(null);
    setInfo(null);
    setDebugCode(null);

    const normalised = phone.replace(/[٠-٩۰-۹]/g, (d) =>
      String("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹".indexOf(d) % 10),
    );
    if (!PHONE_RE.test(normalised)) {
      setError("شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد.");
      return;
    }
    setBusy(true);
    try {
      const r = (await call("/auth/otp/request", { phone: normalised })) as OtpRequestResponse;
      setStep("otp");
      setInfo("کد یک‌بار‌مصرف به موبایل شما ارسال شد.");
      if (r.debug_code) setDebugCode(r.debug_code);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function verifyOtp() {
    setError(null);
    setBusy(true);
    try {
      await call("/auth/otp/verify", { phone, code });
      window.location.href = "/dashboard";
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-16 max-w-md">
        <div className="rounded-2xl border border-[var(--color-border)] bg-white p-6 shadow-[var(--shadow-card)]">
          <h1 className="text-xl font-bold mb-1">
            {step === "phone" ? "ورود / ثبت‌نام" : "تأیید کد یک‌بارمصرف"}
          </h1>
          <p className="text-xs text-[var(--color-text-muted)] mb-5">
            {step === "phone"
              ? "با وارد کردن شماره موبایل، کد یک‌بارمصرف برایتان ارسال می‌شود."
              : "کد ۶ رقمی پیامک شده را وارد کنید."}
          </p>

          {step === "phone" ? (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                requestOtp();
              }}
              className="space-y-3"
            >
              <label className="block">
                <span className="block mb-1 text-sm">شماره موبایل</span>
                <input
                  inputMode="numeric"
                  dir="ltr"
                  autoComplete="tel"
                  placeholder="09123456789"
                  className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  maxLength={11}
                />
              </label>
              <button
                type="submit"
                disabled={busy}
                className="w-full rounded-lg bg-[var(--color-primary)] text-white py-2.5 font-medium disabled:opacity-50 hover:bg-[var(--color-primary-hover)] transition"
              >
                {busy ? "در حال ارسال…" : "ارسال کد"}
              </button>
            </form>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                verifyOtp();
              }}
              className="space-y-3"
            >
              <label className="block">
                <span className="block mb-1 text-sm">کد ۶ رقمی</span>
                <input
                  inputMode="numeric"
                  dir="ltr"
                  autoComplete="one-time-code"
                  maxLength={6}
                  className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2.5 tracking-[0.5em] text-center text-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  autoFocus
                />
              </label>
              <button
                type="submit"
                disabled={busy || code.length !== 6}
                className="w-full rounded-lg bg-[var(--color-primary)] text-white py-2.5 font-medium disabled:opacity-50 hover:bg-[var(--color-primary-hover)] transition"
              >
                {busy ? "در حال بررسی…" : "تأیید و ورود"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setStep("phone");
                  setCode("");
                  setError(null);
                  setInfo(null);
                  setDebugCode(null);
                }}
                className="w-full rounded-lg border border-[var(--color-border)] py-2.5 text-sm hover:bg-[var(--color-bg)]"
              >
                تغییر شماره
              </button>
            </form>
          )}

          {info && (
            <p className="mt-3 text-sm text-[var(--color-success)] bg-[var(--color-success-light)] rounded-md px-3 py-2">
              {info}
            </p>
          )}
          {debugCode && (
            <p className="mt-2 text-xs bg-[var(--color-warning-light)] text-amber-800 rounded-md px-3 py-2">
              <b>حالت توسعه:</b> کد آزمایشی شما{" "}
              <span dir="ltr" className="font-mono text-sm">
                {debugCode}
              </span>{" "}
              است.
            </p>
          )}
          {error && (
            <p className="mt-3 text-sm text-[var(--color-danger)] bg-[var(--color-danger-light)] rounded-md px-3 py-2">
              {error}
            </p>
          )}
        </div>

        <p className="mt-6 text-xs text-[var(--color-text-muted)] text-center">
          با ورود، با{" "}
          <a href="/terms" className="text-[var(--color-primary)]">
            قوانین و مقررات
          </a>{" "}
          و{" "}
          <a href="/privacy" className="text-[var(--color-primary)]">
            حریم خصوصی
          </a>{" "}
          KeyhanGold موافقت می‌کنید.
        </p>
      </main>
      <Footer />
    </>
  );
}
