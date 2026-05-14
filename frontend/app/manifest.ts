import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "KeyhanGold",
    short_name: "KeyhanGold",
    description: "خرید و فروش آنلاین طلا و نقره",
    start_url: "/",
    display: "standalone",
    background_color: "#FFFFFF",
    theme_color: "#2D87F0",
    lang: "fa",
    dir: "rtl",
    icons: [
      { src: "/icon.svg", sizes: "any", type: "image/svg+xml" },
      { src: "/favicon.svg", sizes: "32x32", type: "image/svg+xml" },
    ],
  };
}
