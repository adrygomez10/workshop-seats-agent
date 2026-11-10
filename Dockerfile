FROM python:3.15.2-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv==0.13.6
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# PyYAML and zstandard publish no wheels for Python 3.15 yet.
FROM base AS build-tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# docker build --target quality .
FROM build-tools AS quality
RUN uv sync --frozen
COPY requirements-dev.txt ./
COPY scripts ./scripts
COPY tests ./tests
RUN /app/.venv/bin/python scripts/check_quality.py

FROM build-tools AS dependencies
RUN uv sync --frozen --no-dev

FROM base AS runtime
COPY --from=dependencies /app/.venv /app/.venv
RUN useradd --create-home workshop
USER workshop
ENTRYPOINT ["/app/.venv/bin/python", "-m", "workshop_seats.bootstrap"]
CMD ["--demo"]
