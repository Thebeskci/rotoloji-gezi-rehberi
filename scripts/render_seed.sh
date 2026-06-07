#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRAPI_URL="${STRAPI_URL:-}"
STRAPI_EMAIL="${STRAPI_EMAIL:-}"
STRAPI_PASSWORD="${STRAPI_PASSWORD:-}"

if [[ -z "${STRAPI_URL}" || -z "${STRAPI_EMAIL}" || -z "${STRAPI_PASSWORD}" ]]; then
  echo "Skipping initial ingest because STRAPI_URL, STRAPI_EMAIL, or STRAPI_PASSWORD is missing."
  exit 0
fi

echo "Waiting for Strapi to become reachable at ${STRAPI_URL}"
for attempt in $(seq 1 60); do
  if curl -fsS "${STRAPI_URL}/admin" >/dev/null 2>&1; then
    echo "Strapi is reachable after ${attempt} attempt(s)."
    break
  fi

  if [[ "${attempt}" == "60" ]]; then
    echo "Strapi did not become reachable before timeout."
    exit 1
  fi

  sleep 5
done

export PYTHONPATH="${ROOT_DIR}/python${PYTHONPATH:+:${PYTHONPATH}}"

cd "${ROOT_DIR}"
python -m rota_yz.ingest --seed "${ROOT_DIR}/data/seed_places.json"
