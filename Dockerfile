# Imagen de desarrollo: Jupyter Lab + dependencias del curso (uv + uv.lock).
# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN echo 'deb https://deb.debian.org/debian bookworm main contrib non-free non-free-firmware' > /etc/apt/sources.list \
    && echo 'deb https://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list \
    && echo 'deb https://deb.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
    && rm -rf /var/lib/apt/lists/*

ENV UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY Scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY . /app

EXPOSE 8888

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]