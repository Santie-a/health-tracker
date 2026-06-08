# Frontend — Implementation Plan

Ordered breakdown of the Next.js dashboard build into small, individually-shippable
tasks. Derived from [ARCHITECTURE.md](../ARCHITECTURE.md), [frontend/TODO.md](./TODO.md),
[DEPLOY.md](../DEPLOY.md), and the **already-built** gateway contract
(`server/app/domains/*/router.py` + `schemas.py`, served at `/openapi.json` and `/docs`).
The gateway is the single backend; the frontend mirrors its layered, resilient style.

Status legend: [ ] todo · [~] in progress · [x] done.

---

## Objective & UI philosophy (the principle that drives every design choice)

The frontend is **a single-user logging tool first, a dashboard second.** You log meals
and training from your phone, glance at today, and occasionally inspect trends. So:

- **Logging is the hot path** — fast, few taps, forgiving. Recent/repeat/quick-add over
  perfect data entry. Every log form works with the GPU box off and the watch never synced.
- **The dashboard is read-only context** — it composes the day from one call and degrades
  per-widget; a missing signal greys out one card, never blanks the page.
- **The browser is untrusted** — it never holds the gateway token or URL. All gateway
  access goes through a server-side BFF layer (Next route handlers / server actions). This
  is non-negotiable and matches the gateway's single-token auth ([auth.py](../server/app/core/auth.py)).
- **The OpenAPI schema is the contract** — types are generated from it, never hand-typed,
  so the frontend cannot silently drift from the backend.

**Build implications (carry through every phase):**

1. One typed gateway client, one place that handles auth + non-2xx + network errors.
2. Every data view ships its **loading + empty + error** states in the same task — no
   "happy path now, states later." An async view without all three is not done.
3. Resilience is structural: error boundaries per widget, a normalized error envelope,
   and explicit handling of the gateway's documented degraded paths (image-svc offline,
   partial dashboard, empty telemetry).

---

## Stack (decided)

| Concern                  | Choice                                                    | Rationale                                                                                                                                                |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Package manager          | **pnpm**                                                  | Fast, disk-efficient; pinned Node LTS (20/22) for the arm64 build.                                                                                       |
| Framework                | **Next.js (App Router) + TypeScript**                     | TODO-specified; the BFF keeps the token server-side.                                                                                                     |
| BFF / data access        | **Next Route Handlers, one per domain** under `app/api/*` | Explicit, typed, self-validating proxy per endpoint — over a catch-all. The only place the bearer token is used; browser only ever calls same-origin.    |
| Client cache / mutations | **TanStack Query (all reads + writes)**                   | One mental model: no server-component data fetching to mix with client mutations. Logging is mutation-heavy (optimistic updates, invalidation, retries). |
| Theme                    | **next-themes + shadcn tokens**                           | System-aware light/dark with a manual toggle.                                                                                                            |
| API types                | **openapi-typescript** (+ `openapi-fetch`)                | Generated types from `/openapi.json`; compile-time drift detection.                                                                                      |
| Styling                  | **Tailwind**                                              | TODO-specified.                                                                                                                                          |
| Components               | **shadcn/ui**                                             | Owned (copied-in) primitives, not a black-box dep — fits "modular, clean codebase."                                                                      |
| Charts                   | **Recharts**                                              | TODO-specified; sufficient for trend lines/bars.                                                                                                         |
| Forms                    | **react-hook-form + zod**                                 | Resolver schemas reused for client validation; mirrors gateway's Pydantic 422 contract.                                                                  |
| Dates                    | **date-fns** + a tiny `toLocal()`/`toUtc()` helper        | Gateway is UTC-only; conversion happens at the display/edge boundary, never in components.                                                               |

---

## Architecture & conventions (locked in _before_ views are written)

Mirror the server's layering so HTTP, data, and UI never bleed together. **Feature-first**
folders, one per gateway domain, so a new feature slots into one folder instead of
threading through shared files.

