const SERVER_BACKEND_URL = process.env.BACKEND_URL ?? "http://backend:8000";

export async function api<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const base = typeof window === "undefined" ? SERVER_BACKEND_URL : "";
  const url = `${base}/api/v1${path}`;
  const res = await fetch(url, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export type Wallet = {
  rial: { balance_rial: number; locked_rial: number; available_rial: number; currency: string };
  gold: {
    address: string;
    balance_mg: number;
    available_gold_mg: number;
    silver_balance_mg: number;
    available_silver_mg: number;
  };
};

export type User = {
  id: string;
  phone: string;
  email: string | null;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  is_phone_verified: boolean;
  is_vendor: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  is_frozen: boolean;
  tier: string;
  two_factor_enabled: boolean;
  share_trades: boolean;
  created_at: string;
};

export type Order = {
  id: string;
  order_number: string;
  kind: string;
  state: string;
  mg_amount: number;
  rial_amount: number;
  price_per_mg_rial: number;
  payment_deadline: string | null;
  paid_at: string | null;
  created_at: string;
  invoice_pdf: string | null;
  vendor: string | null;
  items: Array<{
    title_snapshot: string;
    quantity: number;
    unit_price_rial: number;
    line_total_rial: number;
  }>;
};

export type Quote = {
  quote_id: string;
  asset: string;
  side: string;
  price_per_mg_rial: number;
  valid_until: string;
};
