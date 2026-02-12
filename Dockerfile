FROM python:3.13.6-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock ./

FROM base AS dev
RUN uv sync --frozen
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
EXPOSE 8000
CMD ["uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS prod
RUN uv sync --no-dev --frozen
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --group tests --frozen
COPY . .
CMD ["uv", "run", "pytest"]
