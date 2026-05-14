# KeyhanGold frontend

Next.js 16 (App Router) — React 19, TypeScript strict, Tailwind v4,
RTL with `lang="fa"`. JWTs are HttpOnly cookies; the client never reads
or stores them.

```bash
pnpm install
pnpm dev
```

The dev server proxies `/api/*` to the Django backend
(`BACKEND_URL`, default `http://backend:8000`) and `/ws/*` for the
live-price WebSocket.

## Conventions

- All money displayed as toman (with Persian digits); all weights in mg/g
  via `lib/format.ts`.
- New pages go under `app/(group)/<route>/page.tsx`.
- Strings should flow through `next-intl` so roadmap #11 (multi-lang)
  is a pure translation effort, not a refactor.
