"use client";
import { useEffect, useState } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { api, type User } from "@/lib/api";

export default function ProfilePage() {
  const [u, setU] = useState<User | null>(null);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [otpauth, setOtpauth] = useState<string | null>(null);
  const [code, setCode] = useState("");

  useEffect(() => {
    api<User>("/me").then((d) => {
      setU(d);
      setFirstName(d.first_name);
      setLastName(d.last_name);
    }).catch((e) => setErr(e.message));
  }, []);

  async function save() {
    setErr(null); setOk(null);
    try {
      const next = await api<User>("/me", {
        method: "PATCH",
        body: JSON.stringify({ first_name: firstName, last_name: lastName, email }),
      });
      setU(next);
      setOk("اطلاعات ذخیره شد.");
    } catch (e) { setErr((e as Error).message); }
  }

  async function enroll2fa() {
    const res = await api<{ otpauth: string }>("/me/2fa/enroll", { method: "POST" });
    setOtpauth(res.otpauth);
  }
  async function confirm2fa() {
    try {
      await api("/me/2fa/confirm", { method: "POST", body: JSON.stringify({ code }) });
      setOk("تأیید دوعاملی فعال شد.");
      setOtpauth(null);
      setU(u ? { ...u, two_factor_enabled: true } : u);
    } catch (e) { setErr((e as Error).message); }
  }

  if (!u) return <p>در حال بارگذاری…</p>;
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-2xl space-y-4">
        <h1 className="text-2xl font-bold flex items-center gap-3">
          پروفایل
          {u.is_verified ? <Badge tone="success">احراز شده</Badge> : <Badge tone="warning">احراز نشده</Badge>}
          <Badge tone="gold">{u.tier}</Badge>
        </h1>
        {err && <Alert kind="danger">{err}</Alert>}
        {ok && <Alert kind="success">{ok}</Alert>}

        <Card>
          <CardHeader><h2 className="font-bold">اطلاعات شخصی</h2></CardHeader>
          <CardBody className="space-y-3">
            <Input label="نام" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
            <Input label="نام خانوادگی" value={lastName} onChange={(e) => setLastName(e.target.value)} />
            <Input label="ایمیل" type="email" value={email} onChange={(e) => setEmail(e.target.value)} dir="ltr" />
            <Button onClick={save}>ذخیره تغییرات</Button>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h2 className="font-bold">تأیید دوعاملی (TOTP)</h2></CardHeader>
          <CardBody className="space-y-3">
            {u.two_factor_enabled ? (
              <Alert kind="success">تأیید دوعاملی فعال است.</Alert>
            ) : !otpauth ? (
              <Button onClick={enroll2fa}>فعال‌سازی</Button>
            ) : (
              <>
                <p className="text-sm">
                  این لینک را در اپلیکیشن Google Authenticator اسکن یا وارد کنید سپس کد ۶ رقمی تولیدشده را وارد کنید:
                </p>
                <code className="block bg-[var(--color-bg-alt)] p-2 text-xs break-all" dir="ltr">
                  {otpauth}
                </code>
                <Input
                  label="کد ۶ رقمی"
                  maxLength={6}
                  dir="ltr"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="text-center tracking-widest"
                />
                <Button onClick={confirm2fa}>تأیید</Button>
              </>
            )}
          </CardBody>
        </Card>
      </main>
      <Footer />
    </>
  );
}
