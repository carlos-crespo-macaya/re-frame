#!/bin/bash

# Load configuration
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/config.sh"

export PROJECT_ID=$GCP_PROJECT_ID
export REGION=$GCP_REGION
export REPO="re-frame"

gcloud artifacts repositories set-cleanup-policies "$REPO" \
    --project="$PROJECT_ID" \
    --location="$REGION" \
    --policy=infra/gcp/data/keep_latest_5.json \
    --no-dry-run          # remove --dry-run to switch from preview to real deletes
