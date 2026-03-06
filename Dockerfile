# =============================================================================
# Codebase Companion — Dockerfile
# =============================================================================
# Multi-stage build:
#   Stage 1 (builder) — install all Python dependencies into a venv
#   Stage 2 (runtime) — copy only the venv + source code, no build tools
#
# Build:   docker build -t codebase-companion .
# Run:     docker run -p 8501:8501 --env-file .env codebase-companion
# =============================================================================

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies for packages that need compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (Docker layer cache optimisation)
COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip --quiet && \
    /opt/venv/bin/pip install -r requirements.txt --quiet


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# git is needed at runtime for cloning repositories
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source
COPY . .

# Make sure the venv binaries are first on PATH
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Disable HuggingFace tokenizer parallelism warnings
    TOKENIZERS_PARALLELISM=false

# Streamlit config: disable telemetry and set server options
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "streamlit_app.py"]
