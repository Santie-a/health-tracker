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

## Phase 1 — UI design system (shared primitives) ✅ DONE

Build the reusable kit once so every view composes it. Verified at `/design`: every
primitive renders with its variants and loading/empty/error states; build + typecheck +
lint clean, no console errors. **Decision:** hand-authored primitives (shadcn-style API,
oklch tokens) instead of running the shadcn CLI — cleaner on Next 16 + Tailwind v4 and
keeps the components owned. Toasts via **sonner** (no Radix). The Radix-based interactive
primitives (Dialog/Sheet/Select/Tabs) are **deferred to first use** (Phase 3+) so the tree
carries no unused components.

- [x] **1.1 Base primitives** — `Button` (cva variants + loading), `Card` (+parts),
      `Badge` (severity variants), `Input` (`invalid` ring), `Label`, `Separator`; sonner
      `Toaster` (theme-synced) mounted in `Providers`. Skeleton shipped in Phase 0.
- [x] **1.2 Stat & layout primitives** — `StatCard` (null → greyed "—" + empty hint),
      `SectionCard` (title + header action), `MetricGrid` (responsive 2→4 col).
- [x] **1.3 Chart wrappers** (`components/charts/`) — `ChartFrame` (loading/empty/error +
      client-mount gate via `useMounted`, killing the Recharts SSR sizing warning),
      `TrendLine`, `GroupedBars` (target band + per-bar `colorFor`). Token palette, themed
      tooltip, local-time axis (UTC-in / local-out).
- [x] **1.4 Form kit** — `Field` (label/hint/error + a11y), `NumberInput` (decimal pad +
      unit adornment), `useGatewayMutation` (422 → RHF `setError` per field, else friendly
      toast; success toast + query invalidation). RHF + zod ready for the logging forms.
- [x] **1.5 Demo route** (`/design`) — gallery of every primitive + variant + async state.
      *(Removed in the Phase 9 cleanup — it was a dev-only gallery of hardcoded sample data.)*

## Phase 2 — Today / Home dashboard ✅ DONE

One call, full day. Verified live against seed data (steps 10,238 · sleep 5h 52m ·
gym 60min/load 480/9 sets · meals + macro totals · two recommendations rendered) and
against an empty day (2020-01-01 → empty arrays + null telemetry → section empty states).
Shared types now alias the generated schema via `lib/gateway/types.ts`.

- [x] **2.1 `useDashboard(date)` hook + BFF route** — `app/api/dashboard` (typed gateway
      passthrough, requires `date`); `getDashboard` over `apiGet`; keyed by date.
- [x] **2.2 Day view** (`DashboardView`) — `DateNav` (prev/next/today + native picker,
      capped at today, local dates), section cards:
  - `TelemetrySummary`: steps / energy / avg HR / stress / SpO₂ / sleep + stage breakdown;
    each null → greyed "—", all-empty → "no watch data," never an error.
  - `TrainingSummary`: sessions with type badge, distance/duration/load/sets, time.
  - `NutritionSummary`: macro totals + meals (estimated badge, per-meal kcal).
  - `RecommendationsSummary`: severity-coloured cards + signals (feedback in Phase 6).
- [x] **2.3 States** — each section wrapped in its own `AsyncBoundary` (render-error
      isolation) over a layout-matched `DashboardSkeleton`; per-section empty states.

## Phase 3 — Training log + exercise catalog + set logger ✅ DONE

**Endpoints:** `GET/POST /training`, `GET /training/{id}`, `POST /training/{id}/sets`,
`GET /exercises?q=&muscle=&category=`, `POST /exercises`. First write-heavy phase; pulled
in the deferred Radix **Dialog** primitive + a reusable **Segmented** control. Verified
end-to-end through the BFF (list, exercise search, create session → load auto-computed
315 = 45×7, add set with free-text resolution, and the 422 path → normalized envelope)
and visually (list + filter, session detail + set logger, the new-session dialog with the
swim-conditional distance/pace fields). Forms use RHF's 3-generic `useForm` so the zod
*output* reaches `mutate`; `useWatch` keeps the React-Compiler lint clean.

- [x] **3.1 Sessions list** — `useTrainingSessions({type})`; All/Gym/Swim `Segmented`
      filter; rows link to detail; loading/empty/error.
- [x] **3.2 New session form** — `NewSessionDialog`: gym/swim toggle (swim reveals
      distance/pace, ridden on an inline set), datetime/duration/rpe/notes; `useGatewayMutation`
      (invalidate training + dashboard, success toast); load auto-computes server-side.
