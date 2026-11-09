FROM python:3.15.2-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv==0.13.6
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# docker build --target quality .
FROM base AS quality
RUN uv sync --frozen
COPY requirements-dev.txt ./
COPY scripts ./scripts
COPY tests ./tests
RUN /app/.venv/bin/python scripts/check_quality.py

FROM base AS runtime
RUN uv sync --frozen --no-dev \
    && useradd --create-home workshop
USER workshop
ENTRYPOINT ["/app/.venv/bin/python", "-m", "workshop_seats.bootstrap"]
CMD ["--demo"]
