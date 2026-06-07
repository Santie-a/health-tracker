# GPU image service. Run with the NVIDIA Container Toolkit: `docker run --gpus all`.
# Base ships CUDA 12.8 + cuDNN to match the RTX 5070 (Blackwell / sm_120).
# Python 3.12 (not the host's 3.14) so the torch cu128 wheels resolve.
FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 python3.12-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first for layer caching.
COPY requirements.txt ./
RUN python3.12 -m pip install --upgrade pip \
    && python3.12 -m pip install -r requirements.txt

COPY app ./app

# Persisted HF model cache; mount a volume here to avoid re-downloading.
VOLUME ["/models"]

ENV IMAGE_SVC_BACKEND=vlm
EXPOSE 8001

CMD ["python3.12", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
