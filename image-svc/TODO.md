# Image Service — Food -> Macros (GPU, RTX 5070)

Standalone FastAPI inference service on the desktop with the 5070. Only the gateway calls
it; it is never exposed to the browser. Can be off when not logging meals.

## Status (2026-05-31)
v0 is built and validated end-to-end. The `stub` and `vlm` (Qwen2.5-VL-3B) backends both
work; `/estimate` returns the stable contract; CUDA runs on the 5070 (~7.5 GB VRAM, ~2.2 s
per photo). Service runs from a single Python 3.12 venv. See [README.md](./README.md).

Macro table expanded to ~150 foods (198 rows incl. aliases) and the matcher rewritten to
be token-based (singularization + stopword/cooking-word filtering), replacing naive
substring matching. Loose VLM names now resolve well: a 31-case sweep hit 31/31, and the
nachos/zucchini-blossom photos that previously came back `(unmatched)` now map to real macros.

**Next:** v1 — multi-item detection/segmentation, and a wider table (jalapeño, tortilla
chips, etc.) once real meal photos show the gaps. Consider portion priors per food.

## Stack
- [x] FastAPI + Uvicorn. PyTorch CUDA matching the 5070 (Blackwell) — torch 2.11.0+cu128.
- [x] `.env` for model paths and the shared token used by the gateway (`.env` + `.env.example`).
- [x] Dockerfile with NVIDIA Container Toolkit (`--gpus all`). *Build not yet exercised; dev runs bare-metal.*

## API
- [x] `GET  /health` — reports backend, CUDA availability + device name, model-loaded.
- [x] `POST /estimate` — multipart image in; JSON out:
      `{ items: [{food, grams_est, kcal, protein_g, carbs_g, fat_g, confidence}], totals: {...} }`
      (+ `model_version`, `table_version`). Bearer-token auth.

## Model approach (iterate)
- [x] v0: vision-LLM (Qwen2.5-VL-3B) identifies foods + rough portions as strict JSON, mapped
      to the macro table. Pluggable behind a `FoodEstimator` interface (`stub` | `vlm`).
- [ ] v1: food detection/segmentation (e.g. a YOLO/segmentation model fine-tuned on food
      datasets like Food-101 / Nutrition5k) for multiple items per plate.
- [ ] v2: portion/volume estimation for better grams (reference object or depth heuristic).
- [x] Always return a confidence and let the gateway/frontend allow manual correction
      (unmatched foods are kept with zero macros + `(unmatched)` tag, not dropped).

## Data / mapping
- [x] Bundle a local macro lookup table (USDA FDC subset) so estimates don't need network
      (`app/nutrition/data/macros.csv`, ~150 foods, `usda-subset-0.2`).
- [x] Keep model + table versioned; record which version produced each estimate
      (`model_version` + `table_version` on every response).
- [x] Improve name matching so loose VLM detections resolve to macros (token-based matcher
      in `usda.py`: singularization + stopword filtering, no false substring hits).

## Verification
- [x] Confirm `torch.cuda.is_available()` true on the 5070.
- [~] Smoke test: validated on two real food photos (multi-item nachos + squash blossoms) and
      a 31-case name-matching sweep; still want a batch of YOUR real meal photos to tune ranges.
- [x] Latency budget: ~2.2 s for a single photo with the 3B model (well under the p95 target).
- [x] pytest: USDA lookup/scaling, stub determinism, detection->macros assembler, API contract
      (schema, validation, auth) — 15 tests, no GPU required.

## Alignment with the gateway's food DB (planned features)
The gateway is gaining manual + serving-based food entry, so macros must resolve
identically whether they came from a photo or were typed by hand.
- [ ] Treat the bundled macro CSV as the single source of truth for BOTH paths: the
      server seeds its `foods` table from this same file/version. Keep image-svc
      bundling its own copy (it must run offline) but bump `table_version` in lockstep.
- [ ] Consider emitting a canonical food key (matched table name/slug) on each item so
      the gateway can link `meal_items.food_id` directly instead of re-matching the name.
- [ ] **Decided:** extract the macro table + matcher (`app/nutrition/usda.py`) into an
      in-repo `packages/nutrition_core/` package that both image-svc and the server
      install (editable). One matcher (singularization + token matching), one
      `table_version`. Do this when the server is scaffolded (its consumer), not before
      — image-svc keeps bundling the macro *data* so it still runs offline. See
      ARCHITECTURE.md "Shared nutrition core".

## Resilience & error handling (see ARCHITECTURE.md "Resilience")
Audited 2026-06-07: input validation (content-type/size/decode) was already solid and
`_parse` defensive, but there was **no logging** and **no global handler**. Hardened
2026-06-07 (20 tests, incl. inference-failure -> 503 and global-handler -> clean 500):
- [x] Configure stdlib `logging` once at startup (level from `IMAGE_SVC_LOG_LEVEL`, to
      stdout). No `print`. *(`app/logging_config.py`)*
- [x] Catch-all exception handler -> logs with context + clean JSON 500, no stack trace
      to the gateway. HTTPException paths (415/413/400/401) keep their codes.
- [x] Lifespan wraps `MacroTable.from_csv` / model warmup: fail fast on misconfig but
      log a clear, actionable reason first; logs a startup line on success.
- [x] `detect()` failures (CUDA OOM, etc.) -> logged + returned as 503 the gateway treats
      as "degraded -> manual entry", not an opaque 500.
- [x] `_parse` logs a WARNING with the raw snippet before returning `[]`, so silent
      empty results are debuggable.
- [x] `PIL.Image.MAX_IMAGE_PIXELS` decompression-bomb guard -> 413 (configurable via
      `IMAGE_SVC_MAX_IMAGE_PIXELS`, default 100 MP). Bytes were capped; pixels now too.

## Notes
- Keep the contract stable; the gateway stores whatever this returns. Improving the model
  later should not change the response shape.
