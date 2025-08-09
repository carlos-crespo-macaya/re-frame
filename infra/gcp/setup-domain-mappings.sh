#!/usr/bin/env bash
set -euo pipefail

# Cloud Run custom domain mappings helper
#
# Creates domain mappings for frontend and/or backend services and prints the
# required DNS records, then optionally waits for certificate provisioning.
#
# Env vars (set the ones you need):
#   PROJECT_ID            - GCP project id (required if not set in gcloud config)
#   REGION                - Cloud Run region (default: europe-west1)
#   FRONTEND_SERVICE      - Cloud Run service name for the frontend
#   BACKEND_SERVICE       - Cloud Run service name for the backend
#   FRONTEND_DOMAIN       - Custom domain for the frontend (e.g. re-frame.social)
#   BACKEND_DOMAIN        - Custom domain for the backend (e.g. api.re-frame.social)
#   WAIT_MINUTES          - If set (e.g. 10), poll readiness up to N minutes
#
# Usage examples:
#   REGION=europe-west1 FRONTEND_SERVICE=re-frame-frontend FRONTEND_DOMAIN=re-frame.social \
#     ./infra/gcp/setup-domain-mappings.sh
#
#   REGION=europe-west1 BACKEND_SERVICE=re-frame-backend BACKEND_DOMAIN=api.re-frame.social \
#     ./infra/gcp/setup-domain-mappings.sh

echo "== Cloud Run domain mappings setup =="

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud not found. Install the Google Cloud SDK." >&2
  exit 1
fi

PROJECT_ID=${PROJECT_ID:-"$(gcloud config get-value project 2>/dev/null || true)"}
if [[ -z "${PROJECT_ID}" ]]; then
  echo "PROJECT_ID is not set and not configured in gcloud." >&2
  exit 1
fi

REGION=${REGION:-europe-west1}

create_mapping() {
  local service="$1"; shift
  local domain="$1"; shift

  if [[ -z "${service}" || -z "${domain}" ]]; then
    return 0
  fi

  echo "\n→ Creating domain mapping: ${domain} → ${service} (${REGION})"
  # Use beta track because --region on domain-mappings is there
  if gcloud beta run domain-mappings describe --domain="${domain}" --region="${REGION}" \
      --project="${PROJECT_ID}" >/dev/null 2>&1; then
    echo "  Mapping already exists. Skipping create."
  else
    gcloud beta run domain-mappings create \
      --service="${service}" \
      --domain="${domain}" \
      --project="${PROJECT_ID}" \
      --region="${REGION}"
  fi

  echo "\nRequired DNS records for ${domain}:"
  gcloud beta run domain-mappings describe \
    --domain="${domain}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format="table(status.resourceRecords[].name,status.resourceRecords[].type,status.resourceRecords[].rrdata)" || true
}

wait_ready() {
  local domain="$1"; shift
  local minutes=${WAIT_MINUTES:-0}
  if [[ "${minutes}" -le 0 ]]; then
    return 0
  fi
  echo "\n⏳ Waiting up to ${minutes} minute(s) for certificate provisioning: ${domain}"
  local until=$(( $(date +%s) + minutes*60 ))
  while (( $(date +%s) < until )); do
    local status reason
    read -r status reason < <(gcloud beta run domain-mappings list \
      --project="${PROJECT_ID}" --region="${REGION}" \
      --filter="metadata.name=${domain}" \
      --format="value(status.conditions[?type=Ready].status,status.conditions[?type=Ready].reason)" || true)
    if [[ "${status}" == "True" ]]; then
      echo "  Ready"; return 0
    fi
    echo "  Not ready yet (reason: ${reason:-n/a})..."
    sleep 15
  done
  echo "⚠️  Timed out waiting for ${domain} to become Ready. It will continue provisioning in the background."
}

if [[ -n "${FRONTEND_SERVICE:-}" && -n "${FRONTEND_DOMAIN:-}" ]]; then
  create_mapping "${FRONTEND_SERVICE}" "${FRONTEND_DOMAIN}"
  wait_ready "${FRONTEND_DOMAIN}"
fi

if [[ -n "${BACKEND_SERVICE:-}" && -n "${BACKEND_DOMAIN:-}" ]]; then
  create_mapping "${BACKEND_SERVICE}" "${BACKEND_DOMAIN}"
  wait_ready "${BACKEND_DOMAIN}"
fi

echo "\n✅ Done. If status is not Ready yet, DNS may still be propagating."


