import Link from "next/link";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Card, CardBody } from "@/components/ui/Card";
import { api } from "@/lib/api";

type Post = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  cover_image: string | null;
  category: { code: string; title_fa: string } | null;
  author: string;
  published_at: string | null;
};

export default async function BlogIndexPage() {
  let r: { results: Post[] } | null = null;
  try {
    r = await api<{ results: Post[] }>("/blog/posts", { cache: "no-store" });
  } catch {
    r = null;
  }
  const posts = r?.results ?? [];

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold mb-6">وبلاگ KeyhanGold</h1>
        {posts.length === 0 ? (
          <p className="text-sm text-[var(--color-text-muted)]">
            هنوز مطلبی منتشر نشده است.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {posts.map((p) => (
              <Link key={p.id} href={`/blog/${p.slug}`}>
                <Card className="hover:shadow-[var(--shadow-card-hover)] transition h-full">
                  <CardBody className="space-y-2">
                    {p.cover_image ? (
                      <img
                        src={p.cover_image}
                        alt={p.title}
                        className="w-full h-40 object-cover rounded-md"
                      />
                    ) : (
                      <div className="w-full h-40 rounded-md bg-[var(--color-primary-light)] flex items-center justify-center text-4xl">
                        📝
                      </div>
                    )}
                    <h2 className="font-bold">{p.title}</h2>
                    <p className="text-sm text-[var(--color-text-muted)]">
                      {p.summary}
                    </p>
                    <p className="text-xs">
                      {p.author} ·{" "}
                      {p.published_at
                        ? new Date(p.published_at).toLocaleDateString("fa-IR")
                        : "—"}
                    </p>
                  </CardBody>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
