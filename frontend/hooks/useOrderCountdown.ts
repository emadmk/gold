"use client";
import { useEffect, useState } from "react";

/** Returns the remaining ms until `deadline`, ticking every second. */
export function useOrderCountdown(deadlineIso: string | null): {
  remaining: number;
  expired: boolean;
  label: string;
} {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  const deadline = deadlineIso ? new Date(deadlineIso).getTime() : 0;
  const remaining = Math.max(0, deadline - now);
  const mins = Math.floor(remaining / 60_000);
  const secs = Math.floor((remaining % 60_000) / 1000);
  return {
    remaining,
    expired: remaining === 0,
    label: `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`,
  };
}
