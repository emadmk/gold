"use client";

import { useEffect, useState } from "react";

import type { User } from "@/lib/api";

export type AuthState =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "authenticated"; user: User };

/** Fetches `/api/v1/me`. Returns `anonymous` on 401, `authenticated` on 200. */
export function useMe(): AuthState {
  const [state, setState] = useState<AuthState>({ status: "loading" });
  useEffect(() => {
    let cancelled = false;
    fetch("/api/v1/me", { credentials: "include" })
      .then(async (r) => {
        if (cancelled) return;
        if (r.status === 401 || r.status === 403) {
          setState({ status: "anonymous" });
          return;
        }
        if (!r.ok) {
          setState({ status: "anonymous" });
          return;
        }
        const user = (await r.json()) as User;
        setState({ status: "authenticated", user });
      })
      .catch(() => {
        if (!cancelled) setState({ status: "anonymous" });
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return state;
}
