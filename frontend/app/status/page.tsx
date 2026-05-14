"use client";

/* /status — Bare-metal diagnostic page.
 *
 * Uses NO custom hooks, NO custom UI components. Just useState +
 * useEffect + plain HTML so we can be sure ANY failure here is a
 * fundamental React-hydration or network problem.
 */
import { useEffect, useState } from "react";

type Probe = {
  url: string;
  status: number | "pending" | "error";
  body?: string;
  ms?: number;
};

const ENDPOINTS = [
  "/health/",
  "/api/v1/me",
  "/api/v1/prices",
  "/api/v1/marketplace/products",
  "/api/v1/marketplace/facets",
  "/api/v1/blog/posts",
];

async function timedFetch(url: string, ms = 5000): Promise<Probe> {
  const t0 = performance.now();
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), ms);
  try {
    const r = await fetch(url, {
      credentials: "include",
      signal: ctl.signal,
      headers: { Accept: "application/json" },
    });
    clearTimeout(timer);
    let body = "";
    try {
      body = (await r.text()).slice(0, 200);
    } catch {
      /* ignore */
    }
    return {
      url,
      status: r.status,
      body,
      ms: Math.round(performance.now() - t0),
    };
  } catch (e) {
    clearTimeout(timer);
    return {
      url,
      status: "error",
      body: (e as Error).message,
      ms: Math.round(performance.now() - t0),
    };
  }
}

