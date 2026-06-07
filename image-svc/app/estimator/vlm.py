"""Local vision-LLM estimator (Qwen2.5-VL).

Identifies multiple foods per plate and a rough portion in grams, returned as
strict JSON, which is then mapped to macros by the shared assembler. All heavy
imports (torch / transformers) are deferred to load time so this module is
importable on a machine without the GPU stack (e.g. running the stub backend).

Target hardware: RTX 5070 (12 GB, Blackwell / sm_120) -> needs the CUDA 12.8
build of PyTorch. The 3B model fits in bf16; use load_in_4bit for 7B.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any

from ..config import Settings
from ..nutrition.usda import MacroTable
from .base import Detection, FoodEstimator

if TYPE_CHECKING:
    from PIL.Image import Image

_log = logging.getLogger("image_svc.vlm")

_PROMPT = (
    "You are a nutrition assistant. Identify every distinct food in this photo. "
    "For each, estimate the edible portion in grams from visual cues (plate, "
    "utensils, typical serving sizes). Respond with ONLY a JSON array, no prose, "
    "each element: {{\"food\": str, \"grams_est\": number, \"confidence\": number "
    "between 0 and 1}}. Prefer these names when they fit: {names}."
)

_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


class VLMEstimator(FoodEstimator):
    name = "vlm"

    def __init__(self, settings: Settings, table: MacroTable):
        self._settings = settings
        self.table = table
        self._model: Any = None
        self._processor: Any = None
        if settings.preload_model:
            self.warmup()

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def _resolve_device(self) -> str:
        if self._settings.device != "auto":
            return self._settings.device
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"

    def warmup(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

        device = self._resolve_device()
        # transformers 5.x uses `dtype` (`torch_dtype` is deprecated).
        kwargs: dict[str, Any] = {
            "dtype": torch.bfloat16 if device == "cuda" else torch.float32,
        }
        if self._settings.load_in_4bit:
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            kwargs["device_map"] = "auto"
        elif device == "cuda":
            kwargs["device_map"] = "cuda"

        source = self._settings.model_dir or self._settings.model_name
        self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(source, **kwargs)
        self._processor = AutoProcessor.from_pretrained(source)
        if device == "cpu":
            self._model = self._model.to("cpu")
        self._model.eval()

    def detect(self, image: "Image") -> list[Detection]:
        self.warmup()
        import torch

        prompt = _PROMPT.format(names=", ".join(self.table.names))
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._processor(
            text=[text], images=[image], padding=True, return_tensors="pt"
        ).to(self._model.device)

        with torch.inference_mode():
            generated = self._model.generate(**inputs, max_new_tokens=512, do_sample=False)
        trimmed = generated[:, inputs["input_ids"].shape[1] :]
        raw = self._processor.batch_decode(
            trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        return self._parse(raw)

    @staticmethod
    def _parse(raw: str) -> list[Detection]:
        match = _JSON_ARRAY.search(raw)
        if not match:
            _log.warning("Model output had no JSON array; returning no detections: %r", raw[:200])
            return []
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            _log.warning("Model output was not valid JSON; returning no detections: %r", match.group(0)[:200])
            return []
        detections: list[Detection] = []
        for entry in data:
            if not isinstance(entry, dict) or "food" not in entry:
                continue
            try:
                grams = float(entry.get("grams_est", 0) or 0)
                conf = float(entry.get("confidence", 0.5) or 0.5)
            except (TypeError, ValueError):
                continue
            detections.append(
                Detection(
                    food=str(entry["food"]).strip(),
                    grams_est=max(grams, 0.0),
                    confidence=min(max(conf, 0.0), 1.0),
                )
            )
        return detections
