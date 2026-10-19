# PSXviewAI dashboard shell

React + TypeScript + Vite + Tailwind foundation for the evidence-backed PSX
research dashboard, tuned here for a simplified general-user view.

## What this phase includes

- **Responsive shell** with dark left navigation and light content area.
- **Watchlist cards** showing key metrics for a small PSX watchlist using
  clearly labelled prototype fixtures (not live market data).
- **Simplified status bar** focused on watchlist and snapshot timing, without
  internal data-warehouse details.
- **Compact portfolio news panel** that surfaces a short list of
  portfolio-relevant headlines without ticker clutter; each item shows source
  and rough recency.
- **Valuation snapshot placeholder** that explains fair value will only be shown
  once verified financial inputs are available, keeping estimates clearly
  separated from facts.

All dashboard data is served from in-memory fixtures via a typed repository
boundary so that a FastAPI backend can be wired in later without changing the
UI.

## Run locally

```bash
npm install
npm run dev
```

Then open the printed localhost URL in your browser.

Use `npm run build` for a static deployment to Vercel or Netlify.

If you add a backend later, expose `GET /api/dashboard` that matches
`src/types/dashboard.ts` and set `VITE_API_BASE_URL` in the workspace Secrets
panel. When that environment variable is absent the app stays in fixture mode,
which is the default used in this phase.
