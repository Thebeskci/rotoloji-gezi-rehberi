#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-8501}"

STREAMLIT_BIN=""

if [[ -x "${ROOT_DIR}/.live-venv/bin/streamlit" ]]; then
  STREAMLIT_BIN="${ROOT_DIR}/.live-venv/bin/streamlit"
elif [[ -x "${ROOT_DIR}/.venv/bin/streamlit" ]]; then
  STREAMLIT_BIN="${ROOT_DIR}/.venv/bin/streamlit"
elif [[ -x "${ROOT_DIR}/.frontend-venv/bin/streamlit" ]]; then
  STREAMLIT_BIN="${ROOT_DIR}/.frontend-venv/bin/streamlit"
elif command -v streamlit >/dev/null 2>&1; then
  STREAMLIT_BIN="$(command -v streamlit)"
else
  echo "No Streamlit runtime found. Create a Python 3.12 env and run 'pip install -e .'" >&2
  exit 1
fi

export STREAMLIT_DATA_MODE="${STREAMLIT_DATA_MODE:-snapshot}"
export PYTHONPATH="${ROOT_DIR}/python"

exec "${STREAMLIT_BIN}" run "${ROOT_DIR}/frontend/app.py" \
  --server.port "${PORT}" \
  --server.address 0.0.0.0 \
  --server.headless true
