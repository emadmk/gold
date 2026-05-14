# `apps.blog` — Editorial

A small, fast blog with Persian-friendly categories. The frontend
renders `body_md` as paragraphs (no `dangerouslySetInnerHTML`); a
proper Markdown renderer can be added later behind a sanitiser.

## Models

| Model | Purpose |
|-------|---------|
| `Category` | Top-level taxonomy. Seeded by `seed_dev` with `news / education / analysis / faq / announcement`. |
| `Tag` | Flat tag list. |
| `Post` | `author`, `category`, `tags` (M2M), `title`, `slug`, `summary`, `body_md`, `cover_image`, `state` ∈ `draft / published / archived`, `views`, `published_at`. |

## Admin

`PostAdmin` has bulk **publish** and **archive** actions, a state
badge, autocomplete fields for category/tags/author, and
`prepopulated_fields` for `slug`. Date hierarchy on `published_at`.

## Endpoints (public)

```
GET /api/v1/blog/posts            ← list of published only
GET /api/v1/blog/posts/<slug>     ← detail; bumps Post.views
```

Drafts return 404. Archived posts are excluded from the list.

## Frontend

`frontend/app/blog/page.tsx` and `frontend/app/blog/[slug]/page.tsx`.

## Notes

`body_md` is **plain text** in v1. To upgrade:
1. Replace the paragraph split in `[slug]/page.tsx` with a Markdown
   renderer (e.g. `react-markdown` + `rehype-sanitize`).
2. Add a `body_html` cached column populated on save (admin action).
