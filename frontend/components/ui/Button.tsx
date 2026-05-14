import * as React from "react";

import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "gold";
type Size = "sm" | "md" | "lg";

const variants: Record<Variant, string> = {
  primary:
    "bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]",
  secondary:
    "bg-[var(--color-secondary)] text-white hover:bg-[var(--color-secondary-hover)]",
  ghost:
    "bg-transparent text-[var(--color-text)] hover:bg-[var(--color-bg-alt)] border border-[var(--color-border)]",
  danger: "bg-[var(--color-danger)] text-white hover:opacity-90",
  gold: "bg-[var(--color-gold)] text-white hover:opacity-90",
};

const sizes: Record<Size, string> = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-5 py-2.5 text-sm",
  lg: "px-6 py-3 text-base",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  fullWidth?: boolean;
  loading?: boolean;
}

export function Button({
  variant = "primary",
  size = "md",
  fullWidth,
  loading,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={cn(
        "rounded-xl font-medium transition disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2",
        variants[variant],
        sizes[size],
        fullWidth && "w-full",
        className,
      )}
    >
      {loading ? <span className="animate-pulse">…</span> : children}
    </button>
  );
}