```
frontend/
  app/
    layout.tsx                 # shell: nav, providers, top-level error boundary
    (dashboard)/page.tsx       # Home / Today
    training/…                 # route segments per view
    nutrition/…
    trends/…
    recommendations/…
    api/                       # ── BFF: the ONLY place the gateway token is used ──
      [...gateway]/route.ts    #   thin authenticated proxy (or per-domain handlers)
  src/
    lib/
      gateway/
        client.ts              # server-only typed client (openapi-fetch + token + retry)
        errors.ts              # normalize gateway/network errors → GatewayError envelope
        types.gen.ts           # GENERATED from /openapi.json — do not edit
      query/                   # TanStack Query client, keys factory, fetch wrapper
      time.ts                  # UTC↔local helpers (the only place tz logic lives)
    features/
      dashboard/  { api.ts · hooks.ts · components/ }
      training/   { api.ts · hooks.ts · schemas.ts · components/ }
      nutrition/  { api.ts · hooks.ts · schemas.ts · components/ }
      telemetry/  { api.ts · hooks.ts · components/ }
      recommendations/ { api.ts · hooks.ts · components/ }
      ingest/     { api.ts · hooks.ts · components/ }   # Samsung CSV upload + report
    components/
      ui/                      # shadcn primitives (button, card, dialog, input…)
      async/                   # AsyncBoundary, QueryState, ErrorCard, EmptyState, Skeleton
      charts/                  # Recharts wrappers (TrendLine, GroupedBars) w/ empty states
```

**Data strategy (decided):** **all** gateway access — reads and writes — goes through the
BFF + TanStack Query. No server-component data fetching, so there's one cache/invalidation
model for a mutation-heavy app. (Server components are used only for the static shell.)

**Auth (decided):** the shared bearer token lives only in the Node server env
(`GATEWAY_TOKEN`), never `NEXT_PUBLIC_*`; the browser sees only same-origin `/api/*`. No
login screen — the service stays on LAN/VPN, matching the gateway. Revisit only if exposed.

**The layers (server → client):**

- **`lib/gateway/client.ts`** (server-only, `import 'server-only'`) — the "repository":
  the _only_ code that knows the gateway URL + token. Wraps `openapi-fetch`, adds the
  bearer header, one retry on transient/network errors, and converts every failure into a
  typed `GatewayError` (status, code, request_id, friendly message). Never throws raw.
- **`app/api/*` route handlers, one per domain** (the BFF) — thin auth proxy. Each handler
  validates its own inputs, calls the gateway client, and passes through status +
  normalized error body. Explicit and typed over a catch-all. The same-origin surface the
  browser talks to.
- **`features/<domain>/api.ts`** — browser-side fetchers hitting the BFF (typed).
- **`features/<domain>/hooks.ts`** — TanStack Query hooks (`useDashboard(date)`,
  `useLogMeal()`…) with query keys, invalidation, and optimistic updates. Components
  depend on hooks, never on `fetch`.
- **`components/`** — presentational; receive data + state, render. No data access.

**Reusability rules:**

- One `AsyncBoundary` wraps every data widget (Suspense + error boundary + retry); views
  never re-implement loading/error/empty.
- One query-keys factory (`queryKeys.dashboard(date)`, …) so invalidation is consistent.
- Domain `schemas.ts` (zod) are reused for both form validation and typing the BFF body.
- Generated `types.gen.ts` is the single source for request/response shapes.

**Resilience rules (see ARCHITECTURE.md "Resilience"):**

- Per-widget React error boundaries → one failing card shows a retry affordance, the rest
  of the dashboard renders.
- The gateway client never leaks a stack trace to the browser; it logs server-side and
  returns the normalized envelope, and never crashes the Node process on a 5xx.
- Documented degraded paths are first-class UI, not errors: photo meal returns
  `MealCreateResponse.degraded=true` → render the manual editor with a banner; empty
  telemetry → cards show "no watch data," manual views still fully work.
- Every query has explicit `isLoading` / empty / `isError` rendering (no assuming data).

---

## Critical path

A usable app needs **0 → 1 → 2** plus logging (**3, 4**). Trends (**5**),
recommendations (**6**), the strength-balance dashboard (**7**), and the Samsung import UI
(**8**) layer on without blocking each other. Deploy/polish (**9**) is last.

---

