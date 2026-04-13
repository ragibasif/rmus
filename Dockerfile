# Stage 1: Builder ---
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into the virtualenv
RUN uv sync --frozen --no-install-project --no-dev

# --- Stage 2: Runtime ---
FROM python:3.13-slim

# Install system dependencies (Essential for AcoustID)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    libchromaprint-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the venv and app code
COPY --from=builder /app/.venv /app/.venv
COPY . .

# CRITICAL: Match these to your Python version (3.13)
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/.venv/lib/python3.13/site-packages"
ENV PYTHONUNBUFFERED=1

CMD ["python", "server.py"]
