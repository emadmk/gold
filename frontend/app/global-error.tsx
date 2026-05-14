"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    if (typeof console !== "undefined") {
      console.error("[global-error]", error);
    }
  }, [error]);

  return (
    <html lang="fa" dir="rtl">
      <body
        style={{
          fontFamily: "Vazirmatn, Tahoma, sans-serif",
          padding: 48,
          textAlign: "center",
          background: "#F7F8FA",
          color: "#111827",
        }}
      >
        <h1 style={{ color: "#DC2626", fontSize: 28, marginBottom: 12 }}>
          خطای حیاتی در برنامه
        </h1>
        <p style={{ color: "#6B7280" }}>
          متأسفانه برنامه به مشکل خورد. دکمه‌ی زیر را بزنید تا بارگذاری مجدد شود.
        </p>
        <pre
          dir="ltr"
          style={{
            background: "#FFF",
            padding: 12,
            borderRadius: 8,
            margin: "16px auto",
            maxWidth: 600,
            textAlign: "start",
            fontSize: 12,
            overflow: "auto",
          }}
        >
          {error.message}
          {error.digest ? `\n[digest ${error.digest}]` : ""}
        </pre>
        <button
          onClick={() => reset()}
          style={{
            padding: "10px 24px",
            borderRadius: 12,
            background: "#2D87F0",
            color: "#FFF",
            border: 0,
            cursor: "pointer",
          }}
        >
          بارگذاری مجدد
        </button>
      </body>
    </html>
  );
}
