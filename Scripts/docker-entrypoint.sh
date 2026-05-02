#!/usr/bin/env sh
set -eu
cd /workspace
# Copiar código inicial al volumen si está vacío
if [ -z "$(ls -A /workspace)" ]; then
    cp -r /app/* /workspace/
fi
uv sync --frozen
# Sin token ni contraseña: solo para uso local (puerto 8888 en tu máquina). No expongas este puerto a Internet.
exec uv run jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --allow-root \
  --ServerApp.token="" \
  --ServerApp.password=""