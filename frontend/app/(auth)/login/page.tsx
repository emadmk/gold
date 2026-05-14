"use client";
import { useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

export default function LoginPage() {
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function requestOtp() {
    setBusy(true);
    setError(null);
    try {
      await api("/auth/otp/request", { method: "POST", body: JSON.stringify({ phone }) });
      setStep("otp");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function verifyOtp() {
    setBusy(true);
    setError(null);
    try {
      await api("/auth/otp/verify", {
        method: "POST",
        body: JSON.stringify({ phone, code }),
      });
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
        <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-card)] p-6">
          <h1 className="text-xl font-bold mb-4">
            {step === "phone" ? "ورود / ثبت‌نام" : "تأیید کد یکبارمصرف"}
          </h1>

          {step === "phone" ? (
            <div className="space-y-3">
              <label className="block text-sm">شماره موبایل</label>
              <input
                inputMode="numeric"
                dir="ltr"
                placeholder="09123456789"
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              <button
                disabled={busy || phone.length !== 11}
                onClick={requestOtp}
                className="w-full rounded-lg bg-[var(--color-primary)] text-white py-2 disabled:opacity-50"
              >
                ارسال کد
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <label className="block text-sm">کد ۶ رقمی پیامک شده</label>
              <input
                inputMode="numeric"
                dir="ltr"
                maxLength={6}
                className="w-full rounded-lg border border-[var(--color-border)] px-3 py-2 tracking-widest text-center"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <button
                disabled={busy || code.length !== 6}
                onClick={verifyOtp}
                className="w-full rounded-lg bg-[var(--color-primary)] text-white py-2 disabled:opacity-50"
              >
                تأیید و ورود
              </button>
              <button
                onClick={() => setStep("phone")}
                className="w-full rounded-lg border border-[var(--color-border)] py-2 text-sm"
              >
                تغییر شماره
              </button>
            </div>
          )}

          {error ? <p className="mt-3 text-sm text-[var(--color-danger)]">{error}</p> : null}
        </div>
      </main>
      <Footer />
    </>
  );
}
