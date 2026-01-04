FROM mcr.microsoft.com/playwright/python:v1.55.0-noble AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Taipei \
    PATH="/app/.venv/bin:$PATH"

COPY fetnet_automation ./fetnet_automation
COPY pyproject.toml ./

RUN mkdir -p tmp/jwt_tokens tmp/downloads tmp/exports logs credentials

RUN chown -R pwuser:pwuser /app
USER pwuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["python", "-m", "fetnet_automation"]
CMD ["--help"]
