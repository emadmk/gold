const STEPS = [
  "سبد خرید",
  "آدرس",
  "روش ارسال",
  "روش پرداخت",
  "تأیید نهایی",
] as const;

export function CheckoutSteps({ step }: { step: number }) {
  return (
    <ol className="flex flex-wrap gap-2 text-xs">
      {STEPS.map((label, i) => {
        const idx = i; // 0..4
        const done = idx < step;
        const here = idx === step;
        return (
          <li
            key={label}
            className={`flex items-center gap-1 px-3 py-1 rounded-full ${
              here
                ? "bg-[var(--color-primary)] text-white"
                : done
                ? "bg-[var(--color-primary-light)] text-[var(--color-primary-hover)]"
                : "bg-[var(--color-bg-alt)] text-[var(--color-text-muted)]"
            }`}
          >
            <span className="w-5 h-5 rounded-full bg-white/30 flex items-center justify-center text-[10px]">
              {idx + 1}
            </span>
            <span>{label}</span>
          </li>
        );
      })}
    </ol>
  );
}
