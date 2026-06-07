# Frontend — Next.js Dashboard

Single-user dashboard + logging UI. Talks ONLY to the Python gateway. Build last, against
the gateway's OpenAPI contract.

## Stack
- [ ] Next.js (App Router) + TypeScript.
- [ ] Data fetching via Next Route Handlers / server actions that hold the gateway token
      server-side (the browser never sees the bearer token or the gateway URL directly).
- [ ] TanStack Query for client cache, or rely on server components + revalidation.
- [ ] Charts: Recharts (simple) for telemetry trends.
- [ ] Styling: Tailwind. Component lib optional (shadcn/ui).

## Views
- [ ] Home / today: one call to `GET /dashboard?date=` — sleep, steps, stress, training,
      nutrition totals, and today's recommendations.
- [ ] Training log: add swim (distance/pace/duration) and gym (exercises/sets/reps/weight) sessions.
- [ ] Meal log: upload a photo -> shows image-svc macro estimate -> editable before save; manual-entry fallback.
- [ ] Trends: weight / body composition / sleep / stress over time.
- [ ] Recommendations: list with thumbs up/down feeding the `feedback` field.

## Conventions
- [ ] All timestamps from the gateway are UTC; convert to local for display.
- [ ] No direct calls to DB or image-svc. If you're tempted to, add an endpoint on the gateway instead.
- [ ] Handle image-svc being offline gracefully (gateway returns a manual-entry path).

## Strength logging & balance stats (planned feature)
- [ ] Exercise picker: search the catalog (`GET /exercises?q=`) with muscle/category
      filters; quick-add a custom exercise inline.
- [ ] Set logger: under a day's gym session, add sets (reps × weight, RPE, warmup
      toggle); "+set" / repeat-last-set for fast entry; bodyweight + added weight.
- [ ] Balance dashboard: weekly sets-per-muscle-group bars vs the 10–20 target,
      push:pull / upper:lower ratios, per-exercise volume + estimated-1RM trend, PRs.

## Manual nutrition & serving entry (planned feature)
- [ ] Food search with serving picker: type "rice" -> choose "1 cup" × qty (or grams),
      live macro preview before save. Manual entry is the default path; the photo
      estimate is complementary.
- [ ] Fast logging: recent foods, favorites, repeat-yesterday, raw kcal quick-add.
- [ ] Unified meal view: image-detected, manually searched, and estimated items in one
      editable list; show which were estimated vs weighed.

## Resilience & error handling (see ARCHITECTURE.md "Resilience")
- [ ] React error boundaries around each view so one failing widget doesn't blank the
      whole dashboard; show a retry affordance.
- [ ] Centralize gateway calls in the server-side client: handle non-2xx + network
      errors, surface a friendly message, log server-side. Never crash on a 5xx.
- [ ] Image-svc-offline path: the gateway returns the manual-entry fallback — render the
      manual form, don't error. Same for any partial/degraded dashboard data.
- [ ] Loading + empty + error states for every data view (no assuming data exists).

## Verification
- [ ] Run against the gateway's seed data before real data exists.
- [ ] Type the API client from the gateway OpenAPI schema (e.g. openapi-typescript) so frontend/backend stay in sync.
- [ ] Basic responsive check (you'll log meals/training from your phone).
