# Image Service — Food → Macros

Standalone FastAPI inference service (GPU, RTX 5070). Takes a meal photo and returns a per-item macro estimate. **Only the gateway calls it** — never the browser. Can be off when not logging meals.

See [../ARCHITECTURE.md](../ARCHITECTURE.md) for how it fits the system.

## API

| Method | Path        | Auth   | Description                                   |
|--------|-------------|--------|-----------------------------------------------|
| GET    | `/health`   | none   | Status, backend, CUDA availability, device.   |
| POST   | `/estimate` | bearer | Multipart `image` → macro estimate (below).   |

`POST /estimate` response (stable contract — the gateway stores this verbatim):

```json
{
  "items": [
    {"food": "chicken breast", "grams_est": 150.0, "kcal": 247.5,
     "protein_g": 46.5, "carbs_g": 0.0, "fat_g": 5.4, "confidence": 0.82}
  ],
  "totals": {"kcal": 247.5, "protein_g": 46.5, "carbs_g": 0.0, "fat_g": 5.4},
  "model_version": "Qwen/Qwen2.5-VL-3B-Instruct",
  "table_version": "usda-subset-0.1"
}
```

Unidentified foods are kept with `" (unmatched)"` appended and zero macros, so
the gateway/UI can prompt for a manual correction rather than dropping them.

## Backends

Selected by `IMAGE_SVC_BACKEND`:

- **`stub`** (default) — deterministic placeholder, no GPU or model download.
  Lets the gateway integrate against the real response shape immediately.
- **`vlm`** — local vision-LLM (Qwen2.5-VL) identifies foods + portions, mapped
  to macros via the bundled USDA table. This is the v0 target.

## Run

Use a **Python 3.12** venv — PyTorch has no 3.14 wheels, and the RTX 5070
(Blackwell / sm_120) needs the CUDA 12.8 torch build pinned in `requirements.txt`.

```powershell
cd image-svc
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --port 8001
# GET  http://localhost:8001/health
# docs http://localhost:8001/docs
```

The backend is chosen by `IMAGE_SVC_BACKEND` in `.env` (`stub` or `vlm`). With
`vlm`, the first request downloads the model to the HF cache (or
`IMAGE_SVC_MODEL_DIR`); set `IMAGE_SVC_PRELOAD_MODEL=true` to load it at startup.
The `stub` backend needs no GPU or model download.

### Docker (GPU)

```powershell
docker build -t health-image-svc .
docker run --gpus all -p 8001:8001 -v hf-cache:/models `
  -e IMAGE_SVC_API_TOKEN=... health-image-svc
```

## Config

All vars are `IMAGE_SVC_`-prefixed; see [.env.example](./.env.example). Copy it
to `.env`. Key ones: `API_TOKEN` (shared with the gateway), `BACKEND`,
`MODEL_NAME`, `DEVICE`, `LOAD_IN_4BIT`.

## Tests

```powershell
.venv\Scripts\python -m pytest
```

Covers the USDA lookup/scaling, the deterministic stub, the detection→macros
assembler, and the API contract (schema, validation, auth). No GPU required —
the VLM backend's heavy imports are deferred so the suite runs on the stub.

## Layout

```
app/
  main.py            FastAPI app: /health, /estimate, wiring
  config.py          pydantic-settings (.env)
  auth.py            shared bearer-token dependency
  schemas.py         response contract
  estimator/
    base.py          FoodEstimator ABC + detection→macros assembler
    stub.py          deterministic placeholder backend
    vlm.py           Qwen2.5-VL backend (lazy torch/transformers imports)
  nutrition/
    usda.py          macro-table loader + lookup
    data/macros.csv  bundled USDA subset (per-100g)
tests/
```
