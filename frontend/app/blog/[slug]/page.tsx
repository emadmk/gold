import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";

type Post = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  body_md: string;
  cover_image: string | null;
  author: string;
  published_at: string | null;
};

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  let post: Post | null = null;
  try {
    post = await api<Post>(`/blog/posts/${slug}`, { cache: "no-store" });
  } catch {
    post = null;
  }

  return (
    <>
      <Header />
      <main className="container mx-auto px-4 py-10 max-w-3xl">
        {!post ? (
          <p>مطلب یافت نشد.</p>
        ) : (
          <article>
            {post.cover_image && (
              <img
                src={post.cover_image}
                alt={post.title}
                className="w-full rounded-2xl mb-6"
              />
            )}
            <h1 className="text-3xl font-bold mb-2">{post.title}</h1>
            <p className="text-sm text-[var(--color-text-muted)] mb-6">
              {post.author} ·{" "}
              {post.published_at
                ? new Date(post.published_at).toLocaleDateString("fa-IR")
                : ""}
            </p>
            {post.summary && (
              <p className="text-lg leading-8 text-[var(--color-text-muted)] mb-6">
                {post.summary}
              </p>
            )}
            {/*
              body_md is treated as plain-text paragraphs split by blank
              lines. Markdown rendering is intentionally NOT done with
              dangerouslySetInnerHTML to avoid XSS; the admin can use a
              real Markdown renderer behind a sanitiser when needed.
            */}
            {post.body_md.split(/\n{2,}/).map((para, i) => (
              <p key={i} className="leading-8 mb-4">
                {para}
              </p>
            ))}
          </article>
        )}
      </main>
      <Footer />
    </>
  );
}
