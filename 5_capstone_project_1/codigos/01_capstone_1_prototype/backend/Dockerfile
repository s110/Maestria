# Le ponemos un nombre a esta etapa: "builder"
FROM python:3.12-slim AS builder

# 1. Optimizaciones de UV
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# 2. Traemos 'uv' desde su imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Cache inteligente (La parte más potente)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-install-project

# Empezamos desde cero con una imagen limpia de Python
FROM python:3.12-slim

WORKDIR /app

# 4. El truco maestro: COPIAR desde la etapa anterior
COPY --from=builder /app/.venv /app/.venv

# 5. Activar el entorno virtual de forma invisible
ENV PATH="/app/.venv/bin:$PATH"

# 6. Copiar tu código
COPY . .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]