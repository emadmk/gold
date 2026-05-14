"use client";

import { useEffect, useState } from "react";

import type { User } from "@/lib/api";

export type AuthState =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "authenticated"; user: User };

/**
 * Fetches `/api/v1/me` and returns the current auth state.
 *
 * Always reaches a non-loading state within `timeoutMs` (default 8s),
 * even if the network hangs. This keeps the admin layout from sitting
 * on "در حال بررسی دسترسی…" forever.
 */
export function useMe(timeoutMs = 8000): AuthState {
  const [state, setState] = useState<AuthState>({ status: "loading" });

  useEffect(() => {
    let done = false;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      if (done) return;
      controller.abort();
      done = true;
      setState({ status: "anonymous" });
    }, timeoutMs);

    fetch("/api/v1/me", {
      credentials: "include",
      signal: controller.signal,
      headers: { Accept: "application/json" },
    })
      .then(async (r) => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        if (r.status === 401 || r.status === 403 || !r.ok) {
          setState({ status: "anonymous" });
          return;
        }
        try {
          const user = (await r.json()) as User;
          setState({ status: "authenticated", user });
        } catch {
          setState({ status: "anonymous" });
        }
      })
      .catch((err: unknown) => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        // Network error / abort → treat as anonymous so the UI moves on.
        if (typeof console !== "undefined") {
          console.warn("[useMe] fetch failed:", err);
        }
        setState({ status: "anonymous" });
      });

    return () => {
      done = true;
      clearTimeout(timer);
      controller.abort();
    };
  }, [timeoutMs]);

  return state;
}
