import * as React from "react";

import { cn } from "@/lib/cn";

type Tone = "neutral" | "primary" | "success" | "warning" | "danger" | "gold";

const tones: Record<Tone, string> = {
  neutral: "bg-[var(--color-bg-alt)] text-[var(--color-text-muted)]",
  primary: "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)]",
  success: "bg-[var(--color-success-light)] text-[var(--color-success)]",
  warning: "bg-amber-100 text-amber-800",
  danger: "bg-[var(--color-danger-light)] text-[var(--color-danger)]",
  gold: "bg-[var(--color-gold-light)] text-[var(--color-gold)]",
};

export function Badge({
  tone = "neutral",
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      {...props}
      className={cn("inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium", tones[tone], className)}
    />
  );
}
