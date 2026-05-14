"use client";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { toPersianNumber } from "@/lib/format";

type Point = { t: string; price: number };

export function PriceChart({ data }: { data: Point[] }) {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="t" tick={{ fontSize: 11 }} />
          <YAxis
            tick={{ fontSize: 11 }}
            tickFormatter={(v: number) => toPersianNumber((v / 10_000_000).toFixed(0)) + "م"}
          />
          <Tooltip
            formatter={(v: number) => toPersianNumber(Math.floor(v / 10).toLocaleString("fa-IR")) + " تومان"}
          />
          <Line type="monotone" dataKey="price" stroke="#D4AF37" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
