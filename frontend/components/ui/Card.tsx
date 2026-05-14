import * as React from "react";

import { cn } from "@/lib/cn";

export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      {...props}
      className={cn(
        "rounded-2xl bg-[var(--color-card)] border border-[var(--color-border)] shadow-[var(--shadow-card)]",
        className,
      )}
    />
  );
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={cn("p-5 border-b border-[var(--color-border)]", className)} />;
}

export function CardBody({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={cn("p-5", className)} />;
}

export function CardFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={cn("p-5 border-t border-[var(--color-border)] bg-[var(--color-bg-alt)] rounded-b-2xl", className)} />;
}
