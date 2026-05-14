import * as React from "react";

import { cn } from "@/lib/cn";

type Kind = "info" | "success" | "warning" | "danger";

const styles: Record<Kind, string> = {
  info: "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)]",
  success: "bg-[var(--color-success-light)] text-[var(--color-success)]",
  warning: "bg-amber-100 text-amber-800",
  danger: "bg-[var(--color-danger-light)] text-[var(--color-danger)]",
};

export function Alert({
  kind = "info",
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { kind?: Kind }) {
  return (
    <div
      role="alert"
      {...props}
      className={cn(
        "rounded-lg px-3 py-2 text-sm",
        styles[kind],
        className,
      )}
    >
      {children}
    </div>
  );
}