## Phase 0 — Scaffold & cross-cutting core ✅ DONE

The skeleton everything slots into. No views yet. Built on **Next 16.2 + React 19.2 +
Tailwind v4** (newer than planned — create-next-app's current default). Verified: build
passes, typecheck + lint clean, dev server serves the home page, and the BFF
`/api/health` route returns clean JSON with the gateway-**unreachable** path handled
gracefully (retried, normalized, never crashed). Green path pending a running gateway.

- [x] **0.1 Project scaffold** — `create-next-app` (App Router, TS, Tailwind, ESLint),
      Prettier, `tsconfig` path aliases (`@/lib`, `@/features`, `@/components`),
      `.gitignore` (node*modules, `.next`, `.env*`), `.env.example`
      (`GATEWAY_URL`, `GATEWAY_TOKEN`, server-only — never `NEXT_PUBLIC*\*`).
- [x] **0.2 OpenAPI type generation** — `pnpm gen:api` (openapi-typescript) →
      `src/lib/gateway/types.gen.ts`. Source is a committed `openapi.json` dumped from the
      FastAPI app (offline-reproducible); `gen:api:remote` regenerates from a live gateway.
      19 endpoints captured.
- [x] **0.3 Gateway client** (`lib/gateway/client.ts`, `server-only`) — `openapi-fetch` +
      `resilientFetch` (abort timeout + one retry on network/5xx); `gw()` unwraps or throws;
      `rawGatewayFetch` for multipart passthrough. `errors.ts` normalizes to `GatewayError`
      (kind/status/requestId/issues + friendly message). `env.ts` fails fast on unset URL.
- [x] **0.4 BFF proxy** (`app/api/`) — per-domain handlers (decided). `bff.ts` helpers
      (`respond`/`respondNoContent`/`proxyUpload`) keep handlers thin and guarantee a clean
      JSON body + status to the browser, never a stack trace. `app/api/health` smoke route
      lands first; domain routes land with their phases.
- [x] **0.5 Query layer** (`lib/query/`) — `makeQueryClient` (retry only on retryable
      `ApiError`, once), `QueryProvider`, `keys.ts` factory (all domains), `fetcher.ts`
      (`apiGet`/`apiSend` over the BFF + client-side `ApiError` with `fieldErrors()` for 422).
- [x] **0.6 Shared async primitives** (`components/async/`) — `AsyncBoundary`
      (Suspense + class error boundary + retry), `ErrorCard`, `EmptyState`, `Skeleton`,
      `QueryState` (the workhorse: explicit loading→error→empty→data).
- [x] **0.7 App shell** (`layout.tsx`) — responsive nav (top bar desktop / fixed bottom bar
      mobile: Today / Training / Nutrition / Trends / Advice / Import), root `AsyncBoundary`,
      `Providers` (next-themes system+toggle wrapping QueryProvider), shadcn-compatible
      oklch tokens in `globals.css`. System fonts (no network fetch → offline build).
- [x] **0.8 Time helpers** (`lib/time.ts`) — `todayISODate`, `shiftISODate`, `parseInstant`
      (naive→UTC), `formatInstant`, `formatISODate`, `toInstantISO`. The single UTC↔local home.

## Phase 1 — UI design system (shared primitives)

Build the reusable kit once so every view composes it. **Verify:** a Storybook-ish demo
route renders each primitive with loading/empty/error variants.

- [ ] **1.1 shadcn/ui install** + base primitives (button, card, input, select, dialog,
      sheet, tabs, toast, badge, skeleton). Tailwind tokens / theme.
- [ ] **1.2 Stat & layout primitives** — `StatCard` (value + label + unit + trend + empty),
      `SectionCard`, `MetricGrid`. All handle null values (greyed "—").
- [ ] **1.3 Chart wrappers** (`components/charts/`) — `TrendLine`, `GroupedBars` over
      Recharts with built-in empty/loading states, local-time axis, UTC-in / local-out.
- [ ] **1.4 Form kit** — react-hook-form + zod resolver helpers, `Field`, number/weight
      inputs, a `useGatewayMutation` wrapper mapping the gateway's 422 detail → field errors
      and surfacing 5xx via toast (never a white screen).

## Phase 2 — Today / Home dashboard

One call, full day. **Endpoint:** `GET /api/v1/dashboard?date=` → `DashboardOut`
(telemetry summary, training[], nutrition_totals, meals[], recommendations[]).

- [ ] **2.1 `useDashboard(date)` hook + BFF route.**
- [ ] **2.2 Day view** — date picker (defaults today, local), section cards:
  - Telemetry summary: steps / avg stress / HR / SpO2 / TDEE / sleep (`SleepSummary`);
    each null → "no watch data," never an error.
  - Training: today's sessions (swim/gym) with load/duration.
  - Nutrition: `Totals` (kcal/protein/carbs/fat) + meal list.
  - Recommendations: top items (links to Phase 7 view).
- [ ] **2.3 Per-section error boundaries + skeletons + empty states.** **Verify:** against
      gateway **seed data** (`python -m app.seed`) and against an empty day.

## Phase 3 — Training log + exercise catalog + set logger

**Endpoints:** `GET/POST /training`, `GET /training/{id}`, `POST /training/{id}/sets`,
`GET /exercises?q=&muscle=&category=`, `POST /exercises`.

- [ ] **3.1 Sessions list** — `useTrainingSessions({type,from,to})`; filter by type;
      empty/loading/error.
- [ ] **3.2 New session form** — swim (distance/pace/duration) vs gym (type-switched zod
      schema); optional inline `sets[]`; load auto-computes server-side (don't duplicate).
      Optimistic add + invalidate dashboard.
- [ ] **3.3 Exercise picker** — debounced search over `/exercises` with muscle/category
      filters; inline "quick-add custom" (`POST /exercises`, handle 409 dup gracefully).
      Reusable combobox.
- [ ] **3.4 Set logger** — under a session: add sets (reps × weight, RPE, warmup toggle,
      bodyweight + added weight); **"+set" / repeat-last-set** for fast entry; free-text
      exercise resolves server-side. Optimistic, mobile-first.

## Phase 4 — Nutrition: manual, serving, photo

**Endpoints:** `GET /meals?date=` (`DayNutrition`), `POST /meals`, `POST /meals/photo`
(multipart → `MealCreateResponse`, `degraded` flag), `POST /meals/{id}/items`,
`GET /foods?q=`, `/foods/recent`, `/foods/resolve?name=`.

- [ ] **4.1 Day nutrition view** — meals + totals; per-item shows estimated-vs-weighed
      (`MealItemOut.estimated`/`source`); empty/loading/error.
- [ ] **4.2 Food search + serving picker** — `/foods` search → choose portion × qty or
      grams, **live macro preview** before save (reuse `/foods/resolve` math client-side or
      preview via the item shape). Manual entry is the **default** path.
- [ ] **4.3 Fast logging** — recent foods (`/foods/recent`), raw-kcal quick-add,
      repeat-yesterday. Built on the same item-add component.
- [ ] **4.4 Photo flow** — upload → `POST /meals/photo`. **If `degraded=true`
      (image-svc offline): render the manual editor with a banner, not an error.** Otherwise
      show the estimate as an **editable** item list before save. The single most important
      resilience path — test image-svc both up and down.
- [ ] **4.5 Unified editable meal** — image-detected + searched + estimated items in one
      list; add items via `POST /meals/{id}/items` (food_id+portion×qty OR grams OR
      free-text+grams OR raw kcal). Optimistic, invalidates dashboard totals.

## Phase 5 — Trends

**Endpoints:** `GET /telemetry/daily?metric=&from=&to=` (`DailyRollup[]`),
`GET /telemetry?metric=&from=&to=` (raw). Body composition via telemetry/body-comp.

- [ ] **5.1 Range selector** (7d / 30d / 90d, local→UTC at the edge) + metric tabs.
- [ ] **5.2 Trend charts** — weight / body fat / skeletal muscle, sleep (total + stages),
      stress, steps over time via `TrendLine`/`GroupedBars`. Each chart: loading/empty (no
      data for range)/error independently. `sum` vs `avg` per metric semantics respected.

## Phase 6 — Recommendations + feedback

**Endpoints:** `GET /recommendations?date=` (lazy-generates), `POST /recommendations/run`,
`POST /recommendations/feedback` (`{date, feedback}` → 204; 404 if none stored).

- [ ] **6.1 List view** — `RecommendationItem` cards grouped by category/severity with
      signals; empty ("no recommendations / not enough data yet").
- [ ] **6.2 Feedback** — thumbs up/down → `POST /feedback`; optimistic, handle 404
      (regenerate via `/run` then retry) gracefully. Optional "re-run today" action.

## Phase 7 — Strength balance dashboard

**Endpoint:** `GET /training/stats?from=&to=` → `TrainingStats`.

- [ ] **7.1 Weekly sets-per-muscle bars** vs the 10–20 target band (`weekly_sets_per_muscle`).
- [ ] **7.2 Ratios** — push:pull and upper:lower (`push_pull_ratio`, `upper_lower_ratio`),
      with null-safe display.
- [ ] **7.3 Per-exercise** — volume load (`volume_load_per_muscle`), top set + estimated
      1RM trend + PR date (`per_exercise`/`ExerciseStat`); surface `unresolved_exercises` as a
      "map these to the catalog" nudge.

## Phase 8 — Samsung export import UI

**Endpoint:** `POST /api/v1/ingest/samsung` (multipart, one or more CSVs) → `IngestResponse`
(per-file `FileReport`: data_type, target, parsed/written/skipped, errors[] + totals).
Telemetry is complementary and import-only — this page never blocks manual logging.

- [ ] **8.1 Upload page** (`/import`) — multi-file drag-drop (the `com.samsung.*` CSVs),
      BFF multipart pass-through to `/ingest/samsung` (token server-side). Hint to include
      `sleep_stage` alongside `sleep`.
- [ ] **8.2 Per-file report** — render `FileReport[]` (parsed/written/skipped + expandable
      errors) and totals; unknown types shown as skipped, not errors. Idempotent re-upload is
      safe — say so. Loading/empty/error states; large uploads show progress, never hang the UI.

## Phase 9 — Polish, responsive, deploy

- [ ] **9.1 Responsive pass** — phone-first logging (Training, Nutrition); thumb-reachable
      primary actions; tested at mobile width.
- [ ] **9.2 Global states** — offline banner, toast on mutation success/failure, 404 page,
      root error boundary copy, theme-toggle finish.
- [ ] **9.3 Dockerfile (arm64)** — multi-stage `node:lts-alpine` standalone build; runs on
      the Pi5 alongside gateway + DB (`frontend→gateway` becomes localhost). Add to the Pi5
      `docker-compose.yml`; `GATEWAY_URL`/`GATEWAY_TOKEN` from env. Mirror server's DEPLOY.md.
- [ ] **9.4 Verification** — full run against seed data; lighthouse/responsive smoke;
      confirm token never reaches the browser (network tab shows only same-origin `/api/*`).

---

## Verification approach (per TODO "Verification")

- Develop against **gateway seed data** (`python -m app.seed --days N`) before real data.
- **Type from OpenAPI** (`openapi-typescript`) and regenerate on contract change so
  frontend/backend stay in sync — a failing typecheck is the drift alarm.
- Test the resilience paths explicitly: image-svc **offline** (degraded meal), empty
  telemetry day, a gateway 5xx (widget error card + retry), and a 422 (field errors).
- Basic responsive check — you'll log from your phone.

## Resolved decisions (2026-06-08)

- **Package manager:** pnpm, pinned Node LTS for the arm64 build.
- **BFF shape:** per-domain route handlers (explicit, typed, self-validating) over a
  catch-all proxy.
- **Data strategy:** BFF + TanStack Query for _all_ reads and writes; no server-component
  data fetching (one cache/invalidation model for a mutation-heavy app).
- **Auth surface:** single shared token in the Node server env only; no login screen
  (LAN/VPN single-user). Revisit only if exposed beyond the VPN.
- **Theme:** system-aware light/dark with a manual toggle (next-themes).
- **Scope:** v1 **includes** a Samsung-export upload UI (Phase 8), not just viewing.
