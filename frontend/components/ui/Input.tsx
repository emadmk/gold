import * as React from "react";

import { cn } from "@/lib/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, ...props }, ref) => (
    <label className="block">
      {label ? (
        <span className="block mb-1 text-sm text-[var(--color-text)]">{label}</span>
      ) : null}
      <input
        ref={ref}
        {...props}
        className={cn(
          "w-full rounded-lg border bg-[var(--color-card)] px-3 py-2 text-sm",
          "focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]",
          error
            ? "border-[var(--color-danger)]"
            : "border-[var(--color-border)]",
          className,
        )}
      />
      {error ? (
        <span className="mt-1 block text-xs text-[var(--color-danger)]">{error}</span>
      ) : hint ? (
        <span className="mt-1 block text-xs text-[var(--color-text-muted)]">{hint}</span>
      ) : null}
    </label>
  ),
);
Input.displayName = "Input";
