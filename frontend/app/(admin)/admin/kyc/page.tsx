"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { api } from "@/lib/api";

type KYC = {
  id: string;
  state: string;
  rejection_reason: string;
  national_card_front: string | null;
  national_card_back: string | null;
  selfie_with_card: string | null;
  birth_certificate: string | null;
  video_attestation: string | null;
  card_pan_masked: string;
  created_at: string;
};

const TONE: Record<string, "success" | "warning" | "danger" | "primary" | "neutral"> = {
  empty: "neutral",
  submitted: "warning",
  under_review: "primary",
  approved: "success",
  rejected: "danger",
  requires_more: "warning",
};

export default function AdminKYCPage() {
  const [list, setList] = useState<KYC[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function load() {
    try {
      const r = await api<{ results: KYC[] }>("/admin/kyc-queue");
      setList(r.results ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function approve(k: KYC) {
    setBusy(k.id);
    try {
      await api(`/admin/kyc/${k.id}/approve`, { method: "POST" });
      load();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(null);
    }
  }
  async function reject(k: KYC) {
    const reason = prompt("دلیل رد:");
    if (!reason) return;
    setBusy(k.id);
    try {
      await api(`/admin/kyc/${k.id}/reject`, {
        method: "POST",
        body: JSON.stringify({ reason }),
      });
      load();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">صف KYC</h1>
      <p className="text-xs text-[var(--color-text-muted)]">
        درخواست‌های در انتظار تأیید احراز هویت.
      </p>
      {err && <Card><CardBody className="text-sm text-[var(--color-danger)]">{err}</CardBody></Card>}

      {list.length === 0 ? (
        <Card>
          <CardBody className="text-center text-sm py-8 text-[var(--color-text-muted)]">
            صف خالی است — همه درخواست‌های اخیر بررسی شده‌اند.
          </CardBody>
        </Card>
      ) : (
        list.map((k) => (
          <Card key={k.id}>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-bold text-sm">درخواست {k.id.slice(0, 8)}…</p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    {new Date(k.created_at).toLocaleString("fa-IR")}
                  </p>
                </div>
                <Badge tone={TONE[k.state] ?? "neutral"}>{k.state}</Badge>
              </div>
            </CardHeader>
            <CardBody className="space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                {[
                  ["کارت ملی - رو", k.national_card_front],
                  ["کارت ملی - پشت", k.national_card_back],
                  ["سلفی با کارت", k.selfie_with_card],
                  ["شناسنامه", k.birth_certificate],
                  ["ویدیو", k.video_attestation],
                ].map(([label, url]) => (
                  <div key={label as string}>
                    <p className="font-bold mb-1">{label}</p>
                    {url ? (
                      <a
                        href={url}
                        target="_blank"
                        rel="noopener"
                        className="block aspect-square rounded-md bg-[var(--color-bg)] border border-[var(--color-border)] overflow-hidden hover:border-[var(--color-primary)]"
                      >
                        <img
                          src={url}
                          alt={label as string}
                          className="w-full h-full object-cover"
                        />
                      </a>
                    ) : (
                      <div className="aspect-square rounded-md bg-[var(--color-bg)] border border-dashed border-[var(--color-border)] flex items-center justify-center text-[var(--color-text-muted)]">
                        —
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {k.rejection_reason && (
                <p className="text-xs bg-[var(--color-warning-light)] text-amber-800 rounded-md px-3 py-2">
                  دلیل رد قبلی: {k.rejection_reason}
                </p>
              )}
              <div className="flex gap-2">
                <Button onClick={() => approve(k)} loading={busy === k.id}>
                  تأیید
                </Button>
                <Button variant="danger" onClick={() => reject(k)} loading={busy === k.id}>
                  رد
                </Button>
              </div>
            </CardBody>
          </Card>
        ))
      )}
    </div>
  );
}
