# ── Multi-Stage Dockerfile for AutoSec TARA Assistant ──

# ── Base System Image ──────────────────────────────────────────────────────────
FROM python:3.10-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=1000 \
    PIP_RETRIES=5

WORKDIR /app

RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4 \
    && apt-get update && apt-get install -y --no-install-recommends \
       curl \
    && rm -rf /var/lib/apt/lists/*

# ── Target: Frontend (Streamlit UI - Lightweight, No PyTorch/CUDA/ChromaDB) ────
FROM base AS frontend

COPY requirements-frontend.txt .
RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 5 \
    -r requirements-frontend.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

# ── Target: API (FastAPI + CPU-only PyTorch + ChromaDB + LangChain + RAG) ──────
FROM base AS api

# 1. Install CPU-only PyTorch build from official PyTorch CPU wheel index
RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 5 \
    torch \
    --extra-index-url https://download.pytorch.org/whl/cpu

# 2. Install API requirements while preserving CPU-only PyTorch (no NVIDIA/CUDA wheels)
COPY requirements-api.txt .
RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 5 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements-api.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.api.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
