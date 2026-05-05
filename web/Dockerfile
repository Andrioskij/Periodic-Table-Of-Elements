# Multi-stage build for the Reflex browser app.
#
# Build context is the *repo root* — Reflex needs to reach src/ and
# data/ via the sys.path bridge that periodic_table_web/__init__.py
# inserts at import time:
#
#     docker build -t periodic-table-web -f web/Dockerfile .
#
# The image runs ``reflex run --env prod`` which serves the prerendered
# frontend on :3000 and the WebSocket backend on :8000. Both ports are
# exposed; the frontend connects to the backend via the same host.

# ---------------------------------------------------------------------------
# Stage 1 — builder: resolves Python deps and produces the frontend bundle.
# ---------------------------------------------------------------------------
FROM python:3.14-slim AS builder

WORKDIR /app

# curl + unzip + ca-certificates: Reflex's first `reflex export` call
# downloads a vendored Bun + Node toolchain into ~/.local/share/reflex/
# and uses curl + unzip to install it. Without these, the export step
# silently picks up no Bun and the frontend build fails.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        unzip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps before the source copy so the pip layer caches.
COPY web/requirements.txt /app/web/requirements.txt
RUN pip install --no-cache-dir -r /app/web/requirements.txt

# Application sources. The web layer reaches into src/ + data/ via the
# sys.path bridge in periodic_table_web/__init__.py — see web/README.md.
COPY src/ /app/src/
COPY data/ /app/data/
COPY web/ /app/web/

WORKDIR /app/web
ENV PYTHONPATH=/app

# Build the production frontend bundle into ./web/.web. --no-zip keeps
# the output unpacked so stage 2 can copy it directly without a zip
# round-trip.
RUN reflex export --frontend-only --no-zip

# ---------------------------------------------------------------------------
# Stage 2 — runtime: minimal image with the prebuilt bundle + Python deps.
# ---------------------------------------------------------------------------
FROM python:3.14-slim AS runtime

WORKDIR /app/web

# Reflex's `run --env prod` invokes the Next.js production server which
# needs the same Bun toolchain stage 1 downloaded. We carry the bundled
# toolchain forward instead of redownloading it at container start, so
# the first request doesn't pay the bootstrap cost.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        unzip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin/reflex /usr/local/bin/reflex
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

ENV PYTHONPATH=/app
ENV PATH="/root/.local/share/reflex/bun/bin:${PATH}"

EXPOSE 3000 8000

CMD ["reflex", "run", "--env", "prod"]
