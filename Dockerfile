FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml ./
COPY uv.lock ./
COPY src ./src/

RUN uv venv && \
    uv pip install -e .

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN groupadd -r otrs && useradd -r -g otrs otrs

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY pyproject.toml /app/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src" \
    PYTHONFAULTHANDLER=1

ENV OTRS_BASE_URL="" \
    OTRS_USERNAME="" \
    OTRS_PASSWORD="" \
    OTRS_VERIFY_SSL="false" \
    OTRS_DEFAULT_QUEUE="Raw" \
    OTRS_DEFAULT_STATE="new" \
    OTRS_DEFAULT_PRIORITY="3 normal" \
    OTRS_DEFAULT_TYPE="Unclassified"

RUN chown -R otrs:otrs /app
USER otrs

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import otrs_mcp.server; print('OTRS MCP Server is healthy')" || exit 1

CMD ["python", "-m", "otrs_mcp.main"]

LABEL org.opencontainers.image.title="OTRS MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for OTRS integration" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="Season Poon" \
      org.opencontainers.image.source="https://github.com/yourusername/otrs-mcp-server" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.url="https://github.com/yourusername/otrs-mcp-server" \
      org.opencontainers.image.documentation="https://github.com/yourusername/otrs-mcp-server#readme" \
      org.opencontainers.image.vendor="Season Poon"