import type { MetadataRoute } from "next";

import { api } from "@/lib/api";

const STATIC_PATHS = [
  "/", "/prices", "/marketplace", "/about", "/contact",
  "/faq", "/terms", "/privacy", "/blog",
] as const;

type Slugged = { slug: string; published_at?: string | null };

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const host = process.env.NEXT_PUBLIC_SITE_URL ?? "https://keyhan.gold";
  const entries: MetadataRoute.Sitemap = STATIC_PATHS.map((p) => ({
    url: `${host}${p}`,
    changeFrequency: "daily",
    priority: p === "/" ? 1 : 0.7,
  }));

  // Blog
  try {
    const r = await api<{ results: Slugged[] }>("/blog/posts");
    for (const p of r.results ?? []) {
      entries.push({
        url: `${host}/blog/${p.slug}`,
        lastModified: p.published_at ?? undefined,
        changeFrequency: "monthly",
        priority: 0.5,
      });
    }
  } catch {
    /* ignore */
  }
  // Marketplace products
  try {
    const r = await api<{ results: Slugged[] }>("/marketplace/products");
    for (const p of r.results ?? []) {
      entries.push({
        url: `${host}/marketplace/${p.slug}`,
        changeFrequency: "daily",
        priority: 0.6,
      });
    }
  } catch {
    /* ignore */
  }
  return entries;
}
