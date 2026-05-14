"use client";
import { useEffect, useState } from "react";

export type LiveSnapshot = Record<string, number>;

export function useLivePrice(): LiveSnapshot {
  const [data, setData] = useState<LiveSnapshot>({});
  useEffect(() => {
    if (typeof window === "undefined") return;
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/prices/`);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data) as { type: string; data: LiveSnapshot };
        if (msg.data) setData((prev) => ({ ...prev, ...msg.data }));
      } catch {
        /* ignore */
      }
    };
    return () => ws.close();
  }, []);
  return data;
}