export default function StatusPage() {
  const [probes, setProbes] = useState<Probe[]>(
    ENDPOINTS.map((u) => ({ url: u, status: "pending" })),
  );
  const [hydrated, setHydrated] = useState(false);
  const [now, setNow] = useState("—");

  useEffect(() => {
    // Mark hydration explicitly so we can SEE when React picks up.
    setHydrated(true);
    setNow(new Date().toLocaleString("fa-IR"));

    if (typeof console !== "undefined") {
      console.log("[/status] hydrated, starting probes");
    }

    let cancelled = false;
    ENDPOINTS.forEach(async (url) => {
      const p = await timedFetch(url);
      if (cancelled) return;
      if (typeof console !== "undefined") {
        console.log(`[/status] ${url} → ${p.status} (${p.ms}ms)`);
      }
      setProbes((prev) =>
        prev.map((pp) => (pp.url === url ? p : pp)),
      );
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main
      style={{
        fontFamily:
          'Vazirmatn, Tahoma, "Segoe UI", system-ui, sans-serif',
        background: "#F7F8FA",
        minHeight: "100vh",
        padding: "24px",
      }}
      dir="rtl"
    >
      <div style={{ maxWidth: 800, margin: "0 auto" }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, margin: "8px 0" }}>
          وضعیت سامانه
        </h1>
        <p style={{ fontSize: 12, color: "#6B7280" }}>
          صفحه‌ی رفع اشکال. اگر این صفحه برایتان درست رندر می‌شود ولی پنل
          ادمین/خرید کار نمی‌کند، مشکل از <b>بک‌اند</b> یا <b>کوکی</b> است،
          نه از React.
        </p>

        <div
          style={{
            background: "#fff",
            borderRadius: 16,
            padding: 16,
            marginTop: 16,
            border: "1px solid #E5E7EB",
          }}
        >
          <h2 style={{ fontWeight: 700, marginBottom: 8 }}>JavaScript</h2>
          <p style={{ fontSize: 14 }}>
            React hydration:{" "}
            <span
              style={{
                background: hydrated ? "#DCFCE7" : "#FEE2E2",
                color: hydrated ? "#16A34A" : "#DC2626",
                padding: "2px 8px",
                borderRadius: 4,
                fontWeight: 700,
              }}
            >
              {hydrated ? "✓ OK" : "✗ FAIL"}
            </span>
          </p>
          {!hydrated && (
            <p style={{ fontSize: 12, color: "#DC2626", marginTop: 4 }}>
              اگر این متن قرمز را می‌بینید، یعنی فایل‌های JS بارگذاری نشده‌اند
              یا قبل از اجرا خطا داده‌اند. Ctrl+Shift+R بزنید و در DevTools
              تب Network و Console را چک کنید.
            </p>
          )}
          <p style={{ fontSize: 12, color: "#6B7280", marginTop: 8 }}>
            بارگذاری در: <span dir="ltr">{now}</span>
          </p>
        </div>

        <div
          style={{
            background: "#fff",
            borderRadius: 16,
            padding: 16,
            marginTop: 16,
            border: "1px solid #E5E7EB",
          }}
        >
          <h2 style={{ fontWeight: 700, marginBottom: 8 }}>API probes</h2>
          <table
            style={{
              width: "100%",
              fontSize: 13,
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr style={{ background: "#F7F8FA" }}>
                <th style={th}>endpoint</th>
                <th style={th}>وضعیت</th>
                <th style={th}>زمان</th>
              </tr>
            </thead>
            <tbody>
              {probes.map((p) => (
                <tr key={p.url}>
                  <td style={{ ...td, fontFamily: "monospace" }} dir="ltr">
                    {p.url}
                  </td>
                  <td style={td}>
                    <StatusBadge status={p.status} />
                  </td>
                  <td style={td}>
                    {p.ms !== undefined ? `${p.ms}ms` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div
          style={{
            background: "#fff",
            borderRadius: 16,
            padding: 16,
            marginTop: 16,
            border: "1px solid #E5E7EB",
            fontSize: 13,
            lineHeight: 1.9,
          }}
        >
          <h2 style={{ fontWeight: 700, marginBottom: 8 }}>
            راهنمای تفسیر
          </h2>
          <ul style={{ paddingInlineStart: 20 }}>
            <li>
              <b>JS hydration FAIL</b>: فایل JS بارگذاری نشده / خطای syntax /
              بسته‌ی نادرست. Ctrl+Shift+R بزنید و Network tab را چک کنید.
            </li>
            <li>
              <b>/api/v1/me → 401 یا 403</b>: شما وارد نشده‌اید. این طبیعی است.
            </li>
            <li>
              <b>/api/v1/me → 200</b>: شما واردشده هستید. اگر admin هم می‌خواهید،
              کاربر باید <code dir="ltr">is_staff=True</code> داشته باشد.
            </li>
            <li>
              <b>/api/v1/marketplace/products → 500</b>: ستون‌های Product
              ساخته نشده‌اند. اجرا کنید:{" "}
              <code dir="ltr">
                docker compose exec backend python manage.py migrate
              </code>
            </li>
            <li>
              <b>/api/v1/prices → empty</b>: کرالر اجرا نشده. اجرا کنید:{" "}
              <code dir="ltr">make crawl-prices</code>
            </li>
            <li>
              <b>هر چیز دیگری → error/timeout</b>: شبکه‌ی بین فرانت و بک‌اند
              کار نمی‌کند. <code dir="ltr">BACKEND_URL</code> در env فرانت
              را بررسی کنید.
            </li>
          </ul>
        </div>

        <p
          style={{
            textAlign: "center",
            fontSize: 12,
            color: "#6B7280",
            marginTop: 16,
          }}
        >
          خروجی کنسول مرورگر را هم چک کنید — پیام‌های{" "}
          <code dir="ltr">[/status]</code> نشانگر دقیق اجرای کد هستند.
        </p>
      </div>
    </main>
  );
}

const th: React.CSSProperties = {
  textAlign: "start",
  padding: "8px 12px",
  fontWeight: 700,
  fontSize: 12,
  color: "#6B7280",
};
const td: React.CSSProperties = {
  padding: "8px 12px",
  borderTop: "1px solid #E5E7EB",
  fontSize: 12,
};

function StatusBadge({ status }: { status: Probe["status"] }) {
  let bg = "#F7F8FA",
    fg = "#6B7280",
    txt = String(status);
  if (status === "pending") {
    txt = "…";
  } else if (status === "error") {
    bg = "#FEE2E2";
    fg = "#DC2626";
    txt = "error";
  } else if (typeof status === "number") {
    if (status >= 200 && status < 300) {
      bg = "#DCFCE7";
      fg = "#16A34A";
    } else if (status === 401 || status === 403) {
      bg = "#FEF3C7";
      fg = "#A16207";
    } else {
      bg = "#FEE2E2";
      fg = "#DC2626";
    }
    txt = `HTTP ${status}`;
  }
  return (
    <span
      style={{
        background: bg,
        color: fg,
        padding: "2px 8px",
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 700,
      }}
    >
      {txt}
    </span>
  );
}
