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

RUN groupadd -r app && useradd -r -g app app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY pyproject.toml /app/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app" \
    PYTHONFAULTHANDLER=1

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

CMD ["/app/.venv/bin/mcp-server"]

# GitHub Container Registry Metadata
LABEL org.opencontainers.image.title="MCP Server Template" \
      org.opencontainers.image.description="A template for building Model Context Protocol servers" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="Your Name" \
      org.opencontainers.image.source="https://github.com/yourusername/mcp-server-template" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.url="https://github.com/yourusername/mcp-server-template" \
      org.opencontainers.image.documentation="https://github.com/yourusername/mcp-server-template#readme" \
      org.opencontainers.image.vendor="Your Name"