#!/usr/bin/env bash
# dump_assets_local.sh
#
# Dumps the current project’s Cloud Asset inventory to
#   •  <PROJECT_ID>_assets.json
#   •  <PROJECT_ID>_iam_policies.json
#
# Prerequisites:
#   • gcloud CLI authenticated & a default application-default credential
#   • env var PROJECT_ID  (or set gcloud config)

set -euo pipefail

# ---------- Config ----------
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
[[ -z "$PROJECT_ID" ]] && { echo "❌ PROJECT_ID not set"; exit 1; }

SERVICE="cloudasset.googleapis.com"
ASSET_FILE="infra/gcp/data/${PROJECT_ID}_assets.json"
IAM_FILE="${PROJECT_ID}_iam_policies.json"

echo "Project ..........: $PROJECT_ID"
echo "Cloud Asset API ..: $SERVICE"
echo "Output files .....: $ASSET_FILE  |  $IAM_FILE"
echo

# ---------- 1. Enable API if needed ----------
if ! gcloud services list --enabled --project "$PROJECT_ID" \
      --format="value(config.name)" | grep -q "$SERVICE"; then
  echo "🔄 Enabling $SERVICE ..."
  gcloud services enable "$SERVICE" --project "$PROJECT_ID"
  # give the service a few seconds to propagate
  sleep 10
else
  echo "✅ $SERVICE already enabled"
fi
echo

# ---------- 2a. Dump resource inventory ----------
echo "📦 Dumping resource inventory to $ASSET_FILE ..."
gcloud asset search-all-resources \
  --project="$PROJECT_ID" \
  --page-size=1000 \
  --format=json > "$ASSET_FILE"

# ---------- 2b. Dump IAM-policy bindings ----------
echo "🔑 Dumping IAM policy inventory to $IAM_FILE ..."
gcloud asset search-all-iam-policies \
  --project="$PROJECT_ID" \
  --page-size=1000 \
  --format=json > "$IAM_FILE"

echo
echo "🎉 Done. Local snapshots written:"
ls -lh "$ASSET_FILE" "$IAM_FILE"