- [x] **3.3 Exercise picker** — `ExerciseCombobox`: debounced search, one-tap select,
      inline quick-add (`POST /exercises`, 409 → fall back to free text). Custom (input +
      dropdown + `useClickOutside`), no extra Radix dep. Free text resolves server-side.
- [x] **3.4 Set logger** — `/training/[id]` detail + `AddSetForm`: reps × weight, +weight,
      RPE, warm-up toggle; keeps exercise+weight after add for fast "+ Add set"; "Repeat
      last" copies the last set; invalidates session + dashboard.

## Phase 4 — Nutrition: manual, serving, photo ✅ DONE

**Endpoints:** `GET /meals?date=` (`DayNutrition`), `POST /meals`, `POST /meals/photo`
(multipart → `MealCreateResponse`, `degraded` flag), `POST /meals/{id}/items`,
`GET /foods?q=`, `/foods/recent`, `/foods/resolve?name=`. Verified live against seed data
(day 1,811 kcal; brown-rice serving preview 240 kcal = 123/100g × 195g; item-add) **and
the degraded photo path with image-svc offline** (gateway returns `degraded:true`, never
a 5xx → banner + manual editor). `DateNav` promoted to a shared component.

- [x] **4.1 Day nutrition view** (`/nutrition`) — `DateNav` + macro totals + meals list
      (estimated badge, photo icon, per-meal kcal); Log meal + Photo entry points.
- [x] **4.2 Food search + serving picker** — `FoodCombobox` (search `/foods`) → portion
      `<select>` × qty *or* custom grams, with a client-side **live macro preview**
      (`macros.ts`); free text is valid (resolved server-side on save).
- [x] **4.3 Fast logging** — recent-foods chips (`/foods/recent`) and a "Quick kcal" raw
      adder (name + kcal + macros), both inside the one `AddItemForm`.
- [x] **4.4 Photo flow** — `PhotoUpload` (multipart → `/meals/photo`, BFF `proxyUpload`).
      `degraded:true` → toast + navigate with `?degraded=1` → meal detail shows the
      **manual-entry banner**, never an error. (image-svc currently offline, so this is
      the live-tested path; the success path renders the returned items the same way.)
- [x] **4.5 Unified editable meal** (`/nutrition/[id]`) — per-meal totals + item list
      (detected/searched/estimated, estimated badge) + `AddItemForm` adding via
      `POST /meals/{id}/items` (food_id+portion×qty OR grams OR free-text OR raw kcal).

**Cross-cutting fix (read-after-write race).** An immediate invalidate→refetch after a
mutation can race the gateway's just-committed write and render stale (the "must refresh"
symptom). `useGatewayMutation` gained an `update(qc, data)` hook: the write endpoints
return the full updated entity, so we write it straight to the cache via `setQueryData`
(instant, race-free) and only `invalidate` *disjoint* aggregate keys (day/dashboard/list)
that aren't on screen during the edit. Applied to meal-item add, set add, and session
create (prepend to matching list caches). Pairs with the Phase-3 `no-store` fix (which
addressed the browser HTTP cache).

## Phase 5 — Trends ✅ DONE

**Endpoints:** `GET /telemetry/daily?metric=&from=&to=` (`DailyRollup[]`) plus **two new
gateway endpoints added this phase** (the telemetry table had no series read for these):
`GET /body-composition?from=&to=` (`BodyCompositionPoint[]`) and
`GET /telemetry/sleep?from=&to=` (`SleepNight[]`). Both follow the existing
router/service/repository/schemas pattern in the telemetry domain; OpenAPI types
regenerated. Verified live (8 body-comp points, 7 nights, 7 days of steps; metric tab
switch refetches; no console errors).

- [x] **5.1 Range selector** (7d / 30d / 90d, computed as UTC instants at the edge) +
      activity **metric tabs** (steps / stress / heart_rate / spo2 / energy_expenditure).
- [x] **5.2 Trend charts** (`TrendsView`) — **Body composition** (weight / muscle / body-fat
      from `/body-composition`), **Sleep** (total + deep hours from `/telemetry/sleep`),
      **Activity** (selected metric over `/telemetry/daily`, `sum` for steps/energy vs `avg`
      for the rest). Each `TrendLine` carries its own loading / empty / error (via
      `ChartFrame`), local-time x-axis. (Server-side: added `SleepNight`/`BodyCompositionPoint`
      schemas + `query_sleep_series`/`query_body_composition` repo fns + `body_router`.)

## Phase 6 — Recommendations + feedback ✅ DONE

