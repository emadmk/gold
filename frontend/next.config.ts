import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  poweredByHeader: false,
  // App Router (default in Next 16 — no `pages/`).
  experimental: {
    typedRoutes: true,
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "geolocation=(), microphone=(), camera=(self), payment=()",
          },
        ],
      },
    ];
  },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${process.env.BACKEND_URL ?? "http://backend:8000"}/api/:path*` },
      { source: "/ws/:path*", destination: `${process.env.BACKEND_WS_URL ?? "http://backend:8000"}/ws/:path*` },
    ];
  },
};

export default nextConfig;
