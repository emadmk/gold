const FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

export function toPersianNumber(value: number | string): string {
  return String(value).replace(/\d/g, (d) => FA_DIGITS[Number(d)] ?? d);
}

export function formatRial(rial: number): string {
  // Display in toman as is customary
  const toman = Math.floor(rial / 10);
  return toPersianNumber(toman.toLocaleString("fa-IR")) + " تومان";
}

export function formatMg(mg: number): string {
  if (mg >= 1000) return toPersianNumber((mg / 1000).toFixed(3)) + " گرم";
  return toPersianNumber(mg) + " میلی‌گرم";
}
