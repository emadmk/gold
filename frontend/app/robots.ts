import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const host = process.env.NEXT_PUBLIC_SITE_URL ?? "https://keyhan.gold";
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/admin/", "/vendor/", "/api/", "/dashboard", "/wallet/", "/orders", "/profile", "/kyc", "/transfer", "/delivery", "/notifications"],
      },
    ],
    sitemap: `${host}/sitemap.xml`,
    host,
  };
}