**Endpoints:** `GET /recommendations?date=` (lazy-generates), `POST /recommendations/run`,
`POST /recommendations/feedback` (`{date, feedback}` → 204; 404 if none stored). Verified
live (06-08 → 2 recs; feedback → 204; empty day → 404 envelope; thumb highlights + toast;
no console errors).

- [x] **6.1 List view** (`RecommendationsView`, `/recommendations` = "Advice") — `DateNav`
      + severity-coloured `RecommendationCard`s (title/severity badge/detail/category +
      signals) + empty state; a **regenerate** button (`POST /run` → `setQueryData`).
      Extracted `RecommendationCard` to a shared component — the dashboard summary now
      reuses it (DRY).
- [x] **6.2 Feedback** — day-level thumbs up/down → `POST /feedback` (`"up"`/`"down"`),
      optimistic highlight + toast; **404 → `runRecommendations` then retry** once; resets
      when the day changes.

## Phase 7 — Strength balance dashboard ✅ DONE

**Endpoint:** `GET /training/stats?from=&to=` → `TrainingStats`. `BalanceView` at
`/training/balance` (linked from the Training header); 4w/8w/12w range. Verified live
(13 muscles, push:pull 1.33, upper:lower 2.33, Back Squat e1RM 128kg, "freestyle" flagged
unresolved; no console errors).

- [x] **7.1 Weekly sets-per-muscle bars** — avg sets/week per muscle (`GroupedBars` with the
      10–20 target band + per-bar under/in/over colouring). Computed as total credited sets ÷
      weeks-with-data.
- [x] **7.2 Ratios** — push:pull and upper:lower `StatCard`s, null-safe (`"—"` when absent),
      with a "balanced ≈ 1:1" hint.
- [x] **7.3 Per-exercise** — volume-load-by-muscle bars + a per-exercise table (sets, top
      weight, Epley e1RM, PR date, sorted by e1RM); `unresolved_exercises` surfaced as a
      "add them via the exercise picker" nudge. (1RM *trend* deferred — the stat is a single
      best e1RM, not a series; would need a server enhancement.)

## Phase 8 — Samsung export import UI ✅ DONE

**Endpoint:** `POST /api/v1/ingest/samsung` (multipart, repeated `files` field) →
`IngestResponse` (per-file `FileReport`: data_type, target, parsed/written/skipped,
errors[] + totals). Telemetry is import-only — this page never blocks manual logging.
Verified live against the **real export** (weight → 66 written, oxygen_saturation → 1,297
written) and an unsupported file (→ "unsupported — skipped"); no console errors.

- [x] **8.1 Upload page** (`/import`) — multi-file drag-drop + click-to-browse, selected-
      files list (size + remove), `Import N files` button. BFF `proxyUpload` streams the
      multipart `files` to `/ingest/samsung` (token server-side). Hint to include
      `sleep_stage` alongside `sleep`; idempotent-reupload note.
- [x] **8.2 Per-file report** (`ImportReport`) — totals badges (written/parsed/skipped) +
      per-file table (target, parsed/written/skipped) + expandable per-file error lists;
      unknown types show "unsupported — skipped" (not an error). Success invalidates
      dashboard/telemetry/recommendations. (Upload is one-shot; the button shows a spinner.)

## Phase 9 — Polish, responsive, deploy

Polish done (9.1 + 9.2); **deploy (9.3) intentionally out of scope for this session.**

- [x] **9.1 Responsive pass** — added a phone top bar (brand + theme toggle; the toggle
      was desktop-only) alongside the fixed bottom nav. Verified Today + Nutrition at 375px:
      macro grids reflow 2-col, header actions fit, tables scroll (`overflow-x-auto`),
      dialogs are `w-[calc(100%-2rem)]`.
- [x] **9.2 Global states** — `ConnectionBanner` (polls BFF health; shows only when the
      gateway is unreachable/degraded), `app/error.tsx` (route error boundary + retry),
      `app/not-found.tsx` (404 → Back to Today). Mutation toasts already app-wide via
      `useGatewayMutation`. Removed the orphaned `GatewayStatus` (folded into the banner).
- [ ] **9.3 Dockerfile (arm64)** — DEFERRED (not this session). Multi-stage standalone
      build for the Pi5; `GATEWAY_URL`/`GATEWAY_TOKEN` from env; add to the Pi5 compose.
- [~] **9.4 Verification** — done per-phase against seed data + the real Samsung export;
      token confirmed server-only (browser only ever calls same-origin `/api/*`). Formal
      lighthouse/full-deploy smoke pairs with 9.3.

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
